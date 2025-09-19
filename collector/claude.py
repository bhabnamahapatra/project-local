import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from db import insert_claude_metrics

__all__ = ['fetch_claude_metrics', 'collect_claude_metrics']

def fetch_claude_metrics(start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """Fetch metrics from Claude API"""
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    BASE_URL = os.getenv("ANTHROPIC_API_BASE_URL", "https://api.anthropic.com/v1/")

    if not API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    session = requests.Session()
    session.headers.update({
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    })

    # If no dates provided, default to last 24 hours
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=1)

    try:
        # Fetch usage statistics
        response = session.get(f"{BASE_URL}usage", params={
            "start_date": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
            "end_date": end_date.isoformat() if isinstance(end_date, datetime) else end_date
        })
        response.raise_for_status()
        usage_data = response.json()

        # Calculate metrics
        total_requests = sum(day["request_count"] for day in usage_data.get("days", []))
        total_tokens = sum(day["total_tokens"] for day in usage_data.get("days", []))
        total_cost = sum(day["total_cost"] for day in usage_data.get("days", []))
        success_count = sum(day["successful_requests"] for day in usage_data.get("days", []))
        error_count = sum(day["failed_requests"] for day in usage_data.get("days", []))

        # Calculate rates
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 100
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        avg_tokens = (total_tokens / total_requests) if total_requests > 0 else 0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "request_count": total_requests,
            "total_tokens": total_tokens,
            "prompt_tokens": sum(day.get("prompt_tokens", 0) for day in usage_data.get("days", [])),
            "completion_tokens": sum(day.get("completion_tokens", 0) for day in usage_data.get("days", [])),
            "success_rate": success_rate,
            "error_rate": error_rate,
            "average_tokens": avg_tokens,
            "cost": total_cost,
            "model": "claude-2",  # Add model version when available from API
            "uptime": 100,  # Assuming 100% uptime, adjust if API provides status
            "meta": {
                "collection_timestamp": datetime.utcnow().isoformat(),
                "api_version": "2023-06-01",
                "daily_breakdown": usage_data.get("days", [])
            }
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch Claude metrics: {str(e)}")

def collect_claude_metrics(start_date: str = None, end_date: str = None) -> Dict[str, bool]:
    """Collect and store Claude metrics"""
    try:
        metrics = fetch_claude_metrics(start_date, end_date)
        insert_claude_metrics(metrics)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = collect_claude_metrics()
    print(result)
