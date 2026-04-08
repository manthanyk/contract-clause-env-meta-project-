def safe_score(x: float) -> float:
    """Clamp scores to the strict (0, 1) openenv-safe range."""
    try:
        val = float(x)
    except (TypeError, ValueError):
        val = 0.05
    return round(max(0.05, min(0.95, val)), 4)
