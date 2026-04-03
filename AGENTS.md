# AGENTS.md — Contract Clause Review Environment

## Project
Scaler × Meta × PyTorch OpenEnv Hackathon | Deadline: 8 April 2026, 11:59 PM IST
Domain: Contract Clause Review RL Environment

## Environment
name: contract-clause-env
tasks: easy (missing clause detection) | medium (risk rating) | hard (unfair term detection)
port: 7860
stack: Python 3.11, FastAPI, Pydantic v2, Docker, HF Spaces

## File ownership
- models.py, openenv.yaml, server/ → Claude Code
- tasks/, tests/ → Open Code
- inference.py, client.py, Dockerfile → Codex
- README.md, AGENTS.md, .github/ → Antigravity

## Rules (never violate)
1. Rewards always float in [0.0, 1.0] — never binary
2. inference.py in root, uses OpenAI client
3. Dockerfile exposes 7860, python:3.11-slim base
4. No openenv.core imports — package doesn't exist
5. All secrets from os.environ / .env — never hardcoded

## Slash commands
/validate → run the 17-item pre-submission check
/deploy → push to HF Spaces and verify /health returns 200
/test → run pytest tests/ -v
/status → show current step, score, deadline countdown

## Pre-submission checklist
[ ] HF Space returns 200 on /health
[ ] POST /reset returns valid JSON observation
[ ] POST /step returns reward in [0.0, 1.0]
[ ] GET /state returns valid state
[ ] openenv.yaml has all 3 tasks
[ ] Dockerfile builds without errors
[ ] inference.py in root, uses OpenAI client
[ ] All 3 env vars read from os.environ
[ ] inference.py completes < 20 minutes
[ ] All grader scores in [0.0, 1.0]
[ ] All pytest tests pass
[ ] README complete with all sections
[ ] GitHub repo is public
[ ] Only team lead submits
[ ] Submitted before 8 Apr 2026 11:59 PM IST
