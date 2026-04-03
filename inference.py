import os
import asyncio
from openai import OpenAI
from client import MyEnvClient, MyAction

# REQUIRED: These env vars must be set
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME")
HF_TOKEN = os.environ.get("HF_TOKEN")

# MUST use OpenAI client (not Anthropic SDK)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=os.environ.get("OPENAI_API_KEY", HF_TOKEN),
)

HF_SPACE_URL = os.environ.get("HF_SPACE_URL", "http://localhost:7860")

async def run_episode(task_id: str = "easy") -> float:
    """Run one episode and return the score"""
    async with MyEnvClient(base_url=HF_SPACE_URL) as env:
        obs = await env.reset(task_id=task_id)
        total_reward = 0.0
        done = False
        step = 0

        while not done and step < 20:
            # Use LLM to decide action
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an agent solving tasks. Respond with a JSON action."},
                    {"role": "user", "content": f"Current observation: {obs.model_dump_json()}\nWhat action do you take?"}
                ],
                max_tokens=500,
            )

            # Parse action from LLM response
            try:
                action = MyAction.model_validate_json(
                    response.choices[0].message.content
                )
            except Exception as e:
                print(f"Error parsing action: {e}")
                # Fallback to a default action
                action = MyAction(action_type="check_item", parameters={})

            result = await env.step(action)
            total_reward += result.reward
            done = result.done
            obs = result.observation
            step += 1

    return total_reward

async def main():
    print("Running baseline inference across all task difficulties...")
    results = {}

    for task_id in ["easy", "medium", "hard"]:
        try:
            score = await run_episode(task_id=task_id)
            results[task_id] = score
            print(f"  Task '{task_id}': score = {score:.3f}")
        except Exception as e:
            print(f"  Task '{task_id}': ERROR - {e}")
            results[task_id] = 0.0

    avg = sum(results.values()) / len(results)
    print(f"\nBaseline average score: {avg:.3f}")
    return results

if __name__ == "__main__":
    asyncio.run(main())