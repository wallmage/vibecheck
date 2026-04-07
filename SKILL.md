# vibecheck

Vibe coding is fun. Vibe coding is expensive. Let's check.

Universal cost optimizer for ALL AI coding tools. Auto-detects your tool(s), scans all logs across all models and projects, teaches you what you're paying for, then cuts your waste.

Supports 24+ tools: Claude Code, Cursor, Codex, Windsurf, Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, GitHub Copilot, OpenClaw, CodeBuddy, WorkBuddy, TRAE, Qoder, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax, Augment Code.

Works on macOS, Windows, Linux. Works from iPad/mobile via SSH.

## Language Rule

Detect system language via explain.py output (`language` field). Default all responses to that language. If user writes in a different language, switch to match — output language = input language, always. All lesson text, questions, reports: in their language.

## Commands

### `/vibecheck` or `/vibecheck scan`

Full diagnostic with interactive cost education. Most users don't understand API pricing — teach first, optimize second.

**Step 0: Auto-detect their tool (silent)**
```bash
python3 SKILL_DIR/scripts/detect_tool.py [optional_project_dir] > /tmp/claude_tool_detect.json
```
Read the JSON. This tells you:
- Which AI coding tool they use (Claude Code, Cursor, Codex, Windsurf, Cline, Aider, Gemini CLI, etc.)
- Where their logs are
- What their instruction file is called (CLAUDE.md, AGENTS.md, .cursorrules, etc.)
- Whether logs are parseable

If `needs_manual_input` is true: "I couldn't auto-detect your AI coding tool. Can you point me to your project folder? Or tell me which tool you use (Cursor, Claude Code, Codex, etc.)?"

If `can_analyze` is false: explain that their tool's log format is limited, but the waste education and instruction file optimization still apply. Skip the data-driven sections and use industry averages instead.

Use `primary_tool_name` in all user-facing text. Never say "Claude Code" if they use Cursor. Adapt:
- Instruction file name: CLAUDE.md / AGENTS.md / .cursorrules / .windsurfrules / etc.
- "Turn" → "message" or "request" for tools where "turn" isn't natural
- /clear → tool-specific equivalent if known

**Step 1: Discover + Analyze (silent)**

```bash
python3 SKILL_DIR/scripts/find_logs.py 14 > /tmp/claude_sessions.json
```

Read the JSON. Two possible outcomes:

**A) Logs found** (`total_sessions > 0`): Proceed to analyze:
```bash
python3 SKILL_DIR/scripts/analyze_sessions.py /tmp/claude_sessions.json > /tmp/claude_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/claude_analysis.json > /tmp/claude_lesson.json
```
Do NOT show raw output. Read the lesson JSON for all following steps.

**B) No logs found** (`"error": "no_logs"`): The script returns `setup_command` and `platform` (mac/windows/linux). This typically happens because AI apps like Cowork, Cursor, Windsurf etc. run inside a secure sandbox — they can see your project files, but not your chat history. It's like a guest who can see your living room but not your bedroom — your conversations are in the private part.

**Your job: make it easy.** Tell the user (adapt to their language):

> "I can teach you about AI costs right now — but for a personalized scan with YOUR real numbers, I need your chat history. It's stored in a private folder I can't peek into from here — like a guest who can see your living room but not your bedroom. No worries, it takes 5 seconds. Open your regular terminal app (Terminal on Mac, Command Prompt on Windows) and paste this one line:"

Construct the command using SKILL_DIR:
```
python3 SKILL_DIR/scripts/export_logs.py
```

This copies ONLY the last 14 days of logs (~20-50 MB, not the full history). It prints "Done!" when finished. Works on Mac, Windows, and Linux — same command.

If you can't determine SKILL_DIR, use the `fallback_command` from the JSON output instead.

Then say:

> "Done? Great — now point me to that folder (it's in your home folder, called vibecheck-logs)."

If the environment supports folder mounting (Cowork, Cursor, etc.), request to mount `~/vibecheck-logs`. If not, ask the user to provide the path.

Then re-run: `python3 SKILL_DIR/scripts/find_logs.py 14 ~/vibecheck-logs > /tmp/claude_sessions.json`

The script auto-checks these folders (no manual path needed if they used the default destination):
`~/vibecheck-logs`, `~/claude-logs`, `~/Desktop/vibecheck-logs`, `~/Documents/vibecheck-logs`, `~/Developer/vibecheck-logs`

