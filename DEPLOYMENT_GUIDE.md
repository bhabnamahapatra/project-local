# AI Organization Dashboard - Comprehensive Deployment & Testing Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Deployment Instructions](#deployment-instructions)
4. [Configuration Details](#configuration-details)
5. [API Testing Guide](#api-testing-guide)
6. [Troubleshooting](#troubleshooting)
7. [Security Considerations](#security-considerations)

## System Requirements

### Hardware Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 20GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB storage
- **Network**: Internet access for external API integrations

### Software Dependencies
- **Docker**: v20.10+ with Docker Compose v2.0+
- **Node.js**: v18+ (for development mode)
- **Python**: v3.9+ (for development mode)
- **PostgreSQL**: v15+ (if running separately)

### External Service Requirements
The collector component integrates with these AI services (API keys required):
- **OpenAI API**: GPT models
- **GitHub Copilot API**: Code suggestions
- **Anthropic Claude API**: AI assistant
- **Cursor API**: AI code editor

## Environment Setup

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd ai-org-dashboard
```

### 2. Create Environment Configuration
Create a `.env` file in the project root:

```bash
# Database Configuration
DB_HOST=postgres
DB_NAME=metrics_db
DB_USER=metrics_user
DB_PASSWORD=metrics_pass

# External API Keys (Add your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CURSOR_API_KEY=your_cursor_api_key_here

# Optional: Custom ports (uncomment to override defaults)
# POSTGRES_PORT=5432
# API_PORT=5000
# DASHBOARD_PORT=3000
```

### 3. Verify Docker Installation
```bash
docker --version
docker-compose --version
```

## Deployment Instructions

### Method 1: Docker Compose (Recommended)

#### Step 1: Build and Start All Services
```bash
docker-compose up --build
```

#### Step 2: Verify Service Health
Check service status:
```bash
docker-compose ps
```

Expected output:
```
NAME                    SERVICE             STATUS          PORTS
ai-org-dashboard-api-1        api         running         0.0.0.0:5000->5000/tcp
ai-org-dashboard-dashboard-1  dashboard   running         0.0.0.0:3000->80/tcp
ai-org-dashboard-postgres-1   postgres    running         0.0.0.0:5432->5432/tcp
ai-org-dashboard-collector-1 collector   running
```

#### Step 3: Access Applications
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:5000/docs
- **API Health Check**: http://localhost:5000/health

#### Step 4: Insert Sample Data (Optional)
```bash
# Run sample data generator
docker-compose exec collector python Insert_sample_data.py
```

### Method 2: Individual Service Deployment

#### PostgreSQL Database
```bash
# Run PostgreSQL container
docker run -d \
  --name postgres-metrics \
  -e POSTGRES_USER=metrics_user \
  -e POSTGRES_PASSWORD=metrics_pass \
  -e POSTGRES_DB=metrics_db \
  -p 5432:5432 \
  -v db_data:/var/lib/postgresql/data \
  -v $(pwd)/infra/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro \
  postgres:15
```

#### API Service
```bash
cd api
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

#### Dashboard Service
```bash
cd dashboard
npm install
npm run dev
```

#### Collector Service
```bash
cd collector
pip install -r requirements.txt
python collector.py --once
```

## Configuration Details

### Database Configuration
The system uses PostgreSQL with the following schema:
- **openai_metrics**: GPT model usage statistics
- **copilot_metrics**: GitHub Copilot suggestion data
- **claude_metrics**: Anthropic Claude usage metrics
- **cursor_metrics**: Cursor editor analytics

### API Configuration
Key environment variables for the API service:
```bash
DB_HOST=postgres              # Database hostname
DB_NAME=metrics_db              # Database name
DB_USER=metrics_user            # Database user
DB_PASSWORD=metrics_pass        # Database password
PORT=5000                       # API port
HOST=0.0.0.0                    # API host
CORS_ORIGINS=http://localhost:3000  # Frontend origin
```

### Dashboard Configuration
```bash
VITE_API_URL=http://localhost:5000  # API endpoint URL
```

### Collector Configuration
The collector supports multiple execution modes:
```bash
# Run once and exit
python collector.py --once

# Run continuously with interval
python collector.py --interval 3600  # Run every hour

# Run for specific providers only
python collector.py --providers openai,claude
```

## API Testing Guide

### Authentication Testing

#### 1. Login Endpoint
**Request:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": "1",
    "name": "admin",
    "email": "admin@dashboard.com"
  },
  "token": "mock-jwt-token-1234567890"
}
```

#### 2. Token Validation
**Request:**
```bash
curl -X GET http://localhost:5000/auth/validate \
  -H "Authorization: Bearer mock-jwt-token-1234567890"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "1",
      "name": "admin",
      "email": "admin@dashboard.com",
      "username": "admin"
    }
  }
}
```

### Metrics API Testing

#### 1. Health Check
**Request:**
```bash
curl -X GET http://localhost:5000/health
```

**Expected Response:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": {
    "success": true,
    "tables": {
      "openai_metrics": 150,
      "copilot_metrics": 75,
      "claude_metrics": 100,
      "cursor_metrics": 50
    }
  }
}
```

