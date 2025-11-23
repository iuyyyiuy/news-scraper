"""
Alerts Router

Endpoints for retrieving and managing alerts.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from trade_risk_analyzer.core.logger import get_logger

# Placeholder imports
try:
    from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage
except ImportError:
    DatabaseStorage = None

router = APIRouter()
logger = get_logger(__name__)


@router.get("")
async def get_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (HIGH, MEDIUM, LOW)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    sort_by: str = Query("timestamp", description="Sort field (timestamp, risk_level)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)")
):
    """
    Retrieve alerts with filtering, pagination, and sorting
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 1000)
    - **start_date**: Filter alerts from this date (ISO format)
    - **end_date**: Filter alerts until this date (ISO format)
    - **risk_level**: Filter by risk level (HIGH, MEDIUM, LOW)
    - **user_id**: Filter by specific user ID
    - **alert_type**: Filter by alert type
    - **sort_by**: Sort field (timestamp, risk_level)
    - **sort_order**: Sort order (asc, desc)
    """
    try:
        if DatabaseStorage is None:
            raise HTTPException(status_code=501, detail="Database storage module not yet implemented")
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # Initialize storage
        storage = DatabaseStorage()
        
        # Get alerts with filters
        alerts_df = storage.get_alerts(
            start_date=start_dt,
            end_date=end_dt,
            risk_level=risk_level,
            user_id=user_id,
            alert_type=alert_type
        )
        
        if alerts_df.empty:
            return {
                "page": page,
                "page_size": page_size,
                "total": 0,
                "total_pages": 0,
                "alerts": []
            }
        
        # Sort
        ascending = sort_order.lower() == "asc"
        if sort_by in alerts_df.columns:
            alerts_df = alerts_df.sort_values(by=sort_by, ascending=ascending)
        
        # Pagination
        total = len(alerts_df)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_alerts = alerts_df.iloc[start_idx:end_idx]
        
        # Convert to list of dicts
        alerts_list = []
        for _, row in page_alerts.iterrows():
            alert = {
                "id": int(row.get("id", 0)),
                "user_id": row.get("user_id"),
                "alert_type": row.get("alert_type"),
                "risk_level": row.get("risk_level"),
                "description": row.get("description"),
                "anomaly_score": float(row.get("anomaly_score", 0)),
                "timestamp": row.get("timestamp").isoformat() if hasattr(row.get("timestamp"), "isoformat") else str(row.get("timestamp")),
                "metadata": row.get("metadata", {})
            }
            alerts_list.append(alert)
        
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "alerts": alerts_list
        }
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.get("/{alert_id}")
async def get_alert_by_id(alert_id: int):
    """
    Get a specific alert by ID
    
    - **alert_id**: Alert identifier
    """
    try:
        storage = DatabaseStorage()
        alert = storage.get_alert_by_id(alert_id)
        
        if alert is None:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "id": int(alert.get("id", 0)),
            "user_id": alert.get("user_id"),
            "alert_type": alert.get("alert_type"),
            "risk_level": alert.get("risk_level"),
            "description": alert.get("description"),
            "anomaly_score": float(alert.get("anomaly_score", 0)),
            "timestamp": alert.get("timestamp").isoformat() if hasattr(alert.get("timestamp"), "isoformat") else str(alert.get("timestamp")),
            "metadata": alert.get("metadata", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert: {str(e)}")


@router.get("/stats/summary")
async def get_alert_stats(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    """
    Get alert statistics summary
    
    - **start_date**: Start date for statistics (ISO format)
    - **end_date**: End date for statistics (ISO format)
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        storage = DatabaseStorage()
        alerts_df = storage.get_alerts(start_date=start_dt, end_date=end_dt)
        
        if alerts_df.empty:
            return {
                "total_alerts": 0,
                "by_risk_level": {},
                "by_alert_type": {},
                "date_range": {
                    "start": start_date,
                    "end": end_date
                }
            }
        
        # Calculate statistics
        risk_counts = alerts_df["risk_level"].value_counts().to_dict()
        type_counts = alerts_df["alert_type"].value_counts().to_dict()
        
        return {
            "total_alerts": len(alerts_df),
            "by_risk_level": risk_counts,
            "by_alert_type": type_counts,
            "date_range": {
                "start": start_date or alerts_df["timestamp"].min().isoformat(),
                "end": end_date or alerts_df["timestamp"].max().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating alert stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to calculate statistics: {str(e)}")
