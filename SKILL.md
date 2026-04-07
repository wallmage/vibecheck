---
name: vibecheck
description: "Universal AI coding cost optimizer. Trigger when the user says /vibecheck, asks about token spend, wants to reduce AI coding costs, says their AI bill is too high, asks why AI is expensive, wants to compress CLAUDE.md or AGENTS.md or any instruction file, asks about session waste or idle narration or context rot, or mentions optimizing any AI coding tool (Claude Code, Codex, Cursor, Windsurf, Cline, OpenClaw, Copilot, TRAE, Qoder, Gemini CLI, Aider, etc.). Also trigger if the user pastes API usage data or asks how token pricing works."
---

# Vibecheck

Vibe coding is fun. Vibe coding is expensive. Let's check.

This skill teaches users where their AI coding spend goes, finds waste in supported session logs, and tightens the project's instruction file so the same work happens with fewer turns and less context bloat.

## Core rules

- **Privacy first.** All data stays on the user's machine. No server, no uploads, no telemetry. The scripts read local log files, analyze in memory, print to screen. Mention this early in every flow — scan, compress, explain — not just during onboarding. Users worry about their code and conversations being sent somewhere.
- Default to the user's language. Prefer the language they are writing in. Use system locale only as a fallback.
- Use the detected tool name and detected instruction file name in all user-facing text. Never say "Claude Code" if they use Cursor. Never say "CLAUDE.md" if their file is `.cursorrules`.
- Be honest about capability. If full log analysis is not supported for the detected tool, say so and switch to education + instruction-file optimization. Do not route through a broken scan path.

## Setup

`SKILL_DIR` is the directory containing this file. All bundled scripts live under `SKILL_DIR/scripts/`.

If installed into an AI tool (via `claude install-skill`), use the installed location.

If cloned into a sandbox or VM, use the clone directly — do not copy files into a separate skills directory.

Quick sandbox setup:
```bash
git clone https://github.com/wallmage/vibecheck /tmp/vibecheck
```
Then SKILL_DIR = `/tmp/vibecheck`.

## Commands

- `/vibecheck` or `/vibecheck scan` — Full workflow below
- `/vibecheck explain` — Teach lessons only, do not edit files
- `/vibecheck compress` — Compress the detected instruction file
- `/vibecheck monitor` — Weekly comparison on latest analysis

## Workflow

### 1. Detect the user's tool

```bash
python3 SKILL_DIR/scripts/detect_tool.py [optional_project_dir] > /tmp/vibecheck_tool_detect.json
```

Read the JSON. Key fields: `primary_tool_name`, `instruction_file`, `can_analyze`, `analysis_mode`, `note`.

If `needs_manual_input` is true, ask for the project folder or tool name.

If multiple tools are detected (`installed_tools` has more than one entry with `can_analyze`), mention this: "I see you use [Tool A] and [Tool B]. I'll scan [primary] first — you can run `/vibecheck scan` again for the other."

For current support details, read [references/capabilities.md](references/capabilities.md).

### 2. Branch based on analysis support

If `can_analyze` is true → run the data-driven scan (step 3).
If `can_analyze` is false → explain that the tool was detected but full session-cost analysis is not available for that log format yet. Continue with cost education using industry averages + instruction-file optimization + optional compression. Skip step 3.

### 3. Run the scan

All supported tools follow the same three-step pattern. Pick the scripts that match `analysis_mode`:

