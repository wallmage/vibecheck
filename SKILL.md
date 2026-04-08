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
- **Quiet execution only.** Internal detection, scan, analysis, and file-inspection steps are not user-facing content. Run them silently with stdout/stderr redirected to temp files. Do not dump raw JSON, command traces, `cat` output, or long shell logs into the chat. The user should mainly see the final explanation, report, approval prompts, and actionable results.

## Quiet execution protocol

- Redirect every intermediate script run to temp files. Treat `/tmp/vibecheck_*.json` and `/tmp/vibecheck_*.err` as working memory, not user output.
- Never `cat` a full JSON file into the conversation. Do not paste raw tool output unless the user explicitly asks for it.
- Prefer one visible output block per phase at most: the export command when sandboxed, the final plain-language explanation, or the final report/comparison summary.
- If a script fails, inspect the error file briefly and summarize the blocker in one or two sentences. Only surface a short excerpt if the exact error text is necessary to unblock the user.
- During successful runs, do not narrate the internal steps. Move from quiet execution to synthesized results.

## Scan presentation contract

- Every scan item belongs to one of four visibility classes: `internal`, `progress`, `result`, `approval`.
- `internal` includes commands, temp-file reads, raw JSON, stdout/stderr, retries, and trace data. Never show it in the main conversation.
- `progress` is one calm status row only. Maximum one visible progress item at a time.
- `result` is the polished user-facing summary or lesson content.
- `approval` is for export instructions and user confirmation prompts.
- Use these exact progress stages for the default quiet scan flow: `Checking your setup`, `Finding recent sessions`, `Analyzing waste patterns`, `Preparing your report`.
- On completion, remove the progress item and reveal the result payload. Do not stack the result underneath the running state.
- On failure, respond with a short diagnosis first and keep raw stderr behind a collapsed `Technical details` disclosure if you need to show any excerpt at all.
- For the full host/runtime contract, read [references/scan-presentation-contract.md](references/scan-presentation-contract.md) and its machine-readable companion [references/scan-presentation-contract.json](references/scan-presentation-contract.json).
- Use `scripts/scan_state.py` for canonical `internal`, `progress`, `approval`, and `failure` payload shapes. Use `scripts/present_scan.py` for the canonical `result` payload.

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

Visible state before detection: `progress` = `Checking your setup`

If the runtime supports structured payloads, emit:

```bash
python3 SKILL_DIR/scripts/scan_state.py progress "Checking your setup" >/tmp/vibecheck_progress.json 2>/tmp/vibecheck_progress.err
```

```bash
python3 SKILL_DIR/scripts/detect_tool.py [optional_project_dir] >/tmp/vibecheck_tool_detect.json 2>/tmp/vibecheck_tool_detect.err
```

Read the JSON. Key fields: `primary_tool_name`, `instruction_file`, `can_analyze`, `analysis_mode`, `note`, `installed_tools`, `analyzable_tools`, `instruction_targets`, `optimization_targets`.

Do this quietly. Do not print the command output or `cat` the JSON back to the user.

If `needs_manual_input` is true, ask for the project folder or tool name.

If multiple analyzable tools are detected, do not limit the scan to the current tool. Default to a unified machine-wide scan across all detected supported tools, then present one merged result with per-tool, per-model, per-platform, and per-provider breakdowns.

For current support details, read [references/capabilities.md](references/capabilities.md).

### 2. Branch based on analysis support

If `analyzable_tools` is non-empty → run the unified all-tools scan (step 3).
If `analyzable_tools` is empty but `can_analyze` is true → run the single-tool data-driven scan (step 3).
If neither is true → explain that the detected tools do not currently expose a reliable supported session-cost scan. Continue with cost education using industry averages + instruction-file optimization + optional compression. Skip step 3.

### 3. Run the scan

Default behavior: scan all detected supported tools on this machine, not just the tool currently running the skill.

**Unified scan flow** (preferred whenever `analyzable_tools` is non-empty):

