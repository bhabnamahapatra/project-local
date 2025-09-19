import os
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "metrics_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "metrics_pass")
DB_NAME = os.getenv("DB_NAME", "metrics_db")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )


def insert_openai_metrics(metrics: dict):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO openai_metrics (
                    timestamp, response_time, request_count, error_rate,
                    success_rate, average_tokens, prompt_tokens,
                    completion_tokens, total_tokens, cost, uptime, model
                )
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                metrics.get("response_time", 0),
                metrics.get("request_count", 1),
                metrics.get("error_rate", 0),
                metrics.get("success_rate", 100),
                metrics.get("average_tokens", metrics["total_tokens"]),
                metrics.get("total_prompt_tokens"),
                metrics.get("total_completion_tokens"),
                metrics.get("total_tokens"),
                metrics.get("cost", 0),
                metrics.get("uptime", 100),
                ", ".join(metrics["models"].keys()) if "models" in metrics else None,
            ))
        conn.commit()
    finally:
        conn.close()


def insert_copilot_metrics(flat: dict, meta: dict):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO copilot_metrics (
                    timestamp,
                    total_suggestions,
                    accepted_suggestions,
                    total_users,
                    lines_suggested,
                    lines_accepted,
                    meta,
                    request_count,
                    error_rate,
                    success_rate,
                    average_tokens,
                    total_tokens,
                    cost,
                    uptime
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (timestamp) DO UPDATE SET
                    total_suggestions = EXCLUDED.total_suggestions,
                    accepted_suggestions = EXCLUDED.accepted_suggestions,
                    total_users = EXCLUDED.total_users,
                    lines_suggested = EXCLUDED.lines_suggested,
                    lines_accepted = EXCLUDED.lines_accepted,
                    meta = EXCLUDED.meta,
                    request_count = EXCLUDED.request_count,
                    error_rate = EXCLUDED.error_rate,
                    success_rate = EXCLUDED.success_rate,
                    average_tokens = EXCLUDED.average_tokens,
                    total_tokens = EXCLUDED.total_tokens,
                    cost = EXCLUDED.cost,
                    uptime = EXCLUDED.uptime;
            """, (
                flat["date"],
                flat["code_suggestions"],
                flat["code_acceptances"],
                flat["total_active_users"],
                flat["lines_suggested"],
                flat["lines_accepted"],
                json.dumps(meta),
                flat["code_suggestions"],  # Using suggestions as request_count
                0.0,  # Default error_rate
                (flat["code_acceptances"] / flat["code_suggestions"] * 100) if flat["code_suggestions"] > 0 else 100,  # success_rate
                0.0,  # average_tokens (Copilot doesn't provide token metrics)
                0,    # total_tokens
                0.0,  # cost
                100.0 # uptime
            ))
        conn.commit()
    finally:
        conn.close()


def insert_cursor_metrics(metrics: Dict[str, Any]) -> bool:
    """Insert Cursor metrics into the database"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cursor_metrics (
                    timestamp,
                    total_seats,
                    active_users,
                    utilization_rate,
                    monthly_active_users,
                    weekly_active_users,
                    daily_active_users,
                    total_interactions,
                    accepted_suggestions,
                    total_tokens,
                    total_cost,
                    token_breakdown,
                    event_breakdown,
                    model_breakdown,
                    meta,
                    request_count,
                    error_rate,
                    success_rate,
                    average_tokens,
                    prompt_tokens,
                    completion_tokens,
                    uptime
                ) VALUES (
                    NOW(),
                    %(total_seats)s,
                    %(active_users)s,
                    %(utilization_rate)s,
                    %(monthly_active_users)s,
                    %(weekly_active_users)s,
                    %(daily_active_users)s,
                    %(total_interactions)s,
                    %(accepted_suggestions)s,
                    %(total_tokens)s,
                    %(total_cost)s,
                    %(token_breakdown)s,
                    %(event_breakdown)s,
                    %(model_breakdown)s,
                    %(meta)s,
                    %(request_count)s,
                    %(error_rate)s,
                    %(success_rate)s,
                    %(average_tokens)s,
                    %(prompt_tokens)s,
                    %(completion_tokens)s,
                    %(uptime)s
                )
            """, {
                'total_seats': metrics.get('total_seats', 0),
                'active_users': metrics.get('active_users', 0),
                'utilization_rate': metrics.get('utilization_rate', 0),
                'monthly_active_users': metrics.get('monthly_active_users', 0),
                'weekly_active_users': metrics.get('weekly_active_users', 0),
                'daily_active_users': metrics.get('daily_active_users', 0),
                'total_interactions': metrics.get('total_interactions', 0),
                'accepted_suggestions': metrics.get('accepted_suggestions', 0),
                'total_tokens': metrics.get('total_tokens', 0),
                'total_cost': metrics.get('total_cost', 0),
                'token_breakdown': json.dumps(metrics.get('token_breakdown', {})),
                'event_breakdown': json.dumps(metrics.get('event_breakdown', {})),
                'model_breakdown': json.dumps(metrics.get('model_breakdown', {})),
                'meta': json.dumps(metrics.get('meta', {})),
                'request_count': metrics.get('request_count', 0),
                'error_rate': metrics.get('error_rate', 0),
                'success_rate': metrics.get('success_rate', 100),
                'average_tokens': metrics.get('average_tokens', 0),
                'prompt_tokens': metrics.get('prompt_tokens', 0),
                'completion_tokens': metrics.get('completion_tokens', 0),
                'uptime': metrics.get('uptime', 100)
            })
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting cursor metrics: {e}")
        return False
    finally:
        conn.close()


def insert_claude_metrics(metrics: Dict[str, Any]) -> bool:
    """Insert Claude metrics into the database"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO claude_metrics (
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
                    model,
                    meta
                ) VALUES (
                    %(timestamp)s,
                    %(response_time)s,
                    %(request_count)s,
                    %(error_rate)s,
                    %(success_rate)s,
                    %(average_tokens)s,
                    %(prompt_tokens)s,
                    %(completion_tokens)s,
                    %(total_tokens)s,
                    %(cost)s,
                    %(uptime)s,
                    %(model)s,
                    %(meta)s
                )
            """, {
                "timestamp": metrics["timestamp"],
                "response_time": metrics.get("response_time", 0),
                "request_count": metrics["request_count"],
                "error_rate": metrics["error_rate"],
                "success_rate": metrics["success_rate"],
                "average_tokens": metrics["average_tokens"],
                "prompt_tokens": metrics.get("prompt_tokens", 0),
                "completion_tokens": metrics.get("completion_tokens", 0),
                "total_tokens": metrics["total_tokens"],
                "cost": metrics["cost"],
                "uptime": metrics.get("uptime", 100),
                "model": metrics.get("model", "claude-2"),
                "meta": json.dumps(metrics.get("meta", {}))
            })
            conn.commit()
            return True
    except Exception as e:
        print(f"Error inserting Claude metrics: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