**If user doesn't want to copy:** That's fine — say "No problem! I'll teach you the concepts using typical numbers instead. You can always come back later for the personalized scan." Continue with industry averages.

Note: find_logs.py currently only parses Claude Code JSONL. For other tools, the lesson will use industry averages and explain the patterns generically. Log parsing for Cursor (SQLite), Cline (JSON), etc. is planned.

**Step 2: Lesson 1 — "What are you actually paying for?"**

Use their detected tool name throughout. Explain in 3-5 short paragraphs. Zero jargon — imagine explaining to a marketer friend:

1. **Subscription vs reality**: "You pay $X/month for [Tool]. But behind the scenes, every message you send has a real cost in 'tokens' — tiny units the AI reads and writes. Your subscription covers a certain amount of these tokens. Think of it like a phone plan: you pay a flat rate, but every call uses minutes."

   Show their tier: Claude ($20→~$200 value, $100→~$1,000, $200→~$4,000). Cursor ($20→~200 premium requests). GPT ($20→~$100 value, $200→~$3,000). If unknown, skip tiers and say "Your subscription covers a certain amount of AI usage per month."

2. **What's a token?**: "A token is roughly one word. This sentence is about 12 tokens. Every time you send a message, the AI reads ALL your previous messages (costs tokens) and writes a response (costs more tokens). The reading part is cheap per-word, but the AI re-reads EVERYTHING every single time."

3. **Your usage** (if data available): "In the last 14 days, you had [N] conversations using [Model]. Your total usage was worth $[X], about $[Y]/day."
   (If no data): "The average vibe coder spends $5-15/day in actual token value. Heavy users can hit $20-40/day without realizing it."

End with: **"Make sense so far? Ask me anything. When you're ready, I'll show you where the money actually goes — it's not where you'd think."**

WAIT for user response. Do not continue until they reply.

**Step 3: Lesson 2 — "Where your money actually goes"**

If you have their data, use `worst_day`. If not, use industry averages and explain generically.

1. **The bill**: "Your busiest day was [date]: $[X] across [N] conversations."
   (Generic): "A typical heavy day of AI coding costs $10-30."

2. **The 3 things you're paying for** (explain like a phone bill):
   - **Re-reading old messages** (cache read, 50-65% of cost): "Every time you send a new message, the AI re-reads your ENTIRE conversation history. Imagine if every time you texted a friend, your phone re-read all your previous texts out loud before sending. That's what's happening — and you're paying for it. This was [X]% of your bill."
   - **New stuff entering the conversation** (cache create, 15-25%): "When the AI reads a file or runs a command, that output enters the conversation. It costs a bit more than re-reading because it's being 'memorized' for the first time."
   - **AI's actual responses** (output, 10-15%): "The code the AI writes, the explanations. This is the actual work you're paying for — and it's the SMALLEST part of your bill."

3. **The punchline**: "The AI spends most of your money RE-READING, not THINKING. The cost of one unnecessary message isn't just that message — it's the cost of re-reading everything that came before it. Message #50 in a conversation costs roughly 50x what message #1 costs."

End with: **"This is why waste adds up so fast. Want to see the specific things wasting your money? I found [N] patterns."**

WAIT for user response.

**Step 4: Lesson 3 — "Your top money wasters"**

Use `top3_waste` if data available. Use `waste_descriptions` from lesson JSON for plain-language explanations and analogies. Present each pattern with:
1. What it is (one sentence, no jargon)
2. The analogy (from waste_descriptions)
3. Their cost (if data available)

Key patterns explained for non-technical users:
- **idle_narration**: "The AI said 'OK, now I'll fix that for you' — then actually fixed it in the NEXT message. That 'OK now I'll' message did nothing but cost you money. Like a chef announcing 'now I'll crack the egg' before cracking the egg."
- **context_rot**: "Your conversation went on for 60+ messages without starting fresh. Each new message got more expensive because the AI re-read all 59 previous messages. Like a meeting where everyone re-reads all previous meeting notes before speaking."
- **verbose_output**: "The AI ran a command that spit out 500 lines of technical output. That output stayed in the conversation and got re-read on EVERY future message. Like printing a 500-page report and carrying it in your backpack all day."
- **codebase_wandering**: "The AI didn't know where things were, so it opened file after file looking around — 8 files before actually doing anything. Like a new employee opening every drawer looking for a stapler."
- **pingpong_debugging**: "The AI tried to fix something, broke it differently, tried again, broke it again... each attempt re-read the entire conversation including all the failed attempts."
- **chainable_bash**: "The AI ran one command, waited for your response, then ran another. It could have run both at once. Like making two separate trips to the grocery store."
- **unbatched_edits**: "The AI edited three different files in three separate messages instead of all at once."

