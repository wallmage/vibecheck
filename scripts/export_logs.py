#!/usr/bin/env python3
"""Export recent supported session logs to a visible folder.

For sandboxed tools that cannot access hidden dirs.
Copies only the last N days of supported .jsonl session files, preserving project structure.
Cross-platform: Mac, Windows, Linux. No dependencies beyond stdlib.

Usage: python3 export_logs.py [tool] [days] [destination]
  tool:        claude | codex | cursor | openclaw | copilot | windsurf | trae | qoder | codebuddy | workbuddy | antigravity (default: auto-detect)
  days:        how many days back to export (default: 14)
  destination: where to copy (default: ~/vibecheck-logs)
"""
import shutil, sys, os, platform
from pathlib import Path
from datetime import datetime, timedelta, timezone

def find_source(requested_tool=None):
    """Find where session logs live."""
    home = Path.home()

    # Claude Code
    claude = home / '.claude' / 'projects'
    if claude.exists() and requested_tool in (None, 'claude'):
        return claude, 'Claude Code'

    # Windows Claude Code
    appdata = os.environ.get('APPDATA')
    if appdata and requested_tool in (None, 'claude'):
        win_claude = Path(appdata) / 'Claude' / 'projects'
        if win_claude.exists():
            return win_claude, 'Claude Code'

    # Codex
    codex = home / '.codex' / 'sessions'
    if codex.exists() and requested_tool in (None, 'codex'):
        return codex, 'Codex'

    # Cursor
    if requested_tool in (None, 'cursor'):
        if platform.system() == 'Darwin':
            cursor = home / 'Library' / 'Application Support' / 'Cursor' / 'User'
        elif platform.system() == 'Windows':
            appdata = os.environ.get('APPDATA')
            cursor = Path(appdata) / 'Cursor' / 'User' if appdata else home / 'AppData' / 'Roaming' / 'Cursor' / 'User'
        else:
            cursor = home / '.config' / 'Cursor' / 'User'
        if cursor.exists():
            return cursor, 'Cursor'

    # OpenClaw
    openclaw = home / '.openclaw'
    if openclaw.exists() and requested_tool in (None, 'openclaw'):
        return openclaw, 'OpenClaw'

    # Windsurf
    for candidate in [home / '.windsurf', home / '.codeium' / 'windsurf']:
        if candidate.exists() and requested_tool in (None, 'windsurf'):
            return candidate, 'Windsurf'

    # GitHub Copilot / VS Code
    if requested_tool in (None, 'copilot'):
        if platform.system() == 'Darwin':
            for candidate in [
                home / 'Library' / 'Application Support' / 'Code' / 'User',
                home / 'Library' / 'Application Support' / 'Code - Insiders' / 'User',
            ]:
                if candidate.exists():
                    return candidate, 'GitHub Copilot'
        elif platform.system() == 'Windows':
            appdata = os.environ.get('APPDATA')
            bases = [
                Path(appdata) / 'Code' / 'User' if appdata else home / 'AppData' / 'Roaming' / 'Code' / 'User',
                Path(appdata) / 'Code - Insiders' / 'User' if appdata else home / 'AppData' / 'Roaming' / 'Code - Insiders' / 'User',
            ]
            for candidate in bases:
                if candidate.exists():
                    return candidate, 'GitHub Copilot'
        else:
            for candidate in [
                home / '.config' / 'Code' / 'User',
                home / '.config' / 'Code - Insiders' / 'User',
            ]:
                if candidate.exists():
                    return candidate, 'GitHub Copilot'

    # TRAE
    if requested_tool in (None, 'trae'):
        if platform.system() == 'Darwin':
            trae = home / 'Library' / 'Application Support' / 'Trae' / 'User'
        elif platform.system() == 'Windows':
            appdata = os.environ.get('APPDATA')
            trae = Path(appdata) / 'Trae' / 'User' if appdata else home / 'AppData' / 'Roaming' / 'Trae' / 'User'
        else:
            trae = home / '.config' / 'Trae' / 'User'
        if trae.exists():
            return trae, 'TRAE'

    # Qoder
    if requested_tool in (None, 'qoder'):
        if platform.system() == 'Darwin':
            qoder = home / 'Library' / 'Application Support' / 'Qoder' / 'User'
        elif platform.system() == 'Windows':
            appdata = os.environ.get('APPDATA')
            qoder = Path(appdata) / 'Qoder' / 'User' if appdata else home / 'AppData' / 'Roaming' / 'Qoder' / 'User'
        else:
            qoder = home / '.config' / 'Qoder' / 'User'
        if qoder.exists():
            return qoder, 'Qoder'

    if requested_tool in (None, 'codebuddy'):
        for candidate in [
            home / 'Library' / 'Application Support' / 'CodeBuddy',
            home / '.codebuddy',
            home / '.config' / 'CodeBuddy',
        ]:
            if candidate.exists():
                return candidate, 'CodeBuddy'

    if requested_tool in (None, 'workbuddy'):
        for candidate in [
            home / 'Library' / 'Application Support' / 'WorkBuddy',
            home / '.workbuddy',
            home / '.config' / 'WorkBuddy',
        ]:
            if candidate.exists():
                return candidate, 'WorkBuddy'

    if requested_tool in (None, 'antigravity'):
        antigravity = home / '.gemini' / 'antigravity'
        if antigravity.exists():
            return antigravity, 'Google Antigravity'

    return None, None

