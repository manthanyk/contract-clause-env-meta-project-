from models import MyAction, MyObservation
from typing import Tuple
from abc import ABC, abstractmethod


class BaseTask(ABC):
    """Base class for all task implementations"""

    COMPLETION_THRESHOLD = 0.95
    HINT_THRESHOLDS = [0.9, 0.7, 0.5, 0.3]

    def __init__(self, max_steps: int, difficulty: str):
        self.max_steps = max_steps
        self.step_count = 0
        self.difficulty = difficulty
        self.current_state = {}

    @abstractmethod
    async def reset(self) -> MyObservation:
        """Reset the task and return initial observation"""
        pass

    async def step(self, action: MyAction) -> Tuple[MyObservation, float, bool]:
        """Execute one step and return (observation, reward, done)"""
        self.step_count += 1
        self.current_state = self._apply_action(action)
        reward = self._grade()
        done = reward >= self.COMPLETION_THRESHOLD or self.step_count >= self.max_steps
        obs = MyObservation(
            current_state=self.current_state,
            available_actions=self._get_available_actions(),
            progress_hint=self._get_hint(reward)
        )
        return obs, reward, done

    @abstractmethod
    def _apply_action(self, action: MyAction) -> dict:
        """Apply action to current state and return new state"""
        pass

    @abstractmethod
    def _grade(self) -> float:
        """Calculate reward for current state (0.0-1.0)"""
        pass

    @abstractmethod
    def _get_available_actions(self) -> list:
        """Return list of available action names"""
        pass

    def _get_hint(self, reward: float) -> str:
        """Provide progress hint based on reward level"""
        return ""
