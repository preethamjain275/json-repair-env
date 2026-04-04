from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uvicorn
import uuid
from dotenv import load_dotenv

load_dotenv()

from .tasks import TASKS
from .grader import grade_repair

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

# --- Activity Logs (In-Memory) ---
logs: List[str] = [
    "[SYSTEM] Environment Initialized.",
    "[SYSTEM] Ready for incoming agent connections.",
    "[DASHBOARD] UI v2.0.0 (High-Performance) loaded."
]

@app.get("/", response_class=HTMLResponse)
async def root():
    task_cards = ""
    for task in TASKS:
        task_cards += f"""
        <div class="glass-card task-item">
            <div class="task-top">
                <span class="task-id">{task['name']}</span>
                <span class="badge {task['difficulty']}">{task['difficulty'].upper()}</span>
            </div>
            <p class="task-desc">{task['description']}</p>
            <div class="code-container">
                <div class="scan-line"></div>
                <pre><code>{task['broken_json']}</code></pre>
            </div>
            <div class="task-footer">
                <span class="hint-label">DIAGNOSIS:</span>
                <span class="hint-text">{task['hint']}</span>
            </div>
        </div>
        """

    log_items = "".join([f'<div class="log-line">{line}</div>' for line in logs])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JSON-REPAIR | Neural Environment</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #05060d;
                --surface: rgba(18, 20, 32, 0.7);
                --accent: #7c3aed;
                --accent-glow: rgba(124, 58, 237, 0.3);
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --text: #f8fafc;
                --text-dim: #94a3b8;
                --border: rgba(255, 255, 255, 0.08);
            }}

            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg);
                background-image: 
                    radial-gradient(circle at 10% 10%, rgba(124, 58, 237, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
                color: var(--text);
                min-height: 100vh;
                overflow-x: hidden;
            }}

            /* --- Header --- */
            nav {{
                padding: 1.5rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border);
                background: rgba(5, 6, 13, 0.8);
                backdrop-filter: blur(10px);
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            .logo {{ font-size: 1.2rem; font-weight: 700; letter-spacing: 2px; display: flex; align-items: center; gap: 10px; }}
            .logo-icon {{ width: 24px; height: 24px; background: var(--accent); border-radius: 4px; box-shadow: 0 0 15px var(--accent-glow); }}
            .logo span {{ color: var(--accent); }}
            
            .sys-meta {{ display: flex; gap: 30px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
            .meta-item {{ display: flex; flex-direction: column; }}
            .meta-label {{ color: var(--text-dim); font-size: 0.7rem; }}
            .status-active {{ color: var(--success); text-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }}

            /* --- Main Layout --- */
            main {{
                display: grid;
                grid-template-columns: 350px 1fr;
                gap: 2rem;
                padding: 2rem;
                max-width: 1600px;
                margin: 0 auto;
            }}

            /* --- Left Sidebar (Console) --- */
            .console-panel {{
                height: calc(100vh - 120px);
                display: flex;
                flex-direction: column;
                gap: 1rem;
                position: sticky;
                top: 100px;
            }}
            .terminal {{
                flex: 1;
                background: #000;
                border-radius: 12px;
                padding: 1.5rem;
                border: 1px solid var(--border);
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                position: relative;
                overflow: hidden;
            }}
            .terminal-header {{ border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 15px; display: flex; gap: 5px; }}
            .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
            .log-line {{ margin-bottom: 5px; color: var(--text-dim); }}
            .log-line:last-child {{ color: var(--success); border-left: 2px solid var(--success); padding-left: 10px; }}
            
            .action-panel {{
                background: var(--surface);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid var(--border);
                backdrop-filter: blur(10px);
            }}
            .btn {{
                width: 100%;
                padding: 12px;
                background: transparent;
                border: 1px solid var(--border);
                color: var(--text);
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: 0.3s;
                text-decoration: none;
                display: block;
                text-align: center;
                margin-bottom: 10px;
            }}
            .btn:hover {{ background: rgba(255,255,255,0.05); border-color: var(--accent); color: var(--accent); }}
            .btn-accent {{ background: var(--accent); border: none; }}
            .btn-accent:hover {{ background: #8b5cf6; color: white; box-shadow: 0 0 20px var(--accent-glow); }}

            /* --- Center (Tasks) --- */
            .tasks-container {{ display: flex; flex-direction: column; gap: 1.5rem; }}
            .glass-card {{
                background: var(--surface);
                border-radius: 16px;
                padding: 2rem;
                border: 1px solid var(--border);
                backdrop-filter: blur(20px);
                position: relative;
                overflow: hidden;
            }}
            
            .task-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
            .task-id {{ font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--accent); }}
            .badge {{ padding: 4px 12px; border-radius: 100px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }}
            .easy {{ background: rgba(16, 185, 129, 0.1); color: var(--success); }}
            .medium {{ background: rgba(245, 158, 11, 0.1); color: var(--warning); }}
            .hard {{ background: rgba(239, 68, 68, 0.1); color: var(--danger); }}
            .extreme {{ background: rgba(124, 58, 237, 0.1); color: #a78bfa; border: 1px solid var(--accent); }}
            .chaos {{ background: linear-gradient(45deg, #ef4444, #7c3aed); color: white; }}

            .task-desc {{ color: var(--text-dim); margin-bottom: 1.5rem; font-size: 0.95rem; }}
            
            .code-container {{
                background: #000;
                padding: 1.5rem;
                border-radius: 10px;
                position: relative;
                margin-bottom: 1.5rem;
                border: 1px solid #1a1b26;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
            }}
            pre {{ font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #7dd3fc; white-space: pre-wrap; }}
            
            .scan-line {{
                position: absolute;
                top: 0; left: 0; width: 100%; height: 2px;
                background: linear-gradient(to right, transparent, var(--accent), transparent);
                animation: scan 3s infinite linear;
                opacity: 0.5;
            }}
            @keyframes scan {{
                0% {{ top: 0; }}
                100% {{ top: 100%; }}
            }}

            .task-footer {{ display: flex; gap: 15px; align-items: flex-start; padding: 1rem; background: rgba(255,255,255,0.02); border-radius: 8px; }}
            .hint-label {{ font-size: 0.7rem; font-weight: 800; color: var(--text-dim); margin-top: 3px; }}
            .hint-text {{ font-size: 0.9rem; color: #cbd5e1; italic; }}

            /* --- Animations --- */
            .task-item {{ opacity: 0; transform: translateY(20px); animation: fadeInUp 0.5s forwards; }}
            @keyframes fadeInUp {{
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .task-item:nth-child(1) {{ animation-delay: 0.1s; }}
            .task-item:nth-child(2) {{ animation-delay: 0.2s; }}
            .task-item:nth-child(3) {{ animation-delay: 0.3s; }}
            .task-item:nth-child(4) {{ animation-delay: 0.4s; }}
            .task-item:nth-child(5) {{ animation-delay: 0.5s; }}

        </style>
    </head>
    <body>
        <nav>
            <div class="logo">
                <div class="logo-icon"></div>
                JSON<span>REPAIR</span>.ENV
            </div>
            <div class="sys-meta">
                <div class="meta-item">
                    <span class="meta-label">ENVIRONMENT</span>
                    <span>HF-DOCKER-NODE-01</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">SESSION</span>
                    <span style="color:var(--accent)">{state['session_id'][:12] or 'NONE'}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">SYSTEM STATE</span>
                    <span class="status-active">▶ ACTIVE</span>
                </div>
            </div>
        </nav>

        <main>
            <section class="console-panel">
                <div class="terminal">
                    <div class="terminal-header">
                        <div class="dot" style="background:var(--danger)"></div>
                        <div class="dot" style="background:var(--warning)"></div>
                        <div class="dot" style="background:var(--success)"></div>
                        <span style="margin-left: 10px; color:#444; font-size:0.7rem">SRE-COMMAND-UNIT-v2.0</span>
                    </div>
                    <div id="log-container">
                        {log_items}
                    </div>
                </div>
                <div class="action-panel">
                    <a href="/docs" class="btn btn-accent">SWAGGER API DOCS</a>
                    <a href="/tasks" class="btn">VIEW TASKS JSON</a>
                    <a href="/state" class="btn">ENVIRONMENT STATE</a>
                    <p style="text-align: center; color: var(--text-dim); font-size: 0.7rem; margin-top: 10px;">
                        PLATFORM VERSION: 1.0.0-PRO
                    </p>
                </div>
            </section>

            <section class="tasks-container">
                <div class="glass-card" style="border-color: var(--accent); margin-bottom: 2rem;">
                    <h2 style="margin-bottom: 1rem; font-size: 1.2rem;">⚡ CUSTOM REPAIR LAB</h2>
                    <p class="task-desc">Others can use this to validate their own JSON logic instantly.</p>
                    <textarea id="custom-json" style="width: 100%; height: 100px; background: #000; color: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 10px; font-family: 'JetBrains Mono', monospace; margin-bottom: 10px;" placeholder="Paste your broken JSON here..."></textarea>
                    <button onclick="testJSON()" class="btn btn-accent" style="margin: 0;">VALIDATE & FIX TEST</button>
                    <div id="custom-result" style="margin-top: 10px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;"></div>
                </div>
                {task_cards}
            </section>
        </main>

        <script>
            async function testJSON() {{
                const val = document.getElementById('custom-json').value;
                const resDiv = document.getElementById('custom-result');
                resDiv.innerHTML = '<span style="color:var(--accent)">Analyzing...</span>';
                
                try {{
                    const response = await fetch('/test_custom', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ repaired_json: val }})
                    }});
                    const data = await response.json();
                    if (data.status === 'valid') {{
                        resDiv.innerHTML = '<span style="color:var(--success)">✓ VALID JSON STRUCTURE</span>';
                    }} else {{
                        resDiv.innerHTML = '<span style="color:var(--danger)">✗ INVALID: ' + data.error + '</span>';
                    }}
                }} catch (e) {{
                    resDiv.innerHTML = '<span style="color:var(--danger)">Error connecting to server</span>';
                }}
            }}

            // Simple log auto-scroll
            const container = document.getElementById('log-container');
            container.scrollTop = container.scrollHeight;

            // Auto-refresh the dashboard every 2 seconds to show live agent activity
            setTimeout(() => {{
                window.location.reload();
            }}, 2000);
        </script>
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
    logs.append(f"[EVENT] Environment Reset. Session: {state['session_id'][:8]}")
    if len(logs) > 50: logs.pop(0)
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
    logs.append(f"[AGENT] Action submitted for {task['name']}. Reward: {reward}")
    if len(logs) > 50: logs.pop(0)

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

@app.post("/test_custom")
async def test_custom(action: Action):
    """Utility endpoint for users to test their own repairs against a generic validator."""
    try:
        data = json.loads(action.repaired_json)
        logs.append(f"[USER] Manual repair test: VALID JSON")
        return {"status": "valid", "data": data}
    except Exception as e:
        logs.append(f"[USER] Manual repair test: INVALID. Error: {str(e)}")
        return {"status": "invalid", "error": str(e)}

def main():
    """Main entry point for the server."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
