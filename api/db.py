import os
import psycopg2
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'ai_dashboard_db'),
        user=os.getenv('DB_USER', 'ai_dashboard_user'),
        password=os.getenv('DB_PASSWORD', ''),
        cursor_factory=RealDictCursor
    )

def format_metrics(metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format metrics for API response"""
    return [{
        'id': str(m.get('id', m.get('timestamp'))),  # Some services use timestamp as ID
        'applicationId': m.get('application_id', 'ai-dashboard'),
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
                    SUM(requests_count) as total_requests,
                    AVG(avg_response_time) as avg_response_time,
                    AVG(cost_usd) as avg_cost,
                    SUM(tokens_used) as total_tokens
                FROM openai_metrics
                WHERE timestamp >= %s
            """, (last_24h,))
            openai_stats = cur.fetchone()

            # Copilot Metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as metric_count,
                    SUM(suggestions_count) as total_suggestions,
                    SUM(acceptances_count) as accepted_suggestions,
                    AVG(active_users) as avg_users,
                    SUM(lines_suggested) as total_lines_suggested,
                    SUM(lines_accepted) as total_lines_accepted
                FROM copilot_metrics
                WHERE timestamp >= %s
            """, (last_24h,))
            copilot_stats = cur.fetchone()

            # System Metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as metric_count,
                    AVG(metric_value) as avg_cpu_usage
                FROM system_metrics
                WHERE metric_name = 'cpu_usage' AND timestamp >= %s
            """, (last_24h,))
            system_stats = cur.fetchone()

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
                safe_float(copilot_stats['total_suggestions'])
            )

            total_cost = safe_float(openai_stats['avg_cost']) * safe_int(openai_stats['metric_count'])

            # Calculate success rates
            openai_success_rate = 95.0  # Default for OpenAI
            copilot_success_rate = (
                safe_float(copilot_stats['accepted_suggestions']) / safe_float(copilot_stats['total_suggestions']) * 100
                if safe_float(copilot_stats['total_suggestions']) > 0 else 0
            )

            # Overall success rate (weighted average)
            total_openai_weight = safe_float(openai_stats['total_requests'])
            total_copilot_weight = safe_float(copilot_stats['total_suggestions'])
            total_weight = total_openai_weight + total_copilot_weight
            
            if total_weight > 0:
                overall_success_rate = (
                    (openai_success_rate * total_openai_weight + copilot_success_rate * total_copilot_weight) / total_weight
                )
            else:
                overall_success_rate = 0

            return {
                "success": True,
                "data": {
                    "totalRequests": safe_int(total_requests),
                    "averageResponseTime": round(safe_float(openai_stats['avg_response_time']), 2),
                    "overallSuccessRate": round(overall_success_rate, 2),
                    "totalCost": round(total_cost, 2),
                    "activeApplications": sum(1 for s in [openai_stats, copilot_stats, system_stats]
                                              if safe_int(s['metric_count']) > 0),
                    "details": {
                        "openai": {
                            "requests": safe_int(openai_stats['total_requests']),
                            "successRate": round(openai_success_rate, 2),
                            "errorRate": round(100 - openai_success_rate, 2),
                            "totalTokens": safe_int(openai_stats['total_tokens']),
                            "cost": round(total_cost, 2)
                        },
                        "copilot": {
                            "suggestions": safe_int(copilot_stats['total_suggestions']),
                            "acceptedSuggestions": safe_int(copilot_stats['accepted_suggestions']),
                            "activeUsers": safe_int(copilot_stats['avg_users']),
                            "linesSuggested": safe_int(copilot_stats['total_lines_suggested']),
                            "linesAccepted": safe_int(copilot_stats['total_lines_accepted']),
                            "successRate": round(copilot_success_rate, 2)
                        },
                        "system": {
                            "cpuUsage": round(safe_float(system_stats['avg_cpu_usage']), 2)
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
                    "copilot": {},
                    "system": {}
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

            # Check each table
            for table in ['system_metrics', 'logs', 'openai_metrics', 'copilot_metrics']:
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
