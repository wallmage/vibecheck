#!/usr/bin/env python3
"""Mark an optimization step as skipped so the workflow can continue truthfully."""
import json
import sys

from vibecheck_optimize import find_step, find_tool, load_json, persist_payload
from workflow_state import STEP_STATUS_SKIPPED, ensure_execution_state, mark_step_status


def main():
    if len(sys.argv) != 4:
        print("Usage: vibecheck_skip_step.py <scan_payload.json> <tool_id> <step_rank>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    ensure_execution_state(payload)
    tool = find_tool(payload.get("optimization_plan", {}), sys.argv[2])
    step = find_step(tool, int(sys.argv[3]))
    mark_step_status(payload, tool.get("tool_id"), step.get("rank"), STEP_STATUS_SKIPPED, skipped_targets=step.get("target_files", []))
    persist_payload(sys.argv[1], payload)
    refreshed_tool = find_tool(payload.get("optimization_plan", {}), tool.get("tool_id"))
    print(
        json.dumps(
            {
                "ok": True,
                "tool_id": tool.get("tool_id"),
                "step_rank": step.get("rank"),
                "next_pending_step_rank": refreshed_tool.get("execution_state", {}).get("next_step_rank"),
                "tool_complete": refreshed_tool.get("execution_state", {}).get("status") == "completed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
