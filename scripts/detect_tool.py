#!/usr/bin/env python3
"""Auto-detect which AI coding tool the user has and what vibecheck can do with it.

Detection coverage is broad, but full session-cost analysis is intentionally narrower.
When a tool's logs are not supported by the current analyzer, the caller should switch
to instruction-file optimization and cost education instead of pretending a scan works.
"""
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
#   config_paths: where config lives (for detection / settings optimization)
#   global_instruction_paths: machine-wide instruction files worth preferring over
#     per-project instruction edits when the tool supports them
#   detect_files: files/dirs whose existence confirms this tool
# }

HOME = str(Path.home())
IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

APPDATA = os.environ.get('APPDATA', '')
LOCAL_APPDATA = os.environ.get('LOCALAPPDATA', '')
COPILOT_HOME = os.environ.get('COPILOT_HOME', f'{HOME}/.copilot')
DOCUMENTS_HOME = os.path.join(HOME, 'Documents')

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
        'global_instruction_paths': [f'{HOME}/.claude/CLAUDE.md'],
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
        'config_paths': [f'{HOME}/.codex/config.json', f'{HOME}/.codex/config.yaml', f'{HOME}/.codex/config.toml'],
        'global_instruction_paths': [f'{HOME}/.codex/AGENTS.md'],
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
        'config_paths': [
            f'{HOME}/Library/Application Support/Cursor/User/settings.json' if IS_MAC else '',
            f'{HOME}/.config/Cursor/User/settings.json' if IS_LINUX else '',
            f'{APPDATA}/Cursor/User/settings.json' if IS_WIN else '',
        ],
        'global_settings_status': 'inferred',
        'global_settings_note': 'Official docs confirm global User Rules live in Cursor Settings, but do not publish a file path. settings.json locations are inferred from Cursor’s VS Code-style app layout.',
    },
    'windsurf': {
        'name': 'Windsurf (Codeium)',
        'instruction_files': ['.windsurf/rules', '.windsurfrules'],
        'log_paths': {
            'Darwin': [f'{HOME}/.windsurf/transcripts/*.jsonl', f'{HOME}/.codeium/windsurf/cascade/*'],
            'Linux': [f'{HOME}/.windsurf/transcripts/*.jsonl', f'{HOME}/.codeium/windsurf/cascade/*'],
            'Windows': [f'{HOME}/.windsurf/transcripts/*.jsonl', f'{HOME}/.codeium/windsurf/cascade/*'],
        },
        'log_format': 'json',
        'detect_files': [f'{HOME}/.windsurf', f'{HOME}/.codeium/windsurf'],
        'config_paths': [],
        'global_instruction_paths': [f'{HOME}/.codeium/windsurf/memories/global_rules.md'],
        'global_settings_status': 'verified',
        'global_settings_note': 'Official Windsurf docs publish ~/.codeium/windsurf/memories/global_rules.md as the global Rules file, with workspace rules under .windsurf/rules/*.md and AGENTS.md support inside workspaces.',
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
        'global_instruction_paths': [
            os.path.join(DOCUMENTS_HOME, 'Cline', 'Rules'),
            f'{HOME}/Cline/Rules' if IS_LINUX else '',
        ],
        'global_settings_status': 'verified',
        'global_settings_note': 'Official Cline docs publish the global Rules directory in Documents/Cline/Rules, with ~/Cline/Rules as a Linux fallback.',
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'Roo Code docs were found, but an official on-disk path for global rule storage was not clearly documented.',
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
        'global_settings_status': 'verified',
        'global_settings_note': 'Official aider docs state .aider.conf.yml is loaded from the home directory, repo root, and current directory, in that order.',
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
        'global_instruction_paths': [f'{HOME}/.gemini/GEMINI.md'],
    },
    'antigravity': {
        'name': 'Google Antigravity',
        'instruction_files': ['AGENTS.md', 'GEMINI.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/.gemini/antigravity/brain/*/*.metadata.json'],
            'Linux': [f'{HOME}/.gemini/antigravity/brain/*/*.metadata.json'],
            'Windows': [f'{HOME}/.gemini/antigravity/brain/*/*.metadata.json'],
        },
        'log_format': 'markdown',
        'detect_files': [f'{HOME}/.gemini/antigravity'],
        'config_paths': [f'{HOME}/.gemini/antigravity/mcp_config.json'],
        'global_instruction_paths': [f'{HOME}/.gemini/antigravity/AGENTS.md'],
    },
    'github_copilot': {
        'name': 'GitHub Copilot / VS Code',
        'instruction_files': ['.github/copilot-instructions.md'],
        'log_paths': {
            'Darwin': [
                f'{HOME}/Library/Application Support/Code/User/workspaceStorage/*/chatSessions/*.json',
                f'{HOME}/Library/Application Support/Code/User/workspaceStorage/*/chatSessions/*.jsonl',
                f'{HOME}/Library/Application Support/Code/User/globalStorage/emptyWindowChatSessions/*.json',
                f'{HOME}/Library/Application Support/Code/User/globalStorage/emptyWindowChatSessions/*.jsonl',
                f'{HOME}/Library/Application Support/Code - Insiders/User/workspaceStorage/*/chatSessions/*.json',
                f'{HOME}/Library/Application Support/Code - Insiders/User/workspaceStorage/*/chatSessions/*.jsonl',
                f'{HOME}/Library/Application Support/Code - Insiders/User/globalStorage/emptyWindowChatSessions/*.json',
                f'{HOME}/Library/Application Support/Code - Insiders/User/globalStorage/emptyWindowChatSessions/*.jsonl',
            ],
            'Linux': [
                f'{HOME}/.config/Code/User/workspaceStorage/*/chatSessions/*.json',
                f'{HOME}/.config/Code/User/workspaceStorage/*/chatSessions/*.jsonl',
                f'{HOME}/.config/Code/User/globalStorage/emptyWindowChatSessions/*.json',
                f'{HOME}/.config/Code/User/globalStorage/emptyWindowChatSessions/*.jsonl',
                f'{HOME}/.config/Code - Insiders/User/workspaceStorage/*/chatSessions/*.json',
                f'{HOME}/.config/Code - Insiders/User/workspaceStorage/*/chatSessions/*.jsonl',
                f'{HOME}/.config/Code - Insiders/User/globalStorage/emptyWindowChatSessions/*.json',
                f'{HOME}/.config/Code - Insiders/User/globalStorage/emptyWindowChatSessions/*.jsonl',
            ],
            'Windows': [
                f'{APPDATA}/Code/User/workspaceStorage/*/chatSessions/*.json',
                f'{APPDATA}/Code/User/workspaceStorage/*/chatSessions/*.jsonl',
                f'{APPDATA}/Code/User/globalStorage/emptyWindowChatSessions/*.json',
                f'{APPDATA}/Code/User/globalStorage/emptyWindowChatSessions/*.jsonl',
                f'{APPDATA}/Code - Insiders/User/workspaceStorage/*/chatSessions/*.json',
                f'{APPDATA}/Code - Insiders/User/workspaceStorage/*/chatSessions/*.jsonl',
                f'{APPDATA}/Code - Insiders/User/globalStorage/emptyWindowChatSessions/*.json',
                f'{APPDATA}/Code - Insiders/User/globalStorage/emptyWindowChatSessions/*.jsonl',
            ],
        },
        'log_format': 'json',
        'detect_files': [
            f'{HOME}/Library/Application Support/Code/User/globalStorage/github.copilot-chat' if IS_MAC else '',
            f'{HOME}/Library/Application Support/Code/User' if IS_MAC else '',
            f'{HOME}/Library/Application Support/Code - Insiders/User' if IS_MAC else '',
            f'{HOME}/.config/Code/User/globalStorage/github.copilot-chat' if IS_LINUX else '',
            f'{HOME}/.config/Code/User' if IS_LINUX else '',
            f'{HOME}/.config/Code - Insiders/User' if IS_LINUX else '',
            f'{APPDATA}/Code/User' if IS_WIN else '',
            f'{APPDATA}/Code - Insiders/User' if IS_WIN else '',
        ],
        'config_paths': [
            f'{COPILOT_HOME}/config.json',
            f'{COPILOT_HOME}/mcp-config.json',
            f'{COPILOT_HOME}/permissions-config.json',
        ],
        'global_instruction_paths': [f'{COPILOT_HOME}/copilot-instructions.md'],
        'global_settings_status': 'verified',
        'global_settings_note': 'Official GitHub Copilot CLI docs publish $HOME/.copilot/copilot-instructions.md and the configurable COPILOT_HOME config directory.',
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
        'global_instruction_paths': [f'{HOME}/.config/opencode/OPENCODE.md'],
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
        'instruction_files': ['augment-guidelines.md', '.augment-guidelines', '.augment/rules'],
        'log_paths': {},
        'log_format': 'unknown',
        'detect_files': [],
        'config_paths': [],
        'global_instruction_paths': [f'{HOME}/.augment/rules'],
        'global_settings_status': 'verified',
        'global_settings_note': 'Official Augment docs publish ~/.augment/rules/ for user rules, <workspace>/.augment/rules/ for workspace rules, and local IDE-stored User Guidelines that do not have a documented portable file path.',
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
        'global_instruction_paths': [f'{HOME}/.openclaw/AGENTS.md'],
        'always_on': True,  # 24/7 agent — different waste profile
    },
    'codebuddy': {
        'name': 'CodeBuddy (Tencent)',
        'instruction_files': ['CODEBUDDY.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/CodeBuddy/codebuddy-sessions.vscdb', f'{HOME}/.codebuddy/projects/*/*.jsonl'],
            'Linux': [f'{HOME}/.config/CodeBuddy/codebuddy-sessions.vscdb', f'{HOME}/.codebuddy/projects/*/*.jsonl'],
            'Windows': [f'{APPDATA}/CodeBuddy/codebuddy-sessions.vscdb', f'{HOME}/.codebuddy/projects/*/*.jsonl'],
        },
        'log_format': 'sqlite',
        'detect_files': [f'{HOME}/.codebuddy', f'{HOME}/Library/Application Support/CodeBuddy' if IS_MAC else '', f'{HOME}/.config/CodeBuddy' if IS_LINUX else '', f'{APPDATA}/CodeBuddy' if IS_WIN else ''],
        'config_paths': [],
        'global_instruction_paths': [f'{HOME}/.codebuddy/CODEBUDDY.md'],
    },
    'workbuddy': {
        'name': 'WorkBuddy (Tencent)',
        'instruction_files': ['WORKBUDDY.md'],
        'log_paths': {
            'Darwin': [f'{HOME}/Library/Application Support/WorkBuddy/codebuddy-sessions.vscdb', f'{HOME}/Library/Application Support/WorkBuddy/User/workspaceStorage/*/state.vscdb'],
            'Linux': [f'{HOME}/.config/WorkBuddy/codebuddy-sessions.vscdb'],
            'Windows': [f'{APPDATA}/WorkBuddy/codebuddy-sessions.vscdb'],
        },
        'log_format': 'sqlite',
        'detect_files': [f'{HOME}/.workbuddy', f'{HOME}/Library/Application Support/WorkBuddy' if IS_MAC else '', f'{HOME}/.config/WorkBuddy' if IS_LINUX else '', f'{APPDATA}/WorkBuddy' if IS_WIN else ''],
        'config_paths': [],
        'global_instruction_paths': [f'{HOME}/.workbuddy/WORKBUDDY.md'],
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
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
        'global_instruction_paths': [f'{HOME}/.kimi/KIMI.md'],
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
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
        'global_settings_status': 'verified',
        'global_settings_note': 'The global DevChat settings file is ~/.devchat/config.yml in the local install layout.',
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
        'global_settings_status': 'unknown',
        'global_settings_note': 'No official global rule storage path has been verified yet.',
    },
}

