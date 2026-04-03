from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MyAction(BaseModel):
    """Define ALL possible actions the agent can take"""
    action_type: str = Field(..., description="Type of action")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    task_id: Optional[str] = None

class MyObservation(BaseModel):
    """Everything the agent can observe about the environment state"""
    current_state: Dict[str, Any] = Field(default_factory=dict)
    available_actions: List[str] = Field(default_factory=list)
    task_description: str = ""
    progress_hint: Optional[str] = None

class MyState(BaseModel):
    """Episode metadata"""
    episode_id: str
    step_count: int = 0
    task_id: str = ""
    difficulty: TaskDifficulty = TaskDifficulty.EASY
    is_done: bool = False
    score: float = 0.0

class StepResult(BaseModel):
    """Result of a step action"""
    observation: MyObservation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)