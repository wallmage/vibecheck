#!/usr/bin/env python3
"""Merge multiple per-tool vibecheck analyses into one unified analysis."""
import json
import sys
from collections import defaultdict
from pathlib import Path


CONFIDENCE_ORDER = {"estimated": 0, "partial": 1, "measured": 2}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def fmt_date_range(sessions):
    dates = sorted(s.get("date") for s in sessions if s.get("date"))
    if not dates:
        return None
    return f"{dates[0]} to {dates[-1]}"


def merge_confidence(analyses):
    if not analyses:
        return {
            "label": "estimated",
            "score": 0.0,
            "reason": "No analyses were merged.",
        }
    labels = [a.get("analysis_confidence", {}).get("label", "estimated") for a in analyses]
    scores = [a.get("analysis_confidence", {}).get("score", 0.0) for a in analyses]
    if all(label == "measured" for label in labels):
        label = "measured"
    elif any(label in ("measured", "partial") for label in labels):
        label = "partial"
    else:
        label = "estimated"
    return {
        "label": label,
        "score": round(sum(scores) / len(scores), 2),
        "reason": f"Merged {len(analyses)} tool analyses into one machine-wide scan.",
    }


def merge_pricing_metadata(analyses):
    providers = {a.get("pricing_metadata", {}).get("provider", "unknown") for a in analyses}
    registry_versions = {a.get("pricing_metadata", {}).get("registry_version", "unknown") for a in analyses}
    billing_modes = {a.get("pricing_metadata", {}).get("billing_mode", "token_only_estimate") for a in analyses}
    if len(providers) == 1 and len(registry_versions) == 1 and len(billing_modes) == 1:
        return analyses[0].get("pricing_metadata", {}).copy()
    return {
        "registry_version": registry_versions.pop() if len(registry_versions) == 1 else "mixed",
        "registry_label": "Mixed tool pricing inputs",
        "billing_mode": billing_modes.pop() if len(billing_modes) == 1 else "mixed",
        "canonical_model": "multiple",
        "provider": "multi",
    }


def merge_bucket_map(analyses, key):
    merged = defaultdict(lambda: defaultdict(float))
    for analysis in analyses:
        for bucket, info in analysis.get(key, {}).items():
            merged[bucket]["sessions"] += info.get("sessions", 0)
            merged[bucket]["total_cost"] += info.get("total_cost", 0)
            merged[bucket]["avg_turns_weight"] += info.get("avg_turns", 0) * info.get("sessions", 0)
            merged[bucket]["waste_weight"] += info.get("waste_pct", 0) * info.get("sessions", 0)

    output = {}
    total_sessions = sum(info["sessions"] for info in merged.values()) or 1
    total_cost = sum(info["total_cost"] for info in merged.values()) or 1
    for bucket, info in sorted(merged.items(), key=lambda item: item[1]["total_cost"], reverse=True):
        sessions = int(info["sessions"])
        bucket_total_cost = round(info["total_cost"], 2)
        output[bucket] = {
            "sessions": sessions,
            "pct_sessions": round(sessions / total_sessions * 100, 1),
            "total_cost": bucket_total_cost,
            "pct_cost": round(bucket_total_cost / total_cost * 100, 1) if total_cost else 0,
            "avg_cost": round(bucket_total_cost / sessions, 2) if sessions else 0,
            "avg_turns": round(info["avg_turns_weight"] / sessions, 1) if sessions else 0,
            "waste_pct": round(info["waste_weight"] / sessions, 1) if sessions else 0,
        }
    return output


def merge_per_project(analyses):
    merged = defaultdict(lambda: defaultdict(float))
    for analysis in analyses:
        for proj, info in analysis.get("per_project", {}).items():
            merged[proj]["sessions"] += info.get("sessions", 0)
            merged[proj]["total_cost"] += info.get("total_cost", 0)
            merged[proj]["avg_turns_weight"] += info.get("avg_turns", 0) * info.get("sessions", 0)
            merged[proj]["waste"] += info.get("waste", 0)
            merged[proj]["waste_weight"] += info.get("waste_pct", 0) * info.get("sessions", 0)

    output = {}
    for proj, info in sorted(merged.items(), key=lambda item: item[1]["total_cost"], reverse=True):
        sessions = int(info["sessions"])
        total_cost = round(info["total_cost"], 2)
        total_waste = round(info["waste"], 2)
        output[proj] = {
            "sessions": sessions,
            "total_cost": total_cost,
            "avg_cost": round(total_cost / sessions, 2) if sessions else 0,
            "avg_turns": round(info["avg_turns_weight"] / sessions, 1) if sessions else 0,
            "waste": total_waste,
            "waste_pct": round(info["waste_weight"] / sessions, 1) if sessions else 0,
        }
    return output


