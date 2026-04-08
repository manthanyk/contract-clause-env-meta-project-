import pytest

from server.environment import MyEnvironment
from models import ActionType, ContractClauseAction, RiskLevel


def _assert_bounds(val: float):
    assert 0.05 <= val <= 0.95
    assert val not in (0.0, 1.0)


@pytest.mark.asyncio
async def test_reset_scores_in_range():
    env = MyEnvironment()
    for task_id in ["easy", "medium", "hard"]:
        obs = await env.reset(task_id)
        _assert_bounds(obs.current_score)


@pytest.mark.asyncio
async def test_step_scores_in_range():
    env = MyEnvironment()
    actions = {
        "easy": ContractClauseAction(action_type=ActionType.REQUEST_CLARIFICATION),
        "medium": ContractClauseAction(
            action_type=ActionType.RISK_ASSESS,
            risk_level=RiskLevel.HIGH,
            risk_explanation="unfair",
        ),
        "hard": ContractClauseAction(
            action_type=ActionType.FLAG_UNFAIR,
            unfair_clause="unfair",
            unfair_reason="unfair",
        ),
    }
    for task_id, action in actions.items():
        await env.reset(task_id)
        result = await env.step(action)
        _assert_bounds(result.reward)
        _assert_bounds(result.observation.current_score)
