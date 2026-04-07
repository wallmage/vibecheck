# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Your AI coding tool is burning money you don't see.**

Every message you send, your AI re-reads your *entire* conversation from scratch. Message #50 costs 50x what message #1 cost. That narration where it says "OK, now I'll fix that"? That cost you money and did nothing. Those 500 lines of build logs? Re-read on every. single. future. message.

Most vibe coders waste **50%+** of their AI token budget without knowing it.

vibecheck fixes that. It scans your last 14 days of sessions, finds exactly where the waste is, explains it in plain language (no jargon — we'll teach you what tokens are), and applies one-paragraph fixes to your instruction file. Same work gets done. Half the cost.

**Average savings: 50%+ of your token bill.** Supports all LLM models (Claude, GPT, Gemini, DeepSeek). Works with Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf, and 24+ AI coding tools. 100% local — your data never leaves your machine.

## Get started — nothing to download

vibecheck is a **skill** — a set of instructions your AI coding tool learns from. You don't download or install any software. You just give your AI a link, and it teaches itself how to optimize your costs. One message, done.

**Copy this into your AI coding tool** (Claude Code, Cursor, Codex, Windsurf, Cline — any of them):

> Install the vibecheck skill from https://github.com/wallmage/vibecheck and run /vibecheck scan

That's it. Your AI reads the skill, scans your last 14 days, and walks you through everything.

**Or if you prefer the CLI:**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

### What's a "skill"?

A skill is like a recipe card for your AI. It doesn't change your AI or install anything on your computer. It just gives your AI a set of instructions — "here's how to find waste patterns, here's how to explain them, here's how to fix them." Your AI reads the recipe and follows it. You can remove it anytime.

### Coding tools vs chat tools

**Coding tools** (Claude Code CLI, Claude Desktop Builder/Code mode, Cursor, Codex, Windsurf, Cline) run directly on your machine. They can read your session logs and give you a full personalized scan with your real numbers. Best experience.

**Chat/sandbox tools** (Claude Cowork, chat-only modes, browser-based tools) run in a sandbox — they can see your project files but not your chat history. Like a guest who can see your living room but not your bedroom.

vibecheck still works in two ways:

1. **Without a scan (80% of the benefit):** Optimizes your instruction file — trims your CLAUDE.md, adds cost-saving rules, compresses bloated prompts. These fixes alone cut 20-40% of waste. No log access needed.

2. **With a scan (full benefit):** vibecheck asks you to paste one command in your terminal. Copies only the last 14 days of logs (~20-50 MB, not your full history). Takes 5 seconds, then you get the full personalized analysis.

### Permissions

vibecheck needs access to your **project folder** to read and edit your instruction file (CLAUDE.md, AGENTS.md, .cursorrules, SOUL.md, etc.). It asks before every change. You review and approve each edit individually.

## Privacy

**Your data never leaves your machine.** vibecheck is a set of Python scripts that run 100% locally. No server, no API, no telemetry, no analytics, no phoning home. The author cannot collect your data — it's technically impossible. The code is open source; you can read every line.

## Commands

- `/vibecheck` or `/vibecheck scan` — Interactive education + full diagnostic + fixes
- `/vibecheck explain` — Just the education (understand your bill, no changes)
- `/vibecheck compress` — Compress instruction file (25-50% smaller)
- `/vibecheck monitor` — Week-over-week comparison with alerts

## How it works

Most people don't know what they're paying for. A $20/month subscription can hide $200+ of actual AI usage. But where does it go?

vibecheck starts with an interactive lesson — using YOUR real data — that explains it piece by piece:
1. What are tokens? (Hint: roughly one word)
2. Why does the AI re-read your entire conversation every message?
3. Where is YOUR money going? (Spoiler: 50-65% is re-reading old messages)

Then it finds your waste patterns and fixes them with one paragraph in your instruction file. Same work, fewer wasted messages.

### Even without a scan

If you can't or don't want to scan your logs, vibecheck still helps. Installing the skill adds optimization rules to your setup. Your AI learns to:
- Stop narrating what it's about to do (just do it)
- Batch multiple edits into one message
- Chain commands instead of running them one at a time
- Keep conversations shorter to avoid context bloat
- Pipe verbose output to files instead of flooding the chat

These rules alone get you ~80% of the savings. The scan finds the remaining 20% and shows you exactly where your money went.

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

## Multi-language

Auto-detects your system language (English, 中文, 日本語, 한국어, Español, Français, Deutsch, etc). Responds in your language. Switch anytime — output language = input language.

## Supported models

Claude (Opus, Sonnet, Haiku), GPT-4o/4.1/o1/o3/o4-mini, Gemini 2.5/2.0, DeepSeek V3/R1

## Works on

- macOS (Apple Silicon + Intel)
- Windows
- Linux
- iPad/mobile via SSH (Moshi, Termius, Blink)

Requires Python 3.8+. No dependencies beyond stdlib.
