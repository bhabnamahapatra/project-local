import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db import insert_copilot_metrics  # Your DB function

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set in env")
if not GITHUB_ORG:
    raise RuntimeError("GITHUB_ORG not set in env")

BASE_URL = f"https://api.github.com/orgs/{GITHUB_ORG}/copilot/metrics"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

COPILOT_LICENSE_COST = 10.0  # USD per user per month


def fetch_copilot_metrics(since: str, until: str, per_page: int = 100):
    """Fetch Copilot metrics between dates, handle pagination."""
    all_metrics = []
    page = 1

    while True:
        params = {"since": since, "until": until, "page": page, "per_page": per_page}
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)

        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch Copilot metrics: {resp.status_code} - {resp.text}")

        data = resp.json()

        # GitHub returns either a list or dict with 'metrics' key
        metrics = data.get("metrics") if isinstance(data, dict) else data
        if not metrics:
            break

        all_metrics.extend(metrics)

        if len(metrics) < per_page:
            break  # last page reached
        page += 1

    return all_metrics


def normalize_and_flatten(metric: dict) -> tuple:
    """Normalize and flatten a Copilot metric entry and extract metadata."""
    date = metric.get('date')

    # Aggregate suggestions data
    total_suggestions = sum(
        metric.get(f'{lang}_suggestions', 0)
        for lang in ['python', 'javascript', 'typescript', 'go', 'ruby', 'java']
    )
    accepted_suggestions = sum(
        metric.get(f'{lang}_acceptances', 0)
        for lang in ['python', 'javascript', 'typescript', 'go', 'ruby', 'java']
    )

    # Aggregate lines data
    lines_suggested = sum(
        metric.get(f'{lang}_lines_suggested', 0)
        for lang in ['python', 'javascript', 'typescript', 'go', 'ruby', 'java']
    )
    lines_accepted = sum(
        metric.get(f'{lang}_lines_accepted', 0)
        for lang in ['python', 'javascript', 'typescript', 'go', 'ruby', 'java']
    )

    # Extract user metrics
    total_users = metric.get('total_users', 0)
    active_users = metric.get('active_users', 0)

    # Create flattened metrics
    flattened = {
        "date": date,
        "total_suggestions": total_suggestions,
        "accepted_suggestions": accepted_suggestions,
        "total_users": total_users,
        "active_users": active_users,
        "lines_suggested": lines_suggested,
        "lines_accepted": lines_accepted
    }

    # Create metadata with language-specific breakdowns
    metadata = {
        "languages": {},
        "collection_timestamp": datetime.utcnow().isoformat(),
        "active_users": active_users,
        "total_users": total_users,
        "estimated_cost": active_users * COPILOT_LICENSE_COST  # Monthly cost per active user
    }

    # Add language-specific stats to metadata
    for lang in ['python', 'javascript', 'typescript', 'go', 'ruby', 'java']:
        suggestions = metric.get(f'{lang}_suggestions', 0)
        if suggestions > 0:  # Only include languages that had activity
            metadata['languages'][lang] = {
                'suggestions': suggestions,
                'acceptances': metric.get(f'{lang}_acceptances', 0),
                'lines_suggested': metric.get(f'{lang}_lines_suggested', 0),
                'lines_accepted': metric.get(f'{lang}_lines_accepted', 0)
            }

    return flattened, metadata


def aggregate_and_store_copilot_metrics(metrics_list):
    total_cost = 0.0

    for m in metrics_list:
        flat, meta = normalize_and_flatten(m)

        # Skip empty days (no activity at all)
        if flat["total_active_users"] == 0 and flat["code_suggestions"] == 0:
            continue

        if COPILOT_LICENSE_COST > 0:
            flat["estimated_cost_usd"] = round(
                (flat["total_active_users"] * COPILOT_LICENSE_COST) / 30, 2
            )
            total_cost += flat["estimated_cost_usd"]

        print(f"[{flat['date']}] Users: {flat['total_active_users']} | "
              f"Suggestions: {flat['code_suggestions']} | "
              f"Acceptances: {flat['code_acceptances']} | "
              f"Cost: ${flat.get('estimated_cost_usd', 0)}")

        insert_copilot_metrics(flat, meta)

    print(f"\nTotal Estimated Monthly Cost (USD): {round(total_cost, 2)}")


def collect_copilot_metrics(start_date: str = None, end_date: str = None) -> dict:
    """Collect GitHub Copilot metrics for the specified date range"""
    try:
        # If no dates provided, default to last 24 hours
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=1)

        # Format dates for GitHub API
        since = start_date.isoformat() + "Z" if isinstance(start_date, datetime) else start_date
        until = end_date.isoformat() + "Z" if isinstance(end_date, datetime) else end_date

        # Fetch metrics
        metrics = fetch_copilot_metrics(since=since, until=until)

        # Process each day's metrics
        for day_metrics in metrics:
            flattened, metadata = normalize_and_flatten(day_metrics)
            insert_copilot_metrics(flattened, metadata)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    today = datetime.utcnow().date()
    since = (today - timedelta(days=7)).isoformat()  # fetch last 7 days
    until = today.isoformat()

    raw_metrics = fetch_copilot_metrics(since, until)
    aggregate_and_store_copilot_metrics(raw_metrics)
