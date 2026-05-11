"""
Analytics Router - NEW FEATURE
Safe API extension for analytics and charts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from loguru import logger

from app.database import get_db
from app.dependencies import get_optional_user, get_current_user
from app.models.user import User
from app.schemas.analytics import (
    ChartData, TimeRange, ProjectAnalyticsResponse,
    UserEngagementResponse, PerformanceMetricsResponse,
    DashboardAnalytics, RealtimeStats, ProgressOverTimeRequest,
    ActivityAnalyticsRequest
)
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get complete dashboard analytics
    Safe addition - provides new analytics without affecting existing functionality
    """
    try:
        return analytics_service.get_dashboard_analytics(db)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard analytics")


@router.get("/charts/progress-over-time", response_model=ChartData)
def get_progress_chart(
    time_range: TimeRange = Query(TimeRange.LAST_30_DAYS, description="Time range for chart"),
    project_ids: Optional[str] = Query(None, description="Comma-separated project IDs"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get progress over time chart data
    """
    try:
        # Parse project IDs if provided
        parsed_project_ids = None
        if project_ids:
            try:
                parsed_project_ids = [int(pid.strip()) for pid in project_ids.split(",")]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid project IDs format")
        
        return analytics_service.get_progress_over_time_chart(
            db=db,
            time_range=time_range,
            project_ids=parsed_project_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get progress chart: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate progress chart")


@router.get("/charts/daily-activity", response_model=ChartData)
def get_daily_activity_chart(
    time_range: TimeRange = Query(TimeRange.LAST_7_DAYS, description="Time range for chart"),
    user_id: Optional[int] = Query(None, description="Filter by specific user"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get daily activity chart data
    """
    try:
        # If user_id is specified, ensure user can only see their own data
        if user_id and current_user and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return analytics_service.get_daily_activity_chart(
            db=db,
            time_range=time_range,
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get daily activity chart: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate activity chart")


@router.get("/charts/tech-stack-popularity", response_model=ChartData)
def get_tech_stack_chart(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get tech stack popularity chart data
    """
    try:
        return analytics_service.get_tech_stack_popularity_chart(db)
        
    except Exception as e:
        logger.error(f"Failed to get tech stack chart: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate tech stack chart")


@router.get("/projects", response_model=ProjectAnalyticsResponse)
def get_project_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get comprehensive project analytics
    """
    try:
        return analytics_service.get_project_analytics(db)
        
    except Exception as e:
        logger.error(f"Failed to get project analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project analytics")


@router.get("/users", response_model=UserEngagementResponse)
def get_user_engagement(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get user engagement analytics
    """
    try:
        return analytics_service.get_user_engagement(db)
        
    except Exception as e:
        logger.error(f"Failed to get user engagement: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user engagement")


@router.get("/performance", response_model=PerformanceMetricsResponse)
def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get system performance metrics
    """
    try:
        return analytics_service.get_performance_metrics(db)
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")


@router.get("/realtime", response_model=RealtimeStats)
def get_realtime_stats(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get real-time statistics for live dashboard updates
    """
    try:
        return analytics_service.get_realtime_stats(db)
        
    except Exception as e:
        logger.error(f"Failed to get realtime stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve realtime statistics")


# Health check endpoint for the analytics system
@router.get("/health")
def analytics_health_check():
    """Health check for analytics system"""
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": logger.info("Analytics system is healthy")
    }