# vibecheck — Detailed Specifications

Every AI coding turn re-reads your entire conversation, generates a response, and adds both to context for next time. vibecheck detects 15 waste patterns, compresses your instruction file, and teaches habits that cut your bill. This document explains every mechanism with real dollar amounts.

## Token Pricing

| Model | Input | Output | Cached Input | vs Sonnet |
|---|---|---|---|---|
| Sonnet 4.6 | $3.00/MTok | $15.00/MTok | $0.30/MTok | 1.00x |
| Opus 4.6 | $5.00/MTok | $25.00/MTok | $0.50/MTok | 1.67x |

1 MTok = 1,000,000 tokens. 1 token ~ 4 characters ~ 0.75 words.

Prompt caching cuts input cost 10x for content the API has seen before. Most AI coding tools (Claude Code, Cursor, Codex) use this automatically. Cache TTL is 5 minutes — fast-paced coding sessions get high cache hit rates; slow or sporadic sessions pay more.

**Subscription users:** You don't see API prices directly, but waste burns through your message quota faster. Every wasted turn is one message you can't use for real work. Claude Pro ($20/mo) covers ~$200 in API value. Claude Max ($200/mo) covers ~$4,000.

## How a Turn Costs Money

Every turn:
1. **Input** — the AI re-reads everything: system prompt, your instruction file, all previous messages, all tool output. Cost = total context tokens x input rate.
2. **Output** — the AI generates a response. Cost = response tokens x output rate.

Early turns are cheap (small context). Late turns are expensive (everything that came before is re-read). This is why waste compounds — a wasted turn isn't just that turn's cost, it also makes every future turn more expensive because the wasted content stays in context.

## Reference Scenario

All dollar amounts below use this baseline unless noted:

| Parameter | Value |
|---|---|
| Model | Sonnet 4.6 |
| Session length | 25 productive turns |
| Starting context | 5,000 tokens (system prompt + instruction file) |
| Context growth | ~3,000 tokens/turn |
| Average AI output | 1,000 tokens/turn |
| Prompt cache hit rate | 90% |

**Derived costs:**

| Metric | Value |
|---|---|
| Early turn cost (turn 3) | $0.021 |
| Mid-session turn cost (turn 13) | $0.038 |
| Late turn cost (turn 25) | $0.059 |
| Average turn cost | $0.038 |
| Efficient 25-turn session total | $0.96 |
| Context tax: 1K tokens added permanently (12 remaining turns, cached) | $0.004 |
| Context tax: 1K tokens added permanently (12 remaining turns, uncached) | $0.036 |

For Opus 4.6, multiply all costs by 1.67x.

---

## Tier 1 — The Big 3

These three patterns account for 60-70% of total waste. Fixing just these gives most of the savings.

---

### 1. Idle Narration

**What it is.** The AI says "OK, I'll fix that for you" or "Let me read the file first" — then does the actual work in the next turn. The narration turn produced zero useful output: no tool call, no code change, no file read. It was pure status update.

**The waste.** A narration turn re-reads the full context ($0.023 input at mid-session) and generates ~500 tokens of status text ($0.008 output). Direct cost: **$0.031 per narration turn.** The narration text also enters context permanently — 500 tokens re-read on every future turn adds $0.002 in context tax.

Most sessions without instruction file rules have 4-6 narration turns. At 5 narration turns: **$0.155 direct + $0.010 context tax = $0.165/session wasted.** That's 17% of session cost, producing nothing.

Over 10 sessions/day: **$1.65/day ($50/month)** on narration alone.

**The vibecheck fix.** Adds to instruction file: *"No turn without tool call. No narration/status/'now I'll...'. Think and act in the same turn."* This eliminates narration turns entirely. The AI thinks and acts in one turn instead of two. **Saves $0.15-0.18/session (15-19%).**

---

### 2. Context Rot

**What it is.** Long conversations get progressively more expensive. Turn 50 re-reads all 49 prior turns. The cost per turn grows linearly with conversation length, but total session cost grows quadratically. Two 20-turn sessions cost significantly less than one 40-turn session for the same total work.

