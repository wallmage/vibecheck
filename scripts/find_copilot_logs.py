#!/usr/bin/env python3
"""Find GitHub Copilot / VS Code chat session logs from the last N days.

Supports:
- VS Code stable / insiders local chat session files
- Workspace sessions under workspaceStorage/*/chatSessions
- Global empty-window sessions under globalStorage/emptyWindowChatSessions
- Explicit folders containing exported chat JSON
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


def expand_user_roots():
    home = Path.home()
    appdata = os.environ.get('APPDATA')
    roots = []
    if platform.system() == 'Darwin':
        roots.extend([
            home / 'Library' / 'Application Support' / 'Code' / 'User',
            home / 'Library' / 'Application Support' / 'Code - Insiders' / 'User',
        ])
    elif platform.system() == 'Windows':
        base = Path(appdata) if appdata else home / 'AppData' / 'Roaming'
        roots.extend([
            base / 'Code' / 'User',
            base / 'Code - Insiders' / 'User',
        ])
    else:
        roots.extend([
            home / '.config' / 'Code' / 'User',
            home / '.config' / 'Code - Insiders' / 'User',
        ])
    return [root for root in roots if root.exists()]


def find_fallback_dirs():
    home = Path.home()
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']
    names = ['vibecheck-logs', 'copilot-logs', 'vscode-chat-logs']
    for parent in parents:
        for name in names:
            candidate = parent / name
            if not candidate.exists():
                continue
            if any(candidate.rglob('*.json')) or any(candidate.rglob('*.jsonl')):
                return candidate
    return None


def is_session_json(obj):
    return isinstance(obj, dict) and (
        'sessionId' in obj
        or ('requests' in obj and isinstance(obj['requests'], list))
    )


def parse_export_meta(path):
    try:
        if path.suffix == '.json':
            with open(path) as f:
                obj = json.load(f)
            if not is_session_json(obj):
                return None
            session = obj
        elif path.suffix == '.jsonl':
            session = reconstruct_jsonl(path)
            if not session:
                return None
        else:
            return None
    except (OSError, json.JSONDecodeError):
        return None

    created = parse_datetime(session.get('creationDate') or session.get('lastMessageDate'))
    last = parse_datetime(session.get('lastMessageDate') or session.get('creationDate'))
    return {
        'session_id': session.get('sessionId') or path.stem,
        'creation_dt': created or last,
        'last_dt': last or created,
        'title': session.get('customTitle'),
        'request_count': len(session.get('requests', [])),
    }


def parse_path(path):
    if isinstance(path, list):
        return path
    if isinstance(path, str):
        if path.startswith('/'):
            return [part for part in path.split('/') if part]
        if '.' in path:
            return [part for part in path.split('.') if part]
        return [path]
    return []


def set_path(root, path, value):
    cur = root
    for idx, part in enumerate(path):
        last = idx == len(path) - 1
        if isinstance(part, str) and part.isdigit():
            part = int(part)
        next_part = None if last else path[idx + 1]

        if last:
            if isinstance(cur, list) and isinstance(part, int):
                while len(cur) <= part:
                    cur.append(None)
                cur[part] = value
            elif isinstance(cur, dict):
                cur[part] = value
            return

        if isinstance(cur, list) and isinstance(part, int):
            while len(cur) <= part:
                cur.append({} if not isinstance(next_part, int) else [])
            if cur[part] is None:
                cur[part] = {} if not isinstance(next_part, int) else []
            cur = cur[part]
        else:
            if part not in cur or cur[part] is None:
                cur[part] = {} if not isinstance(next_part, int) else []
            cur = cur[part]


def get_path(root, path):
    cur = root
    for part in path:
        if isinstance(part, str) and part.isdigit():
            part = int(part)
        if isinstance(cur, list):
            if not isinstance(part, int) or part >= len(cur):
                return None
            cur = cur[part]
        elif isinstance(cur, dict):
            if part not in cur:
                return None
            cur = cur[part]
        else:
            return None
    return cur


def delete_path(root, path):
    if not path:
        return
    parent = get_path(root, path[:-1]) if len(path) > 1 else root
    key = path[-1]
    if isinstance(key, str) and key.isdigit():
        key = int(key)
    if isinstance(parent, list) and isinstance(key, int) and key < len(parent):
        parent.pop(key)
    elif isinstance(parent, dict):
        parent.pop(key, None)


def reconstruct_jsonl(path):
    state = None
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

                if is_session_json(obj):
                    state = obj
                    continue

                kind = obj.get('kind')
                mutation_path = parse_path(obj.get('path'))
                value = obj.get('value')

                if state is None:
                    if isinstance(value, dict):
                        state = value
                    else:
                        state = {}

                if kind in (0, 1):
                    if not mutation_path:
                        if isinstance(value, dict):
                            state = value
                    else:
                        set_path(state, mutation_path, value)
                elif kind == 2:
                    target = get_path(state, mutation_path)
                    if target is None:
                        set_path(state, mutation_path, [])
                        target = get_path(state, mutation_path)
                    if isinstance(target, list):
                        target.append(value)
                elif kind == 3:
                    delete_path(state, mutation_path)
                elif isinstance(value, dict) and is_session_json(value):
                    state = value
    except OSError:
        return None
    return state if is_session_json(state or {}) else None


def discover_user_sessions(user_dir):
    sessions = {}

    for session_path in user_dir.glob('workspaceStorage/*/chatSessions/*'):
        if session_path.suffix not in ('.json', '.jsonl'):
            continue
        workspace_dir = session_path.parent.parent
        session_id = session_path.stem
        workspace_manifest = workspace_dir / 'workspace.json'
        workspace_path = None
        if workspace_manifest.exists():
            try:
                with open(workspace_manifest) as f:
                    manifest = json.load(f)
                folder = manifest.get('folder') or manifest.get('workspace') or manifest.get('configPath')
                if isinstance(folder, str):
                    workspace_path = folder.replace('file://', '')
            except (OSError, json.JSONDecodeError):
                workspace_path = None

        existing = sessions.get(session_id)
        if existing and existing['path'].suffix == '.jsonl':
            continue
        sessions[session_id] = {
            'path': session_path,
            'workspace_path': workspace_path,
            'workspace_hash': workspace_dir.name,
            'source': 'workspace',
            'user_dir': user_dir,
        }

    global_dir = user_dir / 'globalStorage' / 'emptyWindowChatSessions'
    for session_path in global_dir.glob('*'):
        if session_path.suffix not in ('.json', '.jsonl'):
            continue
        session_id = session_path.stem
        existing = sessions.get(session_id)
        if existing and existing['path'].suffix == '.jsonl':
            continue
        sessions[session_id] = {
            'path': session_path,
            'workspace_path': None,
            'workspace_hash': 'empty-window',
            'source': 'global',
            'user_dir': user_dir,
        }

    return sessions


def discover_explicit_sessions(root_dir):
    sessions = {}
    for session_path in root_dir.rglob('*'):
        if not session_path.is_file() or session_path.suffix not in ('.json', '.jsonl'):
            continue
        meta = parse_export_meta(session_path)
        if not meta:
            continue
        session_id = meta['session_id']
        existing = sessions.get(session_id)
        if existing and existing['path'].suffix == '.jsonl':
            continue
        workspace_path = None
        workspace_hash = 'explicit'
        source = 'explicit'
        parts = session_path.parts
        if 'workspaceStorage' in parts and 'chatSessions' in parts:
            idx = parts.index('workspaceStorage')
            if idx + 1 < len(parts):
                workspace_hash = parts[idx + 1]
            source = 'workspace'
            workspace_manifest = session_path.parent.parent / 'workspace.json'
            if workspace_manifest.exists():
                try:
                    with open(workspace_manifest) as f:
                        manifest = json.load(f)
                    folder = manifest.get('folder') or manifest.get('workspace') or manifest.get('configPath')
                    if isinstance(folder, str):
                        workspace_path = folder.replace('file://', '')
                except (OSError, json.JSONDecodeError):
                    workspace_path = None
        elif 'emptyWindowChatSessions' in parts:
            workspace_hash = 'empty-window'
            source = 'global'
        sessions[session_id] = {
            'path': session_path,
            'workspace_path': workspace_path,
            'workspace_hash': workspace_hash,
            'source': source,
            'user_dir': root_dir,
        }
    return sessions


def session_entry(info, cutoff):
    meta = parse_export_meta(info['path'])
    if not meta:
        return None
    ts = meta['last_dt'] or meta['creation_dt']
    if not ts or ts < cutoff:
        return None

    workspace_path = info.get('workspace_path')
    if workspace_path:
        project = Path(workspace_path).name or info['workspace_hash']
    elif info['source'] == 'global':
        project = 'empty-window'
    else:
        project = info['path'].parent.name

    return {
        'path': str(info['path']),
        'project': project,
        'cwd': workspace_path,
        'timestamp': ts.isoformat(),
        'date': ts.strftime('%Y-%m-%d'),
        'size_kb': info['path'].stat().st_size / 1024,
        'tool': 'github_copilot',
        'workspace_hash': info.get('workspace_hash'),
        'title': meta.get('title'),
        'session_id': meta['session_id'],
        'request_count': meta.get('request_count', 0),
        'source': info['source'],
        'user_dir': str(info['user_dir']),
    }


def find_session_files(root_dir, days=14, explicit=False):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = []

    if explicit:
        discovered = discover_explicit_sessions(root_dir)
        for info in discovered.values():
            entry = session_entry(info, cutoff)
            if entry:
                sessions.append(entry)
    else:
        for user_dir in expand_user_roots():
            discovered = discover_user_sessions(user_dir)
            for info in discovered.values():
                entry = session_entry(info, cutoff)
                if entry:
                    sessions.append(entry)

    sessions.sort(key=lambda s: s['timestamp'])
    return sessions


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    explicit_dir = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else None

    if explicit_dir and explicit_dir.exists():
        source_type = 'explicit'
        root_dir = explicit_dir
        sessions = find_session_files(root_dir, days, explicit=True)
    else:
        source_type = 'direct'
        sessions = find_session_files(None, days, explicit=False)
        root_dir = None
        if not sessions:
            fallback = find_fallback_dirs()
            if fallback:
                source_type = 'fallback'
                root_dir = fallback
                sessions = find_session_files(root_dir, days, explicit=True)

    if not sessions:
        print(json.dumps({
            'error': 'no_logs',
            'platform': detect_platform(),
            'tool': 'github_copilot',
            'export_script': 'scripts/export_logs.py copilot',
            'dest': '~/vibecheck-logs',
            'sessions': [],
            'total_sessions': 0,
        }, indent=2))
        sys.exit(0)

    print(json.dumps({
        'platform': detect_platform(),
        'tool': 'github_copilot',
        'source_type': source_type,
        'projects_dir': str(root_dir) if root_dir else None,
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
