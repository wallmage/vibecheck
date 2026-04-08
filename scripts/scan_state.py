#!/usr/bin/env python3
"""Build structured scan state payloads for host integrations."""
import json
import sys

from scan_contract import (
    INTERNAL_EVENT_TYPES,
    PAYLOAD_KINDS,
    PROGRESS_STAGES,
    TECHNICAL_DETAILS_DEFAULT,
    TECHNICAL_DETAILS_LABEL,
)


def usage():
    print(
        "Usage:\n"
        "  scan_state.py internal <event_type> <summary>\n"
        "  scan_state.py progress <stage>\n"
        "  scan_state.py approval <title> <body> <command>\n"
        "  scan_state.py failure <user_message> [technical_details]",
        file=sys.stderr,
    )
    sys.exit(1)


def build_internal(event_type, summary):
    if event_type not in INTERNAL_EVENT_TYPES:
        print(
            f"Error: invalid internal event '{event_type}'. Expected one of: {', '.join(INTERNAL_EVENT_TYPES)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return {
        "visibility": "internal",
        "kind": PAYLOAD_KINDS["internal"],
        "run_state": {
            "state": "running",
        },
        "event": {
            "type": event_type,
            "summary": summary,
        },
    }


def build_progress(stage):
    if stage not in PROGRESS_STAGES:
        print(
            f"Error: invalid stage '{stage}'. Expected one of: {', '.join(PROGRESS_STAGES)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return {
        "visibility": "progress",
        "kind": PAYLOAD_KINDS["progress"],
        "run_state": {
            "state": "running",
            "stage": stage,
        },
        "message": stage,
    }


def build_approval(title, body, command):
    return {
        "visibility": "approval",
        "kind": PAYLOAD_KINDS["approval"],
        "run_state": {
            "state": "idle",
        },
        "card": {
            "title": title,
            "body": body,
            "command": command,
        },
    }


def build_failure(user_message, technical_details=None):
    payload = {
        "visibility": "result",
        "kind": PAYLOAD_KINDS["failure"],
        "run_state": {
            "state": "failed",
            "userMessage": user_message,
        },
        "error": {
            "user_message": user_message,
            "technical_details_disclosure_label": TECHNICAL_DETAILS_LABEL,
            "technical_details_default": TECHNICAL_DETAILS_DEFAULT,
        },
    }
    if technical_details:
        payload["run_state"]["technicalDetails"] = technical_details
        payload["error"]["technical_details"] = technical_details
    return payload


def main():
    if len(sys.argv) < 3:
        usage()

    mode = sys.argv[1]
    if mode == "internal":
        if len(sys.argv) != 4:
            usage()
        payload = build_internal(sys.argv[2], sys.argv[3])
    elif mode == "progress":
        if len(sys.argv) != 3:
            usage()
        payload = build_progress(sys.argv[2])
    elif mode == "approval":
        if len(sys.argv) != 5:
            usage()
        payload = build_approval(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "failure":
        if len(sys.argv) not in (3, 4):
            usage()
        payload = build_failure(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    else:
        usage()

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