**The waste.** One 40-turn session costs **$1.89** on Sonnet 4.6. Two 20-turn sessions doing the same work cost **$1.22.** The extra cost — **$0.67 per oversized session** — buys nothing. At 100 turns (common for long debugging sessions), the gap is extreme: one session costs **$5.62** vs four 25-turn sessions at **$3.84.** That's **$1.78 wasted** just from not splitting.

Heavy users who routinely run 40+ turn sessions: **$0.50-0.70 wasted per session.**

**The vibecheck fix.** Teaches as a user habit: *"Use /clear or /compact between unrelated tasks. Start a fresh conversation for new tasks."* The instruction file reminds the AI to suggest session clearing when context grows large. **Saves $0.30-0.70/session for users with long-session habits.**

---

### 3. Ping-Pong Debugging

**What it is.** The AI applies a fix, it breaks something, the AI tries again, it breaks differently, the AI tries again. Each attempt adds the full error output and failed code to context, which then gets re-read on every subsequent turn. Three failed cycles can add 12,000+ tokens of dead error text.

**The waste.** Each debug cycle = 2 extra turns (fix attempt + error check) and ~4,000 tokens of error text entering context. Three failed cycles: 6 extra turns x $0.042 avg = **$0.252** in turn costs, plus 12,000 tokens x 10 remaining turns x $0.30/1M = **$0.036** in context tax. **Total: ~$0.29 per ping-pong episode.**

Occurs in roughly 1 in 3 sessions. Weighted average: **~$0.10/session.**

**The vibecheck fix.** Adds: *"After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix."* Cuts 3-cycle loops to 1 effective attempt. **Saves ~$0.20 per session when ping-pong occurs (~$0.07/session average).**

---

## Tier 2 — Turn Density

These patterns waste turns through inefficient tool use. Each instance is small, but they occur frequently and add up.

---

### 4. Verbose Tool Output

**What it is.** The AI runs a build or test command that dumps 500 lines (~5,000 tokens) of output directly into the conversation. The command itself was necessary — the waste is in how the output enters context. Those 5,000 tokens get re-read on every future turn.

**The waste.** 5,000 tokens in context x 12 remaining turns x $0.30/1M = **$0.018 per instance** in context tax. Happens 2-3 times per session (builds, tests, installs). **Total: $0.036-0.054/session.** In uncached scenarios (stale cache, long gaps between turns): 5,000 x 12 x $3.00/1M = **$0.180 per instance** — 10x worse.

**The vibecheck fix.** Adds: *"Pipe build/test/install to /tmp/, use --quiet flags, tail -50 max."* Build output goes to a temp file; only the relevant tail enters context. **Saves $0.03-0.05/session (cached), up to $0.36/session (uncached).**

---

### 5. Unchained Commands

**What it is.** The AI runs `npm install` in one turn, waits for the result, then runs `npm run build` in the next turn. Two full context re-reads for something `npm install && npm run build` handles in one turn.

**The waste.** Each unnecessary turn split costs one extra context re-read: **$0.023 per split** at mid-session (input cost only — output is minimal for command runs). Typical sessions have 3-4 unchained sequences. **Total: $0.069-0.092/session.**

**The vibecheck fix.** Adds: *"Chain commands with `&&` when safe."* **Saves $0.06-0.08/session.**

---

### 6. Codebase Wandering

**What it is.** The AI doesn't know where things are, so it opens file after file — README, package.json, config files, source files — looking around before doing any actual work. Five or more consecutive read turns before the first edit.

**The waste.** Each exploratory read = 1 turn ($0.038) + ~1,500 tokens entering context ($0.005 tax). Five unnecessary reads: **$0.190 in turns + $0.027 tax = $0.217** per wandering episode. Occurs in ~25% of sessions (more in unfamiliar codebases). **Weighted: ~$0.054/session.**

**The vibecheck fix.** Instruction file rules encourage targeted search (grep/glob first), batching multiple file reads into one turn, and skipping files not relevant to the task. **Saves ~$0.15 per session when wandering occurs (~$0.04/session average).**