Visible state before unified detection: `progress` = `Checking your setup`

```bash
python3 SKILL_DIR/scripts/scan_all_tools.py 14 [optional_project_dir] >/tmp/vibecheck_analysis.json 2>/tmp/vibecheck_scan_all.err
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json >/tmp/vibecheck_lesson.json 2>/tmp/vibecheck_explain.err
python3 SKILL_DIR/scripts/present_scan.py /tmp/vibecheck_analysis.json [instruction_file_if_known] >/tmp/vibecheck_result.json 2>/tmp/vibecheck_present.err
```

This unified analysis already merges all detected supported tools and exposes:

- per-tool breakdown
- per-provider breakdown
- per-model breakdown
- per-platform breakdown
- unified waste breakdown across all tools
- all detected instruction targets for optimization
- all detected optimization targets across tools, including project instruction files and machine-wide settings/config files
- ranked tool statistics so the most-used tool is treated as tool `#1`

Only fall back to the single-tool flow below if the runtime explicitly needs it.

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

Visible state before the find script: `progress` = `Finding recent sessions`

If the runtime supports structured payloads, emit:

```bash
python3 SKILL_DIR/scripts/scan_state.py progress "Finding recent sessions" >/tmp/vibecheck_progress.json 2>/tmp/vibecheck_progress.err
```

```bash
python3 SKILL_DIR/scripts/<find_script> 14 >/tmp/vibecheck_sessions.json 2>/tmp/vibecheck_find.err
```

Visible state before the analyze script: `progress` = `Analyzing waste patterns`

If the runtime supports structured payloads, emit:

```bash
python3 SKILL_DIR/scripts/scan_state.py progress "Analyzing waste patterns" >/tmp/vibecheck_progress.json 2>/tmp/vibecheck_progress.err
```

```bash
python3 SKILL_DIR/scripts/<analyze_script> /tmp/vibecheck_sessions.json >/tmp/vibecheck_analysis.json 2>/tmp/vibecheck_analyze.err
```

Visible state before the explain/result stage: `progress` = `Preparing your report`

If the runtime supports structured payloads, emit:

```bash
python3 SKILL_DIR/scripts/scan_state.py progress "Preparing your report" >/tmp/vibecheck_progress.json 2>/tmp/vibecheck_progress.err
```

```bash
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json >/tmp/vibecheck_lesson.json 2>/tmp/vibecheck_explain.err
python3 SKILL_DIR/scripts/present_scan.py /tmp/vibecheck_analysis.json [instruction_file_if_known] >/tmp/vibecheck_result.json 2>/tmp/vibecheck_present.err
```

Do not paste raw JSON to the user. Read the lesson JSON and explain results in plain language.
Do not `cat` `/tmp/vibecheck_sessions.json`, `/tmp/vibecheck_analysis.json`, `/tmp/vibecheck_lesson.json`, or `/tmp/vibecheck_result.json` into chat.
Reveal the result payload first: headline, summary metrics, top 3 waste patterns, one next action. If the scan merged multiple tools, also surface the unified breakdowns by tool, provider, model, and platform before teaching methodology.

**Do not write inline Python to inspect the analysis JSON.** Use `report.py` and `explain.py` — they handle all formatting. If you must inspect a value, the analysis JSON schema is:
- `summary.total_sessions` (int), `summary.total_cost` (float), `summary.avg_cost_per_session` (float), `summary.avg_turns_per_session` (float), `summary.waste_percentage` (float), `summary.total_waste` (float)
- `waste_breakdown.<pattern>` is a **dict** with keys `total_cost`, `per_session`, `percentage_of_waste`, `description` — never format it directly as a number
- `sessions` is an array of per-session results
- `model_mix`, `per_project`, `platform_mix` are dicts of dicts

**If no logs found** (sandbox environment): The JSON includes `platform` (mac/windows/linux).

