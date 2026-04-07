#!/usr/bin/env python3
"""Find Windsurf session logs from the last N days.

Primary supported source:
- Official transcript hook output under ~/.windsurf/transcripts/*.jsonl

Compatibility fallback:
- Older local Windsurf / Codeium cache paths under ~/.codeium/windsurf/cascade/*
"""
import glob
import json
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


def parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        raw = float(value)
        if raw > 1_000_000_000_000:
            raw = raw / 1000.0
        return datetime.fromtimestamp(raw, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.isdigit():
            raw = int(text)
            if raw > 1_000_000_000_000:
                raw = raw / 1000.0
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        try:
            return datetime.fromisoformat(text.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


def default_roots():
    home = Path.home()
    return [
        home / '.windsurf' / 'transcripts',
        home / '.codeium' / 'windsurf' / 'cascade',
    ]


def find_fallback_dirs():
    home = Path.home()
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']
    names = ['vibecheck-logs', 'windsurf-logs']
    for parent in parents:
        for name in names:
            candidate = parent / name
            if not candidate.exists():
                continue
            if any(candidate.rglob('*.jsonl')) or any(candidate.rglob('*.json')):
                return candidate
    return None


def transcript_meta(path):
    first_dt = None
    last_dt = None
    model = None
    project = None
    cwd = None

    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = parse_datetime(obj.get('timestamp') or obj.get('created_at') or obj.get('createdAt'))
                if ts:
                    if first_dt is None:
                        first_dt = ts
                    last_dt = ts

                step_type = obj.get('type')
                payload = obj.get(step_type, {}) if isinstance(step_type, str) else {}
                if isinstance(payload, dict):
                    if cwd is None:
                        cwd = payload.get('cwd') or payload.get('workspace_path') or payload.get('repo_path')
                    if model is None:
                        for key in ('model', 'model_name', 'selected_model', 'modelId'):
                            value = payload.get(key)
                            if isinstance(value, str) and value:
                                model = value
                                break
                    if project is None:
                        for key in ('repo_name', 'project_name', 'workspace_name'):
                            value = payload.get(key)
                            if isinstance(value, str) and value:
                                project = value
                                break
    except OSError:
        return None

    return {
        'first_dt': first_dt,
        'last_dt': last_dt,
        'model': model,
        'cwd': cwd,
        'project': project,
    }


def iter_candidates(root_dir):
    root_dir = Path(root_dir).expanduser()
    if not root_dir.exists():
        return []
    if root_dir.is_file():
        return [root_dir]
    candidates = []
    for suffix in ('*.jsonl', '*.json'):
        candidates.extend(root_dir.rglob(suffix))
    deduped = []
    seen = set()
    for path in candidates:
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(path)
    return deduped


def classify_source(path):
    text = str(path)
    if '/.windsurf/transcripts/' in text:
        return 'official_transcript'
    if '/.codeium/windsurf/cascade/' in text:
        return 'legacy_cache'
    return 'explicit'


def find_session_files(root_dir, days=14):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = []
    for path in iter_candidates(root_dir):
        if path.suffix not in ('.jsonl', '.json'):
            continue
        meta = transcript_meta(path)
        if not meta:
            continue
        ts = meta['last_dt'] or meta['first_dt']
        if not ts or ts < cutoff:
            continue
        cwd = meta.get('cwd')
        project = meta.get('project') or (Path(cwd).name if cwd else path.stem)
        sessions.append({
            'path': str(path),
            'project': project,
            'cwd': cwd,
            'timestamp': ts.isoformat(),
            'date': ts.strftime('%Y-%m-%d'),
            'size_kb': path.stat().st_size / 1024,
            'tool': 'windsurf',
            'model': meta.get('model'),
            'source': classify_source(path),
        })
    sessions.sort(key=lambda s: s['timestamp'])
    return sessions


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    explicit_dir = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else None

    sessions = []
    source_type = 'direct'
    root_dir = explicit_dir if explicit_dir and explicit_dir.exists() else None

    if root_dir:
        source_type = 'explicit'
        sessions = find_session_files(root_dir, days)
    else:
        for root in default_roots():
            sessions.extend(find_session_files(root, days))
        if not sessions:
            fallback = find_fallback_dirs()
            if fallback:
                root_dir = fallback
                source_type = 'fallback'
                sessions = find_session_files(root_dir, days)

    sessions.sort(key=lambda s: s['timestamp'])

    if not sessions:
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': 'windsurf',
            'export_script': 'scripts/export_logs.py windsurf',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    print(json.dumps({
        'platform': detect_platform(),
        'tool': 'windsurf',
        'source_type': source_type,
        'projects_dir': str(root_dir) if root_dir else None,
        'days_scanned': days,
        'total_sessions': len(sessions),
        'projects': list(sorted(set(s['project'] for s in sessions))),
        'sources': list(sorted(set(s['source'] for s in sessions))),
        'date_range': {
            'first': sessions[0]['date'] if sessions else None,
            'last': sessions[-1]['date'] if sessions else None,
        },
        'total_size_mb': round(sum(s['size_kb'] for s in sessions) / 1024, 1),
        'sessions': sessions,
    }, indent=2))


if __name__ == '__main__':
    main()
