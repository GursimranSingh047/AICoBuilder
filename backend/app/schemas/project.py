from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional, List, Dict


# ─── Request Schemas ──────────────────────────────────────────────────────────

class GenerateProjectRequest(BaseModel):
    idea: str = Field(..., min_length=10, max_length=2000, description="Plain-language project idea")
    project_name: Optional[str] = Field(None, max_length=100)

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
    project_id: Optional[int] = None
    history: List[Dict[str, str]] = Field(default_factory=list)


class SuggestRequest(BaseModel):
    idea: str = Field(..., min_length=5, max_length=1000)


# ─── Response Schemas ─────────────────────────────────────────────────────────

class FileNode(BaseModel):
    name: str
    type: str           # "file" | "folder"
    path: str
    content: Optional[str] = None
    children: List["FileNode"] = Field(default_factory=list)


class GenerateProjectResponse(BaseModel):
    project_id: int
    name: str
    tech_stack: Dict[str, Any]
    folder_structure: Dict[str, Any]
    files: Dict[str, str]          # path → content
    readme: str
    status: str
    zip_download_url: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    project_id: Optional[int] = None


class SuggestResponse(BaseModel):
    recommended_stack: Dict[str, str]
    suggested_features: List[str]
    project_type: str
    confidence: float


class ProjectSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    tech_stack: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectSummary):
    idea_prompt: str
    folder_structure: Dict[str, Any]
    generated_files: Dict[str, Any]
    zip_path: Optional[str]
    local_path: Optional[str]
