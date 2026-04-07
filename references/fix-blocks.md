# Fix Blocks

Use these as starting points. Adapt them to the target file format and the project's risk tolerance.

## Interactive tools

Prefer heuristics like these:

```text
Cost rules: keep turns dense and useful. Avoid status-only replies when you can act immediately. Batch independent reads or edits when it is safe to do so. Prefer concise command output and redirect noisy logs to a file when possible. Start a fresh thread between unrelated tasks or after long debugging loops. Re-read files only when they changed or when accuracy depends on it.
```

## Always-on agents

```text
Efficiency rules: avoid frequent idle wake-ups, keep personality files compact, prune or summarize long session history, and suppress noisy output unless the result matters for the next action.
```

## Review-required ideas

Propose these separately and explain tradeoffs:

- strict read-before-edit limits
- aggressive no-reread language
- hard turn caps
- forcing command chaining in cases where separate execution is safer
