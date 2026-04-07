import json
import jsonschema


def grade_repair(repaired_json: str, task: dict) -> tuple:
    """
    Grade the agent's JSON repair. Returns (reward: float 0.0-1.0, info: dict)
    
    Scoring:
    - Valid JSON syntax:     0.40
    - Schema compliance:     0.40
    - Semantic correctness:  0.20
    """
    score = 0.0
    info = {"errors": [], "checks": {}}

    # --- Check 1: Valid JSON syntax (40%) ---
    try:
        parsed = json.loads(repaired_json)
        score += 0.40
        info["checks"]["valid_json"] = True
    except json.JSONDecodeError as e:
        info["errors"].append(f"Invalid JSON syntax: {str(e)}")
        info["checks"]["valid_json"] = False
        info["final_score"] = 0.1
        return 0.1, info

    # --- Check 2: Schema compliance (40%) ---
    try:
        jsonschema.validate(instance=parsed, schema=task["schema"])
        score += 0.40
        info["checks"]["schema_valid"] = True
    except jsonschema.ValidationError as e:
        info["errors"].append(f"Schema validation failed: {e.message}")
        info["checks"]["schema_valid"] = False
        score += 0.05  # tiny partial credit for at least being valid JSON

    # --- Check 3: Exact semantic match (20%) ---
    try:
        correct = json.loads(task["correct_json"])
        if parsed == correct:
            score += 0.20
            info["checks"]["exact_match"] = True
        else:
            # Partial credit: how many required keys match correctly
            required = task["schema"].get("required", [])
            if required:
                matched = sum(
                    1 for k in required
                    if k in parsed and k in correct and parsed[k] == correct[k]
                )
                partial = (matched / len(required)) * 0.10
                score += partial
            info["checks"]["exact_match"] = False
    except Exception:
        info["checks"]["exact_match"] = False

    # CLIP TO (0, 1) RANGE: Hackathon requirements specify scores must be strictly between 0 and 1
    # We use a base of 0.1 and a multiplier of 0.8 so that 0 becomes 0.1 and 1 becomes 0.9
    final_score = round(0.1 + (score * 0.8), 4)

    info["final_score"] = final_score
    return final_score, info
