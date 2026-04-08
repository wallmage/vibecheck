#!/usr/bin/env python3
"""Find OpenClaw session logs from the last N days.

OpenClaw stores per-agent session metadata in:
  ~/.openclaw/agents/<agentId>/sessions/sessions.json

Transcript JSONL files live beside that store:
  ~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl

This script emits the same top-level JSON shape as the other vibecheck finders.
"""
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
        if value > 1_000_000_000_000:
            value = value / 1000.0
        return datetime.fromtimestamp(value, tz=timezone.utc)
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


def default_openclaw_dir():
    return Path.home() / '.openclaw' / 'agents'


def find_fallback_dirs():
    home = Path.home()
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']
    names = ['vibecheck-logs', 'openclaw-logs']
    for parent in parents:
        for name in names:
            candidate = parent / name
            if not candidate.exists():
                continue
            if any(candidate.rglob('sessions.json')) or any(candidate.rglob('*.jsonl')):
                return candidate
    return None


def iter_session_dirs(root_dir):
    root_dir = Path(root_dir).expanduser()
    if not root_dir.exists():
        return []

    candidates = []
    if root_dir.name == 'sessions':
        candidates.append(root_dir)
    if (root_dir / 'agents').exists():
        for sessions_dir in (root_dir / 'agents').glob('*/sessions'):
            if sessions_dir.is_dir():
                candidates.append(sessions_dir)
    for sessions_dir in root_dir.glob('*/sessions'):
        if sessions_dir.is_dir():
            candidates.append(sessions_dir)
    if not candidates:
        for sessions_dir in root_dir.rglob('sessions'):
            if sessions_dir.is_dir():
                candidates.append(sessions_dir)

    deduped = []
    seen = set()
    for path in candidates:
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(path)
    return deduped


def load_store(sessions_dir):
    store_path = sessions_dir / 'sessions.json'
    if not store_path.exists():
        return {}
    try:
        with open(store_path) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_transcript_path(sessions_dir, session_id):
    exact = sessions_dir / f'{session_id}.jsonl'
    if exact.exists():
        return exact
    matches = sorted(glob.glob(str(sessions_dir / f'{session_id}*.jsonl')))
    return Path(matches[0]) if matches else None


def transcript_meta(transcript_path):
    first_dt = None
    last_dt = None
    detected_model = None

    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = (
                    obj.get('timestamp')
                    or obj.get('createdAt')
                    or obj.get('updatedAt')
                    or obj.get('message', {}).get('timestamp')
                )
                dt = parse_datetime(ts)
                if dt:
                    if first_dt is None:
                        first_dt = dt
                    last_dt = dt

                for key in ('model', 'modelName', 'modelId'):
                    value = obj.get(key) or obj.get('metadata', {}).get(key)
                    if not value:
                        value = obj.get('message', {}).get(key) or obj.get('message', {}).get('metadata', {}).get(key)
                    if value:
                        detected_model = value
                        break
    except OSError:
        return None

    return {
        'first_dt': first_dt,
        'last_dt': last_dt,
        'model': detected_model,
    }


def build_session_entry(sessions_dir, session_key, session_id, session_meta, cutoff):
    transcript_path = resolve_transcript_path(sessions_dir, session_id)
    if not transcript_path or not transcript_path.exists():
        return None

    transcript = transcript_meta(transcript_path)
    updated_dt = parse_datetime(
        session_meta.get('updatedAt')
        or session_meta.get('lastActiveAt')
        or session_meta.get('createdAt')
    )
    ts = updated_dt or (transcript and transcript.get('last_dt')) or (transcript and transcript.get('first_dt'))
    if not ts or ts < cutoff:
        return None

    agent_dir = sessions_dir.parent
    workspace_dir = session_meta.get('workspaceDir') or session_meta.get('workspace') or str(agent_dir)
    project = Path(workspace_dir).name if workspace_dir else agent_dir.name

    return {
        'path': str(transcript_path),
        'project': project or agent_dir.name,
        'cwd': workspace_dir,
        'timestamp': ts.isoformat(),
        'date': ts.strftime('%Y-%m-%d'),
        'size_kb': transcript_path.stat().st_size / 1024,
        'tool': 'openclaw',
        'agent_id': agent_dir.name,
        'agent_dir': str(agent_dir),
        'session_key': session_key,
        'session_id': session_id,
        'channel': session_meta.get('channel'),
        'display_name': session_meta.get('displayName') or session_meta.get('subject') or session_meta.get('room'),
        'model': session_meta.get('model') or (transcript or {}).get('model'),
        'source': 'sessions_store',
    }


def fallback_entries(sessions_dir, cutoff):
    entries = []
    agent_dir = sessions_dir.parent
    for transcript_path in sorted(sessions_dir.glob('*.jsonl')):
        meta = transcript_meta(transcript_path)
        ts = (meta or {}).get('last_dt') or (meta or {}).get('first_dt')
        if not ts or ts < cutoff:
            continue
        entries.append({
            'path': str(transcript_path),
            'project': agent_dir.name,
            'cwd': str(agent_dir),
            'timestamp': ts.isoformat(),
            'date': ts.strftime('%Y-%m-%d'),
            'size_kb': transcript_path.stat().st_size / 1024,
            'tool': 'openclaw',
            'agent_id': agent_dir.name,
            'agent_dir': str(agent_dir),
            'session_key': transcript_path.stem,
            'session_id': transcript_path.stem,
            'channel': None,
            'display_name': None,
            'model': (meta or {}).get('model'),
            'source': 'transcript_scan',
        })
    return entries


def find_session_files(root_dir, days=14):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = []

    for sessions_dir in iter_session_dirs(root_dir):
        store = load_store(sessions_dir)
        if store:
            for session_key, session_meta in store.items():
                if not isinstance(session_meta, dict):
                    continue
                session_id = session_meta.get('sessionId')
                if not session_id:
                    continue
                entry = build_session_entry(sessions_dir, session_key, session_id, session_meta, cutoff)
                if entry:
                    sessions.append(entry)
        else:
            sessions.extend(fallback_entries(sessions_dir, cutoff))

    sessions.sort(key=lambda s: s['timestamp'])
    return sessions


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    explicit_dir = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else None

    source_type = 'direct'
    if explicit_dir and explicit_dir.exists():
        root_dir = explicit_dir
        source_type = 'explicit'
    else:
        root_dir = default_openclaw_dir()
        if not root_dir.exists():
            fallback = find_fallback_dirs()
            if fallback:
                root_dir = fallback
                source_type = 'fallback'

    if not root_dir.exists():
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': 'openclaw',
            'export_script': 'scripts/export_logs.py openclaw',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    sessions = find_session_files(root_dir, days)
    print(json.dumps({
        'platform': detect_platform(),
        'tool': 'openclaw',
        'source_type': source_type,
        'projects_dir': str(root_dir),
        'days_scanned': days,
        'total_sessions': len(sessions),
        'projects': list(sorted(set(s['project'] for s in sessions))),
        'agents': list(sorted(set(s['agent_id'] for s in sessions))),
        'date_range': {
            'first': sessions[0]['date'] if sessions else None,
            'last': sessions[-1]['date'] if sessions else None,
        },
        'total_size_mb': round(sum(s['size_kb'] for s in sessions) / 1024, 1),
        'sessions': sessions,
    }, indent=2))


if __name__ == '__main__':
    main()
