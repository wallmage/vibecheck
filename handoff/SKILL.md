---
name: handoff
description: "Use when the user wants to continue work in a fresh chat without losing decisions, current state, or next steps; trigger on phrases like \"handoff\", \"hand off\", \"new session\", \"switch session\", \"start fresh\", \"context is getting long\", or \"wrap up and hand off\"."
---

# Handoff

Move work from one chat to the next without dragging the whole old thread forward.

Default goal: preserve decisions, current state, open issues, and next steps in a block that is compact enough to be worth using regularly.

## Core Rules

- No files. Clipboard/chat text only.
- No chaining. Do not trigger other skills from handoff.
- No tool calls. Generate and resume from conversation context only.
- Keep the current session faithful. Preserve conclusions, decisions, discovered mechanisms, failed experiments, measurements, open issues, and pending work.
- Compress the journey. Drop greetings, side chat, repeated back-and-forth, and raw code dumps.
- Prefer concise structure over narrative prose.
- One fenced code block for generate mode. No extra artifacts before or after it.

## Compression Standard

Handoff uses **lossless compression**, not a casual recap.

- Keep durable facts, decisions, discoveries, blockers, and next actions.
- Remove packaging: greetings, pep talks, acknowledgements, narration about what the assistant was about to do, and other chat glue.
- Remove side discussion that does not change the technical or product state.
- Merge duplicates. If the same conclusion was reached three times, keep it once.
- Collapse trial-and-error into outcomes: what was tried, why it failed, and what matters now.
- Convert tool chatter into findings. Keep the result, not the terminal transcript.
- Keep exact values when they matter: versions, limits, costs, measurements, hashes, and file paths.

## Budget

- Target: **2k-4k tokens**
- Normal case: stay near the lower end of the range.
- Use the upper end only when the session has many important decisions, failures, reversals, or partial state that would be expensive to rediscover.
- Do not exceed **4k** unless the user explicitly asks for a detailed or full-fidelity handoff.

Handoff should make fresh sessions easier, not become a second giant prompt.

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
- Step-by-step trial and error after the outcome is clear
- Raw command transcripts
- Large code blocks unless the exact snippet is the key state
- Greetings, meta discussion, and side chat
- Repeated explanations of the same point

Never keep:
- social glue with no state value
- brainstorming branches that were abandoned without learning anything
- narration like "I’ll check this next" or "let me think"
- repeated status updates that did not change the result

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
2. Extract concrete state first: decisions, discoveries, failures, current state, open issues, next actions.
3. Run lossless compression:
   - remove packaging and side chat
   - merge duplicates
   - collapse transcripts into findings
   - keep only durable older context
4. If the first user message already contained an older handoff, keep only the durable conclusions from it. Compress older context aggressively.
5. Output one fenced code block in this shape:

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

Target section weight:
- `PRIOR CONTEXT`: 5-10%
- `THIS SESSION`: 40-50%
- `FAILED / REVERTED`: 10-15%
- `CURRENT STATE`: 15-20%
- `OPEN ISSUES`: 10-15%
- `NEXT`: 5-10%

### Writing guidance

- Use flat bullets.
- Keep each bullet dense and specific.
- Keep the block inside the 2k-4k target unless the user explicitly asks for more.
- Include commit hashes only when they actually help.
- Include file paths only when the next session will likely need them.
- If the session is mid-task, be explicit about what is done vs. not done.
- Prefer state over chronology.
- Prefer conclusions over narration.
- If the block is getting too long, compress `PRIOR CONTEXT` and repeated background before touching `CURRENT STATE`, `OPEN ISSUES`, or `NEXT`.

### Multi-hop rule

- N-1 context: keep only durable facts and open issues.
- Older layers: compress to a few bullets total.
- Do not keep nesting giant prior handoffs inside new giant handoffs.

Reference example: `examples/reference-handoff.md`

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

Resume rules:
- Keep the resume response compact. Do not turn the handoff back into a long essay.
- Do not restate low-value background the user just pasted.
- Surface uncertainty only when the handoff itself is stale or ambiguous.

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
