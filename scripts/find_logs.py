#!/usr/bin/env python3
"""Cross-platform finder for Claude-style JSONL session logs.

Handles sandboxed environments (Cowork, VMs, containers) by checking
fallback locations and returning platform-specific setup instructions."""
import os, sys, platform, glob, json
from pathlib import Path
from datetime import datetime, timedelta, timezone

def find_claude_dir():
    """Find the default Claude Code data directory cross-platform."""
    home = Path.home()
    claude_dir = home / ".claude"
    if claude_dir.exists():
        return claude_dir
    # Windows
    appdata = os.environ.get("APPDATA")
    if appdata:
        alt = Path(appdata) / "Claude"
        if alt.exists():
            return alt
    return None

def find_projects_dir(claude_dir):
    """Find the projects directory containing session logs."""
    projects = claude_dir / "projects"
    if projects.exists():
        return projects
    return None

def find_session_files(projects_dir, days=14):
    """Find all .jsonl session files from the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sessions = []

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        project_name = project_dir.name

        for jsonl in project_dir.glob("*.jsonl"):
            mtime = datetime.fromtimestamp(jsonl.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                continue

            first_ts = None
            try:
                with open(jsonl) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            if 'timestamp' in obj:
                                first_ts = obj['timestamp']
                                break
                        except json.JSONDecodeError:
                            continue
            except (IOError, PermissionError):
                continue

            if not first_ts:
                continue

            try:
                dt = datetime.fromisoformat(first_ts.replace('Z', '+00:00'))
            except ValueError:
                continue

            if dt < cutoff:
                continue

            sessions.append({
                'path': str(jsonl),
                'project': project_name,
                'timestamp': first_ts,
                'date': dt.strftime('%Y-%m-%d'),
                'size_kb': jsonl.stat().st_size / 1024,
            })

    return sorted(sessions, key=lambda s: s['timestamp'])

def find_fallback_dirs():
    """Check common visible locations where logs might be copied to.

    Checks: ~/vibecheck-logs, ~/Desktop/vibecheck-logs, ~/Documents/vibecheck-logs,
    ~/Developer/vibecheck-logs, plus same with 'claude-logs' name.
    Also checks anywhere a .jsonl file exists in mounted/visible dirs."""
    home = Path.home()
    names = ['vibecheck-logs', 'claude-logs']
    parents = [home, home / 'Desktop', home / 'Documents', home / 'Developer']

    for parent in parents:
        for name in names:
            d = parent / name
            if d.exists() and any(d.rglob("*.jsonl")):
                return d
    return None

def detect_platform():
    """Detect OS for user-facing instructions."""
    s = platform.system()
    if s == 'Darwin':
        return 'mac'
    elif s == 'Windows':
        return 'windows'
    else:
        return 'linux'

def get_setup_info():
    """Return setup info for sandbox users."""
    plat = detect_platform()
    return {
        'platform': plat,
        'export_script': 'scripts/export_logs.py',
        'dest': '~/vibecheck-logs',
    }

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14

    # Accept explicit logs dir as second arg: find_logs.py 14 /path/to/logs
    # The directory should contain Claude-style project subfolders with .jsonl sessions.
    explicit_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    projects_dir = None
    source_type = 'direct'  # direct | fallback | explicit

    if explicit_dir and explicit_dir.exists():
        projects_dir = explicit_dir
        source_type = 'explicit'
    else:
        claude_dir = find_claude_dir()
        projects_dir = find_projects_dir(claude_dir) if claude_dir else None

        if not projects_dir:
            fallback = find_fallback_dirs()
            if fallback:
                projects_dir = fallback
                source_type = 'fallback'

    if not projects_dir:
        setup = get_setup_info()
        print(json.dumps({
            "error": "no_logs",
            "platform": setup['platform'],
            "export_script": setup['export_script'],
            "dest": setup['dest'],
            "sessions": [],
            "total_sessions": 0,
        }, indent=2))
        sys.exit(0)

    sessions = find_session_files(projects_dir, days)

    result = {
        "platform": detect_platform(),
        "source_type": source_type,
        "projects_dir": str(projects_dir),
        "days_scanned": days,
        "total_sessions": len(sessions),
        "projects": list(set(s['project'] for s in sessions)),
        "date_range": {
            "first": sessions[0]['date'] if sessions else None,
            "last": sessions[-1]['date'] if sessions else None,
        },
        "total_size_mb": round(sum(s['size_kb'] for s in sessions) / 1024, 1),
        "sessions": sessions,
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
