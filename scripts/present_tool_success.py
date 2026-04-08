#!/usr/bin/env python3
"""Build a per-tool success payload after completing one optimization pass."""
import json
import os
import sys

from workflow_state import (
    STEP_STATUS_APPLIED,
    STEP_STATUS_SKIPPED,
    compute_before_after,
    ensure_execution_state,
    next_actionable_tool,
)


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


def tool_has_real_optimization(tool):
    step_states = [step.get("execution", {}).get("status") for step in tool.get("steps", []) if step.get("execution")]
    if not step_states:
        return True
    return any(state == STEP_STATUS_APPLIED for state in step_states)


def build_top_savings(tool):
    step_states = [step.get("execution", {}).get("status") for step in tool.get("steps", []) if step.get("execution")]
    steps = [
        step for step in tool.get("steps", [])
        if step.get("execution", {}).get("status") == STEP_STATUS_APPLIED
    ]
    if any(state in {STEP_STATUS_APPLIED, STEP_STATUS_SKIPPED} for state in step_states) and not steps:
        return []
    if not steps:
        steps = tool.get("steps", [])
    savings = []
    for step in sorted(steps, key=lambda item: item.get("projected_monthly_savings", 0), reverse=True):
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
    before_after = compute_before_after(tool, use_execution_state=True)
    original_before_after = tool.get("before_after", {})
    current_avg = before_after.get("current_avg_cost_per_session", 0)
    projected_avg = before_after.get("projected_avg_cost_per_session", 0)
    projected_monthly = before_after.get("projected_monthly_savings", 0)
    waste_ratio = before_after.get("waste_ratio_pct", 0)
    label = tool.get("tool_label", tool.get("tool_id"))
    top_savings = build_top_savings(tool)
    optimization_strategy = tool.get("optimization_strategy", {})
    step_states = [step.get("execution", {}).get("status") for step in tool.get("steps", []) if step.get("execution")]
    use_execution = any(state in {STEP_STATUS_APPLIED, STEP_STATUS_SKIPPED} for state in step_states)
    real_optimization = tool_has_real_optimization(tool)
    if use_execution and not real_optimization:
        before_after = {
            "current_avg_cost_per_session": current_avg,
            "projected_avg_cost_per_session": current_avg,
            "projected_monthly_savings": 0,
            "waste_ratio_pct": original_before_after.get("waste_ratio_pct", 0),
        }
        projected_avg = current_avg
        projected_monthly = 0
        waste_ratio = before_after.get("waste_ratio_pct", 0)

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
            if (step.get("execution", {}).get("status") == STEP_STATUS_APPLIED) or (not use_execution)
        ],
        "skipped_steps": [
            {
                "rank": step.get("rank"),
                "title": step.get("title"),
            }
            for step in tool.get("steps", [])
            if use_execution and step.get("execution", {}).get("status") == STEP_STATUS_SKIPPED
        ],
    }

    if real_optimization:
        hero = {
            "eyebrow": f"Tool #{tool.get('priority_rank', '?')} optimized",
            "headline": f"{label} is projected to drop from {fmt_currency(current_avg)}/session to {fmt_currency(projected_avg)}/session.",
            "supporting_text": "Show the win clearly before asking whether to apply the same treatment everywhere else.",
        }
        message = (
            f"{label} was your tool #{tool.get('priority_rank', '?')}. "
            f"It is projected to move from {waste_ratio:.1f}% waste and {fmt_currency(current_avg)}/session "
            f"to {fmt_currency(projected_avg)}/session, saving about {fmt_currency(projected_monthly)}/month."
        )
    else:
        hero = {
            "eyebrow": f"Tool #{tool.get('priority_rank', '?')} reviewed",
            "headline": f"No changes were applied to {label}, so it stays around {fmt_currency(current_avg)}/session.",
            "supporting_text": "All proposed steps were skipped, so there is no savings win to report for this tool.",
        }
        message = (
            f"All proposed steps were skipped for {label}. "
            f"It still sits around {waste_ratio:.1f}% waste and {fmt_currency(current_avg)}/session."
        )

    payload = {
        "visibility": "result",
        "kind": "tool_success",
        "run_state": {
            "state": "completed",
            "resultPayload": "tool_success",
        },
        "hero": hero,
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
            "skipped_steps": status_report["skipped_steps"],
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
        "message": message,
    }

    if tool.get("priority_rank") == 1:
        if next_tool:
            payload["bulk_apply_prompt"] = {
                "message": (
                    f"{label} is done. Want me to auto-apply the same treatment to your other tools and projects now, "
                    f"starting with {next_tool.get('tool_label')}?"
                ),
                "command": f"python3 SKILL_DIR/scripts/present_bulk_apply_prompt.py /tmp/vibecheck_result.json {tool.get('tool_id')}",
                "next_tool_id": next_tool.get("tool_id"),
            }
            payload["sections"].append({"id": "bulk_apply_prompt", "kind": "bulk_apply"})
            finish_message = "If not, I can stop here and show the final summary for the work already applied."
        else:
            finish_message = "There are no more tools in this scan. I can wrap this up with the final summary and education."

        payload["finish_prompt"] = {
            "message": finish_message,
            "command": "python3 SKILL_DIR/scripts/present_final_success.py /tmp/vibecheck_result.json",
        }
        payload["sections"].append({"id": "finish_prompt", "kind": "finish"})
    return payload


def main():
    if len(sys.argv) != 3:
        print("Usage: present_tool_success.py <scan_payload.json> <tool_id>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    ensure_execution_state(payload)
    plan = payload.get("optimization_plan", {})
    tool = find_tool(plan, sys.argv[2])
    next_tool = None
    if tool.get("next_tool_id"):
        next_tool = find_tool(plan, tool.get("next_tool_id"))
    elif tool.get("tool_id") in plan.get("tool_sequence", []):
        next_tool = next_actionable_tool(plan, tool.get("tool_id"))
    print(json.dumps(build_payload(tool, next_tool), indent=2))


if __name__ == "__main__":
    main()
