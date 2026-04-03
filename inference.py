import os
import json
import asyncio
import subprocess
from typing import Dict, Any

import httpx
from openai import OpenAI

from client import MyEnvClient
from models import (
    ContractClauseAction,
    ActionType,
    ClauseType,
    RiskLevel,
)

# Environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "")
BASE_URL = os.getenv("ENV_URL", "http://localhost:7860")
LOCAL_SERVER = os.getenv("LOCAL_SERVER", "true").lower() != "false"

# OpenAI client pointing to HF endpoint
client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

_server_process = None


async def _is_server_up(base_url: str) -> bool:
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=2.0) as c:
            resp = await c.get("/health")
            return resp.status_code == 200
    except Exception:
        return False


async def _ensure_server(base_url: str):
    """Start local uvicorn if requested and not already running."""
    global _server_process
    if not LOCAL_SERVER:
        return
    if await _is_server_up(base_url):
        return
    _server_process = subprocess.Popen(
        ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(10):
        if await _is_server_up(base_url):
            return
        await asyncio.sleep(0.5)
    raise RuntimeError("Local server failed to start on http://localhost:7860")


def log_start(task_id: str, episode: int):
    print("[START]", json.dumps({"task_id": task_id, "episode": episode}), flush=True)


def log_step(step: int, action: dict, reward: float, done: bool):
    print(
        "[STEP]",
        json.dumps({"step": step, "action": action, "reward": reward, "done": done}),
        flush=True,
    )


def log_end(total_reward: float, steps: int, task_id: str):
    print(
        "[END]",
        json.dumps(
            {
                "total_reward": round(total_reward, 4),
                "steps": steps,
                "task_id": task_id,
            }
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


def _safe_json_parse(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines[-1].strip() == "```":
            raw = "\n".join(lines[1:-1])
        else:
            raw = "\n".join(lines[1:])
    return json.loads(raw)


def parse_action(task_id: str, content: str) -> ContractClauseAction:
    """Parse LLM response into a ContractClauseAction."""
    try:
        data = _safe_json_parse(content)
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

    await _ensure_server(BASE_URL)

    async with MyEnvClient(base_url=BASE_URL) as env:
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
                print(f"LLM error: {e}", flush=True)
                content = ""

            action = parse_action(task_id, content)
            result = await env.step(action)

            step_num += 1
            total_reward += result.reward
            done = result.done
            obs = result.observation

            log_step(
                step=step_num,
                action=action.model_dump(exclude_none=True),
                reward=round(result.reward, 4),
                done=done,
            )

    log_end(total_reward=total_reward, steps=step_num, task_id=task_id)
    return total_reward


async def main():
    results = {}

    for task_id in ["easy", "medium", "hard"]:
        try:
            score = await run_episode(task_id=task_id, episode=1)
            results[task_id] = score
        except Exception as e:
            print(f"Task '{task_id}' ERROR: {e}", flush=True)
            results[task_id] = 0.0

    avg = sum(results.values()) / len(results) if results else 0.0
    print(f"Average score: {avg:.4f}", flush=True)
    return results


if __name__ == "__main__":
    asyncio.run(main())
