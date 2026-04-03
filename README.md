---
title: Contract Clause Review Environment
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# ⚖️ Contract Clause Review Environment

An OpenEnv-compatible reinforcement learning environment for contract clause analyses, built for the Meta PyTorch Hackathon.

## 🎯 Overview

This environment challenges AI agents to review legal contract clauses across three difficulty levels:
- **Easy**: Identify and classify contract clause types
- **Medium**: Rate risk levels of contract clauses  
- **Hard**: Detect unfair or ambiguous terms in contracts

## 🏗️ Architecture

```
openenv_hackathon_project/
├── models.py          # Data models (ClauseType, RiskLevel, Action)
├── openenv.yaml       # OpenEnv configuration
├── inference.py       # AI agent using OpenAI
├── client.py          # Environment client
├── Dockerfile         # Docker deployment
├── server/
│   ├── app.py         # FastAPI server
│   ├── environment.py # Environment logic
│   └── requirements.txt
└── tasks/
    ├── easy.py        # Clause classification
    ├── medium.py      # Risk rating
    └── hard.py        # Unfair term detection
```

## 🚀 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /health  | GET    | Health check |
| /reset   | POST   | Start new episode |
| /step    | POST   | Submit action |
| /state   | GET    | Get current state |

## 🔧 Quick Start

### Run Locally
```bash
# Install dependencies
pip install -r server/requirements.txt

# Start server
uvicorn server.app:app --host 0.0.0.0 --port 7860

# Test health
curl http://localhost:7860/health
```

### Run with Docker
```bash
docker build -t contract-clause-env .
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key contract-clause-env
```

## 📊 Grading

Each task returns a reward between 0.0 and 1.0:

| Task | Full Credit | Partial Credit |
|------|-------------|----------------|
| Easy | Correct clause type + all fields | Correct type only |
| Medium | Correct risk level + explanation | Correct level only |
| Hard | All unfair terms found + explained | Some terms found |

## 🧪 Tests

```bash
python -m pytest tests/ -v
# 39/39 tests passing ✅
```

## 🌐 Environment Variables

```
OPENAI_API_KEY=your_openai_api_key
HF_TOKEN=your_huggingface_token
```

## 📋 OpenEnv Config

```yaml
name: contract_clause_review
version: 1.0.0
domain: legal
difficulty_levels: [easy, medium, hard]
reward_range: [0.0, 1.0]
```

## 🏆 Hackathon

Built for the **Scaler × Meta PyTorch Hackathon**
- Domain: Contract Clause Review
- Team: ManthanYk
- Deadline: April 8, 2025

---
Made with ❤️ for the Meta PyTorch Hackathon
