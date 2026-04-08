#!/usr/bin/env python3
"""Build the approval payload for auto-applying the remaining optimization plan."""
import json
import os
import sys

from scan_contract import PAYLOAD_KINDS
from workflow_state import ensure_execution_state


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(path):
    if not os.path.exists(path):
        fail(f"file not found: {path}")
    with open(path) as f:
        content = f.read().strip()
    if not content:
        fail(f"file is empty: {path}")
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def find_tool(plan, tool_id):
    for tool in plan.get("tools", []):
        if tool.get("tool_id") == tool_id:
            return tool
    fail(f"tool not found in optimization plan: {tool_id}")


def fmt_currency(amount):
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"


def count_unique_target_files(tools):
    seen = set()
    for tool in tools:
        for step in tool.get("steps", []):
            for target in step.get("target_files", []):
                path = target.get("path") or target.get("file")
                if path:
                    seen.add(path)
    return len(seen)


def main():
    if len(sys.argv) != 3:
        print("Usage: present_bulk_apply_prompt.py <scan_payload.json> <completed_tool_id>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    ensure_execution_state(payload)
    completed_tool_id = sys.argv[2]
    plan = payload.get("optimization_plan", {})
    completed_tool = find_tool(plan, completed_tool_id)
    remaining_ids = [tool_id for tool_id in plan.get("tool_sequence", []) if tool_id != completed_tool_id]
    remaining = [find_tool(plan, tool_id) for tool_id in remaining_ids]

    remaining_tools = len(remaining)
    remaining_targets = count_unique_target_files(remaining)
    projected_monthly = round(
        sum(tool.get("before_after", {}).get("projected_monthly_savings", 0) for tool in remaining),
        2,
    )
    target_label = "target edit" if remaining_targets == 1 else "target edits"

    result = {
        "visibility": "approval",
        "kind": PAYLOAD_KINDS["approval"],
        "run_state": {
            "state": "idle",
        },
        "card": {
            "title": "Apply the same treatment everywhere else",
            "body": (
                f"{completed_tool.get('tool_label', completed_tool_id)} is done. "
                f"I can now auto-apply the remaining planned fixes across {remaining_tools} other tools/projects, "
                f"covering about {remaining_targets} {target_label} and roughly {fmt_currency(projected_monthly)}/month in projected savings."
            ),
            "command": f"python3 SKILL_DIR/scripts/vibecheck_optimize_bulk.py /tmp/vibecheck_result.json {completed_tool_id}",
        },
        "workflow": {
            "completed_tool_id": completed_tool_id,
            "remaining_tool_ids": [tool.get("tool_id") for tool in remaining],
            "remaining_tools": remaining_tools,
            "remaining_target_files": remaining_targets,
            "projected_monthly_savings": projected_monthly,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
