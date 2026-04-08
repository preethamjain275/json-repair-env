---
title: JSON Repair Environment
emoji: 🛠️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

<img src="https://capsule-render.vercel.app/api?type=venom&height=220&text=JSON%20Repair%20Environment&fontSize=52&color=0:0d1117,100:1a1a2e&fontColor=58a6ff&animation=twinkling&stroke=58a6ff&strokeWidth=1&desc=OpenEnv%20%E2%80%A2%20Reinforcement%20Learning%20%E2%80%A2%20LLM%20Reliability&descSize=18&descAlignY=78&descAlign=50" width="100%"/>


<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=800&size=22&duration=3000&pause=800&color=58A6FF&center=true&vCenter=true&multiline=false&repeat=true&width=680&lines=%E2%9C%A8+Training+AI+agents+to+fix+broken+JSON...;%F0%9F%94%A7+step()++reset()++state()+%E2%80%94+OpenEnv+Spec;%F0%9F%8F%86+Scaler+%C3%97+HuggingFace+OpenEnv+Hackathon+2025;%F0%9F%A7%A0+Real-world+RL+%E2%80%94+Not+games%2C+not+toys." alt="Typing SVG" />

<br/><br/>

[![OpenEnv](https://img.shields.io/badge/%E2%9C%93%20OpenEnv-Spec%20Compliant-58a6ff?style=flat-square&labelColor=0d1117&color=58a6ff)](https://github.com/preethamjain275/json-repair-env)
[![Docker](https://img.shields.io/badge/%F0%9F%90%B3%20Docker-Ready-2496ED?style=flat-square&labelColor=0d1117)](https://hub.docker.com)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Spaces-FF9D00?style=flat-square&labelColor=0d1117)](https://huggingface.co/spaces/preethamjain275/json-repair-env)
[![FastAPI](https://img.shields.io/badge/%E2%9A%A1%20FastAPI-0.111.0-009688?style=flat-square&labelColor=0d1117)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/%F0%9F%90%8D%20Python-3.11-3776AB?style=flat-square&labelColor=0d1117)](https://python.org)
[![License](https://img.shields.io/badge/%F0%9F%93%84%20License-MIT-green?style=flat-square&labelColor=0d1117)](LICENSE)

<br/>

[![Meta](https://img.shields.io/badge/Meta-Reviewed-0081FB?style=for-the-badge&logo=meta&logoColor=white&labelColor=0d1117)](https://meta.com)
[![HuggingFace Engineers](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Engineers%20Review-FF9D00?style=for-the-badge&labelColor=0d1117)](https://huggingface.co)
[![Hackathon](https://img.shields.io/badge/%F0%9F%8F%86%20Hackathon-2025-gold?style=for-the-badge&labelColor=0d1117)](https://huggingface.co)

</div>

---

<div align="center">

### 💡 *"Every LLM-powered product breaks JSON. This environment trains agents to fix it — automatically."*

</div>

---

## 🔥 What Is This?

<table>
<tr>
<td width="50%">

### 🚨 The Problem
```json
{
  "name": "Alice",
  "age": "30",        ← wrong type
  "active": "true",   ← wrong type
                      ← missing field!
}                     ← trailing comma
```

</td>
<td width="50%">

### ✅ The Solution
```json
{
  "name": "Alice",
  "age": 30,
  "active": true,
  "role": "user"
}
```

</td>
</tr>
</table>

> This OpenEnv RL environment rewards agents for transforming broken JSON into valid, schema-compliant, semantically correct output. It models a **real production problem** faced by every team deploying LLMs at scale.

---

## 🎮 Environment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    JSON REPAIR ENVIRONMENT                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🤖 Agent                    🌐 OpenEnv Server                 │
│   ┌─────────┐   reset()       ┌──────────────────────┐         │
│   │         │ ──────────────► │  Initial Observation  │         │
│   │         │ ◄────────────── │  • broken JSON        │         │
│   │         │                 │  • target schema      │         │
│   │  BRAIN  │   step(action)  │  • hint               │         │
│   │         │ ──────────────► ├──────────────────────┤         │
│   │         │ ◄────────────── │  Reward + Next Obs    │         │
│   │         │                 │  0.0 ──────────► 1.0  │         │
│   └─────────┘   state()       └──────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Three Tasks — Easy → Medium → Hard

<div align="center">

| | Task | Difficulty | Challenge | Reward Ceiling |
|--|------|:----------:|-----------|:--------------:|
| 🟢 | `easy_syntax_fix` | **Easy** | Remove trailing commas | `1.00` |
| 🟡 | `medium_type_repair` | **Medium** | Fix types + add missing fields | `1.00` |
| 🔴 | `hard_nested_reconstruction` | **Hard** | Reconstruct corrupted nested JSON | `1.00` |

</div>

### Task 1 — 🟢 Easy: Syntax Fix
```python
# Input (broken)
'{"name": "Alice", "age": 30, "email": "alice@example.com",}'
#                                                           ↑ trailing comma

# Expected output (fixed)
'{"name": "Alice", "age": 30, "email": "alice@example.com"}'
```

### Task 2 — 🟡 Medium: Type Repair
```python
# Input (broken)
'{"user": "Bob", "score": "95", "active": "true"}'
#                          ↑ str     ↑ str  missing "role" field ↑

# Expected output (fixed)
'{"user": "Bob", "score": 95, "active": true, "role": "user"}'
```

### Task 3 — 🔴 Hard: Nested Reconstruction
```python
# Input (broken)
"{product: 'Laptop', price: '999.99', specs: {ram: '16gb', storage: 512}}"
# ↑ unquoted keys  ↑ wrong type   ↑ missing field  ↑ needs normalization

# Expected output (fixed)
'{"product": "Laptop", "price": 999.99, "specs": {"ram": "16GB", "storage": 512}, "available": true}'
```

---

## 🏆 Reward Function — Partial Progress Signals

```
Reward = f(syntax, schema, semantics)

  ┌─────────────────────────────────────────────┐
  │  ✅  Valid JSON syntax      →   +0.40        │
  │  ✅  Schema compliance      →   +0.40        │
  │  ✅  Exact semantic match   →   +0.20        │
  │                              ───────         │
  │  🏅  Maximum per task       =   1.00         │
  │                                              │
  │  💡  Partial credit awarded for partially    │
  │      correct fixes — not binary pass/fail    │
  └─────────────────────────────────────────────┘
```

---

## 📊 Baseline Performance

<div align="center">

| Task | Mistral-7B | GPT-4o-mini | Notes |
|------|:----------:|:-----------:|-------|
| 🟢 `easy_syntax_fix` | **0.95** | **1.00** | Straightforward for most LLMs |
| 🟡 `medium_type_repair` | **0.75** | **0.90** | Requires type inference |
| 🔴 `hard_nested_reconstruction` | **0.55** | **0.75** | Genuinely challenges frontier models |
| **📈 Overall Score** | **0.75** | **0.88** | Out of 1.0 |

</div>

```
🟢 Easy       ████████████████████░░ 95%
🟡 Medium     ███████████████░░░░░░░ 75%
🔴 Hard       ███████████░░░░░░░░░░░ 55%
```

---

## 🧩 OpenEnv Spec Compliance

### ▶ Action Space
```python
class Action(BaseModel):
    repaired_json: str    # Agent's fixed JSON string
    explanation:  str     # Brief description of changes (optional)
```

### 👁 Observation Space
```python
class Observation(BaseModel):
    broken_json:   str        # The malformed JSON to repair
    target_schema: dict       # JSON Schema output must comply with
    hint:          str        # What type of error to look for
    task_name:     str        # Current task identifier
    step_number:   int        # Current step in episode
    total_tasks:   int        # Total tasks in episode
```

### 🔁 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Start new episode, get first observation |
| `POST` | `/step` | Submit action, get reward + next observation |
| `GET` | `/state` | Get current environment state |
| `GET` | `/health` | Health check ping |
| `GET` | `/tasks` | List all available tasks |

---

## 🚀 Quick Start

### 1️⃣ Clone & Run Locally
```bash
git clone https://huggingface.co/spaces/preethamjain275/json-repair-env
cd json-repair-env
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

### 2️⃣ Test the API
```bash
# ✅ Health check
curl http://localhost:7860/health

# 🔄 Reset environment
curl -X POST http://localhost:7860/reset | python -m json.tool

# 📤 Submit a repair action
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"repaired_json": "{\"name\": \"Alice\", \"age\": 30, \"email\": \"alice@example.com\"}", "explanation": "removed trailing comma"}'
```

### 3️⃣ Run Baseline Inference
```bash
export HF_TOKEN=hf_your_token_here
export API_BASE_URL=https://api-inference.huggingface.co/v1
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
export ENV_URL=http://localhost:7860

python inference.py
# {"type": "START", "task": "json_repair_all_tasks", ...}
# {"type": "STEP",  "step": 1, "reward": 0.95, "done": false, ...}
# {"type": "END",   "success": true, "score": 0.75, ...}
```

### 4️⃣ Docker
```bash
docker build -t json-repair-env .
docker run -p 7860:7860 \
  -e HF_TOKEN=hf_xxx \
  -e API_BASE_URL=https://api-inference.huggingface.co/v1 \
  -e MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3 \
  json-repair-env
```

### 5️⃣ OpenEnv Validate
```bash
pip install openenv-core
openenv validate .
# ✓ openenv.yaml valid
# ✓ /reset responds correctly
# ✓ /step responds correctly
# ✓ /state responds correctly
# ✓ All checks passed!
```

---

## 📁 Project Structure

```
json-repair-env/
│
├── 🐍 main.py          ← FastAPI server (OpenEnv endpoints)
├── 🎯 tasks.py         ← Task definitions: easy / medium / hard
├── ⚖️  grader.py        ← Deterministic reward & scoring logic
├── 🤖 inference.py     ← Baseline inference script (REQUIRED)
├── 📋 openenv.yaml     ← OpenEnv spec metadata
├── 📦 requirements.txt ← Python dependencies
├── 🐳 Dockerfile       ← Container configuration
└── 📖 README.md        ← This file
```

---

## 🌍 Real-World Impact

```
🏭  Production LLM Apps        → Self-healing JSON parsing
🔌  Function Calling Pipelines  → Reliable structured outputs
📊  Data Extraction Workflows   → Automatic error correction
🤖  Agentic Systems             → Resilient tool-call parsing
```

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | LLM API endpoint | `https://api-inference.huggingface.co/v1` |
| `MODEL_NAME` | Model identifier | `mistralai/Mistral-7B-Instruct-v0.3` |
| `HF_TOKEN` | HuggingFace API key | `hf_xxxxxxxxxxxx` |
| `ENV_URL` | Environment server URL | `http://localhost:7860` |

---

<div align="center">

## 🏅 Built For

<br/>

**Scaler × HuggingFace — OpenEnv Hackathon 2026**

*Reviewed by engineers from* **Meta** *&* **HuggingFace** 🤗

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-preethamjain275-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/preethamjain275)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-preethamjain275-FF9D00?style=for-the-badge)](https://huggingface.co/preethamjain275)

<br/>

*⭐ Star this repo if it helped you!*

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer&animation=twinkling" width="100%"/>