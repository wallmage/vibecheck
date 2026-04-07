# Claude Code Cost Optimizer

A Claude Code skill that analyzes your session logs and cuts waste by 30-50%.

## What it does

1. Scans your past 14 days of Claude Code sessions
2. Identifies 6 waste patterns (idle narration, unchained Bash, unbatched Edits, file re-reads, ToolSearch overhead, failed retries)
3. Shows exactly how much you're wasting in dollars
4. Applies fixes to your CLAUDE.md (with your approval)
5. Optionally compresses your CLAUDE.md to reduce per-turn context tax
6. Weekly monitoring to catch regression

## Quick start

```bash
# Install as a Claude Code skill
claude install-skill /path/to/claude-cost-optimizer

# Or just run directly
claude /cost-optimizer scan
```

## Commands

- `/cost-optimizer scan` — Full diagnostic with savings projection
- `/cost-optimizer compress` — Compress CLAUDE.md (25-50% smaller)
- `/cost-optimizer monitor` — Week-over-week comparison with alerts

## Supported models

Claude (Opus, Sonnet, Haiku), GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1

## How it works

Every Claude Code turn re-reads your entire conversation (context tax). The biggest waste is turns where Claude narrates ("Now I'll fix this file...") instead of just doing it. That's 30-40% of most people's spend.

The optimizer adds one paragraph to your CLAUDE.md that eliminates these patterns. No behavior change — same work gets done, fewer turns.

## Works on

- macOS (Apple Silicon + Intel)
- Windows
- Linux

Requires Python 3.8+. No dependencies beyond stdlib.
