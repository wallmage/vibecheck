# Scan Presentation Contract

This is the presentation contract for `/vibecheck scan`. It exists for host apps and runtimes that want the scan to feel calm, premium, and report-first instead of exposing tool chatter.

## Visibility classes

- `internal` — shell commands, temp-file inspection, raw JSON, stdout/stderr, retries, and trace data. Never render in the main transcript.
- `progress` — one calm user-facing status item while the scan is running.
- `result` — the polished scan summary or lesson content the user should actually read.
- `approval` — export instructions, edit approvals, or confirmation prompts.

## Progress stages

Use these exact stage labels for the default quiet-progress flow:

1. `Checking your setup`
2. `Finding recent sessions`
3. `Analyzing waste patterns`
4. `Preparing your report`

Rules:

- Show at most one visible progress item at a time.
- Do not show command names like `Bash`, file paths, JSON, or temp files in the default UI.
- When the scan completes, remove the progress item and replace it with the result payload.

## Run state model

The host layer should model scan execution as:

```text
idle
running(stage)
completed(resultPayload)
failed(userMessage, technicalDetails?)
```

The machine-readable companion for this contract lives at [scan-presentation-contract.json](scan-presentation-contract.json).
Use [scan_state.py](/Users/wallny/Developer/vibecheck/scripts/scan_state.py) and [present_scan.py](/Users/wallny/Developer/vibecheck/scripts/present_scan.py) as the reference payload builders.
Use [validate_scan_payload.py](/Users/wallny/Developer/vibecheck/scripts/validate_scan_payload.py) in CI or local checks to validate emitted payload JSON against this contract.
Use [sync_scan_artifacts.py](/Users/wallny/Developer/vibecheck/scripts/sync_scan_artifacts.py) to check or regenerate the contract JSON and presentation fixtures from the shared source of truth.

## Result payload expectations

The first result block should answer "What did you find?" before it answers "How did you find it?"

Required structure:

- Headline: biggest finding or savings statement
- Summary metrics: sessions scanned, average cost per session, waste percentage
- Header statistics: overall plus ranked tool/model summaries with health markers
- Top 3 waste patterns: plain-language labels and short summaries
- Optimization plan: ranked tool-by-tool roadmap with 3-4 approval-ready areas
- One next action: the clearest first move
- Section order metadata: hero, metrics, header statistics, patterns, optimization plan, next action
- Completed run-state metadata so the host can replace progress cleanly
- Stable summary metric ids: `sessions`, `avg_cost_per_session`, `waste_percentage`

Recommended unified-scan additions when multiple tools are merged:

- `unified_scan.mode`
- `unified_scan.tools_scanned`
- `unified_scan.tools_detected`
- `unified_scan.instruction_targets`
- `unified_scan.optimization_targets`
- `header_statistics.overall`
- `header_statistics.tools`
- `header_statistics.models`
- `breakdowns.tools`
- `breakdowns.providers`
- `breakdowns.models`
- `breakdowns.platforms`
- `coverage.detected_tools`
- `optimization_targets`
- `optimization_plan.tool_sequence`
- `optimization_plan.tools`

Tool breakdown guidance:

- `breakdowns.tools` should represent the full detected machine inventory, not only the tools that successfully produced cost metrics.
- Each tool item should include a normalized `status` such as `scanned`, `skipped`, `failed`, or `unsupported`.
- When a tool was detected but not analyzed, keep its row in the unified view with zeroed session/cost metrics instead of hiding it.
- Header tool stats should be ranked by actual usage first: scanned session count when available, otherwise log count.

Health marker guidance:

- For measured areas, tools, or models with waste ratio `<= 10%`, mark them as `Good ✅`.
- For measured areas, tools, or models with waste ratio `> 10%`, mark them as `Waste ❌`.
- For detected but unscored tools, keep scan status separate from waste health instead of pretending they are already good.

Optimization target guidance:

- `optimization_targets` should carry the actual files/settings worth improving across all detected tools.
- Include both project-level instruction files and machine-wide config/settings files when they are readable.
- Each target should identify the tool, path, filename, kind, and scope so host apps can show a structured follow-up list without exposing raw internals.

Optimization roadmap guidance:

- After the initial scan, the result should include a ranked tool-by-tool roadmap.
- Optimize the most-used tool first, then the second, then the third.
- Each tool roadmap should include current vs projected cost/session, projected monthly savings, and 3-4 approval-ready sections ordered from biggest gain to smallest.
- Each roadmap step should include a short explanation, factual metrics, and an explicit `approval_required` marker so the host can pause for permission at every step.

Methodology, teaching, and token mechanics come after the summary reveal.

Recommended result fields:

- `run_state.state = completed`
- `hero.eyebrow`, `hero.headline`, `hero.supporting_text`
- `sections[]` as a stable rendering order

Empty-state rule:

- If zero sessions were scored, still emit a `scan_result` payload instead of a failure.
- The empty state should stay calm: 0 metrics, no pattern list, and one next action.
- Keep section order stable: normal result = `hero, metrics, patterns, next_action`; empty result = `hero, metrics, next_action`

## Failure and export behavior

- Failure state: show a short human explanation first. Technical details stay behind a collapsed disclosure labeled `Technical details`.
- Export/log-access fallback: show exactly one export card with exactly one command and one sentence explaining why it is needed.
- After export succeeds, return to the quiet progress flow. Do not replay internal discovery output.

## Reference payload builders

- `python3 scripts/scan_state.py internal analyze "Analyzer wrote structured output to a temp file."` -> canonical internal payload
- `python3 scripts/scan_state.py progress "Analyzing waste patterns"` -> canonical progress payload
- `python3 scripts/scan_state.py approval "Export recent logs" "I need one export command because this environment cannot read your local logs directly." "python3 SKILL_DIR/scripts/export_logs.py"` -> canonical approval card
- `python3 scripts/scan_state.py failure "I couldn't finish the scan." "short stderr excerpt"` -> canonical failure payload
- `python3 scripts/present_scan.py /tmp/vibecheck_analysis.json /path/to/instruction_file` -> canonical result payload
- `python3 scripts/validate_scan_payload.py /path/to/payload.json` -> validates any emitted scan payload against the contract
- `python3 scripts/sync_scan_artifacts.py` -> fails if contract JSON or presentation fixtures drift
- `python3 scripts/sync_scan_artifacts.py --write` -> rewrites those artifacts from the shared contract module

Validation rules:

- Internal payloads should use one of these event types only: `detect`, `find`, `analyze`, `explain`, `present`, `report`, `export`
- Approval cards should carry exactly one command as a single string field
- Coverage buckets should include `detected_tools`, `unsupported_tools`, `skipped_tools`, and `failed_tools`
