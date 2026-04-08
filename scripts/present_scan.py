#!/usr/bin/env python3
"""Build a polished scan result payload from analysis JSON."""
from collections import defaultdict
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from scan_contract import PAYLOAD_KINDS
from scan_contract import EMPTY_RESULT_SECTION_KINDS, RESULT_SECTION_KINDS, SUMMARY_METRIC_IDS
from workflow_state import actionable_targets, ensure_execution_state


WASTE_LABELS = {
    "idle_narration": "Idle narration",
    "context_rot": "Long sessions",
    "pingpong_debugging": "Fix-break-fix loops",
    "verbose_output": "Verbose output flooding",
    "codebase_wandering": "Codebase wandering",
    "chainable_bash": "Unchained commands",
    "unbatched_edits": "Unbatched edits",
    "duplicate_reads": "File re-reads",
    "sleep_poll_loops": "Sleep/poll loops",
    "git_ceremony": "Git ceremony",
    "failed_tools": "Failed tools",
    "toolsearch": "Tool search detours",
    "heartbeat_idle": "Idle heartbeats",
    "workspace_bloat": "Workspace bloat",
    "memory_accumulation": "Memory accumulation",
}

WASTE_SUMMARIES = {
    "idle_narration": "Status-only turns that re-read the full conversation before acting.",
    "context_rot": "Long chats keep dragging old context through every later turn.",
    "pingpong_debugging": "Repeated fix-break-fix cycles inflate both turns and reread cost.",
    "verbose_output": "Large command output keeps bloating context long after the command finishes.",
    "codebase_wandering": "Too many read/search turns before the work starts.",
    "chainable_bash": "Independent shell steps could happen in one denser turn.",
    "unbatched_edits": "Separate edits across turns create avoidable reread cost.",
    "duplicate_reads": "Reading the same file again wastes a turn after the content is already in context.",
    "sleep_poll_loops": "Polling loops keep paying context tax while waiting.",
    "git_ceremony": "Git status/diff/log rituals can usually be collapsed.",
    "failed_tools": "Retries after preventable tool failures consume full extra turns.",
    "toolsearch": "Discovery hops add turn cost before the useful action happens.",
    "heartbeat_idle": "Wakeups with no useful action still reread the same workspace.",
    "workspace_bloat": "Large personality or rule files add fixed tax to every turn.",
    "memory_accumulation": "Long-lived sessions keep carrying old state with them.",
}

NEXT_ACTION_HINTS = {
    "idle_narration": "Start with the no-narration, think-and-act rules.",
    "context_rot": "Add guidance to keep long threads compact and avoid dragging stale context forward.",
    "pingpong_debugging": "Add the stop-read-think-single-fix rule after repeated failures.",
    "verbose_output": "Redirect noisy commands to temp files and tail only the useful ending.",
    "codebase_wandering": "Add a project map and focused exploration rules.",
    "chainable_bash": "Batch independent shell commands with && when it is safe.",
    "unbatched_edits": "Encourage batching related edits into the same turn.",
    "duplicate_reads": "Tell the agent not to re-read unchanged files already in context.",
    "sleep_poll_loops": "Prefer wait flags or background execution over sleep/poll loops.",
    "git_ceremony": "Collapse git ceremony into denser chained commands.",
    "failed_tools": "Add guardrails for the most common tool failures before retrying.",
    "toolsearch": "Call the right tool directly instead of searching for it first.",
    "heartbeat_idle": "Lower heartbeat frequency and skip empty wakeups.",
    "workspace_bloat": "Compress the instruction file and remove personality filler.",
    "memory_accumulation": "Prune old sessions and compact after long runs.",
}

GOOD_WASTE_THRESHOLD_PCT = 10.0

PRIORITY_LABELS = {
    1: "daily_driver",
    2: "sidekick",
    3: "third_tool",
}


def fmt_currency(amount):
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"


