# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

[![GitHub stars](https://img.shields.io/github/stars/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/watchers)
[![GitHub last commit](https://img.shields.io/github/last-commit/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff)
[![Top language](https://img.shields.io/github/languages/top/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff)
[![Workflow](https://img.shields.io/badge/workflow-copy%20%26%20paste-111827?style=flat-square)](https://github.com/wallmage/handoff)
[![Works in](https://img.shields.io/badge/works%20in-CLI%20%7C%20GUI%20%7C%20chat-0f766e?style=flat-square)](https://github.com/wallmage/handoff)
[![Storage](https://img.shields.io/badge/storage-no%20files-4f46e5?style=flat-square)](https://github.com/wallmage/handoff)
[![Focus](https://img.shields.io/badge/focus-context%20transfer-b45309?style=flat-square)](https://github.com/wallmage/handoff)
[![Use case](https://img.shields.io/badge/use%20case-context%20rot%20recovery-2563eb?style=flat-square)](https://github.com/wallmage/handoff)

**Your conversations decay. This keeps the signal alive.**

Every AI chat has a half-life. The longer a thread runs, the more the model re-reads stale context, the less sharp its output gets, and the more tokens you burn on noise. You already know the fix: start a fresh session. But then you lose all the decisions you made, the bugs you already chased down, the architecture you landed on. So you keep going in the old thread and the quality keeps dropping.

`handoff` breaks that cycle. Say `handoff` in any session and it generates a transfer block -- lossless-compressed, 2-4K tokens -- that captures what matters: decisions, discoveries, failures, current state, open issues, next steps. Paste it into a new chat and you're back at full speed.

No files, no plugins, no databases. Copy and paste.

## How it works

**Generate mode** -- say `handoff` in the old session. The skill compresses the whole conversation into a structured transfer block. Not a casual recap -- it keeps concrete outcomes (what was decided, what failed, what's half-done, what's next) and strips greetings, side chat, repeated explanations, and raw transcripts.

**Resume mode** -- paste the block into a new session. The skill parses it, gives you a short summary of where things stand, and waits for your instruction.

The transfer block targets **2-4K tokens**. Small enough to use often, dense enough to lose nothing that matters.

## Natural triggers

You don't need to remember a special command. Any of these work:

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## What gets preserved

- Decisions and why they were made
- Technical discoveries and mechanisms
- Failed experiments and why they failed
- Important numbers, limits, versions, timings, costs
- Current branch / commit / dirty state
- Uncommitted or partial work
- Open issues and blockers
- The next best action

What gets dropped: greetings, pep talks, repeated back-and-forth, raw code dumps, side discussion that didn't change anything, narration about what the assistant was about to do.

## Works everywhere

`handoff` runs on plain text. It works in:

- Coding tools (Claude Code, Cursor, Copilot, Windsurf)
- CLI tools (terminal-based AI assistants)
- GUI chat tools (ChatGPT, Claude chat, Gemini)
- Any product where you can paste text into a new conversation

No integration needed.

## When to use it

- The chat is getting long and the model is getting sluggish
- You finished a chunk of work and want a clean next session
- You're about to hit a context limit
- You want to preserve decisions without keeping the old thread alive
- You're switching machines or tools

## Install

Copy this into your AI tool:

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## Usage

In the old chat:

```text
handoff
```

Copy the generated block. Open a new session. Paste.

That's it.

---

Author: [Wallny](https://github.com/wallmage)
