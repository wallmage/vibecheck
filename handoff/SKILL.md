---
name: handoff
description: "Portable session handoff between chat threads via copy-paste. Trigger on phrases like \"handoff\", \"hand off\", \"new session\", \"switch session\", \"start fresh\", or \"wrap up and hand off\". In the old chat, emit one copyable fenced block. In the new chat, absorb the pasted block and resume. Tool-agnostic: works in GUI and CLI. No file I/O. No chained skills."
---

# Handoff

Move work from one chat to the next without dragging the whole old thread forward.

Default goal: preserve decisions, current state, open issues, and next steps in a block that is compact enough to be worth using regularly.

## Core Rules

- No files. Clipboard/chat text only.
- No chaining. Do not trigger other skills from handoff.
- Keep the current session faithful. Preserve conclusions, decisions, discovered mechanisms, failed experiments, measurements, open issues, and pending work.
- Compress the journey. Drop greetings, repeated back-and-forth, and raw code dumps.
- Prefer concise structure over narrative prose.
- One fenced code block for generate mode. No extra artifacts.

## Budget

- Default: **4k-8k tokens**
- Use more only when the session is unusually technical, fragile, or mid-flight.
- If the user explicitly asks for a detailed or full-fidelity handoff, go larger.

This is intentionally smaller than the old default. Handoff should make fresh sessions easier, not become a second giant prompt.

## What To Preserve

Always keep:
- Decisions and why they were made
- Technical discoveries and mechanisms
- Failed experiments and why they failed
- Important numbers, limits, versions, timings, costs
- Current branch / commit / dirty state when known
- Uncommitted or partial work
- Open issues and blockers
- The next best action

Compress heavily:
- Step-by-step trial and error
- Raw command transcripts
- Large code blocks
- Greetings and meta discussion
- Repeated explanations of the same point

## Mode A: Generate

Use when the user wants to move to a new chat.

Triggers include:
- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

### How to generate

1. Reconstruct the session mentally.
2. Capture the useful state, not the whole transcript.
3. If the first user message already contained an older handoff, keep only the durable conclusions from it. Compress older context aggressively.
4. Output one fenced code block in this shape:

```text
---HANDOFF [YYYY-MM-DD HH:MM]---

PRIOR CONTEXT:
- Only durable older context that still matters now

THIS SESSION:
- Topic / task:
  - Goal:
  - Done:
  - Result:
  - Key insight:

FAILED / REVERTED:
- What was tried
- Why it failed
- What we learned

CURRENT STATE:
- Branch / commit / dirty state
- What is complete
- What is partial
- Any important file or architecture notes

OPEN ISSUES:
1. Issue — cause — status

NEXT:
1. Highest-priority next action
2. Second action

---END---
```

### Writing guidance

- Use flat bullets.
- Keep each bullet dense and specific.
- Include commit hashes only when they actually help.
- Include file paths only when the next session will likely need them.
- If the session is mid-task, be explicit about what is done vs. not done.

### Multi-hop rule

- N-1 context: keep only durable facts and open issues.
- Older layers: compress to a few bullets total.
- Do not keep nesting giant prior handoffs inside new giant handoffs.

## Mode B: Resume

Use when the first user message contains a pasted handoff block.

### How to resume

1. Parse the block inline. No tool calls.
2. Acknowledge the context briefly.
3. Summarize:
   - prior durable context
   - what the last session completed
   - current state
   - open issues
   - next action
4. Stop and wait for instruction.

Suggested response shape:

```text
Picked up the handoff.

Prior context: ...
Last session: ...
Current state: ...
Open issues: ...
Next up: ...
```

If the handoff is stale, note that the branch or task state may have changed.

## Quality Bar

A good handoff should let the next session:
- avoid rediscovery
- avoid repeating failed work
- understand current state quickly
- continue without dragging the whole old conversation forward

If you are unsure whether something belongs in the handoff, use this test:

`Will losing this fact make the next session slower, riskier, or more confusing?`

If yes, include it.

## CLI and GUI

This skill is designed to work in both:
- GUI chat tools: user copies the fenced block into a new chat
- CLI tools: user copies the fenced block from terminal output into a new chat

No special button is required. The skill should still be useful with plain copy-paste.
