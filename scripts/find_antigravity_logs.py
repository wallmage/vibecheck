#!/usr/bin/env python3
"""Find Antigravity conversation artifact directories from the last N days."""
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def detect_platform():
    system = platform.system()
    if system == 'Darwin':
        return 'mac'
    if system == 'Windows':
        return 'windows'
    return 'linux'


def default_root():
    return Path.home() / '.gemini' / 'antigravity'


def find_fallback_dirs():
    home = Path.home()
    names = ['vibecheck-logs', 'antigravity-logs']
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']
    for parent in parents:
        for name in names:
            candidate = parent / name
            if candidate.exists() and any(candidate.rglob('*.metadata.json')):
                return candidate
    return None


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def session_entries(root_dir, days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    brain_dir = root_dir / 'brain' if root_dir.name != 'brain' else root_dir
    sessions = []
    if not brain_dir.exists():
        return sessions

    for convo_dir in brain_dir.iterdir():
        if not convo_dir.is_dir():
            continue
        metadata_files = sorted(convo_dir.glob('*.metadata.json'))
        markdown_files = sorted(convo_dir.glob('*.md'))
        if not metadata_files and not markdown_files:
            continue
        updated = None
        summaries = []
        for meta in metadata_files:
            try:
                data = json.loads(meta.read_text())
            except Exception:
                continue
            ts = parse_ts(data.get('updatedAt'))
            if ts and (updated is None or ts > updated):
                updated = ts
            summary = data.get('summary')
            if isinstance(summary, str) and summary:
                summaries.append(summary)
        if updated is None:
            updated = datetime.fromtimestamp(convo_dir.stat().st_mtime, tz=timezone.utc)
        if updated < cutoff:
            continue
        sessions.append({
            'path': str(convo_dir),
            'project': convo_dir.name,
            'cwd': None,
            'timestamp': updated.isoformat(),
            'date': updated.strftime('%Y-%m-%d'),
            'size_kb': sum(path.stat().st_size for path in convo_dir.rglob('*') if path.is_file()) / 1024,
            'tool': 'antigravity',
            'conversation_id': convo_dir.name,
            'title': summaries[0] if summaries else convo_dir.name,
            'artifact_count': len(markdown_files),
            'metadata_count': len(metadata_files),
            'source': 'brain_artifacts',
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
        root_dir = default_root()
        if not root_dir.exists():
            fallback = find_fallback_dirs()
            if fallback:
                root_dir = fallback
                source_type = 'fallback'

    sessions = session_entries(root_dir, days) if root_dir.exists() else []
    if not sessions:
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': 'antigravity',
            'export_script': 'scripts/export_logs.py antigravity',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    print(json.dumps({
        'platform': detect_platform(),
        'tool': 'antigravity',
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
