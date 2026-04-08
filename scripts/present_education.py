#!/usr/bin/env python3
"""Build the final post-optimization education payload from lesson guidance."""
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


def build_payload(lesson):
    guidance = lesson.get("behavior_guidance", {})
    context_rot = guidance.get("context_rot", {})
    session_slicing = guidance.get("session_slicing", {})
    continuity_system = guidance.get("continuity_system", {})
    handoff = guidance.get("handoff_skill", {})

    return {
        "visibility": "result",
        "kind": "optimization_education",
        "run_state": {
            "state": "completed",
            "resultPayload": "optimization_education",
        },
        "hero": {
            "eyebrow": "Keep the gains",
            "headline": "Use shorter focused chats and a lightweight continuity system so the savings keep compounding.",
            "supporting_text": "Teach the human habits only after the optimization win is already visible.",
        },
        "context_window": {
            "headline": context_rot.get("headline"),
            "plain": context_rot.get("plain"),
            "why_capability_drops": context_rot.get("why_capability_drops"),
            "auto_compaction_note": context_rot.get("auto_compaction_note"),
        },
        "session_habits": {
            "headline": session_slicing.get("headline"),
            "recommended_active_minutes": session_slicing.get("recommended_active_minutes"),
            "recommended_turn_ceiling": session_slicing.get("recommended_turn_ceiling"),
            "sweet_spot_reason": session_slicing.get("sweet_spot_reason"),
            "reset_rule": session_slicing.get("reset_rule"),
        },
        "continuity_system": {
            "persistent_behavior": continuity_system.get("persistent_behavior"),
            "project_docs": continuity_system.get("project_docs"),
            "project_doc_structure": continuity_system.get("project_doc_structure", []),
        },
        "handoff": {
            "recommended": handoff.get("recommended", False),
            "purpose": handoff.get("purpose"),
            "how_to_use": handoff.get("how_to_use"),
            "install_timing": handoff.get("install_timing"),
            "install_prompt": handoff.get("install_prompt_template"),
            "repo_url": handoff.get("repo_url"),
        },
        "sections": [
            {"id": "hero", "kind": "hero"},
            {"id": "context_window", "kind": "context"},
            {"id": "session_habits", "kind": "habits"},
            {"id": "continuity_system", "kind": "continuity"},
            {"id": "handoff", "kind": "handoff"},
        ],
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: present_education.py <lesson.json>", file=sys.stderr)
        sys.exit(1)

    lesson = load_json(sys.argv[1])
    print(json.dumps(build_payload(lesson), indent=2))


if __name__ == "__main__":
    main()
