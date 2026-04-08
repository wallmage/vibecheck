#!/usr/bin/env python3
"""Build the final all-tools optimization success summary before education begins."""
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


def fmt_currency(amount):
    return f"${amount:.2f}" if amount >= 1 else f"${amount:.3f}"


def main():
    if len(sys.argv) != 2:
        print("Usage: present_final_success.py <scan_payload.json>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    tools = payload.get("optimization_plan", {}).get("tools", [])
    if not tools:
        fail("no optimization plan tools found")

    total_monthly = round(sum(tool.get("before_after", {}).get("projected_monthly_savings", 0) for tool in tools), 2)
    total_before = round(sum(tool.get("before_after", {}).get("current_avg_cost_per_session", 0) for tool in tools), 3)
    total_after = round(sum(tool.get("before_after", {}).get("projected_avg_cost_per_session", 0) for tool in tools), 3)
    top_tools = sorted(
        tools,
        key=lambda item: item.get("before_after", {}).get("projected_monthly_savings", 0),
        reverse=True,
    )[:3]

    result = {
        "visibility": "result",
        "kind": "optimization_final_success",
        "run_state": {
            "state": "completed",
            "resultPayload": "optimization_final_success",
        },
        "hero": {
            "eyebrow": "Optimization complete",
            "headline": f"Projected average cost drops from {fmt_currency(total_before)} to {fmt_currency(total_after)} across the optimized tools.",
            "supporting_text": "Show the optimization win first. Human education comes after this summary, not before it.",
        },
        "summary": {
            "tools_optimized": len(tools),
            "projected_monthly_savings": total_monthly,
            "avg_cost_before": total_before,
            "avg_cost_after": total_after,
        },
        "top_tool_wins": [
            {
                "tool_id": tool.get("tool_id"),
                "tool_label": tool.get("tool_label"),
                "projected_monthly_savings": tool.get("before_after", {}).get("projected_monthly_savings", 0),
                "avg_cost_before": tool.get("before_after", {}).get("current_avg_cost_per_session", 0),
                "avg_cost_after": tool.get("before_after", {}).get("projected_avg_cost_per_session", 0),
            }
            for tool in top_tools
        ],
        "education_next": {
            "title": "Human-side tips come next",
            "body": "Agents are now tuned. Next, teach the user how to keep context lean, preserve continuity, and use the handoff companion when it is time to switch chats.",
        },
        "sections": [
            {"id": "hero", "kind": "hero"},
            {"id": "summary", "kind": "comparison"},
            {"id": "top_tool_wins", "kind": "savings"},
            {"id": "education_next", "kind": "education"},
        ],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
