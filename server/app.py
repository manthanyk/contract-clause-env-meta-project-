from fastapi import FastAPI
from pydantic import BaseModel
from server.environment import MyEnvironment
from models import MyAction, MyObservation, MyState, StepResult
import uvicorn

# Create the environment instance
environment = MyEnvironment()

# Create the FastAPI app
app = FastAPI(title="Resource Allocation Environment", version="1.0.0")

@app.post("/reset", response_model=MyObservation)
async def reset(task_id: str = "easy"):
    """Reset the environment to start a new episode"""
    return await environment.reset(task_id)

@app.post("/step", response_model=StepResult)
async def step(action: MyAction):
    """Execute one step in the environment"""
    return await environment.step(action)

@app.get("/state", response_model=MyState)
async def state():
    """Get the current state of the environment"""
    return await environment.state()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)