Explain briefly (2-3 sentences):
> Your AI chat logs contain timestamps, token counts, and tool calls — that's what I need to find where your money goes. I can't access them directly because this tool runs in a virtual machine that's walled off from your personal files. But we can copy just the last 14 days over — takes 5 seconds.

Show exactly ONE command based on `platform`. Do NOT show multiple commands or alternatives.
This is an `approval` card, not a progress dump. Show one sentence, one command, and nothing else from the internal scan trace.
If the runtime supports structured payloads, model this with `scripts/scan_state.py approval ...`.

macOS/Linux: `python3 SKILL_DIR/scripts/<sandbox_export>`
Windows: `python SKILL_DIR/scripts/<sandbox_export>`

Tell them: "Open Terminal (or Command Prompt), paste this, hit Enter. Tell me when it's done — or skip this and I'll use typical numbers instead (still gets you most of the benefit)."

Wait for response. If they confirm done, re-run with `~/vibecheck-logs`:
```bash
python3 SKILL_DIR/scripts/<find_script> 14 ~/vibecheck-logs >/tmp/vibecheck_sessions.json 2>/tmp/vibecheck_find.err
```
If they skip, continue with industry averages. After they confirm export, return to the quiet progress flow. Do not replay the internal discovery steps.

**If detect/find/analyze/explain/present fails:** inspect the matching `/tmp/vibecheck_*.err` file quietly. Tell the user what blocked the scan in 1-2 sentences. Only include a short raw excerpt when it is necessary to unblock them, and keep it behind a collapsed `Technical details` disclosure. If the runtime supports structured payloads, model this with `scripts/scan_state.py failure ...`.

### 4. Teach

The teaching flow is interactive — pause between sections and wait for the user to respond before continuing. This is education, not a report dump.
But the scan is now report-first: show the polished result summary before the teaching flow begins.

Use `waste_descriptions`, `worst_day`, `top3_waste`, and `cache_explanations` from the lesson JSON when available. For the full pattern library and analogies, read [references/waste-patterns.md](references/waste-patterns.md).

**Result reveal — always first**

Before Lesson 1, read `/tmp/vibecheck_result.json` quietly and present the scan in this order:

1. Headline takeaway
2. Summary metrics: sessions scanned, avg cost/session, waste percentage
3. Top 3 waste patterns in plain language
4. If present, unified breakdowns by tool, model, provider, and platform
5. One next action

Only after the user has seen the findings should you transition into the teaching flow below.

**Lesson 1 — "What are you actually paying for?"**

Start with a quick privacy note: "Everything I'm about to show you stays on your machine — no data leaves, no servers involved." Then explain subscription vs actual token usage. Key insight: every message re-reads the entire conversation. Message #50 re-reads all 49 previous messages. The AI spends most of your money re-reading, not thinking. Show their tier if known (Claude $20→~$200 API value, $100→~$1,000, $200→~$4,000).
Do not lead with this lesson before the user has already seen their headline finding.

End with: **"Make sense so far? Ask me anything. When you're ready, I'll show you where the money actually goes — it's not where you'd think."** WAIT for response.

**Lesson 2 — "Where your money actually goes"**

Break their bill into three parts: re-reading old messages (50-65%), new content entering context (15-25%), and actual AI responses (10-15%). The punchline: the actual code the AI writes is the smallest part of the bill. Use their busiest day if available.

End with: **"This is why waste adds up so fast. Want to see the specific things wasting your money? I found [N] patterns."** WAIT for response.

**Lesson 3 — "Your top money wasters"**

Show their top 3 waste patterns (from `top3_waste`) with plain-language analogies. Show total waste cost.

End with: **"The fix is simple — one paragraph added to your [instruction_file_name]. Same work gets done, fewer wasted messages. Takes about a minute. Want me to set it up?"** WAIT for response.

### 5. Progressive optimization

This is the core of vibecheck — a step-by-step guided optimization where the user controls every change.

**Tool order first:** After the initial scan, rank tools by actual usage. Prefer scanned session count; if a tool was detected but not scored, fall back to local log count. Optimize tool `#1` first (the daily driver), then tool `#2`, then tool `#3`.

