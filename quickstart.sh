#!/bin/bash

# AI Organization Dashboard - Quick Start Script
# This script automates the deployment and testing process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="http://localhost:5000"
MAX_WAIT_TIME=120

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create environment file
create_env_file() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env file from .env.example"
            log_warning "Please update .env file with your actual API keys before proceeding"
        else
            log_error ".env.example file not found"
            exit 1
        fi
    else
        log_info ".env file already exists"
    fi
}

# Build and start services
start_services() {
    log_info "Building and starting services..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    docker-compose up --build -d
    
    log_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready (this may take up to $MAX_WAIT_TIME seconds)..."
    
    start_time=$(date +%s)
    
    while true; do
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        
        if [ $elapsed -ge $MAX_WAIT_TIME ]; then
            log_error "Services did not become ready within $MAX_WAIT_TIME seconds"
            show_logs
            exit 1
        fi
        
        # Check if API is responding
        if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
            log_success "API service is ready"
            break
        fi
        
        echo -n "."
        sleep 5
    done
    
    # Additional wait for database to be fully initialized
    log_info "Waiting for database initialization..."
    sleep 10
    
    log_success "All services are ready"
}

# Insert sample data
insert_sample_data() {
    log_info "Inserting sample data..."
    
    if docker-compose exec -T collector python Insert_sample_data.py; then
        log_success "Sample data inserted successfully"
    else
        log_warning "Failed to insert sample data automatically. You can run it manually with:"
        log_warning "docker-compose exec collector python Insert_sample_data.py"
    fi
}

# Run API tests
run_tests() {
    log_info "Running API tests..."
    
    if [ -f "test_api.py" ]; then
        if python3 test_api.py; then
            log_success "API tests completed successfully"
        else
            log_warning "Some API tests failed. Check the test report for details."
        fi
    else
        log_warning "test_api.py not found. Skipping automated tests."
    fi
}

# Show service status
show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    echo ""
    log_info "Available endpoints:"
    echo "  Dashboard: http://localhost:3000"
    echo "  API Documentation: http://localhost:5000/docs"
    echo "  API Health Check: http://localhost:5000/health"
    echo ""
    log_info "Default credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
}

# Show logs for debugging
show_logs() {
    log_info "Recent service logs:"
    echo ""
    log_info "API Logs:"
    docker-compose logs --tail=20 api
    echo ""
    log_info "Database Logs:"
    docker-compose logs --tail=20 postgres
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    docker-compose down
    log_success "Cleanup completed"
}

# Main function
main() {
    echo "🚀 AI Organization Dashboard - Quick Start"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-start}" in
        "start")
            check_prerequisites
            create_env_file
            start_services
            wait_for_services
            insert_sample_data
            run_tests
            show_status
            ;;
        "stop")
            cleanup
            ;;
        "restart")
            cleanup
            start_services
            wait_for_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "test")
            run_tests
            ;;
        "sample-data")
            insert_sample_data
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start        Start all services (default)"
            echo "  stop         Stop all services"
            echo "  restart      Restart all services"
            echo "  status       Show service status"
            echo "  logs         Show recent service logs"
            echo "  test         Run API tests"
            echo "  sample-data  Insert sample data"
            echo "  help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start all services"
            echo "  $0 start              # Start all services"
            echo "  $0 stop               # Stop all services"
            echo "  $0 restart            # Restart all services"
            echo "  $0 test               # Run API tests only"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Make the script executable
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi