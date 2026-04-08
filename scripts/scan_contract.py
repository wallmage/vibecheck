#!/usr/bin/env python3
"""Shared scan presentation contract constants and helpers."""

VISIBILITY_VALUES = ["internal", "progress", "result", "approval"]

PROGRESS_STAGES = [
    "Checking your setup",
    "Finding recent sessions",
    "Analyzing waste patterns",
    "Preparing your report",
]

INTERNAL_EVENT_TYPES = [
    "detect",
    "find",
    "analyze",
    "explain",
    "present",
    "report",
    "export",
]

PAYLOAD_KINDS = {
    "internal": "scan_internal",
    "progress": "scan_progress",
    "result": "scan_result",
    "approval": "scan_approval",
    "failure": "scan_failure",
}

TECHNICAL_DETAILS_LABEL = "Technical details"
TECHNICAL_DETAILS_DEFAULT = "collapsed"
SUMMARY_METRIC_IDS = ["sessions", "avg_cost_per_session", "waste_percentage"]
RESULT_SECTION_KINDS = ["hero", "metrics", "header_statistics", "patterns", "optimization_plan", "next_action"]
EMPTY_RESULT_SECTION_KINDS = ["hero", "metrics", "next_action"]


def build_contract_dict():
    return {
        "visibility_values": VISIBILITY_VALUES,
        "progress_stages": PROGRESS_STAGES,
        "scan_run_state": {
            "idle": {
                "state": "idle",
            },
            "running": {
                "state": "running",
                "stage": PROGRESS_STAGES[0],
            },
            "completed": {
                "state": "completed",
                "resultPayload": PAYLOAD_KINDS["result"],
            },
            "failed": {
                "state": "failed",
                "userMessage": "I couldn't finish the scan.",
                "technicalDetails": "Optional short stderr excerpt shown behind a collapsed disclosure.",
            },
        },
        "payload_kinds": PAYLOAD_KINDS,
        "payload_examples": {
            "internal": {
                "visibility": "internal",
                "kind": PAYLOAD_KINDS["internal"],
                "run_state": {
                    "state": "running",
                },
                "event": {
                    "type": "analyze",
                    "summary": "Analyzer wrote structured output to a temp file.",
                },
            },
            "progress": {
                "visibility": "progress",
                "kind": PAYLOAD_KINDS["progress"],
                "run_state": {
                    "state": "running",
                    "stage": PROGRESS_STAGES[2],
                },
                "message": PROGRESS_STAGES[2],
            },
            "approval": {
                "visibility": "approval",
                "kind": PAYLOAD_KINDS["approval"],
                "run_state": {
                    "state": "idle",
                },
                "card": {
                    "title": "Export recent logs",
                    "body": "I need one export command because this environment cannot read your local logs directly.",
                    "command": "python3 SKILL_DIR/scripts/export_logs.py",
                },
            },
            "failure": {
                "visibility": "result",
                "kind": PAYLOAD_KINDS["failure"],
                "run_state": {
                    "state": "failed",
                    "userMessage": "I couldn't finish the scan.",
                },
                "error": {
                    "user_message": "I couldn't finish the scan.",
                    "technical_details_disclosure_label": TECHNICAL_DETAILS_LABEL,
                    "technical_details_default": TECHNICAL_DETAILS_DEFAULT,
                },
            },
            "result": {
                "visibility": "result",
                "kind": PAYLOAD_KINDS["result"],
                "run_state": {
                    "state": "completed",
                    "resultPayload": PAYLOAD_KINDS["result"],
                },
                "hero": {
                    "eyebrow": "Scan complete",
                    "headline": "Idle narration is your biggest drag - fixing it would save about $0.006/session.",
                    "supporting_text": "Start with the finding, not the methodology. The renderer should make this the primary focal block.",
                },
                "headline": "Idle narration is your biggest drag - fixing it would save about $0.006/session.",
                "summary": {
                    "sessions_analyzed": 1,
                    "avg_cost_per_session": 0.02,
                    "waste_percentage": 29.4,
                },
                "summary_metrics": [
                    {
                        "id": SUMMARY_METRIC_IDS[0],
                        "label": "Sessions scanned",
                        "value": "1",
                    },
                    {
                        "id": SUMMARY_METRIC_IDS[1],
                        "label": "Avg cost/session",
                        "value": "$0.020",
                    },
                    {
                        "id": SUMMARY_METRIC_IDS[2],
                        "label": "Waste",
                        "value": "29.4%",
                    },
                ],
                "top_waste_patterns": [
                    {
                        "key": "idle_narration",
                        "label": "Idle narration",
                        "cost_per_session": 0.006,
                        "cost_display": "$0.006/session",
                        "share_of_waste": 100.0,
                        "summary": "Status-only turns that re-read the full conversation before acting.",
                    }
                ],
                "next_action": {
                    "title": "Tighten CLAUDE.md",
                    "body": "Start with the no-narration, think-and-act rules. That is the cleanest first move before re-running /vibecheck scan.",
                    "instruction_file": "CLAUDE.md",
                },
                "unified_scan": {
                    "mode": "all_detected_tools",
                    "tools_scanned": 1,
                    "tools_detected": 2,
                    "tools_unsupported": 1,
                    "tools_skipped": 0,
                    "tools_failed": 0,
                    "instruction_targets": 1,
                    "optimization_targets": 2,
                },
                "breakdowns": {
                    "tools": [
                        {
                            "id": "claude_code",
                            "label": "Claude Code",
                            "status": "scanned",
                            "support_level": "full",
                            "analysis_mode": "claude_jsonl",
                            "sessions": 1,
                            "total_cost": 0.02,
                            "waste_pct": 29.4,
                            "instruction_targets": 1,
                            "optimization_targets": 1,
                        },
                        {
                            "id": "gemini_cli",
                            "label": "Gemini CLI",
                            "status": "unsupported",
                            "support_level": "limited",
                            "analysis_mode": "instruction_only",
                            "sessions": 0,
                            "total_cost": 0,
                            "waste_pct": 0,
                            "instruction_targets": 0,
                            "optimization_targets": 1,
                        },
                    ],
                    "providers": [],
                    "models": [],
                    "platforms": [],
                },
                "coverage": {
                    "detected_tools": [
                        {
                            "id": "claude_code",
                            "label": "Claude Code",
                            "status": "scanned",
                            "support_level": "full",
                            "analysis_mode": "claude_jsonl",
                            "instruction_targets": 1,
                            "optimization_targets": 1,
                        },
                        {
                            "id": "gemini_cli",
                            "label": "Gemini CLI",
                            "status": "unsupported",
                            "support_level": "limited",
                            "analysis_mode": "instruction_only",
                            "instruction_targets": 0,
                            "optimization_targets": 1,
                        },
                    ],
                    "unsupported_tools": [
                        {
                            "id": "gemini_cli",
                            "label": "Gemini CLI",
                            "support_level": "limited",
                        }
                    ],
                    "skipped_tools": [],
                    "failed_tools": [],
                },
                "optimization_targets": [
                    {
                        "tool": "claude_code",
                        "label": "Claude Code",
                        "path": "/tmp/CLAUDE.md",
                        "filename": "CLAUDE.md",
                        "kind": "instruction_file",
                        "scope": "project",
                    },
                    {
                        "tool": "gemini_cli",
                        "label": "Gemini CLI",
                        "path": "/tmp/.gemini/settings.json",
                        "filename": "settings.json",
                        "kind": "config_path",
                        "scope": "global",
                    },
                ],
                "header_statistics": {
                    "overall": {
                        "health": {
                            "id": "waste",
                            "label": "Waste",
                            "emoji": "❌",
                            "threshold_pct": 10.0,
                            "waste_ratio_pct": 29.4,
                        },
                        "avg_cost_per_session": 0.02,
                        "avg_turns_per_session": 3.0,
                        "avg_session_duration_minutes": 12.0,
                        "avg_active_session_duration_minutes": 9.0,
                        "avg_start_context_window_tokens": 1800,
                        "avg_end_context_window_tokens": 4200,
                        "avg_waste_ratio_pct": 29.4,
                        "big_3_waste_areas": [
                            {
                                "key": "idle_narration",
                                "label": "Idle narration",
                                "cost_per_session": 0.006,
                                "cost_display": "$0.006/session",
                                "waste_ratio_pct": 30.0,
                                "health": {
                                    "id": "waste",
                                    "label": "Waste",
                                    "emoji": "❌",
                                    "threshold_pct": 10.0,
                                    "waste_ratio_pct": 30.0,
                                },
                                "summary": "Status-only turns that re-read the full conversation before acting.",
                            }
                        ],
                    },
                    "tools": [
                        {
                            "id": "claude_code",
                            "label": "Claude Code",
                            "rank": 1,
                            "priority_label": "daily_driver",
                            "scan_status": "scanned",
                            "health": {
                                "id": "waste",
                                "label": "Waste",
                                "emoji": "❌",
                                "threshold_pct": 10.0,
                                "waste_ratio_pct": 29.4,
                            },
                            "sessions": 1,
                            "log_count": 1,
                            "avg_cost_per_session": 0.02,
                            "avg_turns_per_session": 3.0,
                            "avg_session_duration_minutes": 12.0,
                            "avg_active_session_duration_minutes": 9.0,
                            "avg_start_context_window_tokens": 1800,
                            "avg_end_context_window_tokens": 4200,
                            "avg_waste_ratio_pct": 29.4,
                            "big_3_waste_areas": [],
                            "projected_avg_cost_per_session": 0.01,
                            "projected_monthly_savings": 0.18,
                        }
                    ],
                    "models": [
                        {
                            "id": "claude-sonnet-4.6",
                            "label": "claude-sonnet-4.6",
                            "health": {
                                "id": "waste",
                                "label": "Waste",
                                "emoji": "❌",
                                "threshold_pct": 10.0,
                                "waste_ratio_pct": 29.4,
                            },
                            "sessions": 1,
                            "avg_cost_per_session": 0.02,
                            "avg_turns_per_session": 3.0,
                            "avg_session_duration_minutes": 12.0,
                            "avg_active_session_duration_minutes": 9.0,
                            "avg_start_context_window_tokens": 1800,
                            "avg_end_context_window_tokens": 4200,
                            "avg_waste_ratio_pct": 29.4,
                            "big_3_waste_areas": [],
                        }
                    ],
                },
                "duration_notes": {
                    "log_session_duration": {
                        "label": "Log session duration",
                        "availability": "all_tools",
                        "description": "Directly from log timestamps. Useful for session span, but noisy if the session sat open while you were away.",
                    },
                    "active_session_duration": {
                        "label": "Active session duration",
                        "availability": "partial",
                        "description": "Estimated from real activity gaps when the underlying logs provide enough event timestamps.",
                    },
                },
                "optimization_plan": {
                    "thresholds": {
                        "good_max_waste_pct": 10.0,
                    },
                    "tool_sequence": ["claude_code"],
                    "tools": [
                        {
                            "tool_id": "claude_code",
                            "tool_label": "Claude Code",
                            "priority_rank": 1,
                            "priority_label": "daily_driver",
                            "scan_status": "scanned",
                            "health": {
                                "id": "waste",
                                "label": "Waste",
                                "emoji": "❌",
                                "threshold_pct": 10.0,
                                "waste_ratio_pct": 29.4,
                            },
                            "before_after": {
                                "current_avg_cost_per_session": 0.02,
                                "projected_avg_cost_per_session": 0.01,
                                "projected_monthly_savings": 0.18,
                                "waste_ratio_pct": 29.4,
                            },
                            "key_statistics": {
                                "avg_turns_per_session": 3.0,
                                "avg_session_duration_minutes": 12.0,
                                "avg_active_session_duration_minutes": 9.0,
                                "avg_start_context_window_tokens": 1800,
                                "avg_end_context_window_tokens": 4200,
                                "big_3_waste_areas": [],
                            },
                            "steps": [
                                {
                                    "id": "claude_code-step-1",
                                    "rank": 1,
                                    "title": "Idle narration",
                                    "health": {
                                        "id": "waste",
                                        "label": "Waste",
                                        "emoji": "❌",
                                        "threshold_pct": 10.0,
                                        "waste_ratio_pct": 30.0,
                                    },
                                    "waste_ratio_pct": 30.0,
                                    "projected_savings_per_session": 0.006,
                                    "projected_monthly_savings": 0.18,
                                    "patterns": [],
                                    "facts": [],
                                    "explanation": {
                                        "summary": "Status-only turns that re-read the full conversation before acting.",
                                        "why_it_matters": "On Claude Code, this area accounts for about 30.0% of the average session spend and should be handled before lower-impact cleanup.",
                                    },
                                    "approval_required": True,
                                    "target_files": [],
                                }
                            ],
                            "next_tool_id": None,
                        }
                    ],
                },
                "sections": [
                    {"id": "hero", "kind": "hero"},
                    {"id": "summary_metrics", "kind": "metrics"},
                    {"id": "header_statistics", "kind": "header_statistics"},
                    {"id": "top_waste_patterns", "kind": "patterns"},
                    {"id": "optimization_plan", "kind": "optimization_plan"},
                    {"id": "next_action", "kind": "next_action"},
                ],
                "education_bridge": "Lead with this summary first. Teach methodology only after the user has seen the findings.",
            },
            "result_empty": {
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
                "summary_metrics": [
                    {
                        "id": SUMMARY_METRIC_IDS[0],
                        "label": "Sessions scanned",
                        "value": "0",
                    },
                    {
                        "id": SUMMARY_METRIC_IDS[1],
                        "label": "Avg cost/session",
                        "value": "$0.000",
                    },
                    {
                        "id": SUMMARY_METRIC_IDS[2],
                        "label": "Waste",
                        "value": "0.0%",
                    },
                ],
                "top_waste_patterns": [],
                "next_action": {
                    "title": "Run scan again after more activity",
                    "body": "I could not find enough recent session data yet. Re-run /vibecheck scan after a few real sessions or export recent logs.",
                    "instruction_file": None,
                },
                "unified_scan": {
                    "mode": "all_detected_tools",
                    "tools_scanned": 0,
                    "tools_detected": 1,
                    "tools_unsupported": 1,
                    "tools_skipped": 0,
                    "tools_failed": 0,
                    "instruction_targets": 0,
                    "optimization_targets": 1,
                },
                "coverage": {
                    "detected_tools": [
                        {
                            "id": "gemini_cli",
                            "label": "Gemini CLI",
                            "status": "unsupported",
                            "support_level": "limited",
                            "analysis_mode": "instruction_only",
                            "instruction_targets": 0,
                            "optimization_targets": 1,
                        }
                    ],
                    "unsupported_tools": [
                        {
                            "id": "gemini_cli",
                            "label": "Gemini CLI",
                            "support_level": "limited",
                        }
                    ],
                    "skipped_tools": [],
                    "failed_tools": [],
                },
                "optimization_targets": [
                    {
                        "tool": "gemini_cli",
                        "label": "Gemini CLI",
                        "path": "/tmp/.gemini/settings.json",
                        "filename": "settings.json",
                        "kind": "config_path",
                        "scope": "global",
                    }
                ],
                "header_statistics": {
                    "overall": {
                        "health": {
                            "id": "unavailable",
                            "label": "Unavailable",
                            "emoji": "➖",
                            "threshold_pct": 10.0,
                            "waste_ratio_pct": None,
                        },
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
                },
                "duration_notes": {
                    "log_session_duration": {
                        "label": "Log session duration",
                        "availability": "unavailable",
                        "description": "Directly from log timestamps. Useful for session span, but noisy if the session sat open while you were away.",
                    },
                    "active_session_duration": {
                        "label": "Active session duration",
                        "availability": "unavailable",
                        "description": "Estimated from real activity gaps when the underlying logs provide enough event timestamps.",
                    },
                },
                "optimization_plan": {
                    "thresholds": {
                        "good_max_waste_pct": 10.0,
                    },
                    "tool_sequence": [],
                    "tools": [],
                },
                "sections": [
                    {"id": "hero", "kind": "hero"},
                    {"id": "summary_metrics", "kind": "metrics"},
                    {"id": "next_action", "kind": "next_action"},
                ],
                "education_bridge": "Lead with this summary first. Teach methodology only after the user has seen the findings.",
            },
        },
        "transcript_rules": {
            "hide_internal_from_primary_transcript": True,
            "max_visible_progress_items": 1,
            "technical_details_default": TECHNICAL_DETAILS_DEFAULT,
            "result_replaces_progress_on_completion": True,
            "export_card_shows_one_command_only": True,
        },
        "validation_rules": {
            "internal_event_types": INTERNAL_EVENT_TYPES,
            "approval_card_command_must_be_single_string": True,
            "summary_metric_ids": SUMMARY_METRIC_IDS,
            "result_section_kinds": RESULT_SECTION_KINDS,
            "empty_result_section_kinds": EMPTY_RESULT_SECTION_KINDS,
            "coverage_buckets": ["detected_tools", "unsupported_tools", "skipped_tools", "failed_tools"],
        },
    }
