# Project Guidelines

## Project Structure

```
/Users/manthan/Desktop/meta_hackathon_project/openenv_hackathon_project/
├── tasks/              # Task implementations (easy.py, medium.py, hard.py)
├── models.py           # Pydantic models, enums (ActionType, ClauseType, RiskLevel)
├── server/             # FastAPI application
│   ├── app.py         # API endpoints
│   └── environment.py # Episode state and task routing
├── tests/              # Test suite
│   └── test_graders.py
├── inference.py       # Inference example
├── client.py          # Client wrapper
├── openenv.yaml       # OpenEnv specification
└── requirements.txt   # Dependencies
```

## Build, Test, and Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server
```bash
# Main contract-clause API (port 7860)
uvicorn server.app:app --reload --port 7860
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_graders.py

# Run a specific test class
pytest tests/test_graders.py::TestRewardRangeInvariant -v

# Run a specific test function
pytest tests/test_graders.py::TestRewardRangeInvariant::test_easy_reward_in_range_correct_clauses -v

# Run with verbose output
pytest tests/test_graders.py -v -s
```

### Linting
```bash
# If ruff is available
ruff check .

# If flake8 is available
flake8 .
```

### Type Checking
```bash
# If mypy is available
mypy tasks/ models/
```

## Code Style Guidelines

### Python Version and Formatting
- Python 3.10+ required
- 4-space indentation (no tabs)
- Maximum line length: 100 characters
- Use Black formatting if available

### Type Hints
- **All function signatures must include type hints**
- Use `typing` module for complex types (Tuple, List, Dict, Optional)
- Return types required for all functions
- Example:
```python
async def step(self, action: ContractClauseAction) -> Tuple[ContractClauseObservation, float, bool]:
```

### Imports
- Group imports in order: standard library, third-party, local project
- Use absolute imports (e.g., `from models import ...`)
- Avoid wildcard imports (`from x import *`)
- Example:
```python
from typing import Tuple, List, Dict, Any
from models import ContractClauseAction, ActionType
from tasks.base import BaseTask
```

### Naming Conventions
- Classes: `PascalCase` (e.g., `EasyTask`, `ContractClauseAction`)
- Functions/methods: `snake_case` (e.g., `_grade()`, `reset()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `EASY_CONTRACTS`)
- Private methods: prefix with `_` (e.g., `_apply_action()`)
- Variables: `snake_case` (e.g., `found_clauses`, `current_score`)

### Async Code
- All task methods must be `async def`
- Use `await` for all async operations
- Never block in async code
- Example:
```python
async def reset(self) -> ContractClauseObservation:
    self.step_count = 0
    return ContractClauseObservation(...)
```

### Error Handling
- Use Pydantic models for validation (don't manually validate in code)
- Return appropriate reward scores for edge cases (0.0 for invalid actions)
- Never raise unhandled exceptions in task logic
- Handle `None` values gracefully

### Task Implementation Pattern
Follow this template for new tasks:
```python
class NewTask(BaseTask):
    def __init__(self):
        super().__init__(max_steps=20, difficulty="easy")

    async def reset(self) -> ContractClauseObservation:
        # Initialize state
        return ContractClauseObservation(...)

    async def step(self, action: ContractClauseAction):
        return await super().step(action)

    def _apply_action(self, action: ContractClauseAction) -> dict:
        # Update internal state based on action
        return self.current_state

    def _grade(self, action: ContractClauseAction) -> float:
        # Calculate reward (MUST be in (0.0, 1.0) not [0.0, 1.0])
        score = ...
        return max(0.05, min(0.95, score))
```

### Reward Clamping (Critical)
- **Scores must be strictly between 0 and 1** (not inclusive)
- Use `_clamp()` helper to ensure compliance:
```python
def _clamp(self, score: float) -> float:
    """Ensure score is strictly between 0 and 1 as required by judges."""
    return max(0.05, min(0.95, score))
```
- Never return exactly `0.0` or `1.0` — use `0.05` and `0.95` instead

### Documentation
- Docstrings for all public classes and methods
- Type hints serve as primary parameter documentation
- Keep docstrings concise (1-3 sentences)

### Testing New Code
- Add test cases in `tests/test_graders.py`
- Test both success and failure paths
- Test edge cases (empty inputs, wrong action types)
- Ensure all tests pass before committing

## Important Notes

### OpenEnv Compatibility
- Tasks must implement `reset()` and `step()` methods
- Observations must follow the schema in `openenv.yaml`
- Actions must be parsed from API requests
- Scores must be in range (0.05, 0.95) — never 0.0 or 1.0

### Model Extensions
- When adding new actions, extend `ActionType` enum in `models.py`
- When adding new clauses, extend `ClauseType` enum
- Update all task graders to handle new action types

### Server Endpoints
- `POST /reset` - Initialize new episode
- `POST /step` - Execute action and get reward
- `GET /state` - Get current episode state
- `GET /health` - Health check