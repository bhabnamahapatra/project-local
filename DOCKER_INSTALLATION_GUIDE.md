# 🐳 Docker Installation & Deployment Guide

## Current Status: Docker Not Installed

Docker is required to run `docker-compose up` and start the AI Organization Dashboard services. Here's how to install it and deploy your system.

## 📦 Docker Installation

### macOS Installation Options:

#### Option 1: Docker Desktop (Recommended)
```bash
# Download from Docker official website
open https://www.docker.com/products/docker-desktop

# Or install via Homebrew
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### Option 2: Colima (Lightweight Alternative)
```bash
# Install Colima for container management
brew install colima

# Start Colima
colima start --cpu 2 --memory 4 --disk 60

# Install Docker CLI
brew install docker
brew install docker-compose
```

#### Option 3: OrbStack (Fast & Lightweight)
```bash
# Install OrbStack
brew install orbstack

# Start OrbStack
open -a OrbStack
```

## 🚀 Deployment Commands

### Once Docker is installed, run:

```bash
# Start all services in detached mode
docker-compose up -d

# View real-time logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## 📋 What Will Happen When You Run `docker-compose up`

### Services Started:
1. **🗄️ PostgreSQL Database** (Port 5432)
   - Database: `ai_metrics`
   - User: `postgres`
   - Persistent volume: `db_data`
   - Initialization: `infra/init-db.sql`

2. **🚀 API Service** (Port 8000)
   - Flask application
   - Health check endpoint: `/health`
   - Database connection pooling

3. **📈 Collector Service** (Port 8080)
   - Metrics collection every 5 minutes
   - Supports OpenAI, GitHub Copilot, Claude, Cursor
   - Cron-based scheduling

4. **📊 Dashboard** (Port 3000)
   - React + TypeScript
   - Vite development server
   - Real-time metrics visualization

### Database Schema Created:
```sql
-- Tables created automatically:
- openai_metrics
- copilot_metrics  
- claude_metrics
- cursor_metrics
- unified_metrics (view)
```

## 🔧 Configuration Checklist

Before running `docker-compose up`, ensure:

### ✅ Environment Variables Set:
```bash
# Check your .env file
cat .env

# Should contain:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
POSTGRES_PASSWORD=your_secure_password
```

### ✅ Ports Available:
```bash
# Check if ports are free
lsof -i :3000  # Dashboard
lsof -i :8000  # API
lsof -i :5432  # Database
lsof -i :8080  # Collector
```

### ✅ System Resources:
- **Minimum**: 2 CPU cores, 4GB RAM, 10GB disk
- **Recommended**: 4 CPU cores, 8GB RAM, 20GB disk

## 📊 Verification Steps

After deployment, verify everything is working:

```bash
# 1. Check container status
docker-compose ps

# 2. Test database connection
docker-compose exec postgres psql -U postgres -d ai_metrics -c "SELECT version();"

# 3. Test API health
curl http://localhost:8000/health

# 4. Check dashboard
curl http://localhost:3000

# 5. View logs for any issues
docker-compose logs --tail=50
```

## 🎯 Success Indicators

### ✅ All Services Healthy:
```
Name                    Command                  State    Ports
-----------------------------------------------------------------
ai-org-dashboard-api_1        python app.py                  Up      0.0.0.0:8000->8000/tcp
ai-org-dashboard-collector_1  python collector.py            Up      0.0.0.0:8080->8080/tcp  
ai-org-dashboard-dashboard_1  npm run dev                    Up      0.0.0.0:3000->3000/tcp
ai-org-dashboard-postgres_1     docker-entrypoint.sh postgres  Up      0.0.0.0:5432->5432/tcp
```

### ✅ Dashboard Accessible:
- **URL**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (if available)
- **Health Check**: http://localhost:8000/health

## 🚨 Common Issues & Solutions

### Issue 1: Port Already in Use
```bash
# Find and kill process using port
lsof -ti:3000 | xargs kill -9
```

### Issue 2: Docker Daemon Not Running
```bash
# Start Docker daemon
open -a Docker
# or for Colima
colima start
```

### Issue 3: Insufficient Resources
```bash
# Increase Docker memory limit (Docker Desktop)
# Go to Docker Desktop → Settings → Resources → Memory

# For Colima
colima stop
colima start --cpu 4 --memory 8 --disk 60
```

### Issue 4: Database Connection Failed
```bash
# Check database logs
docker-compose logs postgres

# Reset database volume
docker-compose down -v
docker-compose up -d
```

## 🔄 Next Steps After Installation

1. **Install Docker** using one of the methods above
2. **Configure API keys** in your `.env` file
3. **Run deployment command**: `docker-compose up -d`
4. **Access dashboard** at http://localhost:3000
5. **Monitor logs** for any issues

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test individual services: `docker-compose up [service-name]`

Your system is **100% ready** for deployment once Docker is installed! 🎉