| `analysis_mode` | find script | analyze script | sandbox export |
|---|---|---|---|
| `claude_jsonl` | `find_claude_logs.py` | `analyze_claude_sessions.py` | `export_logs.py` |
| `codex_jsonl` | `find_codex_logs.py` | `analyze_codex_sessions.py` | `export_logs.py codex` |
| `cursor_sqlite` | `find_cursor_logs.py` | `analyze_cursor_sessions.py` | `export_logs.py cursor` |
| `openclaw_jsonl` | `find_openclaw_logs.py` | `analyze_openclaw_sessions.py` | `export_logs.py openclaw` |
| `copilot_chat_json` | `find_copilot_logs.py` | `analyze_copilot_sessions.py` | `export_logs.py copilot` |
| `windsurf_transcript` | `find_windsurf_logs.py` | `analyze_windsurf_sessions.py` | `export_logs.py windsurf` |
| `trae_sqlite` | `find_trae_logs.py` | `analyze_trae_sessions.py` | `export_logs.py trae` |
| `qoder_sqlite` | `find_qoder_logs.py` | `analyze_qoder_sessions.py` | `export_logs.py qoder` |
| `codebuddy_hybrid` | `find_codebuddy_logs.py` | `analyze_buddy_sessions.py` | `export_logs.py codebuddy` |
| `workbuddy_hybrid` | `find_workbuddy_logs.py` | `analyze_buddy_sessions.py` | `export_logs.py workbuddy` |
| `antigravity_brain` | `find_antigravity_logs.py` | `analyze_antigravity_sessions.py` | `export_logs.py antigravity` |

**Generic scan flow** (same for every tool):

