#!/usr/bin/env python3
"""Build a per-tool success payload after completing one optimization pass."""
import json
import os
import sys


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


def build_top_savings(tool):
    savings = []
    for step in sorted(tool.get("steps", []), key=lambda item: item.get("projected_monthly_savings", 0), reverse=True):
        monthly = step.get("projected_monthly_savings", 0)
        per_session = step.get("projected_savings_per_session", 0)
        if not monthly and not per_session:
            continue
        savings.append(
            {
                "title": step.get("title", "Untitled step"),
                "health": step.get("health", {}),
                "projected_savings_per_session": per_session,
                "projected_monthly_savings": monthly,
                "waste_ratio_pct": step.get("waste_ratio_pct", 0),
            }
        )
        if len(savings) == 3:
            break
    return savings


def build_payload(tool, next_tool=None):
    before_after = tool.get("before_after", {})
    current_avg = before_after.get("current_avg_cost_per_session", 0)
    projected_avg = before_after.get("projected_avg_cost_per_session", 0)
    projected_monthly = before_after.get("projected_monthly_savings", 0)
    waste_ratio = before_after.get("waste_ratio_pct", 0)
    label = tool.get("tool_label", tool.get("tool_id"))
    top_savings = build_top_savings(tool)
    optimization_strategy = tool.get("optimization_strategy", {})
    status_report = {
        "before_after": {
            "avg_cost_before": current_avg,
            "avg_cost_after": projected_avg,
            "waste_ratio_before_pct": waste_ratio,
            "projected_monthly_savings": projected_monthly,
        },
        "key_statistics": tool.get("key_statistics", {}),
        "top_savings": top_savings,
        "optimization_strategy": optimization_strategy,
        "completed_steps": [
            {
                "rank": step.get("rank"),
                "title": step.get("title"),
                "health": step.get("health", {}),
            }
            for step in tool.get("steps", [])
        ],
    }

    payload = {
        "visibility": "result",
        "kind": "tool_success",
        "run_state": {
            "state": "completed",
            "resultPayload": "tool_success",
        },
        "hero": {
            "eyebrow": f"Tool #{tool.get('priority_rank', '?')} optimized",
            "headline": f"{label} is projected to drop from {fmt_currency(current_avg)}/session to {fmt_currency(projected_avg)}/session.",
            "supporting_text": "Show the win clearly before asking to continue to the next tool.",
        },
        "tool_success": {
            "tool_id": tool.get("tool_id"),
            "tool_label": label,
            "priority_rank": tool.get("priority_rank"),
            "health": tool.get("health"),
            "before_after": before_after,
            "key_statistics": tool.get("key_statistics", {}),
            "top_savings": top_savings,
            "optimization_strategy": optimization_strategy,
            "completed_steps": status_report["completed_steps"],
            "summary": {
                "waste_ratio_before_pct": waste_ratio,
                "avg_cost_before": current_avg,
                "avg_cost_after": projected_avg,
                "projected_monthly_savings": projected_monthly,
            },
        },
        "status_report": status_report,
        "sections": [
            {"id": "hero", "kind": "hero"},
            {"id": "before_after", "kind": "comparison"},
            {"id": "key_statistics", "kind": "statistics"},
            {"id": "top_savings", "kind": "savings"},
            {"id": "completed_steps", "kind": "procedure"},
        ],
        "message": (
            f"{label} was your tool #{tool.get('priority_rank', '?')}. "
            f"It is projected to move from {waste_ratio:.1f}% waste and {fmt_currency(current_avg)}/session "
            f"to {fmt_currency(projected_avg)}/session, saving about {fmt_currency(projected_monthly)}/month."
        ),
    }

    if next_tool and tool.get("priority_rank") == 1:
        payload["bulk_apply_prompt"] = {
            "message": (
                f"{label} is done. Want me to auto-apply the same treatment to your other tools and projects now, "
                f"starting with {next_tool.get('tool_label')}?"
            ),
            "command": f"python3 SKILL_DIR/scripts/present_bulk_apply_prompt.py /tmp/vibecheck_result.json {tool.get('tool_id')}",
            "next_tool_id": next_tool.get("tool_id"),
        }
        payload["sections"].append({"id": "bulk_apply_prompt", "kind": "bulk_apply"})
    elif next_tool:
        payload["continue_prompt"] = {
            "next_tool_id": next_tool.get("tool_id"),
            "next_tool_label": next_tool.get("tool_label"),
            "message": f"Next up is {next_tool.get('tool_label')}. Continue with tool #{next_tool.get('priority_rank', '?')}?",
        }
        payload["sections"].append({"id": "continue_prompt", "kind": "next_tool"})
    return payload


def main():
    if len(sys.argv) != 3:
        print("Usage: present_tool_success.py <scan_payload.json> <tool_id>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    plan = payload.get("optimization_plan", {})
    tool = find_tool(plan, sys.argv[2])
    next_tool = None
    if tool.get("next_tool_id"):
        next_tool = find_tool(plan, tool.get("next_tool_id"))
    print(json.dumps(build_payload(tool, next_tool), indent=2))


if __name__ == "__main__":
    main()
