from models import MyAction, MyObservation, MyState
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

    async def reset(self, task_id: str = "easy") -> MyObservation:
        response = await self.client.post(
            f"{self.base_url}/reset",
            json={"task_id": task_id}
        )
        response.raise_for_status()
        data = response.json()
        return MyObservation(**data)

    async def step(self, action: MyAction) -> "StepResult":
        response = await self.client.post(
            f"{self.base_url}/step",
            json=action.model_dump()
        )
        response.raise_for_status()
        data = response.json()

        # Import here to avoid circular imports
        from models import StepResult
        return StepResult(**data)

    async def state(self) -> MyState:
        response = await self.client.get(f"{self.base_url}/state")
        response.raise_for_status()
        data = response.json()
        return MyState(**data)