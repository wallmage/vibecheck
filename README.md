# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Every turn your AI takes costs money.** Sonnet 4.6: $3/$15 per million tokens (input/output). Opus 4.6: $5/$25 — 1.67x more. Here's what that looks like:

- Your AI says "OK, I'll fix that" before fixing it. That narration turn: **$0.031 wasted.** Five per session: **$0.165 gone.**
- Your conversation hits 40 turns instead of splitting at 20. Extra cost from re-reading all that history: **$0.67 wasted.**
- `git add`, then `git commit`, then `git push` — three turns instead of one chained command: **$0.098 wasted.**

These are 3 of the 15 waste patterns vibecheck catches. Every one explained below with dollar amounts, what goes wrong, and how we fix it.

Works with Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ coding tools. Runs locally — your data stays on your machine.

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

vibecheck reads and edits your instruction file (CLAUDE.md, .cursorrules, etc.). It asks before every change.

## Privacy

Your data doesn't leave your machine. No server, no API, no telemetry. Open source.

## Commands

- `/vibecheck scan` — teaches you what tokens are, scans your sessions, applies fixes
- `/vibecheck explain` — just the lesson, no changes
- `/vibecheck compress` — shrinks your instruction file 25-50%
- `/vibecheck monitor` — weekly comparison, flags regressions

## Before / After

