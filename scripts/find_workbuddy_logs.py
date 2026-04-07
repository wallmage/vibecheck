#!/usr/bin/env python3
"""Find WorkBuddy sessions from the last N days."""
import json
import os
import platform
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


APP_NAME = 'WorkBuddy'
TOOL_ID = 'workbuddy'


def detect_platform():
    system = platform.system()
    if system == 'Darwin':
        return 'mac'
    if system == 'Windows':
        return 'windows'
    return 'linux'


def default_app_root():
    home = Path.home()
    if platform.system() == 'Darwin':
        return home / 'Library' / 'Application Support' / APP_NAME
    if platform.system() == 'Windows':
        appdata = os.environ.get('APPDATA')
        return Path(appdata) / APP_NAME if appdata else home / 'AppData' / 'Roaming' / APP_NAME
    return home / f'.{TOOL_ID}'


def find_fallback_dirs():
    home = Path.home()
    names = ['vibecheck-logs', f'{TOOL_ID}-logs']
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']
    for parent in parents:
        for name in names:
            candidate = parent / name
            if candidate.exists() and any(candidate.rglob('*.vscdb')):
                return candidate
    return None


def open_db(path):
    conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def parse_ts(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 1_000_000_000_000:
            raw /= 1000.0
        return datetime.fromtimestamp(raw, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            raw = float(text)
            if raw > 1_000_000_000_000:
                raw /= 1000.0
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        try:
            return datetime.fromisoformat(text.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


def load_index_sessions(index_db, cutoff, logs_dir):
    sessions = []
    if not index_db.exists():
        return sessions

    conn = open_db(index_db)
    try:
        rows = conn.execute("SELECT key, value FROM ItemTable WHERE key LIKE 'session:%'").fetchall()
    except sqlite3.DatabaseError:
        rows = []
    finally:
        conn.close()

    for row in rows:
        try:
            data = json.loads(row['value'])
        except Exception:
            continue
        updated = parse_ts(data.get('updatedAt') or data.get('createdAt'))
        if not updated or updated < cutoff:
            continue
        cwd = data.get('cwd')
        project = Path(cwd).name if cwd else 'unknown'
        sessions.append({
            'path': str(index_db),
            'project': project,
            'cwd': cwd,
            'timestamp': updated.isoformat(),
            'date': updated.strftime('%Y-%m-%d'),
            'size_kb': index_db.stat().st_size / 1024,
            'tool': TOOL_ID,
            'conversation_id': data.get('conversationId') or row['key'].split(':', 1)[-1],
            'title': data.get('title') or 'Untitled',
            'status': data.get('status'),
            'created_at': data.get('createdAt'),
            'updated_at': data.get('updatedAt'),
            'session_index_db': str(index_db),
            'logs_dir': str(logs_dir) if logs_dir.exists() else None,
            'source': 'session_index',
        })
    return sorted(sessions, key=lambda session: session['timestamp'])


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    explicit_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    source_type = 'direct'

    if explicit_dir and explicit_dir.exists():
        root_dir = explicit_dir
        source_type = 'explicit'
    else:
        root_dir = default_app_root()
        if not root_dir.exists():
            fallback = find_fallback_dirs()
            if fallback:
                root_dir = fallback
                source_type = 'fallback'

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    index_db = root_dir / 'codebuddy-sessions.vscdb'
    logs_dir = root_dir / 'logs'
    sessions = load_index_sessions(index_db, cutoff, logs_dir) if root_dir.exists() else []

    if not sessions:
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': TOOL_ID,
            'export_script': f'scripts/export_logs.py {TOOL_ID}',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    print(json.dumps({
        'platform': detect_platform(),
        'tool': TOOL_ID,
        'source_type': source_type,
        'projects_dir': str(root_dir),
        'days_scanned': days,
        'total_sessions': len(sessions),
        'projects': list(sorted(set(session['project'] for session in sessions))),
        'date_range': {
            'first': sessions[0]['date'] if sessions else None,
            'last': sessions[-1]['date'] if sessions else None,
        },
        'total_size_mb': round(sum(session['size_kb'] for session in sessions) / 1024, 1),
        'sessions': sessions,
    }, indent=2))


if __name__ == '__main__':
    main()
