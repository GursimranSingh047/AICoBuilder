from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
from loguru import logger

from app.database import get_db
from app.models.project import Project
from app.schemas.project import (
    GenerateProjectRequest, GenerateProjectResponse,
    ProjectSummary, ProjectDetail,
)
from app.services.project_generator import project_generator
from app.services.activity_service import activity_service
from app.dependencies import get_optional_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/generate", response_model=GenerateProjectResponse, status_code=201)
def generate_project(
    payload: GenerateProjectRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """
    Core endpoint – runs the full V1+V2 generation pipeline.
    No auth required (optional user attaches project to account).
    """
    logger.info(f"Generating project for idea: {payload.idea[:60]}...")

    # Create a DB record with status=generating
    project = Project(
        name=payload.project_name or "Pending...",
        idea_prompt=payload.idea,
        status="generating",
        owner_id=current_user.id if current_user else None,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Log project creation activity
    try:
        activity_service.log_activity(
            db=db,
            action="project_created",
            user_id=current_user.id if current_user else None,
            project_id=project.id,
            description=f"Started generating project: {payload.project_name or 'Unnamed'}",
            metadata={"idea_length": len(payload.idea), "has_custom_name": bool(payload.project_name)},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.warning(f"Failed to log project creation activity: {e}")

    try:
        result = project_generator.generate(
            idea=payload.idea,
            project_name=payload.project_name,
        )

        # Persist results
        project.name = result["name"]
        project.tech_stack = result["tech_stack"]
        project.folder_structure = result["folder_structure"]
        project.generated_files = {k: v[:500] for k, v in result["files"].items()}  # store preview
        project.local_path = result["local_path"]
        project.zip_path = result["zip_path"]
        project.status = "completed"
        db.commit()
        db.refresh(project)

        # Log project completion activity
        try:
            activity_service.log_activity(
                db=db,
                action="project_completed",
                user_id=current_user.id if current_user else None,
                project_id=project.id,
                description=f"Successfully generated project: {project.name}",
                metadata={
                    "tech_stack": result["tech_stack"],
                    "file_count": len(result["files"]),
                    "folder_count": len(result["folder_structure"]) if isinstance(result["folder_structure"], list) else 0
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        except Exception as e:
            logger.warning(f"Failed to log project completion activity: {e}")

        return GenerateProjectResponse(
            project_id=project.id,
            name=project.name,
            tech_stack=result["tech_stack"],
            folder_structure=result["folder_structure"],
            files=result["files"],
            readme=result["readme"],
            status="completed",
            zip_download_url=f"/projects/{project.id}/download",
        )

    except Exception as exc:
        logger.error(f"Project generation failed: {exc}")
        project.status = "failed"
        db.commit()
        
        # Log project failure activity
        try:
            activity_service.log_activity(
                db=db,
                action="project_failed",
                user_id=current_user.id if current_user else None,
                project_id=project.id,
                description=f"Project generation failed: {str(exc)[:200]}",
                metadata={"error": str(exc)[:500]},
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        except Exception as e:
            logger.warning(f"Failed to log project failure activity: {e}")
            
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(exc)}")


@router.get("/", response_model=List[ProjectSummary])
def list_projects(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """List all projects (filtered to owner if authenticated)."""
    query = db.query(Project)
    if current_user:
        query = query.filter(Project.owner_id == current_user.id)
    return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user)
):
    """Get full project details including generated files."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    # Log project view activity (non-blocking)
    try:
        activity_service.log_activity(
            db=db,
            action="project_viewed",
            user_id=current_user.id if current_user else None,
            project_id=project.id,
            description=f"Viewed project: {project.name}",
            metadata={"project_status": project.status},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.warning(f"Failed to log project view activity: {e}")
    
    return project


@router.get("/{project_id}/download")
def download_project(
    project_id: int, 
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user)
):
    """Download the generated project as a ZIP archive."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not project.zip_path or not Path(project.zip_path).exists():
        raise HTTPException(status_code=404, detail="ZIP file not found. Re-generate the project.")
    
    # Log project download activity (non-blocking)
    try:
        activity_service.log_activity(
            db=db,
            action="project_downloaded",
            user_id=current_user.id if current_user else None,
            project_id=project.id,
            description=f"Downloaded project: {project.name}",
            metadata={"file_size": Path(project.zip_path).stat().st_size if Path(project.zip_path).exists() else 0},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.warning(f"Failed to log project download activity: {e}")
    
    return FileResponse(
        project.zip_path,
        media_type="application/zip",
        filename=f"{project.name.replace(' ', '_')}.zip",
    )


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """Delete a project record (and optionally its files)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    # Log project deletion activity before deleting
    try:
        activity_service.log_activity(
            db=db,
            action="project_deleted",
            user_id=current_user.id if current_user else None,
            project_id=project.id,
            description=f"Deleted project: {project.name}",
            metadata={"project_status": project.status},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    except Exception as e:
        logger.warning(f"Failed to log project deletion activity: {e}")
    
    db.delete(project)
    db.commit()
