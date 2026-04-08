from models import ContractClauseAction, ContractClauseObservation
from typing import Tuple
from abc import ABC, abstractmethod
from common.utils import safe_score


class BaseTask(ABC):
    """Base class for all contract clause task implementations"""

    COMPLETION_THRESHOLD = 0.93
    HINT_THRESHOLDS = [0.9, 0.7, 0.5, 0.3]

    def __init__(self, max_steps: int, difficulty: str):
        self.max_steps = max_steps
        self.step_count = 0
        self.difficulty = difficulty
        self.current_state = {}

    @abstractmethod
    async def reset(self) -> ContractClauseObservation:
        """Reset the task and return initial observation"""
        pass

    async def step(
        self, action: ContractClauseAction
    ) -> Tuple[ContractClauseObservation, float, bool]:
        """Execute one step and return (observation, reward, done)"""
        self.step_count += 1
        self.current_state = self._apply_action(action)
        raw_grade = self._grade(action)
        reward = safe_score(raw_grade)
        assert 0.0 < reward < 1.0, "Reward out of range"
        done = reward >= self.COMPLETION_THRESHOLD or self.step_count >= self.max_steps
        obs = ContractClauseObservation(
            contract_text=self._get_contract_text(),
            task_description=self._get_task_description(),
            current_score=reward,
            step_count=self.step_count,
            max_steps=self.max_steps,
            available_actions=self._get_available_actions(),
            progress_hint=self._get_hint(reward),
            review_comments=self._get_review_comments(),
        )
        return obs, reward, done

    @abstractmethod
    def _apply_action(self, action: ContractClauseAction) -> dict:
        """Apply action to current state and return new state"""
        pass

    @abstractmethod
    def _grade(self, action: ContractClauseAction) -> float:
        """Calculate reward for current state (0.05-0.95)"""
        pass

    @abstractmethod
    def _get_available_actions(self) -> list:
        """Return list of available action types"""
        pass

    @abstractmethod
    def _get_contract_text(self) -> str:
        """Return the contract text"""
        pass

    @abstractmethod
    def _get_task_description(self) -> str:
        """Return the task description"""
        pass

    def _get_review_comments(self) -> list:
        """Return review comments"""
        return []

    def _get_hint(self, reward: float) -> str:
        """Provide progress hint based on reward level"""
        return ""

    @staticmethod
    def _clamp(score: float) -> float:
        """Ensure scores remain strictly within (0, 1)."""
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.05
        return round(max(0.05, min(0.95, score)), 4)
