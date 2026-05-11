"""
Analytics Schemas - NEW FEATURE
Pydantic models for analytics and charts API
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum


class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    DONUT = "donut"


class TimeRange(str, Enum):
    """Time range options for analytics"""
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_YEAR = "1y"
    ALL_TIME = "all"


class ChartDataPoint(BaseModel):
    """Single data point for charts"""
    x: str  # Date, category, or label
    y: float  # Value
    label: Optional[str] = None
    color: Optional[str] = None


class ChartData(BaseModel):
    """Chart data structure"""
    type: ChartType
    title: str
    data: List[ChartDataPoint]
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    colors: Optional[List[str]] = None


class ProgressOverTimeRequest(BaseModel):
    """Request schema for progress over time chart"""
    project_ids: Optional[List[int]] = Field(None, description="Specific projects to include")
    time_range: TimeRange = Field(TimeRange.LAST_30_DAYS, description="Time range for data")
    granularity: str = Field("day", description="Data granularity: hour, day, week, month")


class ActivityAnalyticsRequest(BaseModel):
    """Request schema for activity analytics"""
    time_range: TimeRange = Field(TimeRange.LAST_7_DAYS, description="Time range for analysis")
    user_id: Optional[int] = Field(None, description="Filter by specific user")
    action_types: Optional[List[str]] = Field(None, description="Filter by action types")


class ProjectAnalyticsResponse(BaseModel):
    """Response schema for project analytics"""
    total_projects: int
    completed_projects: int
    failed_projects: int
    in_progress_projects: int
    avg_completion_time: Optional[float]
    most_popular_tech_stacks: List[Dict[str, Any]]
    success_rate: float


class UserEngagementResponse(BaseModel):
    """Response schema for user engagement analytics"""
    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    avg_session_duration: Optional[float]
    top_user_actions: List[Dict[str, Any]]


class TechStackPopularityResponse(BaseModel):
    """Response schema for tech stack popularity"""
    frontend_frameworks: List[Dict[str, Any]]
    backend_frameworks: List[Dict[str, Any]]
    databases: List[Dict[str, Any]]
    most_trending: List[Dict[str, Any]]


class PerformanceMetricsResponse(BaseModel):
    """Response schema for system performance metrics"""
    avg_generation_time: float
    fastest_generation: float
    slowest_generation: float
    total_lines_generated: int
    avg_project_size: float
    success_rate: float


class DashboardAnalytics(BaseModel):
    """Complete dashboard analytics response"""
    overview: ProjectAnalyticsResponse
    user_engagement: UserEngagementResponse
    tech_stack_trends: TechStackPopularityResponse
    performance: PerformanceMetricsResponse
    charts: List[ChartData]
    last_updated: datetime


class RealtimeStats(BaseModel):
    """Real-time statistics for live updates"""
    active_generations: int
    queue_length: int
    avg_wait_time: float
    system_load: float
    last_activity: Optional[datetime]


class ExportRequest(BaseModel):
    """Request schema for data export"""
    data_type: str = Field(..., description="Type of data to export")
    format: str = Field("json", description="Export format: json, csv, xlsx")
    time_range: TimeRange = Field(TimeRange.LAST_30_DAYS)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnalyticsInsight(BaseModel):
    """AI-generated insights from analytics data"""
    type: str  # trend, anomaly, recommendation
    title: str
    description: str
    confidence: float  # 0-1
    action_items: List[str]
    created_at: datetime