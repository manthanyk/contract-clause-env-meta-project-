import os
import json
import uuid
import asyncio
import httpx
import random
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN", "")
ENV_URL = os.getenv("ENV_URL", "https://manthanyk-contract-clause-env.hf.space")
TIMEOUT_SECONDS = 20 * 60

llm_client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

# ── HTTP client ────────────────────────────────────────────────────────────────
_http = httpx.AsyncClient(timeout=30.0)


async def api_reset(task_id: str) -> Dict[str, Any]:
    resp = await _http.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    resp.raise_for_status()
    return resp.json()


async def api_step(action: Dict[str, Any]) -> Dict[str, Any]:
    resp = await _http.post(f"{ENV_URL}/step", json=action)
    resp.raise_for_status()
    return resp.json()


async def api_state() -> Dict[str, Any]:
    resp = await _http.get(f"{ENV_URL}/state")
    resp.raise_for_status()
    return resp.json()


# ── Structured logging ─────────────────────────────────────────────────────────
def log_start(task_id: str, episode_id: str):
    print(
        f'[START] {{"task_id": "{task_id}", "episode_id": "{episode_id}"}}', flush=True
    )


def log_step(step: int, action: Dict[str, Any], reward: float, done: bool):
    print(
        f"[STEP] {json.dumps({'step': step, 'action': action, 'reward': reward, 'done': done})}",
        flush=True,
    )


def log_end(task_id: str, final_score: float):
    print(
        f'[END] {{"task_id": "{task_id}", "final_score": {final_score}}}',
        flush=True,
    )


# ── Fallback scoring (offline, deterministic) ──────────────────────────────────
def _fallback_action(task_id: str, contract_text: str, step_num: int) -> Dict[str, Any]:
    """Generate fallback action when LLM is unavailable."""
    text_lower = contract_text.lower()

    if task_id == "easy":
        missing_keywords = [
            "termination",
            "payment",
            "liability",
            "indemnification",
            "governing_law",
            "dispute_resolution",
            "force_majeure",
        ]
        found = [kw for kw in missing_keywords if kw in text_lower]
        if not found or step_num == 1:
            return {
                "action_type": "flag_missing",
                "missing_clauses": missing_keywords[:4],
            }
        return {
            "action_type": "request_clarification",
            "clarification_request": "Reviewing contract terms.",
        }

    elif task_id == "medium":
        risk_keywords = ["penalty", "liability", "indemnify", "waive", "terminate"]
        found_risk = any(kw in text_lower for kw in risk_keywords)
        if not found_risk or step_num == 1:
            return {
                "action_type": "risk_assess",
                "risk_level": "medium",
                "risk_explanation": "This contract contains several clauses that may pose risks including payment penalties, liability limitations, and broad indemnification terms. The asymmetric nature of these provisions warrants careful review.",
            }
        return {
            "action_type": "request_clarification",
            "clarification_request": "Analyzing additional clauses.",
        }

    elif task_id == "hard":
        unfair_keywords = [
            "unilateral",
            "perpetual",
            "waive",
            "any reason",
            "indemnify",
            "unlimited",
        ]
        found_unfair = [kw for kw in unfair_keywords if kw in text_lower]
        if not found_unfair or step_num == 1:
            return {
                "action_type": "flag_unfair",
                "unfair_clause": "Several clauses in this contract appear to be one-sided and may be unenforceable. The contract contains provisions allowing unilateral modifications, excessive liability limitations, and broad indemnification that heavily favors one party.",
                "unfair_reason": "The contract contains multiple problematic clauses including: unlimited liability for one party, waiver of rights, and asymmetric termination terms. These are classic indicators of unconscionable contract terms that may be void under many jurisdictions.",
            }
        return {
            "action_type": "request_clarification",
            "clarification_request": "Continuing review of contract terms.",
        }

    return {
        "action_type": "request_clarification",
        "clarification_request": "Analyzing contract.",
    }


# ── LLM helpers ────────────────────────────────────────────────────────────────
def _strip_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines[-1].strip() == "```":
            raw = "\n".join(lines[1:-1])
        else:
            raw = "\n".join(lines[1:])
    return raw.strip()


def _call_llm(prompt: str) -> str:
    resp = llm_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a contract review agent. Return valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.3,
    )
    return resp.choices[0].message.content or ""


# ── Task-specific prompts ──────────────────────────────────────────────────────
PROMPTS = {
    "easy": (
        "Identify ALL missing critical clauses in this contract.\n"
        "Contract:\n{contract_text}\n"
        "Return ONLY JSON: "
        '{{"action_type": "flag_missing", "missing_clauses": ["termination", "payment", ...]}}\n'
        "Possible clause types: termination, payment, liability, limitation_liability, "
        "indemnification, intellectual_property, confidentiality, governing_law, "
        "dispute_resolution, force_majeure"
    ),
    "medium": (
        "Assess the risk level of the clauses in this contract.\n"
        "Contract:\n{contract_text}\n"
        "Return ONLY JSON: "
        '{{"action_type": "risk_assess", "risk_level": "high", "risk_explanation": "..."}}\n'
        "Risk levels: none, low, medium, high, critical"
    ),
    "hard": (
        "Identify ALL unfair or unconscionable clauses in this contract.\n"
        "Contract:\n{contract_text}\n"
        "Return ONLY JSON: "
        '{{"action_type": "flag_unfair", "unfair_clause": "...", "unfair_reason": "..."}}\n'
        "Be specific about which clause text is unfair and why."
    ),
}

MAX_STEPS = {"easy": 20, "medium": 30, "hard": 50}


def _build_action(task_id: str, llm_response: str) -> Dict[str, Any]:
    """Parse LLM response into an action dict for the API."""
    try:
        data = json.loads(_strip_json(llm_response))
    except Exception:
        return {
            "action_type": "request_clarification",
            "clarification_request": "Unable to parse response.",
        }

    action = {"action_type": data.get("action_type", "request_clarification")}

    if action["action_type"] == "flag_missing":
        action["missing_clauses"] = data.get("missing_clauses", [])
    elif action["action_type"] == "risk_assess":
        action["risk_level"] = data.get("risk_level")
        action["risk_explanation"] = data.get("risk_explanation", "")
    elif action["action_type"] == "flag_unfair":
        action["unfair_clause"] = data.get("unfair_clause", "")
        action["unfair_reason"] = data.get("unfair_reason", "")
    elif action["action_type"] == "request_clarification":
        action["clarification_request"] = data.get(
            "clarification_request", "Need more context."
        )

    return action


# ── Episode runner ─────────────────────────────────────────────────────────────
async def run_episode(task_id: str) -> float:
    episode_id = str(uuid.uuid4())[:8]
    log_start(task_id, episode_id)

    obs = await api_reset(task_id)
    contract_text = obs.get("contract_text", "")
    cumulative_score = 0.0
    max_steps = MAX_STEPS.get(task_id, 20)
    prompt_template = PROMPTS[task_id]

    for step_num in range(1, max_steps + 1):
        prompt = prompt_template.format(contract_text=contract_text)

        try:
            llm_response = await asyncio.to_thread(_call_llm, prompt)
        except Exception as e:
            print(f"LLM error on step {step_num}: {e}", flush=True)
            llm_response = ""
            action = _fallback_action(task_id, contract_text, step_num)
        else:
            action = _build_action(task_id, llm_response)

        result = await api_step(action)

        reward = result.get("reward", 0.0)
        done = result.get("done", False)
        cumulative_score = result.get("observation", {}).get(
            "current_score", cumulative_score
        )

        log_step(step_num, action, round(reward, 4), done)

        if done:
            break

    log_end(task_id, round(cumulative_score, 4))
    return cumulative_score


# ── Main ───────────────────────────────────────────────────────────────────────
async def main():
    start = asyncio.get_event_loop().time()
    results = {}

    for task_id in ["easy", "medium", "hard"]:
        elapsed = asyncio.get_event_loop().time() - start
        if elapsed > TIMEOUT_SECONDS:
            print(f"Timeout reached after {elapsed:.0f}s, stopping.", flush=True)
            break
        try:
            score = await run_episode(task_id)
            results[task_id] = score
        except Exception as e:
            print(f"Task '{task_id}' ERROR: {e}", flush=True)
            results[task_id] = 0.0

    avg = sum(results.values()) / len(results) if results else 0.0
    print(f"\n=== RESULTS ===", flush=True)
    for t, s in results.items():
        print(f"  {t}: {s:.4f}", flush=True)
    print(f"  average: {avg:.4f}", flush=True)

    await _http.aclose()
    return results


if __name__ == "__main__":
    asyncio.run(main())