```
                          BEFORE         NOW            CHANGE
Avg turns/session         36.8           25.9           -10.9
Avg context window        128.4K         89.9K          -30%
Wasteful turns            36.7%          8.1%           -28.6%

Avg cost/session          $2.62          $1.35          -$1.27
Monthly spend             $224           $115           -$109
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

I haven't fully benchmarked Codex's dollar value yet, but at the $20 tier, Codex Plus delivers roughly **3x the real usage** of Claude Pro.

Why: ChatGPT conversations (even with the o4 extended thinking model) don't count against your Codex usage quota. You get the full chat product for free on top of coding usage. So $20 Codex ≈ $60 Claude in real usage.

**If you don't plan to buy at least Claude $100 tier, get $20 Codex Plus instead.** You get free deep research, free extended thinking chat, and 3x more coding usage than Claude Pro.

</details>

### Reference scenario

All dollar amounts below use this baseline (Sonnet 4.6):

| Parameter | Value |
|---|---|
| Session length | 25 turns |
| Starting context | 5,000 tokens |
| Growth per turn | ~3,000 tokens |
| Cache hit rate | 90% |
| Mid-session turn cost | $0.038 |
| Efficient session total | $0.96 |

For Opus 4.6, multiply all costs by 1.67x.

---

## The 15 waste patterns

### Tier 1 — The Big 3 (60-70% of waste)

#### 1. Idle Narration

**What it is.** The AI says "OK, I'll fix that" or "Let me read the file first" — then does the actual work next turn. The narration turn did nothing: no tool call, no code, no file read.

**The waste.** Each narration turn costs **$0.031** (context re-read + ~500 tokens of status text). Most sessions have 5 of these: **$0.165/session wasted** — 17% of your bill producing nothing. Over 10 sessions/day: **$1.65/day ($50/month)** on narration alone.

**The fix.** vibecheck adds: *"No turn without tool call. No narration. Think and act in the same turn."* Eliminates narration entirely. **Saves $0.15-0.18/session.**

#### 2. Context Rot

**What it is.** Long conversations get progressively more expensive. Turn 50 re-reads all 49 prior turns. Total session cost grows quadratically with length.

**The waste.** One 40-turn session: **$1.89.** Two 20-turn sessions (same work): **$1.22.** The difference — **$0.67** — buys nothing. At 100 turns: one session costs **$5.62** vs four 25-turn sessions at **$3.84.** That's **$1.78 wasted** from not splitting.

**The fix.** Teaches: *"Use /clear or /compact between unrelated tasks. Start fresh conversations."* **Saves $0.30-0.70/session for users with long-session habits.**

#### 3. Ping-Pong Debugging

**What it is.** Fix, break, retry, break again. Each failed attempt adds error output to context (~4K tokens per cycle), re-read on every future turn.

**The waste.** Three failed cycles: 6 extra turns ($0.252) + 12K tokens of dead errors ($0.036 context tax). **Total: ~$0.29 per episode.** Occurs in ~1/3 of sessions. **Weighted: ~$0.10/session.**

**The fix.** Adds: *"After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix."* **Saves ~$0.20 per episode.**

### Tier 2 — Turn Density (15-20% of waste)

#### 4. Verbose Tool Output

**What it is.** Build/test command dumps 500 lines (~5K tokens) into the conversation. Those tokens get re-read on every future turn.

**The waste.** 5K tokens x 12 remaining turns x $0.30/1M = **$0.018/instance** context tax. Happens 2-3 times/session. Without caching: **$0.180/instance** — 10x worse. **Total: $0.04-0.05/session.**

**The fix.** Adds: *"Pipe build/test output to /tmp/, use --quiet flags, tail -50 max."* **Saves $0.03-0.05/session.**

#### 5. Unchained Commands

**What it is.** `npm install` in one turn, `npm run build` in the next. Two context re-reads when `&&` chains them in one.

**The waste.** Each split: **$0.023.** Typical sessions have 3-4 splits. **Total: $0.07-0.09/session.**

**The fix.** Adds: *"Chain commands with `&&` when safe."* **Saves $0.06-0.08/session.**

#### 6. Codebase Wandering

**What it is.** The AI opens file after file — README, package.json, configs — before doing any work. Five+ consecutive reads before the first edit.

**The waste.** Five unnecessary reads: $0.190 in turns + $0.027 context tax = **$0.217/episode.** Occurs in ~25% of sessions. **Weighted: ~$0.054/session.**

**The fix.** Encourages targeted search (grep/glob first), batching multiple reads per turn. **Saves ~$0.15 per episode.**

#### 7. Unbatched Edits

**What it is.** Edit file A, then B, then C — three turns when one turn with parallel edits would do.

**The waste.** 2 extra turns x $0.038 = **$0.076/instance.** Happens in ~60% of sessions. **Weighted: ~$0.046/session.**

**The fix.** Adds: *"Batch independent tool calls (multiple Reads/Edits per turn)."* **Saves ~$0.04/session.**

### Tier 3 — The Tail (5-10% of waste)

#### 8. File Re-reads

**What it is.** Same file read twice in one session. Content is already in context after the first read.

**The waste.** 1 wasted turn + duplicate content = **$0.043/re-read.** 1-2 per session. **Weighted: ~$0.039/session.**

**The fix.** Adds: *"Content in context after first read. Re-read only if file changed."* **Saves ~$0.03/session.**

#### 9. Sleep/Poll Loops

**What it is.** `sleep 5 && check_status`, repeated 3-5 times. Each poll re-reads the full context.

**The waste.** 4 polls x $0.038 = **$0.152/episode.** Occurs in ~20% of sessions. **Weighted: ~$0.030/session.**

**The fix.** Adds: *"Use --wait flags or run_in_background."* **Saves ~$0.12/episode.**

#### 10. Failed Retries

**What it is.** Command fails, AI runs the exact same command again. Error output now in context twice.

**The waste.** **$0.042/retry.** Occurs in ~30% of sessions. **Weighted: ~$0.013/session.**

**The fix.** Same rule as ping-pong: *"Stop, re-read error, think, single targeted fix."*

#### 11. Schema Lookups

**What it is.** AI looks up its own tool definitions — information it already has. Adds 2K+ tokens to context.

**The waste.** **$0.052/lookup.** Occurs in ~40% of sessions. **Weighted: ~$0.021/session.**

**The fix.** "No turn without tool call" discourages discovery turns. **Saves ~$0.02/session.**

#### 12. Git Ceremony

**What it is.** `git add` → `git status` → `git commit` → `git push`, four turns. `git add -A && git commit -m "msg" && git push` is one.

**The waste.** 3 extra turns + git output = **$0.098/instance.** Happens in ~70% of sessions. **Weighted: ~$0.069/session.**

**The fix.** Adds: *"Chain git commands with `&&`."* **Saves ~$0.06/session.**

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

A 10K-token file compressed to 6K saves $0.057/session. At 10 sessions/day: **$0.57/day ($17/month).**

### Output Suppression

Output tokens cost 5x input ($15 vs $3/MTok on Sonnet). The AI showing full code blocks and diffs you didn't ask for wastes **~$0.047/session.** vibecheck adds: *"No code/diffs unless asked."*

### Cost Monitoring

`/vibecheck monitor` snapshots your session profile and compares against baseline on subsequent runs. Catches regression before it costs money.

---

## Savings Summary

### Interactive tools (Sonnet 4.6)

| # | Pattern | Avg waste/session | Avg saved |
|---|---|---|---|
| 1 | Idle narration | $0.165 | $0.155 |
| 2 | Context rot | $0.150 | $0.120 |
| 3 | Ping-pong debugging | $0.097 | $0.067 |
| 4 | Verbose output | $0.045 | $0.035 |
| 5 | Unchained commands | $0.080 | $0.065 |
| 6 | Codebase wandering | $0.054 | $0.040 |
| 7 | Unbatched edits | $0.046 | $0.038 |
| 8 | File re-reads | $0.039 | $0.030 |
| 9 | Sleep/poll loops | $0.030 | $0.025 |
| 10 | Failed retries | $0.013 | $0.010 |
| 11 | Schema lookups | $0.021 | $0.018 |
| 12 | Git ceremony | $0.069 | $0.058 |
| + | Compression | $0.057 | $0.057 |
| + | Output suppression | $0.047 | $0.038 |
| | **Total** | **$0.913** | **$0.756** |

**Typical wasteful session: $1.87. After vibecheck: $1.11. Savings: 41%.**

- **Light waste** (short sessions, few patterns): 25-35%
- **Moderate waste** (average user): 40-50%
- **Heavy waste** (long sessions, multiple patterns): 50-65%

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

- **90% prompt cache hit rate** — typical for rapid coding sessions. Slower sessions will have higher costs.
- **25 productive turns/session** — wasteful sessions add 8-12 extra turns from narration, retries, unchained commands.
- **3,000 tokens/turn growth** — verbose sessions can hit 4,000-5,000.
- **Effective input rate: $0.57/1M** — blended 90% cached ($0.30) + 10% uncached ($3.00).
- **Context tax rate: $0.30/1M** — cached input rate for permanent context additions.

Estimates are conservative. Real-world savings can exceed projections for users with long sessions, large instruction files, or heavy debugging.
</details>
