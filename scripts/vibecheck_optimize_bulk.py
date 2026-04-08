#!/usr/bin/env python3
"""Apply all planned optimization steps to the remaining tools after tool #1 approval."""
import json
import sys

from vibecheck_optimize import apply_all_steps_for_tool, load_json, persist_payload
from workflow_state import ensure_execution_state


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) not in {2, 3}:
        print("Usage: vibecheck_optimize_bulk.py <scan_payload.json> [completed_tool_id]", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    ensure_execution_state(payload)
    completed_tool_id = sys.argv[2] if len(sys.argv) == 3 else None
    plan = payload.get("optimization_plan", {})
    tools = plan.get("tools", [])
    if not tools:
        fail("no optimization plan tools found")

    remaining = [
        tool for tool in tools
        if tool.get("tool_id") != completed_tool_id and tool.get("can_auto_optimize") and tool.get("steps")
    ]

    results = []
    total_applied = 0
    total_skipped = 0
    for tool in remaining:
        result = apply_all_steps_for_tool(payload, tool.get("tool_id"))
        total_applied += len(result["applied"])
        total_skipped += len(result["skipped"])
        results.append(result)

    persist_payload(sys.argv[1], payload)

    print(
        json.dumps(
            {
                "ok": True,
                "completed_tool_id": completed_tool_id,
                "tools_processed": len(results),
                "targets_applied": total_applied,
                "targets_skipped": total_skipped,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
