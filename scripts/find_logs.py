#!/usr/bin/env python3
"""Cross-platform Claude Code session log finder."""
import os, sys, platform, glob, json
from pathlib import Path
from datetime import datetime, timedelta, timezone

def find_claude_dir():
    """Find ~/.claude/ cross-platform."""
    home = Path.home()
    claude_dir = home / ".claude"
    if claude_dir.exists():
        return claude_dir
    # Windows fallback
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
            # Quick check: file modification time
            mtime = datetime.fromtimestamp(jsonl.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                continue

            # Get first timestamp from file
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
    """Check for logs copied to visible locations (for sandbox/Cowork use)."""
    home = Path.home()
    candidates = [
        home / "vibecheck-logs",
        home / "claude-logs",
        home / "Developer" / "vibecheck-logs",
        home / "Developer" / "claude-logs",
        home / "Documents" / "vibecheck-logs",
        home / "Documents" / "claude-logs",
    ]
    for d in candidates:
        if d.exists() and any(d.rglob("*.jsonl")):
            return d
    return None

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14

    # Accept explicit logs dir as second arg: find_logs.py 14 /path/to/logs
    explicit_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if explicit_dir and explicit_dir.exists():
        projects_dir = explicit_dir
    else:
        claude_dir = find_claude_dir()
        projects_dir = find_projects_dir(claude_dir) if claude_dir else None

        if not projects_dir:
            # Try fallback locations (for sandbox/Cowork)
            fallback = find_fallback_dirs()
            if fallback:
                projects_dir = fallback
            else:
                print(json.dumps({
                    "error": "no_logs",
                    "message": "Session logs not found. If running in a sandbox (Claude Desktop/Cowork), run this in your terminal first:",
                    "setup_command": 'cp -r ~/.claude/projects ~/vibecheck-logs',
                    "then": "Re-run /vibecheck scan after copying.",
                    "sessions": [],
                }))
                sys.exit(0)

    sessions = find_session_files(projects_dir, days)

    result = {
        "platform": platform.system(),
        "claude_dir": str(claude_dir),
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