Show total: "These patterns cost you $[X] per conversation. At your pace, that's $[Z]/month of pure waste."
(Generic): "Most vibe coders waste 30-50% of their AI spending on these patterns."

End with: **"The fix is simple — one paragraph added to your [instruction_file_name] that tells the AI to stop doing these things. Same work gets done, fewer wasted messages. Takes 3 minutes. Want me to set it up?"**

WAIT for user response.

**Step 5: Full Report + Fixes**

NOW run the standard report (if data available):
```bash
python3 SKILL_DIR/scripts/report.py /tmp/claude_analysis.json /path/to/instruction_file
```
Show the report. Then apply fixes to their instruction file (CLAUDE.md / AGENTS.md / .cursorrules / etc.):

- **SAFE fixes** (narration, verbose output, context rot, bash chaining, polling, git ceremony): "These are 100% safe — they change HOW the AI works, not WHAT it does. Apply?" If yes, add the cost rules block to their instruction file.
- **REVIEW fixes** (wandering, re-reads, edit batching, failed tools, ping-pong): Show each proposed line, ask per-item approval.
- **Instruction file compression**: Show the scan result. If yes, run `/vibecheck compress`.

Adapt the fix block to the tool's instruction format:
- CLAUDE.md: markdown paragraphs
- AGENTS.md: markdown paragraphs (same format)
- SOUL.md: add to personality/rules section
- .cursorrules / .windsurfrules / .clinerules: plain text rules, one per line
- .trae/rules / .qoder/rules / .lingma/rules: plain text rules
- Others: markdown paragraphs (safe default)

**Step 6: Before/After Comparison**

After applying fixes:
```bash
python3 SKILL_DIR/scripts/compare.py /tmp/claude_analysis.json
```

The script auto-detects previous snapshots from `~/.vibecheck/snapshots/`. No manual path needed.

**First run (no previous snapshot):** Shows current operational metrics + projected savings:
```
                              NOW            PROJECTED      SAVINGS
  Operational:
  Avg turns/session           36.8           25.9           -10.9
  Avg context window          128.4K         89.9K          -30%
  Wasteful turns              36.7%          7.3%           -29.4%

  Cost:
  Avg cost/session            $2.62          $1.35          $1.27 (49%)
  Monthly spend               $224           $115           $109
```

**Subsequent runs (previous snapshot found):** Shows actual before/after delta:
```
                              BEFORE         NOW            CHANGE
  Operational:
  Avg turns/session           36.8           25.9           -10.9 ✅
  Avg sub-agents/session      3.2            2.9            -0.3 ✅
  Avg context window          128.4K         89.9K          -30% ✅
  Wasteful turns              36.7%          8.1%           -28.6% ✅

  Cost:
  Avg cost/session            $2.62          $1.35          -$1.27 ✅
  Waste %                     49.0%          12.3%          -36.7% ✅

  Per-pattern:
    idle_narration             $0.412 → $0.031  (✅)
    context_rot                $0.380 → $0.092  (✅)
    ...
```

Snapshots persist in `~/.vibecheck/snapshots/` — survives reboots, /tmp clears, new sessions. Each scan adds a new snapshot; history grows over time.

Present the comparison to the user in plain language: "Last time you averaged 36.8 turns per session at $2.62. Now you're at 25.9 turns at $1.35 — that's 49% less waste."

End with: **"Run `/vibecheck scan` again in 1-2 weeks to see your actual savings. The optimizer auto-compares against today's baseline."**

If multi-tool detected (e.g., Claude Code + Codex + Gemini CLI), report cross-tool:
- "You use 3 tools. Claude Code accounts for 90% of your spend ($X), Codex for 8% ($Y)..."
- Per-tool waste percentage
- "Your most cost-efficient tool is [X]. Consider routing more work there."

### `/vibecheck explain`

Run ONLY the interactive lessons (Steps 1-4) without the full report or fixes. For users who just want to understand their bill.

### `/vibecheck compress`

Compress CLAUDE.md to reduce per-turn context tax.

