"""
Analysis Router

Endpoints for triggering analysis and retrieving results.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from trade_risk_analyzer.core.logger import get_logger

# Placeholder imports - these will be implemented when modules are complete
try:
    from trade_risk_analyzer.detection.engine import DetectionEngine
    from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
except ImportError:
    DetectionEngine = None
    DatabaseStorage = None

router = APIRouter()
logger = get_logger(__name__)

# In-memory job tracking
analysis_jobs = {}


class AnalysisJob:
    def __init__(self, job_id: str, start_date: Optional[datetime], end_date: Optional[datetime], user_ids: Optional[List[str]]):
        self.job_id = job_id
        self.status = "pending"
        self.message = "Analysis queued"
        self.start_date = start_date
        self.end_date = end_date
        self.user_ids = user_ids
        self.total_trades = 0
        self.alerts_generated = 0
        self.high_risk_count = 0
        self.medium_risk_count = 0
        self.low_risk_count = 0
        self.created_at = datetime.now()
        self.completed_at = None
        self.results = None


class AnalysisRequest(BaseModel):
    """Request to run analysis"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    user_ids: Optional[List[str]] = None


async def process_analysis(job_id: str, start_date: Optional[datetime], end_date: Optional[datetime], user_ids: Optional[List[str]]):
    """Background task to process analysis"""
    job = analysis_jobs[job_id]
    
    try:
        if DetectionEngine is None or DatabaseStorage is None:
            job.status = "failed"
            job.message = "Analysis module not yet fully implemented"
            job.completed_at = datetime.now()
            return
        
        job.status = "processing"
        job.message = "Running analysis..."
        
        # Initialize components
        storage = DatabaseStorage()
        engine = DetectionEngine()
        
        # Fetch trades from database
        trades_df = storage.get_trades(
            start_date=start_date,
            end_date=end_date,
            user_ids=user_ids
        )
        
        if trades_df.empty:
            job.status = "completed"
            job.message = "No trades found for the specified criteria"
            job.completed_at = datetime.now()
            return
        
        job.total_trades = len(trades_df)
        
        # Run detection
        alerts = engine.analyze_batch(trades_df)
        
        # Count alerts by risk level
        job.alerts_generated = len(alerts)
        job.high_risk_count = sum(1 for a in alerts if a.risk_level.value == "HIGH")
        job.medium_risk_count = sum(1 for a in alerts if a.risk_level.value == "MEDIUM")
        job.low_risk_count = sum(1 for a in alerts if a.risk_level.value == "LOW")
        
        # Store results
        job.results = {
            "total_trades": job.total_trades,
            "alerts_generated": job.alerts_generated,
            "risk_distribution": {
                "high": job.high_risk_count,
                "medium": job.medium_risk_count,
                "low": job.low_risk_count
            },
            "alerts": [
                {
                    "user_id": a.user_id,
                    "alert_type": a.alert_type.value,
                    "risk_level": a.risk_level.value,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in alerts[:100]  # Limit to first 100 alerts
            ]
        }
        
        job.status = "completed"
        job.message = f"Analysis completed: {job.alerts_generated} alerts generated"
        job.completed_at = datetime.now()
        
        logger.info(f"Analysis job {job_id} completed: {job.alerts_generated} alerts from {job.total_trades} trades")
        
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {e}", exc_info=True)
        job.status = "failed"
        job.message = f"Error: {str(e)}"
        job.completed_at = datetime.now()


@router.post("/run")
async def run_analysis(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest
):
    """
    Trigger batch analysis on historical trade data
    
    - **start_date**: Start date for analysis (ISO format, optional)
    - **end_date**: End date for analysis (ISO format, optional)
    - **user_ids**: List of user IDs to analyze (optional, analyzes all if not specified)
    
    Returns a job ID for tracking the analysis
    """
    # Parse dates
    start_date = datetime.fromisoformat(request.start_date) if request.start_date else None
    end_date = datetime.fromisoformat(request.end_date) if request.end_date else None
    
    # Create job
    job_id = str(uuid.uuid4())
    job = AnalysisJob(job_id, start_date, end_date, request.user_ids)
    analysis_jobs[job_id] = job
    
    # Queue background processing
    background_tasks.add_task(
        process_analysis,
        job_id,
        start_date,
        end_date,
        request.user_ids
    )
    
    logger.info(f"Analysis job {job_id} created")
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Analysis queued successfully"
    }


@router.get("/{job_id}")
async def get_analysis_result(job_id: str):
    """
    Get analysis results by job ID
    
    - **job_id**: Job identifier returned from /run endpoint
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    response = {
        "job_id": job.job_id,
        "status": job.status,
        "message": job.message,
        "total_trades": job.total_trades,
        "alerts_generated": job.alerts_generated,
        "risk_distribution": {
            "high": job.high_risk_count,
            "medium": job.medium_risk_count,
            "low": job.low_risk_count
        },
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }
    
    if job.results:
        response["results"] = job.results
    
    return response