```bash
python3 SKILL_DIR/scripts/<find_script> 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/<analyze_script> /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Do not paste raw JSON to the user. Read the lesson JSON and explain results in plain language.

**If no logs found** (sandbox environment): The JSON includes `platform` (mac/windows/linux).

Explain briefly (2-3 sentences):
> Your AI chat logs contain timestamps, token counts, and tool calls — that's what I need to find where your money goes. I can't access them directly because this tool runs in a virtual machine that's walled off from your personal files. But we can copy just the last 14 days over — takes 5 seconds.

Show exactly ONE command based on `platform`. Do NOT show multiple commands or alternatives.

macOS/Linux: `python3 SKILL_DIR/scripts/<sandbox_export>`
Windows: `python SKILL_DIR/scripts/<sandbox_export>`

Tell them: "Open Terminal (or Command Prompt), paste this, hit Enter. Tell me when it's done — or skip this and I'll use typical numbers instead (still gets you most of the benefit)."

Wait for response. If they confirm done, re-run with `~/vibecheck-logs`:
```bash
python3 SKILL_DIR/scripts/<find_script> 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```
If they skip, continue with industry averages.

### 4. Teach

The teaching flow is interactive — pause between sections and wait for the user to respond before continuing. This is education, not a report dump.

Use `waste_descriptions`, `worst_day`, `top3_waste`, and `cache_explanations` from the lesson JSON when available. For the full pattern library and analogies, read [references/waste-patterns.md](references/waste-patterns.md).

**Lesson 1 — "What are you actually paying for?"**

Start with a quick privacy note: "Everything I'm about to show you stays on your machine — no data leaves, no servers involved." Then explain subscription vs actual token usage. Key insight: every message re-reads the entire conversation. Message #50 re-reads all 49 previous messages. The AI spends most of your money re-reading, not thinking. Show their tier if known (Claude $20→~$200 API value, $100→~$1,000, $200→~$4,000).

End with: **"Make sense so far? Ask me anything. When you're ready, I'll show you where the money actually goes — it's not where you'd think."** WAIT for response.

**Lesson 2 — "Where your money actually goes"**

Break their bill into three parts: re-reading old messages (50-65%), new content entering context (15-25%), and actual AI responses (10-15%). The punchline: the actual code the AI writes is the smallest part of the bill. Use their busiest day if available.

End with: **"This is why waste adds up so fast. Want to see the specific things wasting your money? I found [N] patterns."** WAIT for response.

**Lesson 3 — "Your top money wasters"**

Show their top 3 waste patterns (from `top3_waste`) with plain-language analogies. Show total waste cost.

End with: **"The fix is simple — one paragraph added to your [instruction_file_name]. Same work gets done, fewer wasted messages. Takes about a minute. Want me to set it up?"** WAIT for response.

### 5. Progressive optimization

This is the core of vibecheck — a step-by-step guided optimization where the user controls every change.

**Always backup first.** Before touching the instruction file:
```bash
cp /path/to/instruction_file /path/to/instruction_file.vibecheck-backup
```
Tell the user: "I've backed up your [file name] — you can revert anytime with `cp [file].vibecheck-backup [file]`."

**If no instruction file exists:** Offer to create one. "You don't have a [CLAUDE.md / .cursorrules / etc.] yet — that's the file your AI reads for project-specific rules. Want me to create one with the cost-saving rules? It's just a text file in your project root."

**Generate the analysis report** (for your reference, not shown raw to user):
```bash
python3 SKILL_DIR/scripts/report.py /tmp/vibecheck_analysis.json /path/to/instruction_file
```

**How to build the steps:** Read the waste_breakdown from the analysis. Sort patterns by per-session cost (highest first). Group related patterns into 3-4 optimization steps. The grouping depends on what the data shows — use judgment. Typical grouping:

- **Step 1: Biggest waste patterns** — the top 2-3 patterns by cost (usually idle narration, context rot, verbose output, or ping-pong debugging). These alone often account for 60-70% of waste.
- **Step 2: Turn density** — patterns about wasted turns (unchained commands, unbatched edits, file re-reads, git ceremony). These are safe, mechanical fixes.
- **Step 3: Instruction file compression** — if the file is large (>100 lines), compressing it reduces the context tax on every single turn.
- **Step 4: User habits** — things that can't go in the instruction file (start fresh chats between tasks, use /clear after long debugging, choose the right model). Teach these verbally.

If a pattern has near-zero cost for this user, skip it entirely. If only 2 steps have meaningful savings, do 2 steps. Don't pad.

**For each step, follow this exact flow:**

1. **Explain** — what are these patterns, how do they waste money, what's the mechanism. Use analogies from [references/waste-patterns.md](references/waste-patterns.md). Keep it conversational, 2-3 sentences.

2. **Show projected savings** — "These patterns cost you $X.XX/session. Fixing them would bring your average from $Y.YY to $Z.ZZ/session (~$NNN/month savings at your pace)." Use real numbers from the analysis.

3. **Show the proposed change** — display the exact diff of what will be added/changed/removed in their instruction file. Format it clearly:
   ```
   I'd add this near the top of your [file name]:
   
   + **Cost rules:** No turn without tool call. No narration/status/"now I'll…". Think → act same turn.
   + Verbose output: pipe build/test/install to /tmp/, use --quiet flags, tail -50 max.
   ```
   Or for compression: show what's being removed and why it's safe.

4. **Ask permission** — "Want me to apply this? (You can always revert from the backup.)" WAIT for response.

5. **Handle the response:**
   - **Yes** → apply the change, confirm, move to next step.
   - **No / skip** → ask briefly: "Any concern, or just skip this one?" If they share thoughts, acknowledge them. Then move to next step. Never push.
   - **Modify** → if they want a softer version, offer the alternative from [references/fix-blocks.md](references/fix-blocks.md).

**Every step is optional.** The user can accept steps 1 and 3 but skip 2 and 4. That's fine. Each step is independent.

**Adapt format to the tool:**
- CLAUDE.md / AGENTS.md → markdown paragraphs
- .cursorrules / .windsurfrules / .clinerules → one rule per line, no markdown
- SOUL.md → personality/rules section
- Others → markdown paragraphs (safe default)

**Do not suggest unenforceable rules.** Instruction files can change AI behavior (no narration, batch edits, chain commands) but cannot mechanically enforce limits. Never propose rules like "cap sessions at N turns" or "mandatory compact after N turns" — the AI cannot count its own turns or force-stop a task midway. If a task needs 80 turns, a turn cap would halt it arbitrarily. Instead, teach these as **user habits** in step 4.

#### Rule library

The rules below are the building blocks. Pick the ones that match the user's actual waste patterns — don't dump all of them at once. Add them across the relevant steps.

For interactive tools (Claude Code, Cursor, Codex, etc.):
```
**Cost rules:** Every turn = context tax. No turn without tool call. No narration/status/"now I'll…". Think → act same turn. Batch independent tool calls (multiple Reads/Edits/files per turn). Chain commands with `&&` when safe. File re-reads banned — content in context after first read. Re-read only if the file changed or accuracy depends on it. User sees zero code/diffs unless asked.
Verbose output: pipe build/test/install to /tmp/, use --quiet flags, tail -50 max. After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix. Use /clear or /compact between unrelated tasks.
```

For always-on agents (OpenClaw, etc.):
```
**Efficiency rules:** Heartbeat frequency: 30min minimum for idle checks. Skip wake-up if no triggers/notifications. Compress workspace files — remove verbose personality text, keep behavioral rules. Prune session history: archive after 50 turns, summarize, start fresh. Pipe all command output to files, never inline. No status messages between actions.
```

If the user is cautious about the strong rules, offer the softer alternative from [references/fix-blocks.md](references/fix-blocks.md).

#### Compression (typically step 3)

Compress the detected instruction file when it's large enough to matter:

```bash
python3 SKILL_DIR/scripts/measure.py /path/to/instruction_file
python3 SKILL_DIR/scripts/strip_markdown.py /path/to/instruction_file /path/to/instruction_file.working
```

Four sub-passes — present each separately, show the diff, and WAIT for approval:
1. **Strip markdown** (automatic, lossless) — remove formatting cruft. Show reduction, apply without asking.
2. **Creative compression** (needs approval) — dedup, compress code blocks, trim verbose rationale.
3. **Remove human-only content** (needs approval) — installation guides, coaching, verbose WHY explanations.
4. **Telegram mode** (optional, explicit permission only) — rewrite in shorthand fragments. Only offer if user asks or if target line count requires it.

**Preservation rules — these are non-negotiable:**
- Trigger patterns, shell commands, file paths — exact syntax, no abbreviation
- Migration tables — compress format but keep EVERY row AND every note with behavioral meaning (e.g., "Single-arg compiles but wrong semantics" warns about a subtle bug; "Chrome only" IS the rule)
- Concurrency annotations (nonisolated, @concurrent, Sendable, actor isolation)
- Platform/region constraints (e.g., "unavailable China")
- Decision references (e.g., "DEC-003") — these link to design decisions
- When in doubt, keep it. Dropping a behavioral rule silently is worse than keeping 10 extra lines.

### 6. Before/after comparison

After all optimization steps (whether the user accepted all, some, or none):

```bash
python3 SKILL_DIR/scripts/compare.py /tmp/vibecheck_analysis.json
```

Snapshots persist in `~/.vibecheck/snapshots/`. First run shows projections, subsequent runs show actual delta with ✅/⚠️ flags.

Summarize what was applied: "You accepted optimizations for [patterns]. Here's your projected profile:" Then show the before/after in plain language: "Right now you average $2.62/session. After these changes, projected: $1.35/session — that's ~49% less waste."

If they skipped some steps: "You skipped [pattern group]. That's fine — you can always run `/vibecheck` again if you change your mind."

End with: "Run `/vibecheck scan` again in 1-2 weeks to see your ACTUAL savings. The optimizer auto-compares against today's baseline."

## Guidance

- Core framing: "fewer turns, less repeated context, same outcome."
- Keep user-facing explanation non-technical unless they ask for details.
- If the tool is unsupported for full analysis, never fake precision — use confidence labels.
- Adapt output format to the tool's actual instruction file style.
- The strong fix block ("no turn without tool call") is the #1 cost saver across all tested deployments. Default to it. The soft version exists for users who prefer gentler rules.

## References

- Capabilities and support matrix: [references/capabilities.md](references/capabilities.md)
- Waste pattern explanations and analogies: [references/waste-patterns.md](references/waste-patterns.md)
- Alternative (softer) fix blocks: [references/fix-blocks.md](references/fix-blocks.md)