#### 2. Get All Metrics
**Request:**
```bash
curl -X GET "http://localhost:5000/metrics/?start_date=2024-01-01&end_date=2024-01-31&sort_by=timestamp&sort_order=desc"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "openai": [
      {
        "id": 1,
        "applicationId": "chatgpt",
        "timestamp": "2024-01-15T10:00:00Z",
        "responseTime": 0.5,
        "requestCount": 100,
        "errorRate": 2.5,
        "successRate": 97.5,
        "averageTokens": 150.5,
        "cost": 0.25,
        "uptime": 99.9,
        "model": "gpt-3.5"
      }
    ],
    "copilot": [...],
    "claude": [...],
    "cursor": [...]
  }
}
```

#### 3. Get OpenAI Metrics
**Request:**
```bash
curl -X GET "http://localhost:5000/metrics/openai?start_date=2024-01-01&end_date=2024-01-31&sort_by=responseTime&sort_order=asc"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "applicationId": "chatgpt",
      "timestamp": "2024-01-15T10:00:00Z",
      "responseTime": 0.3,
      "requestCount": 100,
      "errorRate": 1.2,
      "successRate": 98.8,
      "averageTokens": 150.5,
      "promptTokens": 75,
      "completionTokens": 75,
      "totalTokens": 150,
      "cost": 0.25,
      "uptime": 99.9,
      "model": "gpt-3.5"
    }
  ]
}
```

#### 4. Get Copilot Metrics
**Request:**
```bash
curl -X GET "http://localhost:5000/metrics/copilot?start_date=2024-01-01&end_date=2024-01-31"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "applicationId": "copilot",
      "timestamp": "2024-01-15T10:00:00Z",
      "requestCount": 200,
      "errorRate": 15.5,
      "successRate": 84.5,
      "averageTokens": 25.3,
      "totalTokens": 5060,
      "uptime": 100,
      "totalSuggestions": 200,
      "acceptedSuggestions": 169,
      "totalUsers": 25,
      "linesSuggested": 1000,
      "linesAccepted": 845
    }
  ]
}
```

#### 5. Get Claude Metrics
**Request:**
```bash
curl -X GET "http://localhost:5000/metrics/claude?start_date=2024-01-01&end_date=2024-01-31"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "applicationId": "claude",
      "timestamp": "2024-01-15T10:00:00Z",
      "responseTime": 0.8,
      "requestCount": 80,
      "errorRate": 0.5,
      "successRate": 99.5,
      "averageTokens": 200.2,
      "promptTokens": 100,
      "completionTokens": 100,
      "totalTokens": 200,
      "cost": 0.40,
      "uptime": 99.9,
      "model": "claude-2"
    }
  ]
}
```

