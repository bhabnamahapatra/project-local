import os
import psycopg2
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'metrics_db'),
        user=os.getenv('DB_USER', 'metrics_user'),
        password=os.getenv('DB_PASSWORD', 'metrics_pass'),
        cursor_factory=RealDictCursor
    )

def format_metrics(metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format metrics for API response"""
    return [{
        'id': str(m.get('id', m.get('timestamp'))),  # Some services use timestamp as ID
        'applicationId': m['application_id'],
        'timestamp': m['timestamp'].isoformat() if isinstance(m['timestamp'], datetime) else m['timestamp'],
        'responseTime': float(m.get('response_time', 0)),
        'requestCount': int(m.get('request_count', 0)),
        'errorRate': float(m.get('error_rate', 0)),
        'successRate': float(m.get('success_rate', 100)),
        'averageTokens': float(m.get('average_tokens', 0)),
        'cost': float(m.get('cost', 0)),
        'uptime': float(m.get('uptime', 100)),
        # Common LLM metrics
        'model': m.get('model'),
        'promptTokens': m.get('prompt_tokens'),
        'completionTokens': m.get('completion_tokens'),
        'totalTokens': m.get('total_tokens'),
        # Copilot and Cursor specific
        'totalSuggestions': m.get('total_suggestions'),
        'acceptedSuggestions': m.get('accepted_suggestions'),
        'totalUsers': m.get('total_users'),
        'linesSuggested': m.get('lines_suggested'),
        'linesAccepted': m.get('lines_accepted'),
        # Cursor specific
        'totalSeats': m.get('total_seats'),
        'activeUsers': m.get('active_users'),
        'monthlyActiveUsers': m.get('monthly_active_users'),
        'weeklyActiveUsers': m.get('weekly_active_users'),
        'dailyActiveUsers': m.get('daily_active_users'),
        'tokenBreakdown': m.get('token_breakdown'),
        'eventBreakdown': m.get('event_breakdown'),
        'modelBreakdown': m.get('model_breakdown'),
        'meta': m.get('meta')
    } for m in metrics]

def get_dashboard_stats() -> Dict[str, Any]:
    """Get aggregated dashboard statistics from all services (Decimal-safe)"""
    from decimal import Decimal
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            last_24h = datetime.now() - timedelta(hours=24)

            # OpenAI Metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as metric_count,
                    SUM(request_count) as total_requests,
                    AVG(response_time) as avg_response_time,
                    AVG(success_rate) as avg_success_rate,
                    AVG(error_rate) as avg_error_rate,
                    SUM(cost) as total_cost,
                    AVG(uptime) as avg_uptime,
                    SUM(total_tokens) as total_tokens
                FROM openai_metrics
                WHERE timestamp >= %s
            """, (last_24h,))
            openai_stats = cur.fetchone()

            # Claude Metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as metric_count,
                    SUM(request_count) as total_requests,
                    AVG(response_time) as avg_response_time,
                    AVG(success_rate) as avg_success_rate,
                    AVG(error_rate) as avg_error_rate,
                    SUM(cost) as total_cost,
                    AVG(uptime) as avg_uptime,
                    SUM(total_tokens) as total_tokens
                FROM claude_metrics
                WHERE timestamp >= %s
            """, (last_24h,))
            claude_stats = cur.fetchone()

            # Copilot Metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as metric_count,
                    SUM(total_suggestions) as total_suggestions,
                    SUM(accepted_suggestions) as accepted_suggestions,
                    AVG(total_users) as avg_users,
                    SUM(lines_suggested) as total_lines_suggested,
                    SUM(lines_accepted) as total_lines_accepted
                FROM copilot_metrics
                WHERE timestamp >= %s
            """, (last_24h,))
            copilot_stats = cur.fetchone()

            # Cursor Metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as metric_count,
                    SUM(total_interactions) as total_interactions,
                    SUM(accepted_suggestions) as accepted_suggestions,
                    AVG(utilization_rate) as avg_utilization,
                    MAX(total_seats) as total_seats,
                    AVG(active_users) as avg_active_users,
                    AVG(monthly_active_users) as avg_mau,
                    SUM(total_tokens) as total_tokens,
                    SUM(total_cost) as total_cost
                FROM cursor_metrics
                WHERE timestamp >= %s
            """, (last_24h,))
            cursor_stats = cur.fetchone()

            # Helper to safely convert Decimal or None to float
            def safe_float(value):
                if value is None:
                    return 0.0
                return float(value) if isinstance(value, Decimal) else float(value)

            # Helper to safely convert Decimal or None to int
            def safe_int(value):
                if value is None:
                    return 0
                return int(value)

            # Combined statistics
            total_requests = (
                safe_float(openai_stats['total_requests']) +
                safe_float(claude_stats['total_requests']) +
                safe_float(copilot_stats['total_suggestions']) +
                safe_float(cursor_stats['total_interactions'])
            )

            total_cost = (
                safe_float(openai_stats['total_cost']) +
                safe_float(claude_stats['total_cost']) +
                safe_float(cursor_stats['total_cost'])
            )

            # Weighted average response time for LLMs
            total_llm_requests = (
                safe_float(openai_stats['total_requests']) +
                safe_float(claude_stats['total_requests'])
            )
            avg_response_time = (
                (safe_float(openai_stats['avg_response_time']) * safe_float(openai_stats['total_requests']) +
                 safe_float(claude_stats['avg_response_time']) * safe_float(claude_stats['total_requests']))
                / (total_llm_requests if total_llm_requests > 0 else 1)
            )

            # Overall success rate
            success_rates = []
            if safe_int(openai_stats['metric_count']):
                success_rates.append(safe_float(openai_stats['avg_success_rate']))
            if safe_int(claude_stats['metric_count']):
                success_rates.append(safe_float(claude_stats['avg_success_rate']))
            if safe_int(copilot_stats['total_suggestions']):
                copilot_success = safe_float(copilot_stats['accepted_suggestions']) / safe_float(copilot_stats['total_suggestions']) * 100
                success_rates.append(copilot_success)
            if safe_int(cursor_stats['total_interactions']):
                cursor_success = safe_float(cursor_stats['accepted_suggestions']) / safe_float(cursor_stats['total_interactions']) * 100
                success_rates.append(cursor_success)

            overall_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0

            return {
                "success": True,
                "data": {
                    "totalRequests": safe_int(total_requests),
                    "averageResponseTime": round(avg_response_time, 2),
                    "overallSuccessRate": round(overall_success_rate, 2),
                    "totalCost": round(total_cost, 2),
                    "activeApplications": sum(1 for s in [openai_stats, claude_stats, copilot_stats, cursor_stats]
                                              if safe_int(s['metric_count']) > 0),
                    "details": {
                        "openai": {
                            "requests": safe_int(openai_stats['total_requests']),
                            "successRate": round(safe_float(openai_stats['avg_success_rate']), 2),
                            "errorRate": round(safe_float(openai_stats['avg_error_rate']), 2),
                            "totalTokens": safe_int(openai_stats['total_tokens']),
                            "cost": round(safe_float(openai_stats['total_cost']), 2)
                        },
                        "claude": {
                            "requests": safe_int(claude_stats['total_requests']),
                            "successRate": round(safe_float(claude_stats['avg_success_rate']), 2),
                            "errorRate": round(safe_float(claude_stats['avg_error_rate']), 2),
                            "totalTokens": safe_int(claude_stats['total_tokens']),
                            "cost": round(safe_float(claude_stats['total_cost']), 2)
                        },
                        "copilot": {
                            "suggestions": safe_int(copilot_stats['total_suggestions']),
                            "acceptedSuggestions": safe_int(copilot_stats['accepted_suggestions']),
                            "activeUsers": safe_int(copilot_stats['avg_users']),
                            "linesSuggested": safe_int(copilot_stats['total_lines_suggested']),
                            "linesAccepted": safe_int(copilot_stats['total_lines_accepted'])
                        },
                        "cursor": {
                            "totalSeats": safe_int(cursor_stats['total_seats']),
                            "activeUsers": safe_int(cursor_stats['avg_active_users']),
                            "monthlyActiveUsers": safe_int(cursor_stats['avg_mau']),
                            "interactions": safe_int(cursor_stats['total_interactions']),
                            "acceptedSuggestions": safe_int(cursor_stats['accepted_suggestions']),
                            "utilization": round(safe_float(cursor_stats['avg_utilization']), 2),
                            "totalTokens": safe_int(cursor_stats['total_tokens']),
                            "cost": round(safe_float(cursor_stats['total_cost']), 2)
                        }
                    }
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "totalRequests": 0,
                "averageResponseTime": 0,
                "overallSuccessRate": 0,
                "totalCost": 0,
                "activeApplications": 0,
                "details": {
                    "openai": {},
                    "claude": {},
                    "copilot": {},
                    "cursor": {}
                }
            }
        }
    finally:
        conn.close()


def verify_database_connection() -> Dict[str, Any]:
    """Verify database connection and return table counts"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            stats = {}

            # Check each metrics table
            for table in ['openai_metrics', 'claude_metrics', 'copilot_metrics', 'cursor_metrics']:
                try:
                    cur.execute(f"""
                        SELECT 
                            COUNT(*) as count,
                            MIN(timestamp) as earliest_record,
                            MAX(timestamp) as latest_record
                        FROM {table}
                    """)
                    stats[table] = cur.fetchone()
                except Exception as e:
                    stats[table] = {'error': str(e)}

            return {
                "success": True,
                "data": stats
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {}
        }
    finally:
        conn.close()
