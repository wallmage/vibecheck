#!/usr/bin/env python3
"""Find Cursor workspace databases from the last N days."""
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


def cursor_user_dir():
    home = Path.home()
    if platform.system() == 'Darwin':
        return home / 'Library' / 'Application Support' / 'Cursor' / 'User'
    if platform.system() == 'Windows':
        appdata = os.environ.get('APPDATA')
        return Path(appdata) / 'Cursor' / 'User' if appdata else home / 'AppData' / 'Roaming' / 'Cursor' / 'User'
    return home / '.config' / 'Cursor' / 'User'


def find_fallback_dirs():
    home = Path.home()
    names = ['vibecheck-logs', 'cursor-logs']
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']
    for parent in parents:
        for name in names:
            d = parent / name
            if d.exists() and any(d.rglob('state.vscdb')):
                return d
    return None


def load_workspace_path(workspace_json):
    try:
        data = json.loads(workspace_json.read_text())
        if isinstance(data, dict):
            folder = data.get('folder')
            if folder:
                return folder.replace('file://', '')
            config = data.get('configuration')
            if config:
                return config
    except Exception:
        pass
    return None


def find_workspace_dbs(root_dir, days=14):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = []

    if root_dir.name == 'workspaceStorage':
        workspace_root = root_dir
        global_db = root_dir.parent / 'globalStorage' / 'state.vscdb'
    else:
        workspace_root = root_dir / 'workspaceStorage'
        global_db = root_dir / 'globalStorage' / 'state.vscdb'

    if not workspace_root.exists():
        return sessions

    for db in workspace_root.rglob('state.vscdb'):
        mtime = datetime.fromtimestamp(db.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            continue
        workspace_json = db.parent / 'workspace.json'
        workspace_path = load_workspace_path(workspace_json) if workspace_json.exists() else None
        project = Path(workspace_path).name if workspace_path else db.parent.name
        sessions.append({
            'path': str(db),
            'project': project,
            'workspace_path': workspace_path,
            'workspace_hash': db.parent.name,
            'timestamp': mtime.isoformat(),
            'date': mtime.strftime('%Y-%m-%d'),
            'size_kb': db.stat().st_size / 1024,
            'tool': 'cursor',
            'global_db': str(global_db) if global_db.exists() else None,
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
        root_dir = cursor_user_dir()
        if not root_dir.exists():
            fallback = find_fallback_dirs()
            if fallback:
                root_dir = fallback
                source_type = 'fallback'

    sessions = find_workspace_dbs(root_dir, days) if root_dir.exists() else []
    if not sessions:
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': 'cursor',
            'export_script': 'scripts/export_logs.py cursor',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    print(json.dumps({
        'platform': detect_platform(),
        'tool': 'cursor',
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
