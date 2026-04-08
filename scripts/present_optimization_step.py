#!/usr/bin/env python3
"""Build an approval payload for a specific tool optimization step."""
import json
import os
import sys

from scan_contract import PAYLOAD_KINDS
from vibecheck_optimize import build_rule_lines
from workflow_state import ensure_execution_state, pending_steps


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


def find_step(tool, step_rank):
    for step in tool.get("steps", []):
        if step.get("rank") == step_rank:
            return step
    fail(f"step {step_rank} not found for tool {tool.get('tool_id')}")


def build_command(tool_id, step_rank):
    return f"python3 SKILL_DIR/scripts/vibecheck_optimize.py /tmp/vibecheck_result.json {tool_id} {step_rank}"


def build_payload(tool, step):
    facts = []
    for fact in step.get("facts", []):
        label = fact.get("label")
        value = fact.get("value")
        if label and value is not None:
            facts.append(f"{label}: {value}")

    targets = []
    for target in step.get("target_files", []):
        display = target.get("path") or target.get("file") if target.get("scope") == "global" else target.get("filename") or target.get("path") or target.get("file")
        if display:
            targets.append(display)

    body_parts = [
        f"{step.get('health', {}).get('emoji', '➖')} {step.get('title', 'Untitled step')}",
        step.get("explanation", {}).get("summary", ""),
        step.get("explanation", {}).get("why_it_matters", ""),
    ]
    if facts:
        body_parts.append(" | ".join(facts))
    if step.get("projected_savings_per_session", 0):
        body_parts.append(
            f"Projected savings: ${step.get('projected_savings_per_session', 0):.3f}/session and ${step.get('projected_monthly_savings', 0):.2f}/month."
        )
    if targets:
        body_parts.append(f"Targets: {', '.join(targets)}")
    strategy = step.get("target_strategy") or tool.get("optimization_strategy") or {}
    if strategy.get("summary"):
        body_parts.append(strategy.get("summary"))
    if strategy.get("fallback_target_count"):
        body_parts.append(f"Fallback project targets: {strategy.get('fallback_target_count')}")

    preview_lines = [f"+ {line}" for line in build_rule_lines(step)]

    return {
        "visibility": "approval",
        "kind": PAYLOAD_KINDS["approval"],
        "run_state": {
            "state": "idle",
        },
        "card": {
            "title": f"Optimize {tool.get('tool_label', tool.get('tool_id'))}: step {step.get('rank')}",
            "body": " ".join(part for part in body_parts if part),
            "command": build_command(tool.get("tool_id"), step.get("rank")),
        },
        "proposed_change": {
            "format": "diff_preview",
            "additions": preview_lines,
        },
        "workflow": {
            "tool_id": tool.get("tool_id"),
            "tool_label": tool.get("tool_label"),
            "priority_rank": tool.get("priority_rank"),
            "step": step,
            "optimization_strategy": tool.get("optimization_strategy", {}),
            "before_after": tool.get("before_after", {}),
            "next_tool_id": tool.get("next_tool_id"),
        },
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: present_optimization_step.py <scan_payload.json> <tool_id> <step_rank>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    ensure_execution_state(payload)
    tool = find_tool(payload.get("optimization_plan", {}), sys.argv[2])
    step = find_step(tool, int(sys.argv[3]))
    print(json.dumps(build_payload(tool, step), indent=2))


if __name__ == "__main__":
    main()
