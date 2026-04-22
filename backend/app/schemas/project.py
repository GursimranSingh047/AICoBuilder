from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any


# ─── Request Schemas ──────────────────────────────────────────────────────────

class GenerateProjectRequest(BaseModel):
    idea: str = Field(..., min_length=10, max_length=2000, description="Plain-language project idea")
    project_name: str | None = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "idea": "A task management app with real-time collaboration and AI suggestions",
                "project_name": "CollabTask"
            }
        }
    }


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    project_id: int | None = None
    history: list[dict[str, str]] = Field(default_factory=list)


class SuggestRequest(BaseModel):
    idea: str = Field(..., min_length=5, max_length=1000)


# ─── Response Schemas ─────────────────────────────────────────────────────────

class FileNode(BaseModel):
    name: str
    type: str           # "file" | "folder"
    path: str
    content: str | None = None
    children: list["FileNode"] = Field(default_factory=list)


class GenerateProjectResponse(BaseModel):
    project_id: int
    name: str
    tech_stack: dict[str, Any]
    folder_structure: dict[str, Any]
    files: dict[str, str]          # path → content
    readme: str
    status: str
    zip_download_url: str | None = None


class ChatResponse(BaseModel):
    reply: str
    project_id: int | None = None


class SuggestResponse(BaseModel):
    recommended_stack: dict[str, str]
    suggested_features: list[str]
    project_type: str
    confidence: float


class ProjectSummary(BaseModel):
    id: int
    name: str
    description: str | None
    status: str
    tech_stack: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectSummary):
    idea_prompt: str
    folder_structure: dict[str, Any]
    generated_files: dict[str, Any]
    zip_path: str | None
    local_path: str | None
