"""
Activity Service - NEW FEATURE
Handles activity logging and tracking without affecting existing functionality
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from loguru import logger

from app.models.activity import ActivityLog, ProjectMetrics, DailyStats
from app.models.project import Project
from app.models.user import User
from app.schemas.activity import (
    ActivityLogCreate, ActivityLogResponse, ActivityFeedResponse,
    ProjectMetricsResponse, ActivitySummary, UserActivityStats
)


class ActivityService:
    """
    Service for managing activity tracking and metrics
    Safe extension - doesn't modify existing functionality
    """

    @staticmethod
    def log_activity(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """
        Log a new activity - safe addition to existing system
        """
        try:
            activity = ActivityLog(
                action=action,
                description=description,
                activity_metadata=metadata or {},
                user_id=user_id,
                project_id=project_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(activity)
            db.commit()
            db.refresh(activity)
            
            # Update metrics synchronously (non-blocking for the user)
            try:
                ActivityService._update_metrics_sync(db, activity)
            except Exception as e:
                logger.warning(f"Failed to update metrics: {e}")
            
            logger.info(f"Activity logged: {action} for user {user_id}")
            return activity
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            db.rollback()
            raise

    @staticmethod
    def _update_metrics_sync(db: Session, activity: ActivityLog):
        """
        Update metrics synchronously - safe for sync context
        """
        try:
            if activity.project_id:
                ActivityService._update_project_metrics_sync(db, activity.project_id, activity.action)
            
            ActivityService._update_daily_stats_sync(db, activity.created_at.date(), activity.action)
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

    @staticmethod
    def _update_project_metrics_sync(db: Session, project_id: int, action: str):
        """Update project-specific metrics synchronously"""
        metrics = db.query(ProjectMetrics).filter(
            ProjectMetrics.project_id == project_id
        ).first()
        
        if not metrics:
            metrics = ProjectMetrics(project_id=project_id)
            db.add(metrics)
        
        # Update based on action type
        if action == "project_viewed":
            metrics.view_count += 1
            metrics.last_accessed = datetime.now(timezone.utc)
        elif action == "project_downloaded":
            metrics.download_count += 1
        elif action == "project_completed":
            metrics.progress_percentage = 100.0
            
        db.commit()

    @staticmethod
    def _update_daily_stats_sync(db: Session, date: datetime.date, action: str):
        """Update daily aggregated statistics synchronously"""
        stats = db.query(DailyStats).filter(
            func.date(DailyStats.date) == date
        ).first()
        
        if not stats:
            stats = DailyStats(date=datetime.combine(date, datetime.min.time()))
            db.add(stats)
        
        # Update based on action type
        if action == "project_created":
            stats.projects_created += 1
        elif action == "project_completed":
            stats.projects_completed += 1
        elif action == "project_downloaded":
            stats.total_downloads += 1
            
        db.commit()

    @staticmethod
    def get_activity_feed(
        db: Session,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        action_filter: Optional[str] = None
    ) -> ActivityFeedResponse:
        """
        Get paginated activity feed with optional filters
        """
        query = db.query(ActivityLog).join(User, ActivityLog.user_id == User.id, isouter=True)\
                  .join(Project, ActivityLog.project_id == Project.id, isouter=True)
        
        # Apply filters
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if project_id:
            query = query.filter(ActivityLog.project_id == project_id)
        if action_filter:
            query = query.filter(ActivityLog.action.ilike(f"%{action_filter}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        activities = query.order_by(desc(ActivityLog.created_at))\
                         .offset((page - 1) * per_page)\
                         .limit(per_page)\
                         .all()
        
        # Enrich with related data
        enriched_activities = []
        for activity in activities:
            activity_data = ActivityLogResponse(
                id=activity.id,
                action=activity.action,
                description=activity.description,
                metadata=activity.activity_metadata or {},
                user_id=activity.user_id,
                project_id=activity.project_id,
                created_at=activity.created_at
            )
            if activity.user:
                activity_data.user_name = activity.user.username
            if activity.project:
                activity_data.project_name = activity.project.name
            enriched_activities.append(activity_data)
        
        return ActivityFeedResponse(
            activities=enriched_activities,
            total=total,
            page=page,
            per_page=per_page,
            has_next=page * per_page < total,
            has_prev=page > 1
        )

    @staticmethod
    def get_project_metrics(db: Session, project_id: int) -> Optional[ProjectMetricsResponse]:
        """Get metrics for a specific project"""
        metrics = db.query(ProjectMetrics).filter(
            ProjectMetrics.project_id == project_id
        ).first()
        
        if not metrics:
            # Create default metrics if none exist
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                metrics = ProjectMetrics(
                    project_id=project_id,
                    files_generated=len(project.generated_files) if project.generated_files else 0,
                    progress_percentage=100.0 if project.status == "completed" else 0.0
                )
                db.add(metrics)
                db.commit()
                db.refresh(metrics)
        
        return ProjectMetricsResponse.model_validate(metrics) if metrics else None

    @staticmethod
    def get_activity_summary(db: Session, user_id: Optional[int] = None) -> ActivitySummary:
        """Get activity summary for dashboard"""
        base_query = db.query(ActivityLog)
        if user_id:
            base_query = base_query.filter(ActivityLog.user_id == user_id)
        
        # Total activities
        total_activities = base_query.count()
        
        # Recent activities (last 10)
        recent_activities_raw = base_query.join(User, ActivityLog.user_id == User.id, isouter=True)\
                                         .join(Project, ActivityLog.project_id == Project.id, isouter=True)\
                                         .order_by(desc(ActivityLog.created_at))\
                                         .limit(10)\
                                         .all()
        
        recent_activities = []
        for activity in recent_activities_raw:
            activity_data = ActivityLogResponse(
                id=activity.id,
                action=activity.action,
                description=activity.description,
                metadata=activity.activity_metadata or {},
                user_id=activity.user_id,
                project_id=activity.project_id,
                created_at=activity.created_at
            )
            if activity.user:
                activity_data.user_name = activity.user.username
            if activity.project:
                activity_data.project_name = activity.project.name
            recent_activities.append(activity_data)
        
        # Top actions
        top_actions_raw = base_query.with_entities(
            ActivityLog.action,
            func.count(ActivityLog.action).label('count')
        ).group_by(ActivityLog.action)\
         .order_by(desc(func.count(ActivityLog.action)))\
         .limit(5)\
         .all()
        
        top_actions = [
            {"action": action, "count": count}
            for action, count in top_actions_raw
        ]
        
        # Daily and weekly counts
        today = datetime.now(timezone.utc).date()
        week_ago = today - timedelta(days=7)
        
        daily_count = base_query.filter(
            func.date(ActivityLog.created_at) == today
        ).count()
        
        weekly_count = base_query.filter(
            func.date(ActivityLog.created_at) >= week_ago
        ).count()
        
        return ActivitySummary(
            total_activities=total_activities,
            recent_activities=recent_activities,
            top_actions=top_actions,
            daily_activity_count=daily_count,
            weekly_activity_count=weekly_count
        )

    @staticmethod
    def get_user_activity_stats(db: Session, user_id: int) -> UserActivityStats:
        """Get comprehensive activity statistics for a user"""
        # Basic project stats
        user_projects = db.query(Project).filter(Project.owner_id == user_id)
        total_projects = user_projects.count()
        completed_projects = user_projects.filter(Project.status == "completed").count()
        
        # Download count from metrics
        total_downloads = db.query(func.sum(ProjectMetrics.download_count))\
                           .join(Project, ProjectMetrics.project_id == Project.id)\
                           .filter(Project.owner_id == user_id)\
                           .scalar() or 0
        
        # Last activity
        last_activity_record = db.query(ActivityLog)\
                                .filter(ActivityLog.user_id == user_id)\
                                .order_by(desc(ActivityLog.created_at))\
                                .first()
        
        last_activity = last_activity_record.created_at if last_activity_record else None
        
        # Most active day of week
        most_active_day_raw = db.query(
            func.extract('dow', ActivityLog.created_at).label('day_of_week'),
            func.count().label('count')
        ).filter(ActivityLog.user_id == user_id)\
         .group_by(func.extract('dow', ActivityLog.created_at))\
         .order_by(desc(func.count()))\
         .first()
        
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        most_active_day = day_names[int(most_active_day_raw[0])] if most_active_day_raw else None
        
        # Favorite tech stack
        favorite_tech_raw = db.query(
            Project.tech_stack,
            func.count().label('count')
        ).filter(Project.owner_id == user_id)\
         .group_by(Project.tech_stack)\
         .order_by(desc(func.count()))\
         .first()
        
        favorite_tech_stack = None
        if favorite_tech_raw and favorite_tech_raw[0]:
            tech_stack = favorite_tech_raw[0]
            if isinstance(tech_stack, dict):
                favorite_tech_stack = f"{tech_stack.get('frontend', 'Unknown')} + {tech_stack.get('backend', 'Unknown')}"
        
        return UserActivityStats(
            user_id=user_id,
            total_projects=total_projects,
            completed_projects=completed_projects,
            total_downloads=total_downloads,
            last_activity=last_activity,
            most_active_day=most_active_day,
            favorite_tech_stack=favorite_tech_stack
        )


# Singleton instance
activity_service = ActivityService()