from fastapi import APIRouter, Query
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
try:
    from db import get_connection, format_metrics, get_dashboard_stats
except ImportError:
    from db_sqlite import get_dashboard_stats
    
    def get_connection():
        import sqlite3
        conn = sqlite3.connect('local_dashboard.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def format_metrics(metrics):
        """Format SQLite results to match PostgreSQL format"""
        formatted = []
        for row in metrics:
            if isinstance(row, sqlite3.Row):
                formatted.append(dict(row))
            else:
                formatted.append(row)
        return formatted

router = APIRouter()

@router.get("/apps")
async def get_available_apps() -> Dict[str, Any]:
    """Return list of available applications based on DB tables that have data"""
    conn = get_connection()
    try:
        available: List[Dict[str, str]] = []
        with conn.cursor() as cur:
            checks = [
                ("openai_metrics", "chatgpt", "ChatGPT"),
                ("claude_metrics", "claude", "Claude"),
                ("cursor_metrics", "cursor", "Cursor"),
            ]
            for table, app_id, display_name in checks:
                try:
                    cur.execute(f"SELECT COUNT(*) AS count FROM {table}")
                    row = cur.fetchone()
                    if row and int(row.get("count", 0)) > 0:
                        available.append({
                            "id": app_id,
                            "displayName": display_name
                        })
                except Exception:
                    # Table might not exist; skip
                    continue

        return {"success": True, "data": available}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}
    finally:
        conn.close()

@router.get("/")
async def get_all_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
) -> Dict[str, Any]:
    """Get metrics from all services"""
    try:
        # Default window to last 30 days if not provided
        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
            start_date = start_dt.isoformat()
            end_date = end_dt.isoformat()

        openai_result = await get_openai_metrics(start_date, end_date, sort_by, sort_order)
        copilot_result = await get_copilot_metrics(start_date, end_date, sort_by, sort_order)
        claude_result = await get_claude_metrics(start_date, end_date, sort_by, sort_order)
        cursor_result = await get_cursor_metrics(start_date, end_date, sort_by, sort_order)

        return {
            "success": True,
            "data": {
                "openai": openai_result.get("data", []),
                "copilot": copilot_result.get("data", []),
                "claude": claude_result.get("data", []),
                "cursor": cursor_result.get("data", [])
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "data": {}}

@router.get("/stats")
async def get_metrics_stats():
    """Get aggregated statistics from all services"""
    try:
        return get_dashboard_stats()
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/openai")
async def get_openai_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    'chatgpt' as application_id,
                    id,
                    timestamp,
                    avg_response_time as response_time,
                    requests_count as request_count,
                    0 as error_rate,
                    100 as success_rate,
                    tokens_used as total_tokens,
                    0 as prompt_tokens,
                    0 as completion_tokens,
                    tokens_used as total_tokens,
                    cost_usd as cost,
                    100 as uptime,
                    model_name as model
                FROM openai_metrics
                WHERE 1=1
            """
            params = []

            # Default to last 30 days if not specified
            if start_date and end_date:
                query += " AND timestamp >= %s AND timestamp <= %s"
                params.extend([start_date, end_date])
            else:
                query += " AND timestamp >= %s"
                params.append((datetime.now() - timedelta(days=30)).isoformat())

            # Add sorting
            if sort_by:
                column_map = {
                    'responseTime': 'avg_response_time',
                    'requestCount': 'requests_count',
                    'errorRate': 'error_rate',
                    'successRate': 'success_rate',
                    'averageTokens': 'tokens_used',
                    'cost': 'cost_usd',
                    'uptime': 'uptime',
                    'timestamp': 'timestamp'
                }
                db_column = column_map.get(sort_by, 'timestamp')
                query += f" ORDER BY {db_column} {sort_order.upper()}"
            else:
                query += " ORDER BY timestamp DESC"

            query += " LIMIT 1000"  # Reasonable limit

            cur.execute(query, params)
            metrics = cur.fetchall()
            return {"success": True, "data": format_metrics(metrics)}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}
    finally:
        conn.close()

@router.get("/copilot")
async def get_copilot_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    'copilot' as application_id,
                    id,
                    timestamp,
                    0 as response_time,
                    suggestions_count as request_count,
                    CASE 
                        WHEN suggestions_count > 0 
                        THEN ((suggestions_count - acceptances_count)::float / suggestions_count * 100)
                        ELSE 0 
                    END as error_rate,
                    CASE 
                        WHEN suggestions_count > 0 
                        THEN (acceptances_count::float / suggestions_count * 100)
                        ELSE 0 
                    END as success_rate,
                    CASE 
                        WHEN suggestions_count > 0 
                        THEN (lines_suggested::float / suggestions_count)
                        ELSE 0 
                    END as average_tokens,
                    suggestions_count as total_suggestions,
                    acceptances_count as accepted_suggestions,
                    active_users as total_users,
                    lines_suggested,
                    lines_accepted,
                    100 as uptime,
                    0 as cost,
                    '' as meta
                FROM copilot_metrics
                WHERE 1=1
            """
            params = []

            if start_date and end_date:
                query += " AND timestamp >= %s AND timestamp <= %s"
                params.extend([start_date, end_date])
            else:
                query += " AND timestamp >= %s"
                params.append((datetime.now() - timedelta(days=30)).isoformat())

            # Add sorting
            if sort_by:
                column_map = {
                    'requestCount': 'suggestions_count',
                    'successRate': '(acceptances_count::float / suggestions_count * 100)',
                    'errorRate': '((suggestions_count - acceptances_count)::float / suggestions_count * 100)',
                    'averageTokens': '(lines_suggested::float / suggestions_count)',
                    'timestamp': 'timestamp'
                }
                db_column = column_map.get(sort_by, 'timestamp')
                query += f" ORDER BY {db_column} {sort_order.upper()}"
            else:
                query += " ORDER BY timestamp DESC"

            query += " LIMIT 1000"  # Reasonable limit

            cur.execute(query, params)
            metrics = cur.fetchall()
            return {"success": True, "data": format_metrics(metrics)}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}
    finally:
        conn.close()

