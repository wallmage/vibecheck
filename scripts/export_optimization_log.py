#!/usr/bin/env python3
"""Export structured scan or optimization payloads to Markdown."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


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
    amount = amount or 0
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"


def fmt_number(value, digits=1):
    if value is None:
        return "—"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if digits == 0:
            return f"{round(value):,}"
        return f"{value:.{digits}f}"
    return str(value)


def markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_target_list(targets):
    if not targets:
        return "_None_"
    lines = []
    for target in targets:
        path = target.get("path") or target.get("file") or ""
        filename = target.get("filename") or Path(path).name or path
        label = target.get("label") or target.get("tool_name") or target.get("tool") or "Tool"
        scope = target.get("scope", "project")
        status = "update" if target.get("exists", True) else "create"
        lines.append(f"- `{filename}` for {label} [{scope}, {status}]")
        if path:
            lines.append(f"  Path: `{path}`")
    return "\n".join(lines)


def render_scan_markdown(payload):
    summary = payload.get("summary", {})
    hero = payload.get("hero", {})
    header_statistics = payload.get("header_statistics", {})
    duration_notes = payload.get("duration_notes", {})
    overall = header_statistics.get("overall", {})
    tools = header_statistics.get("tools", [])
    models = header_statistics.get("models", [])
    plan = payload.get("optimization_plan", {})
    roadmap = plan.get("tools", [])
    total_monthly_savings = sum(
        item.get("before_after", {}).get("projected_monthly_savings", 0)
        for item in roadmap
    )
    projected_avg = round(
        summary.get("avg_cost_per_session", 0) * (1 - summary.get("waste_percentage", 0) / 100),
        2,
    )

    lines = [
        "# VibeCheck Scan Complete",
        "",
        "## Key Insight",
        hero.get("headline", payload.get("headline", "Scan complete.")),
        "",
        "## Snapshot",
        markdown_table(
            ["Metric", "Value"],
            [
                ["Sessions scanned", str(summary.get("sessions_analyzed", 0))],
                ["Overall health", f"{overall.get('health', {}).get('label', 'Unavailable')} {overall.get('health', {}).get('emoji', '➖')}"],
                ["Average cost per session", fmt_currency(summary.get("avg_cost_per_session", 0))],
                ["Average waste ratio", f"{summary.get('waste_percentage', 0):.1f}%"],
                ["Projected average cost after optimization", fmt_currency(projected_avg)],
                ["Projected monthly savings", fmt_currency(total_monthly_savings)],
                ["Average turns per session", fmt_number(overall.get("avg_turns_per_session"), digits=1)],
                ["Log session duration (min)", fmt_number(overall.get("avg_session_duration_minutes"), digits=1)],
                ["Active session duration (min)", fmt_number(overall.get("avg_active_session_duration_minutes"), digits=1)],
                ["Average start context window", fmt_number(overall.get("avg_start_context_window_tokens"), digits=0)],
                ["Average end context window", fmt_number(overall.get("avg_end_context_window_tokens"), digits=0)],
            ],
        ),
        "",
    ]

    if duration_notes:
        lines.extend([
            "## Duration Notes",
            f"- {duration_notes.get('log_session_duration', {}).get('label', 'Log session duration')}: {duration_notes.get('log_session_duration', {}).get('description', '')}",
            f"- {duration_notes.get('active_session_duration', {}).get('label', 'Active session duration')}: {duration_notes.get('active_session_duration', {}).get('description', '')}",
            "",
        ])

    big_3 = overall.get("big_3_waste_areas", []) or payload.get("top_waste_patterns", [])
    if big_3:
        lines.extend([
            "## Biggest Savings Opportunities",
            markdown_table(
                ["Area", "Health", "Waste", "Savings / session", "Why it matters"],
                [
                    [
                        item.get("label", "Area"),
                        f"{item.get('health', {}).get('label', 'Unavailable')} {item.get('health', {}).get('emoji', '➖')}",
                        f"{item.get('waste_ratio_pct', 0):.1f}%",
                        item.get("cost_display", fmt_currency(item.get("cost_per_session", 0))),
                        item.get("summary", ""),
                    ]
                    for item in big_3
                ],
            ),
            "",
        ])

    if tools:
        lines.extend([
            "## Tool Ranking",
            markdown_table(
                [
                    "#",
                    "Tool",
                    "Health",
                    "Sessions",
                    "Avg cost/session",
                    "Avg turns",
                    "Log min",
                    "Active min",
                    "Start ctx",
                    "End ctx",
                    "Waste",
                    "Projected avg",
                    "Projected monthly",
                ],
                [
                    [
                        str(item.get("rank", "")),
                        item.get("label", item.get("id", "")),
                        f"{item.get('health', {}).get('label', 'Unavailable')} {item.get('health', {}).get('emoji', '➖')}",
                        str(item.get("sessions", 0)),
                        fmt_currency(item.get("avg_cost_per_session", 0)),
                        fmt_number(item.get("avg_turns_per_session"), digits=1),
                        fmt_number(item.get("avg_session_duration_minutes"), digits=1),
                        fmt_number(item.get("avg_active_session_duration_minutes"), digits=1),
                        fmt_number(item.get("avg_start_context_window_tokens"), digits=0),
                        fmt_number(item.get("avg_end_context_window_tokens"), digits=0),
                        f"{item.get('avg_waste_ratio_pct', 0):.1f}%",
                        fmt_currency(item.get("projected_avg_cost_per_session", 0)),
                        fmt_currency(item.get("projected_monthly_savings", 0)),
                    ]
                    for item in tools
                ],
            ),
            "",
        ])

    if models:
        lines.extend([
            "## Model Breakdown",
            markdown_table(
                [
                    "Model",
                    "Health",
                    "Sessions",
                    "Avg cost/session",
                    "Avg turns",
                    "Log min",
                    "Active min",
                    "Start ctx",
                    "End ctx",
                    "Waste",
                ],
                [
                    [
                        item.get("label", item.get("id", "")),
                        f"{item.get('health', {}).get('label', 'Unavailable')} {item.get('health', {}).get('emoji', '➖')}",
                        str(item.get("sessions", 0)),
                        fmt_currency(item.get("avg_cost_per_session", 0)),
                        fmt_number(item.get("avg_turns_per_session"), digits=1),
                        fmt_number(item.get("avg_session_duration_minutes"), digits=1),
                        fmt_number(item.get("avg_active_session_duration_minutes"), digits=1),
                        fmt_number(item.get("avg_start_context_window_tokens"), digits=0),
                        fmt_number(item.get("avg_end_context_window_tokens"), digits=0),
                        f"{item.get('avg_waste_ratio_pct', 0):.1f}%",
                    ]
                    for item in models
                ],
            ),
            "",
        ])

    if roadmap:
        lines.append("## Optimization Plan")
        lines.append("")
        for tool in roadmap:
            before_after = tool.get("before_after", {})
            strategy = tool.get("optimization_strategy", {})
            lines.extend([
                f"### Tool #{tool.get('priority_rank', '?')} — {tool.get('tool_label', tool.get('tool_id', 'Tool'))}",
                markdown_table(
                    ["Metric", "Value"],
                    [
                        ["Health", f"{tool.get('health', {}).get('label', 'Unavailable')} {tool.get('health', {}).get('emoji', '➖')}"],
                        ["Current average cost/session", fmt_currency(before_after.get("current_avg_cost_per_session", 0))],
                        ["Projected average cost/session", fmt_currency(before_after.get("projected_avg_cost_per_session", 0))],
                        ["Projected monthly savings", fmt_currency(before_after.get("projected_monthly_savings", 0))],
                        ["Log session duration (min)", fmt_number(tool.get("key_statistics", {}).get("avg_session_duration_minutes"), digits=1)],
                        ["Active session duration (min)", fmt_number(tool.get("key_statistics", {}).get("avg_active_session_duration_minutes"), digits=1)],
                        ["Optimization strategy", strategy.get("mode", "no_targets")],
                    ],
                ),
                "",
                strategy.get("summary", ""),
                "",
            ])
            if strategy.get("primary_targets"):
                lines.extend([
                    "**Primary targets**",
                    render_target_list(strategy.get("primary_targets", [])),
                    "",
                ])
            if strategy.get("fallback_targets"):
                lines.extend([
                    "**Fallback targets**",
                    render_target_list(strategy.get("fallback_targets", [])),
                    "",
                ])
            if tool.get("steps"):
                lines.extend([
                    markdown_table(
                        ["Step", "Health", "Waste", "Savings / session", "Savings / month"],
                        [
                            [
                                f"{step.get('rank', '')}. {step.get('title', 'Untitled step')}",
                                f"{step.get('health', {}).get('label', 'Unavailable')} {step.get('health', {}).get('emoji', '➖')}",
                                f"{step.get('waste_ratio_pct', 0):.1f}%",
                                fmt_currency(step.get("projected_savings_per_session", 0)),
                                fmt_currency(step.get("projected_monthly_savings", 0)),
                            ]
                            for step in tool.get("steps", [])
                        ],
                    ),
                    "",
                ])

    next_action = payload.get("next_action")
    if next_action:
        lines.extend([
            "## Next Action",
            next_action.get("title", "Next action"),
            "",
            next_action.get("body", ""),
            "",
        ])

    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def render_tool_success_markdown(payload):
    hero = payload.get("hero", {})
    success = payload.get("tool_success", {})
    status_report = payload.get("status_report", {})
    before_after = status_report.get("before_after", success.get("summary", {}))
    key_statistics = status_report.get("key_statistics", {})
    top_savings = status_report.get("top_savings", success.get("top_savings", []))
    optimization_strategy = status_report.get("optimization_strategy", success.get("optimization_strategy", {}))

    lines = [
        f"# VibeCheck Optimization Update — {success.get('tool_label', success.get('tool_id', 'Tool'))}",
        "",
        "## Key Result",
        hero.get("headline", payload.get("message", "Optimization complete.")),
        "",
        "## Before vs After",
        markdown_table(
            ["Metric", "Before", "After / Projection"],
            [
                ["Average cost/session", fmt_currency(before_after.get("avg_cost_before", 0)), fmt_currency(before_after.get("avg_cost_after", 0))],
                ["Waste ratio", f"{before_after.get('waste_ratio_before_pct', 0):.1f}%", "Targeted"],
                ["Projected monthly savings", "—", fmt_currency(before_after.get("projected_monthly_savings", 0))],
            ],
        ),
        "",
        "## Key Statistics",
        markdown_table(
            ["Statistic", "Value"],
            [
                ["Average turns/session", fmt_number(key_statistics.get("avg_turns_per_session"), digits=1)],
                ["Log session duration (min)", fmt_number(key_statistics.get("avg_session_duration_minutes"), digits=1)],
                ["Active session duration (min)", fmt_number(key_statistics.get("avg_active_session_duration_minutes"), digits=1)],
                ["Average start context window", fmt_number(key_statistics.get("avg_start_context_window_tokens"), digits=0)],
                ["Average end context window", fmt_number(key_statistics.get("avg_end_context_window_tokens"), digits=0)],
            ],
        ),
        "",
    ]

    areas = key_statistics.get("big_3_waste_areas", [])
    if areas:
        lines.extend([
            "## Top 3 Waste Areas Before Optimization",
            markdown_table(
                ["Area", "Health", "Waste", "Savings / session"],
                [
                    [
                        item.get("label", "Area"),
                        f"{item.get('health', {}).get('label', 'Unavailable')} {item.get('health', {}).get('emoji', '➖')}",
                        f"{item.get('waste_ratio_pct', 0):.1f}%",
                        item.get("cost_display", fmt_currency(item.get("cost_per_session", 0))),
                    ]
                    for item in areas
                ],
            ),
            "",
        ])

    if top_savings:
        lines.extend([
            "## Top Savings Captured",
            markdown_table(
                ["Area", "Health", "Waste", "Savings / session", "Savings / month"],
                [
                    [
                        item.get("title", "Untitled step"),
                        f"{item.get('health', {}).get('label', 'Unavailable')} {item.get('health', {}).get('emoji', '➖')}",
                        f"{item.get('waste_ratio_pct', 0):.1f}%",
                        fmt_currency(item.get("projected_savings_per_session", 0)),
                        fmt_currency(item.get("projected_monthly_savings", 0)),
                    ]
                    for item in top_savings
                ],
            ),
            "",
        ])

    lines.extend([
        "## What Changed",
        optimization_strategy.get("summary", "Optimization completed."),
        "",
    ])
    if optimization_strategy.get("primary_targets"):
        lines.extend([
            "**Primary targets**",
            render_target_list(optimization_strategy.get("primary_targets", [])),
            "",
        ])
    if optimization_strategy.get("fallback_targets"):
        lines.extend([
            "**Fallback targets**",
            render_target_list(optimization_strategy.get("fallback_targets", [])),
            "",
        ])

    completed_steps = status_report.get("completed_steps", [])
    if completed_steps:
        lines.extend([
            "**Completed steps**",
            "\n".join(
                f"- {step.get('rank', '')}. {step.get('title', 'Untitled step')} "
                f"({step.get('health', {}).get('label', 'Unavailable')} {step.get('health', {}).get('emoji', '➖')})"
                for step in completed_steps
            ),
            "",
        ])

    continue_prompt = payload.get("continue_prompt")
    if continue_prompt:
        lines.extend([
            "## Next Tool",
            continue_prompt.get("message", ""),
            "",
        ])

    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def default_output_path(payload):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    kind = payload.get("kind")
    if kind == "scan_result":
        filename = f"vibecheck-scan-{stamp}.md"
    elif kind == "tool_success":
        tool_id = payload.get("tool_success", {}).get("tool_id", "tool")
        filename = f"vibecheck-{tool_id}-optimization-{stamp}.md"
    else:
        fail(f"unsupported payload kind for markdown export: {kind}")
    return str(Path.cwd() / filename)


def render_markdown(payload):
    kind = payload.get("kind")
    if kind == "scan_result":
        return render_scan_markdown(payload)
    if kind == "tool_success":
        return render_tool_success_markdown(payload)
    fail(f"unsupported payload kind for markdown export: {kind}")


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: export_optimization_log.py <payload.json> [output.md]", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    output_path = sys.argv[2] if len(sys.argv) == 3 else default_output_path(payload)
    markdown = render_markdown(payload)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown)
    print(json.dumps({"path": str(path), "kind": payload.get("kind")}, indent=2))


if __name__ == "__main__":
    main()
