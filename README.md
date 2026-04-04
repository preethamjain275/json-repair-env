---
title: JSON Repair Environment
emoji: 🔧
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# JSON Repair Environment 🔧

An OpenEnv reinforcement learning environment where an AI agent learns to repair 
malformed JSON outputs — a critical real-world problem in LLM pipelines.

## Why This Matters
LLMs frequently produce broken JSON: trailing commas, wrong types, unquoted keys,
missing fields. This environment trains agents to automatically fix these failures.

## Action Space
| Field | Type | Description |
|-------|------|-------------|
| repaired_json | string | Agent's repaired JSON string |
| explanation | string | Optional: brief description of changes |

## Observation Space
| Field | Type | Description |
|-------|------|-------------|
| broken_json | string | The malformed JSON to fix |
| target_schema | object | JSON Schema the output must comply with |
| hint | string | Hint about what's broken |
| task_name | string | Current task identifier |
| step_number | int | Current step in episode |

## Tasks
| Task | Difficulty | Description |
|------|------------|-------------|
| easy_syntax_fix | Easy | Fix trailing comma |
| medium_type_repair | Medium | Fix types + add missing field |
| hard_nested_reconstruction | Hard | Reconstruct corrupted nested JSON |

## Reward Function
- Valid JSON syntax: **+0.40**
- Schema compliance: **+0.40**  
- Exact semantic match: **+0.20**

## Setup
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

## Run Baseline
```bash
export ENV_URL=http://localhost:7860
export API_BASE_URL=https://api-inference.huggingface.co/v1
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
export HF_TOKEN=hf_your_token
python inference.py
```

## Baseline Scores
| Task | Score |
|------|-------|
| easy_syntax_fix | ~0.95 |
| medium_type_repair | ~0.75 |
| hard_nested_reconstruction | ~0.55 |

## Validate
```bash
pip install openenv-core
openenv validate .
```
