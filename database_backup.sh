#!/bin/bash

# AI Organization Dashboard - Database Backup & Migration Script
# This script handles backing up and restoring PostgreSQL data between laptops

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database configuration (from docker-compose.yml)
DB_NAME="metrics_db"
DB_USER="metrics_user"
DB_PASSWORD="metrics_pass"
DB_HOST="localhost"
DB_PORT="5432"

# Default backup file
DEFAULT_BACKUP_FILE="ai-dashboard-backup-$(date +%Y%m%d-%H%M%S).sql"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if PostgreSQL container is running
check_postgres() {
    if ! docker-compose ps postgres | grep -q "Up"; then
        print_error "PostgreSQL container is not running. Please run: docker-compose up -d postgres"
        exit 1
    fi
}

# Function to backup database
backup_database() {
    local backup_file="${1:-$DEFAULT_BACKUP_FILE}"
    
    print_status "Starting database backup to: $backup_file"
    
    # Create backup using docker exec
    docker-compose exec -T postgres pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists > "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_status "Backup completed successfully!"
        print_status "Backup file: $backup_file"
        print_status "File size: $(du -h "$backup_file" | cut -f1)"
    else
        print_error "Backup failed!"
        exit 1
    fi
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_status "Starting database restore from: $backup_file"
    print_warning "This will overwrite existing data in the database!"
    
    # Confirm restore
    read -p "Are you sure you want to restore? This will replace all current data (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled."
        exit 0
    fi
    
    # Restore database
    docker-compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" < "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_status "Restore completed successfully!"
    else
        print_error "Restore failed!"
        exit 1
    fi
}

# Function to list available backups
list_backups() {
    print_status "Available backup files:"
    ls -la ai-dashboard-backup-*.sql 2>/dev/null || echo "No backup files found"
}

# Function to show database info
show_db_info() {
    print_status "Current database information:"
    
    # Get table row counts
    docker-compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT 
        schemaname,
        tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_live_tup as live_rows
    FROM pg_stat_user_tables 
    ORDER BY schemaname, tablename;"
    
    # Get database size
    print_status "Database size:"
    docker-compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT pg_size_pretty(pg_database_size(current_database()));"
}

# Function to export data as CSV
export_csv() {
    local table_name="$1"
    local csv_file="${2:-$table_name-$(date +%Y%m%d-%H%M%S).csv}"
    
    if [ -z "$table_name" ]; then
        print_error "Please specify a table name"
        exit 1
    fi
    
    print_status "Exporting table '$table_name' to CSV: $csv_file"
    
    docker-compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    COPY $table_name TO STDOUT WITH CSV HEADER;" > "$csv_file"
    
    if [ $? -eq 0 ]; then
        print_status "CSV export completed: $csv_file"
    else
        print_error "CSV export failed!"
        exit 1
    fi
}

# Function to import CSV data
import_csv() {
    local csv_file="$1"
    local table_name="$2"
    
    if [ -z "$csv_file" ] || [ -z "$table_name" ]; then
        print_error "Please specify both CSV file and table name"
        exit 1
    fi
    
    if [ ! -f "$csv_file" ]; then
        print_error "CSV file not found: $csv_file"
        exit 1
    fi
    
    print_status "Importing CSV '$csv_file' into table '$table_name'"
    
    docker-compose exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
    COPY $table_name FROM STDIN WITH CSV HEADER;" < "$csv_file"
    
    if [ $? -eq 0 ]; then
        print_status "CSV import completed successfully!"
    else
        print_error "CSV import failed!"
        exit 1
    fi
}

# Main function
main() {
    case "${1:-help}" in
        "backup")
            check_docker
            check_postgres
            backup_database "${2:-}"
            ;;
        "restore")
            check_docker
            check_postgres
            restore_database "${2:-}"
            ;;
        "list")
            list_backups
            ;;
        "info")
            check_docker
            check_postgres
            show_db_info
            ;;
        "export-csv")
            check_docker
            check_postgres
            export_csv "$2" "$3"
            ;;
        "import-csv")
            check_docker
            check_postgres
            import_csv "$2" "$3"
            ;;
        "help"|*)
            echo "AI Organization Dashboard - Database Backup & Migration Tool"
            echo
            echo "Usage: $0 [command] [options]"
            echo
            echo "Commands:"
            echo "  backup [filename]        - Backup database to SQL file"
            echo "  restore <filename>       - Restore database from SQL file"
            echo "  list                     - List available backup files"
            echo "  info                     - Show current database information"
            echo "  export-csv <table> [file] - Export table to CSV file"
            echo "  import-csv <file> <table> - Import CSV file into table"
            echo "  help                     - Show this help message"
            echo
            echo "Examples:"
            echo "  $0 backup                                    # Create backup with timestamp"
            echo "  $0 backup my-backup.sql                     # Create named backup"
            echo "  $0 restore ai-dashboard-backup-20240101.sql # Restore from backup"
            echo "  $0 export-csv openai_metrics                # Export OpenAI metrics to CSV"
            echo "  $0 import-csv data.csv openai_metrics       # Import CSV data"
            echo
            echo "Migration workflow:"
            echo "  1. On source laptop: $0 backup"
            echo "  2. Transfer backup file to target laptop"
            echo "  3. On target laptop: $0 restore <backup-file>"
            ;;
    esac
}

# Run main function
main "$@"