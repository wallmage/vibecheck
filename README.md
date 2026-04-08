# vibecheck

[![GitHub stars](https://img.shields.io/github/stars/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/watchers)
[![GitHub last commit](https://img.shields.io/github/last-commit/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Top language](https://img.shields.io/github/languages/top/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Privacy](https://img.shields.io/badge/privacy-local%20only-111827?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Coverage](https://img.shields.io/badge/coverage-24%2B%20tools-0f766e?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-4f46e5?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Focus](https://img.shields.io/badge/focus-cost%20optimization-b45309?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Codex%20%7C%20Gemini-2563eb?style=flat-square)](https://github.com/wallmage/vibecheck)

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

I kept hitting my Claude quota mid-afternoon and couldn't figure out why. Turns out most of my AI coding sessions were 70% waste — the AI narrating what it was about to do, commands split across three turns that should have been one, stale context piling up and getting re-read on every single turn.

vibecheck finds that waste. It reads your actual session logs across 24+ coding tools, puts dollar amounts on 15 specific patterns, and fixes them. Everything runs locally. Nothing uploaded, no telemetry, no servers.

In my case: monthly spend went from $2,816 to $422. **85% cut.**

## How to Install

Paste this into your AI coding tool and press Enter:

> Help me install this skill: https://github.com/wallmage/vibecheck

That's it. Your AI picks up the skill and you're ready to scan.

<details>
<summary>Or install manually via command line</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Then type `/vibecheck scan` in any session.

To update: `cd ~/.claude/skills/vibecheck && git pull`
</details>

### What exactly is a "skill"?

A plain text file that teaches your AI how to do something new. No binaries, no background processes, no system modifications. vibecheck's skill file says "here's how to find waste and fix it." Delete the folder and it's gone.

### Coding tools vs. chat tools

**Coding tools** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) run on your machine and leave session logs. vibecheck auto-detects what you have and scans those logs directly.

**Chat tools** (Cowork, browser-based Claude) run in a sandbox without local logs. vibecheck still optimizes your instruction files — that's where most of the savings come from anyway. Or paste one terminal command to export 14 days of logs for a full scan.

### Permissions

vibecheck reads your local session logs and inspects instruction files (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) plus machine-wide tool settings. When your tool has a global config — one file that covers all projects — the optimizer goes there first, because one fix saves you money everywhere. It asks before changing anything.

## Privacy

Everything stays on your machine. The analysis is a set of Python scripts that parse your local session logs. No server, no API calls, no analytics. Open source — read every line if you want.

## Commands

| Command | What it does |
|---|---|
| `/vibecheck scan` | Scans all detected tools on your machine. One unified report with health markers, ranked statistics, top waste patterns, and an optimization roadmap |
| `/vibecheck explain` | Teaches you the waste patterns without changing anything. Pure education |
| `/vibecheck compress` | Shrinks your instruction files 25-50% using a 4-pass lossless compressor |
| `/vibecheck monitor` | Weekly comparison against your baseline. Catches cost regressions before they add up |

The scan keeps things quiet: a compact progress indicator, then a clean summary. `Good` means measured waste under 10%, `Waste` means above. Raw logs and tool chatter stay backstage unless something goes wrong.

### Keeping sessions fresh

Long conversations cost more than short ones — every new turn re-reads all the old ones, and overloaded context makes the AI sloppier, which means more back-and-forth.

Rule of thumb: 5-10 active minutes per session, 30-40 turns before the context tax really starts to bite. When you start fresh, keep your durable rules in instruction files (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) and project background in small local docs. New session doesn't mean cold restart — just a clean context with all your knowledge still there.

---

## Before / After

Measured across real sessions:

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## How AI Turns Cost Money

Quick primer if you've never thought about token economics. No AI pricing background needed.

### What happens on every turn

Every time your AI responds, it re-reads the entire conversation from the top. System prompt, instruction file, every message you sent, every response it gave, all tool output — file contents, terminal results, error logs — everything. Then it generates a new response.

**Turn cost = tokens read x input price + tokens generated x output price**

Early turns are cheap. Turn 1 might read 5,000 tokens. By turn 40, it's re-reading 40,000+ tokens of accumulated conversation — every prior message, every code snippet, every error trace. That late turn costs 8x what the first one did.

Here's the thing that makes waste so expensive: **it compounds.** A wasted turn doesn't just cost its own tokens. It sits in context for the rest of the session, getting re-read on every future turn. One unnecessary narration message at turn 10 gets re-read 30 more times before you're done.

### Prompt caching helps, but doesn't fix it

Most providers now cache previously-seen content and charge 10x less for it. Effective input cost drops from $3.00/million tokens to $0.30/million.

That helps. But new content — fresh tool output, new error messages, each new AI response — always enters at full price before getting cached. And waste still compounds even at the cached rate.

### Subscriptions feel the same pain

If you're on a subscription, you might think API pricing doesn't apply to you. It does — you just feel it differently. Subscriptions buy a fixed pool of compute, and waste burns through that pool faster. When you hit your quota and get rate-limited at 3pm, that's not because you worked too much. It's because a lot of that work was waste.

Claude Pro ($20/mo) covers roughly $200 in API-equivalent value. Claude 20x Max ($200/mo) covers roughly $4,000. More waste = faster wall.

<details>
<summary><strong>Deep Dive: What your subscription is actually worth in tokens</strong></summary>

### How I measured this

I have the $200/mo Claude 20x Max plan and kept running out of quota. Got curious enough to switch to API billing and track real dollar spend across 100+ data points — log every coding activity, check usage right after. That gave me enough to work out the relationship between subscription price and actual token value.

### The multipliers

| Plan | Price | API value | Multiplier | 5h window | Weekly total |
|---|---|---|---|---|---|
| Claude Pro | $20/mo | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mo | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mo | ~$4,000 | 20x | $133.33 | $933.31 |

The 20x Max tier is the only one with a real multiplier bump — 20x face value vs. 10x for the lower tiers.

### What that means in practice

- **$20 Claude Pro** — serious dev work (building features, research, writing) burns through your 5-hour quota in under an hour. Weekly capacity under 7 hours. Tight for any professional.
- **$100 5x Max** — roughly 4 hours before hitting the 5-hour window. 30-35 hours/week total. Workable for regular use.
- **$200 20x Max** — built for people who work 80-100+ hours/week, often running multiple sessions in parallel.

### Why Anthropic restricted third-party subscription usage

At 10-20x face value, every subscription dollar buys far more compute than the API rate. Third-party tools burning through that at API-equivalent speeds made the math unsustainable.

### The Codex alternative

At the $20 tier, Codex Plus delivers roughly **3x the coding usage** of Claude Pro. ChatGPT conversations — even GPT-5.4 Extended Thinking and deep research — don't count against the Codex coding quota. So you get 3x the coding capacity plus free GPT-5.4 on top.

**If $20/mo is your budget, Codex Plus gives you more coding time than Claude Pro.** If you're going higher, the Claude 5x and 20x tiers offer a different value proposition.

</details>

### Reference scenario

All dollar amounts in this document use this baseline (Sonnet 4.6 pricing):

| Parameter | Value |
|---|---|
| Session length | 25 turns |
| Starting context | 21,000 tokens |
| Growth per turn | ~600 tokens |
| Cache hit rate | 95% |
| Mid-session turn cost | $0.017 |
| Efficient session total | $0.41 |

For Opus 4.6, multiply all costs by 1.67x.

---

## The 15 Waste Patterns

Organized by how much money they burn. The top three alone account for 60-70% of all waste.

### Tier 1 — The Big Three (60-70% of waste)

#### 1. Idle Narration

Your AI says "OK, I'll fix that now" or "Let me read the file first" — then actually does the work on the next turn. That narration turn did nothing. No tool call, no code, no file read. Just an announcement.

Each one costs about **$0.017** — and worse, those 300-500 tokens of status text stick around in context, getting re-read on every future turn. Across 428 measured sessions: **$1.03/session wasted**, 30% of all waste. At 10 sessions/day, that's **$309/month on narration alone.**

vibecheck adds one rule: *"No turn without a tool call. Think and act in the same turn."* **Saves ~$0.88/session.**

#### 2. Context Rot

Session cost grows quadratically, not linearly. Turn 50 re-reads all 49 prior turns.

Concrete comparison: one 40-turn session costs **$0.70**. Split the same work into two 20-turn sessions and it's **$0.60**. That $0.10 gap is pure waste from keeping a bloated conversation alive. Real-world sessions average 74 turns — **$0.46/session wasted**, 13% of all waste.

vibecheck teaches: *"Unrelated work goes in separate sessions. In long threads, stay compact."* **Saves ~$0.37/session.**

#### 3. Ping-Pong Debugging

Fix, break, retry, break again. Each failed attempt dumps ~4,000 tokens of error output into context, and that dead text gets re-read on every turn after. Three cycles: 6 extra turns ($0.102) + 12K tokens of stale errors ($0.036) = **~$0.14 per episode**. Occurs in ~10% of sessions. **Weighted: $0.015/session.**

vibecheck adds a circuit breaker: *"After 2 failed fixes on the same file — stop, re-read the full error, think, one targeted fix."* **Saves ~$0.01/session.**

### Tier 2 — Turn Density (15-20% of waste)

Doing in three turns what should take one.

#### 4. Verbose Tool Output

A build or test command dumps 500 lines (~5,000 tokens) into the conversation. Those tokens get re-read every turn for the rest of the session. 5K tokens x 12 remaining turns at cached rate = **$0.018/instance**. Without caching: **$0.180** — 10x worse.

This is actually the single costliest pattern by measurement. Build logs, npm output, test dumps — they flood nearly every session. **$1.05/session**, 31% of all waste.

Fix: *"Pipe output to /tmp/. Use --quiet flags. tail -50 max."* **Saves ~$0.89/session.**

#### 5. Unchained Commands

`npm install` in one turn. `npm run build` in the next. Two context re-reads for what `npm install && npm run build` does in one. Each split: **$0.010**. Adds up to **$0.14/session** in command-heavy sessions.

Fix: *"Chain commands with `&&` when safe."* **Saves ~$0.11/session.**

#### 6. Codebase Wandering

The AI opens README, package.json, three configs, and two unrelated modules before writing a single line of code. Five consecutive reads, no edits, no decisions. $0.085 in wasted turns + $0.027 context tax = **$0.112/episode.** Average: **$0.09/session.**

Fix: grep or glob first, read only what's relevant, batch multiple reads per turn. **Saves ~$0.07/session.**

#### 7. Unbatched Edits

Edit file A, then B, then C — three turns. One turn with parallel edits does the same thing. Two extra turns at $0.017 = **$0.034/instance.** Average: **$0.058/session.**

Fix: *"Batch independent tool calls."* **Saves ~$0.05/session.**

### Tier 3 — The Tail (5-10% of waste)

Small individually. They add up.

#### 8. File Re-reads

Same file read twice in one session — content already in context, but the AI grabs it again. **$0.019/re-read**, files get re-read 3-4 times on average. **$0.066/session.** Fix: *"Already in context. Re-read only if the file changed."* **Saves ~$0.05/session.**

#### 9. Sleep/Poll Loops

`sleep 5 && check_status`, repeated 3-5 times. Each poll = full context re-read to see if a background process is done. 4 polls x $0.017 = **$0.068/episode**, **$0.043/session.** Fix: *"Use --wait or run_in_background."* **Saves ~$0.034/session.**

#### 10. Failed Retries

Command fails, AI runs the same command unchanged. Error output now in context twice. **$0.019/retry**, **$0.080/session.** Fix: same as ping-pong — *"Stop, read the error, try something different."*

#### 11. Schema Lookups

The AI looks up its own tool definitions — information it already has. Adds 2K+ tokens for nothing. **$0.023/session.** The "no turn without a tool call" rule handles this. **Saves ~$0.02/session.**

#### 12. Git Ceremony

`git add` → `git status` → `git commit` → `git push`. Four turns. `git add -A && git commit -m "msg" && git push` is one. **$0.044/instance** but rarer than you'd think — **$0.003/session.** Fix: chain with `&&`.

### Tier 4 — Always-On Agents

Different cost model. Agents like OpenClaw wake periodically, and waste is measured per day, not per session.

#### 13. Idle Heartbeats

Agent wakes every 5 minutes, re-reads the whole workspace, finds nothing, goes back to sleep. 288 wake-ups/day, ~97% idle. That's 280 idle wakes at $0.04 each = **$11.20/day ($336/month)** doing nothing.

Fix: *"30-minute minimum heartbeat. Skip if no triggers pending."* Down to ~48 wakes/day. **Saves $8-10/day ($240-300/month).**

#### 14. Workspace File Bloat

35,000 tokens of personality files (SOUL.md, AGENTS.md, etc.) re-read every single wake-up. Tutorials, coaching, philosophy — all written for humans, not for an AI running tasks. **$5.76/day ($173/month)** on config files alone.

vibecheck compresses them: 35K → 12-15K tokens. Same behavioral rules, no human-facing filler. **Saves $3-4/day ($90-120/month).**

#### 15. Memory Accumulation

Session history grows forever. 100+ memory entries re-read every wake, including stuff from weeks ago that no longer matters. **$3.17/day ($95/month)** on stale memories.

Fix: *"Archive after 50 entries, summarize, start fresh."* **Saves $2-3/day ($60-90/month).**

---

## The Optimization Toolkit

vibecheck doesn't just point at problems. It fixes them.

### Instruction File Compression

Your instruction file (`CLAUDE.md`, `AGENTS.md`, `Memory.md`, whatever your tool calls it) gets read on every single turn. It's a fixed tax on everything you do. A bloated instruction file is a toll booth on every road in town.

vibecheck has a 4-pass lossless compressor — 23 techniques, and "lossless" means literally no facts removed. Same information, fewer tokens.

| Pass | What it does | How much it saves |
|---|---|---|
| **Pass 1 — Mechanical** | Strips markdown formatting, converts tables to compact form, merges bullets | 10-15% |
| **Pass 2 — Fact-preserving** | Deduplicates repeated facts, compresses code examples, collapses verbose descriptions | 15-25% |
| **Pass 3 — High-fidelity** | Removes tutorials and coaching text that humans need but the AI doesn't | 10-15% |
| **Pass 4 — Telegram** | Full shorthand rewrite for AI-only files. Dense, compressed, but only with your explicit permission | 15-25% |

A 10,000-token instruction file compressed to 6,000 saves $0.044 per session. At 10 sessions per day: **$0.44/day ($13/month)** from compression alone.

### Output Suppression

Output tokens cost 5x input ($15 vs. $3/million on Sonnet 4.6). The AI printing full code blocks or diffs you didn't ask for? Expensive. vibecheck adds: *"No code or diffs unless asked."* **Saves ~$0.047/session.**

### Cost Monitoring

`/vibecheck monitor` snapshots your session profile and compares against baseline on future runs. New instruction file introduced verbosity? Different project, different habits? The monitor catches regressions before they add up.

---

## Savings Summary

### Interactive tools (Sonnet 4.6 pricing)

| # | Pattern | Avg waste/session | Avg saved |
|---|---|---|---|
| 1 | Idle narration | $1.03 | $0.88 |
| 2 | Context rot | $0.46 | $0.37 |
| 3 | Ping-pong debugging | $0.015 | $0.01 |
| 4 | Verbose output | $1.05 | $0.89 |
| 5 | Unchained commands | $0.14 | $0.11 |
| 6 | Codebase wandering | $0.09 | $0.07 |
| 7 | Unbatched edits | $0.058 | $0.05 |
| 8 | File re-reads | $0.066 | $0.05 |
| 9 | Sleep/poll loops | $0.043 | $0.034 |
| 10 | Failed retries | $0.08 | $0.06 |
| 11 | Schema lookups | $0.023 | $0.02 |
| 12 | Git ceremony | $0.003 | $0.003 |
| + | Compression | $0.044 | $0.044 |
| + | Output suppression | $0.047 | $0.038 |
| | **Total** | **$3.15*** | **$2.61** |

*Individual patterns can co-occur in the same turn — totals reflect per-pattern measurement. Actual aggregate: $3.07 to $0.46 (see Before / After).

**Typical wasteful session: $3.07. After vibecheck: $0.46. Savings: 85%.**

- **Light waste** (short sessions, few patterns): 40-55% reduction
- **Moderate waste** (average user): 55-70% reduction
- **Heavy waste** (long sessions, multiple patterns): 70-85% reduction

### Always-on agents

| # | Pattern | Daily waste | Daily savings |
|---|---|---|---|
| 13 | Idle heartbeats | $11.20 | $9.70 |
| 14 | Workspace bloat | $5.76 | $3.76 |
| 15 | Memory accumulation | $3.17 | $2.37 |
| | **Total** | **$20.13/day** | **$15.83/day** |

**Monthly savings for always-on agents: ~$475.**

---

## Supported Tools

24+ tools. No lock-in — vibecheck is a text file, so any AI that reads instructions can use it. The scan scripts are plain Python, no dependencies.

**Full session scan** (reads your logs, puts dollar amounts on waste):
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Detection + instruction optimization** (no full log parsing yet, but detects the tool and optimizes your config files):
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

**LLMs with pricing data:** Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ more.

**Platforms:** macOS, Windows, Linux, iPad via SSH. Python 3.8+.

---

<details>
<summary><strong>Methodology</strong></summary>

All cost estimates use the reference scenario above. Key assumptions:

- **95% prompt cache hit rate** — typical for rapid coding sessions. Slower sessions with longer pauses between turns will have lower cache hit rates and higher costs.
- **25 productive turns/session** — wasteful sessions add 8-12 extra turns from narration, retries, and unchained commands.
- **600 tokens/turn growth** — verbose sessions can hit 1,000-2,000 tokens per turn.
- **Effective input rate: $0.435/1M** — blended rate of 95% cached ($0.30/1M) + 5% uncached ($3.00/1M).
- **Context tax rate: $0.30/1M** — cached input rate for permanent context additions.

Conservative estimates. Real-world savings often exceed these, especially with long sessions, large instruction files, or heavy debugging.
</details>

## Author

[Wallny](https://github.com/wallmage)