def merge_waste_breakdown(analyses, total_sessions, total_waste):
    merged = defaultdict(lambda: {"total_cost": 0.0, "description": ""})
    for analysis in analyses:
        for key, info in analysis.get("waste_breakdown", {}).items():
            merged[key]["total_cost"] += info.get("total_cost", 0.0)
            if not merged[key]["description"]:
                merged[key]["description"] = info.get("description", "")

    output = {}
    for key, info in merged.items():
        total_cost = round(info["total_cost"], 4)
        output[key] = {
            "total_cost": total_cost,
            "per_session": round(total_cost / total_sessions, 4) if total_sessions else 0,
            "percentage_of_waste": round(total_cost / total_waste * 100, 1) if total_waste else 0,
            "description": info["description"],
        }
    return output


def merge_tool_mix(entries, total_sessions, total_cost):
    output = {}
    for entry in entries:
        analysis = entry["analysis"]
        summary = analysis.get("summary", {})
        sessions = summary.get("sessions", summary.get("total_sessions", 0))
        tool_total_cost = summary.get("total_cost", 0)
        output[entry["tool_id"]] = {
            "name": entry["tool_name"],
            "sessions": sessions,
            "pct_sessions": round(sessions / total_sessions * 100, 1) if total_sessions else 0,
            "total_cost": round(tool_total_cost, 2),
            "pct_cost": round(tool_total_cost / total_cost * 100, 1) if total_cost else 0,
            "avg_cost": round(tool_total_cost / sessions, 2) if sessions else 0,
            "avg_turns": summary.get("avg_turns_per_session", 0),
            "waste_pct": summary.get("waste_percentage", 0),
            "analysis_mode": entry["analysis_mode"],
            "can_analyze": True,
            "instruction_targets": entry.get("instruction_targets", []),
        }
    return output


def merge_provider_mix(analyses):
    merged = defaultdict(lambda: {"sessions": 0, "total_cost": 0.0})
    total_sessions = 0
    total_cost = 0.0
    for analysis in analyses:
        provider = analysis.get("pricing_metadata", {}).get("provider", "unknown")
        sessions = analysis.get("summary", {}).get("sessions", analysis.get("summary", {}).get("total_sessions", 0))
        cost = analysis.get("summary", {}).get("total_cost", 0.0)
        merged[provider]["sessions"] += sessions
        merged[provider]["total_cost"] += cost
        total_sessions += sessions
        total_cost += cost

    output = {}
    for provider, info in sorted(merged.items(), key=lambda item: item[1]["total_cost"], reverse=True):
        output[provider] = {
            "sessions": info["sessions"],
            "pct_sessions": round(info["sessions"] / total_sessions * 100, 1) if total_sessions else 0,
            "total_cost": round(info["total_cost"], 2),
            "pct_cost": round(info["total_cost"] / total_cost * 100, 1) if total_cost else 0,
        }
    return output


