"""
Trades Router

Endpoints for trade data upload and management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
import pandas as pd
import io
import uuid
from datetime import datetime

from trade_risk_analyzer.core.logger import get_logger

# Placeholder imports
try:
    from trade_risk_analyzer.data_ingestion.importer import TradeDataImporter
    from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
except ImportError:
    TradeDataImporter = None
    DatabaseStorage = None

router = APIRouter()
logger = get_logger(__name__)

# In-memory job tracking (in production, use Redis or database)
upload_jobs = {}


class UploadJob:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = "pending"
        self.message = "Upload queued"
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.errors = []
        self.created_at = datetime.now()
        self.completed_at = None


async def process_upload(job_id: str, file_content: bytes, filename: str, file_type: str):
    """Background task to process uploaded file"""
    job = upload_jobs[job_id]
    
    try:
        if TradeDataImporter is None or DatabaseStorage is None:
            job.status = "failed"
            job.message = "Data ingestion module not yet fully implemented"
            job.completed_at = datetime.now()
            return
        
        job.status = "processing"
        job.message = "Processing file..."
        
        # Initialize importer and storage
        importer = TradeDataImporter()
        storage = DatabaseStorage()
        
        # Parse file based on type
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(file_content))
        elif file_type == "json":
            df = pd.read_json(io.BytesIO(file_content))
        elif file_type in ["xlsx", "xls"]:
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        job.total_records = len(df)
        
        # Validate data
        validation_result = importer.validate_data(df)
        
        if not validation_result.is_valid:
            job.status = "failed"
            job.message = "Validation failed"
            job.errors = validation_result.errors
            job.invalid_records = len(validation_result.errors)
            job.completed_at = datetime.now()
            return
        
        # Store valid records
        valid_df = df[validation_result.valid_indices]
        storage.store_trades(valid_df)
        
        job.valid_records = len(valid_df)
        job.invalid_records = job.total_records - job.valid_records
        job.status = "completed"
        job.message = f"Successfully imported {job.valid_records} records"
        job.completed_at = datetime.now()
        
        logger.info(f"Upload job {job_id} completed: {job.valid_records}/{job.total_records} records imported")
        
    except Exception as e:
        logger.error(f"Upload job {job_id} failed: {e}", exc_info=True)
        job.status = "failed"
        job.message = f"Error: {str(e)}"
        job.errors = [str(e)]
        job.completed_at = datetime.now()


@router.post("/upload")
async def upload_trades(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload trade data file
    
    Supports CSV, JSON, and Excel formats.
    Returns a job ID for tracking upload status.
    
    - **file**: Trade data file (CSV, JSON, or Excel)
    """
    # Validate file type
    filename = file.filename.lower()
    if filename.endswith('.csv'):
        file_type = 'csv'
    elif filename.endswith('.json'):
        file_type = 'json'
    elif filename.endswith(('.xlsx', '.xls')):
        file_type = 'xlsx'
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload CSV, JSON, or Excel file."
        )
    
    # Validate file size (max 50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 50MB."
        )
    
    # Create job
    job_id = str(uuid.uuid4())
    job = UploadJob(job_id)
    upload_jobs[job_id] = job
    
    # Queue background processing
    background_tasks.add_task(
        process_upload,
        job_id,
        content,
        file.filename,
        file_type
    )
    
    logger.info(f"Upload job {job_id} created for file: {file.filename}")
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "File upload queued for processing"
    }


@router.get("/upload/{job_id}")
async def get_upload_status(job_id: str):
    """
    Get upload job status
    
    - **job_id**: Job ID returned from upload endpoint
    """
    if job_id not in upload_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = upload_jobs[job_id]
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "message": job.message,
        "total_records": job.total_records,
        "valid_records": job.valid_records,
        "invalid_records": job.invalid_records,
        "errors": job.errors[:10] if job.errors else [],  # Limit to first 10 errors
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }
