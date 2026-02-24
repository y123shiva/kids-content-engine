from pydantic import BaseModel, Field
from typing import List, Literal

class Scene(BaseModel):
    scene_number: int = Field(..., ge=1)
    timestamp: str = Field(
        ..., 
        description="Time marker or range, e.g. '00:00' or '00:10-00:25'"
    )
    # We add emotion here to drive the character's facial expressions
    emotion: str = Field(
        default="HAPPY", 
        description="Bibo's mood: HAPPY, EXCITED, SURPRISED, or THINKING"
    )
    speaker: str = Field(..., min_length=1)
    narration: str = Field(..., min_length=1)
    actions: List[str] = Field(default_factory=list)
    visuals: List[str] = Field(default_factory=list)

class ScriptOutput(BaseModel):
    title: str = Field(..., min_length=1)
    character: str = Field(..., min_length=1)
    age_group: str
    # Changed to float to allow for precise audio timestamps (e.g., 33.12s)
    duration_seconds: float = Field(..., gt=0) 
    learning_goals: List[str] = Field(default_factory=list)
    scenes: List[Scene] = Field(..., min_items=1)