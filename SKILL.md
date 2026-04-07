# Claude Code Cost Optimizer

Analyze Claude Code session logs, identify wasted spend, and apply fixes. Works on macOS and Windows. Supports Claude, GPT, Gemini, DeepSeek model pricing.

## Commands

### `/cost-optimizer` or `/cost-optimizer scan`

Full diagnostic — discover, analyze, report.

**Step 1: Discover logs**
```bash
python3 SKILL_DIR/scripts/find_logs.py 14 > /tmp/claude_sessions.json
```
Report: platform, projects found, session count, date range.

**Step 2: Analyze**
```bash
python3 SKILL_DIR/scripts/analyze_sessions.py /tmp/claude_sessions.json > /tmp/claude_analysis.json
```

**Step 3: Report**
Find the user's CLAUDE.md (check cwd, then project root). Pass it as second arg for compression analysis:
```bash
python3 SKILL_DIR/scripts/report.py /tmp/claude_analysis.json /path/to/CLAUDE.md
```
Show the report. Then apply fixes:

- **SAFE fixes** (idle narration, bash chaining, ToolSearch): "These are 100% safe — they change HOW Claude works, not WHAT. Apply?" If yes, add the cost rules block to their CLAUDE.md.
- **REVIEW fixes** (file re-reads, edit batching, failed tools): Show each proposed CLAUDE.md line, ask per-item approval.
- **CLAUDE.md compression**: Show the scan result ("Your CLAUDE.md can be trimmed by ~X%, saving $Y/session. Approve to compress?"). If yes, run `/cost-optimizer compress`.

### `/cost-optimizer compress`

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

### `/cost-optimizer monitor`

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

# Or via Claude Desktop: create a scheduled task that runs /cost-optimizer monitor weekly
```

## CLAUDE.md Rules

- Trigger patterns: preserve exactly
- Shell commands/paths: keep verbatim
- Migration tables: compress format, preserve every row
- Never reorder sections
- When in doubt, keep more

## The 6 Waste Patterns

1. **Idle narration** (30-40% of waste): Turns with no tool call and <150 output tokens. Claude narrates instead of acting. Fix: "No turn without tool call."

2. **Unchained Bash** (10-15%): Consecutive Bash turns that could be `&&`-chained. Fix: "Chain Bash with &&."

3. **Unbatched Edits** (5-8%): Sequential single-Edit turns. Multiple Edits can go in one turn. Fix: "Batch Edits into one turn."

4. **File re-reads** (5-8%): Same file Read 2+ times per session. Content is already in context. Fix: "File re-reads banned."

5. **ToolSearch overhead** (3-5%): Looking up tool schemas before every call. Fix: "Call known tools directly."

6. **Failed tool retries** (3-5%): Wasted turn + retry. Project-specific guardrails needed.

## The Fix Block

When applying, add near top of CLAUDE.md:

```
**Cost rules:** Every turn = context tax. No turn without tool call. No narration/status/"now I'll…". Think → act same turn. Batch independent tool calls (multiple Reads/Edits/files per turn). Chain Bash with `&&`. File re-reads banned. User sees zero code/diffs unless asked.
```

## Supported Models

Claude: Opus, Sonnet, Haiku
OpenAI: GPT-4o, GPT-4o-mini, GPT-4.1, GPT-4.1-mini, o1, o3, o3-mini, o4-mini
Google: Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash
DeepSeek: V3, R1

Model auto-detected from session logs. Unknown models default to Sonnet pricing.

## Benchmarks

| Metric | Unoptimized | Optimized | Target |
|---|---|---|---|
| Idle turns/session | 20-25 | 3-5 | <5 |
| Cost/session | $1.50-2.50 | $0.80-1.20 | <$1.50 |
| Waste % | 30-50% | 5-10% | <15% |
| Edit batching | 0% | 50%+ | >30% |
