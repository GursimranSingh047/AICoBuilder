"""
Analytics Service - NEW FEATURE
Provides analytics and chart data without affecting existing functionality
"""

from datetime import datetime, timezone, timedelta, date
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from collections import defaultdict, Counter
import json

from app.models.activity import ActivityLog, ProjectMetrics, DailyStats
from app.models.project import Project
from app.models.user import User
from app.schemas.analytics import (
    ChartData, ChartDataPoint, ChartType, TimeRange,
    ProjectAnalyticsResponse, UserEngagementResponse,
    TechStackPopularityResponse, PerformanceMetricsResponse,
    DashboardAnalytics, RealtimeStats, AnalyticsInsight
)


class AnalyticsService:
    """
    Service for generating analytics and chart data
    Safe extension - doesn't modify existing functionality
    """

    @staticmethod
    def get_progress_over_time_chart(
        db: Session,
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
        project_ids: Optional[List[int]] = None
    ) -> ChartData:
        """Generate progress over time line chart"""
        
        # Calculate date range
        end_date = datetime.now(timezone.utc).date()
        if time_range == TimeRange.LAST_7_DAYS:
            start_date = end_date - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            start_date = end_date - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            start_date = end_date - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            start_date = end_date - timedelta(days=365)
        else:  # ALL_TIME
            start_date = date(2020, 1, 1)  # Reasonable start date
        
        # Query daily stats
        daily_stats = db.query(DailyStats)\
                       .filter(func.date(DailyStats.date) >= start_date)\
                       .filter(func.date(DailyStats.date) <= end_date)\
                       .order_by(DailyStats.date)\
                       .all()
        
        # Generate data points
        data_points = []
        current_date = start_date
        stats_dict = {stat.date.date(): stat for stat in daily_stats}
        
        while current_date <= end_date:
            stat = stats_dict.get(current_date)
            completed_count = stat.projects_completed if stat else 0
            
            data_points.append(ChartDataPoint(
                x=current_date.strftime("%Y-%m-%d"),
                y=float(completed_count),
                label=f"{completed_count} projects"
            ))
            current_date += timedelta(days=1)
        
        return ChartData(
            type=ChartType.LINE,
            title="Projects Completed Over Time",
            data=data_points,
            x_axis_label="Date",
            y_axis_label="Projects Completed",
            colors=["#6366f1"]
        )

    @staticmethod
    def get_daily_activity_chart(
        db: Session,
        time_range: TimeRange = TimeRange.LAST_7_DAYS,
        user_id: Optional[int] = None
    ) -> ChartData:
        """Generate daily activity bar chart"""
        
        # Calculate date range
        end_date = datetime.now(timezone.utc).date()
        if time_range == TimeRange.LAST_7_DAYS:
            start_date = end_date - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)  # Default to 7 days
        
        # Query activities
        query = db.query(
            func.date(ActivityLog.created_at).label('activity_date'),
            func.count(ActivityLog.id).label('activity_count')
        ).filter(func.date(ActivityLog.created_at) >= start_date)\
         .filter(func.date(ActivityLog.created_at) <= end_date)
        
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        
        daily_activities = query.group_by(func.date(ActivityLog.created_at))\
                               .order_by(func.date(ActivityLog.created_at))\
                               .all()
        
        # Generate data points
        data_points = []
        current_date = start_date
        activity_dict = {activity.activity_date: activity.activity_count for activity in daily_activities}
        
        while current_date <= end_date:
            count = activity_dict.get(current_date, 0)
            data_points.append(ChartDataPoint(
                x=current_date.strftime("%a %m/%d"),
                y=float(count),
                label=f"{count} activities"
            ))
            current_date += timedelta(days=1)
        
        return ChartData(
            type=ChartType.BAR,
            title="Daily Activity",
            data=data_points,
            x_axis_label="Date",
            y_axis_label="Activities",
            colors=["#22d3ee"]
        )

    @staticmethod
    def get_tech_stack_popularity_chart(db: Session) -> ChartData:
        """Generate tech stack popularity pie chart"""
        
        # Query projects with tech stacks
        projects = db.query(Project.tech_stack)\
                    .filter(Project.tech_stack.isnot(None))\
                    .filter(Project.status == "completed")\
                    .all()
        
        # Count frontend frameworks
        frontend_counts = Counter()
        backend_counts = Counter()
        
        for project in projects:
            if project.tech_stack and isinstance(project.tech_stack, dict):
                frontend = project.tech_stack.get('frontend')
                backend = project.tech_stack.get('backend')
                
                if frontend:
                    frontend_counts[frontend] += 1
                if backend:
                    backend_counts[backend] += 1
        
        # Combine and get top combinations
        stack_combinations = Counter()
        for project in projects:
            if project.tech_stack and isinstance(project.tech_stack, dict):
                frontend = project.tech_stack.get('frontend', 'Unknown')
                backend = project.tech_stack.get('backend', 'Unknown')
                combo = f"{frontend} + {backend}"
                stack_combinations[combo] += 1
        
        # Generate data points for top 6 combinations
        data_points = []
        colors = ["#6366f1", "#22d3ee", "#34d399", "#fbbf24", "#fb7185", "#8b5cf6"]
        
        for i, (combo, count) in enumerate(stack_combinations.most_common(6)):
            data_points.append(ChartDataPoint(
                x=combo,
                y=float(count),
                label=f"{count} projects",
                color=colors[i % len(colors)]
            ))
        
        return ChartData(
            type=ChartType.PIE,
            title="Popular Tech Stack Combinations",
            data=data_points,
            colors=colors
        )

    @staticmethod
    def get_project_analytics(db: Session) -> ProjectAnalyticsResponse:
        """Get comprehensive project analytics"""
        
        # Basic counts
        total_projects = db.query(Project).count()
        completed_projects = db.query(Project).filter(Project.status == "completed").count()
        failed_projects = db.query(Project).filter(Project.status == "failed").count()
        in_progress_projects = db.query(Project).filter(Project.status == "generating").count()
        
        # Average completion time (from metrics)
        avg_completion_time = db.query(func.avg(ProjectMetrics.generation_time_seconds))\
                               .filter(ProjectMetrics.generation_time_seconds.isnot(None))\
                               .scalar()
        
        # Most popular tech stacks
        tech_stack_query = db.query(
            Project.tech_stack,
            func.count().label('count')
        ).filter(Project.tech_stack.isnot(None))\
         .group_by(Project.tech_stack)\
         .order_by(desc(func.count()))\
         .limit(5)\
         .all()
        
        most_popular_tech_stacks = []
        for tech_stack, count in tech_stack_query:
            if isinstance(tech_stack, dict):
                stack_name = f"{tech_stack.get('frontend', 'Unknown')} + {tech_stack.get('backend', 'Unknown')}"
                most_popular_tech_stacks.append({
                    "name": stack_name,
                    "count": count,
                    "percentage": round((count / total_projects) * 100, 1) if total_projects > 0 else 0
                })
        
        # Success rate
        success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        
        return ProjectAnalyticsResponse(
            total_projects=total_projects,
            completed_projects=completed_projects,
            failed_projects=failed_projects,
            in_progress_projects=in_progress_projects,
            avg_completion_time=avg_completion_time,
            most_popular_tech_stacks=most_popular_tech_stacks,
            success_rate=round(success_rate, 1)
        )

    @staticmethod
    def get_user_engagement(db: Session) -> UserEngagementResponse:
        """Get user engagement analytics"""
        
        total_users = db.query(User).count()
        
        # Active users by time period
        now = datetime.now(timezone.utc)
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        active_today = db.query(func.count(func.distinct(ActivityLog.user_id)))\
                        .filter(func.date(ActivityLog.created_at) == today)\
                        .scalar() or 0
        
        active_week = db.query(func.count(func.distinct(ActivityLog.user_id)))\
                       .filter(func.date(ActivityLog.created_at) >= week_ago)\
                       .scalar() or 0
        
        active_month = db.query(func.count(func.distinct(ActivityLog.user_id)))\
                        .filter(func.date(ActivityLog.created_at) >= month_ago)\
                        .scalar() or 0
        
        # Top user actions
        top_actions = db.query(
            ActivityLog.action,
            func.count().label('count')
        ).group_by(ActivityLog.action)\
         .order_by(desc(func.count()))\
         .limit(5)\
         .all()
        
        top_user_actions = [
            {"action": action, "count": count}
            for action, count in top_actions
        ]
        
        return UserEngagementResponse(
            total_users=total_users,
            active_users_today=active_today,
            active_users_week=active_week,
            active_users_month=active_month,
            avg_session_duration=None,  # Would need session tracking
            top_user_actions=top_user_actions
        )

    @staticmethod
    def get_performance_metrics(db: Session) -> PerformanceMetricsResponse:
        """Get system performance metrics"""
        
        # Generation time metrics
        generation_times = db.query(ProjectMetrics.generation_time_seconds)\
                            .filter(ProjectMetrics.generation_time_seconds.isnot(None))\
                            .all()
        
        if generation_times:
            times = [t[0] for t in generation_times]
            avg_generation_time = sum(times) / len(times)
            fastest_generation = min(times)
            slowest_generation = max(times)
        else:
            avg_generation_time = 0.0
            fastest_generation = 0.0
            slowest_generation = 0.0
        
        # Total lines generated
        total_lines = db.query(func.sum(ProjectMetrics.lines_of_code)).scalar() or 0
        
        # Average project size
        avg_project_size = db.query(func.avg(ProjectMetrics.lines_of_code))\
                            .filter(ProjectMetrics.lines_of_code > 0)\
                            .scalar() or 0
        
        # Success rate
        total_projects = db.query(Project).count()
        completed_projects = db.query(Project).filter(Project.status == "completed").count()
        success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        
        return PerformanceMetricsResponse(
            avg_generation_time=round(avg_generation_time, 2),
            fastest_generation=round(fastest_generation, 2),
            slowest_generation=round(slowest_generation, 2),
            total_lines_generated=total_lines,
            avg_project_size=round(avg_project_size, 0),
            success_rate=round(success_rate, 1)
        )

    @staticmethod
    def get_dashboard_analytics(db: Session) -> DashboardAnalytics:
        """Get complete dashboard analytics with charts"""
        
        # Get all analytics components
        overview = AnalyticsService.get_project_analytics(db)
        user_engagement = AnalyticsService.get_user_engagement(db)
        performance = AnalyticsService.get_performance_metrics(db)
        
        # Tech stack popularity (simplified for dashboard)
        tech_stack_trends = TechStackPopularityResponse(
            frontend_frameworks=[],
            backend_frameworks=[],
            databases=[],
            most_trending=[]
        )
        
        # Generate charts
        charts = [
            AnalyticsService.get_progress_over_time_chart(db),
            AnalyticsService.get_daily_activity_chart(db),
            AnalyticsService.get_tech_stack_popularity_chart(db)
        ]
        
        return DashboardAnalytics(
            overview=overview,
            user_engagement=user_engagement,
            tech_stack_trends=tech_stack_trends,
            performance=performance,
            charts=charts,
            last_updated=datetime.now(timezone.utc)
        )

    @staticmethod
    def get_realtime_stats(db: Session) -> RealtimeStats:
        """Get real-time statistics for live dashboard updates"""
        
        # Active generations (projects currently being generated)
        active_generations = db.query(Project)\
                              .filter(Project.status == "generating")\
                              .count()
        
        # Recent activity (last activity timestamp)
        last_activity_record = db.query(ActivityLog)\
                                .order_by(desc(ActivityLog.created_at))\
                                .first()
        
        last_activity = last_activity_record.created_at if last_activity_record else None
        
        return RealtimeStats(
            active_generations=active_generations,
            queue_length=0,  # Would need queue implementation
            avg_wait_time=0.0,  # Would need queue metrics
            system_load=0.0,  # Would need system monitoring
            last_activity=last_activity
        )


# Singleton instance
analytics_service = AnalyticsService()