#### 6. Get Cursor Metrics
**Request:**
```bash
curl -X GET "http://localhost:5000/metrics/cursor?start_date=2024-01-01&end_date=2024-01-31"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "applicationId": "cursor",
      "timestamp": "2024-01-15T10:00:00Z",
      "requestCount": 500,
      "errorRate": 8.2,
      "successRate": 91.8,
      "averageTokens": 40.5,
      "totalTokens": 20250,
      "uptime": 95.5,
      "totalSeats": 100,
      "activeUsers": 75,
      "utilizationRate": 75.0,
      "monthlyActiveUsers": 80,
      "weeklyActiveUsers": 70,
      "dailyActiveUsers": 60,
      "totalInteractions": 500,
      "acceptedSuggestions": 459,
      "totalCost": 5.25
    }
  ]
}
```

#### 7. Get Aggregated Statistics
**Request:**
```bash
curl -X GET http://localhost:5000/metrics/stats
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "totalRequests": 880,
    "averageResponseTime": 0.53,
    "totalCost": 6.15,
    "averageSuccessRate": 93.2,
    "totalTokens": 45660,
    "applications": {
      "openai": {
        "totalRequests": 100,
        "averageResponseTime": 0.5,
        "totalCost": 0.25,
        "averageSuccessRate": 97.5,
        "totalTokens": 150
      },
      "copilot": {
        "totalRequests": 200,
        "averageResponseTime": 0,
        "totalCost": 0,
        "averageSuccessRate": 84.5,
        "totalTokens": 5060
      },
      "claude": {
        "totalRequests": 80,
        "averageResponseTime": 0.8,
        "totalCost": 0.4,
        "averageSuccessRate": 99.5,
        "totalTokens": 200
      },
      "cursor": {
        "totalRequests": 500,
        "averageResponseTime": 0,
        "totalCost": 5.25,
        "averageSuccessRate": 91.8,
        "totalTokens": 20250
      }
    }
  }
}
```

### Load Testing with Apache Bench
```bash
# Test health endpoint with 1000 requests
ab -n 1000 -c 10 http://localhost:5000/health

# Test metrics endpoint with authentication
ab -n 500 -c 5 -H "Authorization: Bearer mock-jwt-token-1234567890" \
   http://localhost:5000/metrics/stats
```

## Error Handling Scenarios

### Common Error Responses

#### 401 Unauthorized
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

#### 404 Not Found
```json
{
  "success": false,
  "error": "Endpoint not found"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error"
}
```

#### Database Connection Error
```json
{
  "success": false,
  "status": "unhealthy",
  "error": "Database connection failed",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Symptoms**: API returns database errors
**Solution**:
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Verify database initialization
docker-compose exec postgres psql -U metrics_user -d metrics_db -c "\dt"
```

#### 2. Collector Not Fetching Data
**Symptoms**: No data in metrics tables
**Solution**:
```bash
# Check collector logs
docker-compose logs collector

# Verify API keys in .env file
grep -E "(OPENAI|GITHUB|ANTHROPIC|CURSOR)" .env

# Run collector manually
docker-compose exec collector python collector.py --once --verbose
```

#### 3. Dashboard Not Loading
**Symptoms**: Blank page or connection errors
**Solution**:
```bash
# Check dashboard logs
docker-compose logs dashboard

# Verify API URL configuration
docker-compose exec dashboard printenv | grep VITE_API_URL

# Rebuild dashboard
docker-compose build dashboard --no-cache
```

#### 4. CORS Issues
**Symptoms**: Browser blocks API requests
**Solution**:
```bash
# Check CORS configuration in API
docker-compose exec api env | grep CORS

# Update CORS origins in docker-compose.yml
# Rebuild and restart API service
docker-compose build api
docker-compose restart api
```

### Performance Monitoring

#### Database Performance
```bash
# Check query performance
docker-compose exec postgres psql -U metrics_user -d metrics_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"
```

