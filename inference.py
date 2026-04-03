import os
import sys
import json
import asyncio
from openai import OpenAI
from client import MyEnvClient
from models import (
    ContractClauseAction,
    ActionType,
    ClauseType,
    RiskLevel,
)

# REQUIRED: These env vars must be set
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_SPACE_URL = os.environ.get("HF_SPACE_URL", "http://localhost:7860")

# MUST use OpenAI client (not Anthropic SDK)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=os.environ.get("OPENAI_API_KEY", HF_TOKEN),
)


def log_start(task_id: str, episode: int):
    print(
        json.dumps({"type": "START", "task_id": task_id, "episode": episode}),
        flush=True,
    )


def log_step(step: int, action: dict, reward: float, done: bool):
    print(
        json.dumps(
            {
                "type": "STEP",
                "step": step,
                "action": action,
                "reward": reward,
                "done": done,
            }
        ),
        flush=True,
    )


def log_end(total_reward: float, steps: int):
    print(
        json.dumps(
            {"type": "END", "total_reward": round(total_reward, 4), "steps": steps}
        ),
        flush=True,
    )


def build_prompt_for_task(task_id: str, obs) -> str:
    """Build an LLM prompt appropriate for the task type."""
    if task_id == "easy":
        return (
            f"You are reviewing a contract to identify MISSING critical clauses.\n\n"
            f"Contract text:\n{obs.contract_text}\n\n"
            f"Available actions: {[a.value for a in obs.available_actions]}\n\n"
            f"Return a JSON action. Example:\n"
            f'{{"action_type": "flag_missing", "missing_clauses": ["termination", "payment", "governing_law"]}}'
        )
    elif task_id == "medium":
        return (
            f"You are assessing the RISK LEVEL of contract clauses.\n\n"
            f"Contract text:\n{obs.contract_text}\n\n"
            f"Available actions: {[a.value for a in obs.available_actions]}\n\n"
            f"Return a JSON action. Example:\n"
            f'{{"action_type": "risk_assess", "risk_level": "high", "risk_explanation": "The payment clause has excessive penalties."}}'
        )
    else:
        return (
            f"You are detecting UNFAIR or unconscionable clauses in a contract.\n\n"
            f"Contract text:\n{obs.contract_text}\n\n"
            f"Available actions: {[a.value for a in obs.available_actions]}\n\n"
            f"Return a JSON action. Example:\n"
            f'{{"action_type": "flag_unfair", "unfair_clause": "unilateral modification", "unfair_reason": "This clause allows one-sided changes."}}'
        )


def parse_action(task_id: str, content: str) -> ContractClauseAction:
    """Parse LLM response into a ContractClauseAction."""
    try:
        data = json.loads(content)
        action_type = ActionType(data.get("action_type", "request_clarification"))

        kwargs: dict = {"action_type": action_type}

        if action_type == ActionType.FLAG_MISSING:
            clauses = data.get("missing_clauses", [])
            kwargs["missing_clauses"] = [
                ClauseType(c) for c in clauses if c in [e.value for e in ClauseType]
            ]
        elif action_type == ActionType.RISK_ASSESS:
            rl = data.get("risk_level")
            kwargs["risk_level"] = (
                RiskLevel(rl) if rl and rl in [e.value for e in RiskLevel] else None
            )
            kwargs["risk_explanation"] = data.get("risk_explanation", "")
        elif action_type == ActionType.FLAG_UNFAIR:
            kwargs["unfair_clause"] = data.get("unfair_clause", "")
            kwargs["unfair_reason"] = data.get("unfair_reason", "")
        elif action_type == ActionType.REQUEST_CLARIFICATION:
            kwargs["clarification_request"] = data.get(
                "clarification_request", "Need more context."
            )

        return ContractClauseAction(**kwargs)
    except Exception:
        # Fallback: request clarification
        return ContractClauseAction(
            action_type=ActionType.REQUEST_CLARIFICATION,
            clarification_request="Unable to parse previous response.",
        )


async def run_episode(task_id: str, episode: int) -> float:
    """Run one episode and return total reward."""
    log_start(task_id, episode)

    async with MyEnvClient(base_url=HF_SPACE_URL) as env:
        obs = await env.reset(task_id=task_id)
        total_reward = 0.0
        done = False
        step_num = 0
        max_steps = 20

        while not done and step_num < max_steps:
            prompt = build_prompt_for_task(task_id, obs)
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a contract review agent. Respond with valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=500,
                    temperature=0.3,
                )
                content = response.choices[0].message.content or ""
            except Exception as e:
                print(json.dumps({"type": "ERROR", "message": str(e)}), flush=True)
                content = ""

            action = parse_action(task_id, content)
            result = await env.step(action)

            step_num += 1
            total_reward += result.reward
            done = result.done
            obs = result.observation

            log_step(
                step=step_num,
                action=action.model_dump(),
                reward=round(result.reward, 4),
                done=done,
            )

    log_end(total_reward=total_reward, steps=step_num)
    return total_reward


async def main():
    print(
        json.dumps({"type": "INFERENCE_START", "tasks": ["easy", "medium", "hard"]}),
        flush=True,
    )
    results = {}

    for task_id in ["easy", "medium", "hard"]:
        try:
            score = await run_episode(task_id=task_id, episode=1)
            results[task_id] = score
            print(
                json.dumps(
                    {
                        "type": "TASK_RESULT",
                        "task_id": task_id,
                        "score": round(score, 4),
                    }
                ),
                flush=True,
            )
        except Exception as e:
            print(
                json.dumps({"type": "TASK_ERROR", "task_id": task_id, "error": str(e)}),
                flush=True,
            )
            results[task_id] = 0.0

    avg = sum(results.values()) / len(results) if results else 0.0
    print(
        json.dumps({"type": "FINAL", "results": results, "average": round(avg, 4)}),
        flush=True,
    )
    return results


if __name__ == "__main__":
    asyncio.run(main())
