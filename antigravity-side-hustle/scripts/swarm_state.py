import json
import os
import argparse
import sys
from datetime import datetime

STATE_FILE = "_artifacts/swarm_state.json"
TASK_ID_PREFIX = "TKT-"
TASK_ID_START = 100


def _derive_next_id(tasks):
    max_seen = TASK_ID_START - 1
    for task in tasks:
        raw = str(task.get("id", ""))
        if raw.startswith(TASK_ID_PREFIX):
            try:
                num = int(raw[len(TASK_ID_PREFIX):])
                max_seen = max(max_seen, num)
            except ValueError:
                continue
    return max_seen + 1



def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "mission_id": "INIT",
            "status": "active",
            "tasks": [],
            "next_id": TASK_ID_START,
        }
    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    # Backfill next_id if missing
    if "next_id" not in state:
        state["next_id"] = _derive_next_id(state.get("tasks", []))
    return state



def save_state(state):
    os.makedirs("_artifacts", exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)



def _next_task_id(state):
    task_id = f"{TASK_ID_PREFIX}{state['next_id']}"
    state["next_id"] += 1
    return task_id



def add_task(desc, skill):
    state = load_state()
    task_id = _next_task_id(state)
    state["tasks"].append({
        "id": task_id,
        "description": desc,
        "assigned_skill": skill,
        "status": "todo",
        "created_at": datetime.now().isoformat(),
    })
    save_state(state)
    print(f"Created {task_id}: {desc}")



def update_task(task_id, status, artifact=None):
    state = load_state()
    for task in state["tasks"]:
        if task["id"] == task_id:
            task["status"] = status
            if artifact:
                task["artifact"] = artifact
            save_state(state)
            print(f"Updated {task_id} to {status}")
            return True

    # Task not found: do not write state; signal failure
    raise ValueError(f"Task {task_id} not found; no updates applied.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Side Hustle Task Ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add Task
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--desc", required=True)
    add_parser.add_argument("--skill", required=True)

    # Update Task
    upd_parser = subparsers.add_parser("update")
    upd_parser.add_argument("--id", required=True)
    upd_parser.add_argument(
        "--status",
        choices=["todo", "in_progress", "done", "blocked"],
        required=True,
    )
    upd_parser.add_argument("--artifact", help="Path to output file")

    args = parser.parse_args()
    if args.command == "add":
        add_task(args.desc, args.skill)
    elif args.command == "update":
        try:
            update_task(args.id, args.status, args.artifact)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
