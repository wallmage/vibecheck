# vibecheck

Vibe coding is fun. Vibe coding is expensive. Let's check.

Works with any AI coding tool. Auto-detects yours, explains your bill in plain language, cuts waste by 30-50%.

## Supported tools (auto-detected)

| Tool | Instruction file | Status |
|------|-----------------|--------|
| **Claude Code** | CLAUDE.md | Full analysis |
| **OpenClaw** | SOUL.md | Full analysis (24/7) |
| **CodeBuddy** (Tencent) | CODEBUDDY.md | Full analysis |
| **Kimi Code** (Moonshot) | KIMI.md | Full analysis |
| Codex CLI (OpenAI) | AGENTS.md | Detection + education |
| Cursor | .cursorrules | Detection + education |
| Windsurf | .windsurfrules | Detection + education |
| Cline | .clinerules | Detection + education |
| Roo Code | .roo/rules | Detection + education |
| Kilo Code | .kilo/rules | Detection + education |
| Aider | .aider.conf.yml | Detection + education |
| Gemini CLI | GEMINI.md | Detection + education |
| GitHub Copilot | copilot-instructions.md | Detection + education |
| OpenCode | OPENCODE.md | Detection + education |
| Augment Code | augment-guidelines.md | Detection + education |
| **TRAE** (ByteDance) | .trae/rules | Detection + education |
| **Qoder** (Alibaba) | .qoder/rules | Detection + education |
| **MarsCode** (ByteDance) | .marscode/rules | Detection + education |
| **Tongyi Lingma** (Alibaba) | .lingma/rules | Detection + education |
| **Baidu Comate** | .comate/rules | Detection + education |
| **CodeGeeX** (Zhipu/Z.AI) | .codegeex/rules | Detection + education |
| **WorkBuddy** (Tencent) | WORKBUDDY.md | Detection + education |
| **DevChat** | .devchat/config.yml | Detection + education |
| **MiniMax Code** | .minimax/rules | Detection + education |

Can't auto-detect? Just point it at your project folder.

Works from iPad/mobile via SSH (Moshi, Termius, Blink, etc.) — logs are on the remote machine.

## Install

### Claude Code (CLI) — recommended

```bash
claude install-skill https://github.com/wallmage/vibecheck
```

Then in any conversation:
```
/vibecheck scan
```

This gives you full analysis with your real session data — the CLI can read your logs directly.

### Claude Desktop / Cowork

Same install command, but Cowork runs in a sandbox that can't access `~/.claude/` (hidden directory where logs live). vibecheck handles this gracefully — it'll teach you the concepts using industry averages instead of your personal data. Still useful, just not personalized.

For the full data-driven experience, run `/vibecheck scan` from the CLI.

### Any other AI coding tool

Tell your AI:

> Install the vibecheck skill from https://github.com/wallmage/vibecheck and run /vibecheck scan

It works. The AI reads the SKILL.md and knows what to do.

## Commands

- `/vibecheck` or `/vibecheck scan` — Interactive education + full diagnostic + fixes
- `/vibecheck explain` — Just the education (understand your bill, no changes)
- `/vibecheck compress` — Compress instruction file (25-50% smaller)
- `/vibecheck monitor` — Week-over-week comparison with alerts

## How it works

Most people don't know what they're paying for. A $20/month subscription can give you $200+ of actual AI usage. But where does it go?

vibecheck starts with an interactive lesson — using YOUR real data — that explains it piece by piece:
1. What are tokens? (Hint: roughly one word)
2. Why does the AI re-read your entire conversation every message?
3. Where is YOUR money going? (Spoiler: 50-65% is re-reading old messages)

Then it finds your waste patterns and fixes them with one paragraph in your instruction file. Same work, fewer wasted messages.

## Before / After

vibecheck tracks your progress. First run shows projections, subsequent runs show actual savings:

```
                              BEFORE         NOW            CHANGE
  Avg turns/session           36.8           25.9           -10.9 ✅
  Avg sub-agents/session      3.2            2.9            -0.3 ✅
  Avg context window          128.4K         89.9K          -30% ✅
  Wasteful turns              36.7%          8.1%           -28.6% ✅

  Avg cost/session            $2.62          $1.35          -$1.27 ✅
  Monthly spend               $224           $115           -$109 ✅
```

Snapshots saved locally in `~/.vibecheck/snapshots/`. Survives reboots. History grows over time.

## The 15 waste patterns

**Tier 1 — The Big 3 (70-80% of waste)**
1. Idle narration — AI says "Now I'll…" before doing it
2. Context rot — Conversations that run too long without clearing
3. Ping-pong debugging — Fix, break, fix, break cycles

**Tier 2 — The Mechanics (15-20%)**
4. Verbose output — Build logs flooding the conversation
5. Unchained commands — Running commands one at a time
6. Codebase wandering — Reading 8 files before editing 1
7. Unbatched edits — One edit per message instead of many

**Tier 3 — The Tail (5-10%)**
8. File re-reads — Reading the same file twice
9. Sleep/poll loops — Checking "is it done yet?" repeatedly
10. Failed retries — Broken commands that stay in context
11. Schema lookups — Looking up tools it already knows
12. Git ceremony — Running git commands one at a time

**Tier 4 — Always-On Agents (OpenClaw, etc.)**
13. Idle heartbeats — Agent wakes every 5min, nothing to do, still pays
14. Workspace file bloat — 35K tokens of personality re-read every wake-up
15. Memory accumulation — Session history grows forever without cleanup

## Multi-language

Auto-detects your system language (English, 中文, 日本語, 한국어, Español, Français, Deutsch, etc). Responds in your language. Switch anytime — output language = input language.

## Supported models

Claude (Opus, Sonnet, Haiku), GPT-4o/4.1/o1/o3/o4-mini, Gemini 2.5/2.0, DeepSeek V3/R1

## Works on

- macOS (Apple Silicon + Intel)
- Windows
- Linux

Requires Python 3.8+. No dependencies beyond stdlib.