---

### 7. Unbatched Edits

**What it is.** The AI edits file A in one turn, file B in the next, file C in the third. Three separate turns — three full context re-reads — when one turn with three parallel edit calls would do.

**The waste.** 2 extra turns x $0.038 = **$0.076 per instance.** Happens in ~60% of sessions. **Weighted: ~$0.046/session.**

**The vibecheck fix.** Adds: *"Batch independent tool calls (multiple Reads/Edits/files per turn)."* **Saves ~$0.04/session.**

---

## Tier 3 — The Tail

Individually small, but easy mechanical fixes. Zero risk, free money.

---

### 8. File Re-reads

**What it is.** The AI reads the same file twice in one session. After the first read, the file content is already in context. The second read adds a duplicate copy and costs a full turn.

**The waste.** 1 wasted turn ($0.038) + ~1,500 duplicate tokens in context ($0.005 tax) = **$0.043 per re-read.** Happens 1-2 times in ~60% of sessions. **Weighted: ~$0.039/session.**

**The vibecheck fix.** Adds: *"File re-reads banned — content in context after first read. Re-read only if the file changed or accuracy depends on it."* **Saves ~$0.03/session.**

---

### 9. Sleep/Poll Loops

**What it is.** The AI runs a long command, then polls for completion: `sleep 5 && check_status`, repeated 3-5 times. Each poll is a full turn with a full context re-read, just to check if something finished.

**The waste.** 4 poll turns x $0.038 = **$0.152 per polling episode.** Occurs in ~20% of sessions (builds, deployments, CI). **Weighted: ~$0.030/session.**

**The vibecheck fix.** Adds: *"Use --wait flags or run_in_background. Don't poll."* **Saves ~$0.12 per session when polling occurs (~$0.025/session average).**

---

### 10. Failed Retries

**What it is.** A command fails. The AI runs the exact same command again hoping for a different result. The error output is now in context twice. Neither attempt fixed the underlying issue.

**The waste.** 1 wasted turn ($0.038) + ~1,000 tokens of duplicate error in context ($0.004 tax) = **$0.042 per retry.** Occurs in ~30% of sessions. **Weighted: ~$0.013/session.**

**The vibecheck fix.** Covered by the same rule as ping-pong debugging: *"After 2 failed fixes, stop, re-read error, think, single targeted fix."* **Saves ~$0.03 per session when it occurs.**

---

### 11. Schema Lookups

**What it is.** The AI requests its own tool definitions at session start — information it already has baked in. The schema response adds 2,000+ tokens to context that get re-read for the entire session.

**The waste.** 1 wasted turn ($0.038) + 2,000 tokens x 24 remaining turns x $0.30/1M = $0.014 tax = **$0.052 per lookup.** Occurs in ~40% of sessions. **Weighted: ~$0.021/session.**

**The vibecheck fix.** Instruction file rules ("no turn without tool call") discourage unnecessary discovery turns. Newer models are better about this. **Saves ~$0.02/session.**

---

### 12. Git Ceremony

**What it is.** `git add` in one turn. `git status` in the next. `git commit` in another. `git push` in a fourth. Four separate turns — four full context re-reads — when `git add -A && git commit -m "msg" && git push` is one turn.

**The waste.** 3 extra turns x $0.031 (minimal output) = **$0.093 per ceremony.** Plus ~1,500 tokens of git output permanently in context ($0.005 tax). **Total: ~$0.098 per instance.** Happens in ~70% of sessions. **Weighted: ~$0.069/session.**

**The vibecheck fix.** Adds: *"Chain git commands with `&&`."* **Saves ~$0.06/session.**

---

## Tier 4 — Always-On Agents

For tools like OpenClaw that run 24/7. Different cost model: cost per wake-up x wakes per day. These can dominate your bill.

---

### 13. Idle Heartbeats

**What it is.** The agent wakes up every 5 minutes to check if anything needs doing. Each wake-up re-reads the full workspace (SOUL.md, memory, history). 288 wake-ups per day. About 97% find nothing to do.

