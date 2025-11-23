"""
Feedback Router

Endpoints for submitting feedback and triggering model retraining.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from trade_risk_analyzer.core.logger import get_logger

# Placeholder imports - these will be implemented when feedback module is complete
try:
    from trade_risk_analyzer.feedback.collector import FeedbackCollector
    from trade_risk_analyzer.feedback.retraining import ModelRetrainer
except ImportError:
    FeedbackCollector = None
    ModelRetrainer = None

router = APIRouter()
logger = get_logger(__name__)

# In-memory job tracking
retraining_jobs = {}


class FeedbackSubmission(BaseModel):
    """Feedback submission"""
    alert_id: int
    is_correct: bool
    comments: Optional[str] = None
    user_id: Optional[str] = None


class RetrainingJob:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = "pending"
        self.message = "Retraining queued"
        self.model_version = None
        self.metrics = None
        self.created_at = datetime.now()
        self.completed_at = None


async def process_retraining(job_id: str):
    """Background task to retrain models"""
    job = retraining_jobs[job_id]
    
    try:
        job.status = "processing"
        job.message = "Retraining models..."
        
        # Initialize retrainer
        retrainer = ModelRetrainer()
        
        # Retrain models
        result = retrainer.retrain_with_feedback()
        
        job.model_version = result.get("version")
        job.metrics = result.get("metrics")
        job.status = "completed"
        job.message = f"Retraining completed. New model version: {job.model_version}"
        job.completed_at = datetime.now()
        
        logger.info(f"Retraining job {job_id} completed: version {job.model_version}")
        
    except Exception as e:
        logger.error(f"Retraining job {job_id} failed: {e}", exc_info=True)
        job.status = "failed"
        job.message = f"Error: {str(e)}"
        job.completed_at = datetime.now()


@router.post("")
async def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit feedback on an alert
    
    - **alert_id**: ID of the alert being reviewed
    - **is_correct**: Whether the alert was correct (true/false)
    - **comments**: Optional comments about the alert
    - **user_id**: Optional user ID of the reviewer
    """
    if FeedbackCollector is None:
        raise HTTPException(status_code=501, detail="Feedback module not yet implemented")
    
    try:
        collector = FeedbackCollector()
        
        feedback_id = collector.submit_feedback(
            alert_id=feedback.alert_id,
            is_correct=feedback.is_correct,
            comments=feedback.comments,
            reviewer_id=feedback.user_id
        )
        
        logger.info(f"Feedback submitted: alert_id={feedback.alert_id}, is_correct={feedback.is_correct}")
        
        return {
            "feedback_id": feedback_id,
            "status": "success",
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/stats")
async def get_feedback_stats():
    """
    Get feedback statistics
    
    Returns summary of feedback submissions including:
    - Total feedback count
    - Correct vs incorrect alerts
    - Feedback by alert type
    """
    try:
        collector = FeedbackCollector()
        stats = collector.get_feedback_stats()
        
        return {
            "total_feedback": stats.get("total", 0),
            "correct_alerts": stats.get("correct", 0),
            "incorrect_alerts": stats.get("incorrect", 0),
            "accuracy_rate": stats.get("accuracy_rate", 0),
            "by_alert_type": stats.get("by_type", {})
        }
        
    except Exception as e:
        logger.error(f"Error retrieving feedback stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@router.post("/models/retrain")
async def trigger_retraining(background_tasks: BackgroundTasks):
    """
    Trigger model retraining with feedback data
    
    This will retrain all models using the accumulated feedback.
    Returns a job ID for tracking the retraining progress.
    """
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = RetrainingJob(job_id)
        retraining_jobs[job_id] = job
        
        # Queue background processing
        background_tasks.add_task(process_retraining, job_id)
        
        logger.info(f"Retraining job {job_id} created")
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Model retraining queued successfully"
        }
        
    except Exception as e:
        logger.error(f"Error triggering retraining: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger retraining: {str(e)}")


@router.get("/models/retrain/{job_id}")
async def get_retraining_status(job_id: str):
    """
    Get retraining job status
    
    - **job_id**: Job ID returned from retrain endpoint
    """
    if job_id not in retraining_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = retraining_jobs[job_id]
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "message": job.message,
        "model_version": job.model_version,
        "metrics": job.metrics,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }


@router.get("/models/versions")
async def get_model_versions():
    """
    Get all model versions and their performance metrics
    
    Returns a list of all trained model versions with their metrics.
    """
    try:
        retrainer = ModelRetrainer()
        versions = retrainer.get_model_versions()
        
        return {
            "versions": versions,
            "current_version": versions[0] if versions else None
        }
        
    except Exception as e:
        logger.error(f"Error retrieving model versions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model versions: {str(e)}")


@router.get("/models/performance")
async def get_model_performance():
    """
    Get current model performance metrics
    
    Returns performance metrics for the currently active models.
    """
    try:
        retrainer = ModelRetrainer()
        performance = retrainer.get_current_performance()
        
        return {
            "model_version": performance.get("version"),
            "metrics": performance.get("metrics"),
            "last_updated": performance.get("last_updated")
        }
        
    except Exception as e:
        logger.error(f"Error retrieving model performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance metrics: {str(e)}")
