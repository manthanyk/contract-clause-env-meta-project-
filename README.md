# Contract Clause Review: An OpenEnv RL Environment for AI Legal Review Agents

## Environment Overview

Contract Clause Review is a specialized RL environment designed to train and evaluate AI agents in the domain of legal document analysis. The environment simulates the workflow of a legal professional tasked with identifying missing essential clauses, assessing risk levels in existing terms, and detecting unfair contractual conditions. Agents must navigate through contract texts, flag deficiencies, and provide structured legal assessments to maximize their performance score.

## Task Table

| Task ID | Difficulty | Max Steps | Success Threshold | Description |
| :--- | :--- | :--- | :--- | :--- |
| **easy** | Easy | 20 | 0.8 | **Missing Clause Detection**: Identify essential legal clauses (e.g., Termination, Liability) that are absent from the document. |
| **medium** | Medium | 30 | 0.7 | **Risk Rating**: Review specific clauses and assign accurate risk ratings (Low, Medium, High) based on legal standard benchmarks. |
| **hard** | Hard | 50 | 0.6 | **Unfair Term Detection**: Analyze complex legal prose to identify and flag terms that are considered unfair or unenforceable under consumer protection laws. |

## Action Space Table

| Action Type | Fields | Description |
| :--- | :--- | :--- |
| `SCAN_DOCUMENT` | `None` | Moves the agent's focus to the next logical section or clause of the contract. |
| `FLAG_MISSING` | `missing_clauses: List[ClauseType]` | Flags specific essential clauses that have been identified as missing from the document. |
| `RATE_RISK` | `clause_id: str, risk_level: RiskLevel` | Assigns a risk assessment (Low, Medium, High) to a specific identified clause. |
| `IDENTIFY_UNFAIR` | `text_snippet: str, reason: str` | Flags a specific portion of text as an unfair term with a provided justification. |
| `FINALIZE` | `None` | Submits the current assessment for final grading and ends the episode. |

## Observation Space Table

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `contract_text` | `str` | The full or partial text of the contract currently being reviewed. |
| `current_clause_id` | `str` | The unique identifier of the clause currently under focus. |
| `available_actions` | `List[str]` | A list of valid action types that can be performed in the current state. |
| `review_summary` | `Dict[str, Any]` | Information about clauses flagged or rated so far in the current episode. |
| `progress_hint` | `str \| None` | A context-aware hint to guide the agent towards successful task completion. |

## Reward Design

The environment utilizes a **partial credit system** with rewards mapped in the range `[0.0, 1.0]`. Rewards are typically granted in `0.25` increments based on incremental progress:

- **0.25**: Accurate identification of a single missing clause or correct risk rating for a minor term.
- **0.50**: Significant progress, such as identifying 50% of the target issues in the document.
- **0.75**: Near-complete assessment with only minor discrepancies in justification or rating accuracy.
- **1.00**: Perfect identification and assessment of all target legal issues within the step limit.

## Setup — Local

1.  **Install dependencies**:
    ```bash
    pip install -r server/requirements.txt
    ```
2.  **Set up environment variables**:
    Create a `.env` file with the following:
    ```bash
    API_BASE_URL=https://api.openai.com/v1
    MODEL_NAME=gpt-4o-mini
    HF_TOKEN=your_huggingface_token
    ```
3.  **Start the environment server**:
    ```bash
    uvicorn server.app:app --host 0.0.0.0 --port 7860
    ```
4.  **Test endpoints**:
    ```bash
    curl http://localhost:7860/health
    ```
5.  **Run baseline inference**:
    ```bash
    python inference.py
    ```

## Setup — Docker

1.  **Build the image**:
    ```bash
    docker build -t contract-clause-env .
    ```
2.  **Run the container**:
    ```bash
    docker run -p 7860:7860 \
      -e API_BASE_URL=https://api.openai.com/v1 \
      -e MODEL_NAME=gpt-4o-mini \
      -e HF_TOKEN=your_token \
      contract-clause-env
    ```

## API Endpoint Reference

- **Health Check**:
  `curl -f http://localhost:7860/health`
- **Reset Environment**:
  `curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task_id": "easy"}'`
- **Step Action**:
  `curl -X POST http://localhost:7860/step -H "Content-Type: application/json" -d '{"action_type": "SCAN_DOCUMENT", "parameters": {}}'`
- **Get State**:
  `curl http://localhost:7860/state`

## Environment Variables Table

| Variable | Description | Default |
| :--- | :--- | :--- |
| `API_BASE_URL` | Base URL for the LLM provider (OpenAI compatible). | `https://api.openai.com/v1` |
| `MODEL_NAME` | The name of the model to use for inference. | `gpt-4o-mini` |
| `HF_TOKEN` | Hugging Face API token for deployment/authentication. | `None` |
| `HF_SPACE_URL` | URL of the hosted HF Space (for remote inference). | `http://localhost:7860` |

## File Structure

```text
├── openenv.yaml          # Environment manifest (REQUIRED)
├── inference.py          # Baseline evaluation script (REQUIRED)
├── Dockerfile            # Container configuration (REQUIRED)
├── README.md             # Project documentation (REQUIRED)
├── models.py             # Pydantic data models for actions/observations
├── client.py             # Environment client for interaction
├── server/
│   ├── app.py            # FastAPI application entry point
│   ├── environment.py    # Core RL environment logic
│   └── requirements.txt  # Python dependencies for the server
└── tasks/
    ├── easy.py           # Missing clause detection grader
    ├── medium.py         # Risk rating assessment grader
    └── hard.py           # Unfair term detection grader
```

## Pre-submission Checklist

1. [ ] HF Space returns 200 on `/health`
2. [ ] `POST /reset` returns valid JSON observation
3. [ ] `POST /step` returns reward in `[0.0, 1.0]`
4. [ ] `GET /state` returns valid state
5. [ ] `openenv.yaml` has all 3 tasks
6. [ ] `Dockerfile` builds without errors
7. [ ] `inference.py` in root, uses OpenAI client
8. [ ] All 3 env vars read from `os.environ`
9. [ ] `inference.py` completes in < 20 minutes
10. [ ] All grader scores in `[0.0, 1.0]`
11. [ ] All pytest tests pass
12. [ ] README complete with all sections
13. [ ] GitHub repo is public
14. [ ] Only team lead submits
15. [ ] Submitted before 8 Apr 2026 11:59 PM IST
16. [ ] Action space is documented in `openenv.yaml`
17. [ ] Observation space is documented in `openenv.yaml`