def merge_reviewer_roi(analyses):
    sessions_with = sum(a.get("reviewer_roi", {}).get("sessions_with", 0) for a in analyses)
    sessions_without = sum(a.get("reviewer_roi", {}).get("sessions_without", 0) for a in analyses)
    if not sessions_with and not sessions_without:
        return {}
    weighted_with_cost = sum(a.get("reviewer_roi", {}).get("avg_cost_with", 0) * a.get("reviewer_roi", {}).get("sessions_with", 0) for a in analyses)
    weighted_without_cost = sum(a.get("reviewer_roi", {}).get("avg_cost_without", 0) * a.get("reviewer_roi", {}).get("sessions_without", 0) for a in analyses)
    weighted_with_turns = sum(a.get("reviewer_roi", {}).get("avg_turns_with", 0) * a.get("reviewer_roi", {}).get("sessions_with", 0) for a in analyses)
    weighted_without_turns = sum(a.get("reviewer_roi", {}).get("avg_turns_without", 0) * a.get("reviewer_roi", {}).get("sessions_without", 0) for a in analyses)
    reviewer_types_seen = defaultdict(int)
    for analysis in analyses:
        for key, value in analysis.get("reviewer_roi", {}).get("reviewer_types_seen", {}).items():
            reviewer_types_seen[key] += value
    avg_cost_with = weighted_with_cost / sessions_with if sessions_with else 0
    avg_cost_without = weighted_without_cost / sessions_without if sessions_without else 0
    return {
        "sessions_with": sessions_with,
        "sessions_without": sessions_without,
        "avg_cost_with": round(avg_cost_with, 2),
        "avg_cost_without": round(avg_cost_without, 2),
        "marginal_cost": round(avg_cost_with - avg_cost_without, 2),
        "avg_turns_with": round(weighted_with_turns / sessions_with, 1) if sessions_with else 0,
        "avg_turns_without": round(weighted_without_turns / sessions_without, 1) if sessions_without else 0,
        "reviewer_types_seen": dict(sorted(reviewer_types_seen.items())),
    }


def merge_polling_summary(analyses):
    total_turns = sum(a.get("polling_summary", {}).get("total_sleep_poll_turns", 0) for a in analyses)
    total_cost = sum(a.get("polling_summary", {}).get("estimated_cost", 0) for a in analyses)
    total_sessions = sum(a.get("summary", {}).get("sessions", a.get("summary", {}).get("total_sessions", 0)) for a in analyses)
    if not total_turns and not total_cost:
        return {}
    return {
        "total_sleep_poll_turns": total_turns,
        "avg_per_session": round(total_turns / total_sessions, 1) if total_sessions else 0,
        "estimated_cost": round(total_cost, 2),
    }


def merge_targets(entries, key):
    seen = set()
    targets = []
    for entry in entries:
        for target in entry.get(key, []):
            file_key = target.get("file")
            if not file_key or file_key in seen:
                continue
            seen.add(file_key)
            targets.append(target)
    targets.sort(key=lambda item: (item.get("tool_name", ""), item.get("filename", ""), item.get("file", "")))
    return targets


def merge_instruction_targets(entries):
    return merge_targets(entries, "instruction_targets")


def merge_optimization_targets(entries):
    return merge_targets(entries, "optimization_targets")


def count_targets_by_tool(targets):
    counts = defaultdict(int)
    for target in targets or []:
        tool_id = target.get("tool")
        if tool_id:
            counts[tool_id] += 1
    return counts


