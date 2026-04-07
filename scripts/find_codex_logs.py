#!/usr/bin/env python3
"""Find Codex session logs from the last N days.

Codex stores sessions as JSONL under ~/.codex/sessions/YYYY/MM/DD/*.jsonl.
This script mirrors find_logs.py but targets Codex's session layout and emits
the same top-level JSON shape so the rest of vibecheck can stay consistent.
"""
import json
import os
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def detect_platform():
    s = platform.system()
    if s == 'Darwin':
        return 'mac'
    if s == 'Windows':
        return 'windows'
    return 'linux'


def default_codex_dir():
    return Path.home() / '.codex' / 'sessions'


def find_fallback_dirs():
    home = Path.home()
    names = ['vibecheck-logs', 'codex-logs']
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']

    for parent in parents:
        for name in names:
            d = parent / name
            if d.exists() and any(d.rglob('*.jsonl')):
                return d
    return None


def parse_session_meta(jsonl_path):
    try:
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if obj.get('type') != 'session_meta':
                    continue
                payload = obj.get('payload', {})
                ts = payload.get('timestamp') or obj.get('timestamp')
                cwd = payload.get('cwd')
                model_provider = payload.get('model_provider')
                return ts, cwd, model_provider
    except (OSError, json.JSONDecodeError):
        return None, None, None
    return None, None, None


def find_session_files(root_dir, days=14):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = []

    for jsonl in root_dir.rglob('*.jsonl'):
        ts, cwd, model_provider = parse_session_meta(jsonl)
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            continue
        if dt < cutoff:
            continue

        project = Path(cwd).name if cwd else 'unknown'
        sessions.append({
            'path': str(jsonl),
            'project': project,
            'cwd': cwd,
            'timestamp': ts,
            'date': dt.strftime('%Y-%m-%d'),
            'size_kb': jsonl.stat().st_size / 1024,
            'tool': 'codex',
            'model_provider': model_provider,
        })

    return sorted(sessions, key=lambda s: s['timestamp'])


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    explicit_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    source_type = 'direct'
    if explicit_dir and explicit_dir.exists():
        root_dir = explicit_dir
        source_type = 'explicit'
    else:
        root_dir = default_codex_dir()
        if not root_dir.exists():
            fallback = find_fallback_dirs()
            if fallback:
                root_dir = fallback
                source_type = 'fallback'

    if not root_dir.exists():
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': 'codex',
            'export_script': 'scripts/export_logs.py codex',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    sessions = find_session_files(root_dir, days)
    print(json.dumps({
        'platform': detect_platform(),
        'tool': 'codex',
        'source_type': source_type,
        'projects_dir': str(root_dir),
        'days_scanned': days,
        'total_sessions': len(sessions),
        'projects': list(sorted(set(s['project'] for s in sessions))),
        'date_range': {
            'first': sessions[0]['date'] if sessions else None,
            'last': sessions[-1]['date'] if sessions else None,
        },
        'total_size_mb': round(sum(s['size_kb'] for s in sessions) / 1024, 1),
        'sessions': sessions,
    }, indent=2))


if __name__ == '__main__':
    main()
