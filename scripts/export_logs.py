#!/usr/bin/env python3
"""Export recent session logs to a visible folder.

For sandboxed tools (Cowork, Cursor, etc.) that can't access hidden dirs.
Copies only the last N days of .jsonl files, preserving project structure.
Cross-platform: Mac, Windows, Linux. No dependencies beyond stdlib.

Usage: python3 export_logs.py [days] [destination]
  days:        how many days back to export (default: 14)
  destination: where to copy (default: ~/vibecheck-logs)
"""
import shutil, sys, os, platform
from pathlib import Path
from datetime import datetime, timedelta, timezone

def find_source():
    """Find where session logs live."""
    home = Path.home()

    # Claude Code
    claude = home / '.claude' / 'projects'
    if claude.exists():
        return claude, 'Claude Code'

    # Windows Claude Code
    appdata = os.environ.get('APPDATA')
    if appdata:
        win_claude = Path(appdata) / 'Claude' / 'projects'
        if win_claude.exists():
            return win_claude, 'Claude Code'

    # Codex
    codex = home / '.codex' / 'sessions'
    if codex.exists():
        return codex, 'Codex'

    return None, None

def export(days=14, dest=None):
    src, tool_name = find_source()
    if not src:
        print("Could not find any AI coding tool logs.")
        print("Checked: ~/.claude/projects, %APPDATA%/Claude/projects, ~/.codex/sessions")
        return False

    if dest is None:
        dest = Path.home() / 'vibecheck-logs'
    else:
        dest = Path(dest)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    copied = 0
    total_size = 0

    for f in src.rglob('*.jsonl'):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            continue

        # Preserve project directory structure: src/projectname/file.jsonl → dest/projectname/file.jsonl
        rel = f.relative_to(src)
        target_dir = dest / rel.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target_dir / rel.name)
        copied += 1
        total_size += f.stat().st_size

    size_mb = total_size / (1024 * 1024)

    if copied == 0:
        print(f"No sessions found in the last {days} days.")
        return False

    print(f"Done! Copied {copied} sessions ({size_mb:.1f} MB) from {tool_name}.")
    print(f"Location: {dest}")
    print()
    print("Now go back to your AI tool and re-run /vibecheck scan.")
    return True

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    dest = sys.argv[2] if len(sys.argv) > 2 else None
    export(days, dest)

if __name__ == "__main__":
    main()
