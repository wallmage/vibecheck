import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


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
    def test_claude_analysis_includes_confidence_and_pricing_metadata(self):
        data = run_json("analyze_claude_sessions.py", ROOT / "tests/fixtures/claude/sessions.json")
        self.assertEqual(data["analysis_confidence"]["label"], "measured")
        self.assertEqual(data["pricing_metadata"]["billing_mode"], "full_billing")
        self.assertEqual(data["pricing_metadata"]["registry_version"], "2026-04-08")

    def test_codex_analysis_includes_confidence_and_pricing_metadata(self):
        data = run_json("analyze_codex_sessions.py", ROOT / "tests/fixtures/codex/sessions.json")
        self.assertEqual(data["analysis_confidence"]["label"], "measured")
        self.assertEqual(data["pricing_metadata"]["canonical_model"], "gpt-5.4")
        self.assertEqual(data["pricing_metadata"]["billing_mode"], "full_billing")

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


if __name__ == "__main__":
    unittest.main()
