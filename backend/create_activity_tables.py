#!/usr/bin/env python3
"""
Database Migration Script for Activity Tracking System
Safe addition - creates new tables without affecting existing ones
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from loguru import logger

from app.core.config import settings
from app.database import Base
from app.models.activity import ActivityLog, ProjectMetrics, DailyStats
from app.models.user import User
from app.models.project import Project

def create_activity_tables():
    """
    Create new activity tracking tables
    Safe migration - only adds new tables, doesn't modify existing ones
    """
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        logger.info("Starting activity tables migration...")
        
        # Create only the new tables
        with engine.begin() as conn:
            # Check if tables already exist (SQLite version)
            result = conn.execute(text("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                AND name IN ('activity_logs', 'project_metrics', 'daily_stats')
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
            if existing_tables:
                logger.info(f"Some activity tables already exist: {existing_tables}")
                logger.info("Skipping creation of existing tables...")
            
            # Create new tables (SQLAlchemy will skip existing ones)
            ActivityLog.__table__.create(engine, checkfirst=True)
            ProjectMetrics.__table__.create(engine, checkfirst=True)
            DailyStats.__table__.create(engine, checkfirst=True)
            
            logger.info("✅ Activity tracking tables created successfully!")
            
            # Create some sample data for testing
            db = SessionLocal()
            try:
                # Check if we have any existing data
                existing_activities = db.query(ActivityLog).count()
                if existing_activities == 0:
                    logger.info("Creating sample activity data...")
                    
                    # Create sample activities (if users exist)
                    users = db.query(User).limit(3).all()
                    projects = db.query(Project).limit(3).all()
                    
                    if users and projects:
                        from datetime import datetime, timezone, timedelta
                        
                        sample_activities = [
                            ActivityLog(
                                action="project_created",
                                description="New project created",
                                user_id=users[0].id,
                                project_id=projects[0].id,
                                created_at=datetime.now(timezone.utc) - timedelta(days=2)
                            ),
                            ActivityLog(
                                action="project_viewed",
                                description="Project viewed",
                                user_id=users[0].id,
                                project_id=projects[0].id,
                                created_at=datetime.now(timezone.utc) - timedelta(days=1)
                            ),
                            ActivityLog(
                                action="project_downloaded",
                                description="Project downloaded",
                                user_id=users[0].id,
                                project_id=projects[0].id,
                                created_at=datetime.now(timezone.utc)
                            )
                        ]
                        
                        for activity in sample_activities:
                            db.add(activity)
                        
                        # Create sample metrics
                        for project in projects:
                            metrics = ProjectMetrics(
                                project_id=project.id,
                                progress_percentage=100.0,
                                files_generated=5,
                                lines_of_code=250,
                                view_count=10,
                                download_count=3,
                                generation_time_seconds=45.5,
                                complexity_score=75.0
                            )
                            db.add(metrics)
                        
                        # Create sample daily stats
                        today = datetime.now(timezone.utc).date()
                        for i in range(7):
                            date = today - timedelta(days=i)
                            stats = DailyStats(
                                date=datetime.combine(date, datetime.min.time()),
                                projects_created=2 - (i % 3),
                                projects_completed=1 + (i % 2),
                                total_downloads=5 + i,
                                active_users=3 + (i % 4),
                                avg_generation_time=30.0 + (i * 5),
                                total_lines_generated=500 + (i * 100)
                            )
                            db.add(stats)
                        
                        db.commit()
                        logger.info("✅ Sample activity data created!")
                    else:
                        logger.info("No existing users/projects found, skipping sample data creation")
                else:
                    logger.info(f"Activity data already exists ({existing_activities} records)")
                    
            except Exception as e:
                logger.error(f"Failed to create sample data: {e}")
                db.rollback()
            finally:
                db.close()
                
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    create_activity_tables()
    logger.info("🎉 Activity tracking system migration completed!")