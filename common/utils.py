"""Shared scoring utilities ensuring rewards are strictly within (0, 1)."""

SAFE_MIN = 0.05
SAFE_MAX = 0.95
SAFE_DEFAULT = SAFE_MIN


def safe_score(score: float) -> float:
    """Clamp any numeric score to the safe (0, 1) openenv range."""
    try:
        val = float(score)
    except (TypeError, ValueError):
        val = SAFE_DEFAULT
    if val <= 0.0:
        return SAFE_MIN
    if val >= 1.0:
        return SAFE_MAX
    return round(max(SAFE_MIN, min(SAFE_MAX, val)), 4)


def safe_score_observation(score: float) -> float:
    result = safe_score(score)
    assert 0.0 < result < 1.0, f"safe_score_observation: invalid {result}"
    return result


def safe_score_reward(score: float) -> float:
    result = safe_score(score)
    assert 0.0 < result < 1.0, f"safe_score_reward: invalid {result}"
    return result