**Health markers:** For scored tools or areas with waste ratio `<= 10%`, mark them as `Good ✅`. For scored tools or areas with waste ratio `> 10%`, mark them as `Waste ❌`. For detected but unscored tools, keep scan status separate instead of pretending they are already good.

**Always backup first.** Before touching any instruction file, create a backup.
```bash
cp /path/to/instruction_file /path/to/instruction_file.vibecheck-backup
```
Tell the user which files were backed up and how to revert each one.

**Optimization targets:** Use `optimization_targets` from detect/scan output. This list can include project instruction files, machine-wide instruction files, and machine-wide settings/config files. Prefer machine-wide instruction targets first when a tool exposes them (for example `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`) so one fix can improve every project; treat per-project files as fallback exceptions, not the default first move. If the project contains multiple tool instruction files (for example `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `GEMINI.md`), treat them as one optimization batch only when the tool does not have a stronger machine-wide target.

**Optimization logs:** After the initial scan or after a tool-specific win, you can export a local Markdown log with:
```bash
python3 SKILL_DIR/scripts/export_optimization_log.py /tmp/vibecheck_result.json
python3 SKILL_DIR/scripts/export_optimization_log.py /tmp/vibecheck_tool_success.json
```
Use these exports for the polished local audit trail, not raw transcript dumps.

**If no instruction file exists for a detected tool:** Do not create one. Skip file edits for that tool and keep the optimization in recommendations only.

**Generate the analysis report** (for your reference, not shown raw to user):
```bash
python3 SKILL_DIR/scripts/report.py /tmp/vibecheck_analysis.json /path/to/instruction_file >/tmp/vibecheck_report.txt 2>/tmp/vibecheck_report.err
```

Read the report quietly and summarize it in natural language. Do not dump the full report text into chat unless the user explicitly asks to see it verbatim.

**How to build the steps:** Read the waste_breakdown from the analysis. Sort patterns by per-session cost (highest first). Group related patterns into 3-4 optimization steps. The grouping depends on what the data shows — use judgment. Typical grouping:

- **Step 1: Biggest waste patterns** — the top 2-3 patterns by cost (usually idle narration, context rot, verbose output, or ping-pong debugging). These alone often account for 60-70% of waste.
- **Step 2: Turn density** — patterns about wasted turns (unchained commands, unbatched edits, file re-reads, git ceremony). These are safe, mechanical fixes.
- **Step 3: Instruction file compression** — if the file is large (>100 lines), compressing it reduces the context tax on every single turn.
- **Step 4: User habits** — things that can't go in the instruction file (start fresh chats between tasks, use /clear after long debugging, choose the right model). Teach these verbally.

If a pattern has near-zero cost for this user, skip it entirely. If only 2 steps have meaningful savings, do 2 steps. Don't pad.

**Per-tool scan summary before editing:** Before starting tool `#1`, show that tool's factual header first: average cost/session, average turns/session, average session duration if available, start/end context window if available, the top 3 waste areas, overall waste ratio, and the projected after-optimization cost/session plus monthly savings. Do the same again for tool `#2`, tool `#3`, and later tools.

**For each step, follow this exact flow:**

1. **Explain** — what are these patterns, how do they waste money, what's the mechanism. Use analogies from [references/waste-patterns.md](references/waste-patterns.md). Keep it conversational, 2-3 sentences.

2. **Show projected savings** — "These patterns cost you $X.XX/session. Fixing them would bring your average from $Y.YY to $Z.ZZ/session (~$NNN/month savings at your pace)." Use real numbers from the analysis.

3. **Show the proposed change** — display the exact lines that will be added, changed, or removed. Use `+` for additions and `-` for removals so it reads like a diff:
   ```
   I'd add this near the top of your [file name]:
   
   + Every turn should include a tool call or code change. Do not narrate what you are about to do.
   + Think and act in the same turn. Batch independent edits into one response.
   + Pipe verbose build output to a temp file. Use --quiet flags when available.
   ```
   For compression, show what's being removed with `-` prefix and why it's safe to remove.

4. **Ask permission explicitly** — end each step with a direct question: "Want me to apply this change? (You can always revert from the backup.)" Then STOP and WAIT for the user's response. Do not continue to the next step until the user replies.

5. **Handle the response:**
   - **Yes** → apply the change with `vibecheck_optimize.py`, then call `present_next_workflow_item.py` to continue.
   - **No / skip** → ask briefly: "Any concern, or just skip this one?" If they share thoughts, acknowledge them. Then mark the step skipped with `vibecheck_skip_step.py` and call `present_next_workflow_item.py`. Never push.
   - **Modify** → if they want a softer version, offer the alternative from [references/fix-blocks.md](references/fix-blocks.md).

**Structured helper payloads:** If the runtime supports structured payloads, use:
- `python3 SKILL_DIR/scripts/present_optimization_step.py /tmp/vibecheck_result.json <tool_id> <step_rank>` to build the approval card for the next step.
- `python3 SKILL_DIR/scripts/vibecheck_skip_step.py /tmp/vibecheck_result.json <tool_id> <step_rank>` if the user skips a step and you need to advance the state truthfully.
- `python3 SKILL_DIR/scripts/present_next_workflow_item.py /tmp/vibecheck_result.json <tool_id>` after each apply or skip. It returns the next pending step for that tool, or the final per-tool success payload once that tool is complete.
- `python3 SKILL_DIR/scripts/present_tool_success.py /tmp/vibecheck_result.json <tool_id>` when you explicitly need the standalone per-tool success payload.

**Every step is optional.** The user can accept steps 1 and 3 but skip 2 and 4. That's fine. Each step is independent.

**After tool `#1` finishes:** Show a before-vs-projected comparison for that tool alone first. Then ask one bulk question: "Do you want me to auto-apply the same treatment to your other tools/projects?" If yes, do not keep walking tool `#2`, `#3`, etc. step by step — auto-apply the remaining planned fixes across the rest of the detected tools/projects.

Use these helper scripts for that handoff:
- `python3 SKILL_DIR/scripts/present_bulk_apply_prompt.py /tmp/vibecheck_result.json <tool_id>` to build the approval card after tool `#1`
- `python3 SKILL_DIR/scripts/vibecheck_optimize_bulk.py /tmp/vibecheck_result.json <tool_id>` to apply the remaining plan after approval
- `python3 SKILL_DIR/scripts/present_final_success.py /tmp/vibecheck_result.json` to show the all-tools projected win before education starts

**Education comes last.** After all optimization is done, show the final success, the statistics, and the before/after comparison first. Only then begin the human education section.

**Post-optimization education (last step):** Teach the continuity lesson here, not during the initial scan. Use `behavior_guidance` from `scripts/explain.py`.

- Explain why overloaded context is bad in two dimensions: it costs more because every turn re-reads more stale material, and it performs worse because the model has to sort through too much old state.
- Explain that people avoid clearing because continuity matters. Do not frame it as laziness. The real friction is fear of losing background, decisions, and momentum.
- Give a rule of thumb: use focused work chunks that usually fit in **5-10 active minutes**, and treat **~30-40 turns** as the upper comfort band before context cost usually starts snowballing. Between unrelated slices, start a fresh chat or use `/clear` when the tool supports it. Teach this as a habit only — never as an instruction-file rule.
- Explain that waiting for platform auto-compaction is not a win: by then the user already paid the cost of the bloated thread, and the model may still lose detail when the platform compresses history.
- Teach the continuity system:
  - persistent behavior rules belong in `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, or `Memory.md` when supported
  - project background belongs in well-structured local `.md` docs, split by topic and kept slice-sized
  - the instruction file should point to those docs with a short index instead of embedding everything inline
- Only after that, offer the sister `handoff` skill with one static GitHub install prompt. Do not use local scripts, subfolder installs, or `/vibecheck handoff`. This is the final step of the whole flow.
- Present the install as a copyable prompt, for example: `Help me install this skill too: <handoff GitHub URL>`.

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
Verbose output: pipe build/test/install to /tmp/, use --quiet flags, tail -50 max. After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix. In long threads, keep replies compact and avoid re-explaining old context unless it helps the next action.
```

For always-on agents (OpenClaw, etc.):
```
**Efficiency rules:** Heartbeat frequency: 30min minimum for idle checks. Skip wake-up if no triggers/notifications. Compress workspace files — remove verbose personality text, keep behavioral rules. Prune session history: archive after 50 turns, summarize, start fresh. Pipe all command output to files, never inline. No status messages between actions.
```

If the user is cautious about the strong rules, offer the softer alternative from [references/fix-blocks.md](references/fix-blocks.md).

#### Compression (typically step 3)

Compress the detected instruction file when it's large enough to matter. This uses the lossless prompt compressor — a 4-pass process that strips formatting, deduplicates facts, removes human-only scaffolding, and optionally rewrites in telegram shorthand.

Before starting, read these reference files for the technique catalog and detailed rules:
- [references/compressor.md](references/compressor.md) — full compressor operating manual (modes, preservation rules, edge cases)
- [references/compression-techniques.md](references/compression-techniques.md) — 23 techniques with before/after examples

**Run these scripts** (do not skip — they handle Pass 1 mechanically and establish the baseline):

```bash
python3 SKILL_DIR/scripts/measure.py /path/to/instruction_file >/tmp/vibecheck_measure.txt 2>/tmp/vibecheck_measure.err
python3 SKILL_DIR/scripts/strip_markdown.py /path/to/instruction_file /path/to/instruction_file.working >/tmp/vibecheck_strip.out 2>/tmp/vibecheck_strip.err
```

**Three modes** (default to Strict Lossless):
- **Strict Lossless** (default): Pass 1 + approved Pass 2. Human-readable, all facts preserved.
- **AI-Lossless**: + Pass 3. Remove human-only scaffolding (tutorials, coaching, schedules).
- **AI-Only**: + Pass 4. Ultra-dense telegram rewrite. Only if user explicitly wants it.

**Four sub-passes** — present each separately, show the diff, and WAIT for approval:
1. **Pass 1: Mechanical** (automatic) — strip markdown formatting, convert tables to semicolons, merge short bullet lists. Show reduction, apply without asking.
2. **Pass 2: Fact-preserving** (needs approval) — dedup repeated facts with cross-references, compress code blocks to inline descriptions, trim verbose rationales. Propose each as a numbered list with estimated savings.
3. **Pass 3: High-fidelity** (needs approval) — remove tutorials, coaching, motivational content, validation tables that duplicate specs. Decision test: "If I remove this, will the AI produce worse code?" If no → candidate.
4. **Pass 4: Telegram** (explicit permission only) — full rewrite in shorthand fragments. Only for AI-only documents.

**Always report** word count and estimated token reduction after each pass. Finish with a summary table showing Original → Pass 1 → Pass 2 → etc.

### 6. Before/after comparison

After all optimization steps (whether the user accepted all, some, or none):

```bash
python3 SKILL_DIR/scripts/compare.py /tmp/vibecheck_analysis.json >/tmp/vibecheck_compare.txt 2>/tmp/vibecheck_compare.err
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
- Scan presentation contract: [references/scan-presentation-contract.md](references/scan-presentation-contract.md)
- Waste pattern explanations and analogies: [references/waste-patterns.md](references/waste-patterns.md)
- Alternative (softer) fix blocks: [references/fix-blocks.md](references/fix-blocks.md)
- Instruction file compressor (full operating manual): [references/compressor.md](references/compressor.md)
- Compression technique catalog (23 techniques with examples): [references/compression-techniques.md](references/compression-techniques.md)
