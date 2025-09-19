import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
import random
import os

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def generate_dates(start, end, step_hours=1):
    """Generate datetime list from start to end every step_hours"""
    current = start
    while current <= end:
        yield current
        current += timedelta(hours=step_hours)

def insert_openai_metrics(conn, timestamps):
    rows = []
    for ts in timestamps:
        rows.append((
            'openai',
            round(random.uniform(0.2, 1.0), 2),  # response_time
            random.randint(50, 200),             # request_count
            round(random.uniform(0, 5), 2),      # error_rate
            round(random.uniform(95, 100), 2),   # success_rate
            round(random.uniform(100, 300), 2),  # average_tokens
            random.randint(50, 200),             # prompt_tokens
            random.randint(50, 200),             # completion_tokens
            random.randint(100, 400),            # total_tokens
            round(random.uniform(0.05, 0.5), 2), # cost
            round(random.uniform(95, 100), 2),   # uptime
            random.choice(['gpt-3.5', 'gpt-4'])  # model
        ))
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO openai_metrics (
                application_id, response_time, request_count, error_rate, success_rate,
                average_tokens, prompt_tokens, completion_tokens, total_tokens, cost, uptime, model, timestamp
            ) VALUES %s
        """, [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], ts) for r, ts in zip(rows, timestamps)])
    conn.commit()

def insert_copilot_metrics(conn, timestamps):
    rows = []
    for ts in timestamps:
        total_suggestions = random.randint(100, 300)
        accepted_suggestions = random.randint(int(total_suggestions*0.5), total_suggestions)
        total_users = random.randint(10, 50)
        lines_suggested = random.randint(500, 1500)
        lines_accepted = random.randint(int(lines_suggested*0.5), lines_suggested)
        rows.append((
            'copilot', total_suggestions, accepted_suggestions, total_users,
            lines_suggested, lines_accepted, total_suggestions,
            round(100 - (accepted_suggestions/total_suggestions*100), 2),
            round(accepted_suggestions/total_suggestions*100, 2),
            round(lines_suggested/total_suggestions, 2),
            lines_suggested, 0.0, 100.0, ts
        ))
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO copilot_metrics (
                application_id, total_suggestions, accepted_suggestions, total_users,
                lines_suggested, lines_accepted, request_count, error_rate, success_rate,
                average_tokens, total_tokens, cost, uptime, timestamp
            ) VALUES %s
        """, rows)
    conn.commit()

def insert_claude_metrics(conn, timestamps):
    rows = []
    for ts in timestamps:
        rows.append((
            'claude',
            round(random.uniform(0.3, 1.2), 2),  # response_time
            random.randint(40, 150),             # request_count
            round(random.uniform(0, 3), 2),      # error_rate
            round(random.uniform(97, 100), 2),   # success_rate
            round(random.uniform(120, 350), 2),  # average_tokens
            random.randint(50, 200),             # prompt_tokens
            random.randint(50, 150),             # completion_tokens
            random.randint(100, 400),            # total_tokens
            round(random.uniform(0.05, 0.5), 2), # cost
            round(random.uniform(95, 100), 2),   # uptime
            random.choice(['claude-1', 'claude-2']),
            ts
        ))
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO claude_metrics (
                application_id, response_time, request_count, error_rate, success_rate,
                average_tokens, prompt_tokens, completion_tokens, total_tokens, cost, uptime, model, timestamp
            ) VALUES %s
        """, rows)
    conn.commit()

def insert_cursor_metrics(conn, timestamps):
    rows = []
    for ts in timestamps:
        total_interactions = random.randint(200, 1000)
        accepted_suggestions = random.randint(int(total_interactions*0.5), total_interactions)
        total_tokens = random.randint(5000, 20000)
        rows.append((
            'cursor',
            random.randint(50, 200),           # total_seats
            random.randint(20, 150),           # active_users
            round(random.uniform(50, 100), 2), # utilization_rate
            random.randint(50, 150),           # monthly_active_users
            random.randint(30, 100),           # weekly_active_users
            random.randint(10, 80),            # daily_active_users
            total_interactions,
            accepted_suggestions,
            total_tokens,
            round(random.uniform(0.1, 1.0), 2), # total_cost
            total_interactions,
            round(100 - (accepted_suggestions/total_interactions*100), 2),
            round(accepted_suggestions/total_interactions*100, 2),
            round(total_tokens/total_interactions, 2),
            random.randint(1000, 5000),
            random.randint(1000, 5000),
            ts
        ))
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO cursor_metrics (
                application_id, total_seats, active_users, utilization_rate,
                monthly_active_users, weekly_active_users, daily_active_users,
                total_interactions, accepted_suggestions, total_tokens, total_cost,
                request_count, error_rate, success_rate, average_tokens,
                prompt_tokens, completion_tokens, timestamp
            ) VALUES %s
        """, rows)
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    timestamps = list(generate_dates(start_date, end_date, step_hours=6))  # every 6 hours ~ 4/day

    print(f"Inserting {len(timestamps)} records per table...")
    insert_openai_metrics(conn, timestamps)
    insert_copilot_metrics(conn, timestamps)
    insert_claude_metrics(conn, timestamps)
    insert_cursor_metrics(conn, timestamps)
    conn.close()
    print("Sample data generation complete!")
