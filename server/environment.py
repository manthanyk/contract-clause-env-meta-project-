from models import (
    ContractClauseAction,
    ContractClauseObservation,
    ContractClauseState,
    StepResult,
)
from tasks.easy import EasyTask
from tasks.medium import MediumTask
from tasks.hard import HardTask
import uuid


class MyEnvironment:
    """Standalone environment implementation"""

    def __init__(self):
        self.tasks = {
            "easy": EasyTask(),
            "medium": MediumTask(),
            "hard": HardTask(),
        }
        self._episode_id = None
        self._step_count = 0
        self._current_task = None
        self._score = 0.05

    async def reset(self, task_id: str = "easy") -> ContractClauseObservation:
        self._episode_id = str(uuid.uuid4())
        self._step_count = 0
        self._score = 0.05
        self._current_task = self.tasks[task_id]
        return await self._current_task.reset()

    async def step(self, action: ContractClauseAction) -> StepResult:
        self._step_count += 1
        obs, reward, done = await self._current_task.step(action)
        self._score += reward
        return StepResult(
            observation=obs,
            reward=reward,
            done=done,
            info={"step": self._step_count, "cumulative_score": self._score},
        )

    async def state(self) -> ContractClauseState:
        return ContractClauseState(
            episode_id=self._episode_id or "not_started",
            step_count=self._step_count,
            task_id=self._current_task.__class__.__name__ if self._current_task else "",
            is_done=False,
            cumulative_score=self._score,
        )
