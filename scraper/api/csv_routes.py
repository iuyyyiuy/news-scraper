"""
CSV Export API Routes
Provides endpoints for exporting articles to CSV format with filtering
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from scraper.core.csv_exporter import CSVExportService, CSVExportConfig

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/export", tags=["CSV Export"])

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=3)

# Global CSV service
csv_service = CSVExportService()

# Pydantic models
class CSVExportRequest(BaseModel):
    """Request model for CSV export"""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    sources: Optional[List[str]] = Field(None, description="Source filters (e.g., ['BlockBeats', 'Jinse'])")
    keywords: Optional[List[str]] = Field(None, description="Keyword filters")
    include_content: bool = Field(True, description="Include full article content")
    max_records: Optional[int] = Field(None, description="Maximum number of records", ge=1, le=10000)
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    @validator('sources')
    def validate_sources(cls, v):
        if v is not None:
            valid_sources = ['BlockBeats', 'Jinse', 'blockbeats', 'jinse']
            for source in v:
                if source not in valid_sources:
                    raise ValueError(f'Invalid source: {source}. Valid sources: {valid_sources}')
        return v
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None:
            return [kw.strip() for kw in v if kw.strip()]
        return v

class CSVExportResponse(BaseModel):
    """Response model for CSV export"""
    success: bool
    message: str
    file_id: Optional[str] = None
    download_url: Optional[str] = None
    articles_count: int = 0
    duration_seconds: Optional[float] = None
    filters_applied: Optional[Dict[str, Any]] = None

class CSVExportStatus(BaseModel):
    """Status model for CSV export"""
    file_id: str
    status: str  # 'processing', 'completed', 'failed', 'not_found'
    message: str
    articles_count: int = 0
    created_at: Optional[str] = None
    file_size: Optional[int] = None

# In-memory storage for export status (in production, use Redis or database)
export_status: Dict[str, Dict[str, Any]] = {}

def create_csv_config(request: CSVExportRequest) -> CSVExportConfig:
    """Create CSVExportConfig from request"""
    config = CSVExportConfig(
        include_content=request.include_content,
        max_records=request.max_records
    )
    
    # Parse dates
    if request.start_date:
        config.start_date = datetime.strptime(request.start_date, '%Y-%m-%d').date()
    
    if request.end_date:
        config.end_date = datetime.strptime(request.end_date, '%Y-%m-%d').date()
    
    # Set filters
    if request.sources:
        config.sources = request.sources
    
    if request.keywords:
        config.keywords = request.keywords
    
    return config

def run_csv_export_task(file_id: str, config: CSVExportConfig):
    """Background task to run CSV export"""
    try:
        logger.info(f"Starting CSV export task for file_id: {file_id}")
        
        # Update status to processing
        export_status[file_id] = {
            'status': 'processing',
            'message': 'Export in progress...',
            'articles_count': 0,
            'created_at': datetime.now().isoformat()
        }
        
        # Run export
        result = csv_service.export_articles(config)
        
        if result['success']:
            # Update status to completed
            file_size = os.path.getsize(result['file_path']) if result['file_path'] else 0
            export_status[file_id] = {
                'status': 'completed',
                'message': result['message'],
                'articles_count': result['articles_count'],
                'created_at': datetime.now().isoformat(),
                'file_path': result['file_path'],
                'file_size': file_size
            }
            logger.info(f"CSV export completed for file_id: {file_id}")
        else:
            # Update status to failed
            export_status[file_id] = {
                'status': 'failed',
                'message': result['message'],
                'articles_count': 0,
                'created_at': datetime.now().isoformat()
            }
            logger.error(f"CSV export failed for file_id: {file_id}: {result['message']}")
            
    except Exception as e:
        logger.error(f"CSV export task error for file_id: {file_id}: {str(e)}", exc_info=True)
        export_status[file_id] = {
            'status': 'failed',
            'message': f'Export failed: {str(e)}',
            'articles_count': 0,
            'created_at': datetime.now().isoformat()
        }

@router.post("/csv", response_model=CSVExportResponse)
async def export_csv(request: CSVExportRequest, background_tasks: BackgroundTasks):
    """
    Export articles to CSV format with optional filtering
    
    - **start_date**: Filter articles from this date (YYYY-MM-DD)
    - **end_date**: Filter articles until this date (YYYY-MM-DD)
    - **sources**: Filter by news sources (e.g., ['BlockBeats', 'Jinse'])
    - **keywords**: Filter by keywords in title or content
    - **include_content**: Include full article content in CSV
    - **max_records**: Maximum number of records to export
    """
    try:
        logger.info(f"CSV export request: {request}")
        
        # Create configuration
        config = create_csv_config(request)
        
        # For small exports, process synchronously
        if request.max_records and request.max_records <= 1000:
            result = csv_service.export_articles(config)
            
            if result['success']:
                file_id = result['file_id']
                return CSVExportResponse(
                    success=True,
                    message="Export completed successfully",
                    file_id=file_id,
                    download_url=f"/api/export/download/{file_id}",
                    articles_count=result['articles_count'],
                    duration_seconds=result['duration_seconds'],
                    filters_applied=result['filters_applied']
                )
            else:
                raise HTTPException(status_code=400, detail=result['message'])
        
        # For large exports, process asynchronously
        else:
            # Generate file ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_id = f"export_{timestamp}_{hash(str(config)) % 10000:04d}.csv"
            
            # Start background task
            background_tasks.add_task(run_csv_export_task, file_id, config)
            
            return CSVExportResponse(
                success=True,
                message="Export started. Use the status endpoint to check progress.",
                file_id=file_id,
                download_url=f"/api/export/download/{file_id}",
                articles_count=0
            )
            
    except ValueError as e:
        logger.error(f"CSV export validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/csv/status/{file_id}", response_model=CSVExportStatus)
async def get_export_status(file_id: str):
    """
    Get the status of a CSV export operation
    
    - **file_id**: The file ID returned from the export request
    """
    try:
        if file_id not in export_status:
            # Check if file exists directly (for synchronous exports)
            file_path = csv_service.get_export_file(file_id)
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                return CSVExportStatus(
                    file_id=file_id,
                    status="completed",
                    message="Export completed",
                    created_at=datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    file_size=file_size
                )
            else:
                return CSVExportStatus(
                    file_id=file_id,
                    status="not_found",
                    message="Export not found"
                )
        
        status_info = export_status[file_id]
        return CSVExportStatus(
            file_id=file_id,
            status=status_info['status'],
            message=status_info['message'],
            articles_count=status_info['articles_count'],
            created_at=status_info['created_at'],
            file_size=status_info.get('file_size')
        )
        
    except Exception as e:
        logger.error(f"Error getting export status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/download/{file_id}")
async def download_csv(file_id: str):
    """
    Download a CSV export file
    
    - **file_id**: The file ID returned from the export request
    """
    try:
        # Check if export is completed
        if file_id in export_status:
            status_info = export_status[file_id]
            if status_info['status'] == 'processing':
                raise HTTPException(status_code=202, detail="Export still in progress")
            elif status_info['status'] == 'failed':
                raise HTTPException(status_code=400, detail=status_info['message'])
            elif status_info['status'] == 'completed':
                file_path = status_info.get('file_path')
            else:
                raise HTTPException(status_code=404, detail="Export not found")
        else:
            # Try to find file directly
            file_path = csv_service.get_export_file(file_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Return file
        return FileResponse(
            path=file_path,
            filename=file_id,
            media_type='text/csv',
            headers={
                "Content-Disposition": f"attachment; filename={file_id}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.delete("/csv/{file_id}")
async def delete_export(file_id: str):
    """
    Delete a CSV export file
    
    - **file_id**: The file ID to delete
    """
    try:
        # Remove from status tracking
        if file_id in export_status:
            status_info = export_status[file_id]
            file_path = status_info.get('file_path')
            del export_status[file_id]
        else:
            file_path = csv_service.get_export_file(file_id)
        
        # Delete file if exists
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return {"success": True, "message": "Export deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Export file not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/csv/list")
async def list_exports():
    """
    List all available CSV exports
    """
    try:
        exports = []
        
        # Add tracked exports
        for file_id, status_info in export_status.items():
            exports.append({
                "file_id": file_id,
                "status": status_info['status'],
                "articles_count": status_info['articles_count'],
                "created_at": status_info['created_at'],
                "file_size": status_info.get('file_size', 0)
            })
        
        # Add files in export directory that aren't tracked
        export_dir = csv_service.export_dir
        if os.path.exists(export_dir):
            for filename in os.listdir(export_dir):
                if filename.endswith('.csv') and filename not in export_status:
                    file_path = os.path.join(export_dir, filename)
                    if os.path.isfile(file_path):
                        exports.append({
                            "file_id": filename,
                            "status": "completed",
                            "articles_count": 0,  # Unknown for untracked files
                            "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                            "file_size": os.path.getsize(file_path)
                        })
        
        # Sort by creation time (newest first)
        exports.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "success": True,
            "exports": exports,
            "total_count": len(exports)
        }
        
    except Exception as e:
        logger.error(f"Error listing exports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list exports: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_exports(days: int = 1):
    """
    Clean up export files older than specified days
    
    - **days**: Number of days to keep files (default: 1)
    """
    try:
        if days < 1:
            raise HTTPException(status_code=400, detail="Days must be at least 1")
        
        # Clean up files
        csv_service.cleanup_old_exports(days)
        
        # Clean up status tracking for old files
        cutoff_time = datetime.now() - timedelta(days=days)
        to_remove = []
        
        for file_id, status_info in export_status.items():
            created_at = datetime.fromisoformat(status_info['created_at'])
            if created_at < cutoff_time:
                to_remove.append(file_id)
        
        for file_id in to_remove:
            del export_status[file_id]
        
        return {
            "success": True,
            "message": f"Cleaned up exports older than {days} days",
            "removed_count": len(to_remove)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up exports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")