def load_analysis(path):
    if not os.path.exists(path):
        print(f"Error: analysis file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        content = f.read().strip()
    if not content:
        print(f"Error: analysis file is empty: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def sorted_waste_items(waste_breakdown):
    items = []
    for key, info in waste_breakdown.items():
        items.append((key, info))
    return sorted(
        items,
        key=lambda item: (
            item[1].get("per_session", 0),
            item[1].get("total_cost", 0),
        ),
        reverse=True,
    )


def build_headline(summary, top_patterns):
    if top_patterns:
        top = top_patterns[0]
        return (
            f"{top['label']} is your biggest drag "
            f"- fixing it would save about {top['cost_display']}."
        )

    waste_pct = summary.get("waste_percentage", 0)
    avg_cost = summary.get("avg_cost_per_session", 0)
    return (
        f"Your scan looks fairly tight already "
        f"- about {waste_pct:.1f}% of the average {fmt_currency(avg_cost)} session still looks recoverable."
    )


def build_next_action(top_patterns, instruction_file_name, optimization_plan=None):
    if top_patterns:
        top = top_patterns[0]
        if instruction_file_name:
            title = f"Tighten {instruction_file_name}"
            body = (
                f"{NEXT_ACTION_HINTS.get(top['key'], 'Start with the highest-impact fix block first.')} "
                f"That is the cleanest first move before re-running /vibecheck scan."
            )
        else:
            title = "Start with the first fix"
            body = (
                f"{NEXT_ACTION_HINTS.get(top['key'], 'Start with the highest-impact fix block first.')} "
                f"Then re-run /vibecheck scan after the change lands."
            )
    else:
        if instruction_file_name:
            title = f"Polish {instruction_file_name}"
            body = (
                f"Use the instruction-file optimization and compression flow for {instruction_file_name}; "
                "that is where the remaining gains are likely to come from."
            )
        else:
            title = "Run the polish pass"
            body = "Use the instruction-file optimization and compression flow to squeeze out the remaining waste."

    result = {
        "title": title,
        "body": body,
        "instruction_file": instruction_file_name,
    }
    entry_tool_id = (optimization_plan or {}).get("entry_tool_id")
    tools = {tool.get("tool_id"): tool for tool in (optimization_plan or {}).get("tools", [])}
    entry_tool = tools.get(entry_tool_id)
    first_step = entry_tool.get("steps", [None])[0] if entry_tool else None
    if entry_tool_id and first_step:
        result["command"] = f"python3 SKILL_DIR/scripts/present_next_workflow_item.py /tmp/vibecheck_result.json {entry_tool_id}"
        result["workflow"] = {
            "tool_id": entry_tool_id,
            "step_rank": first_step.get("rank"),
        }
    return result


def build_empty_state(instruction_file_name):
    if instruction_file_name:
        next_action = {
            "title": f"Check {instruction_file_name} first",
            "body": (
                f"I could not find enough recent session data yet, so the best next move is to tighten "
                f"{instruction_file_name} and then re-run /vibecheck scan once more logs exist."
            ),
            "instruction_file": instruction_file_name,
        }
    else:
        next_action = {
            "title": "Run scan again after more activity",
            "body": "I could not find enough recent session data yet. Re-run /vibecheck scan after a few real sessions or export recent logs.",
            "instruction_file": None,
        }

    summary_metrics = [
        {"id": SUMMARY_METRIC_IDS[0], "label": "Sessions scanned", "value": "0"},
        {"id": SUMMARY_METRIC_IDS[1], "label": "Avg cost/session", "value": "$0.000"},
        {"id": SUMMARY_METRIC_IDS[2], "label": "Waste", "value": "0.0%"},
    ]

    return {
        "visibility": "result",
        "kind": PAYLOAD_KINDS["result"],
        "run_state": {
            "state": "completed",
            "resultPayload": PAYLOAD_KINDS["result"],
        },
        "hero": {
            "eyebrow": "Scan ready",
            "headline": "I could not find enough recent sessions to score yet.",
            "supporting_text": "This result is intentionally calm and sparse so the UI can render a clean empty state instead of noisy internals.",
        },
        "headline": "I could not find enough recent sessions to score yet.",
        "summary": {
            "sessions_analyzed": 0,
            "avg_cost_per_session": 0,
            "waste_percentage": 0,
        },
        "summary_metrics": summary_metrics,
        "top_waste_patterns": [],
        "next_action": next_action,
        "sections": [
            {"id": "hero", "kind": EMPTY_RESULT_SECTION_KINDS[0]},
            {"id": "summary_metrics", "kind": EMPTY_RESULT_SECTION_KINDS[1]},
            {"id": "next_action", "kind": EMPTY_RESULT_SECTION_KINDS[2]},
        ],
        "education_bridge": "Lead with this summary first. Teach methodology only after the user has seen the findings.",
    }


def build_detected_tool_inventory(data):
    tool_inventory = data.get("tool_inventory")
    if tool_inventory:
        return tool_inventory

    tool_mix = data.get("tool_mix", {})
    installed_tools = data.get("installed_tools", [])
    unsupported_tools = {item.get("id"): item for item in data.get("unsupported_tools", []) if item.get("id")}
    skipped_tools = {item.get("tool_id"): item for item in data.get("skipped_tools", []) if item.get("tool_id")}
    failed_tools = {item.get("tool_id"): item for item in data.get("failed_tools", []) if item.get("tool_id")}
    instruction_targets = data.get("instruction_targets", [])
    optimization_targets = data.get("optimization_targets", instruction_targets)

    instruction_counts = {}
    for target in instruction_targets:
        tool_id = target.get("tool")
        if tool_id:
            instruction_counts[tool_id] = instruction_counts.get(tool_id, 0) + 1

    optimization_counts = {}
    for target in optimization_targets:
        tool_id = target.get("tool")
        if tool_id:
            optimization_counts[tool_id] = optimization_counts.get(tool_id, 0) + 1

    ordered_ids = []
    for tool in installed_tools:
        tool_id = tool.get("id")
        if tool_id and tool_id not in ordered_ids:
            ordered_ids.append(tool_id)
    for tool_id in tool_mix:
        if tool_id not in ordered_ids:
            ordered_ids.append(tool_id)

    inventory = []
    for tool_id in ordered_ids:
        installed = next((tool for tool in installed_tools if tool.get("id") == tool_id), {})
        info = tool_mix.get(tool_id, {})
        status = "detected"
        if info:
            status = "scanned"
        elif tool_id in failed_tools:
            status = "failed"
        elif tool_id in skipped_tools:
            status = "skipped"
        elif tool_id in unsupported_tools or installed.get("can_analyze") is False:
            status = "unsupported"

        item = {
            "id": tool_id,
            "name": installed.get("name") or info.get("name") or unsupported_tools.get(tool_id, {}).get("name") or skipped_tools.get(tool_id, {}).get("tool_name") or failed_tools.get(tool_id, {}).get("tool_name") or tool_id,
            "status": status,
            "support_level": installed.get("support_level") or unsupported_tools.get(tool_id, {}).get("support_level"),
            "analysis_mode": installed.get("analysis_mode") or info.get("analysis_mode"),
            "sessions": info.get("sessions", 0),
            "total_cost": info.get("total_cost", 0),
            "waste_pct": info.get("waste_pct", 0),
            "instruction_targets": instruction_counts.get(tool_id, 0),
            "optimization_targets": optimization_counts.get(tool_id, 0),
        }
        if tool_id in skipped_tools:
            item["skip_reason"] = skipped_tools[tool_id].get("reason")
        if tool_id in failed_tools:
            item["failure_stage"] = failed_tools[tool_id].get("stage")
        inventory.append(item)

    if inventory:
        return inventory

    summary = data.get("summary", {})
    sessions = summary.get("sessions", summary.get("total_sessions", 0))
    if sessions:
        return [
            {
                "id": data.get("scan_tool_id", "current_tool"),
                "name": data.get("scan_tool_name", "Current tool"),
                "status": "scanned",
                "support_level": "full",
                "analysis_mode": data.get("scan_analysis_mode", "current"),
                "sessions": sessions,
                "total_cost": summary.get("total_cost", 0),
                "waste_pct": summary.get("waste_percentage", 0),
                "instruction_targets": len(instruction_targets),
                "optimization_targets": len(optimization_targets),
                "log_count": sessions,
            }
        ]

    return inventory


def build_optimization_targets(data, instruction_file_path=None, detected_tools=None):
    targets = data.get("optimization_targets", data.get("instruction_targets", []))
    output = []
    for target in targets:
        output.append(
            {
                "tool": target.get("tool"),
                "label": target.get("tool_name", target.get("tool")),
                "path": target.get("file"),
                "filename": target.get("filename"),
                "kind": target.get("kind", "instruction_file"),
                "scope": target.get("scope", "project"),
                "exists": target.get("exists", True),
                "action": target.get("action", "update"),
                "priority_band": target.get("priority_band", "primary"),
                "source": target.get("source", "project_instruction"),
            }
        )
    if output or not instruction_file_path:
        return output

    tool_mix = data.get("tool_mix", {})
    candidate_tool_id = None
    candidate_label = None
    if len(tool_mix) == 1:
        candidate_tool_id, info = next(iter(tool_mix.items()))
        candidate_label = info.get("name", candidate_tool_id)
    elif data.get("scan_tool_id"):
        candidate_tool_id = data.get("scan_tool_id")
        candidate_label = data.get("scan_tool_name", candidate_tool_id)
    elif detected_tools and len(detected_tools) == 1:
        candidate_tool_id = detected_tools[0].get("id")
        candidate_label = detected_tools[0].get("name", candidate_tool_id)

    if candidate_tool_id:
        path = str(instruction_file_path)
        output.append(
            {
                "tool": candidate_tool_id,
                "label": candidate_label or candidate_tool_id,
                "path": path,
                "filename": Path(path).name,
                "kind": "instruction_file",
                "scope": "project",
                "exists": Path(path).exists(),
                "action": "update",
                "priority_band": "fallback",
                "source": "present_scan_fallback",
            }
        )
    return output


def build_health(waste_ratio_pct, measured=True):
    if not measured:
        return {
            "id": "unavailable",
            "label": "Unavailable",
            "emoji": "➖",
            "threshold_pct": GOOD_WASTE_THRESHOLD_PCT,
            "waste_ratio_pct": None,
        }

    rounded = round(waste_ratio_pct or 0, 1)
    if rounded > GOOD_WASTE_THRESHOLD_PCT:
        return {
            "id": "waste",
            "label": "Waste",
            "emoji": "❌",
            "threshold_pct": GOOD_WASTE_THRESHOLD_PCT,
            "waste_ratio_pct": rounded,
        }
    return {
        "id": "good",
        "label": "Good",
        "emoji": "✅",
        "threshold_pct": GOOD_WASTE_THRESHOLD_PCT,
        "waste_ratio_pct": rounded,
    }


def avg_or_none(values, digits=1):
    items = [value for value in values if isinstance(value, (int, float))]
    if not items:
        return None
    return round(sum(items) / len(items), digits)


def parse_iso_timestamp(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def infer_period_days(summary, sessions):
    seen_dates = sorted({session.get("date") for session in sessions if session.get("date")})
    if seen_dates:
        return max(1, len(seen_dates))

    date_range = summary.get("date_range")
    if isinstance(date_range, str) and " to " in date_range:
        left, right = date_range.split(" to ", 1)
        try:
            start = datetime.strptime(left, "%Y-%m-%d").date()
            end = datetime.strptime(right, "%Y-%m-%d").date()
            return max(1, (end - start).days + 1)
        except ValueError:
            return 1
    return 1


def monthly_savings_from_total(total_cost, period_days):
    if period_days <= 0:
        return 0
    return round(total_cost / period_days * 30, 2)


def compute_session_waste_total(session):
    return round(
        sum(info.get("cost", 0) for info in session.get("waste", {}).values() if isinstance(info, dict)),
        4,
    )


def aggregate_pattern_totals(sessions):
    totals = defaultdict(float)
    descriptions = {}
    for session in sessions:
        for key, info in session.get("waste", {}).items():
            if not isinstance(info, dict):
                continue
            totals[key] += info.get("cost", 0)
            if key not in descriptions and info.get("description"):
                descriptions[key] = info.get("description")
    return totals, descriptions


def build_top_area_list(pattern_totals, descriptions, total_sessions, avg_cost_per_session, limit=3):
    if total_sessions <= 0:
        return []

    areas = []
    for key, total_cost in sorted(pattern_totals.items(), key=lambda item: item[1], reverse=True):
        if total_cost <= 0:
            continue
        cost_per_session = total_cost / total_sessions
        waste_ratio_pct = min(100.0, round(cost_per_session / avg_cost_per_session * 100, 1)) if avg_cost_per_session else 0
        areas.append(
            {
                "key": key,
                "label": WASTE_LABELS.get(key, key.replace("_", " ").title()),
                "cost_per_session": round(cost_per_session, 4),
                "cost_display": f"{fmt_currency(cost_per_session)}/session",
                "waste_ratio_pct": waste_ratio_pct,
                "health": build_health(waste_ratio_pct),
                "summary": WASTE_SUMMARIES.get(key, descriptions.get(key, "")),
            }
        )
        if len(areas) == limit:
            break
    return areas


def tool_priority_sort_key(item):
    sessions = item.get("sessions", 0)
    log_count = item.get("log_count", 0)
    total_cost = item.get("total_cost", 0)
    return (-sessions, -log_count, -total_cost, item.get("name", ""))


def build_tool_ranked_list(detected_tools):
    ordered = sorted(detected_tools, key=tool_priority_sort_key)
    for idx, item in enumerate(ordered, start=1):
        item["rank"] = idx
        item["priority_label"] = PRIORITY_LABELS.get(idx, "later_tool")
    return ordered


def duration_availability(values, total_items):
    available = len([value for value in values if isinstance(value, (int, float))])
    if available == 0:
        return "unavailable"
    if available == total_items:
        return "all_tools"
    return "partial"


def build_duration_notes(sessions):
    log_values = [session.get("duration_minutes") for session in sessions]
    active_values = [session.get("active_session_duration_minutes") for session in sessions]
    total_items = len(sessions)
    return {
        "log_session_duration": {
            "label": "Log session duration",
            "availability": duration_availability(log_values, total_items),
            "description": "Directly from log timestamps. Useful for session span, but noisy if the session sat open while you were away.",
        },
        "active_session_duration": {
            "label": "Active session duration",
            "availability": duration_availability(active_values, total_items),
            "description": "Estimated from real activity gaps when the underlying logs provide enough event timestamps.",
        },
    }


def tool_session_filter(session, tool_id, single_tool_id=None):
    source_tool = session.get("source_tool")
    if source_tool:
        return source_tool == tool_id
    return single_tool_id == tool_id


def build_header_statistics(summary, detected_tools, sessions, model_mix, top_patterns):
    period_days = infer_period_days(summary, sessions)
    ranked_tools = build_tool_ranked_list([dict(item) for item in detected_tools])
    single_tool_id = ranked_tools[0]["id"] if len([item for item in ranked_tools if item.get("sessions", 0) > 0]) == 1 else None
    overall_areas = []
    for item in top_patterns:
        overall_areas.append(
            {
                "key": item["key"],
                "label": item["label"],
                "cost_per_session": item["cost_per_session"],
                "cost_display": item["cost_display"],
                "waste_ratio_pct": round(item["cost_per_session"] / summary.get("avg_cost_per_session", 0) * 100, 1) if summary.get("avg_cost_per_session", 0) else 0,
                "health": build_health(round(item["cost_per_session"] / summary.get("avg_cost_per_session", 0) * 100, 1) if summary.get("avg_cost_per_session", 0) else 0),
                "summary": item["summary"],
            }
        )

    tool_stats = []
    for item in ranked_tools:
        tool_id = item["id"]
        tool_sessions = [session for session in sessions if tool_session_filter(session, tool_id, single_tool_id)]
        tool_session_count = len(tool_sessions)
        avg_cost = round(sum(session.get("total_cost", 0) for session in tool_sessions) / tool_session_count, 2) if tool_session_count else 0
        pattern_totals, descriptions = aggregate_pattern_totals(tool_sessions)
        waste_ratio_pct = round(item.get("waste_pct", 0), 1) if item.get("sessions", 0) else round(min(100.0, sum(pattern_totals.values()) / sum(session.get("total_cost", 0) for session in tool_sessions) * 100), 1) if tool_session_count and sum(session.get("total_cost", 0) for session in tool_sessions) else item.get("waste_pct", 0)
        projected_avg = round(max(avg_cost * (1 - waste_ratio_pct / 100), 0), 2) if tool_session_count else 0
        projected_monthly = round(avg_cost * tool_session_count / period_days * 30 * (waste_ratio_pct / 100), 2) if tool_session_count else 0
        tool_stats.append(
            {
                "id": tool_id,
                "label": item.get("name", tool_id),
                "rank": item["rank"],
                "priority_label": item["priority_label"],
                "scan_status": item.get("status"),
                "health": build_health(waste_ratio_pct, measured=tool_session_count > 0),
                "sessions": tool_session_count or item.get("sessions", 0),
                "log_count": item.get("log_count", 0),
                "avg_cost_per_session": avg_cost if tool_session_count else round(item.get("total_cost", 0) / item.get("sessions", 1), 2) if item.get("sessions", 0) else 0,
                "avg_turns_per_session": avg_or_none([session.get("total_turns") for session in tool_sessions], digits=1) if tool_session_count else 0,
                "avg_session_duration_minutes": avg_or_none([session.get("duration_minutes") for session in tool_sessions], digits=1),
                "avg_active_session_duration_minutes": avg_or_none([session.get("active_session_duration_minutes") for session in tool_sessions], digits=1),
                "avg_start_context_window_tokens": avg_or_none([session.get("start_context_window_tokens") for session in tool_sessions], digits=0),
                "avg_end_context_window_tokens": avg_or_none([session.get("end_context_window_tokens") for session in tool_sessions], digits=0),
                "avg_waste_ratio_pct": waste_ratio_pct,
                "big_3_waste_areas": build_top_area_list(pattern_totals, descriptions, tool_session_count, avg_cost, limit=3),
                "projected_avg_cost_per_session": projected_avg,
                "projected_monthly_savings": projected_monthly,
            }
        )

    model_stats = []
    model_ids = sorted(model_mix.keys(), key=lambda model: (-model_mix[model].get("sessions", 0), -model_mix[model].get("total_cost", 0), model))
    for model_id in model_ids:
        info = model_mix[model_id]
        model_sessions = [session for session in sessions if session.get("model") == model_id]
        model_count = len(model_sessions)
        pattern_totals, descriptions = aggregate_pattern_totals(model_sessions)
        total_waste = round(sum(pattern_totals.values()), 4)
        avg_cost = info.get("avg_cost", 0)
        waste_ratio_pct = min(100.0, round(total_waste / sum(session.get("total_cost", 0) for session in model_sessions) * 100, 1)) if model_sessions and sum(session.get("total_cost", 0) for session in model_sessions) else info.get("waste_pct", 0)
        model_stats.append(
            {
                "id": model_id,
                "label": model_id,
                "health": build_health(waste_ratio_pct, measured=model_count > 0),
                "sessions": info.get("sessions", 0),
                "avg_cost_per_session": avg_cost,
                "avg_turns_per_session": info.get("avg_turns", 0),
                "avg_session_duration_minutes": avg_or_none([session.get("duration_minutes") for session in model_sessions], digits=1),
                "avg_active_session_duration_minutes": avg_or_none([session.get("active_session_duration_minutes") for session in model_sessions], digits=1),
                "avg_start_context_window_tokens": avg_or_none([session.get("start_context_window_tokens") for session in model_sessions], digits=0),
                "avg_end_context_window_tokens": avg_or_none([session.get("end_context_window_tokens") for session in model_sessions], digits=0),
                "avg_waste_ratio_pct": waste_ratio_pct,
                "big_3_waste_areas": build_top_area_list(pattern_totals, descriptions, model_count, avg_cost, limit=3),
            }
        )

    sessions_present = summary.get("sessions", summary.get("total_sessions", 0)) > 0
    overall = {
        "health": build_health(summary.get("waste_percentage", 0), measured=sessions_present),
        "avg_cost_per_session": summary.get("avg_cost_per_session", 0),
        "avg_turns_per_session": summary.get("avg_turns_per_session", 0),
        "avg_session_duration_minutes": avg_or_none([session.get("duration_minutes") for session in sessions], digits=1),
        "avg_active_session_duration_minutes": avg_or_none([session.get("active_session_duration_minutes") for session in sessions], digits=1),
        "avg_start_context_window_tokens": avg_or_none([session.get("start_context_window_tokens") for session in sessions], digits=0),
        "avg_end_context_window_tokens": avg_or_none([session.get("end_context_window_tokens") for session in sessions], digits=0),
        "avg_waste_ratio_pct": summary.get("waste_percentage", 0),
        "big_3_waste_areas": overall_areas,
    }
    if not sessions_present:
        overall["health"] = build_health(0, measured=False)

    return {
        "overall": overall,
        "tools": tool_stats,
        "models": model_stats,
    }


def build_tool_optimization_steps(tool_label, tool_id, tool_sessions, avg_cost_per_session, tool_targets, period_days, target_strategy):
    total_sessions = len(tool_sessions)
    pattern_totals, descriptions = aggregate_pattern_totals(tool_sessions)
    top_areas = build_top_area_list(pattern_totals, descriptions, total_sessions, avg_cost_per_session, limit=3)
    effective_targets = target_strategy.get("effective_targets", [])
    fallback_targets = target_strategy.get("fallback_targets", [])
    if not effective_targets:
        return []
    steps = []
    for idx, area in enumerate(top_areas, start=1):
        monthly = monthly_savings_from_total(area["cost_per_session"] * total_sessions, period_days)
        steps.append(
            {
                "id": f"{tool_id}-step-{idx}",
                "rank": idx,
                "title": area["label"],
                "health": area["health"],
                "waste_ratio_pct": area["waste_ratio_pct"],
                "projected_savings_per_session": area["cost_per_session"],
                "projected_monthly_savings": monthly,
                "patterns": [
                    {
                        "key": area["key"],
                        "label": area["label"],
                        "cost_per_session": area["cost_per_session"],
                        "waste_ratio_pct": area["waste_ratio_pct"],
                    }
                ],
                "facts": [
                    {"label": "Avg cost/session", "value": fmt_currency(avg_cost_per_session)},
                    {"label": "Avg turns/session", "value": f"{avg_or_none([session.get('total_turns') for session in tool_sessions], digits=1) or 0:.1f}"},
                    {"label": "Waste ratio", "value": f"{area['waste_ratio_pct']:.1f}%"},
                ],
                "explanation": {
                    "summary": area["summary"],
                    "why_it_matters": f"On {tool_label}, this area accounts for about {area['waste_ratio_pct']:.1f}% of the average session spend and should be handled before lower-impact cleanup.",
                },
                "approval_required": True,
                "target_files": effective_targets,
                "target_strategy": {
                    "mode": target_strategy.get("mode"),
                    "summary": target_strategy.get("summary"),
                    "fallback_target_count": len(fallback_targets),
                },
            }
        )

    if len(steps) < 4 and effective_targets:
        steps.append(
            {
                "id": f"{tool_id}-step-{len(steps) + 1}",
                "rank": len(steps) + 1,
                "title": "Instruction and settings cleanup",
                "health": build_health(sum(step["waste_ratio_pct"] for step in steps), measured=bool(steps)),
                "waste_ratio_pct": round(sum(step["waste_ratio_pct"] for step in steps), 1) if steps else 0,
                "projected_savings_per_session": 0,
                "projected_monthly_savings": 0,
                "patterns": [],
                "facts": [
                    {"label": "Targets", "value": str(len(tool_targets))},
                    {"label": "Scope", "value": ", ".join(sorted({target.get('scope', 'project') for target in tool_targets}))},
                ],
                "explanation": {
                    "summary": "This step is where the approved rules and cleanup changes get written into the tool's instruction or settings files.",
                    "why_it_matters": f"It keeps the optimization durable for {tool_label} instead of relying on one-off habits.",
                },
                "approval_required": True,
                "target_files": effective_targets,
                "target_strategy": {
                    "mode": target_strategy.get("mode"),
                    "summary": target_strategy.get("summary"),
                    "fallback_target_count": len(fallback_targets),
                },
            }
        )

    return steps


def build_target_strategy(tool_targets):
    primary_targets = [target for target in tool_targets if target.get("priority_band") == "primary"]
    secondary_targets = [target for target in tool_targets if target.get("priority_band") == "secondary"]
    fallback_targets = [target for target in tool_targets if target.get("priority_band") == "fallback"]
    effective_primary_targets = actionable_targets(primary_targets)
    effective_secondary_targets = actionable_targets(secondary_targets)
    effective_fallback_targets = actionable_targets(fallback_targets)
    effective_targets = effective_primary_targets or effective_secondary_targets or effective_fallback_targets

    global_primary = [
        target for target in effective_primary_targets
        if target.get("scope") == "global" and target.get("kind") == "instruction_file"
    ]
    global_secondary = [
        target for target in effective_secondary_targets
        if target.get("scope") == "global" and target.get("kind") == "instruction_file"
    ]

    if global_primary:
        mode = "global_first"
        summary = "Start with one machine-wide instruction change, then touch project files only if a repo needs an exception."
    elif global_secondary:
        mode = "global_settings_first"
        summary = "Start with machine-wide settings, then use project files only for tool-specific gaps."
    elif effective_targets:
        mode = "project_only"
        summary = "This tool does not expose a reliable machine-wide instruction surface, so optimization stays project-local."
    else:
        mode = "no_targets"
        summary = "No writable optimization targets were detected for this tool yet."

    return {
        "mode": mode,
        "summary": summary,
        "preferred_scope": "global" if mode in {"global_first", "global_settings_first"} else "project",
        "primary_targets": primary_targets,
        "secondary_targets": secondary_targets,
        "fallback_targets": fallback_targets,
        "effective_targets": effective_targets,
        "counts": {
            "primary": len(primary_targets),
            "secondary": len(secondary_targets),
            "fallback": len(fallback_targets),
            "effective": len(effective_targets),
        },
    }


def build_optimization_plan(header_statistics, optimization_target_list, sessions):
    period_days = infer_period_days({"date_range": None}, sessions)
    tools = []
    target_map = defaultdict(list)
    for target in optimization_target_list:
        target_map[target.get("tool")].append(target)

    for tool in header_statistics.get("tools", []):
        tool_id = tool["id"]
        tool_sessions = [session for session in sessions if session.get("source_tool") == tool_id or (not session.get("source_tool") and len(header_statistics.get("tools", [])) == 1)]
        current_avg = tool.get("avg_cost_per_session", 0)
        tool_targets = target_map.get(tool_id, [])
        target_strategy = build_target_strategy(tool_targets)
        steps = build_tool_optimization_steps(
            tool.get("label", tool_id),
            tool_id,
            tool_sessions,
            current_avg,
            tool_targets,
            period_days,
            target_strategy,
        )
        planned_savings_per_session = round(sum(step.get("projected_savings_per_session", 0) for step in steps), 3)
        planned_monthly = round(sum(step.get("projected_monthly_savings", 0) for step in steps), 2)
        planned_waste_ratio = round(sum(step.get("waste_ratio_pct", 0) for step in steps), 1)
        tools.append(
            {
                "tool_id": tool_id,
                "tool_label": tool.get("label", tool_id),
                "priority_rank": tool.get("rank"),
                "priority_label": tool.get("priority_label"),
                "scan_status": tool.get("scan_status"),
                "health": tool.get("health"),
                "before_after": {
                    "current_avg_cost_per_session": current_avg,
                    "projected_avg_cost_per_session": round(max(current_avg - planned_savings_per_session, 0), 2) if tool_sessions else current_avg,
                    "projected_monthly_savings": planned_monthly if tool_sessions else 0,
                    "waste_ratio_pct": planned_waste_ratio,
                },
                "key_statistics": {
                    "avg_turns_per_session": tool.get("avg_turns_per_session"),
                    "avg_session_duration_minutes": tool.get("avg_session_duration_minutes"),
                    "avg_active_session_duration_minutes": tool.get("avg_active_session_duration_minutes"),
                    "avg_start_context_window_tokens": tool.get("avg_start_context_window_tokens"),
                    "avg_end_context_window_tokens": tool.get("avg_end_context_window_tokens"),
                    "big_3_waste_areas": tool.get("big_3_waste_areas", []),
                },
                "optimization_strategy": target_strategy,
                "steps": steps,
                "can_auto_optimize": bool(target_strategy.get("effective_targets")),
                "next_tool_id": None,
            }
        )

    actionable_tools = [tool for tool in tools if tool.get("can_auto_optimize") and tool.get("steps")]
    for idx, tool in enumerate(actionable_tools[:-1]):
        tool["next_tool_id"] = actionable_tools[idx + 1]["tool_id"]

    return {
        "thresholds": {
            "good_max_waste_pct": GOOD_WASTE_THRESHOLD_PCT,
        },
        "tool_sequence": [tool["tool_id"] for tool in actionable_tools],
        "entry_tool_id": actionable_tools[0]["tool_id"] if actionable_tools else None,
        "tools": tools,
    }


def build_payload(data, instruction_file_path=None):
    summary = data.get("summary", {})
    waste_breakdown = data.get("waste_breakdown", {})
    sessions = data.get("sessions", [])
    sessions_analyzed = summary.get("sessions", summary.get("total_sessions", 0))
    tool_mix = data.get("tool_mix", {})
    provider_mix = data.get("provider_mix", {})
    model_mix = data.get("model_mix", {})
    platform_mix = data.get("platform_mix", {})
    instruction_targets = data.get("instruction_targets", [])
    optimization_targets = data.get("optimization_targets", instruction_targets)
    installed_tools = data.get("installed_tools", [])
    unsupported_tools = data.get("unsupported_tools", [])
    skipped_tools = data.get("skipped_tools", [])
    failed_tools = data.get("failed_tools", [])
    detected_tools = build_detected_tool_inventory(data)
    optimization_target_list = build_optimization_targets(data, instruction_file_path, detected_tools)
    preferred_instruction_target = next(
        (
            target for target in optimization_target_list
            if target.get("kind") == "instruction_file" and target.get("priority_band") == "primary"
        ),
        None,
    )
    instruction_file_name = (
        Path(instruction_file_path).name
        if instruction_file_path
        else preferred_instruction_target.get("filename") if preferred_instruction_target else None
    )

    if not sessions_analyzed:
        payload = build_empty_state(instruction_file_name)
        payload["unified_scan"] = {
            "mode": data.get("scan_scope", {}).get("mode", "single_tool"),
            "tools_scanned": data.get("summary", {}).get("tools_scanned", 0),
            "tools_detected": len(installed_tools) or len(detected_tools),
            "tools_unsupported": len(unsupported_tools),
            "tools_skipped": len(skipped_tools),
            "tools_failed": len(failed_tools),
            "instruction_targets": len(instruction_targets),
            "optimization_targets": len(optimization_targets),
        }
        payload["coverage"] = {
            "detected_tools": [
                {
                    "id": item.get("id"),
                    "label": item.get("name", item.get("id")),
                    "status": item.get("status"),
                    "support_level": item.get("support_level"),
                    "analysis_mode": item.get("analysis_mode"),
                    "instruction_targets": item.get("instruction_targets", 0),
                    "optimization_targets": item.get("optimization_targets", 0),
                }
                for item in detected_tools
            ],
            "unsupported_tools": [
                {
                    "id": item.get("id"),
                    "label": item.get("name", item.get("id")),
                    "support_level": item.get("support_level"),
                }
                for item in unsupported_tools
            ],
            "skipped_tools": [
                {
                    "id": item.get("tool_id"),
                    "label": item.get("tool_name", item.get("tool_id")),
                    "reason": item.get("reason"),
                }
                for item in skipped_tools
            ],
            "failed_tools": [
                {
                    "id": item.get("tool_id"),
                    "label": item.get("tool_name", item.get("tool_id")),
                    "stage": item.get("stage"),
                }
                for item in failed_tools
            ],
        }
        payload["optimization_targets"] = optimization_target_list
        payload["header_statistics"] = {
            "overall": {
                "health": build_health(0, measured=False),
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "avg_session_duration_minutes": None,
                "avg_active_session_duration_minutes": None,
                "avg_start_context_window_tokens": None,
                "avg_end_context_window_tokens": None,
                "avg_waste_ratio_pct": 0,
                "big_3_waste_areas": [],
            },
            "tools": [],
            "models": [],
        }
        payload["duration_notes"] = build_duration_notes(sessions)
        payload["optimization_plan"] = {
            "thresholds": {"good_max_waste_pct": GOOD_WASTE_THRESHOLD_PCT},
            "tool_sequence": [],
            "tools": [],
        }
        return payload

    tool_breakdown = [
        {
            "id": item.get("id"),
            "label": item.get("name", item.get("id")),
            "status": item.get("status"),
            "support_level": item.get("support_level"),
            "analysis_mode": item.get("analysis_mode"),
            "sessions": item.get("sessions", 0),
            "total_cost": item.get("total_cost", 0),
            "waste_pct": item.get("waste_pct", 0),
            "instruction_targets": item.get("instruction_targets", 0),
            "optimization_targets": item.get("optimization_targets", 0),
        }
        for item in detected_tools
    ]
    provider_breakdown = [
        {
            "id": provider,
            "label": provider,
            "sessions": info.get("sessions", 0),
            "total_cost": info.get("total_cost", 0),
        }
        for provider, info in sorted(provider_mix.items(), key=lambda item: item[1].get("total_cost", 0), reverse=True)
    ]
    model_breakdown = [
        {
            "id": model,
            "label": model,
            "sessions": info.get("sessions", 0),
            "total_cost": info.get("total_cost", 0),
        }
        for model, info in sorted(model_mix.items(), key=lambda item: item[1].get("total_cost", 0), reverse=True)
    ]
    platform_breakdown = [
        {
            "id": platform,
            "label": platform,
            "sessions": info.get("sessions", 0),
            "total_cost": info.get("total_cost", 0),
            "waste_pct": info.get("waste_pct", 0),
        }
        for platform, info in sorted(platform_mix.items(), key=lambda item: item[1].get("total_cost", 0), reverse=True)
    ]

    top_patterns = []
    for key, info in sorted_waste_items(waste_breakdown):
        per_session = info.get("per_session", 0)
        if per_session <= 0:
            continue
        top_patterns.append(
            {
                "key": key,
                "label": WASTE_LABELS.get(key, key.replace("_", " ").title()),
                "cost_per_session": per_session,
                "cost_display": f"{fmt_currency(per_session)}/session",
                "share_of_waste": info.get("percentage_of_waste", 0),
                "summary": WASTE_SUMMARIES.get(key, info.get("description", "")),
            }
        )
        if len(top_patterns) == 3:
            break

    header_statistics = build_header_statistics(summary, detected_tools, sessions, model_mix, top_patterns)
    optimization_plan = build_optimization_plan(header_statistics, optimization_target_list, sessions)
    duration_notes = build_duration_notes(sessions)

    payload = {
        "visibility": "result",
        "kind": PAYLOAD_KINDS["result"],
        "run_state": {
            "state": "completed",
            "resultPayload": PAYLOAD_KINDS["result"],
        },
        "hero": {
            "eyebrow": "Scan complete",
            "headline": build_headline(summary, top_patterns),
            "supporting_text": "Start with the finding, not the methodology. The renderer should make this the primary focal block.",
        },
        "headline": build_headline(summary, top_patterns),
        "summary": {
            "sessions_analyzed": sessions_analyzed,
            "avg_cost_per_session": summary.get("avg_cost_per_session", 0),
            "waste_percentage": summary.get("waste_percentage", 0),
        },
        "summary_metrics": [
            {
                "id": SUMMARY_METRIC_IDS[0],
                "label": "Sessions scanned",
                "value": str(summary.get("sessions", summary.get("total_sessions", 0))),
            },
            {
                "id": SUMMARY_METRIC_IDS[1],
                "label": "Avg cost/session",
                "value": fmt_currency(summary.get("avg_cost_per_session", 0)),
            },
            {
                "id": SUMMARY_METRIC_IDS[2],
                "label": "Waste",
                "value": f"{summary.get('waste_percentage', 0):.1f}%",
            },
        ],
        "top_waste_patterns": top_patterns,
        "next_action": build_next_action(top_patterns, instruction_file_name, optimization_plan),
        "unified_scan": {
            "mode": data.get("scan_scope", {}).get("mode", "single_tool"),
            "tools_scanned": len([item for item in detected_tools if item.get("status") == "scanned"]) or data.get("summary", {}).get("tools_scanned", 0),
            "tools_detected": len(installed_tools) or len(detected_tools),
            "tools_unsupported": len(unsupported_tools),
            "tools_skipped": len(skipped_tools),
            "tools_failed": len(failed_tools),
            "instruction_targets": len(instruction_targets),
            "optimization_targets": len(optimization_targets),
        },
        "breakdowns": {
            "tools": tool_breakdown,
            "providers": provider_breakdown,
            "models": model_breakdown,
            "platforms": platform_breakdown,
        },
        "header_statistics": header_statistics,
        "duration_notes": duration_notes,
        "optimization_plan": optimization_plan,
        "coverage": {
            "detected_tools": [
                {
                    "id": item.get("id"),
                    "label": item.get("name", item.get("id")),
                    "status": item.get("status"),
                    "support_level": item.get("support_level"),
                    "analysis_mode": item.get("analysis_mode"),
                    "instruction_targets": item.get("instruction_targets", 0),
                    "optimization_targets": item.get("optimization_targets", 0),
                }
                for item in detected_tools
            ],
            "unsupported_tools": [
                {
                    "id": item.get("id"),
                    "label": item.get("name", item.get("id")),
                    "support_level": item.get("support_level"),
                }
                for item in unsupported_tools
            ],
            "skipped_tools": [
                {
                    "id": item.get("tool_id"),
                    "label": item.get("tool_name", item.get("tool_id")),
                    "reason": item.get("reason"),
                }
                for item in skipped_tools
            ],
            "failed_tools": [
                {
                    "id": item.get("tool_id"),
                    "label": item.get("tool_name", item.get("tool_id")),
                    "stage": item.get("stage"),
                }
                for item in failed_tools
            ],
        },
        "optimization_targets": optimization_target_list,
        "sections": [
            {"id": "hero", "kind": RESULT_SECTION_KINDS[0]},
            {"id": "summary_metrics", "kind": RESULT_SECTION_KINDS[1]},
            {"id": "header_statistics", "kind": RESULT_SECTION_KINDS[2]},
            {"id": "top_waste_patterns", "kind": RESULT_SECTION_KINDS[3]},
            {"id": "optimization_plan", "kind": RESULT_SECTION_KINDS[4]},
            {"id": "next_action", "kind": RESULT_SECTION_KINDS[5]},
        ],
        "education_bridge": "Lead with this summary first. Teach methodology only after the user has seen the findings.",
    }
    return ensure_execution_state(payload)


def main():
    if len(sys.argv) < 2:
        print("Usage: present_scan.py <analysis.json> [instruction_file_path]", file=sys.stderr)
        sys.exit(1)

    analysis_path = sys.argv[1]
    instruction_file_path = sys.argv[2] if len(sys.argv) > 2 else None
    payload = build_payload(load_analysis(analysis_path), instruction_file_path)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
