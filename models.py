from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum

try:
    from .common.utils import safe_score
except ImportError:
    from common.utils import safe_score


class ActionType(str, Enum):
    FLAG_MISSING = "flag_missing"
    RISK_ASSESS = "risk_assess"
    FLAG_UNFAIR = "flag_unfair"
    REQUEST_CLARIFICATION = "request_clarification"
    PROPOSE_REVISION = "propose_revision"
    APPROVE = "approve"
    REJECT = "reject"


class ClauseType(str, Enum):
    TERMINATION = "termination"
    PAYMENT = "payment"
    LIABILITY = "liability"
    LIMITATION_LIABILITY = "limitation_liability"
    INDEMNIFICATION = "indemnification"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"
    FORCE_MAJEURE = "force_majeure"


class RiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContractClauseAction(BaseModel):
    """Action the agent can take to analyze contract clauses"""

    action_type: ActionType = Field(..., description="Type of action to perform")
    missing_clauses: Optional[List[ClauseType]] = Field(
        default=None, description="List of missing clause types"
    )
    risk_level: Optional[RiskLevel] = Field(
        default=None, description="Risk assessment level"
    )
    risk_explanation: Optional[str] = Field(
        default=None, description="Explanation for risk assessment"
    )
    unfair_clause: Optional[str] = Field(
        default=None, description="Text of unfair clause identified"
    )
    unfair_reason: Optional[str] = Field(
        default=None, description="Explanation of why clause is unfair"
    )
    clarification_request: Optional[str] = Field(
        default=None, description="Specific clarification needed"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters"
    )


class ContractClauseObservation(BaseModel):
    """Observation of contract state"""

    contract_text: str = Field(..., description="Full contract text to analyze")
    task_description: str = Field(..., description="Description of the task")
    current_score: float = Field(
        default=0.05, description="Current score in range (0.0, 1.0)"
    )
    step_count: int = Field(default=0, description="Current step count")
    max_steps: int = Field(default=20, description="Maximum steps allowed")
    available_actions: List[ActionType] = Field(
        default_factory=list, description="Available actions"
    )
    progress_hint: Optional[str] = Field(default=None, description="Hint for progress")
    review_comments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Comments from review"
    )

    @field_validator("current_score", mode="before")
    @classmethod
    def _clamp_current_score(cls, value: Any) -> float:
        """Normalize observation scores to the allowed open interval."""
        return safe_score(value)


class ContractClauseState(BaseModel):
    """Episode state metadata"""

    episode_id: str = Field(..., description="Unique episode identifier")
    step_count: int = Field(default=0, description="Current step count")
    task_id: str = Field(..., description="Current task ID")
    is_done: bool = Field(default=False, description="Whether episode is complete")
    cumulative_score: float = Field(default=0.05, description="Cumulative reward score")

    @field_validator("cumulative_score", mode="before")
    @classmethod
    def _clamp_cumulative_score(cls, value: Any) -> float:
        """Normalize cumulative scores to the allowed open interval."""
        return safe_score(value)


class StepResult(BaseModel):
    """Result of a step action"""

    observation: ContractClauseObservation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("reward", mode="before")
    @classmethod
    def _clamp_reward(cls, value: Any) -> float:
        """Normalize rewards to the allowed open interval."""
        return safe_score(value)
