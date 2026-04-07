# Support Priority - April 2026

This is the current top-10 support roadmap for vibecheck.

Rule used for this list:

- Only March 2026 and April 2026 sources were treated as current.
- Anything published before February 2026 was treated as obsolete for ranking purposes.
- This is a product support priority list, not a strict single-source market-share leaderboard.
- User overrides are respected where they intentionally shape the roadmap.
- When hard usage data is unavailable, current official product activity plus ecosystem visibility was used as a proxy.

## Before / After README story in plain English

Before:

- "All major coding tools get a full personalized measured scan already."
- "vibecheck mainly optimizes CLAUDE.md."
- "24+ tools effectively share the same support depth."

After:

- "vibecheck supports 24+ tools, but full scan support ships per tool."
- "Claude Code, Codex, and Cursor already have full scan support."
- "vibecheck optimizes the instruction file used by each tool, not just CLAUDE.md."

## Priority list

1. GitHub Copilot
2. Cursor
3. Claude Code
4. Google Antigravity
5. VS Code Agent Mode
6. OpenAI Codex
7. Windsurf
8. TRAE
9. Qoder
10. CodeBuddy / WorkBuddy

## Delivery override

Implementation priority is not identical to the market-ranking snapshot above.

- User-directed next build: `OpenClaw` first.
- Reason: OpenClaw is a major always-on agent surface with a distinct waste profile, and it already has enough documented local storage structure to support a real parser.
- After OpenClaw: resume the main order with GitHub Copilot / VS Code, Windsurf, TRAE, Qoder, and CodeBuddy / WorkBuddy.

## Evidence snapshot

### Measured adoption signal

