from fastapi import APIRouter
from loguru import logger

from app.schemas.project import SuggestRequest, SuggestResponse
from app.services.ml_service import ml_service

router = APIRouter(prefix="/suggest", tags=["Suggestions"])


@router.post("/", response_model=SuggestResponse)
def suggest(payload: SuggestRequest):
    """
    ML-powered endpoint – predicts project type, tech stack, and features
    from a plain-text idea.
    """
    logger.info(f"Suggest request: {payload.idea[:60]}")
    prediction = ml_service.predict(payload.idea)

    return SuggestResponse(
        recommended_stack=prediction["recommended_stack"],
        suggested_features=prediction["suggested_features"],
        project_type=prediction["project_type"],
        confidence=prediction["confidence"],
    )


@router.get("/stacks")
def list_stacks():
    """Return all available tech stacks keyed by project type."""
    from app.services.ml_service import STACK_MAP
    return STACK_MAP


@router.get("/features/{project_type}")
def features_for_type(project_type: str):
    """Return suggested features for a given project type."""
    from app.services.ml_service import FEATURES_MAP
    features = FEATURES_MAP.get(project_type)
    if not features:
        return {"error": f"Unknown project type: {project_type}", "available": list(FEATURES_MAP)}
    return {"project_type": project_type, "features": features}
