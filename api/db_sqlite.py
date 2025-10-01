import sqlite3
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create SQLite database for local development
def get_db_connection():
    """Create and return a SQLite connection"""
    conn = sqlite3.connect('local_dashboard.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the SQLite database with sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) as count FROM metrics')
    if cursor.fetchone()['count'] == 0:
        # Insert sample metrics
        sample_metrics = [
            ('cpu_usage', 45.2, datetime.now() - timedelta(hours=1)),
            ('memory_usage', 67.8, datetime.now() - timedelta(hours=1)),
            ('disk_usage', 23.5, datetime.now() - timedelta(hours=1)),
            ('cpu_usage', 48.7, datetime.now() - timedelta(minutes=30)),
            ('memory_usage', 71.2, datetime.now() - timedelta(minutes=30)),
            ('disk_usage', 25.1, datetime.now() - timedelta(minutes=30)),
            ('cpu_usage', 52.3, datetime.now()),
            ('memory_usage', 69.4, datetime.now()),
            ('disk_usage', 24.8, datetime.now()),
        ]
        
        cursor.executemany('''
            INSERT INTO metrics (metric_name, metric_value, timestamp) 
            VALUES (?, ?, ?)
        ''', sample_metrics)
        
        # Insert sample logs
        sample_logs = [
            ('INFO', 'System startup completed', datetime.now() - timedelta(hours=2)),
            ('INFO', 'Database connection established', datetime.now() - timedelta(hours=1, minutes=45)),
            ('WARNING', 'High memory usage detected', datetime.now() - timedelta(hours=1, minutes=30)),
            ('INFO', 'Backup completed successfully', datetime.now() - timedelta(hours=1)),
            ('ERROR', 'Failed to connect to external service', datetime.now() - timedelta(minutes=45)),
            ('INFO', 'Service recovered from error state', datetime.now() - timedelta(minutes=30)),
            ('INFO', 'System running normally', datetime.now() - timedelta(minutes=15)),
        ]
        
        cursor.executemany('''
            INSERT INTO logs (level, message, timestamp) 
            VALUES (?, ?, ?)
        ''', sample_logs)
    
    conn.commit()
    conn.close()

def get_dashboard_stats():
    """Get dashboard statistics from SQLite"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get latest metrics
        cursor.execute('''
            SELECT metric_name, metric_value, timestamp 
            FROM metrics 
            WHERE timestamp >= datetime('now', '-1 hour')
            ORDER BY timestamp DESC
        ''')
        
        metrics_data = {}
        for row in cursor.fetchall():
            metric_name = row['metric_name']
            if metric_name not in metrics_data:
                metrics_data[metric_name] = {
                    'current': row['metric_value'],
                    'history': []
                }
            metrics_data[metric_name]['history'].append({
                'value': row['metric_value'],
                'timestamp': row['timestamp']
            })
        
        # Get log statistics
        cursor.execute('''
            SELECT level, COUNT(*) as count 
            FROM logs 
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY level
        ''')
        
        log_stats = {}
        for row in cursor.fetchall():
            log_stats[row['level']] = row['count']
        
        # Get recent logs
        cursor.execute('''
            SELECT level, message, timestamp 
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        recent_logs = []
        for row in cursor.fetchall():
            recent_logs.append({
                'level': row['level'],
                'message': row['message'],
                'timestamp': row['timestamp']
            })
        
        conn.close()
        
        return {
            'success': True,
            'data': {
                'metrics': metrics_data,
                'log_stats': log_stats,
                'recent_logs': recent_logs,
                'system_status': 'healthy',
                'timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def create_metrics_tables():
    """Create metrics tables for local development"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create OpenAI metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS openai_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            response_time REAL,
            request_count INTEGER,
            error_rate REAL,
            success_rate REAL,
            average_tokens REAL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            cost REAL,
            uptime REAL,
            model TEXT
        )
    ''')
    
    # Create Copilot metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS copilot_metrics (
            timestamp DATETIME PRIMARY KEY,
            total_suggestions INTEGER,
            accepted_suggestions INTEGER,
            total_users INTEGER,
            lines_suggested INTEGER,
            lines_accepted INTEGER,
            meta TEXT
        )
    ''')
    
    # Insert sample OpenAI metrics
    cursor.execute('SELECT COUNT(*) as count FROM openai_metrics')
    if cursor.fetchone()['count'] == 0:
        sample_openai = [
            (datetime.now() - timedelta(hours=2), 1.2, 150, 2.5, 97.5, 125.0, 100, 50, 150, 0.75, 99.5, 'gpt-4'),
            (datetime.now() - timedelta(hours=1), 1.1, 180, 1.8, 98.2, 132.0, 110, 60, 170, 0.85, 99.8, 'gpt-4'),
            (datetime.now(), 1.0, 200, 1.2, 98.8, 128.0, 105, 55, 160, 0.80, 99.9, 'gpt-4'),
        ]
        
        cursor.executemany('''
            INSERT INTO openai_metrics (timestamp, response_time, request_count, error_rate, success_rate, average_tokens, prompt_tokens, completion_tokens, total_tokens, cost, uptime, model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_openai)
    
    # Insert sample Copilot metrics
    cursor.execute('SELECT COUNT(*) as count FROM copilot_metrics')
    if cursor.fetchone()['count'] == 0:
        sample_copilot = [
            (datetime.now() - timedelta(hours=2), 500, 400, 25, 1200, 1000, '{"language": "python"}'),
            (datetime.now() - timedelta(hours=1), 550, 450, 28, 1300, 1100, '{"language": "javascript"}'),
            (datetime.now(), 600, 500, 30, 1400, 1200, '{"language": "typescript"}'),
        ]
        
        cursor.executemany('''
            INSERT INTO copilot_metrics (timestamp, total_suggestions, accepted_suggestions, total_users, lines_suggested, lines_accepted, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_copilot)
    
    conn.commit()
    conn.close()

def verify_database_connection():
    """Verify SQLite database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        conn.close()
        
        return {
            'success': True,
            'connected': True,
            'database': 'SQLite (Local Development)',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {
            'success': False,
            'connected': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Initialize database on module import
init_database()
create_metrics_tables()