**The waste.** Each idle wake costs **$0.02-0.08** depending on workspace size (Sonnet 4.6). At 280 idle wakes/day x $0.04 average = **$11.20/day wasted on checking nothing.** That's **$336/month** in idle heartbeats alone.

**The vibecheck fix.** Adds to agent config: *"Heartbeat frequency: 30min minimum for idle checks. Skip wake-up if no triggers/notifications."* Reduces from 288 to ~48 wakes/day, most of which are triggered (actual work). **Saves $8-10/day ($240-300/month).**

---

### 14. Workspace File Bloat

**What it is.** SOUL.md + AGENTS.md + USER.md and other personality/config files get injected into every wake-up. Typical always-on setup: 35,000 tokens of personality and coaching text. The AI only needs the behavioral rules — the tutorials, examples, and motivational text are for human readers.

**The waste.** 35,000 tokens x $0.57/1M effective rate = **$0.020 per wake.** At 288 wakes/day: **$5.76/day ($173/month)** just from reading personality files repeatedly.

**The vibecheck fix.** Compresses workspace files: removes verbose personality text, coaching paragraphs, and human-only scaffolding while preserving all behavioral rules. Typical reduction: 35K to 12-15K tokens. **Saves $3-4/day ($90-120/month).**

---

### 15. Memory Accumulation

**What it is.** The agent's memory files grow without pruning. After 100+ entries, every wake-up re-reads months of accumulated context that's mostly irrelevant to the current task.

**The waste.** 20,000 tokens of stale memory x $0.57/1M = **$0.011 per wake.** At 288 wakes/day: **$3.17/day ($95/month)** re-reading old memory entries.

**The vibecheck fix.** Adds: *"Prune session history: archive after 50 turns, summarize, start fresh."* Keeps memory focused on recent and relevant entries. **Saves $2-3/day ($60-90/month).**

---

## Optimization Tools

Beyond the 15 waste patterns, vibecheck includes three optimization tools that reduce cost independently of specific patterns.

---

### 16. Instruction File Compression

**What it is.** Your CLAUDE.md, .cursorrules, or SOUL.md is read on every single turn. It's a fixed tax — you pay it whether the turn does useful work or not. vibecheck includes a 4-pass lossless compressor with 23 techniques that reduces file size 25-50% without losing any behavioral rules.

**The waste.** A 3,000-token instruction file costs **$0.043/session** in re-reads (25 turns x $0.30/1M cached + small uncached portion). A 10,000-token file: **$0.143/session.** A bloated 25,000-token SOUL.md: **$0.356/session.** These costs are invisible — you pay them on every session regardless of task.

At 10 sessions/day, a 10K file costs **$1.43/day ($43/month)** just to exist.

**The vibecheck fix.** 4-pass compression:
- **Pass 1 (Mechanical):** Strip markdown formatting, convert tables, merge bullet lists. ~10-15% reduction.
- **Pass 2 (Fact-preserving):** Deduplicate repeated facts, compress code examples to inline references. ~15-25% additional.
- **Pass 3 (High-fidelity):** Remove tutorials, coaching text, validation tables that only humans need. ~10-15% additional.
- **Pass 4 (Telegram):** Full shorthand rewrite for AI-only documents. ~15-25% additional (only with explicit permission).

A 10,000-token file compressed to 6,000 tokens saves $0.057/session. **At 10 sessions/day: $0.57/day ($17/month).**

---

### 17. Output Suppression

**What it is.** The AI shows full code blocks, complete diffs, or explains every change in detail — even when you didn't ask. Output tokens cost 5x input tokens ($15 vs $3/MTok on Sonnet). Unnecessary output also enters context and gets re-read on every future turn.

**The waste.** 5 unnecessary code displays per session x ~500 tokens each x $15/1M = **$0.038 in output cost.** Plus 2,500 tokens of unnecessary code in context x 12 remaining turns x $0.30/1M = **$0.009 context tax.** Total: **~$0.047/session.**

**The vibecheck fix.** Adds: *"User sees zero code/diffs unless asked."* The AI confirms changes with a short sentence instead of displaying the full code. **Saves ~$0.04/session.**

