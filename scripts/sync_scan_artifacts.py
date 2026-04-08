#!/usr/bin/env python3
"""Check or rewrite scan presentation artifacts from the shared contract."""
import argparse
import json
import sys
from pathlib import Path

from scan_contract import build_contract_dict


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "references" / "scan-presentation-contract.json"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "presentation"

FIXTURE_MAP = {
    "internal": FIXTURE_DIR / "internal.json",
    "progress": FIXTURE_DIR / "progress.json",
    "approval": FIXTURE_DIR / "approval.json",
    "failure": FIXTURE_DIR / "failure.json",
    "result": FIXTURE_DIR / "result.json",
    "result_empty": FIXTURE_DIR / "result-empty.json",
}


def canonical_json(data):
    return json.dumps(data, indent=2) + "\n"


def check_or_write(path, expected, write):
    expected_text = canonical_json(expected)
    current_text = path.read_text() if path.exists() else None
    if current_text == expected_text:
        return True
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected_text)
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Rewrite artifacts to match the shared contract.")
    args = parser.parse_args()

    contract = build_contract_dict()
    mismatches = []

    if not check_or_write(CONTRACT_PATH, contract, args.write):
        mismatches.append(str(CONTRACT_PATH))

    for key, path in FIXTURE_MAP.items():
        if not check_or_write(path, contract["payload_examples"][key], args.write):
            mismatches.append(str(path))

    if mismatches and not args.write:
        print("Out of sync artifacts:", file=sys.stderr)
        for path in mismatches:
            print(f"  {path}", file=sys.stderr)
        sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
