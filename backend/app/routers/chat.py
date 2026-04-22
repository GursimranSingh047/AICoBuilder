from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

import httpx
from app.core.config import settings

from app.database import get_db
from app.models.project import Project, Prompt
from app.schemas.project import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Conversational AI endpoint.
    Optionally provide a project_id for context-aware responses.
    History is sent from the client (stateless server).
    """
    context = ""
    if payload.project_id:
        project = db.query(Project).filter(Project.id == payload.project_id).first()
        if project:
            context = (
                f"Project: {project.name}\n"
                f"Stack: {project.tech_stack}\n"
                f"Idea: {project.idea_prompt[:300]}"
            )

    logger.info(f"Chat request | project_id={payload.project_id} msg_len={len(payload.message)}")

    reply = gemini_service.chat(
        message=payload.message,
        history=payload.history,
        context=context,
    )

    # Persist prompt + reply
    if payload.project_id:
        for role, content in [("user", payload.message), ("assistant", reply)]:
            db.add(Prompt(role=role, content=content, project_id=payload.project_id))
        db.commit()

    return ChatResponse(reply=reply, project_id=payload.project_id)


@router.post("/improve")
def improve_code(code: str, instruction: str):
    """Improve a code snippet based on a plain-English instruction."""
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    result = gemini_service.improve_code(code, instruction)
    return {"improved_code": result}


@router.post("/explain")
def explain_code(code: str):
    """Get a plain-English explanation of a code snippet."""
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
    result = gemini_service.explain_code(code)
    return {"explanation": result}


# ✅ STEP 5 ADDITION
@router.get("/debug/models")
def debug_models():
    # Return available models via the service (handles OpenAI vs Gemini keys)
    return {"models": gemini_service.list_available_models()}