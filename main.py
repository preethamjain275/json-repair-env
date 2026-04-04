from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid

from tasks import TASKS
from grader import grade_repair

app = FastAPI(
    title="JSON Repair Environment",
    description="OpenEnv environment for training agents to repair malformed JSON",
    version="1.0.0"
)

# --- Pydantic Models ---

class Action(BaseModel):
    repaired_json: str
    explanation: Optional[str] = ""

class Observation(BaseModel):
    broken_json: str
    target_schema: Dict[str, Any]
    hint: str
    task_name: str
    step_number: int
    total_tasks: int

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

class ResetResult(BaseModel):
    observation: Observation
    done: bool
    reward: float

# --- In-memory State ---
state: Dict[str, Any] = {
    "session_id": "",
    "task_index": 0,
    "step": 0,
    "total_reward": 0.0,
    "done": False,
    "history": []
}


def build_observation() -> Observation:
    task = TASKS[state["task_index"]]
    return Observation(
        broken_json=task["broken_json"],
        target_schema=task["schema"],
        hint=task["hint"],
        task_name=task["name"],
        step_number=state["step"],
        total_tasks=len(TASKS)
    )


# --- Endpoints ---

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root():
    task_rows = ""
    for task in TASKS:
        task_rows += f"""
        <div class="task-card">
            <div class="task-header">
                <span class="task-name">{task['name']}</span>
                <span class="difficulty {task['difficulty']}">{task['difficulty'].upper()}</span>
            </div>
            <p class="description">{task['description']}</p>
            <div class="code-block">
                <strong>Broken JSON:</strong>
                <pre><code>{task['broken_json']}</code></pre>
            </div>
            <div class="hint"><strong>Hint:</strong> {task['hint']}</div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JSON Repair OpenEnv Dashboard</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0a0b10;
                --card-bg: #151720;
                --accent: #6366f1;
                --text: #e2e8f0;
                --text-dim: #94a3b8;
                --easy: #10b981;
                --medium: #f59e0b;
                --hard: #ef4444;
            }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                line-height: 1.6;
                padding: 2rem;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            header {{ margin-bottom: 3rem; text-align: center; }}
            h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .subtitle {{ color: var(--text-dim); font-size: 1.1rem; }}
            
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; }}
            .stat-card {{ background: var(--card-bg); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); text-align: center; }}
            .stat-val {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); display: block; }}
            .stat-label {{ color: var(--text-dim); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }}

            .tasks-grid {{ display: grid; grid-template-columns: 1fr; gap: 2rem; }}
            .task-card {{ background: var(--card-bg); padding: 2rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); transition: transform 0.2s; }}
            .task-card:hover {{ transform: translateY(-4px); border-color: rgba(99, 102, 241, 0.3); }}
            .task-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
            .task-name {{ font-size: 1.4rem; font-weight: 600; }}
            .difficulty {{ padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }}
            .difficulty.easy {{ background: rgba(16, 185, 129, 0.1); color: var(--easy); }}
            .difficulty.medium {{ background: rgba(245, 158, 11, 0.1); color: var(--medium); }}
            .difficulty.hard {{ background: rgba(239, 68, 68, 0.1); color: var(--hard); }}
            
            .description {{ color: var(--text-dim); margin-bottom: 1.5rem; }}
            .code-block {{ background: #000; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; overflow-x: auto; }}
            pre {{ font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #10b981; }}
            .hint {{ padding: 1rem; background: rgba(255,255,255,0.02); border-left: 4px solid var(--accent); font-size: 0.95rem; }}
            
            footer {{ margin-top: 5rem; text-align: center; color: var(--text-dim); font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 2rem; }}
            .api-link {{ display: inline-block; margin: 1rem; color: var(--accent); text-decoration: none; font-weight: 600; }}
            .api-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>JSON Repair OpenEnv</h1>
                <p class="subtitle">A reinforcement learning environment for autonomous JSON fixing</p>
            </header>

            <div class="stats">
                <div class="stat-card"><span class="stat-val">{len(TASKS)}</span><span class="stat-label">Total Tasks</span></div>
                <div class="stat-card"><span class="stat-val">FastAPI</span><span class="stat-label">Environment</span></div>
                <div class="stat-card"><span class="stat-val">active</span><span class="stat-label">Status</span></div>
            </div>

            <div class="tasks-grid">
                {task_rows}
            </div>

            <footer>
                <p>Interactive API exploration:</p>
                <a href="/docs" class="api-link">API Swagger Documentation</a>
                <a href="/tasks" class="api-link">Tasks JSON</a>
                <a href="/state" class="api-link">Env State</a>
                <p style="margin-top: 1rem;">RL Environment Version 1.0.0</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/reset", response_model=ResetResult)
async def reset():
    """Reset the environment to the first task."""
    state.update({
        "session_id": str(uuid.uuid4()),
        "task_index": 0,
        "step": 0,
        "total_reward": 0.0,
        "done": False,
        "history": []
    })
    obs = build_observation()
    return ResetResult(observation=obs, done=False, reward=0.0)

@app.post("/step", response_model=StepResult)
async def step(action: Action):
    """Submit a repaired JSON and advance to next task."""
    if state["done"]:
        raise HTTPException(status_code=400, detail="Episode is done. Call /reset to start again.")

    task = TASKS[state["task_index"]]
    reward, info = grade_repair(action.repaired_json, task)

    state["step"] += 1
    state["total_reward"] += reward
    state["history"].append({
        "task": task["name"],
        "action": action.repaired_json[:100],
        "reward": reward,
        "info": info
    })

    state["task_index"] += 1
    done = state["task_index"] >= len(TASKS)
    state["done"] = done

    if done:
        obs = Observation(
            broken_json="",
            target_schema={},
            hint="All tasks completed! Call /reset to start a new episode.",
            task_name="episode_complete",
            step_number=state["step"],
            total_tasks=len(TASKS)
        )
    else:
        obs = build_observation()

    return StepResult(observation=obs, reward=reward, done=done, info=info)

@app.get("/state")
async def get_state():
    """Return current environment state."""
    return state

@app.get("/tasks")
async def list_tasks():
    """List all available tasks."""
    return [
        {
            "name": t["name"],
            "difficulty": t["difficulty"],
            "description": t["description"],
            "hint": t["hint"]
        }
        for t in TASKS
    ]
