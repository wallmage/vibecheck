# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**You're paying for your AI to re-read its own messages.**

Every time you send a message, the AI reads the entire conversation again. From the top. Message #50 re-reads all 49 previous messages before it even starts thinking. That "OK, now I'll fix that" line the AI typed? It did nothing — but you paid for it, and you'll keep paying for it every turn after because it's now part of the conversation the AI re-reads.

I ran this on my own sessions. Over 50% of my token spend was waste. These patterns show up in almost every session.

vibecheck analyzes your AI coding session logs, shows you where the money went, and adds a paragraph to your instruction file that stops most of the waste. Same work, lower bill.

Works with Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. Supports 24+ coding tools -- full session analysis for Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, and Google Antigravity, plus instruction-file optimization for the rest. Runs locally. Your data stays on your machine.

## Nothing to install

vibecheck is a **skill** -- a cheat sheet your AI reads. No downloads. You paste one message, your AI learns the skill, done.

Copy this into whatever AI coding tool you use:

> Install the vibecheck skill from https://github.com/wallmage/vibecheck and run /vibecheck scan

That's the whole setup. Your AI reads the skill file and walks you through the result.

If you're on Claude Code, install permanently:
```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```
Then in any Claude Code session:
```
/vibecheck scan
```

If you're using a sandbox tool (Cowork, etc.):
> Clone https://github.com/wallmage/vibecheck to /tmp/vibecheck, read SKILL.md, and run /vibecheck scan

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

## The 15 patterns

**The big 3 (70-80% of waste)**
1. Idle narration -- "Now I'll fix that" then fixes it. Just fix it.
2. Context rot -- 60-message conversations where the last message costs 60x the first
3. Ping-pong debugging -- edit, break, edit, break

**Mechanics (15-20%)**
4. Verbose output -- 500 lines of build logs re-read every future turn
5. Unchained commands -- `git add` then `git commit` as two separate messages
6. Codebase wandering -- reading 8 files before touching 1
7. Unbatched edits -- editing 3 files in 3 messages instead of 1

**The tail (5-10%)**
8. File re-reads -- same file, read twice
9. Sleep/poll loops -- "is it done yet?" every 5 seconds
10. Failed retries -- broken command stays in context forever
11. Schema lookups -- checking what tools exist (it already knows)
12. Git ceremony -- 4 git commands in 4 separate turns

**Always-on agents (OpenClaw, etc.)**
13. Idle heartbeats -- wakes up every 5 minutes, nothing to do, pays anyway
14. Workspace bloat -- re-reads 35K tokens of personality files every wake-up
15. Memory accumulation -- session history grows forever

## Supported tools

24+ tools today.

- **Full session scan:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot / VS Code chat sessions, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Detection + instruction optimization:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

All LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ more.

## Runs on

macOS, Windows, Linux, iPad via SSH. Python 3.8+, no dependencies.
