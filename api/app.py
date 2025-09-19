from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, UTC
import logging

from starlette import status

from metrics import router as metrics_router
from db import get_dashboard_stats, verify_database_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS for dashboard frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin instead of *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the metrics router
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/stats")
async def get_stats():
    """Get dashboard statistics"""
    try:
        return get_dashboard_stats()
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to fetch dashboard statistics",
                "details": str(e)
            }
        )

@app.get("/health")
async def health_check():
    """Detailed health check including database connectivity"""
    try:
        db_status = verify_database_connection()
        return {
            "success": True,
            "status": "healthy" if db_status["success"] else "degraded",
            "timestamp": datetime.now().isoformat(),
            "database": db_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/auth/login")
def login(request: Request, payload: dict = Body(...)):
    username = payload.get("username")
    password = payload.get("password")
    # For demo, use hardcoded credentials
    if username == "admin" and password == "admin123":
        return {
            "user": {
                "id": "1",
                "name": "admin",
                "email": "admin@dashboard.com"
            },
            "token": f"mock-jwt-token-{datetime.now(UTC).timestamp()}"
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get("/auth/validate")
async def validate_token(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token.startswith("mock-jwt-token-"):
        user = {
            "id": "1",
            "name": "admin",
            "email": "admin@dashboard.com",
            "username": "admin"
        }
        return {"success": True, "data": {"user": user}}
    return JSONResponse(status_code=401, content={"success": False, "error": "Invalid token"})

@app.post("/auth/refresh")
async def refresh_token(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token.startswith("mock-jwt-token-"):
        new_token = f"mock-jwt-token-{datetime.now(UTC).timestamp()}"
        return {"success": True, "data": {"token": new_token}}
    return JSONResponse(status_code=401, content={"success": False, "error": "Invalid token"})

# Error handling for common scenarios
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )
