---
name: vibecheck
description: Universal AI coding cost optimizer. Use when the user asks to run /vibecheck, reduce token spend, analyze AI coding session waste, compress instruction files like CLAUDE.md or AGENTS.md, or explain where AI coding costs come from across tools such as Claude Code, Codex, Cursor, Windsurf, Cline, Gemini CLI, and OpenClaw.
---

# Vibecheck

Vibe coding is fun. Vibe coding is expensive. Let's check.

This skill teaches users where their AI coding spend goes, finds waste in supported session logs, and tightens the project's instruction file so the same work happens with fewer turns and less context bloat.

## Core rules

- Default to the user's language. Prefer the language they are writing in right now. Use system locale only as a fallback.
- Use the detected tool name and detected instruction file name in all user-facing text.
- Be honest about capability. If full log analysis is not supported for the detected tool, say so plainly and switch to education + instruction-file optimization instead of implying a broken scan.
- Treat this like a cost-and-behavior optimization skill, not a generic repo edit. Show changes before applying them when editing a user's instruction file.

## Setup

`SKILL_DIR` is the directory containing this file. All bundled scripts live under `SKILL_DIR/scripts/`.

If the skill was installed into an AI tool, use that installed location.

If the repo was cloned into a sandbox or VM, use the clone directly. Do not copy files into a separate skills directory unless the user asked for that.

## Commands

### `/vibecheck` or `/vibecheck scan`

Run the full workflow below.

### `/vibecheck explain`

Teach the lessons only. Do not edit files.

### `/vibecheck compress`

Compress the detected instruction file, not just `CLAUDE.md`.

### `/vibecheck monitor`

Run the weekly comparison on the latest supported session analysis.

## Workflow

### 1. Detect the user's tool first

Run:

```bash
python3 SKILL_DIR/scripts/detect_tool.py [optional_project_dir] > /tmp/vibecheck_tool_detect.json
```

Read the JSON and use:

- `primary_tool_name`
- `instruction_file`
- `can_analyze`
- `analysis_mode`
- `supports_instruction_optimization`
- `note`

If detection fails and `needs_manual_input` is true, ask for the project folder or tool name.

If an instruction file was detected, use its real path and filename everywhere. Do not hardcode `CLAUDE.md`.

For current support details, read [references/capabilities.md](references/capabilities.md).

### 2. Branch based on analysis support

If `can_analyze` is `true`, choose the data-driven scan that matches `analysis_mode`.

If `can_analyze` is `false`, explain that the tool was detected but full session-cost analysis is not available yet for that log format. Continue with:

- cost education using industry averages
- instruction-file optimization
- optional compression of the detected instruction file

Do not send the user through a broken scan path when the detector already says analysis is unsupported.

### 3. Full scan path for supported session logs

#### Claude Code (`analysis_mode = claude_jsonl`)

Run:

```bash
python3 SKILL_DIR/scripts/find_logs.py 14 > /tmp/vibecheck_sessions.json
```

If logs are found, continue:

```bash
python3 SKILL_DIR/scripts/analyze_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Do not paste raw JSON to the user. Read the lesson JSON and explain results in plain language.

If `find_logs.py` returns `"error": "no_logs"`, explain that the sandbox cannot see their personal logs directly, then show exactly one export command for their platform:

- macOS/Linux: `python3 SKILL_DIR/scripts/export_logs.py`
- Windows: `python SKILL_DIR/scripts/export_logs.py`

Then wait. If they copy logs into `~/vibecheck-logs`, re-run:

```bash
python3 SKILL_DIR/scripts/find_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

If they skip exporting logs, continue with education + instruction-file optimization.

#### Codex (`analysis_mode = codex_jsonl`)

Run:

```bash
python3 SKILL_DIR/scripts/find_codex_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_codex_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Codex logs expose per-step `last_token_usage`, so the analysis can estimate turn costs from real session telemetry instead of generic averages.

If Codex logs are not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py codex
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_codex_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### Cursor (`analysis_mode = cursor_sqlite`)

Run:

```bash
python3 SKILL_DIR/scripts/find_cursor_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_cursor_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Cursor stores conversations in SQLite under `workspaceStorage` and related global storage. When Cursor includes token counters, use them. When it does not, estimate token cost from the reconstructed conversation content and model metadata.

If Cursor storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py cursor
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_cursor_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### OpenClaw (`analysis_mode = openclaw_jsonl`)

Run:

```bash
python3 SKILL_DIR/scripts/find_openclaw_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_openclaw_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

OpenClaw stores per-agent session metadata in `sessions.json` and transcript JSONL files beside it. Use the measured transcript data when available, and surface always-on waste patterns like idle heartbeats, bloated workspace files, and memory buildup.

If OpenClaw storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py openclaw
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_openclaw_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### GitHub Copilot / VS Code (`analysis_mode = copilot_chat_json`)

Run:

```bash
python3 SKILL_DIR/scripts/find_copilot_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_copilot_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

This path supports local VS Code Copilot chat sessions and exported chat JSON/JSONL. It reconstructs newer JSONL mutation logs, reads workspace and empty-window sessions, and estimates turn costs from stored token usage when present or from reconstructed turn size when not.

If the storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py copilot
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_copilot_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### Windsurf (`analysis_mode = windsurf_transcript`)

Run:

```bash
python3 SKILL_DIR/scripts/find_windsurf_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_windsurf_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Prefer the official Windsurf transcript hook output under `~/.windsurf/transcripts/*.jsonl`. Keep compatibility support for older local cache files under `.codeium/windsurf/cascade` when they are present, but treat the transcript hook as the primary supported source.

If Windsurf storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py windsurf
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_windsurf_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### TRAE (`analysis_mode = trae_sqlite`)

Run:

```bash
python3 SKILL_DIR/scripts/find_trae_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_trae_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

TRAE stores workspace state in `workspaceStorage/*/state.vscdb`. Use the current chat data stored under `ItemTable` keys that start with `memento/icube-ai-ng-chat-storage`, and reconstruct session/message lists from there instead of pretending the schema is identical to Cursor.

If TRAE storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py trae
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_trae_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### Qoder (`analysis_mode = qoder_sqlite`)

Run:

```bash
python3 SKILL_DIR/scripts/find_qoder_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_qoder_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Qoder stores workspace state in `workspaceStorage/*/state.vscdb`. The exact chat-storage keys are not formally documented, so use a broad `ItemTable` extractor that looks for current chat, conversation, session, quest, and agent payloads, then reconstruct message lists from those JSON values.

If Qoder storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py qoder
```

Then re-run:

```bash
python3 SKILL_DIR/scripts/find_qoder_logs.py 14 ~/vibecheck-logs > /tmp/vibecheck_sessions.json
```

#### CodeBuddy (`analysis_mode = codebuddy_hybrid`)

Run:

```bash
python3 SKILL_DIR/scripts/find_codebuddy_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_buddy_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

CodeBuddy exposes a session index plus runtime logs. Use the session index to enumerate conversations, then merge in runtime events like session creation, model selection, prompt resolution, message counts, and failures from `codebuddy.log`.

If CodeBuddy storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py codebuddy
```

#### WorkBuddy (`analysis_mode = workbuddy_hybrid`)

Run:

```bash
python3 SKILL_DIR/scripts/find_workbuddy_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_buddy_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

WorkBuddy uses the same session index pattern as CodeBuddy and also keeps VS Code-style workspace state plus app logs under `WorkBuddy/logs`. Prefer the session index plus runtime logs, and treat workspace SQLite as an auxiliary source.

If WorkBuddy storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py workbuddy
```

#### Google Antigravity (`analysis_mode = antigravity_brain`)

Run:

```bash
python3 SKILL_DIR/scripts/find_antigravity_logs.py 14 > /tmp/vibecheck_sessions.json
python3 SKILL_DIR/scripts/analyze_antigravity_sessions.py /tmp/vibecheck_sessions.json > /tmp/vibecheck_analysis.json
python3 SKILL_DIR/scripts/explain.py /tmp/vibecheck_analysis.json > /tmp/vibecheck_lesson.json
```

Antigravity keeps raw conversations in encrypted `.pb` files, but it also writes readable task, plan, and walkthrough artifacts under `~/.gemini/antigravity/brain/<conversation-id>/`. Use those artifacts and their metadata as the supported scan surface instead of pretending the encrypted transport is directly parseable.

If Antigravity storage is not directly visible in a sandbox, tell the user to run:

```bash
python3 SKILL_DIR/scripts/export_logs.py antigravity
```

### 4. Teaching flow

Keep the interactive explanation short and concrete:

1. Explain subscription vs actual token usage.
2. Explain that most cost comes from re-reading context, not generating code.
3. Show the user's busiest day and top waste patterns when data is available.
4. End each lesson chunk with a short pause for confirmation before moving on.

Use `waste_descriptions`, `worst_day`, and `top3_waste` from the lesson JSON when available.

For the full pattern library and plain-language analogies, read [references/waste-patterns.md](references/waste-patterns.md).

### 5. Report + fixes

When analysis exists, generate the report:

```bash
python3 SKILL_DIR/scripts/report.py /tmp/vibecheck_analysis.json /path/to/instruction_file
```

Then propose edits to the detected instruction file.

Safe, low-risk fixes:

- reduce idle narration
- reduce verbose tool output
- encourage batching of independent actions
- prefer command chaining where appropriate
- encourage fresh sessions between unrelated tasks

Review-before-applying fixes:

- strict exploration limits
- aggressive anti-reread rules
- behavior changes that could reduce accuracy in complex repos

Avoid absolute rules like "no turn without tool call" or "file rereads banned." Prefer heuristics that reduce waste without forcing premature edits.

For reusable rule blocks, read [references/fix-blocks.md](references/fix-blocks.md).

### 6. Compression flow

Compression always targets the detected instruction file path.

1. Back it up.
2. Measure it.
3. Run mechanical markdown stripping.
4. Propose higher-risk creative compression separately.
5. Keep examples, commands, paths, and critical project guidance intact.

Example:

```bash
cp /path/to/instruction_file /path/to/instruction_file.backup
python3 SKILL_DIR/scripts/measure.py /path/to/instruction_file
python3 SKILL_DIR/scripts/strip_markdown.py /path/to/instruction_file /path/to/instruction_file.working
```

### 7. Comparison flow

After applying fixes from a supported analysis run:

```bash
python3 SKILL_DIR/scripts/compare.py /tmp/vibecheck_analysis.json
```

Explain the before/after numbers in plain language. Focus on turns per session, waste percentage, and average cost per session.

## Guidance

- Prefer "fewer turns, less repeated context, same outcome" as the core framing.
- Keep the user-facing explanation non-technical unless they ask for pricing details.
- If the tool is unsupported for full analysis, never fake precision.
- If you edit the instruction file, adapt the output format to the tool's actual file style.

## References

- Capabilities and support matrix: [references/capabilities.md](references/capabilities.md)
- Waste pattern explanations: [references/waste-patterns.md](references/waste-patterns.md)
- Reusable fix blocks: [references/fix-blocks.md](references/fix-blocks.md)