def export(days=14, dest=None, tool=None):
    src, tool_name = find_source(tool)
    if not src:
        print("Could not find supported session logs.")
        print("Checked: ~/.claude/projects, %APPDATA%/Claude/projects, ~/.codex/sessions, Cursor User storage, ~/.openclaw, VS Code User storage, ~/.windsurf, ~/.codeium/windsurf, Trae User storage, Qoder User storage, CodeBuddy, WorkBuddy, ~/.gemini/antigravity")
        return False

    if dest is None:
        dest = Path.home() / 'vibecheck-logs'
    else:
        dest = Path(dest)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    copied = 0
    total_size = 0

    if tool == 'cursor' or tool_name == 'Cursor':
        copied = 0
        total_size = 0
        for rel_path in [
            Path('workspaceStorage'),
            Path('globalStorage') / 'state.vscdb',
            Path('globalStorage') / 'state.vscdb-wal',
            Path('globalStorage') / 'state.vscdb-shm',
        ]:
            source = src / rel_path
            if source.is_dir():
                for f in source.rglob('*'):
                    if not f.is_file():
                        continue
                    if f.name not in ('state.vscdb', 'state.vscdb-wal', 'state.vscdb-shm', 'workspace.json'):
                        continue
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff and f.name != 'state.vscdb':
                        continue
                    rel = f.relative_to(src)
                    target_dir = dest / rel.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target_dir / rel.name)
                    copied += 1
                    total_size += f.stat().st_size
            elif source.exists():
                target_dir = dest / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target_dir / source.name)
                copied += 1
                total_size += source.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No Cursor sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} Cursor files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'openclaw' or tool_name == 'OpenClaw':
        copied = 0
        total_size = 0
        for agent_dir in (src / 'agents').glob('*'):
            if not agent_dir.is_dir():
                continue

            for name in ('AGENTS.md', 'SOUL.md', 'HEARTBEAT.md', 'IDENTITY.md', 'TOOLS.md', 'SOUVENIR.md', 'GOALS.md', 'BOOT.md'):
                source = agent_dir / name
                if not source.exists():
                    continue
                rel = source.relative_to(src)
                target_dir = dest / rel.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target_dir / source.name)
                copied += 1
                total_size += source.stat().st_size

            sessions_dir = agent_dir / 'sessions'
            if not sessions_dir.exists():
                continue

            store = sessions_dir / 'sessions.json'
            if store.exists():
                rel = store.relative_to(src)
                target_dir = dest / rel.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(store, target_dir / store.name)
                copied += 1
                total_size += store.stat().st_size

            for transcript in sessions_dir.glob('*.jsonl'):
                mtime = datetime.fromtimestamp(transcript.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    continue
                rel = transcript.relative_to(src)
                target_dir = dest / rel.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(transcript, target_dir / transcript.name)
                copied += 1
                total_size += transcript.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No OpenClaw sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} OpenClaw files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'copilot' or tool_name == 'GitHub Copilot':
        copied = 0
        total_size = 0
        patterns = [
            src / 'workspaceStorage',
            src / 'globalStorage' / 'emptyWindowChatSessions',
        ]
        for base in patterns:
            if base.is_dir():
                for f in base.rglob('*'):
                    if not f.is_file():
                        continue
                    if f.suffix not in ('.json', '.jsonl'):
                        continue
                    if 'chatSessions' not in str(f) and 'emptyWindowChatSessions' not in str(f) and f.name != 'workspace.json':
                        continue
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff and f.name != 'workspace.json':
                        continue
                    rel = f.relative_to(src)
                    target_dir = dest / rel.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target_dir / rel.name)
                    copied += 1
                    total_size += f.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No GitHub Copilot / VS Code chat sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} Copilot / VS Code chat files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'windsurf' or tool_name == 'Windsurf':
        copied = 0
        total_size = 0
        for rel_path in [
            Path('transcripts'),
            Path('.'),
        ]:
            source = src / rel_path
            if not source.exists():
                continue
            for f in source.rglob('*'):
                if not f.is_file():
                    continue
                if f.name in ('.windsurfrules', 'rules'):
                    pass
                elif f.suffix not in ('.json', '.jsonl'):
                    continue
                if 'transcripts' not in str(f) and 'cascade' not in str(f):
                    if f.name not in ('.windsurfrules', 'rules'):
                        continue
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff and f.suffix in ('.json', '.jsonl'):
                    continue
                rel = f.relative_to(src)
                target_dir = dest / rel.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target_dir / rel.name)
                copied += 1
                total_size += f.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No Windsurf transcripts found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} Windsurf files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'trae' or tool_name == 'TRAE':
        copied = 0
        total_size = 0
        for rel_path in [
            Path('workspaceStorage'),
            Path('globalStorage') / 'state.vscdb',
            Path('globalStorage') / 'state.vscdb-wal',
            Path('globalStorage') / 'state.vscdb-shm',
        ]:
            source = src / rel_path
            if source.is_dir():
                for f in source.rglob('*'):
                    if not f.is_file():
                        continue
                    if f.name not in ('state.vscdb', 'state.vscdb-wal', 'state.vscdb-shm', 'workspace.json'):
                        continue
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff and f.name != 'state.vscdb':
                        continue
                    rel = f.relative_to(src)
                    target_dir = dest / rel.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target_dir / rel.name)
                    copied += 1
                    total_size += f.stat().st_size
            elif source.exists():
                target_dir = dest / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target_dir / source.name)
                copied += 1
                total_size += source.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No TRAE sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} TRAE files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'qoder' or tool_name == 'Qoder':
        copied = 0
        total_size = 0
        for rel_path in [
            Path('workspaceStorage'),
            Path('globalStorage') / 'state.vscdb',
            Path('globalStorage') / 'state.vscdb-wal',
            Path('globalStorage') / 'state.vscdb-shm',
        ]:
            source = src / rel_path
            if source.is_dir():
                for f in source.rglob('*'):
                    if not f.is_file():
                        continue
                    if f.name not in ('state.vscdb', 'state.vscdb-wal', 'state.vscdb-shm', 'workspace.json'):
                        continue
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff and f.name != 'state.vscdb':
                        continue
                    rel = f.relative_to(src)
                    target_dir = dest / rel.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target_dir / rel.name)
                    copied += 1
                    total_size += f.stat().st_size
            elif source.exists():
                target_dir = dest / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target_dir / source.name)
                copied += 1
                total_size += source.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No Qoder sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} Qoder files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'codebuddy' or tool_name == 'CodeBuddy':
        copied = 0
        total_size = 0
        for rel_path in [Path('codebuddy-sessions.vscdb'), Path('logs')]:
            source = src / rel_path
            if source.is_dir():
                for f in source.rglob('codebuddy.log'):
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff:
                        continue
                    rel = f.relative_to(src)
                    target_dir = dest / rel.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target_dir / rel.name)
                    copied += 1
                    total_size += f.stat().st_size
            elif source.exists():
                target_dir = dest / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target_dir / source.name)
                copied += 1
                total_size += source.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No CodeBuddy sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} CodeBuddy files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'workbuddy' or tool_name == 'WorkBuddy':
        copied = 0
        total_size = 0
        for rel_path in [Path('codebuddy-sessions.vscdb'), Path('logs'), Path('User') / 'workspaceStorage', Path('User') / 'globalStorage' / 'state.vscdb']:
            source = src / rel_path
            if source.is_dir():
                for f in source.rglob('*'):
                    if not f.is_file():
                        continue
                    if f.name not in ('codebuddy.log', 'state.vscdb', 'workspace.json'):
                        continue
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                    if mtime < cutoff and f.name not in ('state.vscdb', 'workspace.json'):
                        continue
                    rel = f.relative_to(src)
                    target_dir = dest / rel.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target_dir / rel.name)
                    copied += 1
                    total_size += f.stat().st_size
            elif source.exists():
                target_dir = dest / rel_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target_dir / source.name)
                copied += 1
                total_size += source.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No WorkBuddy sessions found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} WorkBuddy files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

    if tool == 'antigravity' or tool_name == 'Google Antigravity':
        copied = 0
        total_size = 0
        for rel_path in [Path('brain'), Path('knowledge'), Path('browser_recordings')]:
            source = src / rel_path
            if not source.exists():
                continue
            for f in source.rglob('*'):
                if not f.is_file():
                    continue
                if f.suffix not in ('.md', '.json', '.webp') and '.resolved.' not in f.name and not f.name.endswith('.metadata.json'):
                    continue
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    continue
                rel = f.relative_to(src)
                target_dir = dest / rel.parent
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target_dir / rel.name)
                copied += 1
                total_size += f.stat().st_size

        size_mb = total_size / (1024 * 1024)
        if copied == 0:
            print(f"No Antigravity artifacts found in the last {days} days.")
            return False
        print(f"Done! Copied {copied} Antigravity files ({size_mb:.1f} MB).")
        print(f"Location: {dest}")
        print()
        print("Now go back to your AI tool and re-run /vibecheck scan.")
        return True

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
    args = sys.argv[1:]
    tool = None
    if args and args[0] in ('claude', 'codex', 'cursor', 'openclaw', 'copilot', 'windsurf', 'trae', 'qoder', 'codebuddy', 'workbuddy', 'antigravity'):
        tool = args.pop(0)
    days = int(args[0]) if args else 14
    dest = args[1] if len(args) > 1 else None
    export(days, dest, tool)

if __name__ == "__main__":
    main()