**Step 1: Measure**
```bash
cp CLAUDE.md CLAUDE.md.backup
python3 SKILL_DIR/scripts/measure.py CLAUDE.md
```

**Step 2: Pass 1 — Strip markdown (automatic, lossless)**
```bash
python3 SKILL_DIR/scripts/strip_markdown.py CLAUDE.md CLAUDE.working.md
```
Apply automatically. Report reduction.

**Step 3: Pass 2 — Creative compression (needs approval)**
Read CLAUDE.md. Find: deduplication, code block compression, verbose rationale, repeated paths. Propose numbered list with word savings. Wait for per-item approval.

**Step 4: Pass 3 — Remove human-only content (needs approval)**
Find: installation guides, coaching, verbose WHY explanations. Propose by category. Wait for approval.

**Step 5: Pass 4 — Telegram mode (optional)**
Only with explicit permission. Rewrite in shorthand fragments: drop articles, bridge phrases, implied subjects. AI-readable, not human-readable.

**Step 6: Final report**
```bash
python3 SKILL_DIR/scripts/measure.py CLAUDE.md.backup CLAUDE.md
```

### `/vibecheck monitor`

Weekly comparison — current vs previous week.

```bash
python3 SKILL_DIR/scripts/find_logs.py 14 > /tmp/claude_sessions.json
python3 SKILL_DIR/scripts/analyze_sessions.py /tmp/claude_sessions.json > /tmp/claude_analysis.json
python3 SKILL_DIR/scripts/monitor.py /tmp/claude_analysis.json
```

Shows week-over-week delta for: avg cost, waste %, idle turns, total spend. Flags regressions with alerts.

**To run automatically:** Use Claude Desktop scheduled tasks or a system cron:
```bash
# cron (runs every Monday 9am)
0 9 * * 1 cd /path/to/project && python3 /path/to/scripts/find_logs.py 14 > /tmp/claude_sessions.json && python3 /path/to/scripts/analyze_sessions.py /tmp/claude_sessions.json > /tmp/claude_analysis.json && python3 /path/to/scripts/monitor.py /tmp/claude_analysis.json > /tmp/claude_weekly_report.txt

# Or via Claude Desktop: create a scheduled task that runs /vibecheck monitor weekly
```

## CLAUDE.md Rules

- Trigger patterns: preserve exactly
- Shell commands/paths: keep verbatim
- Migration tables: compress format, preserve every row
- Never reorder sections
- When in doubt, keep more

## The 15 Waste Patterns

### Tier 1 — The Big 3 (70-80% of waste)

1. **Idle narration** (30-40%): AI says "Now I'll…" instead of doing it. Fix: "No turn without tool call."

2. **Context rot** (15-25%): Sessions run 40-80+ turns without clearing. Late turns cost 3-5x early turns. Fix: "Clear/compact between tasks."

3. **Ping-pong debugging** (10-20%): Edit→error→re-edit→error. Each cycle carries full context. Fix: "After 2 failed fixes, stop, re-read error, single targeted fix."

### Tier 2 — The Mechanics (15-20%)

4. **Verbose tool output** (5-10%): Build logs, npm output, test results flooding context. Re-read on every future turn. Fix: "Pipe to /tmp/. Use --quiet. Tail last 50 lines."

5. **Unchained commands** (5-10%): Consecutive solo command turns. Fix: "Chain with &&."

6. **Codebase wandering** (5-10%): 5+ consecutive read/search turns before acting. Fix: "Project map in instruction file. Max 3 reads before first edit."

7. **Unbatched edits** (3-5%): Sequential single-edit turns. Fix: "Batch edits into one turn."

### Tier 3 — The Tail (5-10%)

8. **File re-reads** (2-4%): Same file read 2+ times per session. Fix: "Already in context after first read."

9. **Sleep/poll loops** (2-4%): Waiting with sleep+check. Fix: "--wait flags or run_in_background."

10. **Failed retries** (2-4%): Broken command + retry. Fix: Project-specific guardrails.

11. **Schema lookups** (1-3%): Looking up tools AI already knows. Fix: "Call known tools directly."

12. **Git ceremony** (1-2%): Consecutive git-only turns. Fix: "Chain git commands with &&."

### Tier 4 — Always-On Agents (OpenClaw, etc.)

These apply to agents that run 24/7 with heartbeat/cron schedules:

