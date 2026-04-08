# vibecheck

[![Runs local](https://img.shields.io/badge/runs-local%20only-1f6feb)](https://github.com/wallmage/vibecheck)
[![Multi-tool](https://img.shields.io/badge/multi--tool-24%2B%20tools-0a7f5a)](https://github.com/wallmage/vibecheck)
[![Privacy](https://img.shields.io/badge/privacy-no%20telemetry-6f42c1)](https://github.com/wallmage/vibecheck)
[![Sister skill](https://img.shields.io/badge/sister%20skill-handoff-f97316)](https://github.com/wallmage/handoff)

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Every turn your AI takes costs money.** Sonnet 4.6: $3/$15 per million tokens (input/output). Opus 4.6: $5/$25 — 1.67x more. Here's what that looks like:

- Your AI says "OK, I'll fix that" before fixing it. That narration turn: **$0.017 wasted.** Across a real session: **$1.03 gone.**
- Your average session runs 74 turns instead of three focused chats. Extra re-reading cost: **$0.46 wasted.**
- `git add`, then `git commit`, then `git push` — three turns instead of one chained command: **$0.044 wasted.**

These are 3 of the 15 waste patterns vibecheck catches. Every one explained below with dollar amounts, what goes wrong, and how we fix it.

Works with Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ coding tools. Runs locally — your data stays on your machine.

## What vibecheck does

- scans the supported AI coding tools on your machine in one unified pass
- shows waste by tool, model, provider, and project
- fixes the first important tool step by step
- bulk-applies the same treatment to the rest after one approval
- finishes with human-side education so people keep costs down without breaking their workflow

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

### What's a skill?

A recipe card for your AI. It doesn't modify anything or install anything. Just a text file that says "here's how to find waste and fix it." Delete it whenever you want.

### Coding tools vs chat tools

**Coding tools** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) run on your machine — vibecheck auto-detects your tool and scans your session logs.

**Chat tools** (Cowork, browser-based) run in a sandbox. vibecheck still optimizes your instruction file (most of the benefit), or you paste one terminal command to copy 14 days of logs over for a full scan.

### Permissions

vibecheck reads your local tool logs and can inspect project instruction files, machine-wide instruction files, and machine-wide tool settings/config files. When a tool supports a global instruction surface, the optimizer now prefers that one-fix-for-all-projects path before falling back to per-project files. It asks before every change.

## Privacy

Your data doesn't leave your machine. No server, no API, no telemetry. Open source.

## Commands

- `/vibecheck scan` — scans all detected supported tools on this machine, then shows one unified result plus machine-wide optimization targets
- `/vibecheck explain` — just the lesson, no changes
- `/vibecheck compress` — shrinks your instruction file 25-50%
- `/vibecheck monitor` — weekly comparison, flags regressions
- `python3 scripts/export_optimization_log.py <payload.json> [output.md]` — saves a clean Markdown scan log or tool-optimization log locally

`/vibecheck scan` should feel calm: one compact progress state while it works, then a clean unified summary with health markers (`Good ✅` for measured waste `<= 10%`, `Waste ❌` for measured waste `> 10%`), ranked tool/model statistics, top patterns, and a daily-driver-first optimization roadmap. Raw logs and internal tool chatter stay backstage unless something fails and you explicitly need details.

## Related

- [handoff](https://github.com/wallmage/handoff) — separate sister skill for switching to fresh chats without losing decisions or state

### Fresh sessions without losing context

vibecheck teaches that long threads are expensive for two reasons: each turn re-reads more stale context, and overloaded context makes the model less sharp. A practical rule of thumb is to keep focused work in chunks that usually fit inside 5-10 active minutes, and treat roughly 30-40 turns as the upper comfort band before the context tax starts snowballing.

The hard part is continuity. People keep bloated chats alive because they do not want to lose decisions, state, and momentum. Keep durable behavior rules in `CLAUDE.md` / `AGENTS.md` / `Memory.md`, keep project background in small local `.md` docs, and use a separate handoff skill when you want a fresh chat without a cold restart. vibecheck should offer that later, after the user has already seen the optimization win, with one static GitHub install prompt.

The sister skill is [handoff](https://github.com/wallmage/handoff). When the education flow gets to context rot and fresh-session habits, the install prompt should be:

```text
Help me install this skill too: https://github.com/wallmage/handoff
```

## Before / After

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## How turns cost money

Every turn, your AI re-reads the entire conversation — system prompt, instruction file, all previous messages, all tool output — then generates a response.

**Turn cost = input tokens x input rate + output tokens x output rate**

Early turns are cheap (small context). Late turns are expensive (everything before gets re-read). That's why waste compounds — a wasted turn makes every future turn more expensive because the wasted content stays in context.

Prompt caching cuts input cost 10x for previously-seen content. Most tools use it automatically.

**Subscription users:** You don't see API prices directly, but waste burns through your message quota faster. Claude Pro ($20/mo) covers ~$200 in API value. Max ($200/mo) covers ~$4,000.

<details>
<summary><strong>Research: What your subscription is really worth in tokens</strong></summary>

### How I measured this

I have the $200/mo Claude 20x Max plan and kept running out of quota. So I got curious: how much API usage does each tier actually buy?

I switched to API billing and tracked real dollar spend across 100+ data points — every activity followed by a usage refresh. Enough to calculate the linear relationship between subscription price and token value.

### The multipliers

| Plan | Price | API value | Multiplier | 5h window | Weekly total |
|---|---|---|---|---|---|
| Claude Pro | $20/mo | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mo | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mo | ~$4,000 | 20x | $133.33 | $933.31 |

The 20x Max tier is the only one that actually gives you a multiplier bump (20x vs 10x for the lower tiers).

### Real-world usage limits

- **$20 Claude Pro** — serious work (dev, research, writing) lasts less than 1 hour before your 5h quota is gone. Weekly total under 7 hours. Too limiting for any professional.
- **$100 5x Max** — you can work about 4 hours before hitting the 5h window. 30-35 hours/week total. Workable for regular use.
- **$200 20x Max** — for people who work 80-100+ hours/week, often multi-threading across sessions.

### Why Claude banned third-party subscription use

These multipliers explain it. At 10-20x face value, every subscription dollar buys far more compute than API pricing. Third-party tools burning through subscription quota at API-equivalent rates made the economics unsustainable.

### The Codex alternative

I haven't fully benchmarked Codex's dollar value yet, but at the $20 tier, Codex Plus delivers roughly **3x the coding usage** of Claude Pro.

Why: ChatGPT conversations — even GPT-5.4 Extended Thinking and deep research — don't count against your Codex quota. Pure coding alone is 3x Claude Pro, and you get Pro chat free on top.

**If you don't plan to buy at least Claude $100 tier, get $20 Codex Plus instead.** 3x the coding usage of Claude Pro, plus free GPT-5.4 Extended Thinking and deep research.

</details>

### Reference scenario

All dollar amounts below use this baseline (Sonnet 4.6):

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

## The 15 waste patterns

### Tier 1 — The Big 3 (60-70% of waste)

#### 1. Idle Narration

**What it is.** The AI says "OK, I'll fix that" or "Let me read the file first" — then does the actual work next turn. The narration turn did nothing: no tool call, no code, no file read.

**The waste.** Each narration turn costs **$0.017** (context re-read + ~500 tokens of status text). Real data across 428 sessions: **$1.03/session wasted** — 30% of all waste, tied with verbose output as the costliest pattern. Over 10 sessions/day: **$10.30/day ($309/month)** on narration alone.

**The fix.** vibecheck adds: *"No turn without tool call. No narration. Think and act in the same turn."* Eliminates narration entirely. **Saves ~$0.88/session.**

#### 2. Context Rot

**What it is.** Long conversations get progressively more expensive. Turn 50 re-reads all 49 prior turns. Total session cost grows quadratically with length.

**The waste.** One 40-turn session: **$0.70.** Two 20-turn sessions (same work): **$0.60.** Difference: **$0.10.** Real-world average at 74 turns/session: **$0.46/session wasted** from not splitting — 13% of all waste.

**The fix.** Teaches: *"Keep unrelated work in fresh chats when you can. In long threads, stay compact and avoid dragging old context forward unless it helps the next action."* **Saves ~$0.37/session for users with long-session habits.**

#### 3. Ping-Pong Debugging

**What it is.** Fix, break, retry, break again. Each failed attempt adds error output to context (~4K tokens per cycle), re-read on every future turn.

**The waste.** Three failed cycles: 6 extra turns ($0.102) + 12K tokens of dead errors ($0.036 context tax). **Total: ~$0.14 per episode.** Real data: occurs in ~10% of sessions. **Weighted: $0.015/session.**

**The fix.** Adds: *"After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix."* **Saves ~$0.01/session.**

### Tier 2 — Turn Density (15-20% of waste)

#### 4. Verbose Tool Output

**What it is.** Build/test command dumps 500 lines (~5K tokens) into the conversation. Those tokens get re-read on every future turn.

**The waste.** 5K tokens x 12 remaining turns x $0.30/1M = **$0.018/instance** context tax. Without caching: **$0.180/instance** — 10x worse. Real data: **$1.05/session** — the costliest pattern at 31% of all waste. Build logs, npm output, and test dumps flood context in nearly every session.

**The fix.** Adds: *"Pipe build/test output to /tmp/, use --quiet flags, tail -50 max."* **Saves ~$0.89/session.**

#### 5. Unchained Commands

**What it is.** `npm install` in one turn, `npm run build` in the next. Two context re-reads when `&&` chains them in one.

**The waste.** Each split: **$0.010.** Real data: **$0.14/session** — splits happen far more than 3-4 times in long sessions.

**The fix.** Adds: *"Chain commands with `&&` when safe."* **Saves ~$0.11/session.**

#### 6. Codebase Wandering

**What it is.** The AI opens file after file — README, package.json, configs — before doing any work. Five+ consecutive reads before the first edit.

**The waste.** Five unnecessary reads: $0.085 in turns + $0.027 context tax = **$0.112/episode.** Real data: **$0.09/session.**

**The fix.** Encourages targeted search (grep/glob first), batching multiple reads per turn. **Saves ~$0.07/session.**

#### 7. Unbatched Edits

**What it is.** Edit file A, then B, then C — three turns when one turn with parallel edits would do.

**The waste.** 2 extra turns x $0.017 = **$0.034/instance.** Real data: **$0.058/session.**

**The fix.** Adds: *"Batch independent tool calls (multiple Reads/Edits per turn)."* **Saves ~$0.05/session.**

### Tier 3 — The Tail (5-10% of waste)

#### 8. File Re-reads

**What it is.** Same file read twice in one session. Content is already in context after the first read.

**The waste.** 1 wasted turn + duplicate content = **$0.019/re-read.** Real data: **$0.066/session** — files get re-read 3-4 times on average.

**The fix.** Adds: *"Content in context after first read. Re-read only if file changed."* **Saves ~$0.05/session.**

#### 9. Sleep/Poll Loops

**What it is.** `sleep 5 && check_status`, repeated 3-5 times. Each poll re-reads the full context.

**The waste.** 4 polls x $0.017 = **$0.068/episode.** Real data: **$0.043/session.**

**The fix.** Adds: *"Use --wait flags or run_in_background."* **Saves ~$0.034/session.**

#### 10. Failed Retries

**What it is.** Command fails, AI runs the exact same command again. Error output now in context twice.

**The waste.** **$0.019/retry.** Real data: **$0.080/session** — retries happen more often than expected.

**The fix.** Same rule as ping-pong: *"Stop, re-read error, think, single targeted fix."*

#### 11. Schema Lookups

**What it is.** AI looks up its own tool definitions — information it already has. Adds 2K+ tokens to context.

**The waste.** **$0.023/lookup.** Real data: **$0.023/session.**

**The fix.** "No turn without tool call" discourages discovery turns. **Saves ~$0.02/session.**

#### 12. Git Ceremony

**What it is.** `git add` → `git status` → `git commit` → `git push`, four turns. `git add -A && git commit -m "msg" && git push` is one.

**The waste.** 3 extra turns + git output = **$0.044/instance.** Real data: **$0.003/session** — rarer than expected.

**The fix.** Adds: *"Chain git commands with `&&`."* **Saves ~$0.003/session.**

### Tier 4 — Always-On Agents (OpenClaw, etc.)

Different cost model: cost per wake-up x wakes per day.

#### 13. Idle Heartbeats

**What it is.** Agent wakes every 5 minutes, re-reads full workspace, finds nothing. 288 wakes/day, ~97% idle.

**The waste.** 280 idle wakes/day x $0.04 = **$11.20/day ($336/month)** doing nothing.

**The fix.** *"30min minimum heartbeat. Skip if no triggers."* Reduces to ~48 wakes/day. **Saves $8-10/day ($240-300/month).**

#### 14. Workspace File Bloat

**What it is.** 35K tokens of personality files (SOUL.md, AGENTS.md) re-read every wake. The AI only needs the behavioral rules — tutorials and coaching are for humans.

**The waste.** **$5.76/day ($173/month)** just reading config files.

**The fix.** Compresses workspace files: 35K → 12-15K tokens. **Saves $3-4/day ($90-120/month).**

#### 15. Memory Accumulation

**What it is.** Session history grows without pruning. 100+ entries re-read every wake.

**The waste.** **$3.17/day ($95/month)** reading stale memory.

**The fix.** *"Archive after 50 turns, summarize, start fresh."* **Saves $2-3/day ($60-90/month).**

---

## Plus: Optimization Tools

### Instruction File Compression

Your instruction file is read every turn — a fixed tax you pay regardless of task. vibecheck includes a 4-pass lossless compressor (23 techniques) that cuts file size 25-50%:

- **Pass 1 (Mechanical):** Strip markdown, convert tables, merge bullets. ~10-15%.
- **Pass 2 (Fact-preserving):** Deduplicate facts, compress code examples. ~15-25%.
- **Pass 3 (High-fidelity):** Remove tutorials and coaching text humans need but AI doesn't. ~10-15%.
- **Pass 4 (Telegram):** Full shorthand rewrite for AI-only files. ~15-25% (only with permission).

A 10K-token file compressed to 6K saves $0.044/session. At 10 sessions/day: **$0.44/day ($13/month).**

### Output Suppression

Output tokens cost 5x input ($15 vs $3/MTok on Sonnet). The AI showing full code blocks and diffs you didn't ask for wastes **~$0.047/session.** vibecheck adds: *"No code/diffs unless asked."*

### Cost Monitoring

`/vibecheck monitor` snapshots your session profile and compares against baseline on subsequent runs. Catches regression before it costs money.

---

## Savings Summary

### Interactive tools (Sonnet 4.6)

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

*Individual patterns can co-occur in the same turn — totals reflect per-pattern measurement. Actual aggregate savings: $3.07 → $0.46 (see bottom line).

**Typical wasteful session: $3.07. After vibecheck: $0.46. Savings: 85%.**

- **Light waste** (short sessions, few patterns): 40-55%
- **Moderate waste** (average user): 55-70%
- **Heavy waste** (long sessions, multiple patterns): 70-85%

### Always-on agents

| # | Pattern | Daily waste | Daily savings |
|---|---|---|---|
| 13 | Idle heartbeats | $11.20 | $9.70 |
| 14 | Workspace bloat | $5.76 | $3.76 |
| 15 | Memory accumulation | $3.17 | $2.37 |
| | **Total** | **$20.13/day** | **$15.83/day** |

**Monthly savings for always-on agents: ~$475.**

---

## Supported tools

24+ tools.

- **Full session scan:** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Detection + instruction optimization:** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

All LLMs: Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ more.

macOS, Windows, Linux, iPad via SSH. Python 3.8+, no dependencies.

<details>
<summary>Methodology</summary>

All cost estimates use the reference scenario above. Key assumptions:

- **95% prompt cache hit rate** — typical for rapid coding sessions. Slower sessions will have higher costs.
- **25 productive turns/session** — wasteful sessions add 8-12 extra turns from narration, retries, unchained commands.
- **600 tokens/turn growth** — verbose sessions can hit 1,000-2,000.
- **Effective input rate: $0.435/1M** — blended 95% cached ($0.30) + 5% uncached ($3.00).
- **Context tax rate: $0.30/1M** — cached input rate for permanent context additions.

Estimates are conservative. Real-world savings can exceed projections for users with long sessions, large instruction files, or heavy debugging.
</details>
