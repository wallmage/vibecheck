#!/usr/bin/env python3
"""Helpers for tracking optimization workflow state."""
from copy import deepcopy


STEP_STATUS_PENDING = "pending"
STEP_STATUS_APPLIED = "applied"
STEP_STATUS_SKIPPED = "skipped"
VALID_STEP_STATUSES = {STEP_STATUS_PENDING, STEP_STATUS_APPLIED, STEP_STATUS_SKIPPED}


def actionable_targets(targets):
    output = []
    seen = set()
    for target in targets or []:
        if target.get("kind", "instruction_file") != "instruction_file":
            continue
        if target.get("exists") is False:
            continue
        path = target.get("path") or target.get("file")
        if not path or path in seen:
            continue
        seen.add(path)
        output.append(target)
    return output


def actionable_targets_for_step(step):
    return actionable_targets(step.get("target_files", []))


def pending_steps(tool):
    return [step for step in tool.get("steps", []) if step.get("execution", {}).get("status") == STEP_STATUS_PENDING]


def applied_steps(tool):
    return [step for step in tool.get("steps", []) if step.get("execution", {}).get("status") == STEP_STATUS_APPLIED]


def skipped_steps(tool):
    return [step for step in tool.get("steps", []) if step.get("execution", {}).get("status") == STEP_STATUS_SKIPPED]


def planned_steps(tool):
    return [step for step in tool.get("steps", []) if actionable_targets_for_step(step) or step.get("projected_savings_per_session", 0) or step.get("projected_monthly_savings", 0)]


def compute_before_after(tool, use_execution_state=False):
    current_avg = tool.get("before_after", {}).get("current_avg_cost_per_session", 0)
    baseline = {
        "current_avg_cost_per_session": current_avg,
        "projected_avg_cost_per_session": tool.get("before_after", {}).get("projected_avg_cost_per_session", current_avg),
        "projected_monthly_savings": tool.get("before_after", {}).get("projected_monthly_savings", 0),
        "waste_ratio_pct": tool.get("before_after", {}).get("waste_ratio_pct", 0),
    }
    if not use_execution_state:
        return baseline

    step_states = [step.get("execution", {}).get("status") for step in tool.get("steps", []) if step.get("execution")]
    if not any(state in {STEP_STATUS_APPLIED, STEP_STATUS_SKIPPED} for state in step_states):
        return baseline

    steps = applied_steps(tool)
    if not steps:
        return {
            "current_avg_cost_per_session": current_avg,
            "projected_avg_cost_per_session": current_avg,
            "projected_monthly_savings": 0,
            "waste_ratio_pct": 0,
        }

    projected_savings_per_session = sum(step.get("projected_savings_per_session", 0) for step in steps)
    projected_monthly = round(sum(step.get("projected_monthly_savings", 0) for step in steps), 2)
    waste_ratio_pct = round(sum(step.get("waste_ratio_pct", 0) for step in steps), 1)
    return {
        "current_avg_cost_per_session": current_avg,
        "projected_avg_cost_per_session": round(max(current_avg - projected_savings_per_session, 0), 2),
        "projected_monthly_savings": projected_monthly,
        "waste_ratio_pct": waste_ratio_pct,
    }


def next_actionable_tool(plan, current_tool_id=None):
    sequence = plan.get("tool_sequence", [])
    tools = {tool.get("tool_id"): tool for tool in plan.get("tools", [])}
    if current_tool_id is None:
        for tool_id in sequence:
            tool = tools.get(tool_id)
            if tool:
                return tool
        return None

    seen_current = False
    for tool_id in sequence:
        if tool_id == current_tool_id:
            seen_current = True
            continue
        if not seen_current:
            continue
        tool = tools.get(tool_id)
        if tool:
            return tool
    return None


def ensure_execution_state(payload):
    plan = payload.setdefault("optimization_plan", {})
    tools = plan.get("tools", [])
    existing_sequence = plan.get("tool_sequence", [])
    actionable_sequence = []

    for tool in tools:
        tool_steps = tool.get("steps", [])
        existing_execution = tool.get("execution_state", {})
        effective_targets = actionable_targets(
            tool.get("optimization_strategy", {}).get("effective_targets")
            or tool.get("optimization_strategy", {}).get("primary_targets")
            or tool.get("optimization_strategy", {}).get("fallback_targets")
        )
        step_targets = []

        for step in tool_steps:
            execution = step.setdefault("execution", {})
            status = execution.get("status", STEP_STATUS_PENDING)
            if status not in VALID_STEP_STATUSES:
                status = STEP_STATUS_PENDING
            execution["status"] = status
            execution.setdefault("applied_targets", [])
            execution.setdefault("skipped_targets", [])
            step_targets.extend(actionable_targets_for_step(step))

        applied = [step.get("rank") for step in applied_steps(tool)]
        skipped = [step.get("rank") for step in skipped_steps(tool)]
        pending = [step.get("rank") for step in pending_steps(tool)]
        has_prior_execution = existing_execution.get("status") not in (None, "blocked", {})
        can_auto_optimize = bool(effective_targets or step_targets or has_prior_execution)

        if can_auto_optimize and tool_steps:
            actionable_sequence.append(tool.get("tool_id"))

        if not can_auto_optimize:
            status = "blocked"
        elif pending:
            status = "in_progress" if applied or skipped else "pending"
        else:
            status = "completed"

        tool["can_auto_optimize"] = can_auto_optimize
        target_count = len(actionable_targets(effective_targets or step_targets))
        tool["execution_state"] = {
            "status": status,
            "applied_step_ranks": applied,
            "skipped_step_ranks": skipped,
            "pending_step_ranks": pending,
            "next_step_rank": pending[0] if pending else None,
            "actionable_target_count": target_count,
            "before_after": compute_before_after(tool, use_execution_state=True),
        }

    if existing_sequence:
        plan["tool_sequence"] = [tid for tid in existing_sequence if tid in actionable_sequence] + [tid for tid in actionable_sequence if tid not in existing_sequence]
    else:
        plan["tool_sequence"] = actionable_sequence
    sequence = plan.get("tool_sequence", [])
    plan["entry_tool_id"] = sequence[0] if sequence else None
    return payload


def mark_step_status(payload, tool_id, step_rank, status, applied_targets=None, skipped_targets=None):
    ensure_execution_state(payload)
    tool = next((tool for tool in payload.get("optimization_plan", {}).get("tools", []) if tool.get("tool_id") == tool_id), None)
    if tool is None:
        raise KeyError(tool_id)
    step = next((step for step in tool.get("steps", []) if step.get("rank") == step_rank), None)
    if step is None:
        raise KeyError(step_rank)

    execution = step.setdefault("execution", {})
    execution["status"] = status
    if applied_targets is not None:
        execution["applied_targets"] = deepcopy(applied_targets)
    if skipped_targets is not None:
        execution["skipped_targets"] = deepcopy(skipped_targets)
    ensure_execution_state(payload)
    return tool, step