# Current analyzer support is intentionally strict.
# The bundled analyzer understands Claude-style JSONL session logs. Other tools may be
# detectable and may have instruction files worth optimizing, but they should not be
# routed into the full scan flow unless their log schema is explicitly supported here.
ANALYSIS_SUPPORT = {
    'claude_code': {
        'can_analyze': True,
        'analysis_mode': 'claude_jsonl',
        'support_level': 'full',
        'note': 'Full session-cost analysis is available for Claude Code JSONL logs.',
    },
    'codex': {
        'can_analyze': True,
        'analysis_mode': 'codex_jsonl',
        'support_level': 'full',
        'note': 'Full session-cost analysis is available for Codex session JSONL logs.',
    },
    'cursor': {
        'can_analyze': True,
        'analysis_mode': 'cursor_sqlite',
        'support_level': 'full',
        'note': 'Full session analysis is available for Cursor workspace SQLite data, with token-cost estimation when local token counters are missing.',
    },
    'windsurf': {
        'can_analyze': True,
        'analysis_mode': 'windsurf_transcript',
        'support_level': 'full',
        'note': 'Full session analysis is available for Windsurf transcript JSONL files, with compatibility support for older local cache paths.',
    },
    'github_copilot': {
        'can_analyze': True,
        'analysis_mode': 'copilot_chat_json',
        'support_level': 'full',
        'note': 'Full session analysis is available for local or exported VS Code Copilot chat sessions stored as JSON or JSONL.',
    },
    'trae': {
        'can_analyze': True,
        'analysis_mode': 'trae_sqlite',
        'support_level': 'full',
        'note': 'Full session analysis is available for TRAE workspace SQLite data using the current chat storage keys under ItemTable.',
    },
    'qoder': {
        'can_analyze': True,
        'analysis_mode': 'qoder_sqlite',
        'support_level': 'full',
        'note': 'Full session analysis is available for Qoder workspace SQLite data using broad chat/session extraction from ItemTable and current workspace storage state.',
    },
    'antigravity': {
        'can_analyze': True,
        'analysis_mode': 'antigravity_brain',
        'support_level': 'full',
        'note': 'Full session analysis is available for Antigravity brain artifacts and metadata, using the readable task/plan/walkthrough exports that accompany encrypted raw conversations.',
    },
    'codebuddy': {
        'can_analyze': True,
        'analysis_mode': 'codebuddy_hybrid',
        'support_level': 'full',
        'note': 'Full session analysis is available for CodeBuddy session index SQLite plus runtime logs, with hybrid reconstruction when direct chat payloads are not exposed.',
    },
    'workbuddy': {
        'can_analyze': True,
        'analysis_mode': 'workbuddy_hybrid',
        'support_level': 'full',
        'note': 'Full session analysis is available for WorkBuddy session index SQLite plus runtime logs, with hybrid reconstruction when direct chat payloads are not exposed.',
    },
    'openclaw': {
        'can_analyze': True,
        'analysis_mode': 'openclaw_jsonl',
        'support_level': 'full',
        'note': 'Full session analysis is available for OpenClaw transcript JSONL plus per-agent session metadata, including always-on waste patterns.',
    },
}

