import asyncio
from server.environment import MyEnvironment
from models import MyAction

async def test_environment():
    """Test the environment implementation"""
    env = MyEnvironment()

    # Test reset for each task
    for task_id in ["easy", "medium", "hard"]:
        print(f"Testing {task_id} task...")
        obs = await env.reset(task_id=task_id)
        print(f"  Observation: {obs}")

        # Test a simple step
        action = MyAction(action_type="check_item", parameters={})
        result = await env.step(action)
        print(f"  Step result: reward={result.reward}, done={result.done}")

        # Test state
        state = await env.state()
        print(f"  State: {state}")
        print()

if __name__ == "__main__":
    asyncio.run(test_environment())