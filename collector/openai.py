import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from db import insert_openai_metrics

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://api.openai.com/v1/usage"

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment variables")


def fetch_openai_usage(start_date: str = None, end_date: str = None):
    """Fetch usage metrics from OpenAI API"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    params = {
        "start_date": start_date or today,
        "end_date": end_date or today,
    }

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch OpenAI usage: {response.status_code} - {response.text}")

    data = response.json()

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0
    request_count = 0
    model_breakdown = {}

    for item in data.get("data", []):
        model = item.get("aggregation_key", {}).get("model", "unknown")
        prompt_tokens = item.get("n_prompt_tokens_total", 0)
        completion_tokens = item.get("n_completion_tokens_total", 0)
        requests = item.get("n_requests", 0)
        cost = item.get("cost", 0)

        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens
        total_cost += cost
        request_count += requests

        model_breakdown[model] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "requests": requests,
            "cost": cost
        }

    # Calculate success and error rates from response data
    success_count = sum(item.get("n_success", 0) for item in data.get("data", []))
    error_count = sum(item.get("n_errors", 0) for item in data.get("data", []))
    total_requests = success_count + error_count

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "request_count": request_count,
        "response_time": 0,  # OpenAI doesn't provide this metric
        "error_rate": (error_count / total_requests * 100) if total_requests > 0 else 0,
        "success_rate": (success_count / total_requests * 100) if total_requests > 0 else 100,
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens": total_prompt_tokens + total_completion_tokens,
        "average_tokens": ((total_prompt_tokens + total_completion_tokens) / request_count) if request_count > 0 else 0,
        "cost": total_cost,
        "uptime": 100,  # OpenAI doesn't provide this metric
        "models": model_breakdown,
        "meta": {
            "start_date": params["start_date"],
            "end_date": params["end_date"],
            "collection_timestamp": datetime.utcnow().isoformat()
        }
    }


def collect_openai_metrics(start_date: str = None, end_date: str = None):
    """Collect and store OpenAI metrics"""
    try:
        metrics = fetch_openai_usage(start_date, end_date)
        insert_openai_metrics(metrics)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = collect_openai_metrics()
    print(result)
