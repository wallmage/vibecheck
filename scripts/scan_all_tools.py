#!/usr/bin/env python3
"""Detect, scan, and merge all analyzable tools on this machine."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from detect_tool import TOOLS, detect_installed_tools, find_instruction_targets, find_optimization_targets
from merge_analyses import build_tool_inventory, merge_entries


MODE_TO_SCRIPTS = {
    "claude_jsonl": ("find_claude_logs.py", "analyze_claude_sessions.py"),
    "codex_jsonl": ("find_codex_logs.py", "analyze_codex_sessions.py"),
    "cursor_sqlite": ("find_cursor_logs.py", "analyze_cursor_sessions.py"),
    "openclaw_jsonl": ("find_openclaw_logs.py", "analyze_openclaw_sessions.py"),
    "copilot_chat_json": ("find_copilot_logs.py", "analyze_copilot_sessions.py"),
    "windsurf_transcript": ("find_windsurf_logs.py", "analyze_windsurf_sessions.py"),
    "trae_sqlite": ("find_trae_logs.py", "analyze_trae_sessions.py"),
    "qoder_sqlite": ("find_qoder_logs.py", "analyze_qoder_sessions.py"),
    "codebuddy_hybrid": ("find_codebuddy_logs.py", "analyze_buddy_sessions.py"),
    "workbuddy_hybrid": ("find_workbuddy_logs.py", "analyze_buddy_sessions.py"),
    "antigravity_brain": ("find_antigravity_logs.py", "analyze_antigravity_sessions.py"),
}

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    project_dir = sys.argv[2] if len(sys.argv) > 2 else None

    installed = detect_installed_tools()
    analyzable = [tool for tool in installed if tool.get("can_analyze") and tool.get("analysis_mode") in MODE_TO_SCRIPTS]
    unsupported = [tool for tool in installed if not (tool.get("can_analyze") and tool.get("analysis_mode") in MODE_TO_SCRIPTS)]

    entries = []
    skipped = []
    failed = []
    instruction_targets = find_instruction_targets(project_dir)
    optimization_targets = find_optimization_targets(project_dir, installed)

    with tempfile.TemporaryDirectory(prefix="vibecheck-all-") as tmp:
        tmpdir = Path(tmp)
        for tool in analyzable:
            tool_id = tool["id"]
            analysis_mode = tool["analysis_mode"]
            find_script, analyze_script = MODE_TO_SCRIPTS[analysis_mode]
            find_path = tmpdir / f"{tool_id}-sessions.json"
            analysis_path = tmpdir / f"{tool_id}-analysis.json"

            try:
                found = run_json([sys.executable, str(SCRIPTS / find_script), str(days)])
            except subprocess.CalledProcessError as exc:
                failed.append({
                    "tool_id": tool_id,
                    "tool_name": tool["name"],
                    "stage": "find",
                    "error": (exc.stderr or exc.stdout or "").strip()[:500],
                })
                continue

            if found.get("error") == "no_logs" or found.get("total_sessions", 0) == 0:
                skipped.append({
                    "tool_id": tool_id,
                    "tool_name": tool["name"],
                    "reason": "no_logs",
                })
                continue

            find_path.write_text(json.dumps(found))

            try:
                analysis = run_json([sys.executable, str(SCRIPTS / analyze_script), str(find_path)])
            except subprocess.CalledProcessError as exc:
                failed.append({
                    "tool_id": tool_id,
                    "tool_name": tool["name"],
                    "stage": "analyze",
                    "error": (exc.stderr or exc.stdout or "").strip()[:500],
                })
                continue

            analysis["scan_tool_id"] = tool_id
            analysis["scan_tool_name"] = tool["name"]
            analysis["scan_analysis_mode"] = analysis_mode
            analysis["instruction_targets"] = [target for target in instruction_targets if target.get("tool") == tool_id]
            analysis["optimization_targets"] = [target for target in optimization_targets if target.get("tool") == tool_id]
            analysis_path.write_text(json.dumps(analysis))
            entries.append({
                "tool_id": tool_id,
                "tool_name": tool["name"],
                "analysis_mode": analysis_mode,
                "analysis": analysis,
                "instruction_targets": analysis["instruction_targets"],
                "optimization_targets": analysis["optimization_targets"],
            })

    if not entries:
        print(json.dumps({
            "error": "no_supported_logs",
            "installed_tools": installed,
            "analyzable_tools": analyzable,
            "unsupported_tools": unsupported,
            "skipped_tools": skipped,
            "failed_tools": failed,
            "instruction_targets": instruction_targets,
            "optimization_targets": optimization_targets,
            "tool_inventory": build_tool_inventory(
                [],
                installed_tools=installed,
                skipped_tools=skipped,
                failed_tools=failed,
                unsupported_tools=unsupported,
                instruction_targets=instruction_targets,
                optimization_targets=optimization_targets,
            ),
            "scan_scope": {
                "mode": "all_detected_tools",
                "tool_count": 0,
                "tool_ids": [],
                "tool_names": [],
            },
        }, indent=2))
        sys.exit(0)

    merged = merge_entries(entries)
    merged["installed_tools"] = installed
    merged["analyzable_tools"] = analyzable
    merged["unsupported_tools"] = unsupported
    merged["skipped_tools"] = skipped
    merged["failed_tools"] = failed
    merged["instruction_targets"] = instruction_targets
    merged["optimization_targets"] = optimization_targets
    merged["tool_inventory"] = build_tool_inventory(
        entries,
        installed_tools=installed,
        skipped_tools=skipped,
        failed_tools=failed,
        unsupported_tools=unsupported,
        instruction_targets=instruction_targets,
        optimization_targets=optimization_targets,
    )
    merged["scan_scope"]["installed_tool_count"] = len(installed)
    merged["scan_scope"]["analyzable_tool_count"] = len(analyzable)
    merged["scan_scope"]["unsupported_tool_count"] = len(unsupported)

    print(json.dumps(merged, indent=2))


if __name__ == "__main__":
    main()
