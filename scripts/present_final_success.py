#!/usr/bin/env python3
"""Build the final all-tools optimization success summary before education begins."""
import json
import os
import sys

from workflow_state import STEP_STATUS_APPLIED, compute_before_after, ensure_execution_state


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


def fmt_currency(amount):
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"


def build_tool_session_weights(payload, tools):
    stats = payload.get("header_statistics", {}).get("tools", [])
    stats_by_id = {item.get("id"): item for item in stats}
    weights = {}
    for tool in tools:
        tool_id = tool.get("tool_id")
        weight = (
            tool.get("session_count")
            or tool.get("sessions")
            or stats_by_id.get(tool_id, {}).get("sessions")
            or 0
        )
        weights[tool_id] = weight
    return weights


def weighted_average(tool_before_after, weights, key):
    weighted_items = [
        (item.get(key, 0), weights.get(tool_id, 0))
        for tool_id, item in tool_before_after.items()
        if weights.get(tool_id, 0) > 0
    ]
    if weighted_items:
        total_weight = sum(weight for _, weight in weighted_items)
        return round(sum(value * weight for value, weight in weighted_items) / total_weight, 3)

    values = [item.get(key, 0) for item in tool_before_after.values()]
    if not values:
        return 0
    return round(sum(values) / len(values), 3)


def tool_has_real_optimization(tool):
    step_states = [step.get("execution", {}).get("status") for step in tool.get("steps", []) if step.get("execution")]
    if not step_states:
        return True
    return any(state == STEP_STATUS_APPLIED for state in step_states)


def build_payload(payload):
    ensure_execution_state(payload)
    completed_tools = [
        tool for tool in payload.get("optimization_plan", {}).get("tools", [])
        if tool.get("execution_state", {}).get("status") == "completed"
    ]
    if not completed_tools:
        completed_tools = payload.get("optimization_plan", {}).get("tools", [])
    if not completed_tools:
        fail("no optimization plan tools found")

    optimized_tools = [tool for tool in completed_tools if tool_has_real_optimization(tool)]
    summary_tools = optimized_tools or completed_tools

    tool_before_after = {tool.get("tool_id"): compute_before_after(tool, use_execution_state=True) for tool in summary_tools}
    total_monthly = round(
        sum(compute_before_after(tool, use_execution_state=True).get("projected_monthly_savings", 0) for tool in optimized_tools),
        2,
    )
    session_weights = build_tool_session_weights(payload, summary_tools)
    total_before = weighted_average(tool_before_after, session_weights, "current_avg_cost_per_session")
    total_after = weighted_average(tool_before_after, session_weights, "projected_avg_cost_per_session")
    top_tools = sorted(
        optimized_tools,
        key=lambda item: compute_before_after(item, use_execution_state=True).get("projected_monthly_savings", 0),
        reverse=True,
    )[:3]

    if optimized_tools:
        hero = {
            "eyebrow": "Optimization complete",
            "headline": f"Projected average cost drops from {fmt_currency(total_before)} to {fmt_currency(total_after)} across the optimized tools.",
            "supporting_text": "Show the optimization win first. Human education comes after this summary, not before it.",
        }
    else:
        hero = {
            "eyebrow": "Review complete",
            "headline": f"No changes were applied, so average cost stays around {fmt_currency(total_before)} across the reviewed tools.",
            "supporting_text": "The user skipped the proposed changes, so this summary is a truthful stop point before education.",
        }

    result = {
        "visibility": "result",
        "kind": "optimization_final_success",
        "run_state": {
            "state": "completed",
            "resultPayload": "optimization_final_success",
        },
        "hero": hero,
        "summary": {
            "tools_optimized": len(optimized_tools),
            "projected_monthly_savings": total_monthly,
            "avg_cost_before": total_before,
            "avg_cost_after": total_after,
        },
        "top_tool_wins": [
            {
                "tool_id": tool.get("tool_id"),
                "tool_label": tool.get("tool_label"),
                "projected_monthly_savings": compute_before_after(tool, use_execution_state=True).get("projected_monthly_savings", 0),
                "avg_cost_before": compute_before_after(tool, use_execution_state=True).get("current_avg_cost_per_session", 0),
                "avg_cost_after": compute_before_after(tool, use_execution_state=True).get("projected_avg_cost_per_session", 0),
            }
            for tool in top_tools
        ],
        "education_next": {
            "title": "Human-side tips come next",
            "body": "Agents are now tuned. Next, teach the user how to keep context lean, preserve continuity, and use the handoff companion when it is time to switch chats.",
            "command": "python3 SKILL_DIR/scripts/present_education.py /tmp/vibecheck_lesson.json",
            "lesson_file": "/tmp/vibecheck_lesson.json",
        },
        "sections": [
            {"id": "hero", "kind": "hero"},
            {"id": "summary", "kind": "comparison"},
            {"id": "top_tool_wins", "kind": "savings"},
            {"id": "education_next", "kind": "education"},
        ],
    }
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: present_final_success.py <scan_payload.json>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    result = build_payload(payload)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
