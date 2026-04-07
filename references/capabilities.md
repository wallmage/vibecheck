# Capability Matrix

Use this file when deciding whether to run a full scan or switch to instruction-only mode.

## Support levels

- `full`: detect tool, locate logs, run data-driven analysis, generate lessons and reports
- `instruction_only`: detect tool and optimize the instruction file, but do not promise a real session-cost scan
- `manual_only`: detection is weak and the user may need to point you at the project or instruction file directly

## Current matrix

| Tool family | Detection | Full session analysis | Instruction optimization | Notes |
|---|---|---|---|---|
| Claude Code | Yes | Yes | Yes | Primary supported scan path |
| Codex | Yes | Yes | Yes | Uses Codex session JSONL plus per-step token telemetry |
| OpenClaw / always-on agents | Yes | Yes | Yes | Uses OpenClaw per-agent `sessions.json` plus transcript JSONL to measure always-on waste patterns |
| Cursor | Yes | Yes | Yes | Uses workspace/global SQLite state plus estimated token cost when Cursor does not store token counters |
| GitHub Copilot / VS Code chats | Yes | Yes | Yes | Uses local or exported VS Code `chatSessions` JSON / JSONL plus empty-window chat session files |
| Windsurf | Yes | Yes | Yes | Uses official Windsurf transcript JSONL plus compatibility support for older local cache paths |
| TRAE | Yes | Yes | Yes | Uses TRAE `workspaceStorage/*/state.vscdb` chat state under the current `memento/icube-ai-ng-chat-storage*` keys |
| Qoder | Yes | Yes | Yes | Uses Qoder `workspaceStorage/*/state.vscdb` with broad `ItemTable` extraction for current chat, session, quest, and agent payloads |
| CodeBuddy | Yes | Yes | Yes | Uses CodeBuddy session index SQLite plus runtime `codebuddy.log` reconstruction for model, prompt, completion, and failure signals |
| WorkBuddy | Yes | Yes | Yes | Uses WorkBuddy session index SQLite plus runtime logs, with auxiliary VS Code-style workspace state under `User/workspaceStorage` |
| Google Antigravity | Yes | Yes | Yes | Uses readable Antigravity `brain/<conversation-id>/` artifacts and metadata; raw `.pb` conversations are encrypted and not the supported parse surface |
| Cline / Roo Code | Yes | Not yet | Yes | Use the detected rules file and general heuristics |
| Gemini CLI / Copilot / OpenCode / Aider | Partial to yes | Not yet | Yes | Education + instruction-file optimization still help |
| Other detected tools in `detect_tool.py` | Usually yes | Not yet | Usually yes | Keep wording honest and avoid fake precision |

## 2026 full-support targets

Use [support-priority-2026-04.md](/Users/wallny/Developer/vibecheck/references/support-priority-2026-04.md) as the current roadmap for which tool families should receive full session-analysis support next.

Current top-10 target families:

1. GitHub Copilot
2. Cursor
3. Claude Code
4. OpenClaw
5. Google Antigravity
6. VS Code Agent Mode
7. OpenAI Codex
8. Windsurf
9. TRAE
10. Qoder / CodeBuddy / WorkBuddy

## What to say when full analysis is unsupported

Use a short explanation:

"I found your tool and your instruction file, but this version of vibecheck does not yet support a reliable token-cost scan for that log format. I can still optimize your instruction file, teach the main waste patterns, and use typical ranges instead of invented session numbers."

## Do not do this

- Do not detect Cursor/Codex and then run `find_claude_logs.py` as if those logs were supported.
- Do not imply that unsupported tools have broken logs. The limitation is our parser coverage, not user error.
- Do not fabricate dollar amounts for unsupported tools and present them as measured facts.