#### API Performance
```bash
# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/metrics/stats
```

Create `curl-format.txt`:
```
time_namelookup:  %{time_namelookup}\ntime_connect:     %{time_connect}\ntime_appconnect:  %{time_appconnect}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect:    %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total:       %{time_total}\n\n```

## Security Considerations

### Development Environment
⚠️ **WARNING**: The current authentication system uses hardcoded demo credentials and should NOT be used in production.

- **Username**: `admin`
- **Password**: `admin123`
- **Token**: `mock-jwt-token-*`

### Production Security Checklist

#### 1. Authentication
- [ ] Replace demo auth with proper JWT/OAuth2 implementation
- [ ] Implement user management system
- [ ] Add password complexity requirements
- [ ] Enable multi-factor authentication (MFA)

#### 2. API Security
- [ ] Implement rate limiting
- [ ] Add request validation and sanitization
- [ ] Use HTTPS with proper SSL certificates
- [ ] Implement API key management for external services

#### 3. Database Security
- [ ] Use strong database passwords
- [ ] Enable database encryption at rest
- [ ] Implement database connection pooling with limits
- [ ] Regular database backups and recovery testing

#### 4. Network Security
- [ ] Configure firewall rules
- [ ] Use VPN for database access
- [ ] Implement network segmentation
- [ ] Enable container security scanning

#### 5. Secrets Management
- [ ] Use environment variables for sensitive data
- [ ] Implement secrets rotation policy
- [ ] Use secret management tools (HashiCorp Vault, AWS Secrets Manager)
- [ ] Never commit secrets to version control

### Security Testing

#### API Security Tests
```bash
# Test SQL injection
curl -X GET "http://localhost:5000/metrics/openai?sort_by=timestamp;DROP TABLE users;--"

# Test authentication bypass
curl -X GET http://localhost:5000/metrics/stats \
  -H "Authorization: Bearer invalid-token"

# Test rate limiting (if implemented)
for i in {1..100}; do curl -s http://localhost:5000/health; done
```

#### Container Security
```bash
# Scan Docker images for vulnerabilities
docker scan ai-org-dashboard-api:latest
docker scan ai-org-dashboard-dashboard:latest

# Check container permissions
docker-compose exec api ls -la /app
docker-compose exec api whoami
```

## Maintenance and Operations

### Regular Maintenance Tasks

#### Daily
- [ ] Monitor service health endpoints
- [ ] Check error logs for anomalies
- [ ] Verify data collection is working

#### Weekly
- [ ] Review API performance metrics
- [ ] Check database storage usage
- [ ] Update external API keys if needed

#### Monthly
- [ ] Update Docker images and dependencies
- [ ] Review and rotate secrets
- [ ] Backup database and test recovery
- [ ] Security audit and vulnerability scanning

### Backup and Recovery

#### Database Backup
```bash
# Create database backup
docker-compose exec postgres pg_dump -U metrics_user metrics_db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U metrics_user metrics_db < backup_20240115.sql
```

### Scaling Considerations

#### Horizontal Scaling
- Use container orchestration (Kubernetes, Docker Swarm)
- Implement load balancing for API services
- Use managed database services (RDS, Cloud SQL)

#### Performance Optimization
- Add Redis caching layer
- Implement database read replicas
- Use CDN for static assets
- Optimize database queries with proper indexing

---

## Support and Resources

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Useful Commands Reference
```bash
# View all logs
docker-compose logs -f

# Restart specific service
docker-compose restart api

# Scale services
docker-compose up -d --scale api=3

# Clean up
docker-compose down -v  # Remove volumes too
docker system prune -a  # Clean unused images
```

### Getting Help
If you encounter issues:
1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs <service-name>`
3. Verify configuration files and environment variables
4. Test individual components separately
5. Consult the documentation links provided

---

**Last Updated**: January 2024
**Version**: 1.0.0