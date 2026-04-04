"""
Baseline inference script for JSON Repair Environment.
Uses OpenAI-compatible client to run a model against the environment.

Usage:
    ENV_URL=https://your-space.hf.space \
    API_BASE_URL=https://api-inference.huggingface.co/v1 \
    MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3 \
    HF_TOKEN=hf_xxx \
    python inference.py
"""

import asyncio
import json
import os
import sys
from typing import List

import httpx
from openai import OpenAI

# --- Configuration ---
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
ENV_URL      = os.environ.get("ENV_URL", "http://localhost:7860")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", HF_TOKEN)

TASK_NAME = "json_repair_all_tasks"
BENCHMARK = "json-repair-env"
MAX_STEPS  = 3
MAX_TOTAL_REWARD = 3.0
SUCCESS_SCORE_THRESHOLD = 0.7


# --- Logging (MUST follow [START] [STEP] [END] format exactly) ---

def log_start(task: str, env: str, model: str):
    print(json.dumps({"type": "START", "task": task, "env": env, "model": model}), flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error):
    print(json.dumps({
        "type": "STEP",
        "step": step,
        "action": action,
        "reward": reward,
        "done": done,
        "error": error
    }), flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    print(json.dumps({
        "type": "END",
        "success": success,
        "steps": steps,
        "score": score,
        "rewards": rewards
    }), flush=True)


# --- Simple HTTP client wrapping the environment ---

class EnvClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.http = httpx.AsyncClient(timeout=60.0)
        self.last_result = None

    async def reset(self):
        resp = await self.http.post(f"{self.base_url}/reset")
        resp.raise_for_status()
        self.last_result = resp.json()
        return self

    async def step(self, repaired_json: str, explanation: str = ""):
        payload = {"repaired_json": repaired_json, "explanation": explanation}
        resp = await self.http.post(f"{self.base_url}/step", json=payload)
        resp.raise_for_status()
        self.last_result = resp.json()
        return self

    async def close(self):
        await self.http.aclose()

    @property
    def observation(self):
        return self.last_result.get("observation", {})

    @property
    def reward(self):
        return float(self.last_result.get("reward", 0.0))

    @property
    def done(self):
        return bool(self.last_result.get("done", False))


# --- LLM call ---

def get_model_repair(client: OpenAI, broken_json: str, hint: str, history: List[str]) -> str:
    history_text = "\n".join(history[-3:]) if history else "No previous steps."
    prompt = f"""You are a JSON repair expert. Your task is to fix the broken JSON below.

BROKEN JSON:
{broken_json}

HINT: {hint}

RECENT HISTORY:
{history_text}

Rules:
- Output ONLY the repaired JSON string, nothing else
- No markdown, no explanation, no code blocks
- Ensure it is valid JSON
- Fix all syntax errors, type errors, and add any clearly missing fields

Repaired JSON:"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1
    )
    return response.choices[0].message.content.strip()


# --- Main ---

async def main():
    client = OpenAI(api_key=OPENAI_API_KEY or HF_TOKEN, base_url=API_BASE_URL)
    env = EnvClient(ENV_URL)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset()
        obs = result.observation
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            broken = obs.get("broken_json", "")
            hint   = obs.get("hint", "")
            task_name = obs.get("task_name", f"task_{step}")

            action = get_model_repair(client, broken, hint, history)
            result = await env.step(repaired_json=action, explanation="")

            obs     = result.observation
            reward  = result.reward
            done    = result.done
            error   = None

            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(step=step, action=action[:200], reward=reward, done=done, error=error)
            history.append(f"Step {step} [{task_name}]: reward={reward:.2f}")

            if done:
                break

        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = round(min(max(score, 0.0), 1.0), 4)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        error = str(e)
    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