def build_tool_inventory(
    entries,
    installed_tools=None,
    skipped_tools=None,
    failed_tools=None,
    unsupported_tools=None,
    instruction_targets=None,
    optimization_targets=None,
):
    installed_tools = installed_tools or []
    skipped_tools = skipped_tools or []
    failed_tools = failed_tools or []
    unsupported_tools = unsupported_tools or []
    instruction_targets = instruction_targets or []
    optimization_targets = optimization_targets or []

    entry_map = {}
    for entry in entries:
        summary = entry["analysis"].get("summary", {})
        entry_map[entry["tool_id"]] = {
            "id": entry["tool_id"],
            "name": entry["tool_name"],
            "status": "scanned",
            "sessions": summary.get("sessions", summary.get("total_sessions", 0)),
            "total_cost": round(summary.get("total_cost", 0), 2),
            "waste_pct": summary.get("waste_percentage", 0),
            "analysis_mode": entry.get("analysis_mode", "unknown"),
        }

    skipped_map = {item.get("tool_id"): item for item in skipped_tools if item.get("tool_id")}
    failed_map = {item.get("tool_id"): item for item in failed_tools if item.get("tool_id")}
    unsupported_map = {item.get("id"): item for item in unsupported_tools if item.get("id")}
    instruction_counts = count_targets_by_tool(instruction_targets)
    optimization_counts = count_targets_by_tool(optimization_targets)

    tool_ids = []
    for tool in installed_tools:
        tool_id = tool.get("id")
        if tool_id and tool_id not in tool_ids:
            tool_ids.append(tool_id)
    for tool_id in entry_map:
        if tool_id not in tool_ids:
            tool_ids.append(tool_id)

    inventory = []
    for tool_id in tool_ids:
        installed = next((tool for tool in installed_tools if tool.get("id") == tool_id), {})
        scanned = entry_map.get(tool_id)
        skipped = skipped_map.get(tool_id)
        failed = failed_map.get(tool_id)
        unsupported = unsupported_map.get(tool_id)

        status = "detected"
        if scanned:
            status = "scanned"
        elif failed:
            status = "failed"
        elif skipped:
            status = "skipped"
        elif unsupported or installed.get("can_analyze") is False:
            status = "unsupported"

        item = {
            "id": tool_id,
            "name": installed.get("name") or (scanned or {}).get("name") or (unsupported or {}).get("name") or (skipped or {}).get("tool_name") or (failed or {}).get("tool_name") or tool_id,
            "status": status,
            "support_level": installed.get("support_level") or (unsupported or {}).get("support_level") or "unknown",
            "can_analyze": installed.get("can_analyze", status == "scanned"),
            "analysis_mode": installed.get("analysis_mode") or (scanned or {}).get("analysis_mode") or "unknown",
            "log_format": installed.get("log_format"),
            "log_count": installed.get("log_count", 0),
            "support_note": installed.get("support_note"),
            "always_on": installed.get("always_on", False),
            "sessions": (scanned or {}).get("sessions", 0),
            "total_cost": (scanned or {}).get("total_cost", 0),
            "waste_pct": (scanned or {}).get("waste_pct", 0),
            "instruction_targets": instruction_counts.get(tool_id, 0),
            "optimization_targets": optimization_counts.get(tool_id, 0),
        }
        if skipped:
            item["skip_reason"] = skipped.get("reason")
        if failed:
            item["failure_stage"] = failed.get("stage")
        inventory.append(item)

    return inventory


