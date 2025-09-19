import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from db import insert_cursor_metrics

def fetch_cursor_metrics(start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """Fetch metrics from Cursor API"""
    API_KEY = os.getenv("CURSOR_API_KEY")
    BASE_URL = os.getenv("CURSOR_API_BASE_URL", "https://api.cursor.com/")

    if not API_KEY:
        raise ValueError("CURSOR_API_KEY environment variable not set")

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {API_KEY}"})

    # If no dates provided, default to last 24 hours
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=1)

    # Fetch all metrics components
    users_data = get_organization_users(session)
    usage_data = get_usage_metrics(session, start_date, end_date)
    billing_data = get_billing_summary(session)

    return {
        "users": users_data,
        "usage": usage_data,
        "billing": billing_data,
        "timestamp": datetime.utcnow().isoformat()
    }

def collect_cursor_metrics(start_date: str = None, end_date: str = None) -> Dict[str, bool]:
    """Collect and store Cursor metrics"""
    try:
        metrics = fetch_cursor_metrics(start_date, end_date)
        processed_metrics = calculate_metrics(
            metrics["users"],
            metrics["usage"],
            metrics["billing"],
            datetime.fromisoformat(metrics["timestamp"])
        )
        insert_cursor_metrics(processed_metrics)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_organization_users(session: requests.Session) -> Dict[str, Any]:
    """Fetch organization users data"""
    response = session.get("/api/v1/organization/users")
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data.get("data", []))
    if df.empty:
        return {"total_seats": 0, "active_users": 0}

    df['last_active_at'] = pd.to_datetime(df['last_active_at'], errors='coerce')

    now = datetime.now(df['last_active_at'].dt.tz)
    active_users = len(df[df['status'] == 'active'])
    mau = df[df['last_active_at'] > (now - timedelta(days=30))]['id'].nunique()
    wau = df[df['last_active_at'] > (now - timedelta(days=7))]['id'].nunique()
    dau = df[df['last_active_at'] > (now - timedelta(days=1))]['id'].nunique()

    return {
        "total_seats": len(df),
        "active_users": active_users,
        "monthly_active_users": mau,
        "weekly_active_users": wau,
        "daily_active_users": dau
    }

def get_usage_metrics(
    session: requests.Session,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Fetch usage metrics for the specified date range"""
    params = {
        "start_date": start_date.isoformat() + "Z",
        "end_date": end_date.isoformat() + "Z"
    }

    response = session.get("/api/v1/organization/usage_events", params=params)
    response.raise_for_status()
    events = response.json().get("data", [])

    df = pd.DataFrame(events)
    if df.empty:
        return {
            "total_interactions": 0,
            "accepted_suggestions": 0,
            "event_breakdown": {},
            "model_breakdown": {}
        }

    total_interactions = len(df)
    accepted_suggestions = len(df[df.get('metadata_accepted', False)])

    event_breakdown = df['event_type'].value_counts().to_dict() if 'event_type' in df else {}
    model_breakdown = df['model_name'].value_counts().to_dict() if 'model_name' in df else {}

    return {
        "total_interactions": total_interactions,
        "accepted_suggestions": accepted_suggestions,
        "event_breakdown": event_breakdown,
        "model_breakdown": model_breakdown
    }

def get_billing_summary(session: requests.Session) -> Dict[str, Any]:
    """Fetch billing summary"""
    response = session.get("/api/v1/organization/billing/summary")
    response.raise_for_status()
    data = response.json()

    return {
        "total_tokens": data.get('total_token_consumption', {}).get('total_tokens', 0),
        "total_cost": data.get('total_estimated_cost_usd', 0),
        "token_breakdown": data.get('consumption_by_model', [])
    }

def calculate_metrics(
    users_data: Dict[str, Any],
    usage_data: Dict[str, Any],
    billing_data: Dict[str, Any],
    timestamp: datetime
) -> Dict[str, Any]:
    """Calculate unified metrics from raw data"""
    # Calculate utilization rate
    utilization_rate = (users_data['active_users'] / users_data['total_seats'] * 100) if users_data['total_seats'] > 0 else 0

    # Extract token and cost information from billing data
    total_tokens = billing_data.get('total_token_consumption', {}).get('total_tokens', 0)
    total_cost = billing_data.get('total_estimated_cost_usd', 0.0)

    # Calculate success and error rates from usage data
    total_interactions = usage_data.get('total_interactions', 0)
    accepted_suggestions = usage_data.get('accepted_suggestions', 0)
    success_rate = (accepted_suggestions / total_interactions * 100) if total_interactions > 0 else 100
    error_rate = 100 - success_rate

    # Calculate average tokens per interaction
    average_tokens = total_tokens / total_interactions if total_interactions > 0 else 0

    return {
        'timestamp': timestamp,
        'total_seats': users_data['total_seats'],
        'active_users': users_data['active_users'],
        'utilization_rate': utilization_rate,
        'monthly_active_users': users_data['monthly_active_users'],
        'weekly_active_users': users_data['weekly_active_users'],
        'daily_active_users': users_data['daily_active_users'],
        'total_interactions': total_interactions,
        'accepted_suggestions': accepted_suggestions,
        'total_tokens': total_tokens,
        'total_cost': total_cost,
        'token_breakdown': billing_data.get('consumption_by_model', {}),
        'event_breakdown': usage_data.get('event_breakdown', {}),
        'model_breakdown': usage_data.get('model_breakdown', {}),
        'meta': {
            'collection_timestamp': timestamp.isoformat(),
            'data_period': 'daily'
        },
        'request_count': total_interactions,
        'error_rate': error_rate,
        'success_rate': success_rate,
        'average_tokens': average_tokens,
        'prompt_tokens': billing_data.get('prompt_tokens', 0),
        'completion_tokens': billing_data.get('completion_tokens', 0),
        'uptime': 100.0  # Default value as Cursor doesn't provide uptime metrics
    }

if __name__ == "__main__":
    result = collect_cursor_metrics()