@router.get("/cursor")
async def get_cursor_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    'cursor' as application_id,
                    id,
                    timestamp,
                    COALESCE(total_interactions, 0) as request_count,
                    0 as response_time,
                    CASE 
                        WHEN total_interactions > 0 
                        THEN ((accepted_suggestions::float / total_interactions) * 100)
                        ELSE 0 
                    END as success_rate,
                    CASE 
                        WHEN total_interactions > 0 
                        THEN ((total_interactions - accepted_suggestions)::float / total_interactions * 100)
                        ELSE 0 
                    END as error_rate,
                    CASE 
                        WHEN total_interactions > 0 
                        THEN (total_tokens::float / total_interactions)
                        ELSE 0 
                    END as average_tokens,
                    total_tokens,
                    total_cost as cost,
                    utilization_rate as uptime,
                    total_seats,
                    active_users,
                    monthly_active_users,
                    weekly_active_users,
                    daily_active_users,
                    total_interactions,
                    accepted_suggestions,
                    token_breakdown,
                    event_breakdown,
                    model_breakdown,
                    meta
                FROM cursor_metrics
                WHERE 1=1
            """
            params = []

            if start_date and end_date:
                query += " AND timestamp >= %s AND timestamp <= %s"
                params.extend([start_date, end_date])
            else:
                query += " AND timestamp >= %s"
                params.append((datetime.now() - timedelta(days=30)).isoformat())

            # Add sorting
            if sort_by:
                column_map = {
                    'requestCount': 'total_interactions',
                    'successRate': '(accepted_suggestions::float / total_interactions * 100)',
                    'errorRate': '((total_interactions - accepted_suggestions)::float / total_interactions * 100)',
                    'averageTokens': '(total_tokens::float / total_interactions)',
                    'totalTokens': 'total_tokens',
                    'cost': 'total_cost',
                    'uptime': 'utilization_rate',
                    'timestamp': 'timestamp'
                }
                db_column = column_map.get(sort_by, 'timestamp')
                query += f" ORDER BY {db_column} {sort_order.upper()}"
            else:
                query += " ORDER BY timestamp DESC"

            query += " LIMIT 1000"  # Reasonable limit

            cur.execute(query, params)
            metrics = cur.fetchall()
            return {"success": True, "data": format_metrics(metrics)}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}
    finally:
        conn.close()

@router.get("/claude")
async def get_claude_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    'claude' as application_id,
                    id,
                    timestamp,
                    response_time,
                    request_count,
                    error_rate,
                    success_rate,
                    average_tokens,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    cost,
                    uptime,
                    model
                FROM claude_metrics
                WHERE 1=1
            """
            params = []

            if start_date and end_date:
                query += " AND timestamp >= %s AND timestamp <= %s"
                params.extend([start_date, end_date])
            else:
                query += " AND timestamp >= %s"
                params.append((datetime.now() - timedelta(days=30)).isoformat())

            if sort_by:
                column_map = {
                    'responseTime': 'response_time',
                    'requestCount': 'request_count',
                    'errorRate': 'error_rate',
                    'successRate': 'success_rate',
                    'averageTokens': 'average_tokens',
                    'cost': 'cost',
                    'uptime': 'uptime',
                    'timestamp': 'timestamp'
                }
                db_column = column_map.get(sort_by, 'timestamp')
                query += f" ORDER BY {db_column} {sort_order.upper()}"
            else:
                query += " ORDER BY timestamp DESC"

            query += " LIMIT 1000"

            cur.execute(query, params)
            metrics = cur.fetchall()
            return {"success": True, "data": format_metrics(metrics)}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}
    finally:
        conn.close()
