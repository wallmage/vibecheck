import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import detect_tool
from model_pricing import get_pricing, get_pricing_metadata
from scan_contract import build_contract_dict


def run_json(script_name, *args):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


class RegressionTests(unittest.TestCase):
    def test_model_pricing_resolves_deepseek_aliases(self):
        pricing = get_pricing("deepseek-chat")
        metadata = get_pricing_metadata("deepseek-chat")

        self.assertEqual(pricing["provider"], "deepseek")
        self.assertAlmostEqual(pricing["output"], 0.42)
        self.assertEqual(metadata["canonical_model"], "deepseek-v3.2")
        self.assertEqual(metadata["provider"], "deepseek")

    def test_claude_analysis_includes_confidence_and_pricing_metadata(self):
        data = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        self.assertEqual(data["analysis_confidence"]["label"], "measured")
        self.assertEqual(data["pricing_metadata"]["billing_mode"], "full_billing")
        self.assertEqual(data["pricing_metadata"]["registry_version"], "2026-04-08")

    def test_claude_analysis_keeps_log_duration_and_adds_active_duration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            session_path = base / "session.jsonl"
            sessions_path = base / "sessions.json"
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-07T09:00:00Z",
                                "type": "assistant",
                                "message": {
                                    "model": "claude-sonnet-4.6",
                                    "usage": {
                                        "input_tokens": 1000,
                                        "cache_read_input_tokens": 100,
                                        "cache_creation_input_tokens": 50,
                                        "output_tokens": 120,
                                    },
                                    "content": [{"type": "text", "text": "Starting work."}],
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-07T09:05:00Z",
                                "type": "assistant",
                                "message": {
                                    "model": "claude-sonnet-4.6",
                                    "usage": {
                                        "input_tokens": 1100,
                                        "cache_read_input_tokens": 120,
                                        "cache_creation_input_tokens": 40,
                                        "output_tokens": 180,
                                    },
                                    "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "git status"}}],
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-07T11:05:00Z",
                                "type": "assistant",
                                "message": {
                                    "model": "claude-sonnet-4.6",
                                    "usage": {
                                        "input_tokens": 1200,
                                        "cache_read_input_tokens": 130,
                                        "cache_creation_input_tokens": 30,
                                        "output_tokens": 200,
                                    },
                                    "content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": "src/app.py"}}],
                                },
                            }
                        ),
                    ]
                )
                + "\n"
            )
            sessions_path.write_text(
                json.dumps({"sessions": [{"path": str(session_path), "project": "demo", "date": "2026-04-07"}]})
            )
            data = run_json("analyze_claude_sessions.py", sessions_path)

        session = data["sessions"][0]
        self.assertEqual(session["duration_minutes"], 125.0)
        self.assertEqual(session["active_session_duration_minutes"], 10.0)

    def test_codex_analysis_includes_confidence_and_pricing_metadata(self):
        data = run_json("analyze_codex_sessions.py", ROOT / "tests/fixtures/codex/sessions.json")
        self.assertEqual(data["analysis_confidence"]["label"], "measured")
        self.assertEqual(data["pricing_metadata"]["canonical_model"], "gpt-5.4")
        self.assertEqual(data["pricing_metadata"]["billing_mode"], "full_billing")

    def test_codex_analysis_keeps_log_duration_and_adds_active_duration_when_timestamps_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            session_path = base / "session.jsonl"
            sessions_path = base / "sessions.json"
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "session_meta", "payload": {"timestamp": "2026-04-07T10:00:00Z", "model": "gpt-5.4"}}),
                        json.dumps({"type": "turn_context", "timestamp": "2026-04-07T10:00:00Z", "payload": {"turn_id": "t1", "model": "gpt-5.4"}}),
                        json.dumps({"type": "response_item", "timestamp": "2026-04-07T10:00:10Z", "payload": {"type": "message", "role": "assistant", "phase": "analysis", "content": [{"type": "output_text", "text": "Inspecting."}]}}),
                        json.dumps({"type": "response_item", "timestamp": "2026-04-07T10:05:00Z", "payload": {"type": "function_call", "name": "exec_command", "arguments": "{\"cmd\":\"git status\"}"}}),
                        json.dumps({"type": "event_msg", "timestamp": "2026-04-07T10:05:05Z", "payload": {"type": "token_count", "info": {"last_token_usage": {"input_tokens": 900, "cached_input_tokens": 400, "output_tokens": 120, "reasoning_output_tokens": 30}}}}),
                        json.dumps({"type": "turn_context", "timestamp": "2026-04-07T12:05:00Z", "payload": {"turn_id": "t2", "model": "gpt-5.4"}}),
                        json.dumps({"type": "response_item", "timestamp": "2026-04-07T12:05:10Z", "payload": {"type": "message", "role": "assistant", "phase": "analysis", "content": [{"type": "output_text", "text": "Applying patch."}]}}),
                        json.dumps({"type": "response_item", "timestamp": "2026-04-07T12:05:20Z", "payload": {"type": "function_call", "name": "apply_patch", "arguments": "{\"patch\":\"*** Begin Patch\\n*** End Patch\\n\"}"}}),
                        json.dumps({"type": "event_msg", "timestamp": "2026-04-07T12:05:30Z", "payload": {"type": "token_count", "info": {"last_token_usage": {"input_tokens": 1100, "cached_input_tokens": 500, "output_tokens": 160, "reasoning_output_tokens": 40}}}}),
                    ]
                )
                + "\n"
            )
            sessions_path.write_text(
                json.dumps({"sessions": [{"path": str(session_path), "project": "demo", "date": "2026-04-07"}]})
            )
            data = run_json("analyze_codex_sessions.py", sessions_path)

        session = data["sessions"][0]
        self.assertEqual(session["duration_minutes"], 125.5)
        self.assertEqual(session["active_session_duration_minutes"], 10.6)

    def test_explain_surfaces_registry_and_confidence(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        fixture_path = ROOT / "tests/fixtures/tmp-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            lesson = run_json("explain.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(lesson["pricing_registry"]["registry_version"], "2026-04-08")
        self.assertEqual(lesson["analysis_confidence"]["label"], "measured")
        self.assertEqual(lesson["pricing_registry"]["billing_mode"], "full_billing")
        self.assertEqual(lesson["behavior_guidance"]["session_slicing"]["recommended_active_minutes"], "A good default is 5-10 active minutes per focused session.")
        self.assertTrue(lesson["behavior_guidance"]["handoff_skill"]["recommended"])
        self.assertEqual(lesson["behavior_guidance"]["handoff_skill"]["install_mode"], "static_github_prompt_only")
        self.assertEqual(lesson["behavior_guidance"]["handoff_skill"]["repo_url"], "https://github.com/wallmage/handoff")
        self.assertIn("https://github.com/wallmage/handoff", lesson["behavior_guidance"]["handoff_skill"]["install_prompt_template"])

    def test_report_prints_confidence_and_pricing_basis(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        fixture_path = ROOT / "tests/fixtures/tmp-report-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(fixture_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertIn("Confidence:", result.stdout)
        self.assertIn("Pricing registry:", result.stdout)
        self.assertIn("Billing mode:", result.stdout)

    def test_report_handles_empty_analysis_without_crashing(self):
        analysis = {
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "date_range": None,
                "total_cost": 0,
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "avg_cost_per_turn": 0,
                "total_waste": 0,
                "waste_per_session": 0,
                "waste_percentage": 0,
                "projected_cost_after_fix": 0,
            },
            "sessions": [],
            "waste_breakdown": {},
            "tool_mix": {},
            "model_mix": {},
            "analysis_confidence": {"label": "estimated", "score": 0, "reason": "none"},
            "pricing_metadata": {"provider": "unknown", "billing_mode": "token_only_estimate"},
        }
        fixture_path = ROOT / "tests/fixtures/tmp-empty-report-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(fixture_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Sessions analyzed:   0", result.stdout)
        self.assertIn("Period:              unavailable", result.stdout)

    def test_report_handles_missing_waste_breakdown_without_crashing(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "date_range": "2026-04-09 to 2026-04-09",
                "total_cost": 1.0,
                "avg_cost_per_session": 1.0,
                "avg_turns_per_session": 2.0,
                "avg_cost_per_turn": 0.5,
                "total_waste": 0,
                "waste_per_session": 0,
                "waste_percentage": 0,
                "projected_cost_after_fix": 1.0,
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-missing-waste-report-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(fixture_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Sessions analyzed:   1", result.stdout)
        self.assertIn("WASTE IDENTIFIED", result.stdout)

    def test_compare_handles_sparse_empty_snapshots_without_crashing(self):
        before = {
            "schema_version": 1,
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "total_cost": 0,
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "total_waste": 0,
                "waste_percentage": 0,
            },
            "waste_breakdown": {},
        }
        after = {
            "schema_version": 1,
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "total_cost": 0,
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "total_waste": 0,
                "waste_percentage": 0,
            },
            "waste_breakdown": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            before_path = Path(tmpdir) / "before.json"
            after_path = Path(tmpdir) / "after.json"
            before_path.write_text(json.dumps(before))
            after_path.write_text(json.dumps(after))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "compare.py"), str(after_path), str(before_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Period:              unavailable", result.stdout)
        self.assertIn("Sessions:            0", result.stdout)

    def test_compare_projected_view_handles_zero_context_window_without_crashing(self):
        current = {
            "schema_version": 1,
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "date_range": None,
                "total_cost": 0,
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "avg_context_window_tokens": 0,
                "avg_output_tokens_per_turn": 0,
                "waste_percentage": 0,
                "total_waste": 0,
                "waste_per_session": 0,
                "projected_cost_after_fix": 0,
            },
            "waste_breakdown": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            current_path = Path(tmpdir) / "current.json"
            current_path.write_text(json.dumps(current))
            env = dict(os.environ)
            env["HOME"] = tmpdir
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "compare.py"), str(current_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("PROJECTED — AFTER APPLYING FIXES", result.stdout)
        self.assertIn("Avg context window", result.stdout)

    def test_compare_ignores_auto_snapshot_without_measurable_sessions(self):
        current = {
            "summary": {
                "sessions": 2,
                "total_sessions": 2,
                "date_range": "2026-04-01 to 2026-04-02",
                "total_cost": 4.0,
                "avg_cost_per_session": 2.0,
                "avg_turns_per_session": 6.0,
                "avg_context_window_tokens": 1000,
                "avg_output_tokens_per_turn": 100,
                "avg_cost_per_turn": 0.33,
                "total_waste": 1.0,
                "waste_per_session": 0.5,
                "waste_percentage": 25.0,
                "projected_cost_after_fix": 1.5,
            },
            "waste_breakdown": {},
        }
        empty_snapshot = {
            "schema_version": 1,
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "total_cost": 0,
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "total_waste": 0,
                "waste_percentage": 0,
            },
            "waste_breakdown": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            current_path = Path(tmpdir) / "current.json"
            current_path.write_text(json.dumps(current))
            snapshot_dir = Path(tmpdir) / ".vibecheck" / "snapshots"
            snapshot_dir.mkdir(parents=True)
            (snapshot_dir / "snapshot_20260409_010203.json").write_text(json.dumps(empty_snapshot))
            env = dict(os.environ)
            env["HOME"] = tmpdir
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "compare.py"), str(current_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("PROJECTED — AFTER APPLYING FIXES", result.stdout)
        self.assertNotIn("BEFORE / AFTER COMPARISON", result.stdout)

    def test_monitor_handles_zero_cost_previous_week_without_crashing(self):
        analysis = {
            "sessions": [
                {
                    "timestamp": "2026-04-08T00:00:00+00:00",
                    "total_cost": 1.0,
                    "total_turns": 10,
                    "waste": {"idle_narration": {"cost": 0.1, "turns": 1}},
                },
                {
                    "timestamp": "2026-03-31T00:00:00+00:00",
                    "total_cost": 0.0,
                    "total_turns": 8,
                    "waste": {"idle_narration": {"cost": 0.0, "turns": 0}},
                },
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "monitor.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("ALERTS:", result.stdout)
        self.assertIn("Avg session cost up from $0.00 to $1.00", result.stdout)

    def test_monitor_handles_sessions_without_waste_map(self):
        analysis = {
            "sessions": [
                {
                    "timestamp": "2026-04-08T00:00:00+00:00",
                    "total_cost": 1.0,
                    "total_turns": 10,
                },
                {
                    "timestamp": "2026-03-31T00:00:00+00:00",
                    "total_cost": 0.5,
                    "total_turns": 8,
                    "waste": {"idle_narration": {"cost": 0.1, "turns": 1}},
                },
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "monitor.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("WEEKLY COST MONITOR", result.stdout)

    def test_monitor_previous_week_excludes_older_history(self):
        recent = "2026-04-08T00:00:00+00:00"
        previous_week = "2026-04-01T00:00:00+00:00"
        older = "2026-02-01T00:00:00+00:00"
        analysis = {
            "sessions": [
                {
                    "timestamp": recent,
                    "total_cost": 1.0,
                    "total_turns": 10,
                    "waste": {"idle_narration": {"cost": 0.1, "turns": 1}},
                },
                {
                    "timestamp": previous_week,
                    "total_cost": 2.0,
                    "total_turns": 8,
                    "waste": {"idle_narration": {"cost": 0.2, "turns": 2}},
                },
                {
                    "timestamp": older,
                    "total_cost": 20.0,
                    "total_turns": 80,
                    "waste": {"idle_narration": {"cost": 2.0, "turns": 20}},
                },
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "monitor.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("$2.00", result.stdout)
        self.assertNotIn("$11.00", result.stdout)

    def test_present_scan_outputs_result_first_payload(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        fixture_path = ROOT / "tests/fixtures/tmp-present-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", fixture_path, "/tmp/CLAUDE.md")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["visibility"], "result")
        self.assertEqual(payload["kind"], "scan_result")
        self.assertEqual(payload["run_state"]["state"], "completed")
        self.assertEqual(payload["summary"]["sessions_analyzed"], 1)
        self.assertEqual(payload["hero"]["eyebrow"], "Scan complete")
        self.assertEqual(payload["top_waste_patterns"][0]["key"], "idle_narration")
        self.assertEqual(
            [section["kind"] for section in payload["sections"]],
            ["hero", "metrics", "header_statistics", "patterns", "optimization_plan", "next_action"],
        )
        self.assertEqual(payload["next_action"]["instruction_file"], "CLAUDE.md")
        self.assertIn("Lead with this summary first", payload["education_bridge"])

    def test_explain_and_present_education_provide_fallback_guidance_for_empty_analysis(self):
        analysis = {
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "date_range": None,
                "total_cost": 0,
                "avg_cost_per_session": 0,
                "avg_turns_per_session": 0,
                "avg_cost_per_turn": 0,
                "total_waste": 0,
                "waste_per_session": 0,
                "waste_percentage": 0,
                "projected_cost_after_fix": 0,
            },
            "sessions": [],
            "waste_breakdown": {},
            "tool_mix": {},
            "model_mix": {},
            "analysis_confidence": {"label": "estimated", "score": 0, "reason": "none"},
            "pricing_metadata": {"provider": "unknown", "billing_mode": "token_only_estimate"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            analysis_path = base / "analysis.json"
            lesson_path = base / "lesson.json"
            analysis_path.write_text(json.dumps(analysis))
            lesson = run_json("explain.py", analysis_path)
            lesson_path.write_text(json.dumps(lesson))
            payload = run_json("present_education.py", lesson_path)

        self.assertNotIn("error", lesson)
        self.assertEqual(payload["context_window"]["headline"], "Long threads get more expensive and less sharp.")
        self.assertEqual(payload["session_habits"]["recommended_active_minutes"], "A good default is 5-10 active minutes per focused session.")
        self.assertTrue(payload["handoff"]["recommended"])

    def test_explain_uses_summary_period_days_for_monthly_projection(self):
        analysis = {
            "summary": {
                "sessions": 10,
                "total_sessions": 10,
                "date_range": "2026-04-01 to 2026-04-30",
                "total_cost": 30.0,
                "avg_cost_per_session": 3.0,
                "avg_turns_per_session": 5.0,
                "avg_cost_per_turn": 0.6,
                "total_waste": 6.0,
                "waste_per_session": 0.6,
                "waste_percentage": 20.0,
                "period_days": 30,
            },
            "sessions": [
                {
                    "date": "2026-04-02",
                    "total_cost": 30.0,
                    "total_turns": 50,
                    "total_cache_read": 0,
                    "total_cache_create": 0,
                    "total_output_tokens": 0,
                    "model": "sonnet",
                    "waste": {"idle_narration": {"cost": 6.0}},
                }
            ],
            "waste_breakdown": {},
            "model_mix": {"sonnet": {"sessions": 10, "total_cost": 30.0, "avg_cost": 3.0, "avg_turns": 5.0}},
            "tool_mix": {},
            "analysis_confidence": {"label": "estimated", "score": 0.5, "reason": "fixture"},
            "pricing_metadata": {"provider": "anthropic", "billing_mode": "token_only_estimate"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            lesson = run_json("explain.py", analysis_path)

        self.assertEqual(lesson["usage_summary"]["daily_cost"], 1.0)
        self.assertEqual(lesson["usage_summary"]["monthly_projected"], 30.0)

    def test_compare_uses_period_days_for_monthly_projection(self):
        current = {
            "summary": {
                "sessions": 10,
                "total_sessions": 10,
                "date_range": "2026-04-01 to 2026-04-30",
                "period_days": 30,
                "total_cost": 30.0,
                "avg_cost_per_session": 3.0,
                "avg_turns_per_session": 5.0,
                "avg_context_window_tokens": 1000,
                "avg_output_tokens_per_turn": 100,
                "avg_cost_per_turn": 0.6,
                "total_waste": 6.0,
                "waste_per_session": 0.6,
                "waste_percentage": 20.0,
                "projected_cost_after_fix": 2.4,
            },
            "waste_breakdown": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            current_path = Path(tmpdir) / "current.json"
            current_path.write_text(json.dumps(current))
            env = dict(os.environ)
            env["HOME"] = tmpdir
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "compare.py"), str(current_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Your pace: 0.3 sessions/day", result.stdout)
        self.assertIn("Potential: $0.60/session -> ~$6/month", result.stdout.replace("→", "->"))

    def test_merge_entries_keeps_projected_cost_after_fix_as_per_session_average(self):
        from merge_analyses import merge_entries

        entries = [
            {
                "tool_id": "claude_code",
                "tool_name": "Claude Code",
                "analysis_mode": "claude_jsonl",
                "analysis": {
                    "summary": {
                        "sessions": 10,
                        "total_sessions": 10,
                        "total_cost": 100.0,
                        "total_turns": 50,
                        "total_waste": 40.0,
                        "projected_cost_after_fix": 6.0,
                    },
                    "sessions": [{"timestamp": f"2026-04-01T00:00:{i:02d}Z"} for i in range(10)],
                },
            },
            {
                "tool_id": "codex",
                "tool_name": "OpenAI Codex CLI",
                "analysis_mode": "codex_jsonl",
                "analysis": {
                    "summary": {
                        "sessions": 20,
                        "total_sessions": 20,
                        "total_cost": 50.0,
                        "total_turns": 40,
                        "total_waste": 10.0,
                        "projected_cost_after_fix": 2.0,
                    },
                    "sessions": [{"timestamp": f"2026-04-02T00:00:{i:02d}Z"} for i in range(20)],
                },
            },
        ]

        merged = merge_entries(entries)

        self.assertEqual(merged["summary"]["total_cost"], 150.0)
        self.assertEqual(merged["summary"]["total_waste"], 50.0)
        self.assertEqual(merged["summary"]["projected_cost_after_fix"], 3.33)

    def test_report_uses_period_days_and_derived_waste_per_session(self):
        analysis = {
            "summary": {
                "sessions": 10,
                "total_sessions": 10,
                "date_range": "2026-04-01 to 2026-04-30",
                "period_days": 30,
                "total_cost": 30.0,
                "avg_cost_per_session": 3.0,
                "projected_cost_after_fix": 2.4,
                "total_waste": 6.0,
                "waste_percentage": 20.0,
            },
            "waste_breakdown": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            env = dict(os.environ)
            env["HOME"] = tmpdir
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Total waste:         $0.600/session (20% of spend)", result.stdout)
        self.assertIn("At your pace (0.3 sessions/day):", result.stdout)
        self.assertIn("Monthly savings:   $6", result.stdout)

    def test_report_auto_saves_markdown_report(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "date_range": "2026-04-09 to 2026-04-09",
                "total_cost": 1.0,
                "avg_cost_per_session": 1.0,
                "avg_turns_per_session": 2.0,
                "avg_cost_per_turn": 0.5,
                "total_waste": 0.25,
                "waste_per_session": 0.25,
                "waste_percentage": 25.0,
                "projected_cost_after_fix": 0.75,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.25,
                    "total_cost": 0.25,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call.",
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(analysis_path)],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            exported = sorted(Path(tmpdir).glob("vibecheck-report-*.md"))
            exported_content = exported[0].read_text() if exported else ""

        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(exported), 1)
        self.assertIn("Saved report:", result.stdout)
        self.assertIn("# VibeCheck Scan Complete", exported_content)

    def test_report_handles_partial_confidence_metadata(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "total_cost": 1.0,
                "avg_cost_per_session": 1.0,
            },
            "analysis_confidence": {"label": "estimated"},
            "waste_breakdown": {},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Confidence:          estimated (0.50)", result.stdout)
        self.assertIn("Confidence metadata was not included in this analysis.", result.stdout)

    def test_report_handles_sparse_waste_breakdown(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "total_cost": 1.0,
                "avg_cost_per_session": 1.0,
                "total_waste": 0.5,
                "waste_percentage": 50.0,
            },
            "analysis_confidence": {"label": "estimated", "score": 0.5, "reason": "fixture"},
            "waste_breakdown": {"idle_narration": {"per_session": 0.5}},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("idle_narration:", result.stdout)
        self.assertIn("Cost: $0.500/session (100% of waste)", result.stdout)

    def test_compare_handles_sparse_waste_breakdown(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "total_cost": 1.0,
                "avg_cost_per_session": 1.0,
                "total_waste": 0.5,
                "waste_percentage": 50.0,
            },
            "waste_breakdown": {"idle_narration": {"per_session": 0.5}},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            env = dict(os.environ)
            env["HOME"] = tmpdir
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "compare.py"), str(analysis_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("idle_narration", result.stdout)
        self.assertIn("$   0.50  (100%)", result.stdout)

    def test_explain_prefers_date_range_over_active_days_when_period_days_missing(self):
        analysis = {
            "summary": {
                "sessions": 2,
                "total_sessions": 2,
                "date_range": "2026-04-01 to 2026-04-30",
                "total_cost": 10.0,
                "avg_cost_per_session": 5.0,
                "avg_turns_per_session": 4.0,
                "avg_cost_per_turn": 1.25,
                "total_waste": 2.0,
                "waste_percentage": 20.0,
            },
            "sessions": [
                {
                    "date": "2026-04-01",
                    "total_cost": 5.0,
                    "total_turns": 4,
                    "total_cache_read": 0,
                    "total_cache_create": 0,
                    "total_output_tokens": 0,
                    "model": "sonnet",
                    "waste": {"idle_narration": {"cost": 1.0}},
                },
                {
                    "date": "2026-04-02",
                    "total_cost": 5.0,
                    "total_turns": 4,
                    "total_cache_read": 0,
                    "total_cache_create": 0,
                    "total_output_tokens": 0,
                    "model": "sonnet",
                    "waste": {"idle_narration": {"cost": 1.0}},
                },
            ],
            "waste_breakdown": {},
            "model_mix": {"sonnet": {"sessions": 2, "total_cost": 10.0, "avg_cost": 5.0, "avg_turns": 4.0}},
            "tool_mix": {},
            "analysis_confidence": {"label": "estimated", "score": 0.5, "reason": "fixture"},
            "pricing_metadata": {"provider": "anthropic", "billing_mode": "token_only_estimate"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            lesson = run_json("explain.py", analysis_path)

        self.assertEqual(lesson["usage_summary"]["daily_cost"], 0.33)
        self.assertEqual(lesson["usage_summary"]["monthly_projected"], 10.0)

    def test_explain_handles_mixed_models_on_same_day(self):
        analysis = {
            "summary": {
                "sessions": 2,
                "total_sessions": 2,
                "date_range": "2026-04-01 to 2026-04-01",
                "period_days": 1,
                "total_cost": 10.0,
                "avg_cost_per_session": 5.0,
                "avg_turns_per_session": 2.0,
                "avg_cost_per_turn": 2.5,
                "total_waste": 0.0,
                "waste_percentage": 0.0,
            },
            "sessions": [
                {
                    "date": "2026-04-01",
                    "total_cost": 5.0,
                    "total_turns": 2,
                    "total_cache_read": 0,
                    "total_cache_create": 0,
                    "total_output_tokens": 100000,
                    "model": "sonnet",
                    "waste": {},
                },
                {
                    "date": "2026-04-01",
                    "total_cost": 5.0,
                    "total_turns": 2,
                    "total_cache_read": 0,
                    "total_cache_create": 0,
                    "total_output_tokens": 100000,
                    "model": "deepseek-chat",
                    "waste": {},
                },
            ],
            "waste_breakdown": {},
            "model_mix": {
                "sonnet": {"sessions": 1, "total_cost": 5.0, "avg_cost": 5.0, "avg_turns": 2.0},
                "deepseek-chat": {"sessions": 1, "total_cost": 5.0, "avg_cost": 5.0, "avg_turns": 2.0},
            },
            "tool_mix": {},
            "analysis_confidence": {"label": "estimated", "score": 0.5, "reason": "fixture"},
            "pricing_metadata": {"provider": "anthropic", "billing_mode": "token_only_estimate"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))
            lesson = run_json("explain.py", analysis_path)

        self.assertEqual(lesson["worst_day"]["model"], "mixed")
        self.assertEqual(lesson["worst_day"]["cost_breakdown"]["output"]["cost"], 1.54)
        self.assertEqual(lesson["worst_day"]["cost_breakdown"]["fresh_input"]["cost"], 8.46)

    def test_present_scan_prefers_date_range_over_active_days_for_monthly_savings(self):
        analysis = {
            "summary": {
                "sessions": 2,
                "total_sessions": 2,
                "date_range": "2026-04-01 to 2026-04-30",
                "total_cost": 10.0,
                "avg_cost_per_session": 5.0,
                "avg_turns_per_session": 4.0,
                "avg_cost_per_turn": 1.25,
                "total_waste": 2.0,
                "waste_per_session": 1.0,
                "waste_percentage": 20.0,
            },
            "sessions": [
                {
                    "date": "2026-04-01",
                    "tool": "claude_code",
                    "model": "sonnet",
                    "total_cost": 5.0,
                    "total_turns": 4,
                    "waste": {"idle_narration": {"cost": 1.0, "description": "idle"}},
                },
                {
                    "date": "2026-04-02",
                    "tool": "claude_code",
                    "model": "sonnet",
                    "total_cost": 5.0,
                    "total_turns": 4,
                    "waste": {"idle_narration": {"cost": 1.0, "description": "idle"}},
                },
            ],
            "waste_breakdown": {
                "idle_narration": {
                    "total_cost": 2.0,
                    "per_session": 1.0,
                    "percentage_of_waste": 100.0,
                    "description": "idle",
                }
            },
            "tool_mix": {
                "claude_code": {"sessions": 2, "avg_cost": 5.0, "avg_turns": 4.0, "total_cost": 10.0}
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            instruction_path = Path(tmpdir) / "CLAUDE.md"
            analysis_path.write_text(json.dumps(analysis))
            instruction_path.write_text("# Claude\n")
            payload = run_json("present_scan.py", analysis_path, instruction_path)

        plan = payload["optimization_plan"]["tools"][0]
        self.assertEqual(plan["before_after"]["projected_monthly_savings"], 2.0)
        self.assertEqual(plan["steps"][0]["projected_monthly_savings"], 2.0)

    def test_present_scan_derives_tool_waste_ratio_when_tool_mix_omits_it(self):
        analysis = {
            "summary": {
                "sessions": 2,
                "total_sessions": 2,
                "date_range": "2026-04-01 to 2026-04-30",
                "total_cost": 10.0,
                "avg_cost_per_session": 5.0,
                "avg_turns_per_session": 4.0,
                "avg_cost_per_turn": 1.25,
                "total_waste": 2.0,
                "waste_per_session": 1.0,
                "waste_percentage": 20.0,
            },
            "sessions": [
                {
                    "date": "2026-04-01",
                    "tool": "claude_code",
                    "model": "sonnet",
                    "total_cost": 5.0,
                    "total_turns": 4,
                    "waste": {"idle_narration": {"cost": 1.0, "description": "idle"}},
                },
                {
                    "date": "2026-04-02",
                    "tool": "claude_code",
                    "model": "sonnet",
                    "total_cost": 5.0,
                    "total_turns": 4,
                    "waste": {"idle_narration": {"cost": 1.0, "description": "idle"}},
                },
            ],
            "waste_breakdown": {
                "idle_narration": {
                    "total_cost": 2.0,
                    "per_session": 1.0,
                    "percentage_of_waste": 100.0,
                    "description": "idle",
                }
            },
            "tool_mix": {
                "claude_code": {"sessions": 2, "avg_cost": 5.0, "avg_turns": 4.0, "total_cost": 10.0}
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_path = Path(tmpdir) / "analysis.json"
            instruction_path = Path(tmpdir) / "CLAUDE.md"
            analysis_path.write_text(json.dumps(analysis))
            instruction_path.write_text("# Claude\n")
            payload = run_json("present_scan.py", analysis_path, instruction_path)

        tool_stats = payload["header_statistics"]["tools"][0]
        self.assertEqual(tool_stats["avg_waste_ratio_pct"], 20.0)
        self.assertEqual(tool_stats["health"]["id"], "waste")

    def test_export_optimization_log_supports_final_success_payload(self):
        payload = {
            "kind": "optimization_final_success",
            "hero": {"headline": "Final summary"},
            "summary": {
                "tools_optimized": 1,
                "projected_monthly_savings": 5.0,
                "avg_cost_before": 2.0,
                "avg_cost_after": 1.0,
            },
            "top_tool_wins": [
                {
                    "tool_id": "codex",
                    "tool_label": "Codex",
                    "projected_monthly_savings": 5.0,
                    "avg_cost_before": 2.0,
                    "avg_cost_after": 1.0,
                }
            ],
            "education_next": {
                "title": "Next",
                "body": "Education follows.",
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "payload.json"
            dst = Path(tmpdir) / "out.md"
            src.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "export_optimization_log.py"), str(src), str(dst)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(dst.exists())
            markdown = dst.read_text()

        self.assertIn("Final summary", markdown)
        self.assertIn("Projected monthly savings", markdown)
        self.assertIn("Education follows.", markdown)

    def test_export_optimization_log_supports_education_payload(self):
        payload = {
            "kind": "optimization_education",
            "hero": {"headline": "Keep the gains"},
            "context_window": {"headline": "Context", "plain": "Trim old context."},
            "session_habits": {
                "headline": "Habits",
                "recommended_active_minutes": "5-10",
                "recommended_turn_ceiling": "30-40 turns",
            },
            "continuity_system": {
                "persistent_behavior": "Put durable rules in instruction files.",
                "project_docs": "Split project docs by topic.",
                "project_doc_structure": ["Architecture", "Roadmap"],
            },
            "handoff": {
                "recommended": True,
                "purpose": "Carry state to a fresh chat.",
                "how_to_use": "Say handoff.",
                "install_prompt": "Help me install this skill too: ...",
                "repo_url": "https://example.com/handoff",
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "payload.json"
            dst = Path(tmpdir) / "out.md"
            src.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "export_optimization_log.py"), str(src), str(dst)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(dst.exists())
            markdown = dst.read_text()

        self.assertIn("Keep the gains", markdown)
        self.assertIn("Trim old context.", markdown)
        self.assertIn("https://example.com/handoff", markdown)

    def test_present_scan_exposes_workflow_start_handoff(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        with tempfile.TemporaryDirectory() as tmpdir:
            fixture_path = Path(tmpdir) / "analysis.json"
            instruction_path = Path(tmpdir) / "CLAUDE.md"
            instruction_path.write_text("# Claude\n")
            fixture_path.write_text(json.dumps(analysis))
            payload = run_json("present_scan.py", fixture_path, instruction_path)
        self.assertIsNotNone(payload["optimization_plan"]["entry_tool_id"])
        self.assertEqual(
            payload["next_action"]["workflow"]["tool_id"],
            payload["optimization_plan"]["entry_tool_id"],
        )
        self.assertEqual(payload["next_action"]["workflow"]["step_rank"], 1)
        self.assertIn("present_next_workflow_item.py", payload["next_action"]["command"])

    def test_present_scan_does_not_crash_when_entry_tool_has_no_steps(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "avg_cost_per_session": 1.23,
                "waste_percentage": 40.0,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.5,
                    "total_cost": 0.5,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call and <150 output tokens (pure narration)",
                }
            },
            "tool_mix": {
                "claude_code": {"name": "Claude Code", "sessions": 1, "total_cost": 1.23, "waste_pct": 40.0, "analysis_mode": "claude_jsonl"},
            },
            "sessions": [
                {
                    "source_tool": "claude_code",
                    "source_tool_name": "Claude Code",
                    "model": "claude-sonnet-4.6",
                    "total_turns": 10,
                    "total_cost": 1.23,
                    "waste": {
                        "idle_narration": {"cost": 0.5, "description": "Turns with no tool call and <150 output tokens (pure narration)"},
                    },
                }
            ],
            "installed_tools": [
                {"id": "claude_code", "name": "Claude Code", "support_level": "full", "can_analyze": True, "analysis_mode": "claude_jsonl", "log_count": 3},
            ],
            "optimization_targets": [],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-empty-steps-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertIsNone(payload["optimization_plan"]["entry_tool_id"])
        self.assertNotIn("workflow", payload["next_action"])

    def test_present_scan_emits_calm_empty_state_for_zero_sessions(self):
        analysis = {
            "summary": {
                "sessions": 0,
                "total_sessions": 0,
                "avg_cost_per_session": 0,
                "waste_percentage": 0,
            },
            "waste_breakdown": {},
        }
        fixture_path = ROOT / "tests/fixtures/tmp-empty-present-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", fixture_path, "/tmp/CLAUDE.md")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["kind"], "scan_result")
        self.assertEqual(payload["run_state"]["state"], "completed")
        self.assertEqual(payload["summary"]["sessions_analyzed"], 0)
        self.assertEqual(payload["top_waste_patterns"], [])
        self.assertEqual(
            [section["kind"] for section in payload["sections"]],
            ["hero", "metrics", "next_action"],
        )
        self.assertEqual(payload["next_action"]["instruction_file"], "CLAUDE.md")

    def test_scan_presentation_contract_lists_exact_visibilities_and_stages(self):
        contract = json.loads((ROOT / "references/scan-presentation-contract.json").read_text())
        self.assertEqual(contract, build_contract_dict())
        self.assertEqual(contract["visibility_values"], ["internal", "progress", "result", "approval"])
        self.assertEqual(
            contract["progress_stages"],
            [
                "Checking your setup",
                "Finding recent sessions",
                "Analyzing waste patterns",
                "Preparing your report",
            ],
        )
        self.assertTrue(contract["transcript_rules"]["hide_internal_from_primary_transcript"])
        self.assertEqual(contract["transcript_rules"]["max_visible_progress_items"], 1)
        self.assertEqual(contract["payload_kinds"]["internal"], "scan_internal")
        self.assertEqual(contract["payload_kinds"]["progress"], "scan_progress")
        self.assertEqual(contract["payload_kinds"]["approval"], "scan_approval")
        self.assertEqual(contract["payload_kinds"]["failure"], "scan_failure")
        self.assertEqual(contract["payload_examples"]["result"]["run_state"]["state"], "completed")
        self.assertEqual(
            contract["validation_rules"]["internal_event_types"],
            ["detect", "find", "analyze", "explain", "present", "report", "export"],
        )
        self.assertEqual(
            contract["validation_rules"]["summary_metric_ids"],
            ["sessions", "avg_cost_per_session", "waste_percentage"],
        )
        self.assertEqual(
            contract["validation_rules"]["result_section_kinds"],
            ["hero", "metrics", "header_statistics", "patterns", "optimization_plan", "next_action"],
        )

    def test_scan_state_internal_payload_is_never_user_facing(self):
        payload = run_json("scan_state.py", "internal", "analyze", "Analyzer wrote structured output to a temp file.")
        self.assertEqual(payload["visibility"], "internal")
        self.assertEqual(payload["kind"], "scan_internal")
        self.assertEqual(payload["run_state"]["state"], "running")
        self.assertEqual(payload["event"]["type"], "analyze")

    def test_scan_state_progress_payload_uses_exact_stage(self):
        payload = run_json("scan_state.py", "progress", "Analyzing waste patterns")
        self.assertEqual(payload["visibility"], "progress")
        self.assertEqual(payload["kind"], "scan_progress")
        self.assertEqual(payload["run_state"]["state"], "running")
        self.assertEqual(payload["run_state"]["stage"], "Analyzing waste patterns")
        self.assertEqual(payload["message"], "Analyzing waste patterns")

    def test_scan_state_approval_payload_is_single_command_card(self):
        payload = run_json(
            "scan_state.py",
            "approval",
            "Export recent logs",
            "I need one export command because this environment cannot read your local logs directly.",
            "python3 SKILL_DIR/scripts/export_logs.py",
        )
        self.assertEqual(payload["visibility"], "approval")
        self.assertEqual(payload["kind"], "scan_approval")
        self.assertEqual(payload["run_state"]["state"], "idle")
        self.assertEqual(payload["card"]["title"], "Export recent logs")
        self.assertEqual(payload["card"]["command"], "python3 SKILL_DIR/scripts/export_logs.py")

    def test_scan_state_failure_payload_hides_technical_details_by_default(self):
        payload = run_json(
            "scan_state.py",
            "failure",
            "I couldn't finish the scan.",
            "short stderr excerpt",
        )
        self.assertEqual(payload["visibility"], "result")
        self.assertEqual(payload["kind"], "scan_failure")
        self.assertEqual(payload["run_state"]["state"], "failed")
        self.assertEqual(payload["error"]["technical_details_disclosure_label"], "Technical details")
        self.assertEqual(payload["error"]["technical_details_default"], "collapsed")
        self.assertEqual(payload["error"]["technical_details"], "short stderr excerpt")

    def test_scan_state_rejects_invalid_progress_stage(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scan_state.py"), "progress", "Doing random stuff"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid stage", result.stderr)

    def test_validate_scan_payload_accepts_generated_result_payload(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        analysis_path = ROOT / "tests/fixtures/tmp-validate-analysis.json"
        payload_path = ROOT / "tests/fixtures/tmp-validate-payload.json"
        analysis_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", analysis_path, "/tmp/CLAUDE.md")
            payload_path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_scan_payload.py"), str(payload_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            analysis_path.unlink(missing_ok=True)
            payload_path.unlink(missing_ok=True)
        self.assertEqual(result.stdout.strip(), "OK")

    def test_merge_analyses_builds_unified_machine_scan(self):
        claude = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        codex = run_json("analyze_codex_sessions.py", ROOT / "tests/fixtures/codex/sessions.json")
        claude["scan_tool_name"] = "Claude Code"
        claude["scan_analysis_mode"] = "claude_jsonl"
        claude["instruction_targets"] = [{"tool": "claude_code", "tool_name": "Claude Code", "file": "/tmp/CLAUDE.md", "filename": "CLAUDE.md"}]
        codex["scan_tool_name"] = "OpenAI Codex CLI"
        codex["scan_analysis_mode"] = "codex_jsonl"
        codex["instruction_targets"] = [{"tool": "codex", "tool_name": "OpenAI Codex CLI", "file": "/tmp/AGENTS.md", "filename": "AGENTS.md"}]
        claude_path = ROOT / "tests/fixtures/tmp-claude-merged.json"
        codex_path = ROOT / "tests/fixtures/tmp-codex-merged.json"
        claude_path.write_text(json.dumps(claude))
        codex_path.write_text(json.dumps(codex))
        try:
            merged = run_json("merge_analyses.py", f"claude_code={claude_path}", f"codex={codex_path}")
        finally:
            claude_path.unlink(missing_ok=True)
            codex_path.unlink(missing_ok=True)
        self.assertEqual(merged["summary"]["sessions"], 2)
        self.assertEqual(merged["summary"]["tools_scanned"], 2)
        self.assertEqual(merged["scan_scope"]["mode"], "all_detected_tools")
        self.assertEqual(set(merged["tool_mix"].keys()), {"claude_code", "codex"})
        self.assertEqual(set(merged["provider_mix"].keys()), {"anthropic", "openai"})
        self.assertEqual(merged["pricing_metadata"]["provider"], "multi")
        self.assertEqual(len(merged["instruction_targets"]), 2)

    def test_present_scan_surfaces_unified_breakdowns_for_merged_analysis(self):
        claude = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        codex = run_json("analyze_codex_sessions.py", ROOT / "tests/fixtures/codex/sessions.json")
        claude["scan_tool_name"] = "Claude Code"
        claude["scan_analysis_mode"] = "claude_jsonl"
        codex["scan_tool_name"] = "OpenAI Codex CLI"
        codex["scan_analysis_mode"] = "codex_jsonl"
        claude_path = ROOT / "tests/fixtures/tmp-claude-present-merged.json"
        codex_path = ROOT / "tests/fixtures/tmp-codex-present-merged.json"
        merged_path = ROOT / "tests/fixtures/tmp-merged-present-analysis.json"
        claude_path.write_text(json.dumps(claude))
        codex_path.write_text(json.dumps(codex))
        try:
            merged = run_json("merge_analyses.py", f"claude_code={claude_path}", f"codex={codex_path}")
            merged_path.write_text(json.dumps(merged))
            payload = run_json("present_scan.py", merged_path)
        finally:
            claude_path.unlink(missing_ok=True)
            codex_path.unlink(missing_ok=True)
            merged_path.unlink(missing_ok=True)
        self.assertEqual(payload["unified_scan"]["mode"], "all_detected_tools")
        self.assertEqual(payload["unified_scan"]["tools_scanned"], 2)
        self.assertEqual(len(payload["breakdowns"]["tools"]), 2)
        self.assertEqual(len(payload["breakdowns"]["providers"]), 2)
        self.assertTrue(len(payload["breakdowns"]["models"]) >= 2)

    def test_present_scan_surfaces_coverage_for_unsupported_and_skipped_tools(self):
        merged = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "avg_cost_per_session": 1.23,
                "waste_percentage": 40.0,
                "tools_scanned": 1,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.5,
                    "total_cost": 0.5,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call and <150 output tokens (pure narration)",
                }
            },
            "scan_scope": {"mode": "all_detected_tools"},
            "tool_mix": {"claude_code": {"name": "Claude Code", "sessions": 1, "total_cost": 1.23, "waste_pct": 40.0}},
            "provider_mix": {},
            "model_mix": {},
            "platform_mix": {},
            "installed_tools": [{"id": "claude_code"}, {"id": "gemini_cli"}],
            "unsupported_tools": [{"id": "gemini_cli", "name": "Gemini CLI", "support_level": "limited"}],
            "skipped_tools": [{"tool_id": "openclaw", "tool_name": "OpenClaw", "reason": "no_logs"}],
            "failed_tools": [{"tool_id": "workbuddy", "tool_name": "WorkBuddy", "stage": "analyze"}],
            "instruction_targets": [],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-coverage-present-analysis.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["unified_scan"]["tools_detected"], 2)
        self.assertEqual(payload["unified_scan"]["tools_unsupported"], 1)
        self.assertEqual(payload["unified_scan"]["tools_skipped"], 1)
        self.assertEqual(payload["unified_scan"]["tools_failed"], 1)
        self.assertEqual(payload["coverage"]["unsupported_tools"][0]["id"], "gemini_cli")
        self.assertEqual(payload["coverage"]["skipped_tools"][0]["id"], "openclaw")
        self.assertEqual(payload["coverage"]["failed_tools"][0]["id"], "workbuddy")

    def test_present_scan_builds_detected_tool_inventory_for_all_installed_tools(self):
        merged = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "avg_cost_per_session": 1.23,
                "waste_percentage": 40.0,
                "tools_scanned": 1,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.5,
                    "total_cost": 0.5,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call and <150 output tokens (pure narration)",
                }
            },
            "scan_scope": {"mode": "all_detected_tools"},
            "tool_mix": {
                "claude_code": {
                    "name": "Claude Code",
                    "sessions": 1,
                    "total_cost": 1.23,
                    "waste_pct": 40.0,
                    "analysis_mode": "claude_jsonl",
                }
            },
            "provider_mix": {},
            "model_mix": {},
            "platform_mix": {},
            "installed_tools": [
                {"id": "claude_code", "name": "Claude Code", "support_level": "full", "can_analyze": True, "analysis_mode": "claude_jsonl"},
                {"id": "gemini_cli", "name": "Gemini CLI", "support_level": "limited", "can_analyze": False, "analysis_mode": "instruction_only"},
                {"id": "openclaw", "name": "OpenClaw", "support_level": "full", "can_analyze": True, "analysis_mode": "openclaw_jsonl"},
                {"id": "workbuddy", "name": "WorkBuddy", "support_level": "full", "can_analyze": True, "analysis_mode": "workbuddy_hybrid"},
            ],
            "unsupported_tools": [{"id": "gemini_cli", "name": "Gemini CLI", "support_level": "limited"}],
            "skipped_tools": [{"tool_id": "openclaw", "tool_name": "OpenClaw", "reason": "no_logs"}],
            "failed_tools": [{"tool_id": "workbuddy", "tool_name": "WorkBuddy", "stage": "analyze"}],
            "instruction_targets": [
                {"tool": "claude_code", "tool_name": "Claude Code", "file": "/tmp/CLAUDE.md", "filename": "CLAUDE.md"},
                {"tool": "gemini_cli", "tool_name": "Gemini CLI", "file": "/tmp/GEMINI.md", "filename": "GEMINI.md"},
            ],
            "optimization_targets": [
                {"tool": "claude_code", "tool_name": "Claude Code", "file": "/tmp/CLAUDE.md", "kind": "instruction_file"},
                {"tool": "gemini_cli", "tool_name": "Gemini CLI", "file": "/tmp/.gemini/settings.json", "kind": "config_path"},
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-tool-inventory-analysis.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(len(payload["breakdowns"]["tools"]), 4)
        self.assertEqual(payload["coverage"]["detected_tools"][0]["id"], "claude_code")
        self.assertEqual(payload["coverage"]["detected_tools"][0]["status"], "scanned")
        self.assertEqual(payload["coverage"]["detected_tools"][1]["status"], "unsupported")
        self.assertEqual(payload["coverage"]["detected_tools"][2]["status"], "skipped")
        self.assertEqual(payload["coverage"]["detected_tools"][3]["status"], "failed")
        self.assertEqual(payload["coverage"]["detected_tools"][0]["optimization_targets"], 1)
        self.assertEqual(payload["coverage"]["detected_tools"][1]["optimization_targets"], 0)
        self.assertEqual(len(payload["optimization_targets"]), 2)
        self.assertEqual(payload["optimization_targets"][0]["kind"], "instruction_file")
        self.assertEqual(payload["optimization_targets"][1]["kind"], "config_path")

    def test_present_scan_adds_current_instruction_file_as_fallback_when_global_target_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            instruction_path = base / "AGENTS.md"
            instruction_path.write_text("# local rules\n")
            analysis = {
                "summary": {
                    "sessions": 1,
                    "total_sessions": 1,
                    "avg_cost_per_session": 1.20,
                    "waste_percentage": 30.0,
                },
                "waste_breakdown": {
                    "idle_narration": {
                        "per_session": 0.2,
                        "total_cost": 0.2,
                        "percentage_of_waste": 100.0,
                        "description": "Turns with no tool call.",
                    }
                },
                "tool_mix": {
                    "codex": {
                        "name": "OpenAI Codex CLI",
                        "sessions": 1,
                        "total_cost": 1.20,
                        "waste_pct": 30.0,
                        "analysis_mode": "codex_jsonl",
                    }
                },
                "sessions": [
                    {
                        "source_tool": "codex",
                        "source_tool_name": "OpenAI Codex CLI",
                        "model": "gpt-5.4",
                        "total_turns": 12,
                        "total_cost": 1.20,
                        "waste": {
                            "idle_narration": {
                                "cost": 0.2,
                                "description": "Turns with no tool call.",
                            }
                        },
                    }
                ],
                "installed_tools": [
                    {
                        "id": "codex",
                        "name": "OpenAI Codex CLI",
                        "support_level": "full",
                        "can_analyze": True,
                        "analysis_mode": "codex_jsonl",
                    }
                ],
                "optimization_targets": [
                    {
                        "tool": "codex",
                        "tool_name": "OpenAI Codex CLI",
                        "file": "/Users/test/.codex/AGENTS.md",
                        "filename": "AGENTS.md",
                        "kind": "instruction_file",
                        "scope": "global",
                        "exists": False,
                        "action": "update",
                        "priority_band": "primary",
                        "source": "global_instruction",
                    }
                ],
            }
            analysis_path = base / "analysis.json"
            analysis_path.write_text(json.dumps(analysis))

            payload = run_json("present_scan.py", analysis_path, instruction_path)

        strategy = payload["optimization_plan"]["tools"][0]["optimization_strategy"]
        self.assertEqual(payload["optimization_plan"]["entry_tool_id"], "codex")
        self.assertEqual(payload["optimization_plan"]["tool_sequence"], ["codex"])
        self.assertEqual(strategy["mode"], "project_only")
        self.assertEqual(strategy["counts"]["effective"], 1)
        self.assertEqual(strategy["effective_targets"][0]["path"], str(instruction_path))
        self.assertEqual(payload["next_action"]["workflow"]["tool_id"], "codex")
        self.assertEqual(payload["optimization_targets"][-1]["path"], str(instruction_path))

    def test_present_scan_keeps_settings_only_targets_in_report_but_out_of_auto_apply_flow(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "avg_cost_per_session": 1.20,
                "waste_percentage": 30.0,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.2,
                    "total_cost": 0.2,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call.",
                }
            },
            "tool_mix": {
                "gemini_cli": {
                    "name": "Gemini CLI",
                    "sessions": 1,
                    "total_cost": 1.20,
                    "waste_pct": 30.0,
                    "analysis_mode": "instruction_only",
                }
            },
            "sessions": [
                {
                    "source_tool": "gemini_cli",
                    "source_tool_name": "Gemini CLI",
                    "model": "gemini-2.5-pro",
                    "total_turns": 12,
                    "total_cost": 1.20,
                    "waste": {
                        "idle_narration": {
                            "cost": 0.2,
                            "description": "Turns with no tool call.",
                        }
                    },
                }
            ],
            "installed_tools": [
                {
                    "id": "gemini_cli",
                    "name": "Gemini CLI",
                    "support_level": "limited",
                    "can_analyze": False,
                    "analysis_mode": "instruction_only",
                }
            ],
            "optimization_targets": [
                {
                    "tool": "gemini_cli",
                    "tool_name": "Gemini CLI",
                    "file": "/tmp/.gemini/settings.json",
                    "filename": "settings.json",
                    "kind": "config_path",
                    "scope": "global",
                    "exists": True,
                    "action": "update",
                    "priority_band": "secondary",
                    "source": "config",
                }
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-settings-only-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        tool = payload["optimization_plan"]["tools"][0]
        self.assertEqual(payload["coverage"]["detected_tools"][0]["optimization_targets"], 0)
        self.assertEqual(payload["optimization_targets"][0]["kind"], "config_path")
        self.assertEqual(tool["optimization_strategy"]["mode"], "settings_only")
        self.assertFalse(tool["can_auto_optimize"])
        self.assertEqual(tool["steps"], [])

    def test_present_scan_exposes_save_report_header_action(self):
        analysis = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "avg_cost_per_session": 1.2,
                "waste_percentage": 30.0,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.2,
                    "total_cost": 0.2,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call.",
                }
            },
            "sessions": [
                {
                    "source_tool": "codex",
                    "source_tool_name": "OpenAI Codex CLI",
                    "model": "gpt-5.4",
                    "total_turns": 12,
                    "total_cost": 1.2,
                    "waste": {
                        "idle_narration": {
                            "cost": 0.2,
                            "description": "Turns with no tool call.",
                        }
                    },
                }
            ],
            "tool_mix": {
                "codex": {
                    "name": "OpenAI Codex CLI",
                    "sessions": 1,
                    "total_cost": 1.2,
                    "waste_pct": 30.0,
                    "analysis_mode": "codex_jsonl",
                    "can_analyze": True,
                }
            },
            "optimization_targets": [
                {
                    "tool": "codex",
                    "tool_name": "OpenAI Codex CLI",
                    "file": "/tmp/AGENTS.md",
                    "filename": "AGENTS.md",
                    "kind": "instruction_file",
                    "scope": "project",
                    "exists": True,
                    "action": "update",
                    "priority_band": "primary",
                    "source": "project_instruction",
                }
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-save-report-analysis.json"
        fixture_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", fixture_path, "/tmp/AGENTS.md")
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["header_actions"][0]["id"], "save_report")
        self.assertEqual(payload["header_actions"][0]["label"], "Save Report")
        self.assertIn("export_optimization_log.py /tmp/vibecheck_result.json", payload["header_actions"][0]["command"])
        self.assertTrue(payload["header_actions"][0]["default_filename"].startswith("vibecheck-report-"))

    def test_find_optimization_targets_prefers_global_instruction_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            project_dir = base / "project"
            project_dir.mkdir()
            (project_dir / "AGENTS.md").write_text("# project\n")
            config_dir = base / ".fakecodex"
            config_dir.mkdir()
            (config_dir / "config.json").write_text("{}\n")
            (config_dir / "AGENTS.md").write_text("# global\n")

            fake_tools = {
                "fakecodex": {
                    "name": "Fake Codex",
                    "instruction_files": ["AGENTS.md"],
                    "log_paths": {},
                    "log_format": "unknown",
                    "detect_files": [str(config_dir)],
                    "config_paths": [str(config_dir / "config.json")],
                    "global_instruction_paths": [str(config_dir / "AGENTS.md")],
                }
            }
            with patch.object(detect_tool, "TOOLS", fake_tools):
                targets = detect_tool.find_optimization_targets(
                    project_dir,
                    installed_tools=[{"id": "fakecodex"}],
                )

        self.assertEqual(targets[0]["scope"], "global")
        self.assertEqual(targets[0]["priority_band"], "primary")
        self.assertTrue(targets[0]["exists"])
        self.assertEqual(targets[0]["action"], "update")
        self.assertEqual(targets[1]["kind"], "config_path")
        self.assertEqual(targets[1]["priority_band"], "secondary")
        self.assertEqual(targets[2]["scope"], "project")
        self.assertEqual(targets[2]["priority_band"], "fallback")

    def test_find_optimization_targets_does_not_surface_missing_global_instruction_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            project_dir = base / "project"
            project_dir.mkdir()
            (project_dir / "AGENTS.md").write_text("# project\n")
            config_dir = base / ".fakecodex"
            config_dir.mkdir()
            (config_dir / "config.json").write_text("{}\n")

            fake_tools = {
                "fakecodex": {
                    "name": "Fake Codex",
                    "instruction_files": ["AGENTS.md"],
                    "log_paths": {},
                    "log_format": "unknown",
                    "detect_files": [str(config_dir)],
                    "config_paths": [str(config_dir / "config.json")],
                    "global_instruction_paths": [str(config_dir / "missing-AGENTS.md")],
                }
            }
            with patch.object(detect_tool, "TOOLS", fake_tools):
                targets = detect_tool.find_optimization_targets(
                    project_dir,
                    installed_tools=[{"id": "fakecodex"}],
                )

        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[0]["scope"], "project")
        self.assertEqual(targets[1]["kind"], "config_path")

    def test_registry_includes_verified_global_paths_for_major_tools(self):
        self.assertEqual(
            detect_tool.TOOLS["github_copilot"]["global_instruction_paths"],
            [f"{detect_tool.COPILOT_HOME}/copilot-instructions.md"],
        )
        self.assertEqual(
            detect_tool.TOOLS["cline"]["global_instruction_paths"][0],
            str(Path(detect_tool.DOCUMENTS_HOME) / "Cline" / "Rules"),
        )
        self.assertEqual(
            detect_tool.TOOLS["windsurf"]["global_instruction_paths"],
            [f"{detect_tool.HOME}/.codeium/windsurf/memories/global_rules.md"],
        )
        self.assertEqual(
            detect_tool.TOOLS["augment"]["global_instruction_paths"],
            [f"{detect_tool.HOME}/.augment/rules"],
        )

    def test_detect_installed_tools_surfaces_global_settings_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            fake_root = base / ".faketool"
            fake_root.mkdir()
            fake_global = fake_root / "GLOBAL.md"
            fake_global.write_text("# global\n")

            fake_tools = {
                "faketool": {
                    "name": "Fake Tool",
                    "instruction_files": ["GLOBAL.md"],
                    "log_paths": {},
                    "log_format": "unknown",
                    "detect_files": [str(fake_root)],
                    "config_paths": [],
                    "global_instruction_paths": [str(fake_global)],
                    "global_settings_status": "verified",
                    "global_settings_note": "Official docs publish this path.",
                }
            }
            with patch.object(detect_tool, "TOOLS", fake_tools):
                installed = detect_tool.detect_installed_tools()
                targets = detect_tool.find_global_instruction_targets(installed)

        self.assertEqual(installed[0]["global_settings_status"], "verified")
        self.assertEqual(installed[0]["known_global_instruction_paths"], [str(fake_global)])
        self.assertEqual(targets[0]["file"], str(fake_global))

    def test_detect_tool_emits_documented_default_keys_when_no_tool_is_found(self):
        stdout = StringIO()
        with patch.object(detect_tool, "detect_installed_tools", return_value=[]), \
             patch.object(detect_tool, "find_global_instruction_targets", return_value=[]), \
             patch.object(detect_tool, "scan_project_for_tool", return_value=None), \
             patch.object(detect_tool, "find_instruction_file", return_value=None), \
             patch.object(detect_tool, "find_instruction_targets", return_value=[]), \
             patch.object(detect_tool, "find_optimization_targets", return_value=[]), \
             patch.object(detect_tool, "detect_remote_session", return_value={"is_ssh": False, "is_mobile_terminal": False, "note": None}), \
             patch.object(sys, "argv", ["detect_tool.py"]), \
             redirect_stdout(stdout):
            detect_tool.main()

        payload = json.loads(stdout.getvalue())
        self.assertIsNone(payload["primary_tool_name"])
        self.assertFalse(payload["can_analyze"])
        self.assertIsNone(payload["note"])
        self.assertEqual(payload["analysis_mode"], "instruction_only")
        self.assertEqual(payload["support_level"], "limited")

    def test_report_prints_tool_and_provider_breakdowns_for_merged_analysis(self):
        claude = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        codex = run_json("analyze_codex_sessions.py", ROOT / "tests/fixtures/codex/sessions.json")
        claude["scan_tool_name"] = "Claude Code"
        claude["scan_analysis_mode"] = "claude_jsonl"
        codex["scan_tool_name"] = "OpenAI Codex CLI"
        codex["scan_analysis_mode"] = "codex_jsonl"
        claude_path = ROOT / "tests/fixtures/tmp-claude-report-merged.json"
        codex_path = ROOT / "tests/fixtures/tmp-codex-report-merged.json"
        merged_path = ROOT / "tests/fixtures/tmp-merged-report-analysis.json"
        claude_path.write_text(json.dumps(claude))
        codex_path.write_text(json.dumps(codex))
        try:
            merged = run_json("merge_analyses.py", f"claude_code={claude_path}", f"codex={codex_path}")
            merged_path.write_text(json.dumps(merged))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(merged_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            claude_path.unlink(missing_ok=True)
            codex_path.unlink(missing_ok=True)
            merged_path.unlink(missing_ok=True)
        self.assertIn("TOOL BREAKDOWN", result.stdout)
        self.assertIn("PROVIDER MIX", result.stdout)

    def test_report_prints_all_detected_tools_in_one_table(self):
        merged = {
            "summary": {
                "date_range": "2026-04-01 to 2026-04-08",
                "sessions": 1,
                "total_cost": 1.23,
                "avg_cost_per_session": 1.23,
                "avg_turns_per_session": 4.0,
                "avg_cost_per_turn": 0.3075,
                "waste_per_session": 0.5,
                "waste_percentage": 40.0,
                "projected_cost_after_fix": 0.73,
                "tools_scanned": 1,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.5,
                    "total_cost": 0.5,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call and <150 output tokens (pure narration)",
                }
            },
            "analysis_confidence": {"label": "measured", "score": 0.94, "reason": "fixture"},
            "pricing_metadata": {"registry_label": "fixture", "billing_mode": "full_billing", "canonical_model": "multiple", "provider": "multi", "registry_version": "2026-04-08"},
            "scan_scope": {"mode": "all_detected_tools"},
            "tool_inventory": [
                {"id": "claude_code", "name": "Claude Code", "status": "scanned", "support_level": "full", "analysis_mode": "claude_jsonl", "sessions": 1, "total_cost": 1.23, "waste_pct": 40.0},
                {"id": "gemini_cli", "name": "Gemini CLI", "status": "unsupported", "support_level": "limited", "analysis_mode": "instruction_only", "sessions": 0, "total_cost": 0, "waste_pct": 0},
                {"id": "openclaw", "name": "OpenClaw", "status": "skipped", "support_level": "full", "analysis_mode": "openclaw_jsonl", "sessions": 0, "total_cost": 0, "waste_pct": 0},
                {"id": "workbuddy", "name": "WorkBuddy", "status": "failed", "support_level": "full", "analysis_mode": "workbuddy_hybrid", "sessions": 0, "total_cost": 0, "waste_pct": 0},
            ],
            "tool_mix": {
                "claude_code": {"name": "Claude Code", "sessions": 1, "total_cost": 1.23, "waste_pct": 40.0, "analysis_mode": "claude_jsonl"}
            },
            "provider_mix": {},
            "model_mix": {},
            "platform_mix": {},
            "unsupported_tools": [{"id": "gemini_cli", "name": "Gemini CLI", "support_level": "limited"}],
            "skipped_tools": [{"tool_id": "openclaw", "tool_name": "OpenClaw", "reason": "no_logs"}],
            "failed_tools": [{"tool_id": "workbuddy", "tool_name": "WorkBuddy", "stage": "analyze"}],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-report-tool-inventory.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(fixture_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertIn("ALL DETECTED TOOLS", result.stdout)
        self.assertIn("unsupported", result.stdout)
        self.assertIn("skipped", result.stdout)
        self.assertIn("failed", result.stdout)

    def test_report_prints_optimization_targets_section(self):
        merged = {
            "summary": {
                "date_range": "2026-04-01 to 2026-04-08",
                "sessions": 1,
                "total_cost": 1.23,
                "avg_cost_per_session": 1.23,
                "avg_turns_per_session": 4.0,
                "avg_cost_per_turn": 0.3075,
                "waste_per_session": 0.5,
                "waste_percentage": 40.0,
                "projected_cost_after_fix": 0.73,
                "tools_scanned": 1,
            },
            "waste_breakdown": {
                "idle_narration": {
                    "per_session": 0.5,
                    "total_cost": 0.5,
                    "percentage_of_waste": 100.0,
                    "description": "Turns with no tool call and <150 output tokens (pure narration)",
                }
            },
            "analysis_confidence": {"label": "measured", "score": 0.94, "reason": "fixture"},
            "pricing_metadata": {"registry_label": "fixture", "billing_mode": "full_billing", "canonical_model": "multiple", "provider": "multi", "registry_version": "2026-04-08"},
            "optimization_targets": [
                {"tool": "claude_code", "tool_name": "Claude Code", "file": "/tmp/CLAUDE.md", "filename": "CLAUDE.md", "kind": "instruction_file", "scope": "project"},
                {"tool": "gemini_cli", "tool_name": "Gemini CLI", "file": "/tmp/.gemini/settings.json", "filename": "settings.json", "kind": "config_path", "scope": "global"},
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-report-optimization-targets.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(fixture_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertIn("OPTIMIZATION TARGETS", result.stdout)
        self.assertIn("CLAUDE.md", result.stdout)
        self.assertIn("settings.json", result.stdout)

    def test_present_scan_builds_header_statistics_and_ranked_tool_plan(self):
        merged = {
            "summary": {
                "sessions": 3,
                "total_sessions": 3,
                "date_range": "2026-04-07 to 2026-04-08",
                "total_cost": 3.51,
                "avg_cost_per_session": 1.17,
                "avg_turns_per_session": 20.7,
                "avg_cost_per_turn": 0.0566,
                "total_waste": 0.79,
                "waste_per_session": 0.2633,
                "waste_percentage": 22.5,
                "projected_cost_after_fix": 0.91,
                "avg_context_window_tokens": 3733,
                "avg_output_tokens_per_turn": 190,
                "total_turns": 62,
                "tools_scanned": 2,
            },
            "waste_breakdown": {
                "verbose_output": {
                    "per_session": 0.19,
                    "total_cost": 0.57,
                    "percentage_of_waste": 72.2,
                    "description": "Large command output keeps bloating context long after the command finishes.",
                },
                "idle_narration": {
                    "per_session": 0.05,
                    "total_cost": 0.15,
                    "percentage_of_waste": 19.0,
                    "description": "Status-only turns that re-read the full conversation before acting.",
                },
                "duplicate_reads": {
                    "per_session": 0.0233,
                    "total_cost": 0.07,
                    "percentage_of_waste": 8.8,
                    "description": "Reading the same file again wastes a turn after the content is already in context.",
                },
            },
            "scan_scope": {"mode": "all_detected_tools"},
            "tool_mix": {
                "claude_code": {"name": "Claude Code", "sessions": 2, "total_cost": 3.02, "waste_pct": 37.0, "analysis_mode": "claude_jsonl"},
                "codex": {"name": "OpenAI Codex CLI", "sessions": 1, "total_cost": 0.49, "waste_pct": 5.0, "analysis_mode": "codex_jsonl"},
            },
            "model_mix": {
                "claude-sonnet-4.6": {"sessions": 2, "pct_sessions": 66.7, "total_cost": 3.02, "pct_cost": 86.0, "avg_cost": 1.51, "avg_turns": 28.0, "waste_pct": 37.0},
                "gpt-5.4": {"sessions": 1, "pct_sessions": 33.3, "total_cost": 0.49, "pct_cost": 14.0, "avg_cost": 0.49, "avg_turns": 6.0, "waste_pct": 5.0},
            },
            "provider_mix": {
                "anthropic": {"sessions": 2, "pct_sessions": 66.7, "total_cost": 3.02, "pct_cost": 86.0},
                "openai": {"sessions": 1, "pct_sessions": 33.3, "total_cost": 0.49, "pct_cost": 14.0},
            },
            "platform_mix": {
                "python": {"sessions": 2, "pct_sessions": 66.7, "total_cost": 2.11, "pct_cost": 60.1, "avg_cost": 1.06, "avg_turns": 17.0, "waste_pct": 28.0},
                "general": {"sessions": 1, "pct_sessions": 33.3, "total_cost": 1.4, "pct_cost": 39.9, "avg_cost": 1.4, "avg_turns": 28.0, "waste_pct": 14.0},
            },
            "sessions": [
                {
                    "source_tool": "claude_code",
                    "source_tool_name": "Claude Code",
                    "model": "claude-sonnet-4.6",
                    "total_turns": 30,
                    "total_cost": 1.60,
                    "duration_minutes": 24.0,
                    "active_session_duration_minutes": 19.0,
                    "start_context_window_tokens": 1800,
                    "end_context_window_tokens": 8200,
                    "waste": {
                        "verbose_output": {"cost": 0.33, "description": "Large command output keeps bloating context long after the command finishes."},
                        "idle_narration": {"cost": 0.18, "description": "Status-only turns that re-read the full conversation before acting."},
                        "duplicate_reads": {"cost": 0.05, "description": "Reading the same file again wastes a turn after the content is already in context."},
                    },
                },
                {
                    "source_tool": "claude_code",
                    "source_tool_name": "Claude Code",
                    "model": "claude-sonnet-4.6",
                    "total_turns": 26,
                    "total_cost": 1.42,
                    "duration_minutes": 20.0,
                    "active_session_duration_minutes": 16.0,
                    "start_context_window_tokens": 1500,
                    "end_context_window_tokens": 7600,
                    "waste": {
                        "verbose_output": {"cost": 0.24, "description": "Large command output keeps bloating context long after the command finishes."},
                        "idle_narration": {"cost": 0.08, "description": "Status-only turns that re-read the full conversation before acting."},
                    },
                },
                {
                    "source_tool": "codex",
                    "source_tool_name": "OpenAI Codex CLI",
                    "model": "gpt-5.4",
                    "total_turns": 6,
                    "total_cost": 0.49,
                    "duration_minutes": 8.0,
                    "active_session_duration_minutes": 5.0,
                    "start_context_window_tokens": 900,
                    "end_context_window_tokens": 1200,
                    "waste": {
                        "duplicate_reads": {"cost": 0.02, "description": "Reading the same file again wastes a turn after the content is already in context."},
                    },
                },
            ],
            "installed_tools": [
                {"id": "claude_code", "name": "Claude Code", "support_level": "full", "can_analyze": True, "analysis_mode": "claude_jsonl", "log_count": 12},
                {"id": "codex", "name": "OpenAI Codex CLI", "support_level": "full", "can_analyze": True, "analysis_mode": "codex_jsonl", "log_count": 4},
            ],
            "optimization_targets": [
                {"tool": "claude_code", "tool_name": "Claude Code", "file": "/tmp/CLAUDE.md", "filename": "CLAUDE.md", "kind": "instruction_file", "scope": "project"},
                {"tool": "codex", "tool_name": "OpenAI Codex CLI", "file": "/tmp/AGENTS.md", "filename": "AGENTS.md", "kind": "instruction_file", "scope": "project"},
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-ranked-plan-analysis.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["header_statistics"]["overall"]["health"]["emoji"], "❌")
        self.assertEqual(payload["header_statistics"]["tools"][0]["id"], "claude_code")
        self.assertEqual(payload["header_statistics"]["tools"][0]["rank"], 1)
        self.assertEqual(payload["header_statistics"]["tools"][0]["health"]["emoji"], "❌")
        self.assertEqual(payload["header_statistics"]["tools"][0]["avg_session_duration_minutes"], 22.0)
        self.assertEqual(payload["header_statistics"]["tools"][0]["avg_active_session_duration_minutes"], 17.5)
        self.assertEqual(payload["header_statistics"]["tools"][0]["avg_start_context_window_tokens"], 1650)
        self.assertEqual(payload["header_statistics"]["tools"][0]["avg_end_context_window_tokens"], 7900)
        self.assertEqual(payload["header_statistics"]["tools"][1]["id"], "codex")
        self.assertEqual(payload["header_statistics"]["tools"][1]["health"]["emoji"], "✅")
        self.assertEqual(payload["header_statistics"]["models"][0]["id"], "claude-sonnet-4.6")
        self.assertEqual(payload["optimization_plan"]["tools"][0]["tool_id"], "claude_code")
        self.assertEqual(payload["optimization_plan"]["tools"][0]["priority_rank"], 1)
        self.assertTrue(3 <= len(payload["optimization_plan"]["tools"][0]["steps"]) <= 4)
        self.assertTrue(payload["optimization_plan"]["tools"][0]["steps"][0]["approval_required"])
        self.assertLess(
            payload["optimization_plan"]["tools"][0]["before_after"]["projected_avg_cost_per_session"],
            payload["optimization_plan"]["tools"][0]["before_after"]["current_avg_cost_per_session"],
        )
        self.assertEqual(payload["optimization_plan"]["tools"][1]["tool_id"], "codex")
        self.assertEqual(payload["duration_notes"]["log_session_duration"]["availability"], "all_tools")
        self.assertEqual(payload["duration_notes"]["active_session_duration"]["availability"], "all_tools")

    def test_present_scan_uses_global_first_strategy_when_available(self):
        merged = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "date_range": "2026-04-08 to 2026-04-08",
                "total_cost": 1.20,
                "avg_cost_per_session": 1.20,
                "avg_turns_per_session": 16.0,
                "avg_cost_per_turn": 0.075,
                "total_waste": 0.36,
                "waste_per_session": 0.36,
                "waste_percentage": 30.0,
                "projected_cost_after_fix": 0.84,
                "tools_scanned": 1,
            },
            "waste_breakdown": {
                "verbose_output": {
                    "per_session": 0.20,
                    "total_cost": 0.20,
                    "percentage_of_waste": 55.6,
                    "description": "Large command output keeps bloating context long after the command finishes.",
                },
                "duplicate_reads": {
                    "per_session": 0.16,
                    "total_cost": 0.16,
                    "percentage_of_waste": 44.4,
                    "description": "Reading the same file again wastes a turn after the content is already in context.",
                },
            },
            "tool_mix": {
                "codex": {"name": "OpenAI Codex CLI", "sessions": 1, "total_cost": 1.20, "waste_pct": 30.0, "analysis_mode": "codex_jsonl"},
            },
            "model_mix": {
                "gpt-5.4": {"sessions": 1, "pct_sessions": 100.0, "total_cost": 1.20, "pct_cost": 100.0, "avg_cost": 1.20, "avg_turns": 16.0, "waste_pct": 30.0},
            },
            "sessions": [
                {
                    "source_tool": "codex",
                    "source_tool_name": "OpenAI Codex CLI",
                    "model": "gpt-5.4",
                    "total_turns": 16,
                    "total_cost": 1.20,
                    "duration_minutes": 18.0,
                    "start_context_window_tokens": 1200,
                    "end_context_window_tokens": 9500,
                    "waste": {
                        "verbose_output": {"cost": 0.20, "description": "Large command output keeps bloating context long after the command finishes."},
                        "duplicate_reads": {"cost": 0.16, "description": "Reading the same file again wastes a turn after the content is already in context."},
                    },
                }
            ],
            "installed_tools": [
                {"id": "codex", "name": "OpenAI Codex CLI", "support_level": "full", "can_analyze": True, "analysis_mode": "codex_jsonl", "log_count": 9},
            ],
            "optimization_targets": [
                {
                    "tool": "codex",
                    "tool_name": "OpenAI Codex CLI",
                    "file": "/Users/test/.codex/AGENTS.md",
                    "filename": "AGENTS.md",
                    "kind": "instruction_file",
                    "scope": "global",
                    "exists": True,
                    "action": "update",
                    "priority_band": "primary",
                    "source": "global_instruction",
                },
                {
                    "tool": "codex",
                    "tool_name": "OpenAI Codex CLI",
                    "file": "/tmp/project/AGENTS.md",
                    "filename": "AGENTS.md",
                    "kind": "instruction_file",
                    "scope": "project",
                    "exists": True,
                    "action": "update",
                    "priority_band": "fallback",
                    "source": "project_instruction",
                },
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-global-first-analysis.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        strategy = payload["optimization_plan"]["tools"][0]["optimization_strategy"]
        self.assertEqual(strategy["mode"], "global_first")
        self.assertEqual(strategy["preferred_scope"], "global")
        self.assertEqual(strategy["counts"]["primary"], 1)
        self.assertEqual(strategy["counts"]["fallback"], 1)
        self.assertEqual(strategy["counts"]["effective"], 1)
        self.assertEqual(strategy["primary_targets"][0]["path"], "/Users/test/.codex/AGENTS.md")
        self.assertEqual(
            payload["optimization_plan"]["tools"][0]["steps"][0]["target_files"][0]["path"],
            "/Users/test/.codex/AGENTS.md",
        )

    def test_present_scan_uses_existing_project_targets_when_global_surface_is_missing(self):
        merged = {
            "summary": {
                "sessions": 1,
                "total_sessions": 1,
                "total_cost": 1.20,
                "avg_cost_per_session": 1.20,
                "avg_turns_per_session": 16.0,
                "waste_percentage": 30.0,
            },
            "waste_breakdown": {
                "verbose_output": {
                    "per_session": 0.20,
                    "total_cost": 0.20,
                    "percentage_of_waste": 55.6,
                    "description": "Large command output keeps bloating context long after the command finishes.",
                }
            },
            "tool_mix": {
                "codex": {"name": "OpenAI Codex CLI", "sessions": 1, "total_cost": 1.20, "waste_pct": 30.0, "analysis_mode": "codex_jsonl"},
            },
            "sessions": [
                {
                    "source_tool": "codex",
                    "source_tool_name": "OpenAI Codex CLI",
                    "model": "gpt-5.4",
                    "total_turns": 16,
                    "total_cost": 1.20,
                    "duration_minutes": 18.0,
                    "waste": {
                        "verbose_output": {"cost": 0.20, "description": "Large command output keeps bloating context long after the command finishes."},
                    },
                }
            ],
            "installed_tools": [
                {"id": "codex", "name": "OpenAI Codex CLI", "support_level": "full", "can_analyze": True, "analysis_mode": "codex_jsonl", "log_count": 9},
            ],
            "optimization_targets": [
                {
                    "tool": "codex",
                    "tool_name": "OpenAI Codex CLI",
                    "file": "/Users/test/.codex/AGENTS.md",
                    "filename": "AGENTS.md",
                    "kind": "instruction_file",
                    "scope": "global",
                    "exists": False,
                    "action": "update",
                    "priority_band": "primary",
                    "source": "global_instruction",
                },
                {
                    "tool": "codex",
                    "tool_name": "OpenAI Codex CLI",
                    "file": "/tmp/project/AGENTS.md",
                    "filename": "AGENTS.md",
                    "kind": "instruction_file",
                    "scope": "project",
                    "exists": True,
                    "action": "update",
                    "priority_band": "fallback",
                    "source": "project_instruction",
                },
            ],
        }
        fixture_path = ROOT / "tests/fixtures/tmp-project-fallback-analysis.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            payload = run_json("present_scan.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        strategy = payload["optimization_plan"]["tools"][0]["optimization_strategy"]
        self.assertEqual(strategy["mode"], "project_only")
        self.assertEqual(strategy["counts"]["effective"], 1)
        self.assertEqual(strategy["effective_targets"][0]["path"], "/tmp/project/AGENTS.md")
        self.assertEqual(payload["optimization_plan"]["tool_sequence"], ["codex"])
        self.assertEqual(
            payload["optimization_plan"]["tools"][0]["steps"][0]["target_files"][0]["path"],
            "/tmp/project/AGENTS.md",
        )

    def test_report_prints_ranked_scan_summary_with_emoji_markers(self):
        merged = {
            "summary": {
                "date_range": "2026-04-07 to 2026-04-08",
                "sessions": 2,
                "total_cost": 2.00,
                "avg_cost_per_session": 1.00,
                "avg_turns_per_session": 17.0,
                "avg_cost_per_turn": 0.0588,
                "waste_per_session": 0.21,
                "waste_percentage": 21.0,
                "projected_cost_after_fix": 0.79,
                "tools_scanned": 2,
            },
            "waste_breakdown": {
                "verbose_output": {"per_session": 0.18, "total_cost": 0.36, "percentage_of_waste": 85.7, "description": "Large command output keeps bloating context long after the command finishes."},
                "duplicate_reads": {"per_session": 0.03, "total_cost": 0.06, "percentage_of_waste": 14.3, "description": "Reading the same file again wastes a turn after the content is already in context."},
            },
            "analysis_confidence": {"label": "measured", "score": 0.94, "reason": "fixture"},
            "pricing_metadata": {"registry_label": "fixture", "billing_mode": "full_billing", "canonical_model": "multiple", "provider": "multi", "registry_version": "2026-04-08"},
            "header_statistics": {
                "overall": {"health": {"emoji": "❌", "label": "Waste"}},
                "tools": [
                    {"id": "claude_code", "label": "Claude Code", "rank": 1, "health": {"emoji": "❌", "label": "Waste"}, "sessions": 1, "avg_cost_per_session": 1.51, "avg_turns_per_session": 28.0, "avg_session_duration_minutes": 22.0, "avg_active_session_duration_minutes": 17.0, "avg_waste_ratio_pct": 37.0},
                    {"id": "codex", "label": "OpenAI Codex CLI", "rank": 2, "health": {"emoji": "✅", "label": "Good"}, "sessions": 1, "avg_cost_per_session": 0.49, "avg_turns_per_session": 6.0, "avg_session_duration_minutes": 8.0, "avg_active_session_duration_minutes": 5.0, "avg_waste_ratio_pct": 5.0},
                ],
                "models": [
                    {"id": "claude-sonnet-4.6", "label": "claude-sonnet-4.6", "health": {"emoji": "❌", "label": "Waste"}, "avg_session_duration_minutes": 22.0, "avg_active_session_duration_minutes": 17.0},
                    {"id": "gpt-5.4", "label": "gpt-5.4", "health": {"emoji": "✅", "label": "Good"}, "avg_session_duration_minutes": 8.0, "avg_active_session_duration_minutes": 5.0},
                ],
            },
            "duration_notes": {
                "log_session_duration": {"label": "Log session duration", "availability": "all_tools"},
                "active_session_duration": {"label": "Active session duration", "availability": "partial"},
            },
            "optimization_plan": {
                "tools": [
                    {"tool_id": "claude_code", "tool_label": "Claude Code", "priority_rank": 1, "key_statistics": {"avg_session_duration_minutes": 22.0, "avg_active_session_duration_minutes": 17.0}, "steps": [{"title": "Output and context drag", "health": {"emoji": "❌", "label": "Waste"}}]},
                    {"tool_id": "codex", "tool_label": "OpenAI Codex CLI", "priority_rank": 2, "key_statistics": {"avg_session_duration_minutes": 8.0, "avg_active_session_duration_minutes": 5.0}, "steps": [{"title": "Keep the current rules tight", "health": {"emoji": "✅", "label": "Good"}}]},
                ]
            },
        }
        fixture_path = ROOT / "tests/fixtures/tmp-report-ranked-summary.json"
        fixture_path.write_text(json.dumps(merged))
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "report.py"), str(fixture_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertIn("HEADER STATISTICS", result.stdout)
        self.assertIn("OPTIMIZATION ROADMAP", result.stdout)
        self.assertIn("✅", result.stdout)
        self.assertIn("❌", result.stdout)
        self.assertIn("Log session duration", result.stdout)

    def test_present_optimization_step_builds_approval_payload_for_ranked_tool_step(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["claude_code", "codex"],
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "priority_rank": 1,
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                            "waste_ratio_pct": 37.0,
                        },
                        "next_tool_id": "codex",
                        "steps": [
                            {
                                "rank": 1,
                                "title": "Output and context drag",
                                "health": {"emoji": "❌", "label": "Waste"},
                                "projected_savings_per_session": 0.32,
                                "projected_monthly_savings": 260.0,
                                "facts": [
                                    {"label": "Avg cost/session", "value": "$1.51"},
                                    {"label": "Waste ratio", "value": "37.0%"},
                                ],
                                "explanation": {
                                    "summary": "Large command output keeps bloating context long after the command finishes.",
                                    "why_it_matters": "This is the biggest drag on Claude Code right now.",
                                },
                                "approval_required": True,
                                "target_files": [
                                    {"filename": "CLAUDE.md"},
                                ],
                            }
                        ],
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "priority_rank": 2,
                        "steps": [],
                    },
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-step-payload.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_optimization_step.py", fixture_path, "claude_code", 1)
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["visibility"], "approval")
        self.assertEqual(payload["kind"], "scan_approval")
        self.assertIn("Claude Code", payload["card"]["title"])
        self.assertIn("CLAUDE.md", payload["card"]["body"])
        self.assertTrue(payload["proposed_change"]["additions"][0].startswith("+ "))
        self.assertEqual(payload["workflow"]["tool_id"], "claude_code")
        self.assertEqual(payload["workflow"]["step"]["rank"], 1)
        self.assertEqual(payload["workflow"]["next_tool_id"], "codex")

    def test_present_tool_success_builds_bulk_apply_prompt_after_tool_one(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["claude_code", "codex"],
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "priority_rank": 1,
                        "health": {"emoji": "❌", "label": "Waste"},
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                            "waste_ratio_pct": 37.0,
                        },
                        "key_statistics": {
                            "avg_turns_per_session": 28.0,
                        },
                        "next_tool_id": "codex",
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "priority_rank": 2,
                        "health": {"emoji": "✅", "label": "Good"},
                        "before_after": {
                            "current_avg_cost_per_session": 0.49,
                            "projected_avg_cost_per_session": 0.42,
                            "projected_monthly_savings": 40.0,
                            "waste_ratio_pct": 5.0,
                        },
                    },
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-tool-success.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_tool_success.py", fixture_path, "claude_code")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["visibility"], "result")
        self.assertEqual(payload["kind"], "tool_success")
        self.assertEqual(payload["tool_success"]["tool_id"], "claude_code")
        self.assertIn("$1.51/session", payload["hero"]["headline"])
        self.assertEqual(payload["bulk_apply_prompt"]["next_tool_id"], "codex")
        self.assertIn("other tools and projects", payload["bulk_apply_prompt"]["message"])
        self.assertIn("present_bulk_apply_prompt.py", payload["bulk_apply_prompt"]["command"])
        self.assertIn("present_final_success.py", payload["finish_prompt"]["command"])

    def test_present_tool_success_does_not_offer_manual_next_tool_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            claude_path = base / "CLAUDE.md"
            codex_path = base / "AGENTS.md"
            claude_path.write_text("# Claude\n")
            codex_path.write_text("# Codex\n")
            scan_payload = {
                "optimization_plan": {
                    "tool_sequence": ["claude_code", "codex"],
                    "tools": [
                        {
                            "tool_id": "claude_code",
                            "tool_label": "Claude Code",
                            "priority_rank": 1,
                            "before_after": {
                                "current_avg_cost_per_session": 1.51,
                                "projected_avg_cost_per_session": 0.95,
                                "projected_monthly_savings": 400.0,
                                "waste_ratio_pct": 37.0,
                            },
                            "optimization_strategy": {
                                "effective_targets": [
                                    {"kind": "instruction_file", "path": str(claude_path), "exists": True}
                                ]
                            },
                            "steps": [
                                {
                                    "rank": 1,
                                    "title": "Output and context drag",
                                    "projected_savings_per_session": 0.32,
                                    "projected_monthly_savings": 260.0,
                                    "target_files": [{"kind": "instruction_file", "file": str(claude_path), "exists": True}],
                                    "execution": {"status": "applied"},
                                }
                            ],
                            "execution_state": {"status": "completed"},
                        },
                        {
                            "tool_id": "codex",
                            "tool_label": "OpenAI Codex CLI",
                            "priority_rank": 2,
                            "optimization_strategy": {
                                "effective_targets": [
                                    {"kind": "instruction_file", "path": str(codex_path), "exists": True}
                                ]
                            },
                            "steps": [
                                {
                                    "rank": 1,
                                    "title": "Narration",
                                    "projected_savings_per_session": 0.08,
                                    "projected_monthly_savings": 40.0,
                                    "target_files": [{"kind": "instruction_file", "file": str(codex_path), "exists": True}],
                                    "execution": {"status": "pending"},
                                }
                            ],
                        },
                    ]
                }
            }
            fixture_path = base / "payload.json"
            fixture_path.write_text(json.dumps(scan_payload))
            payload = run_json("present_tool_success.py", fixture_path, "claude_code")

        self.assertEqual(payload["bulk_apply_prompt"]["next_tool_id"], "codex")
        self.assertNotIn("continue_prompt", payload)

    def test_present_bulk_apply_prompt_summarizes_remaining_plan(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["claude_code", "codex", "workbuddy"],
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "priority_rank": 1,
                        "before_after": {"projected_monthly_savings": 400.0},
                        "steps": [],
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "priority_rank": 2,
                        "before_after": {"projected_monthly_savings": 120.0},
                        "steps": [
                            {"target_files": [{"path": "/tmp/AGENTS.md"}, {"path": "/tmp/TEAM_GUIDE.md"}]},
                        ],
                    },
                    {
                        "tool_id": "workbuddy",
                        "tool_label": "WorkBuddy",
                        "priority_rank": 3,
                        "before_after": {"projected_monthly_savings": 30.0},
                        "steps": [
                            {"target_files": [{"path": "/tmp/WORKBUDDY.md"}]},
                        ],
                    },
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-bulk-prompt.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_bulk_apply_prompt.py", fixture_path, "claude_code")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["visibility"], "approval")
        self.assertEqual(payload["kind"], "scan_approval")
        self.assertEqual(payload["workflow"]["remaining_tools"], 2)
        self.assertEqual(payload["workflow"]["projected_monthly_savings"], 150.0)
        self.assertIn("vibecheck_optimize_bulk.py", payload["card"]["command"])

    def test_present_bulk_apply_prompt_counts_unique_target_files(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["claude_code", "codex"],
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "before_after": {"projected_monthly_savings": 400.0},
                        "steps": [],
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "before_after": {"projected_monthly_savings": 120.0},
                        "steps": [
                            {"target_files": [{"path": "/tmp/AGENTS.md"}]},
                            {"target_files": [{"path": "/tmp/AGENTS.md"}]},
                            {"target_files": [{"path": "/tmp/AGENTS.md"}]},
                        ],
                    },
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-bulk-unique-targets.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_bulk_apply_prompt.py", fixture_path, "claude_code")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["workflow"]["remaining_target_files"], 1)
        self.assertIn("1 target edit", payload["card"]["body"])

    def test_present_bulk_apply_prompt_excludes_non_instruction_targets_from_edit_count(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["tool1", "tool2"],
                "tools": [
                    {
                        "tool_id": "tool1",
                        "tool_label": "Tool 1",
                        "steps": [
                            {
                                "rank": 1,
                                "title": "done",
                                "target_files": [{"kind": "instruction_file", "path": "/tmp/ONE.md", "exists": True}],
                                "execution": {"status": "applied"},
                            }
                        ],
                    },
                    {
                        "tool_id": "tool2",
                        "tool_label": "Tool 2",
                        "before_after": {"projected_monthly_savings": 10.0},
                        "steps": [
                            {"rank": 1, "title": "config", "target_files": [{"kind": "config_path", "path": "/tmp/settings.json", "exists": True}]},
                            {"rank": 2, "title": "rule", "target_files": [{"kind": "instruction_file", "path": "/tmp/TWO.md", "exists": True}]},
                        ],
                    },
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-bulk-instruction-only-targets.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_bulk_apply_prompt.py", fixture_path, "tool1")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["workflow"]["remaining_target_files"], 1)
        self.assertIn("1 target edit", payload["card"]["body"])

    def test_present_tool_success_includes_status_report_and_top_savings(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["codex"],
                "tools": [
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "priority_rank": 1,
                        "health": {"emoji": "❌", "label": "Waste"},
                        "before_after": {
                            "current_avg_cost_per_session": 1.20,
                            "projected_avg_cost_per_session": 0.84,
                            "projected_monthly_savings": 180.0,
                            "waste_ratio_pct": 30.0,
                        },
                        "key_statistics": {
                            "avg_turns_per_session": 16.0,
                            "avg_session_duration_minutes": 18.0,
                            "avg_start_context_window_tokens": 1200,
                            "avg_end_context_window_tokens": 9500,
                        },
                        "optimization_strategy": {
                            "mode": "global_first",
                            "summary": "Start with one machine-wide instruction change, then touch project files only if a repo needs an exception.",
                            "primary_targets": [
                                {"path": "/Users/test/.codex/AGENTS.md", "filename": "AGENTS.md", "scope": "global", "exists": False}
                            ],
                            "fallback_targets": [
                                {"path": "/tmp/project/AGENTS.md", "filename": "AGENTS.md", "scope": "project", "exists": True}
                            ],
                        },
                        "steps": [
                            {"rank": 1, "title": "Verbose output flooding", "health": {"emoji": "❌", "label": "Waste"}, "projected_savings_per_session": 0.20, "projected_monthly_savings": 100.0, "waste_ratio_pct": 16.7},
                            {"rank": 2, "title": "Duplicate reads", "health": {"emoji": "❌", "label": "Waste"}, "projected_savings_per_session": 0.16, "projected_monthly_savings": 80.0, "waste_ratio_pct": 13.3},
                        ],
                    }
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-tool-success-rich.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_tool_success.py", fixture_path, "codex")
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["status_report"]["before_after"]["avg_cost_before"], 1.20)
        self.assertEqual(payload["status_report"]["top_savings"][0]["title"], "Verbose output flooding")
        self.assertEqual(payload["status_report"]["optimization_strategy"]["mode"], "global_first")
        self.assertEqual(payload["sections"][1]["kind"], "comparison")
        self.assertEqual(payload["tool_success"]["completed_steps"][0]["rank"], 1)

    def test_present_tool_success_omits_savings_when_all_steps_were_skipped(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["claude_code"],
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "priority_rank": 1,
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                            "waste_ratio_pct": 37.0,
                        },
                        "steps": [
                            {
                                "rank": 1,
                                "title": "Narration",
                                "projected_savings_per_session": 0.20,
                                "projected_monthly_savings": 150.0,
                                "execution": {"status": "skipped"},
                            }
                        ],
                        "execution_state": {"status": "completed"},
                    }
                ],
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-tool-success-skipped.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_tool_success.py", fixture_path, "claude_code")
        finally:
            fixture_path.unlink(missing_ok=True)
        self.assertEqual(payload["tool_success"]["summary"]["projected_monthly_savings"], 0)
        self.assertEqual(payload["tool_success"]["summary"]["waste_ratio_before_pct"], 37.0)
        self.assertEqual(payload["tool_success"]["top_savings"], [])
        self.assertEqual(payload["status_report"]["completed_steps"], [])
        self.assertEqual(payload["status_report"]["skipped_steps"][0]["rank"], 1)
        self.assertEqual(payload["hero"]["eyebrow"], "Tool #1 reviewed")
        self.assertIn("No changes were applied", payload["hero"]["headline"])
        self.assertIn("All proposed steps were skipped", payload["message"])

    def test_vibecheck_optimize_bulk_applies_remaining_tools(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            claude_file = base / "CLAUDE.md"
            codex_file = base / "AGENTS.md"
            claude_file.write_text("# Claude\n")
            codex_file.write_text("# Codex\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tools": [
                                {
                                    "tool_id": "claude_code",
                                    "tool_label": "Claude Code",
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Narration",
                                            "patterns": [{"key": "idle_narration"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(claude_file)}],
                                        }
                                    ],
                                },
                                {
                                    "tool_id": "codex",
                                    "tool_label": "OpenAI Codex CLI",
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Verbose output",
                                            "patterns": [{"key": "verbose_output"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(codex_file)}],
                                        }
                                    ],
                                },
                            ]
                        }
                    }
                )
            )
            result = run_json("vibecheck_optimize_bulk.py", payload_path, "claude_code")
            codex_content = codex_file.read_text()
            claude_content = claude_file.read_text()

        self.assertTrue(result["ok"])
        self.assertEqual(result["tools_processed"], 1)
        self.assertIn("Redirect noisy build/test/install output", codex_content)
        self.assertNotIn("Vibecheck Cost Rules", claude_content)

    def test_vibecheck_optimize_bulk_marks_missing_runtime_targets_skipped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            claude_file = base / "CLAUDE.md"
            codex_file = base / "AGENTS.md"
            claude_file.write_text("# Claude\n")
            codex_file.write_text("# Codex\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tool_sequence": ["claude_code", "codex"],
                            "tools": [
                                {
                                    "tool_id": "claude_code",
                                    "tool_label": "Claude Code",
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Narration",
                                            "patterns": [{"key": "idle_narration"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(claude_file), "exists": True}],
                                            "execution": {"status": "applied"},
                                        }
                                    ],
                                },
                                {
                                    "tool_id": "codex",
                                    "tool_label": "OpenAI Codex CLI",
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Verbose output",
                                            "patterns": [{"key": "verbose_output"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(codex_file), "exists": True}],
                                        }
                                    ],
                                },
                            ]
                        }
                    }
                )
            )
            codex_file.unlink()

            result = run_json("vibecheck_optimize_bulk.py", payload_path, "claude_code")
            payload = json.loads(payload_path.read_text())

        tool = next(item for item in payload["optimization_plan"]["tools"] if item["tool_id"] == "codex")
        self.assertTrue(result["ok"])
        self.assertEqual(result["results"][0]["applied"], [])
        self.assertEqual(result["results"][0]["skipped"][0]["reason"], "missing_or_not_editable")
        self.assertEqual(tool["steps"][0]["execution"]["status"], "skipped")
        self.assertEqual(tool["execution_state"]["applied_step_ranks"], [])
        self.assertEqual(tool["execution_state"]["skipped_step_ranks"], [1])

    def test_vibecheck_optimize_accumulates_rules_across_steps_and_updates_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            instruction_path = base / "AGENTS.md"
            instruction_path.write_text("# Existing rules\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tools": [
                                {
                                    "tool_id": "codex",
                                    "tool_label": "OpenAI Codex CLI",
                                    "optimization_strategy": {
                                        "effective_targets": [
                                            {"kind": "instruction_file", "path": str(instruction_path), "exists": True}
                                        ]
                                    },
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Narration",
                                            "patterns": [{"key": "idle_narration"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(instruction_path), "exists": True}],
                                        },
                                        {
                                            "rank": 2,
                                            "title": "Verbose output",
                                            "patterns": [{"key": "verbose_output"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(instruction_path), "exists": True}],
                                        },
                                    ],
                                }
                            ]
                        }
                    }
                )
            )

            first = run_json("vibecheck_optimize.py", payload_path, "codex", 1)
            second = run_json("vibecheck_optimize.py", payload_path, "codex", 2)
            content = instruction_path.read_text()
            payload = json.loads(payload_path.read_text())

        self.assertTrue(first["ok"])
        self.assertFalse(first["tool_complete"])
        self.assertEqual(first["next_pending_step_rank"], 2)
        self.assertTrue(second["ok"])
        self.assertTrue(second["tool_complete"])
        self.assertIsNone(second["next_pending_step_rank"])
        self.assertIn("Do not spend a turn narrating", content)
        self.assertIn("Redirect noisy build/test/install output", content)
        self.assertEqual(content.count("<!-- vibecheck:cost-rules:start -->"), 1)
        tool = payload["optimization_plan"]["tools"][0]
        self.assertEqual(tool["execution_state"]["applied_step_ranks"], [1, 2])

    def test_vibecheck_optimize_marks_step_skipped_when_target_disappears_before_apply(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            instruction_path = base / "AGENTS.md"
            instruction_path.write_text("# Existing rules\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tool_sequence": ["codex"],
                            "tools": [
                                {
                                    "tool_id": "codex",
                                    "tool_label": "OpenAI Codex CLI",
                                    "priority_rank": 1,
                                    "before_after": {
                                        "current_avg_cost_per_session": 1.20,
                                        "projected_avg_cost_per_session": 0.80,
                                        "projected_monthly_savings": 20.0,
                                        "waste_ratio_pct": 33.0,
                                    },
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Narration",
                                            "patterns": [{"key": "idle_narration"}],
                                            "projected_savings_per_session": 0.40,
                                            "projected_monthly_savings": 20.0,
                                            "target_files": [{"kind": "instruction_file", "file": str(instruction_path), "exists": True}],
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                )
            )
            instruction_path.unlink()

            result = run_json("vibecheck_optimize.py", payload_path, "codex", 1)
            payload = json.loads(payload_path.read_text())
            final = run_json("present_final_success.py", payload_path)

        tool = payload["optimization_plan"]["tools"][0]
        self.assertTrue(result["ok"])
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["skipped"][0]["reason"], "missing_or_not_editable")
        self.assertEqual(tool["steps"][0]["execution"]["status"], "skipped")
        self.assertEqual(tool["execution_state"]["applied_step_ranks"], [])
        self.assertEqual(tool["execution_state"]["skipped_step_ranks"], [1])
        self.assertEqual(final["summary"]["tools_optimized"], 0)
        self.assertIn("No changes were applied", final["hero"]["headline"])

    def test_present_next_workflow_item_advances_from_step_to_tool_success_for_single_tool(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            instruction_path = base / "CLAUDE.md"
            instruction_path.write_text("# Claude\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tool_sequence": ["claude_code"],
                            "tools": [
                                {
                                    "tool_id": "claude_code",
                                    "tool_label": "Claude Code",
                                    "priority_rank": 1,
                                    "before_after": {
                                        "current_avg_cost_per_session": 1.51,
                                        "projected_avg_cost_per_session": 0.95,
                                        "projected_monthly_savings": 400.0,
                                        "waste_ratio_pct": 37.0,
                                    },
                                    "optimization_strategy": {
                                        "effective_targets": [
                                            {"kind": "instruction_file", "path": str(instruction_path), "exists": True}
                                        ]
                                    },
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Output and context drag",
                                            "patterns": [{"key": "verbose_output"}],
                                            "projected_savings_per_session": 0.32,
                                            "projected_monthly_savings": 260.0,
                                            "waste_ratio_pct": 21.0,
                                            "health": {"emoji": "❌", "label": "Waste"},
                                            "target_files": [{"kind": "instruction_file", "file": str(instruction_path), "exists": True}],
                                        }
                                    ],
                                }
                            ],
                        }
                    }
                )
            )

            first_item = run_json("present_next_workflow_item.py", payload_path, "claude_code")
            run_json("vibecheck_optimize.py", payload_path, "claude_code", 1)
            second_item = run_json("present_next_workflow_item.py", payload_path, "claude_code")

        self.assertEqual(first_item["visibility"], "approval")
        self.assertEqual(first_item["workflow"]["step"]["rank"], 1)
        self.assertEqual(second_item["kind"], "tool_success")
        self.assertEqual(second_item["tool_success"]["tool_id"], "claude_code")
        self.assertIn("present_final_success.py", second_item["finish_prompt"]["command"])
        self.assertNotIn("bulk_apply_prompt", second_item)

    def test_present_final_success_uses_review_language_when_nothing_was_applied(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tool_sequence": ["claude_code"],
                            "tools": [
                                {
                                    "tool_id": "claude_code",
                                    "tool_label": "Claude Code",
                                    "priority_rank": 1,
                                    "before_after": {
                                        "current_avg_cost_per_session": 1.20,
                                        "projected_avg_cost_per_session": 0.84,
                                        "projected_monthly_savings": 210.0,
                                        "waste_ratio_pct": 30.0,
                                    },
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Verbose output",
                                            "projected_savings_per_session": 0.20,
                                            "projected_monthly_savings": 120.0,
                                            "execution": {"status": "skipped"},
                                        },
                                    ],
                                }
                            ],
                        }
                    }
                )
            )

            next_item = run_json("present_final_success.py", payload_path)

        self.assertEqual(next_item["kind"], "optimization_final_success")
        self.assertEqual(next_item["summary"]["tools_optimized"], 0)
        self.assertEqual(next_item["hero"]["eyebrow"], "Review complete")
        self.assertIn("No changes were applied", next_item["hero"]["headline"])

    def test_vibecheck_skip_step_marks_state_and_advances_to_next_step(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            instruction_path = base / "CLAUDE.md"
            instruction_path.write_text("# Claude\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tool_sequence": ["claude_code"],
                            "tools": [
                                {
                                    "tool_id": "claude_code",
                                    "tool_label": "Claude Code",
                                    "priority_rank": 1,
                                    "optimization_strategy": {
                                        "effective_targets": [
                                            {"kind": "instruction_file", "path": str(instruction_path), "exists": True}
                                        ]
                                    },
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Narration",
                                            "patterns": [{"key": "idle_narration"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(instruction_path), "exists": True}],
                                        },
                                        {
                                            "rank": 2,
                                            "title": "Verbose output",
                                            "patterns": [{"key": "verbose_output"}],
                                            "target_files": [{"kind": "instruction_file", "file": str(instruction_path), "exists": True}],
                                        },
                                    ],
                                }
                            ],
                        }
                    }
                )
            )

            result = run_json("vibecheck_skip_step.py", payload_path, "claude_code", 1)
            next_item = run_json("present_next_workflow_item.py", payload_path, "claude_code")
            payload = json.loads(payload_path.read_text())

        self.assertTrue(result["ok"])
        self.assertEqual(result["next_pending_step_rank"], 2)
        self.assertEqual(next_item["workflow"]["step"]["rank"], 2)
        self.assertEqual(payload["optimization_plan"]["tools"][0]["execution_state"]["skipped_step_ranks"], [1])

    def test_present_final_success_summarizes_all_tools_before_education(self):
        scan_payload = {
            "optimization_plan": {
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                        },
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "before_after": {
                            "current_avg_cost_per_session": 0.49,
                            "projected_avg_cost_per_session": 0.42,
                            "projected_monthly_savings": 40.0,
                        },
                    },
                ]
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-final-success.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_final_success.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["kind"], "optimization_final_success")
        self.assertEqual(payload["summary"]["tools_optimized"], 2)
        self.assertEqual(payload["summary"]["projected_monthly_savings"], 440.0)
        self.assertIn("Human-side tips come next", payload["education_next"]["title"])
        self.assertIn("present_education.py", payload["education_next"]["command"])

    def test_present_final_success_uses_applied_state_when_workflow_has_run(self):
        scan_payload = {
            "optimization_plan": {
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                        },
                        "steps": [
                            {
                                "rank": 1,
                                "title": "Narration",
                                "projected_savings_per_session": 0.20,
                                "projected_monthly_savings": 150.0,
                                "execution": {"status": "applied"},
                            }
                        ],
                        "execution_state": {"status": "completed"},
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "before_after": {
                            "current_avg_cost_per_session": 0.49,
                            "projected_avg_cost_per_session": 0.42,
                            "projected_monthly_savings": 40.0,
                        },
                        "steps": [
                            {
                                "rank": 1,
                                "title": "Verbose output",
                                "projected_savings_per_session": 0.07,
                                "projected_monthly_savings": 40.0,
                                "execution": {"status": "pending"},
                            }
                        ],
                        "execution_state": {"status": "in_progress"},
                    },
                ]
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-final-success-applied.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_final_success.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["summary"]["tools_optimized"], 1)
        self.assertEqual(payload["summary"]["projected_monthly_savings"], 150.0)

    def test_present_final_success_does_not_count_skipped_only_tools_as_optimized(self):
        scan_payload = {
            "optimization_plan": {
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                        },
                        "steps": [
                            {
                                "rank": 1,
                                "title": "Narration",
                                "projected_savings_per_session": 0.20,
                                "projected_monthly_savings": 150.0,
                                "execution": {"status": "skipped"},
                            }
                        ],
                        "execution_state": {"status": "completed"},
                    }
                ]
            }
        }
        fixture_path = ROOT / "tests/fixtures/tmp-final-success-skipped-only.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_final_success.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["summary"]["tools_optimized"], 0)
        self.assertEqual(payload["summary"]["projected_monthly_savings"], 0)
        self.assertEqual(payload["top_tool_wins"], [])

    def test_present_final_success_uses_weighted_average_when_session_counts_exist(self):
        scan_payload = {
            "optimization_plan": {
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "before_after": {
                            "current_avg_cost_per_session": 1.50,
                            "projected_avg_cost_per_session": 1.00,
                            "projected_monthly_savings": 300.0,
                        },
                    },
                    {
                        "tool_id": "codex",
                        "tool_label": "OpenAI Codex CLI",
                        "before_after": {
                            "current_avg_cost_per_session": 0.50,
                            "projected_avg_cost_per_session": 0.25,
                            "projected_monthly_savings": 40.0,
                        },
                    },
                ]
            },
            "header_statistics": {
                "tools": [
                    {"id": "claude_code", "sessions": 3},
                    {"id": "codex", "sessions": 1},
                ]
            },
        }
        fixture_path = ROOT / "tests/fixtures/tmp-final-success-weighted.json"
        fixture_path.write_text(json.dumps(scan_payload))
        try:
            payload = run_json("present_final_success.py", fixture_path)
        finally:
            fixture_path.unlink(missing_ok=True)

        self.assertEqual(payload["summary"]["avg_cost_before"], 1.25)
        self.assertEqual(payload["summary"]["avg_cost_after"], 0.812)

    def test_present_education_builds_continuity_and_handoff_payload(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        analysis_path = ROOT / "tests/fixtures/tmp-education-analysis.json"
        lesson_path = ROOT / "tests/fixtures/tmp-lesson.json"
        analysis_path.write_text(json.dumps(analysis))
        try:
            lesson = run_json("explain.py", analysis_path)
            lesson_path.write_text(json.dumps(lesson))
            payload = run_json("present_education.py", lesson_path)
        finally:
            analysis_path.unlink(missing_ok=True)
            lesson_path.unlink(missing_ok=True)

        self.assertEqual(payload["kind"], "optimization_education")
        self.assertEqual(payload["hero"]["eyebrow"], "Keep the gains")
        self.assertEqual(payload["session_habits"]["recommended_active_minutes"], "A good default is 5-10 active minutes per focused session.")
        self.assertIn("https://github.com/wallmage/handoff", payload["handoff"]["install_prompt"])
        self.assertEqual(
            [section["kind"] for section in payload["sections"]],
            ["hero", "context", "habits", "continuity", "handoff"],
        )

    def test_export_optimization_log_writes_scan_markdown(self):
        analysis = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        analysis_path = ROOT / "tests/fixtures/tmp-export-scan-analysis.json"
        payload_path = ROOT / "tests/fixtures/tmp-export-scan-payload.json"
        output_path = ROOT / "tests/fixtures/tmp-scan-log.md"
        analysis_path.write_text(json.dumps(analysis))
        try:
            payload = run_json("present_scan.py", analysis_path, "/tmp/CLAUDE.md")
            payload_path.write_text(json.dumps(payload))
            result = run_json("export_optimization_log.py", payload_path, output_path)
        finally:
            analysis_path.unlink(missing_ok=True)
            payload_path.unlink(missing_ok=True)
        try:
            content = output_path.read_text()
        finally:
            output_path.unlink(missing_ok=True)

        self.assertEqual(result["kind"], "scan_result")
        self.assertIn("# VibeCheck Scan Complete", content)
        self.assertIn("## Snapshot", content)
        self.assertIn("## Tool Ranking", content)
        self.assertIn("## Optimization Plan", content)
        self.assertIn("Active session duration", content)

    def test_export_optimization_log_writes_tool_success_markdown(self):
        scan_payload = {
            "optimization_plan": {
                "tool_sequence": ["claude_code"],
                "tools": [
                    {
                        "tool_id": "claude_code",
                        "tool_label": "Claude Code",
                        "priority_rank": 1,
                        "health": {"emoji": "❌", "label": "Waste"},
                        "before_after": {
                            "current_avg_cost_per_session": 1.51,
                            "projected_avg_cost_per_session": 0.95,
                            "projected_monthly_savings": 400.0,
                            "waste_ratio_pct": 37.0,
                        },
                        "key_statistics": {
                            "avg_turns_per_session": 28.0,
                            "avg_session_duration_minutes": 22.0,
                            "avg_active_session_duration_minutes": 17.0,
                            "avg_start_context_window_tokens": 1650,
                            "avg_end_context_window_tokens": 7900,
                        },
                        "optimization_strategy": {
                            "mode": "global_first",
                            "summary": "Start with one machine-wide instruction change, then touch project files only if a repo needs an exception.",
                            "primary_targets": [
                                {"path": "/Users/test/.claude/CLAUDE.md", "filename": "CLAUDE.md", "scope": "global", "exists": False}
                            ],
                            "fallback_targets": [
                                {"path": "/tmp/project/CLAUDE.md", "filename": "CLAUDE.md", "scope": "project", "exists": True}
                            ],
                        },
                        "steps": [
                            {"rank": 1, "title": "Verbose output flooding", "health": {"emoji": "❌", "label": "Waste"}, "projected_savings_per_session": 0.32, "projected_monthly_savings": 260.0, "waste_ratio_pct": 21.0},
                            {"rank": 2, "title": "Idle narration", "health": {"emoji": "❌", "label": "Waste"}, "projected_savings_per_session": 0.24, "projected_monthly_savings": 140.0, "waste_ratio_pct": 16.0},
                        ],
                    }
                ],
            }
        }
        scan_payload_path = ROOT / "tests/fixtures/tmp-export-tool-success-source.json"
        success_payload_path = ROOT / "tests/fixtures/tmp-export-tool-success-payload.json"
        output_path = ROOT / "tests/fixtures/tmp-tool-success-log.md"
        scan_payload_path.write_text(json.dumps(scan_payload))
        try:
            success_payload = run_json("present_tool_success.py", scan_payload_path, "claude_code")
            success_payload_path.write_text(json.dumps(success_payload))
            result = run_json("export_optimization_log.py", success_payload_path, output_path)
        finally:
            scan_payload_path.unlink(missing_ok=True)
            success_payload_path.unlink(missing_ok=True)
        try:
            content = output_path.read_text()
        finally:
            output_path.unlink(missing_ok=True)

        self.assertEqual(result["kind"], "tool_success")
        self.assertIn("# VibeCheck Optimization Update", content)
        self.assertIn("## Before vs After", content)
        self.assertIn("## Top Savings Captured", content)
        self.assertIn("## What Changed", content)
        self.assertIn("Active session duration", content)

    def test_export_optimization_log_includes_skipped_steps_and_finish_option(self):
        payload = {
            "kind": "tool_success",
            "hero": {"headline": "Claude Code is projected to drop from $1.51/session to $1.31/session."},
            "tool_success": {
                "tool_id": "claude_code",
                "tool_label": "Claude Code",
                "top_savings": [],
                "summary": {
                    "avg_cost_before": 1.51,
                    "avg_cost_after": 1.31,
                    "waste_ratio_before_pct": 37.0,
                    "projected_monthly_savings": 120.0,
                },
            },
            "status_report": {
                "before_after": {
                    "avg_cost_before": 1.51,
                    "avg_cost_after": 1.31,
                    "waste_ratio_before_pct": 37.0,
                    "projected_monthly_savings": 120.0,
                },
                "key_statistics": {},
                "top_savings": [],
                "optimization_strategy": {"summary": "Project-only optimization."},
                "completed_steps": [{"rank": 1, "title": "Verbose output", "health": {"label": "Waste", "emoji": "❌"}}],
                "skipped_steps": [{"rank": 2, "title": "Narration"}],
            },
            "finish_prompt": {
                "message": "If not, I can stop here and show the final summary for the work already applied.",
            },
        }
        payload_path = ROOT / "tests/fixtures/tmp-export-tool-success-skipped.json"
        output_path = ROOT / "tests/fixtures/tmp-tool-success-skipped-log.md"
        payload_path.write_text(json.dumps(payload))
        try:
            run_json("export_optimization_log.py", payload_path, output_path)
        finally:
            payload_path.unlink(missing_ok=True)
        try:
            content = output_path.read_text()
        finally:
            output_path.unlink(missing_ok=True)

        self.assertIn("## Skipped Steps", content)
        self.assertIn("2. Narration", content)
        self.assertIn("## Finish Here", content)

    def test_find_cursor_logs_strips_file_uri_prefix_from_workspace_path(self):
        import find_cursor_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_json = Path(tmpdir) / "workspace.json"
            workspace_json.write_text(json.dumps({"folder": "file:///Users/test/project"}))
            workspace_path = find_cursor_logs.load_workspace_path(workspace_json)

        self.assertEqual(workspace_path, "/Users/test/project")

    def test_export_logs_uses_workbuddy_filenames_for_workbuddy_exports(self):
        import export_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            src = base / "src"
            dest = base / "dest"
            (src / "logs").mkdir(parents=True)
            (src / "User" / "workspaceStorage" / "abc").mkdir(parents=True)
            (src / "User" / "globalStorage").mkdir(parents=True)
            (src / "workbuddy-sessions.vscdb").write_text("db")
            (src / "logs" / "workbuddy.log").write_text("log")
            (src / "User" / "workspaceStorage" / "abc" / "workspace.json").write_text("{}")
            (src / "User" / "workspaceStorage" / "abc" / "state.vscdb").write_text("state")
            (src / "User" / "globalStorage" / "state.vscdb").write_text("global")

            with patch.object(export_logs, "find_source", return_value=(src, "WorkBuddy")):
                ok = export_logs.export(days=14, dest=dest, tool="workbuddy")
                copied_index = (dest / "workbuddy-sessions.vscdb").exists()
                copied_log = (dest / "logs" / "workbuddy.log").exists()

        self.assertTrue(ok)
        self.assertTrue(copied_index)
        self.assertTrue(copied_log)

    def test_analyze_buddy_sessions_parses_top_level_buddy_logs(self):
        import analyze_buddy_sessions

        for filename in ("codebuddy.log", "workbuddy.log"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmpdir:
                logs_dir = Path(tmpdir) / "logs"
                logs_dir.mkdir()
                (logs_dir / filename).write_text(
                    "2026-04-09 00:00:00.000 Reporting session created for run-1: conversationId=abc123\n"
                    "2026-04-09 00:00:01.000 Setting session model for abc123: gpt-5.4\n"
                    "2026-04-09 00:00:02.000 Prompting session abc123\n"
                    "2026-04-09 00:00:03.000 Sub-run run-1 completed successfully, output length: 400, foo messageCount: 9\n"
                )

                stats = analyze_buddy_sessions.parse_logs(logs_dir)

                self.assertIn("abc123", stats)
                self.assertEqual(stats["abc123"]["runs"], 1)
                self.assertEqual(stats["abc123"]["message_count"], 9)
                self.assertEqual(stats["abc123"]["output_chars"], 400)
                self.assertIn("gpt-5.4", stats["abc123"]["models"])

    def test_find_workbuddy_logs_uses_linux_config_root(self):
        import find_workbuddy_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            config_root = home / ".config" / "WorkBuddy"
            config_root.mkdir(parents=True)
            index_db = config_root / "workbuddy-sessions.vscdb"
            conn = sqlite3.connect(index_db)
            conn.execute("CREATE TABLE ItemTable (key TEXT, value TEXT)")
            conn.execute(
                "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
                (
                    "session:abc123",
                    json.dumps(
                        {
                            "conversationId": "abc123",
                            "cwd": "/tmp/demo",
                            "title": "Demo",
                            "createdAt": "2026-04-09T00:00:00Z",
                            "updatedAt": "2026-04-09T00:05:00Z",
                        }
                    ),
                ),
            )
            conn.commit()
            conn.close()
            (config_root / "logs").mkdir()

            output = StringIO()
            with patch.object(find_workbuddy_logs.platform, "system", return_value="Linux"), \
                patch.object(find_workbuddy_logs.Path, "home", return_value=home), \
                patch.object(sys, "argv", ["find_workbuddy_logs.py", "14"]), \
                redirect_stdout(output):
                try:
                    find_workbuddy_logs.main()
                except SystemExit:
                    pass

            payload = json.loads(output.getvalue())
            self.assertEqual(payload["total_sessions"], 1)
            self.assertEqual(payload["projects_dir"], str(config_root))

    def test_detect_tool_workbuddy_registry_uses_workbuddy_session_db(self):
        workbuddy_patterns = [
            pattern
            for patterns in detect_tool.TOOLS["workbuddy"]["log_paths"].values()
            for pattern in patterns
        ]

        self.assertTrue(any("workbuddy-sessions.vscdb" in pattern for pattern in workbuddy_patterns))
        self.assertFalse(any("codebuddy-sessions.vscdb" in pattern for pattern in workbuddy_patterns))
        self.assertFalse(any("workspaceStorage" in pattern for pattern in workbuddy_patterns))

    def test_export_logs_prefers_workbuddy_source_with_session_data(self):
        import export_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / ".workbuddy").mkdir()
            config_root = home / ".config" / "WorkBuddy"
            config_root.mkdir(parents=True)
            (config_root / "workbuddy-sessions.vscdb").write_text("db")

            with patch.object(export_logs.platform, "system", return_value="Linux"), \
                patch.object(export_logs.Path, "home", return_value=home):
                source, tool_name = export_logs.find_source("workbuddy")

            self.assertEqual(tool_name, "WorkBuddy")
            self.assertEqual(source, config_root)

    def test_find_codebuddy_logs_uses_linux_config_root(self):
        import find_codebuddy_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            config_root = home / ".config" / "CodeBuddy"
            config_root.mkdir(parents=True)
            index_db = config_root / "codebuddy-sessions.vscdb"
            conn = sqlite3.connect(index_db)
            conn.execute("CREATE TABLE ItemTable (key TEXT, value TEXT)")
            conn.execute(
                "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
                (
                    "session:abc123",
                    json.dumps(
                        {
                            "conversationId": "abc123",
                            "cwd": "/tmp/demo",
                            "title": "Demo",
                            "createdAt": "2026-04-09T00:00:00Z",
                            "updatedAt": "2026-04-09T00:05:00Z",
                        }
                    ),
                ),
            )
            conn.commit()
            conn.close()
            (home / ".codebuddy").mkdir()
            (config_root / "logs").mkdir()

            output = StringIO()
            with patch.object(find_codebuddy_logs.platform, "system", return_value="Linux"), \
                patch.object(find_codebuddy_logs.Path, "home", return_value=home), \
                patch.object(sys, "argv", ["find_codebuddy_logs.py", "14"]), \
                redirect_stdout(output):
                try:
                    find_codebuddy_logs.main()
                except SystemExit:
                    pass

            payload = json.loads(output.getvalue())
            self.assertEqual(payload["total_sessions"], 1)
            self.assertEqual(payload["projects_dir"], str(config_root))

    def test_detect_tool_codebuddy_registry_uses_session_db_not_project_jsonl(self):
        codebuddy_patterns = [
            pattern
            for patterns in detect_tool.TOOLS["codebuddy"]["log_paths"].values()
            for pattern in patterns
        ]

        self.assertTrue(any("codebuddy-sessions.vscdb" in pattern for pattern in codebuddy_patterns))
        self.assertFalse(any(".jsonl" in pattern for pattern in codebuddy_patterns))

    def test_export_logs_prefers_codebuddy_source_with_session_data(self):
        import export_logs

        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / ".codebuddy").mkdir()
            config_root = home / ".config" / "CodeBuddy"
            config_root.mkdir(parents=True)
            (config_root / "codebuddy-sessions.vscdb").write_text("db")

            with patch.object(export_logs.platform, "system", return_value="Linux"), \
                patch.object(export_logs.Path, "home", return_value=home):
                source, tool_name = export_logs.find_source("codebuddy")

            self.assertEqual(tool_name, "CodeBuddy")
            self.assertEqual(source, config_root)

    def test_validate_scan_payload_rejects_bad_approval_command_shape(self):
        payload_path = ROOT / "tests/fixtures/tmp-invalid-payload.json"
        payload_path.write_text(
            json.dumps(
                {
                    "visibility": "approval",
                    "kind": "scan_approval",
                    "run_state": {"state": "idle"},
                    "card": {
                        "title": "Export recent logs",
                        "body": "Need one command.",
                        "command": "python3 foo.py\npython3 bar.py",
                    },
                }
            )
        )
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_scan_payload.py"), str(payload_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        finally:
            payload_path.unlink(missing_ok=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("single command string", result.stderr)

    def test_validate_scan_payload_accepts_reference_fixture_payloads(self):
        fixture_dir = ROOT / "tests/fixtures/presentation"
        for name in ["internal.json", "progress.json", "approval.json", "failure.json", "result.json", "result-empty.json"]:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_scan_payload.py"), str(fixture_dir / name)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(result.stdout.strip(), "OK")

    def test_contract_payload_examples_are_validator_clean(self):
        contract = json.loads((ROOT / "references/scan-presentation-contract.json").read_text())
        for key in ["internal", "progress", "approval", "failure", "result", "result_empty"]:
            payload_path = ROOT / f"tests/fixtures/tmp-contract-{key}.json"
            payload_path.write_text(json.dumps(contract["payload_examples"][key]))
            try:
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS / "validate_scan_payload.py"), str(payload_path)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            finally:
                payload_path.unlink(missing_ok=True)
            self.assertEqual(result.stdout.strip(), "OK")

    def test_fix_block_no_longer_includes_clear_rule(self):
        fix_blocks = (ROOT / "references/fix-blocks.md").read_text()
        self.assertNotIn("Use /clear or /compact", fix_blocks)
        self.assertIn("keep replies compact", fix_blocks)

    def test_vibecheck_optimize_updates_existing_instruction_file_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            instruction_path = base / "AGENTS.md"
            instruction_path.write_text("# Existing rules\n")
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tools": [
                                {
                                    "tool_id": "codex",
                                    "optimization_strategy": {"primary_targets": []},
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Biggest waste patterns",
                                            "patterns": [
                                                {"key": "idle_narration"},
                                                {"key": "verbose_output"},
                                            ],
                                            "target_files": [
                                                {
                                                    "kind": "instruction_file",
                                                    "file": str(instruction_path),
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                )
            )

            result = run_json("vibecheck_optimize.py", payload_path, "codex", 1)
            content = instruction_path.read_text()
            second = run_json("vibecheck_optimize.py", payload_path, "codex", 1)
            content_after_second = instruction_path.read_text()
            backup_exists = Path(result["applied"][0]["backup_path"]).exists()

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["applied"]), 1)
        self.assertTrue(result["applied"][0]["backup_created"])
        self.assertTrue(backup_exists)
        self.assertIn("Vibecheck Cost Rules", content)
        self.assertIn("Do not spend a turn narrating", content)
        self.assertIn("Redirect noisy build/test/install output", content)
        self.assertNotIn("/clear", content)
        self.assertEqual(content.count("<!-- vibecheck:cost-rules:start -->"), 1)
        self.assertTrue(second["ok"])
        self.assertEqual(content_after_second.count("<!-- vibecheck:cost-rules:start -->"), 1)

    def test_vibecheck_optimize_never_creates_missing_instruction_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            missing_path = base / "CLAUDE.md"
            payload_path = base / "payload.json"
            payload_path.write_text(
                json.dumps(
                    {
                        "optimization_plan": {
                            "tools": [
                                {
                                    "tool_id": "claude_code",
                                    "optimization_strategy": {"primary_targets": []},
                                    "steps": [
                                        {
                                            "rank": 1,
                                            "title": "Biggest waste patterns",
                                            "patterns": [{"key": "idle_narration"}],
                                            "target_files": [
                                                {
                                                    "kind": "instruction_file",
                                                    "file": str(missing_path),
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                )
            )

            result = run_json("vibecheck_optimize.py", payload_path, "claude_code", 1)

        self.assertTrue(result["ok"])
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["skipped"][0]["reason"], "missing_or_not_editable")
        self.assertFalse(missing_path.exists())

    def test_sync_scan_artifacts_reports_clean_state(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "sync_scan_artifacts.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "OK")


if __name__ == "__main__":
    unittest.main()
