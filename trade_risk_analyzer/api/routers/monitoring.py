"""
Monitoring Router

Endpoints for starting/stopping market monitoring.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()


class MonitoringRequest(BaseModel):
    """Request to start monitoring"""
    markets: Optional[List[str]] = None
    market_type: str = "spot"  # spot, futures, or both
    quote_currency: str = "USDT"
    min_volume: float = 10000


@router.post("/start")
async def start_monitoring(request: Request, config: MonitoringRequest):
    """
    Start market monitoring
    
    - **markets**: List of specific markets to monitor (optional)
    - **market_type**: Type of markets (spot, futures, both)
    - **quote_currency**: Quote currency filter
    - **min_volume**: Minimum 24h volume threshold
    """
    app_state = request.app.state.app_state
    
    if app_state.get("monitoring_active"):
        return {
            "status": "already_running",
            "message": "Monitoring is already active"
        }
    
    # For now, return success (full implementation requires MCP setup)
    app_state["monitoring_active"] = True
    
    return {
        "status": "started",
        "config": {
            "markets": config.markets or "all",
            "market_type": config.market_type,
            "quote_currency": config.quote_currency,
            "min_volume": config.min_volume
        },
        "message": "Monitoring started successfully"
    }


@router.post("/stop")
async def stop_monitoring(request: Request):
    """Stop market monitoring"""
    app_state = request.app.state.app_state
    
    if not app_state.get("monitoring_active"):
        return {
            "status": "not_running",
            "message": "Monitoring is not active"
        }
    
    app_state["monitoring_active"] = False
    
    return {
        "status": "stopped",
        "message": "Monitoring stopped successfully"
    }


@router.get("/stats")
async def get_monitoring_stats(request: Request):
    """Get monitoring statistics"""
    app_state = request.app.state.app_state
    
    return {
        "monitoring_active": app_state.get("monitoring_active", False),
        "stats": {
            "total_markets": 0,
            "active_markets": 0,
            "total_checks": 0,
            "total_alerts": 0,
            "uptime_seconds": 0
        }
    }
