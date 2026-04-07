# Fix Blocks

Two versions: strong (default, proven 40-50% waste reduction) and soft (for cautious users who prefer gentler rules). SKILL.md uses the strong version by default. Offer the soft version if the user expresses concern about the strong rules being too aggressive.

## Strong fix block (default)

For interactive tools:
```text
**Cost rules:** Every turn = context tax. No turn without tool call. No narration/status/"now I'll…". Think → act same turn. Batch independent tool calls (multiple Reads/Edits/files per turn). Chain commands with `&&`. File re-reads banned — content in context after first read. User sees zero code/diffs unless asked.
Verbose output: pipe build/test/install to /tmp/, use --quiet flags, tail -50 max. After 2 failed fixes on same file: stop, re-read error fully, think, single targeted fix. Clear/compact between unrelated tasks — never exceed ~20 turns without clearing. Max 3 file reads before first Edit.
```

For always-on agents:
```text
**Efficiency rules:** Heartbeat frequency: 30min minimum for idle checks. Skip wake-up if no triggers/notifications. Compress workspace files — remove verbose personality text, keep behavioral rules. Prune session history: archive after 50 turns, summarize, start fresh. Pipe all command output to files, never inline. No status messages between actions.
```

## Soft fix block (alternative)

For users who prefer less prescriptive rules:

```text
Cost rules: keep turns dense and useful. Avoid status-only replies when you can act immediately. Batch independent reads or edits when it is safe to do so. Prefer concise command output and redirect noisy logs to a file when possible. Start a fresh thread between unrelated tasks or after long debugging loops. Re-read files only when they changed or when accuracy depends on it.
```

## Adapting to tool formats

- CLAUDE.md / AGENTS.md → markdown paragraphs (as shown above)
- .cursorrules / .windsurfrules / .clinerules → one rule per line, no markdown
- SOUL.md → add to personality/rules section
- .trae/rules / .qoder/rules / .lingma/rules → plain text rules
- Others → markdown paragraphs (safe default)

### Example: .cursorrules format

```text
Every turn should include a tool call or code change. Do not narrate what you are about to do.
Think and act in the same turn. Batch independent edits into one response.
Chain shell commands with && instead of running them separately.
Do not re-read files that are already in context.
Pipe verbose build output to a temp file. Use --quiet flags when available.
After 2 failed fixes on the same file, stop, re-read the error, and make one targeted fix.
Start a new chat between unrelated tasks.
```

## Review-required ideas

Propose these separately and explain tradeoffs. Do not add without user approval:

- strict read-before-edit limits
- hard turn caps per session
- forcing command chaining in cases where separate execution is safer
- aggressive no-reread language that could cause the AI to skip necessary re-reads
