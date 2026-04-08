# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Every turn your AI takes costs money.** Sonnet 4.6: $3/$15 per million tokens (input/output). Opus 4.6: $5/$25 — 1.67x more. A mid-session turn on Sonnet costs ~$0.038. When your AI says "OK, let me fix that" before fixing it — that turn cost you $0.031 for nothing. And it compounds: every turn re-reads the entire conversation from the top, so the longer your chat goes, the more expensive each turn becomes. That's context rot.

AI coding tools waste turns constantly — narrating instead of acting, reading 3 files one at a time instead of all at once, running `git add` and `git commit` as separate turns. vibecheck detects 18 mechanisms across 4 tiers, fixes them through instruction file rules and compression, and tracks improvement over time. Together they cut your bill 40-65% depending on usage pattern. [Full mechanism specs with dollar breakdowns →](SPECSHEET.md)

Works with Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. Supports 24+ coding tools. Runs locally. Your data stays on your machine.

## How to install

Paste this into your AI coding tool and press Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

That's it. Your AI does the rest.

<details>
<summary>Or install manually via command line</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Then type `/vibecheck scan` in any session.

To update: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Wait, what's a skill?

A recipe card for your AI. It doesn't modify anything or install anything. Just a text file that says "here's how to find waste and fix it." Your AI reads it and follows the instructions. Delete it whenever you want.

### Coding tools vs chat tools

**Coding tools** run on your machine, so vibecheck can detect your tool and instruction file automatically. Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, and Google Antigravity get the full session scan. Other supported tools get instruction-file optimization while deeper log support rolls out.

**Chat tools** (Cowork, browser-based tools) run in a sandbox and can't see your logs. vibecheck still works two ways:

1. **Skip the scan.** vibecheck trims your instruction file, adds rules that reduce narration and noisy output, and encourages batching. No log access needed. This alone gets you most of the benefit.

2. **Copy your logs over (5 seconds).** Paste one command in your terminal. It copies 14 days of logs to a folder the sandbox can see, then you get the full scan.

### Permissions

vibecheck reads and edits your instruction file (CLAUDE.md, AGENTS.md, .cursorrules, etc.). It asks before every change. You approve each one.

## Privacy

Your data doesn't leave your machine. No server. A handful of Python scripts that read local files and print results to your screen. Open source, read it yourself.

## Commands

- `/vibecheck scan` -- teaches you what tokens are, runs a scan when your tool supports it, then applies fixes
- `/vibecheck explain` -- just the lesson, no changes
- `/vibecheck compress` -- shrinks your instruction file 25-50%
- `/vibecheck monitor` -- weekly comparison, flags regressions

## What it actually does

Most people don't know what they're paying for. A $20/month Claude subscription covers about $200 in actual API usage. Where does it go?

When full analysis is supported, vibecheck walks you through it with your own data: what tokens are, why the AI re-reads everything every message (this is where most of your money goes), and your specific waste patterns with dollar amounts.

Then it adds one paragraph to your instruction file. Your AI reads those rules and stops doing the wasteful stuff.

### Even without a scan

Just installing the skill makes your AI:
- Stop saying "now I'll fix that" before fixing it (just fix it)
- Edit three files in one message instead of three
- Run `git add && git commit` instead of two separate turns
- Clear long conversations instead of letting them bloat
- Pipe build output to a file instead of dumping 500 lines into the chat

That's where most of the savings come from. A scan finds the rest.

## Before / After

Run it once, get projections. Run it again in a couple weeks, see what changed:

```
                              BEFORE         NOW            CHANGE
  Avg turns/session           36.8           25.9           -10.9 ✅
  Avg context window          128.4K         89.9K          -30% ✅
  Wasteful turns              36.7%          8.1%           -28.6% ✅

  Avg cost/session            $2.62          $1.35          -$1.27 ✅
  Monthly spend               $224           $115           -$109 ✅
```

Snapshots saved in `~/.vibecheck/snapshots/`. Persists across reboots.

## The 18 mechanisms

**Tier 1 — The Big 3 (60-70% of waste)**
1. Idle narration — "Now I'll fix that" then fixes it next turn. $0.031 wasted per occurrence.
2. Context rot — 60-turn conversation where turn 60 costs 12x turn 1. Splitting saves $0.67/session.
3. Ping-pong debugging — fix, break, fix, break. 12K tokens of dead errors in context.

**Tier 2 — Turn Density (15-20%)**
4. Verbose output — 5K tokens of build logs re-read every future turn. $0.018/instance context tax.
5. Unchained commands — `git add` then `git commit` as two turns. $0.023 per unnecessary split.
6. Codebase wandering — reading 8 files before touching 1. $0.217 per episode.
7. Unbatched edits — editing 3 files in 3 turns instead of 1. $0.076/instance.

**Tier 3 — The Tail (5-10%)**
8. File re-reads — same file, read twice. $0.043 wasted.
9. Sleep/poll loops — "is it done yet?" every 5 seconds. $0.152 per episode.
10. Failed retries — same broken command, run twice. Error output stuck in context.
11. Schema lookups — checking what tools exist (it already knows). $0.052 wasted.
12. Git ceremony — 4 git commands in 4 turns. $0.098/instance.

**Tier 4 — Always-On Agents**
13. Idle heartbeats — wakes every 5 min, nothing to do. **$11.20/day** wasted.
14. Workspace bloat — re-reads 35K tokens of personality files every wake. $5.76/day.
15. Memory accumulation — session history grows forever. $3.17/day.

**Optimization Tools**
16. Instruction file compression — 4-pass lossless compressor, 23 techniques, 25-50% reduction.
17. Output suppression — no code/diffs unless asked. Output tokens cost 5x input.
18. Cost monitoring — weekly comparison, regression alerts.

[Detailed breakdown with methodology →](SPECSHEET.md)

## Supported tools

24+ tools today.

- **Full session scan:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot / VS Code chat sessions, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Detection + instruction optimization:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

All LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ more.

## Runs on

macOS, Windows, Linux, iPad via SSH. Python 3.8+, no dependencies.
