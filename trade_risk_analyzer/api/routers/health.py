"""
Health Check Router

Provides health check and status endpoints.
"""

from fastapi import APIRouter
from datetime import datetime
import psutil
import platform


router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/status")
async def system_status():
    """Detailed system status"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }
