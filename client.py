try:
    from .models import (
        ContractClauseAction,
        ContractClauseObservation,
        ContractClauseState,
        StepResult,
    )
except ImportError:
    from models import (
        ContractClauseAction,
        ContractClauseObservation,
        ContractClauseState,
        StepResult,
    )
import httpx
from typing import Optional


class MyEnvClient:
    """Client for interacting with the environment"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def reset(self, task_id: str = "easy") -> ContractClauseObservation:
        response = await self.client.post(
            f"{self.base_url}/reset", json={"task_id": task_id}
        )
        response.raise_for_status()
        data = response.json()
        return ContractClauseObservation(**data)

    async def step(self, action: ContractClauseAction) -> StepResult:
        response = await self.client.post(
            f"{self.base_url}/step", json=action.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        data = response.json()
        return StepResult(**data)

    async def state(self) -> ContractClauseState:
        response = await self.client.get(f"{self.base_url}/state")
        response.raise_for_status()
        data = response.json()
        return ContractClauseState(**data)