DEFAULT_SUPPORT = {
    'can_analyze': False,
    'analysis_mode': 'instruction_only',
    'support_level': 'limited',
    'note': 'Tool detected, but this version of vibecheck does not yet support a reliable session-cost scan for this log format.',
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
            support = get_support(tool_id)
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
                'can_analyze': support['can_analyze'],
                'analysis_mode': support['analysis_mode'],
                'support_level': support['support_level'],
                'support_note': support['note'],
                'always_on': tool.get('always_on', False),
                'global_settings_status': tool.get(
                    'global_settings_status',
                    'verified' if tool.get('global_instruction_paths') else 'unknown',
                ),
                'global_settings_note': tool.get('global_settings_note'),
                'known_global_instruction_paths': [
                    path for path in tool.get('global_instruction_paths', []) if path
                ],
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


def find_instruction_targets(project_dir=None):
    """Find all instruction files for all tools in project_dir and cwd."""
    search_dirs = []
    if project_dir:
        search_dirs.append(os.path.abspath(project_dir))
    search_dirs.append(os.path.abspath(os.getcwd()))

    seen = set()
    targets = []

    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for tool_id, tool in TOOLS.items():
            for fname in tool['instruction_files']:
                fpath = os.path.join(d, fname)
                if os.path.exists(fpath):
                    real = os.path.realpath(fpath)
                    if real in seen:
                        continue
                    seen.add(real)
                    targets.append({
                        'tool': tool_id,
                        'tool_name': tool['name'],
                        'file': fpath,
                        'filename': fname,
                        'search_dir': d,
                    })

    targets.sort(key=lambda item: (item['tool_name'].lower(), item['filename'].lower(), item['file']))
    return targets


def find_global_instruction_targets(installed_tools=None):
    """Find machine-wide instruction targets for detected tools.

    Only existing machine-wide instruction files/directories are returned. We never
    create missing instruction surfaces for the user.
    """
    installed_ids = None
    if installed_tools is not None:
        installed_ids = {tool['id'] for tool in installed_tools}

    targets = []
    seen = set()
    for tool_id, tool in TOOLS.items():
        if installed_ids is not None and tool_id not in installed_ids:
            continue
        for idx, path in enumerate(tool.get('global_instruction_paths', [])):
            if not path:
                continue
            if not os.path.exists(path):
                continue
            key = os.path.realpath(path)
            if key in seen:
                continue
            seen.add(key)
            targets.append({
                'tool': tool_id,
                'tool_name': tool['name'],
                'file': path,
                'filename': os.path.basename(path),
                'kind': 'instruction_file',
                'scope': 'global',
                'exists': True,
                'action': 'update',
                'priority_band': 'primary' if idx == 0 else 'secondary',
                'source': 'global_instruction',
            })

    targets.sort(key=lambda item: (item['tool_name'].lower(), item['priority_band'], item['filename'].lower(), item['file']))
    return targets


def find_config_targets(installed_tools=None):
    """Find readable config/settings files for detected tools across the machine."""
    installed_ids = None
    if installed_tools is not None:
        installed_ids = {tool['id'] for tool in installed_tools}

    seen = set()
    targets = []
    for tool_id, tool in TOOLS.items():
        if installed_ids is not None and tool_id not in installed_ids:
            continue
        for path in tool.get('config_paths', []):
            if not path or not os.path.exists(path):
                continue
            real = os.path.realpath(path)
            if real in seen:
                continue
            seen.add(real)
            targets.append({
                'tool': tool_id,
                'tool_name': tool['name'],
                'file': path,
                'filename': os.path.basename(path),
                'kind': 'config_path',
                'scope': 'global',
                'exists': True,
                'action': 'update',
                'priority_band': 'secondary',
                'source': 'config',
            })

    targets.sort(key=lambda item: (item['tool_name'].lower(), item['filename'].lower(), item['file']))
    return targets


def find_optimization_targets(project_dir=None, installed_tools=None):
    """Find both project instruction files and machine-wide tool settings worth optimizing."""
    instruction_targets = []
    for target in find_instruction_targets(project_dir):
        item = dict(target)
        item['kind'] = 'instruction_file'
        item['scope'] = 'project'
        item['exists'] = True
        item['action'] = 'update'
        item['priority_band'] = 'primary'
        item['source'] = 'project_instruction'
        instruction_targets.append(item)

    global_instruction_targets = find_global_instruction_targets(installed_tools)
    config_targets = find_config_targets(installed_tools)

    tools_with_global_primary = {
        target['tool']
        for target in global_instruction_targets
        if target.get('priority_band') == 'primary'
    }
    for item in instruction_targets:
        if item.get('tool') in tools_with_global_primary:
            item['priority_band'] = 'fallback'

    seen = set()
    targets = []
    for target in global_instruction_targets + config_targets + instruction_targets:
        key = os.path.realpath(target['file']) if os.path.exists(target['file']) else target['file']
        if key in seen:
            continue
        seen.add(key)
        targets.append(target)

    priority_order = {'primary': 0, 'secondary': 1, 'fallback': 2}
    scope_order = {'global': 0, 'project': 1}
    kind_order = {'instruction_file': 0, 'config_path': 1}
    targets.sort(
        key=lambda item: (
            item['tool_name'].lower(),
            priority_order.get(item.get('priority_band'), 9),
            scope_order.get(item.get('scope'), 9),
            kind_order.get(item.get('kind'), 9),
            item['filename'].lower(),
            item['file'],
        )
    )
    return targets


def scan_project_for_tool(project_dir):
    """Scan a project directory to detect which AI tool is being used."""
    if not os.path.isdir(project_dir):
        return None

    candidates = []
    for tool_id, tool in TOOLS.items():
        matches = []
        for fname in tool['instruction_files']:
            fpath = os.path.join(project_dir, fname)
            if os.path.exists(fpath):
                matches.append((fname, fpath))

        if matches:
            candidates.append({
                'tool': tool_id,
                'tool_name': tool['name'],
                'matches': matches,
                'score': len(matches),
            })

    if not candidates:
        return None

    best = sorted(candidates, key=lambda c: (-c['score'], c['tool']))[0]
    filename, fpath = best['matches'][0]
    return {
        'tool': best['tool'],
        'tool_name': best['tool_name'],
        'file': fpath,
        'filename': filename,
    }


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


def get_support(tool_id):
    """Return the supported vibecheck capability level for a tool."""
    return ANALYSIS_SUPPORT.get(tool_id, DEFAULT_SUPPORT).copy()


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
        'analyzable_tools': [tool for tool in installed if tool.get('can_analyze')],
        'global_instruction_targets': find_global_instruction_targets(installed),
        'project_tool': project_tool,
        'cwd_tool': cwd_tool,
        'instruction_targets': find_instruction_targets(project_dir),
        'optimization_targets': find_optimization_targets(project_dir, installed),
        'primary_tool': None,
        'primary_log_format': None,
        'log_count': 0,
        'instruction_file': None,
        'needs_manual_input': False,
        'is_always_on': False,
        'supports_instruction_optimization': False,
        'analysis_mode': DEFAULT_SUPPORT['analysis_mode'],
        'support_level': DEFAULT_SUPPORT['support_level'],
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
        support = get_support(result['primary_tool'])
        result['primary_log_format'] = tool['log_format']
        logs = get_log_paths(result['primary_tool'])
        result['log_count'] = len(logs)
        result['primary_tool_name'] = tool['name']
        result['is_always_on'] = tool.get('always_on', False)
        result['supports_instruction_optimization'] = bool(tool['instruction_files'])
        result['can_analyze'] = support['can_analyze']
        result['analysis_mode'] = support['analysis_mode']
        result['support_level'] = support['support_level']
        result['note'] = support['note']

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