---

### 18. Cost Monitoring

**What it is.** vibecheck snapshots your session cost profile after each scan. On subsequent runs, it compares against the baseline and shows actual vs projected savings with clear pass/fail indicators.

**The value.** Without monitoring, optimization drifts. New team members, instruction file edits, changed habits — waste creeps back. The `/vibecheck monitor` command catches regression before it costs meaningful money. This mechanism doesn't directly save money — it protects the savings from all other mechanisms.

---

## Savings Summary

### Interactive tools (Claude Code, Cursor, Codex, etc.)

Estimated per-session savings on Sonnet 4.6. Weighted by frequency of occurrence.

| # | Mechanism | Avg waste/session | Avg saved/session |
|---|---|---|---|
| 1 | Idle narration | $0.165 | $0.155 |
| 2 | Context rot | $0.150 | $0.120 |
| 3 | Ping-pong debugging | $0.097 | $0.067 |
| 4 | Verbose tool output | $0.045 | $0.035 |
| 5 | Unchained commands | $0.080 | $0.065 |
| 6 | Codebase wandering | $0.054 | $0.040 |
| 7 | Unbatched edits | $0.046 | $0.038 |
| 8 | File re-reads | $0.039 | $0.030 |
| 9 | Sleep/poll loops | $0.030 | $0.025 |
| 10 | Failed retries | $0.013 | $0.010 |
| 11 | Schema lookups | $0.021 | $0.018 |
| 12 | Git ceremony | $0.069 | $0.058 |
| 16 | Instruction file compression | $0.057 | $0.057 |
| 17 | Output suppression | $0.047 | $0.038 |
| | **Total** | **$0.913** | **$0.756** |

**Typical session: $0.96 (efficient baseline) + $0.91 (waste) = $1.87. After vibecheck: $1.11. Savings: 41%.**

Savings vary by usage pattern:
- **Light waste** (short sessions, few patterns): 25-35%
- **Moderate waste** (average user): 40-50%
- **Heavy waste** (long sessions, multiple patterns): 50-65%

The "50%+" headline applies to moderate-to-heavy users — the majority of vibecheck's target audience.

### Always-on agents (OpenClaw, etc.)

| # | Mechanism | Daily waste | Daily savings |
|---|---|---|---|
| 13 | Idle heartbeats | $11.20 | $9.70 |
| 14 | Workspace file bloat | $5.76 | $3.76 |
| 15 | Memory accumulation | $3.17 | $2.37 |
| | **Total** | **$20.13/day** | **$15.83/day** |

**Monthly savings for always-on agents: ~$475/month.**

---

## Supported Platforms

### AI Coding Tools (24+)

**Full session scan** (log analysis + waste detection + instruction file optimization):
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Detection + instruction file optimization** (scan support rolling out):
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

### LLMs

All models supported. Token costs differ by model — vibecheck adapts its waste estimates to the model in use:

Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, and 40+ more.

### Operating Systems

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, no external dependencies.

---

## Methodology

All cost estimates use the reference scenario defined at the top of this document. Key assumptions:

- **90% prompt cache hit rate** — typical for rapid coding sessions. Slower sessions (2+ minutes between turns) will have lower cache rates and higher per-turn costs. All waste amounts scale up proportionally with lower cache rates.
- **25 productive turns per session** — the baseline efficient session. Wasteful sessions add 8-12 extra turns from narration, retries, and unchained commands.
- **3,000 tokens/turn context growth** — average across tool output, AI responses, and user messages. Verbose sessions (build output, large files) can hit 4,000-5,000.
- **Effective input rate: $0.57/1M** — blended rate of 90% cached ($0.30) + 10% uncached ($3.00) input. Used for full-turn cost calculations.
- **Context tax rate: $0.30/1M** — cached input rate. Used for marginal cost of adding tokens to context permanently, since new content is cached after its first appearance.

All estimates are conservative. Real-world savings can exceed the projections, especially for users with long sessions, large instruction files, or heavy debugging workflows.
