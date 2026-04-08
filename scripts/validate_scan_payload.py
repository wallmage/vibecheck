#!/usr/bin/env python3
"""Validate structured scan payloads against vibecheck's presentation contract."""
import json
import sys
from pathlib import Path

from scan_contract import (
    EMPTY_RESULT_SECTION_KINDS,
    PAYLOAD_KINDS,
    RESULT_SECTION_KINDS,
    SUMMARY_METRIC_IDS,
    TECHNICAL_DETAILS_LABEL,
    VISIBILITY_VALUES,
    build_contract_dict,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "references" / "scan-presentation-contract.json"


def fail(message):
    print(f"Invalid payload: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def require_string(value, field_name):
    if not isinstance(value, str) or not value:
        fail(f"{field_name} must be a non-empty string")


def require_dict(value, field_name):
    if not isinstance(value, dict):
        fail(f"{field_name} must be an object")


def require_list(value, field_name):
    if not isinstance(value, list):
        fail(f"{field_name} must be an array")


def require_number(value, field_name):
    if not isinstance(value, (int, float)):
        fail(f"{field_name} must be numeric")


def validate_progress(payload, contract):
    if payload.get("kind") != PAYLOAD_KINDS["progress"]:
        fail("progress payload must use kind scan_progress")
    run_state = payload.get("run_state")
    require_dict(run_state, "run_state")
    if run_state.get("state") != "running":
        fail("progress run_state.state must be running")
    stage = run_state.get("stage")
    if stage not in contract["progress_stages"]:
        fail("progress stage must be one of the contract stages")
    if payload.get("message") != stage:
        fail("progress message must match the stage")


def validate_approval(payload, contract):
    if payload.get("kind") != PAYLOAD_KINDS["approval"]:
        fail("approval payload must use kind scan_approval")
    run_state = payload.get("run_state")
    require_dict(run_state, "run_state")
    if run_state.get("state") != "idle":
        fail("approval run_state.state must be idle")
    card = payload.get("card")
    require_dict(card, "card")
    require_string(card.get("title"), "card.title")
    require_string(card.get("body"), "card.body")
    require_string(card.get("command"), "card.command")
    if "\n" in card["command"]:
        fail("approval card.command must be a single command string")


def validate_failure(payload, contract):
    if payload.get("kind") != PAYLOAD_KINDS["failure"]:
        fail("failure payload must use kind scan_failure")
    run_state = payload.get("run_state")
    require_dict(run_state, "run_state")
    if run_state.get("state") != "failed":
        fail("failure run_state.state must be failed")
    require_string(run_state.get("userMessage"), "run_state.userMessage")
    error = payload.get("error")
    require_dict(error, "error")
    require_string(error.get("user_message"), "error.user_message")
    if error.get("technical_details_disclosure_label") != TECHNICAL_DETAILS_LABEL:
        fail("failure disclosure label must be Technical details")
    if error.get("technical_details_default") != contract["transcript_rules"]["technical_details_default"]:
        fail("failure technical_details_default must match the contract")


def validate_internal(payload, contract):
    if payload.get("kind") != PAYLOAD_KINDS["internal"]:
        fail("internal payload must use kind scan_internal")
    run_state = payload.get("run_state")
    require_dict(run_state, "run_state")
    if run_state.get("state") != "running":
        fail("internal run_state.state must be running")
    event = payload.get("event")
    require_dict(event, "event")
    if event.get("type") not in contract["validation_rules"]["internal_event_types"]:
        fail("internal event.type must be in the allowed internal event types")
    require_string(event.get("summary"), "event.summary")


def validate_result(payload, contract):
    if payload.get("kind") != PAYLOAD_KINDS["result"]:
        fail("result payload must use kind scan_result")
    run_state = payload.get("run_state")
    require_dict(run_state, "run_state")
    if run_state.get("state") != "completed":
        fail("result run_state.state must be completed")
    if run_state.get("resultPayload") != PAYLOAD_KINDS["result"]:
        fail("result run_state.resultPayload must be scan_result")

    hero = payload.get("hero")
    require_dict(hero, "hero")
    require_string(hero.get("eyebrow"), "hero.eyebrow")
    require_string(hero.get("headline"), "hero.headline")
    require_string(hero.get("supporting_text"), "hero.supporting_text")

    summary = payload.get("summary")
    require_dict(summary, "summary")
    sessions_analyzed = summary.get("sessions_analyzed")
    if not isinstance(sessions_analyzed, int) or sessions_analyzed < 0:
        fail("summary.sessions_analyzed must be a non-negative integer")

    summary_metrics = payload.get("summary_metrics")
    require_list(summary_metrics, "summary_metrics")
    if len(summary_metrics) != 3:
        fail("summary_metrics must contain exactly 3 items")
    metric_ids = [metric.get("id") for metric in summary_metrics]
    if metric_ids != SUMMARY_METRIC_IDS:
        fail("summary_metrics ids must match the contract ordering")

    sections = payload.get("sections")
    require_list(sections, "sections")
    section_kinds = [section.get("kind") for section in sections]
    if sessions_analyzed == 0:
        if section_kinds != EMPTY_RESULT_SECTION_KINDS:
            fail("empty-state result sections must be hero, metrics, next_action")
        if payload.get("top_waste_patterns") != []:
            fail("empty-state result must not include top waste patterns")
    else:
        if section_kinds != RESULT_SECTION_KINDS:
            fail("result sections must be hero, metrics, patterns, next_action")
        top_patterns = payload.get("top_waste_patterns")
        require_list(top_patterns, "top_waste_patterns")
        if not 1 <= len(top_patterns) <= 3:
            fail("result must include between 1 and 3 top_waste_patterns when sessions are present")

    next_action = payload.get("next_action")
    require_dict(next_action, "next_action")
    require_string(next_action.get("title"), "next_action.title")
    require_string(next_action.get("body"), "next_action.body")

    unified_scan = payload.get("unified_scan")
    if unified_scan is not None:
        require_dict(unified_scan, "unified_scan")
        require_string(unified_scan.get("mode"), "unified_scan.mode")
        require_number(unified_scan.get("tools_scanned"), "unified_scan.tools_scanned")
        if "tools_detected" in unified_scan:
            require_number(unified_scan.get("tools_detected"), "unified_scan.tools_detected")
        if "tools_unsupported" in unified_scan:
            require_number(unified_scan.get("tools_unsupported"), "unified_scan.tools_unsupported")
        if "tools_skipped" in unified_scan:
            require_number(unified_scan.get("tools_skipped"), "unified_scan.tools_skipped")
        if "tools_failed" in unified_scan:
            require_number(unified_scan.get("tools_failed"), "unified_scan.tools_failed")
        require_number(unified_scan.get("instruction_targets"), "unified_scan.instruction_targets")
        if "optimization_targets" in unified_scan:
            require_number(unified_scan.get("optimization_targets"), "unified_scan.optimization_targets")

    breakdowns = payload.get("breakdowns")
    if breakdowns is not None:
        require_dict(breakdowns, "breakdowns")
        for bucket in ("tools", "providers", "models", "platforms"):
            require_list(breakdowns.get(bucket, []), f"breakdowns.{bucket}")

    header_statistics = payload.get("header_statistics")
    if header_statistics is not None:
        require_dict(header_statistics, "header_statistics")
        require_dict(header_statistics.get("overall"), "header_statistics.overall")
        require_list(header_statistics.get("tools", []), "header_statistics.tools")
        require_list(header_statistics.get("models", []), "header_statistics.models")

    optimization_plan = payload.get("optimization_plan")
    if optimization_plan is not None:
        require_dict(optimization_plan, "optimization_plan")
        require_list(optimization_plan.get("tool_sequence", []), "optimization_plan.tool_sequence")
        require_list(optimization_plan.get("tools", []), "optimization_plan.tools")

    coverage = payload.get("coverage")
    if coverage is not None:
        require_dict(coverage, "coverage")
        for bucket in ("detected_tools", "unsupported_tools", "skipped_tools", "failed_tools"):
            require_list(coverage.get(bucket, []), f"coverage.{bucket}")

    optimization_targets = payload.get("optimization_targets")
    if optimization_targets is not None:
        require_list(optimization_targets, "optimization_targets")


def validate_payload(payload, contract):
    visibility = payload.get("visibility")
    if visibility not in VISIBILITY_VALUES:
        fail("visibility must match one of the contract visibility values")

    if visibility == "progress":
        validate_progress(payload, contract)
    elif visibility == "approval":
        validate_approval(payload, contract)
    elif visibility == "internal":
        validate_internal(payload, contract)
    elif payload.get("kind") == PAYLOAD_KINDS["failure"]:
        validate_failure(payload, contract)
    else:
        validate_result(payload, contract)


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_scan_payload.py <payload.json>", file=sys.stderr)
        sys.exit(1)

    payload = load_json(sys.argv[1])
    contract = load_json(CONTRACT_PATH)
    if contract != build_contract_dict():
        fail(f"contract file drift detected: {CONTRACT_PATH}")
    validate_payload(payload, contract)
    print("OK")


if __name__ == "__main__":
    main()
