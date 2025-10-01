#!/usr/bin/env python3
"""
AI Organization Dashboard - Flow Diagram Validator
This script validates the system flow by testing individual components
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

class FlowValidator:
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def log(self, message: str, status: str = "INFO"):
        """Log with color coding"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green  
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")
    
    def check_file_exists(self, filepath: str) -> bool:
        """Check if required files exist"""
        exists = Path(filepath).exists()
        self.log(f"File check: {filepath} - {'EXISTS' if exists else 'MISSING'}", 
                "SUCCESS" if exists else "ERROR")
        return exists
    
    def validate_docker_compose(self) -> bool:
        """Validate docker-compose.yml structure"""
        self.log("Validating Docker Compose configuration...")
        
        try:
            # Check if docker-compose.yml exists
            if not self.check_file_exists("docker-compose.yml"):
                return False
                
            # Parse YAML structure (basic validation)
            with open("docker-compose.yml", "r") as f:
                content = f.read()
                
            required_services = ["postgres", "api", "collector", "dashboard"]
            missing_services = []
            
            for service in required_services:
                if f"{service}:" not in content:
                    missing_services.append(service)
            
            if missing_services:
                self.log(f"Missing services: {missing_services}", "ERROR")
                return False
                
            self.log("Docker Compose validation successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Docker Compose validation failed: {e}", "ERROR")
            return False
    
    def validate_environment_files(self) -> bool:
        """Validate environment configuration files"""
        self.log("Validating environment files...")
        
        required_files = [".env.example", ".env"]
        all_exist = True
        
        for file in required_files:
            if not self.check_file_exists(file):
                all_exist = False
                
        # Check .env has required variables
        if Path(".env").exists():
            with open(".env", "r") as f:
                env_content = f.read()
                
            required_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
            missing_vars = []
            
            for var in required_vars:
                if var not in env_content:
                    missing_vars.append(var)
            
            if missing_vars:
                self.log(f"Missing environment variables: {missing_vars}", "WARNING")
        
        return all_exist
    
    def validate_api_structure(self) -> bool:
        """Validate API structure and dependencies"""
        self.log("Validating API structure...")
        
        required_files = ["api/app.py", "api/requirements.txt", "api/metrics.py", "api/db.py"]
        all_exist = True
        
        for file in required_files:
            if not self.check_file_exists(file):
                all_exist = False
        
        # Check requirements.txt has essential packages
        if Path("api/requirements.txt").exists():
            with open("api/requirements.txt", "r") as f:
                requirements = f.read()
                
            essential_packages = ["fastapi", "uvicorn", "psycopg2"]
            missing_packages = []
            
            for package in essential_packages:
                if package not in requirements.lower():
                    missing_packages.append(package)
            
            if missing_packages:
                self.log(f"Missing essential packages: {missing_packages}", "WARNING")
        
        return all_exist
    
    def validate_collector_structure(self) -> bool:
        """Validate collector structure"""
        self.log("Validating collector structure...")
        
        required_files = [
            "collector/collector.py", 
            "collector/requirements.txt",
            "collector/openai.py",
            "collector/copilot.py", 
            "collector/claude.py",
            "collector/cursor.py"
        ]
        
        all_exist = True
        for file in required_files:
            if not self.check_file_exists(file):
                all_exist = False
                
        return all_exist
    
    def validate_dashboard_structure(self) -> bool:
        """Validate dashboard structure"""
        self.log("Validating dashboard structure...")
        
        required_files = [
            "dashboard/package.json",
            "dashboard/src/App.tsx",
            "dashboard/src/main.tsx",
            "dashboard/Dockerfile"
        ]
        
        all_exist = True
        for file in required_files:
            if not self.check_file_exists(file):
                all_exist = False
                
        # Check package.json has required dependencies
        if Path("dashboard/package.json").exists():
            try:
                with open("dashboard/package.json", "r") as f:
                    package_data = json.load(f)
                
                dependencies = package_data.get("dependencies", {})
                required_deps = ["react", "react-dom"]
                
                missing_deps = []
                for dep in required_deps:
                    if dep not in dependencies:
                        missing_deps.append(dep)
                
                if missing_deps:
                    self.log(f"Missing dashboard dependencies: {missing_deps}", "WARNING")
                    
            except json.JSONDecodeError:
                self.log("Invalid package.json format", "ERROR")
                return False
        
        return all_exist
    
    def validate_database_schema(self) -> bool:
        """Validate database initialization script"""
        self.log("Validating database schema...")
        
        schema_file = "infra/init-db.sql"
        if not self.check_file_exists(schema_file):
            return False
        
        try:
            with open(schema_file, "r") as f:
                schema_content = f.read()
            
            # Check for essential SQL commands
            required_elements = ["CREATE TABLE", "openai_metrics", "copilot_metrics"]
            missing_elements = []
            
            for element in required_elements:
                if element not in schema_content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log(f"Missing schema elements: {missing_elements}", "ERROR")
                return False
            
            self.log("Database schema validation successful", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Database schema validation failed: {e}", "ERROR")
            return False
    
    def validate_test_structure(self) -> bool:
        """Validate test files"""
        self.log("Validating test structure...")
        
        test_files = ["test_api.py", "database_backup.sh", "quickstart.sh"]
        all_exist = True
        
        for file in test_files:
            if not self.check_file_exists(file):
                all_exist = False
            else:
                # Check if scripts are executable
                if file.endswith('.sh'):
                    import os
                    if not os.access(file, os.X_OK):
                        self.log(f"Script not executable: {file}", "WARNING")
        
        return all_exist
    
    def run_syntax_check(self, filepath: str) -> bool:
        """Run basic syntax check on Python files"""
        if not filepath.endswith('.py'):
            return True
            
        try:
            with open(filepath, 'r') as f:
                code = f.read()
            
            compile(code, filepath, 'exec')
            self.log(f"Syntax check passed: {filepath}", "SUCCESS")
            return True
            
        except SyntaxError as e:
            self.log(f"Syntax error in {filepath}: {e}", "ERROR")
            return False
    
    def generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""
        self.log("Generating validation report...")
        
        validations = {
            "docker_compose": self.validate_docker_compose(),
            "environment": self.validate_environment_files(),
            "api_structure": self.validate_api_structure(),
            "collector_structure": self.validate_collector_structure(),
            "dashboard_structure": self.validate_dashboard_structure(),
            "database_schema": self.validate_database_schema(),
            "test_structure": self.validate_test_structure()
        }
        
        # Run syntax checks on key Python files
        python_files = ["api/app.py", "api/metrics.py", "collector/collector.py", "test_api.py"]
        syntax_results = {}
        
        for file in python_files:
            if Path(file).exists():
                syntax_results[file] = self.run_syntax_check(file)
        
        # Calculate overall score
        total_checks = len(validations) + len(syntax_results)
        passed_checks = sum(validations.values()) + sum(syntax_results.values())
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        report = {
            "overall_score": round(score, 1),
            "validations": validations,
            "syntax_checks": syntax_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report
    
    def save_report(self, report: Dict):
        """Save validation report to file"""
        report_file = "validation_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Validation report saved to: {report_file}", "SUCCESS")
    
    def print_summary(self, report: Dict):
        """Print validation summary"""
        print("\n" + "="*60)
        print("🎯 AI ORGANIZATION DASHBOARD - VALIDATION SUMMARY")
        print("="*60)
        
        print(f"\n📊 Overall Score: {report['overall_score']}%")
        
        print("\n🔍 Component Validations:")
        for component, status in report['validations'].items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component.replace('_', ' ').title()}")
        
        if report['syntax_checks']:
            print("\n🔍 Syntax Checks:")
            for file, status in report['syntax_checks'].items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {file}")
        
        print(f"\n🕐 Generated: {report['timestamp']}")
        print("="*60)
        
        if report['overall_score'] >= 90:
            print("🎉 EXCELLENT! System is ready for deployment.")
        elif report['overall_score'] >= 70:
            print("⚠️  GOOD! System needs minor fixes before deployment.")
        else:
            print("🚨 CRITICAL! System requires significant fixes.")

def main():
    """Main validation function"""
    print("🚀 Starting AI Organization Dashboard Flow Validation...")
    print("="*60)
    
    validator = FlowValidator()
    
    # Generate comprehensive report
    report = validator.generate_validation_report()
    
    # Save and display results
    validator.save_report(report)
    validator.print_summary(report)
    
    return 0 if report['overall_score'] >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())