"""
Activity Tracking Models - NEW FEATURE
Safe extension to existing system - no modifications to existing models
"""

from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project

from app.database import Base


class ActivityLog(Base):
    """
    Tracks all user activities and project interactions
    NEW TABLE - Safe addition to existing schema
    """
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Activity details
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # Actions: project_created, project_updated, project_deleted, project_generated, 
    # project_downloaded, user_login, user_signup, chat_message, suggestion_requested
    
    description: Mapped[str] = mapped_column(Text, nullable=True)
    activity_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    
    # Relationships - nullable to support system-wide activities
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    
    # Tracking info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        index=True  # For efficient time-based queries
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", backref="activities")
    project: Mapped[Optional["Project"]] = relationship("Project", backref="activities")


class ProjectMetrics(Base):
    """
    Stores calculated metrics and progress data for projects
    NEW TABLE - Safe addition for analytics
    """
    __tablename__ = "project_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, unique=True)
    
    # Progress tracking
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    files_generated: Mapped[int] = mapped_column(Integer, default=0)
    lines_of_code: Mapped[int] = mapped_column(Integer, default=0)
    
    # Activity metrics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Performance metrics
    generation_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    complexity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", backref="metrics")


class DailyStats(Base):
    """
    Aggregated daily statistics for analytics
    NEW TABLE - For efficient dashboard queries
    """
    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Daily counts
    projects_created: Mapped[int] = mapped_column(Integer, default=0)
    projects_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_downloads: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance metrics
    avg_generation_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_lines_generated: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )