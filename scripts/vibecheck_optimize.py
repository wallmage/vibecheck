#!/usr/bin/env python3
"""Apply a concrete optimization step to existing instruction files."""
import json
import os
import shutil
import sys
from pathlib import Path

from workflow_state import (
    STEP_STATUS_APPLIED,
    STEP_STATUS_SKIPPED,
    actionable_targets,
    actionable_targets_for_step,
    applied_steps,
    ensure_execution_state,
    mark_step_status,
)


MARKDOWN_START = "<!-- vibecheck:cost-rules:start -->"
MARKDOWN_END = "<!-- vibecheck:cost-rules:end -->"
PLAINTEXT_START = "VIBECHECK COST RULES START"
PLAINTEXT_END = "VIBECHECK COST RULES END"

SKIP_SUFFIXES = {
    ".json",
    ".jsonl",
    ".toml",
    ".yaml",
    ".yml",
    ".sqlite",
    ".db",
    ".vscdb",
}

BASELINE_RULES = [
    "Every turn should include action: a tool call, code change, or concrete result. Do not spend a turn narrating what you are about to do.",
    "Think and act in the same turn when the next action is clear.",
    "Batch independent reads, edits, and shell steps when it is safe.",
    "Keep command output quiet. Redirect noisy build/test/install output to a temp file and surface only the useful tail.",
    "Do not re-read unchanged files that are already in context unless accuracy depends on it.",
    "After repeated failures on the same issue, stop, inspect the error carefully, and make one targeted fix instead of retrying blindly.",
]

PATTERN_RULES = {
    "idle_narration": [
        "Every turn should include action: a tool call, code change, or concrete result. Do not spend a turn narrating what you are about to do.",
        "Think and act in the same turn when the next action is clear.",
    ],
    "context_rot": [
        "In long threads, keep replies compact and avoid re-explaining old context unless it helps the next action.",
        "Prefer concise summaries over repeating the same background when the thread is already long.",
    ],
    "pingpong_debugging": [
        "After repeated failures on the same issue, stop, inspect the error carefully, and make one targeted fix instead of retrying blindly.",
    ],
    "verbose_output": [
        "Keep command output quiet. Redirect noisy build/test/install output to a temp file and surface only the useful tail.",
    ],
    "codebase_wandering": [
        "Use focused search first, then open only the files needed for the change.",
    ],
    "chainable_bash": [
        "Batch independent shell commands into one step when it is safe.",
    ],
    "unbatched_edits": [
        "Batch related file edits into one response when the files are already known.",
    ],
    "duplicate_reads": [
        "Do not re-read unchanged files that are already in context unless accuracy depends on it.",
    ],
    "sleep_poll_loops": [
        "Prefer wait flags or background execution over repeated sleep/poll loops.",
    ],
    "git_ceremony": [
        "Collapse routine git status/diff/log ceremony into denser command sequences when it is safe.",
    ],
    "failed_tools": [
        "If a tool call fails, read the error, fix the cause, and retry once with a targeted change instead of looping.",
    ],
    "toolsearch": [
        "Call the right tool directly when the path is clear instead of spending extra turns searching for the tool schema.",
    ],
    "heartbeat_idle": [
        "Skip idle wake-ups when nothing changed. Do not emit status messages that do not lead to action.",
    ],
    "workspace_bloat": [
        "Keep this instruction surface lean. Remove human-only filler and keep only behavioral rules the agent needs on every turn.",
    ],
    "memory_accumulation": [
        "Prune stale working memory and keep only the compact state needed for the next action.",
    ],
}


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


def unique(items):
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def build_rule_lines(step):
    lines = []
    for pattern in step.get("patterns", []):
        for line in PATTERN_RULES.get(pattern.get("key"), []):
            lines.append(line)
    if not lines:
        lines.extend(BASELINE_RULES)
    return unique(lines)


def collect_targets(raw_targets):
    results = []
    seen = set()
    for target in actionable_targets(raw_targets):
        path = target.get("path") or target.get("file")
        if not path or path in seen:
            continue
        seen.add(path)
        results.append(target)
    return results


def is_markdown(path):
    suffix = Path(path).suffix.lower()
    return suffix in {".md", ".markdown"}


def is_editable_instruction_file(path):
    target = Path(path)
    if not target.exists() or target.is_dir():
        return False
    return target.suffix.lower() not in SKIP_SUFFIXES


def render_block(path, steps, rules):
    step_titles = ", ".join(step.get("title", f"Step {step.get('rank', '?')}") for step in steps)
    if is_markdown(path):
        body = "\n".join(f"- {line}" for line in rules)
        return "\n".join(
            [
                MARKDOWN_START,
                "## Vibecheck Cost Rules",
                "",
                body,
                "",
                f"_Applied from: {step_titles}_",
                MARKDOWN_END,
            ]
        )

    body = "\n".join(rules)
    return "\n".join(
        [
            PLAINTEXT_START,
            body,
            f"Applied from: {step_titles}",
            PLAINTEXT_END,
        ]
    )


def replace_or_append_block(content, block, markdown):
    start = MARKDOWN_START if markdown else PLAINTEXT_START
    end = MARKDOWN_END if markdown else PLAINTEXT_END
    if start in content and end in content:
        before, rest = content.split(start, 1)
        _, after = rest.split(end, 1)
        merged = before.rstrip() + "\n\n" + block + "\n" + after.lstrip("\n")
        return merged.rstrip() + "\n"

    base = content.rstrip()
    if base:
        return base + "\n\n" + block + "\n"
    return block + "\n"


def ensure_backup(path):
    backup_path = f"{path}.vibecheck-backup"
    if not os.path.exists(backup_path):
        shutil.copy2(path, backup_path)
        return backup_path, True
    return backup_path, False


def persist_payload(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def build_cumulative_rules(tool):
    lines = []
    for step in applied_steps(tool):
        lines.extend(build_rule_lines(step))
    return unique(lines)


def collect_applied_targets(tool):
    raw_targets = []
    for step in applied_steps(tool):
        raw_targets.extend(step.get("target_files", []))
    if not raw_targets:
        raw_targets.extend(tool.get("optimization_strategy", {}).get("effective_targets", []))
    return collect_targets(raw_targets)


def apply_cumulative_rules(tool):
    targets = collect_applied_targets(tool)
    rules = build_cumulative_rules(tool)
    if not targets:
        return {
            "applied": [],
            "skipped": [],
            "rules_written": rules,
        }

    applied = []
    skipped = []
    for target in targets:
        path = target.get("path") or target.get("file")
        if not path:
            continue
        if not is_editable_instruction_file(path):
            skipped.append(
                {
                    "path": path,
                    "reason": "missing_or_not_editable",
                }
            )
            continue

        backup_path, backup_created = ensure_backup(path)
        with open(path) as f:
            original = f.read()
        block = render_block(path, applied_steps(tool), rules)
        updated = replace_or_append_block(original, block, is_markdown(path))
        with open(path, "w") as f:
            f.write(updated)
        applied.append(
            {
                "path": path,
                "backup_path": backup_path,
                "backup_created": backup_created,
                "rules_written": rules,
            }
        )

    return {
        "applied": applied,
        "skipped": skipped,
        "rules_written": rules,
    }


def apply_step(payload_path, tool_id, step_rank):
    payload = load_json(payload_path)
    ensure_execution_state(payload)
    tool = find_tool(payload.get("optimization_plan", {}), tool_id)
    step = find_step(tool, step_rank)

    if not actionable_targets_for_step(step):
        fail(f"step {step_rank} for {tool_id} has no editable instruction targets")

    mark_step_status(payload, tool_id, step_rank, STEP_STATUS_APPLIED, applied_targets=step.get("target_files", []))
    tool = find_tool(payload.get("optimization_plan", {}), tool_id)
    result = apply_cumulative_rules(tool)
    mark_step_status(
        payload,
        tool_id,
        step_rank,
        STEP_STATUS_APPLIED,
        applied_targets=result["applied"],
        skipped_targets=result["skipped"],
    )
    persist_payload(payload_path, payload)
    refreshed_tool = find_tool(payload.get("optimization_plan", {}), tool_id)
    result.update(
        {
            "ok": True,
            "tool_id": tool_id,
            "step_rank": step_rank,
            "next_pending_step_rank": refreshed_tool.get("execution_state", {}).get("next_step_rank"),
            "tool_complete": refreshed_tool.get("execution_state", {}).get("status") == "completed",
        }
    )
    return result


def apply_all_steps_for_tool(payload, tool_id):
    ensure_execution_state(payload)
    tool = find_tool(payload.get("optimization_plan", {}), tool_id)
    step_results = []
    for step in sorted(tool.get("steps", []), key=lambda item: item.get("rank", 0)):
        if not actionable_targets_for_step(step):
            continue
        mark_step_status(payload, tool_id, step.get("rank"), STEP_STATUS_APPLIED, applied_targets=step.get("target_files", []))
        step_results.append(
            {
                "step_rank": step.get("rank"),
                "step_title": step.get("title"),
                "applied_targets": len(actionable_targets_for_step(step)),
                "skipped_targets": 0,
            }
        )
    tool = find_tool(payload.get("optimization_plan", {}), tool_id)
    result = apply_cumulative_rules(tool)
    for step in applied_steps(tool):
        step.get("execution", {})["applied_targets"] = result["applied"]
        step.get("execution", {})["skipped_targets"] = result["skipped"]
    ensure_execution_state(payload)

    return {
        "tool_id": tool_id,
        "tool_label": tool.get("tool_label", tool_id),
        "applied": result["applied"],
        "skipped": result["skipped"],
        "step_results": step_results,
    }


def main():
    if len(sys.argv) != 4:
        print("Usage: vibecheck_optimize.py <scan_payload.json> <tool_id> <step_rank>", file=sys.stderr)
        sys.exit(1)

    payload = apply_step(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
