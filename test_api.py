#!/usr/bin/env python3
"""
Comprehensive API Testing Script for AI Organization Dashboard
Tests all endpoints with various scenarios including success and error cases
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 30
MAX_RETRIES = 3

# Test data
VALID_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

INVALID_CREDENTIALS = [
    {"username": "admin", "password": "wrong"},
    {"username": "wrong", "password": "admin123"},
    {"username": "", "password": ""},
]

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, response: Any = None, error: str = None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_status": response.status_code if response else None,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success and error:
            print(f"   Error: {error}")
        if response and not success:
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=TIMEOUT,
                    **kwargs
                )
                return response
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n🩺 Testing Health Endpoints...")
        
        # Test root endpoint
        try:
            response = self.make_request("GET", "/")
            success = response.status_code == 200 and "status" in response.json()
            self.log_test("Root Health Check", success, response)
        except Exception as e:
            self.log_test("Root Health Check", False, error=str(e))
        
        # Test detailed health endpoint
        try:
            response = self.make_request("GET", "/health")
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "database" in data)
            self.log_test("Detailed Health Check", success, response)
        except Exception as e:
            self.log_test("Detailed Health Check", False, error=str(e))
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        # Test valid login
        try:
            response = self.make_request("POST", "/auth/login", json=VALID_CREDENTIALS)
            data = response.json()
            success = (response.status_code == 200 and 
                      "token" in data and 
                      "user" in data)
            if success:
                self.auth_token = data["token"]
            self.log_test("Valid Login", success, response)
        except Exception as e:
            self.log_test("Valid Login", False, error=str(e))
        
        # Test invalid logins
        for i, creds in enumerate(INVALID_CREDENTIALS):
            try:
                response = self.make_request("POST", "/auth/login", json=creds)
                success = response.status_code == 401
                self.log_test(f"Invalid Login {i+1}", success, response)
            except Exception as e:
                self.log_test(f"Invalid Login {i+1}", False, error=str(e))
        
        # Test token validation with valid token
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.make_request("GET", "/auth/validate", headers=headers)
                data = response.json()
                success = (response.status_code == 200 and 
                          data.get("success") == True and 
                          "data" in data)
                self.log_test("Valid Token Validation", success, response)
            except Exception as e:
                self.log_test("Valid Token Validation", False, error=str(e))
        
        # Test token validation with invalid token
        try:
            headers = {"Authorization": "Bearer invalid-token"}
            response = self.make_request("GET", "/auth/validate", headers=headers)
            success = response.status_code == 401
            self.log_test("Invalid Token Validation", success, response)
        except Exception as e:
            self.log_test("Invalid Token Validation", False, error=str(e))
        
        # Test token refresh
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.make_request("POST", "/auth/refresh", headers=headers)
                data = response.json()
                success = (response.status_code == 200 and 
                          data.get("success") == True and 
                          "data" in data)
                self.log_test("Token Refresh", success, response)
            except Exception as e:
                self.log_test("Token Refresh", False, error=str(e))
    
    def test_metrics_endpoints(self):
        """Test metrics endpoints"""
        print("\n📊 Testing Metrics Endpoints...")
        
        # Calculate date range for testing
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        date_params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Test get all metrics
        try:
            response = self.make_request("GET", "/metrics/", params=date_params)
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get All Metrics", success, response)
        except Exception as e:
            self.log_test("Get All Metrics", False, error=str(e))
        
        # Test get OpenAI metrics
        try:
            response = self.make_request("GET", "/metrics/openai", params=date_params)
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get OpenAI Metrics", success, response)
        except Exception as e:
            self.log_test("Get OpenAI Metrics", False, error=str(e))
        
        # Test get Copilot metrics
        try:
            response = self.make_request("GET", "/metrics/copilot", params=date_params)
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get Copilot Metrics", success, response)
        except Exception as e:
            self.log_test("Get Copilot Metrics", False, error=str(e))
        
        # Test get Claude metrics
        try:
            response = self.make_request("GET", "/metrics/claude", params=date_params)
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get Claude Metrics", success, response)
        except Exception as e:
            self.log_test("Get Claude Metrics", False, error=str(e))
        
        # Test get Cursor metrics
        try:
            response = self.make_request("GET", "/metrics/cursor", params=date_params)
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get Cursor Metrics", success, response)
        except Exception as e:
            self.log_test("Get Cursor Metrics", False, error=str(e))
        
        # Test get aggregated statistics
        try:
            response = self.make_request("GET", "/metrics/stats")
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get Aggregated Stats", success, response)
        except Exception as e:
            self.log_test("Get Aggregated Stats", False, error=str(e))
        
        # Test get available apps
        try:
            response = self.make_request("GET", "/metrics/apps")
            data = response.json()
            success = (response.status_code == 200 and 
                      data.get("success") == True and 
                      "data" in data)
            self.log_test("Get Available Apps", success, response)
        except Exception as e:
            self.log_test("Get Available Apps", False, error=str(e))
    
    def test_error_scenarios(self):
        """Test error handling scenarios"""
        print("\n⚠️  Testing Error Scenarios...")
        
        # Test invalid endpoint
        try:
            response = self.make_request("GET", "/invalid-endpoint")
            success = response.status_code == 404
            self.log_test("Invalid Endpoint", success, response)
        except Exception as e:
            self.log_test("Invalid Endpoint", False, error=str(e))
        
        # Test invalid HTTP method
        try:
            response = self.make_request("DELETE", "/auth/login")
            success = response.status_code == 405
            self.log_test("Invalid HTTP Method", success, response)
        except Exception as e:
            self.log_test("Invalid HTTP Method", False, error=str(e))
        
        # Test malformed JSON in request body
        try:
            response = self.make_request(
                "POST", 
                "/auth/login", 
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            success = response.status_code >= 400
            self.log_test("Malformed JSON", success, response)
        except Exception as e:
            self.log_test("Malformed JSON", False, error=str(e))
    
    def test_performance(self):
        """Test API performance"""
        print("\n🚀 Testing Performance...")
        
        # Test response time for health endpoint
        try:
            start_time = time.time()
            response = self.make_request("GET", "/health")
            end_time = time.time()
            response_time = end_time - start_time
            success = response.status_code == 200 and response_time < 2.0
            self.log_test(
                f"Health Endpoint Performance ({response_time:.2f}s)", 
                success, 
                response
            )
        except Exception as e:
            self.log_test("Health Endpoint Performance", False, error=str(e))
        
        # Test concurrent requests
        try:
            import threading
            results = []
            
            def make_request():
                try:
                    resp = self.make_request("GET", "/health")
                    results.append(resp.status_code == 200)
                except:
                    results.append(False)
            
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_rate = sum(results) / len(results)
            success = success_rate >= 0.8  # 80% success rate
            self.log_test(
                f"Concurrent Requests ({success_rate*100:.0f}% success)", 
                success
            )
        except Exception as e:
            self.log_test("Concurrent Requests", False, error=str(e))
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📋 TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Authentication Token: {'✅ Available' if self.auth_token else '❌ Not available'}")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result.get('error', 'Unknown error')}")
        
        # Save detailed report
        report_filename = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": success_rate
                },
                "results": self.test_results,
                "auth_token": self.auth_token is not None
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        return success_rate >= 80  # Return True if overall success rate is good
    
    def wait_for_services(self, max_wait: int = 60):
        """Wait for services to be ready"""
        print(f"⏳ Waiting for services to be ready (max {max_wait}s)...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = self.make_request("GET", "/health")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("status") == "healthy":
                        print("✅ Services are ready!")
                        return True
            except:
                pass
            
            time.sleep(5)
            print(".", end="", flush=True)
        
        print("\n❌ Services not ready after waiting")
        return False

def main():
    """Main test execution"""
    print("🧪 AI Organization Dashboard API Testing Suite")
    print("=" * 60)
    
    # Check if custom URL provided
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        print(f"Using custom base URL: {base_url}")
    else:
        base_url = BASE_URL
        print(f"Using default base URL: {base_url}")
    
    # Initialize tester
    tester = APITester(base_url)
    
    # Wait for services to be ready
    if not tester.wait_for_services():
        print("❌ Services not available. Please ensure they are running.")
        sys.exit(1)
    
    # Run all tests
    try:
        tester.test_health_endpoints()
        tester.test_authentication()
        tester.test_metrics_endpoints()
        tester.test_error_scenarios()
        tester.test_performance()
        
        # Generate final report
        success = tester.generate_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        tester.generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        tester.generate_report()
        sys.exit(1)

if __name__ == "__main__":
    main()