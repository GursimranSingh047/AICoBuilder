"""
Activity Schemas - NEW FEATURE
Pydantic models for activity tracking API
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class ActivityLogCreate(BaseModel):
    """Schema for creating new activity log entries"""
    action: str = Field(..., max_length=100, description="Action type")
    description: Optional[str] = Field(None, max_length=1000, description="Activity description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    project_id: Optional[int] = Field(None, description="Related project ID")


class ActivityLogResponse(BaseModel):
    """Schema for activity log responses"""
    id: int
    action: str
    description: Optional[str]
    metadata: Dict[str, Any]
    user_id: Optional[int]
    project_id: Optional[int]
    created_at: datetime
    
    # Related data (populated via joins)
    user_name: Optional[str] = None
    project_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ActivityFeedResponse(BaseModel):
    """Schema for activity feed with pagination"""
    activities: List[ActivityLogResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class ProjectMetricsResponse(BaseModel):
    """Schema for project metrics"""
    id: int
    project_id: int
    progress_percentage: float
    files_generated: int
    lines_of_code: int
    view_count: int
    download_count: int
    last_accessed: Optional[datetime]
    generation_time_seconds: Optional[float]
    complexity_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectMetricsUpdate(BaseModel):
    """Schema for updating project metrics"""
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    files_generated: Optional[int] = Field(None, ge=0)
    lines_of_code: Optional[int] = Field(None, ge=0)
    complexity_score: Optional[float] = Field(None, ge=0, le=100)


class DailyStatsResponse(BaseModel):
    """Schema for daily statistics"""
    id: int
    date: datetime
    projects_created: int
    projects_completed: int
    total_downloads: int
    active_users: int
    avg_generation_time: Optional[float]
    total_lines_generated: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivitySummary(BaseModel):
    """Schema for activity summary dashboard"""
    total_activities: int
    recent_activities: List[ActivityLogResponse]
    top_actions: List[Dict[str, Any]]
    daily_activity_count: int
    weekly_activity_count: int


class UserActivityStats(BaseModel):
    """Schema for user-specific activity statistics"""
    user_id: int
    total_projects: int
    completed_projects: int
    total_downloads: int
    last_activity: Optional[datetime]
    most_active_day: Optional[str]
    favorite_tech_stack: Optional[str]