- [JetBrains Research, April 2026](https://blog.jetbrains.com/research/2026/04/which-ai-coding-tools-do-developers-actually-use-at-work/) is the strongest recent usage source in this window:
  - GitHub Copilot: 29% work usage
  - Cursor: 18% work usage
  - Claude Code: 18% work usage
  - The same article explicitly frames Codex, Claude Code, Gemini CLI, Junie, and others as part of the live 2026 agentic coding market.

### Product-momentum signal

- [WIRED, April 2, 2026](https://www.wired.com/story/cusor-launches-coding-agent-openai-anthropic/) describes Cursor 3 as competing directly with Claude Code and Codex, and says Claude Code and Codex have "taken off with millions of developers in recent months."
- [WIRED, March 11, 2026](https://www.wired.com/story/openai-codex-race-claude-code/) describes Codex as rapidly catching up to Claude Code in the coding-agent race.
- [Anthropic Engineering, March 25, 2026](https://www.anthropic.com/engineering) shows Claude Code continuing to ship material workflow updates in the current window.
- [Cursor blog, March 2026](https://cursor.com/blog/third-era) says agent use has overtaken tab completion in Cursor's own product usage.
- [VS Code docs, published April 2, 2026](https://code.visualstudio.com/docs/copilot/agents/overview) show VS Code agents as a first-class workflow across local, background, cloud, and third-party providers.
- [VS Code release notes for version 1.110, released March 4, 2026](https://code.visualstudio.com/updates/v1_110) show agent plugins, browser tools, customization commands, and debug visibility expanding quickly inside VS Code.
- [GitHub changelog, March 17, 2026](https://github.blog/changelog/2026-03-17-copilot-coding-agent-works-faster-with-semantic-code-search/) shows Copilot's coding agent still actively improving in this time window.
- [GitHub Docs, current April 2026 surface](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent) show Copilot cloud agent as a mature background-agent workflow with session tracking, MCP, and environment customization.
- [Windsurf product page, crawled April 2026](https://windsurf.com/windsurf) shows an active agentic IDE surface with 1M+ active users claimed on the current product page.
- [Google blog, November 18, 2025](https://blog.google/products-and-platforms/products/gemini/gemini-3/) is outside the preferred window, so it is not used for ranking. Antigravity remains in the top 5 as a user-directed roadmap priority rather than a measured March/April 2026 adoption win.

### China-priority signal

- [TRAE blog, March 31, 2026](https://www.trae.ai/blog) shows active SOLO rollout and pricing/package changes in the current window.
- [TRAE download/product pages, crawled April 2026](https://www.trae.ai/download) show both IDE and SOLO surfaces live and actively distributed.
- [Qoder docs, crawled April 2026](https://docs.qoder.com/) show a full agentic platform with IDE, CLI, MCP, memory, and Quest Mode.
- [Qoder Quest Mode docs, crawled March/April 2026](https://docs.qoder.com/user-guide/quest-mode) show autonomous long-running, parallel, local/worktree/remote execution as a core surface.
- [CodeBuddy docs, crawled March/April 2026](https://www.codebuddy.ai/docs/cli/best-practices) show a full agentic CLI/editor workflow with skills, rules, memory, and autonomous execution patterns.
- [CodeBuddy release notes, crawled late March 2026](https://www.codebuddy.ai/docs/cli/release-notes/v2.62.0) show rapid current iteration, including delegate tools, memory-path alignment, and remote-control workflows.
- [Tencent Cloud Techpedia, March 12, 2026](https://www.tencentcloud.com/techpedia/142834) describes WorkBuddy public beta and verifies it has already been tested by 2,000+ Tencent employees and tens of thousands of external users.

## Why these 10

### 1. GitHub Copilot

- Strongest current usage signal from JetBrains Research in April 2026: 29% of developers use it at work.
- Also matters because GitHub and VS Code remain core distribution surfaces.

### 2. Cursor

- JetBrains Research in April 2026 shows 18% work usage.
- Cursor 3 launched on April 2, 2026 and current reporting still treats Cursor as one of the three central competitive products in the category.

### 3. Claude Code

- JetBrains Research in April 2026 shows 18% work usage and strong growth.
- Multiple March and April 2026 sources describe it as one of the fastest-growing agentic coding tools.

### 4. Google Antigravity

- User override: treat Antigravity as a top-five target.
- Broad March/April 2026 usage data is still thin, so this slot is roadmap-driven rather than survey-driven.
- It remains strategically important because Gemini-first agent workflows are becoming a distinct surface we should support well.

### 5. VS Code Agent Mode

- User override: treat VS Code itself as a first-class integration surface.
- This is strategically distinct from Copilot because repo rules, editor behaviors, and agent workflows may need separate optimization even when the model provider overlaps.
- By April 2026, VS Code agents, subagents, hooks, skills, and third-party provider handoff are mature enough to justify dedicated support.

### 6. OpenAI Codex

- March and April 2026 reporting places Codex in the core competitive set with Claude Code and Cursor.
- Already implemented in vibecheck with a real session analysis path.

### 7. Windsurf

- Windsurf remains one of the recurring names in current agentic-coding comparisons.
- Its docs show a mature agentic IDE surface with model routing, enterprise/self-serve plans, and a growing custom model stack.

### 8. TRAE

- Strategic China priority.
- March 31, 2026 TRAE product/blog activity shows active SOLO rollout and ongoing pricing/package changes.

### 9. Qoder

- Strategic China priority.
- March and April 2026 docs show active IDE and Quest-mode iteration, skills, parallel execution, MCP, and memory surfaces.

### 10. CodeBuddy / WorkBuddy

- Strategic Tencent family priority.
- CodeBuddy has IDE/plugin/CLI surfaces; WorkBuddy matters for always-on or workplace-agent style workflows.
- Shared Tencent ecosystem makes it sensible to treat them as one support family for roadmap purposes.

## Ranking note

This order is a synthesis, not a pure market-share table.

- Slots 1-3 are anchored by the strongest current usage data.
- Slots 4-5 reflect explicit product strategy choices from the user.
- Slots 6-10 reflect current market visibility, implementation leverage, and China-priority coverage.

## Current implementation status

- Full scan implemented: Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot / VS Code chat sessions, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- Current top-10 buildout is complete.
