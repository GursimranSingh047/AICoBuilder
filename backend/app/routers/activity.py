"""
Activity Router - NEW FEATURE
Safe API extension for activity tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from loguru import logger

from app.database import get_db
from app.dependencies import get_optional_user, get_current_user
from app.models.user import User
from app.schemas.activity import (
    ActivityLogCreate, ActivityLogResponse, ActivityFeedResponse,
    ProjectMetricsResponse, ActivitySummary, UserActivityStats
)
from app.services.activity_service import activity_service

router = APIRouter(prefix="/activity", tags=["Activity Tracking"])


@router.post("/log", response_model=ActivityLogResponse)
def log_activity(
    activity_data: ActivityLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Log a new activity - Safe addition to existing system
    Works with or without authentication
    """
    try:
        # Extract request metadata
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Log the activity
        activity = activity_service.log_activity(
            db=db,
            action=activity_data.action,
            user_id=current_user.id if current_user else None,
            project_id=activity_data.project_id,
            description=activity_data.description,
            metadata=activity_data.metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return ActivityLogResponse(
            id=activity.id,
            action=activity.action,
            description=activity.description,
            metadata=activity.activity_metadata or {},
            user_id=activity.user_id,
            project_id=activity.project_id,
            created_at=activity.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to log activity")


@router.get("/feed", response_model=ActivityFeedResponse)
def get_activity_feed(
    page: int = 1,
    per_page: int = 20,
    action_filter: Optional[str] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get paginated activity feed
    Shows user's activities if authenticated, otherwise public activities
    """
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        user_id = current_user.id if current_user else None
        
        return activity_service.get_activity_feed(
            db=db,
            user_id=user_id,
            project_id=project_id,
            page=page,
            per_page=per_page,
            action_filter=action_filter
        )
        
    except Exception as e:
        logger.error(f"Failed to get activity feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve activity feed")


@router.get("/summary", response_model=ActivitySummary)
def get_activity_summary(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get activity summary for dashboard
    Shows user's summary if authenticated, otherwise global summary
    """
    try:
        user_id = current_user.id if current_user else None
        return activity_service.get_activity_summary(db=db, user_id=user_id)
        
    except Exception as e:
        logger.error(f"Failed to get activity summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve activity summary")


@router.get("/user/{user_id}/stats", response_model=UserActivityStats)
def get_user_activity_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive activity statistics for a user
    Requires authentication and user can only see their own stats
    """
    try:
        # Users can only see their own stats (privacy protection)
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return activity_service.get_user_activity_stats(db=db, user_id=user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user activity stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user statistics")


@router.get("/project/{project_id}/metrics", response_model=ProjectMetricsResponse)
def get_project_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get metrics for a specific project
    Public endpoint - works without authentication
    """
    try:
        metrics = activity_service.get_project_metrics(db=db, project_id=project_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Project metrics not found")
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project metrics")


@router.post("/project/{project_id}/view")
def track_project_view(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Track when a project is viewed
    Safe addition - doesn't affect existing project viewing functionality
    """
    try:
        # Log the view activity
        activity_service.log_activity(
            db=db,
            action="project_viewed",
            user_id=current_user.id if current_user else None,
            project_id=project_id,
            description=f"Project {project_id} viewed",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return {"status": "success", "message": "Project view tracked"}
        
    except Exception as e:
        logger.error(f"Failed to track project view: {e}")
        # Don't raise exception - this is non-critical tracking
        return {"status": "error", "message": "Failed to track view"}


@router.post("/project/{project_id}/download")
def track_project_download(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Track when a project is downloaded
    Safe addition - doesn't affect existing download functionality
    """
    try:
        # Log the download activity
        activity_service.log_activity(
            db=db,
            action="project_downloaded",
            user_id=current_user.id if current_user else None,
            project_id=project_id,
            description=f"Project {project_id} downloaded",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return {"status": "success", "message": "Project download tracked"}
        
    except Exception as e:
        logger.error(f"Failed to track project download: {e}")
        # Don't raise exception - this is non-critical tracking
        return {"status": "error", "message": "Failed to track download"}


# Health check endpoint for the activity system
@router.get("/health")
def activity_health_check():
    """Health check for activity tracking system"""
    return {
        "status": "healthy",
        "service": "activity_tracking",
        "timestamp": logger.info("Activity tracking system is healthy")
    }