def merge_entries(entries):
    analyses = [entry["analysis"] for entry in entries]
    sessions = []
    for entry in entries:
        for session in entry["analysis"].get("sessions", []):
            item = dict(session)
            item["source_tool"] = entry["tool_id"]
            item["source_tool_name"] = entry["tool_name"]
            item["analysis_mode"] = entry["analysis_mode"]
            sessions.append(item)
    sessions.sort(key=lambda s: s.get("timestamp", ""))

    total_sessions = len(sessions)
    total_cost = round(sum(a.get("summary", {}).get("total_cost", 0) for a in analyses), 2)
    total_turns = sum(a.get("summary", {}).get("total_turns", 0) for a in analyses)
    total_waste = round(sum(a.get("summary", {}).get("total_waste", 0) for a in analyses), 2)
    total_output_tokens = sum(a.get("summary", {}).get("total_output_tokens", 0) for a in analyses)
    total_cache_read = sum(a.get("summary", {}).get("total_cache_read", 0) for a in analyses)
    total_cache_create = sum(a.get("summary", {}).get("total_cache_create", 0) for a in analyses)
    total_agent_spawns = sum(a.get("summary", {}).get("total_agent_spawns", 0) for a in analyses)
    wasteful_turns_total = sum(a.get("summary", {}).get("wasteful_turns_total", 0) for a in analyses)
    context_rot_sessions = sum(a.get("summary", {}).get("context_rot_sessions", 0) for a in analyses)
    projected_cost_after_fix = round(max(0, total_cost - total_waste) / total_sessions, 2) if total_sessions else 0

    avg_cost_per_session = round(total_cost / total_sessions, 2) if total_sessions else 0
    avg_turns_per_session = round(total_turns / total_sessions, 1) if total_sessions else 0
    avg_cost_per_turn = round(total_cost / total_turns, 4) if total_turns else 0
    avg_context_window_tokens = round(sum(a.get("summary", {}).get("avg_context_window_tokens", 0) * a.get("summary", {}).get("sessions", a.get("summary", {}).get("total_sessions", 0)) for a in analyses) / total_sessions) if total_sessions else 0
    avg_output_tokens_per_turn = round(total_output_tokens / total_turns) if total_turns else 0
    waste_per_session = round(total_waste / total_sessions, 4) if total_sessions else 0
    waste_percentage = round(total_waste / total_cost * 100, 1) if total_cost else 0

    instruction_targets = merge_instruction_targets(entries)
    optimization_targets = merge_optimization_targets(entries)

    merged = {
        "summary": {
            "sessions": total_sessions,
            "total_sessions": total_sessions,
            "date_range": fmt_date_range(sessions),
            "total_cost": total_cost,
            "avg_cost_per_session": avg_cost_per_session,
            "avg_turns_per_session": avg_turns_per_session,
            "avg_cost_per_turn": avg_cost_per_turn,
            "total_waste": total_waste,
            "waste_per_session": waste_per_session,
            "waste_percentage": waste_percentage,
            "projected_cost_after_fix": projected_cost_after_fix,
            "avg_context_window_tokens": avg_context_window_tokens,
            "avg_output_tokens_per_turn": avg_output_tokens_per_turn,
            "avg_agent_spawns_per_session": round(total_agent_spawns / total_sessions, 1) if total_sessions else 0,
            "total_agent_spawns": total_agent_spawns,
            "wasteful_turns_total": wasteful_turns_total,
            "wasteful_turns_pct": round(wasteful_turns_total / total_turns * 100, 1) if total_turns else 0,
            "context_rot_sessions": context_rot_sessions,
            "context_rot_pct": round(context_rot_sessions / total_sessions * 100, 1) if total_sessions else 0,
            "total_turns": total_turns,
            "total_output_tokens": total_output_tokens,
            "total_cache_read": total_cache_read,
            "total_cache_create": total_cache_create,
            "tools_scanned": len(entries),
        },
        "waste_breakdown": merge_waste_breakdown(analyses, total_sessions, total_waste),
        "sessions": sessions,
        "analysis_confidence": merge_confidence(analyses),
        "pricing_metadata": merge_pricing_metadata(analyses),
        "tool_mix": merge_tool_mix(entries, total_sessions, total_cost),
        "provider_mix": merge_provider_mix(analyses),
        "model_mix": merge_bucket_map(analyses, "model_mix"),
        "platform_mix": merge_bucket_map(analyses, "platform_mix"),
        "per_project": merge_per_project(analyses),
        "reviewer_roi": merge_reviewer_roi(analyses),
        "polling_summary": merge_polling_summary(analyses),
        "scan_scope": {
            "mode": "all_detected_tools",
            "tool_count": len(entries),
            "tool_ids": [entry["tool_id"] for entry in entries],
            "tool_names": [entry["tool_name"] for entry in entries],
        },
        "instruction_targets": instruction_targets,
        "optimization_targets": optimization_targets,
        "tool_inventory": build_tool_inventory(
            entries,
            instruction_targets=instruction_targets,
            optimization_targets=optimization_targets,
        ),
        "source_analyses": [
            {
                "tool_id": entry["tool_id"],
                "tool_name": entry["tool_name"],
                "analysis_mode": entry["analysis_mode"],
                "sessions": entry["analysis"].get("summary", {}).get("sessions", entry["analysis"].get("summary", {}).get("total_sessions", 0)),
                "total_cost": entry["analysis"].get("summary", {}).get("total_cost", 0),
            }
            for entry in entries
        ],
    }
    return merged


def parse_args(argv):
    entries = []
    for arg in argv:
        if "=" not in arg:
            raise SystemExit("Usage: merge_analyses.py tool_id=analysis.json [tool_id=analysis.json ...]")
        tool_id, path = arg.split("=", 1)
        entries.append((tool_id, path))
    return entries


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: merge_analyses.py tool_id=analysis.json [tool_id=analysis.json ...]")

    entries = []
    for tool_id, path in parse_args(sys.argv[1:]):
        data = load_json(path)
        tool_name = data.get("scan_tool_name") or data.get("source_tool_name") or tool_id
        analysis_mode = data.get("scan_analysis_mode") or "unknown"
        entries.append({
            "tool_id": tool_id,
            "tool_name": tool_name,
            "analysis_mode": analysis_mode,
            "analysis": data,
            "instruction_targets": data.get("instruction_targets", []),
            "optimization_targets": data.get("optimization_targets", []),
        })

    print(json.dumps(merge_entries(entries), indent=2))


if __name__ == "__main__":
    main()
