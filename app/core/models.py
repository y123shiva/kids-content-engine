from pydantic import BaseModel, Field, conint
from typing import List, Optional

# Instead of using the alias in the annotation directly, define with Field
class TopicRequest(BaseModel):
    month: int = Field(..., ge=1, le=12)   # month must be between 1 and 12
    category: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)

class Scene(BaseModel):
    scene_number: int
    timestamp: Optional[str] = "00:00"
    text: str
    visuals: str
    audio_cues: Optional[List[str]] = Field(default_factory=list)

class ScriptResponse(BaseModel):
    month: int
    category: str
    title: str
    scenes: List[Scene]

class RAGQuery(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(default=3, gt=0)  # must be >0
