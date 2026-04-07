#!/usr/bin/env python3
"""Auto-detect which AI coding tool the user has, find their logs.
Covers 90%+ of vibe coders. Falls back to asking for project folder."""
import os, sys, platform, json, glob, subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ============================================================
# TOOL REGISTRY — add new tools here
# ============================================================
# Each entry: {
#   name: display name
#   instruction_files: list of filenames the tool uses for system prompts
#   log_paths: {platform: [glob patterns]} for session logs
#   log_format: 'jsonl' | 'json' | 'sqlite' | 'markdown' | 'unknown'
#   config_paths: where config lives (for detection)
#   detect_files: files/dirs whose existence confirms this tool
# }

HOME = str(Path.home())
IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

APPDATA = os.environ.get('APPDATA', '')
LOCAL_APPDATA = os.environ.get('LOCALAPPDATA', '')

TOOLS = {
    'claude_code': {
        'name': 'Claude Code',
        'instruction_files': ['CLAUDE.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.claude/projects/*/*.jsonl'],
            'Linux': [f'{HOME}/.claude/projects/*/*.jsonl'],
            'Windows': [
                f'{APPDATA}/Claude/projects/*/*.jsonl',
                f'{HOME}/.claude/projects/*/*.jsonl',
            ],
        },
        'log_format': 'jsonl',
        'detect_files': [f'{HOME}/.claude'],
        'config_paths': [f'{HOME}/.claude/settings.json'],
    },
    'codex': {
        'name': 'OpenAI Codex CLI',
        'instruction_files': ['AGENTS.md', 'AGENTS.override.md', 'TEAM_GUIDE.md', '.agents.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.codex/log/*.log', f'{HOME}/.codex/sessions/*'],
            'Linux': [f'{HOME}/.codex/log/*.log', f'{HOME}/.codex/sessions/*'],
            'Windows': [f'{HOME}/.codex/log/*.log'],
        },
        'log_format': 'unknown',
        'detect_files': [f'{HOME}/.codex'],
        'config_paths': [f'{HOME}/.codex/config.json', f'{HOME}/.codex/config.yaml'],
    },
    'cursor': {
        'name': 'Cursor',
        'instruction_files': ['.cursorrules', '.cursor/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Cursor/User/workspaceStorage/*/state.vscdb'],
            'Linux': [f'{HOME}/.config/Cursor/User/workspaceStorage/*/state.vscdb'],
            'Windows': [f'{APPDATA}/Cursor/User/workspaceStorage/*/state.vscdb'],
        },
        'log_format': 'sqlite',
        'detect_files': [
            f'{HOME}/Library/Application Support/Cursor' if IS_MAC else '',
            f'{HOME}/.config/Cursor' if IS_LINUX else '',
            f'{APPDATA}/Cursor' if IS_WIN else '',
        ],
        'config_paths': [],
    },
    'windsurf': {
        'name': 'Windsurf (Codeium)',
        'instruction_files': ['.windsurfrules'],
        'log_paths': {
            'Darwin': [f'{HOME}/.codeium/windsurf/cascade/*'],
            'Linux': [f'{HOME}/.codeium/windsurf/cascade/*'],
            'Windows': [f'{HOME}/.codeium/windsurf/cascade/*'],
        },
        'log_format': 'json',
        'detect_files': [f'{HOME}/.codeium/windsurf'],
        'config_paths': [],
    },
    'cline': {
        'name': 'Cline',
        'instruction_files': ['.clinerules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/*/api_conversation_history.json'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/*/api_conversation_history.json'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/saoudrizwan.claude-dev/tasks/*/api_conversation_history.json'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev' if IS_MAC else '',
            f'{HOME}/.config/Code/User/globalStorage/saoudrizwan.claude-dev' if IS_LINUX else '',
            f'{APPDATA}/Code/User/globalStorage/saoudrizwan.claude-dev' if IS_WIN else '',
        ],
        'config_paths': [],
    },
    'roo_code': {
        'name': 'Roo Code',
        'instruction_files': ['.roo/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/tasks/*'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/tasks/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/rooveterinaryinc.roo-cline/tasks/*'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/.roo',
            f'{HOME}/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline' if IS_MAC else '',
        ],
        'config_paths': [],
    },
    'aider': {
        'name': 'Aider',
        'instruction_files': ['.aider.conf.yml', '.aider.model.settings.yml'],
        'log_paths': {
            # Aider writes .aider.chat.history.md in project dirs
            # We scan common project locations
            'Darwin': [f'{HOME}/**/.aider.chat.history.md'],
            'Linux': [f'{HOME}/**/.aider.chat.history.md'],
            'Windows': [f'{HOME}/**/.aider.chat.history.md'],
        },
        'log_format': 'markdown',
        'detect_files': [f'{HOME}/.aider.conf.yml'],
        'config_paths': [f'{HOME}/.aider.conf.yml'],
    },
    'gemini_cli': {
        'name': 'Gemini CLI',
        'instruction_files': ['GEMINI.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.gemini/tmp/*/logs.json', f'{HOME}/.gemini/sessions/*'],
            'Linux': [f'{HOME}/.gemini/tmp/*/logs.json', f'{HOME}/.gemini/sessions/*'],
            'Windows': [f'{HOME}/.gemini/tmp/*/logs.json'],
        },
        'log_format': 'json',
        'detect_files': [f'{HOME}/.gemini'],
        'config_paths': [f'{HOME}/.gemini/settings.json'],
    },
    'github_copilot': {
        'name': 'GitHub Copilot',
        'instruction_files': ['.github/copilot-instructions.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/workspaceStorage/*/chatSessions/*.json'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/github.copilot-chat/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/github.copilot-chat/*'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/Library/Application Support/Code/User/globalStorage/github.copilot-chat' if IS_MAC else '',
            f'{HOME}/.config/Code/User/globalStorage/github.copilot-chat' if IS_LINUX else '',
        ],
        'config_paths': [],
    },
    'opencode': {
        'name': 'OpenCode',
        'instruction_files': ['OPENCODE.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.local/share/opencode/message/*/*.json', f'{HOME}/.local/share/opencode/session/*/*.json'],
            'Linux': [f'{HOME}/.local/share/opencode/message/*/*.json', f'{HOME}/.local/share/opencode/session/*/*.json'],
            'Windows': [f'{LOCAL_APPDATA}/opencode/message/*/*.json'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/.local/share/opencode',
            f'{HOME}/.config/opencode',
        ],
        'config_paths': [f'{HOME}/.config/opencode/config.json'],
    },
    'kilo_code': {
        'name': 'Kilo Code',
        'instruction_files': ['.kilo/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/kilocode.kilo-code/tasks/*'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/kilocode.kilo-code/tasks/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/kilocode.kilo-code/tasks/*'],
        },
        'log_format': 'json',
        'detect_files': [],
        'config_paths': [],
    },
    'augment': {
        'name': 'Augment Code',
        'instruction_files': ['augment-guidelines.md'],
        'log_paths': {},
        'log_format': 'unknown',
        'detect_files': [],
        'config_paths': [],
    },
    'openclaw': {
        'name': 'OpenClaw',
        'instruction_files': ['SOUL.md', 'HEARTBEAT.md', 'AGENTS.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.openclaw/agents/*/sessions/*.jsonl'],
            'Linux': [f'{HOME}/.openclaw/agents/*/sessions/*.jsonl'],
            'Windows': [f'{HOME}/.openclaw/agents/*/sessions/*.jsonl'],
        },
        'log_format': 'jsonl',
        'detect_files': [f'{HOME}/.openclaw'],
        'config_paths': [f'{HOME}/.openclaw/openclaw.json'],
        'always_on': True,  # 24/7 agent — different waste profile
    },
    'codebuddy': {
        'name': 'CodeBuddy (Tencent)',
        'instruction_files': ['CODEBUDDY.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.codebuddy/projects/*/*.jsonl'],
            'Linux': [f'{HOME}/.codebuddy/projects/*/*.jsonl'],
            'Windows': [f'{HOME}/.codebuddy/projects/*/*.jsonl'],
        },
        'log_format': 'jsonl',
        'detect_files': [f'{HOME}/.codebuddy'],
        'config_paths': [],
    },
    'workbuddy': {
        'name': 'WorkBuddy (Tencent)',
        'instruction_files': ['WORKBUDDY.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.workbuddy/projects/*/*.jsonl'],
            'Linux': [f'{HOME}/.workbuddy/projects/*/*.jsonl'],
            'Windows': [f'{HOME}/.workbuddy/projects/*/*.jsonl'],
        },
        'log_format': 'jsonl',
        'detect_files': [f'{HOME}/.workbuddy'],
        'config_paths': [],
    },
    'trae': {
        'name': 'TRAE (ByteDance)',
        'instruction_files': ['.trae/rules', '.rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Trae/User/workspaceStorage/*/state.vscdb',
                       f'{HOME}/.trae/sessions/*'],
            'Linux': [f'{HOME}/.config/Trae/User/workspaceStorage/*/state.vscdb',
                      f'{HOME}/.trae/sessions/*'],
            'Windows': [f'{APPDATA}/Trae/User/workspaceStorage/*/state.vscdb'],
        },
        'log_format': 'sqlite',
        'detect_files': [
            f'{HOME}/Library/Application Support/Trae' if IS_MAC else '',
            f'{HOME}/.config/Trae' if IS_LINUX else '',
            f'{APPDATA}/Trae' if IS_WIN else '',
        ],
        'config_paths': [],
    },
    'qoder': {
        'name': 'Qoder (Alibaba)',
        'instruction_files': ['.qoder/rules', '.qoder/config.json'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Qoder/User/workspaceStorage/*/state.vscdb'],
            'Linux': [f'{HOME}/.config/Qoder/User/workspaceStorage/*/state.vscdb'],
            'Windows': [f'{APPDATA}/Qoder/User/workspaceStorage/*/state.vscdb'],
        },
        'log_format': 'sqlite',
        'detect_files': [
            f'{HOME}/Library/Application Support/Qoder' if IS_MAC else '',
            f'{HOME}/.config/Qoder' if IS_LINUX else '',
        ],
        'config_paths': [],
    },
    'kimi_code': {
        'name': 'Kimi Code (Moonshot)',
        'instruction_files': ['KIMI.md', '.kimi/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/.kimi/sessions/*/*.jsonl', f'{HOME}/.kimi/history/*'],
            'Linux': [f'{HOME}/.kimi/sessions/*/*.jsonl', f'{HOME}/.kimi/history/*'],
            'Windows': [f'{HOME}/.kimi/sessions/*/*.jsonl'],
        },
        'log_format': 'jsonl',
        'detect_files': [f'{HOME}/.kimi'],
        'config_paths': [f'{HOME}/.kimi/config.json'],
    },
    'marscode': {
        'name': 'MarsCode (ByteDance)',
        'instruction_files': ['.marscode/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/MarsCode/User/workspaceStorage/*/state.vscdb'],
            'Linux': [f'{HOME}/.config/MarsCode/User/workspaceStorage/*/state.vscdb'],
            'Windows': [f'{APPDATA}/MarsCode/User/workspaceStorage/*/state.vscdb'],
        },
        'log_format': 'sqlite',
        'detect_files': [
            f'{HOME}/Library/Application Support/MarsCode' if IS_MAC else '',
            f'{HOME}/.config/MarsCode' if IS_LINUX else '',
        ],
        'config_paths': [],
    },
    'tongyi_lingma': {
        'name': 'Tongyi Lingma (Alibaba)',
        'instruction_files': ['.lingma/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/alibaba-cloud.tongyi-lingma/*'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/alibaba-cloud.tongyi-lingma/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/alibaba-cloud.tongyi-lingma/*'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/Library/Application Support/Code/User/globalStorage/alibaba-cloud.tongyi-lingma' if IS_MAC else '',
            f'{HOME}/.config/Code/User/globalStorage/alibaba-cloud.tongyi-lingma' if IS_LINUX else '',
        ],
        'config_paths': [],
    },
    'baidu_comate': {
        'name': 'Baidu Comate',
        'instruction_files': ['.comate/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/baidu.comate/*'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/baidu.comate/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/baidu.comate/*'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/Library/Application Support/Code/User/globalStorage/baidu.comate' if IS_MAC else '',
        ],
        'config_paths': [],
    },
    'codegeex': {
        'name': 'CodeGeeX (Zhipu/Z.AI)',
        'instruction_files': ['.codegeex/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/aminer.codegeex/*'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/aminer.codegeex/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/aminer.codegeex/*'],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/Library/Application Support/Code/User/globalStorage/aminer.codegeex' if IS_MAC else '',
        ],
        'config_paths': [],
    },
    'devchat': {
        'name': 'DevChat',
        'instruction_files': ['.devchat/config.yml'],
        'log_paths': {
            'Darwin': [f'{HOME}/.devchat/history/*'],
            'Linux': [f'{HOME}/.devchat/history/*'],
            'Windows': [f'{HOME}/.devchat/history/*'],
        },
        'log_format': 'json',
        'detect_files': [f'{HOME}/.devchat'],
        'config_paths': [f'{HOME}/.devchat/config.yml'],
    },
    'minimax': {
        'name': 'MiniMax Code',
        'instruction_files': ['.minimax/rules'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/Code/User/globalStorage/ezeoli88.minmax-vscode/*'],
            'Linux': [f'{HOME}/.config/Code/User/globalStorage/ezeoli88.minmax-vscode/*'],
            'Windows': [f'{APPDATA}/Code/User/globalStorage/ezeoli88.minmax-vscode/*'],
        },
        'log_format': 'json',
        'detect_files': [],
        'config_paths': [],
    },
}


def detect_installed_tools():
    """Detect which AI coding tools are installed on this machine."""
    plat = platform.system()
    found = []

    for tool_id, tool in TOOLS.items():
        detected = False
        reason = ''

        # Check detect_files
        for path in tool['detect_files']:
            if path and os.path.exists(path):
                detected = True
                reason = f'Found {path}'
                break

        # Check config_paths
        if not detected:
            for path in tool['config_paths']:
                if path and os.path.exists(path):
                    detected = True
                    reason = f'Found config {path}'
                    break

        # Check if any logs exist
        if not detected:
            log_patterns = tool.get('log_paths', {}).get(plat, [])
            for pattern in log_patterns:
                # Use shallow glob (no recursive ** for speed)
                if '**' not in pattern:
                    matches = glob.glob(pattern)
                    if matches:
                        detected = True
                        reason = f'Found {len(matches)} log files'
                        break

        if detected:
            # Count log files
            log_count = 0
            log_patterns = tool.get('log_paths', {}).get(plat, [])
            for pattern in log_patterns:
                if '**' not in pattern:
                    log_count += len(glob.glob(pattern))

            found.append({
                'id': tool_id,
                'name': tool['name'],
                'reason': reason,
                'log_format': tool['log_format'],
                'log_count': log_count,
                'instruction_files': tool['instruction_files'],
            })

    return found


def find_instruction_file(project_dir=None):
    """Find instruction/system prompt file in project or cwd."""
    search_dirs = []
    if project_dir:
        search_dirs.append(project_dir)
    search_dirs.append(os.getcwd())

    for d in search_dirs:
        for tool_id, tool in TOOLS.items():
            for fname in tool['instruction_files']:
                fpath = os.path.join(d, fname)
                if os.path.exists(fpath):
                    return {
                        'tool': tool_id,
                        'tool_name': tool['name'],
                        'file': fpath,
                        'filename': fname,
                    }
    return None


def scan_project_for_tool(project_dir):
    """Scan a project directory to detect which AI tool is being used."""
    if not os.path.isdir(project_dir):
        return None

    # Check for instruction files
    result = find_instruction_file(project_dir)
    if result:
        return result

    # Check for hidden config dirs
    for tool_id, tool in TOOLS.items():
        for fname in tool['instruction_files']:
            # Check if it's a directory-based config
            fpath = os.path.join(project_dir, fname)
            if os.path.exists(fpath):
                return {
                    'tool': tool_id,
                    'tool_name': tool['name'],
                    'file': fpath,
                    'filename': fname,
                }

    return None


def get_log_paths(tool_id):
    """Get log file paths for a detected tool."""
    plat = platform.system()
    tool = TOOLS.get(tool_id)
    if not tool:
        return []

    patterns = tool.get('log_paths', {}).get(plat, [])
    all_logs = []
    for pattern in patterns:
        if '**' not in pattern:
            all_logs.extend(glob.glob(pattern))

    # Sort by modification time, newest first
    all_logs.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return all_logs


def detect_remote_session():
    """Detect if running via SSH (iPad/mobile user connecting to remote machine)."""
    ssh_indicators = [
        os.environ.get('SSH_CLIENT'),
        os.environ.get('SSH_TTY'),
        os.environ.get('SSH_CONNECTION'),
    ]
    is_ssh = any(ssh_indicators)

    # Check for known mobile terminal apps
    term_program = os.environ.get('TERM_PROGRAM', '').lower()
    lc_terminal = os.environ.get('LC_TERMINAL', '').lower()
    mobile_terms = ['moshi', 'termius', 'blink', 'ish', 'a-shell', 'termly', 'happy']
    is_mobile = any(m in term_program or m in lc_terminal for m in mobile_terms)

    return {
        'is_ssh': is_ssh,
        'is_mobile_terminal': is_mobile,
        'note': 'Running via SSH — logs are on this machine, not your device' if is_ssh else None,
    }


def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None

    # 1. Detect installed tools
    installed = detect_installed_tools()

    # 2. If project dir given, detect which tool that project uses
    project_tool = None
    if project_dir:
        project_tool = scan_project_for_tool(project_dir)

    # 3. Check cwd for instruction files
    cwd_tool = find_instruction_file()

    # 4. Detect remote/mobile session
    remote = detect_remote_session()

    result = {
        'platform': platform.system(),
        'remote_session': remote,
        'installed_tools': installed,
        'project_tool': project_tool,
        'cwd_tool': cwd_tool,
        'primary_tool': None,
        'primary_log_format': None,
        'log_count': 0,
        'instruction_file': None,
        'needs_manual_input': False,
        'is_always_on': False,
    }

    # Determine primary tool
    if project_tool:
        result['primary_tool'] = project_tool['tool']
        result['instruction_file'] = project_tool['file']
    elif cwd_tool:
        result['primary_tool'] = cwd_tool['tool']
        result['instruction_file'] = cwd_tool['file']
    elif installed:
        # Pick the one with most logs
        best = max(installed, key=lambda t: t['log_count'])
        result['primary_tool'] = best['id']
    else:
        result['needs_manual_input'] = True

    if result['primary_tool']:
        tool = TOOLS[result['primary_tool']]
        result['primary_log_format'] = tool['log_format']
        logs = get_log_paths(result['primary_tool'])
        result['log_count'] = len(logs)
        result['primary_tool_name'] = tool['name']
        result['is_always_on'] = tool.get('always_on', False)

        # Check if we can actually parse their logs
        if tool['log_format'] in ('jsonl', 'json'):
            result['can_analyze'] = True
        elif tool['log_format'] == 'sqlite':
            result['can_analyze'] = True
            result['note'] = 'SQLite format — will query database directly'
        elif tool['log_format'] == 'markdown':
            result['can_analyze'] = False
            result['note'] = 'Markdown chat logs — limited analysis (no token counts)'
        else:
            result['can_analyze'] = False
            result['note'] = 'Unknown log format — may need manual inspection'

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
