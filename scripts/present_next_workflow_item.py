#!/usr/bin/env python3
"""Return the next pending optimization step for a tool, or the tool success payload if complete."""
import json
import sys

from present_final_success import build_payload as build_final_success_payload
from present_optimization_step import build_payload as build_step_payload
from present_tool_success import build_payload as build_tool_success_payload, find_tool
from vibecheck_optimize import load_json
from workflow_state import ensure_execution_state, next_actionable_tool


def main():
    if len(sys.argv) != 3:
        print("Usage: present_next_workflow_item.py <scan_payload.json> <tool_id>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    ensure_execution_state(payload)
    plan = payload.get("optimization_plan", {})
    tool = find_tool(plan, sys.argv[2])
    next_step_rank = tool.get("execution_state", {}).get("next_step_rank")

    if next_step_rank is not None:
        step = next(step for step in tool.get("steps", []) if step.get("rank") == next_step_rank)
        result = build_step_payload(tool, step)
    else:
        if tool.get("priority_rank") == 1:
            next_tool = next_actionable_tool(plan, tool.get("tool_id"))
            result = build_tool_success_payload(tool, next_tool)
        else:
            result = build_final_success_payload(payload)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
