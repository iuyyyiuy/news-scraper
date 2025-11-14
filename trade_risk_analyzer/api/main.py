"""
Main FastAPI Application

Entry point for the Trade Risk Analyzer REST API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.api.routers import markets, monitoring, analysis, health, trades, alerts, config, feedback


logger = get_logger(__name__)


# Global state
app_state = {
    "monitoring_active": False,
    "mcp_client": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Trade Risk Analyzer API...")
    yield
    # Shutdown
    logger.info("Shutting down Trade Risk Analyzer API...")
    if app_state.get("mcp_client"):
        await app_state["mcp_client"].disconnect()


# Create FastAPI app
app = FastAPI(
    title="Trade Risk Analyzer API",
    description="REST API for cryptocurrency market monitoring and risk analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests"""
    logger.info(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "details": str(e)
                }
            }
        )


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(trades.router, prefix="/api/v1/trades", tags=["Trades"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(markets.router, prefix="/api/v1/markets", tags=["Markets"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Trade Risk Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Make app_state accessible to routers
app.state.app_state = app_state
