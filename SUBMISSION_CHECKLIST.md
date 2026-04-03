# SUBMISSION_CHECKLIST.md — Contract Clause Review

This is a living checklist to verify the environment prior to final submission for the Scaler × Meta × PyTorch OpenEnv Hackathon.

## Official Pre-Submission Checks

| # | Check | Verification Command | Expected Passing Result |
| :--- | :--- | :--- | :--- |
| 1 | HF Space Health | `curl -f https://$HF_USERNAME-contract-clause-env.hf.space/health` | HTTP 200 OK |
| 2 | Reset Endpoint | `curl -s -X POST http://localhost:7860/reset -d '{"task_id":"easy"}'` | Valid JSON with `contract_text` and `available_actions`. |
| 3 | Step Reward | `curl -s -X POST http://localhost:7860/step -d '{"action_type":"SCAN_DOCUMENT"}'` | JSON with `reward` as a float between `0.0` and `1.0`. |
| 4 | State Endpoint | `curl -s http://localhost:7860/state` | JSON with `episode_id`, `step_count`, and `score`. |
| 5 | Manifest Tasks | `grep -c "id:" openenv.yaml` | Output is `3` (easy, medium, hard). |
| 6 | Docker Build | `docker build -t test-build .` | `Successfully built ...` (Exit code 0). |
| 7 | Inference Baseline | `grep "from openai import OpenAI" inference.py` | Must use the OpenAI client. |
| 8 | Env Vars Usage | `grep -E "API_BASE_URL\|MODEL_NAME\|HF_TOKEN" inference.py` | All three variables must be read from `os.environ`. |
| 9 | Runtime Limit | `time python inference.py` | `real` time is less than `20m`. |
| 10 | Grader Ranges | `python -m pytest tests/test_graders.py` | All tests pass ensuring rewards stay in `[0.0, 1.0]`. |
| 11 | Unit Tests | `python -m pytest tests/ -v` | `100% passed`. |
| 12 | README Quality | `ls -l README.md` | File exists and contains all required sections. |
| 13 | Repo Visibility | Check GitHub settings. | Repository must be set to **Public**. |
| 14 | Submission Role | Communicate with team. | Ensure **only the team lead** hits the submit button. |
| 15 | Deadline Check | Check local time. | Submission must be before **8 Apr 2026 11:59 PM IST**. |
| 16 | Action Spec | `grep "action_space:" openenv.yaml -A 5` | Detailed action space description in manifest. |
| 17 | Obs Spec | `grep "observation_space:" openenv.yaml -A 5` | Detailed observation space description in manifest. |

## How to Submit

1.  **Final Push**: Ensure all code is on the `main` branch and CI is **Green**.
2.  **Verify Space**: Visit the Hugging Face Space URL and ensure it is "Running".
3.  **Run Inference**: Run `python inference.py` locally and record the final average score.
4.  **Dashboard**: Team lead logs into the Scaler/Meta Hackathon dashboard.
5.  **Form**:
    *   Enter the GitHub Repository URL.
    *   Enter the Hugging Face Space URL.
    *   Paste the output of the final `inference.py` run.
6.  **Submit**: Click "Submit Project".

## If something is broken at the last minute

**Triage Order (Fix first, skip last):**

1.  **CRITICAL (Fix Immediately)**:
    *   Docker build failure (environment won't run).
    *   `/health` or `/reset` returning 500 errors.
    *   `inference.py` crashing or taking >20 minutes.
2.  **HIGH (Fix if time permits)**:
    *   Reward scores outside `[0.0, 1.0]`.
    *   Manifest (`openenv.yaml`) missing fields.
3.  **LOW (Skip if necessary)**:
    *   Minor README typos.
    *   Extra files in the repo (as long as it builds).
    *   Non-breaking unit test failures (if the environment logic is sound).