13. **Idle heartbeats** (20-40% of always-on cost): Agent wakes every 5min, re-reads SOUL.md + full memory, finds nothing to do. A no-op heartbeat still costs $0.01-0.10. Fix: "Reduce frequency to 30min+. Skip wake if no triggers."

14. **Workspace file bloat** (10-20% of always-on cost): SOUL.md + AGENTS.md + USER.md injected into every wake-up. Typical setup = 35K tokens re-read per message. Fix: "Compress personality files. Remove verbose text AI doesn't need."

15. **Memory accumulation** (10-15% of always-on cost): Session JSONL grows without pruning. After 100+ messages, every new message re-reads everything. Fix: "Prune sessions. Archive after 50 turns. Use compact/summary."

## The Fix Block

When applying, add near top of instruction file. Pick relevant lines based on scan results. Adapt format to the tool (.cursorrules = one rule per line, SOUL.md = personality section, etc.):

**For interactive tools (Claude Code, Cursor, Codex, etc.):**
```
**Cost rules:** Every turn = context tax. No turn without tool call. No narration/status/"now I'll…". Think → act same turn. Batch independent tool calls (multiple Reads/Edits/files per turn). Chain commands with `&&`. File re-reads banned. User sees zero code/diffs unless asked.
Verbose output: pipe build/test/install to /tmp/, use --quiet flags, tail -50 max. After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix. Clear/compact between unrelated tasks — never exceed ~20 turns without clearing. Max 3 file reads before first Edit.
```

**For always-on agents (OpenClaw, etc.) — add to SOUL.md or AGENTS.md:**
```
**Efficiency rules:** Heartbeat frequency: 30min minimum for idle checks. Skip wake-up if no triggers/notifications. Compress workspace files — remove verbose personality text, keep behavioral rules. Prune session history: archive after 50 turns, summarize, start fresh. Pipe all command output to files, never inline. No status messages between actions.
```

## Supported Models

Claude: Opus, Sonnet, Haiku
OpenAI: GPT-4o, GPT-4o-mini, GPT-4.1, GPT-4.1-mini, o1, o3, o3-mini, o4-mini
Google: Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash
DeepSeek: V3, R1

Model auto-detected from session logs. Unknown models default to Sonnet pricing.

**Non-Claude models in lessons**: When explain.py detects a non-Claude provider, the lesson adapts:
- OpenAI: explain that GPT uses different caching ("Prompt Caching" — 50% discount for repeated prefixes, no creation surcharge). Show their specific $/MTok rates.
- Google: explain Gemini's context caching (25% of input price for cache reads, charged per-hour for storage).
- DeepSeek: explain that DeepSeek V3/R1 have the lowest per-token costs but cache read discount is smaller (10-14%).
- Unknown models: use WebSearch to look up current pricing, then explain using found rates.

The lesson always explains in terms the user understands: "You're using [Model]. Here's how [Provider] charges you..."

## New: Platform Detection

Auto-detects your dev stack from session logs (file types, bash commands, tool calls):
- **iOS/macOS:** Swift, Xcode, SwiftPM, simulators
- **Android:** Kotlin/Java, Gradle, ADB, emulators
- **Web frontend:** React/Vue/Svelte, npm/yarn, Vite/Webpack
- **Backend:** Go/Rust/Ruby/PHP, Docker, Kubernetes
- **Python:** pytest, pip/poetry, Django/FastAPI
- **DevOps:** Terraform, kubectl, Helm, AWS/GCP CLI

Each platform gets tailored recommendations (e.g., iOS: "don't explore node_modules" is irrelevant; web: "simulator boot" is irrelevant).

## New: Reviewer Fleet ROI

If you use code reviewers (qa, design, judgment, codex, etc.), the report shows:
- Marginal cost per session (with vs without reviewers)
- Extra turns from review phases
- Per-reviewer-type frequency
- Optimization tips (parallel launch, --wait flags, triage rules)

## New: Polling/Wait Detection

Detects generic sleep/poll patterns beyond specific tools. Each poll turn re-reads your full context for $0.01-0.05. Reports total polling turns and estimated cost.

## Benchmarks

| Metric | Unoptimized | Optimized | Target |
|---|---|---|---|
| Idle turns/session | 20-25 | 3-5 | <5 |
| Cost/session | $1.50-2.50 | $0.80-1.20 | <$1.50 |
| Waste % | 30-50% | 5-10% | <15% |
| Edit batching | 0% | 50%+ | >30% |
