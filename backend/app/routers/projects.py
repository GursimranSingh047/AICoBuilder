from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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
from app.dependencies import get_optional_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/generate", response_model=GenerateProjectResponse, status_code=201)
def generate_project(
    payload: GenerateProjectRequest,
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
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get full project details including generated files."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.get("/{project_id}/download")
def download_project(project_id: int, db: Session = Depends(get_db)):
    """Download the generated project as a ZIP archive."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not project.zip_path or not Path(project.zip_path).exists():
        raise HTTPException(status_code=404, detail="ZIP file not found. Re-generate the project.")
    return FileResponse(
        project.zip_path,
        media_type="application/zip",
        filename=f"{project.name.replace(' ', '_')}.zip",
    )


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """Delete a project record (and optionally its files)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    db.delete(project)
    db.commit()
