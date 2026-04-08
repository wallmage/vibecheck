# Reference Handoff

Use this as a density reference, not a rigid template.

```text
---HANDOFF [2026-04-09 09:30]---

PRIOR CONTEXT:
- Product family has two separate skills/repos: `vibecheck` for cost optimization and `handoff` for fresh-session transfer.
- Install model is static GitHub prompt only; no local installer scripts.
- User strongly prefers direct, single-step workflows and no process ceremony.

THIS SESSION:
- Topic / task:
  - Goal: finish handoff as a portable, compact, cross-tool skill that is worth using frequently.
  - Done: split handoff into its own repo, added standalone README, cross-linked it with vibecheck, and upgraded repo badges.
  - Result: handoff now stands on its own as a sister skill while still being recommended later from vibecheck's education flow.
  - Key insight: the handoff itself must stay compact or it becomes another source of context waste.
- Topic / task:
  - Goal: decide the right handoff size target.
  - Done: set target budget to 2k-4k tokens instead of the older, much larger range.
  - Result: lower end is the normal case; upper end is reserved for technical sessions with many real decisions, failures, or partial state.
  - Key insight: compress by importance, not by transcript length.
- Topic / task:
  - Goal: define what "lossless" means for handoff.
  - Done: aligned on preserving concrete outcomes only: decisions, progress, discoveries, failures, current state, blockers, and next actions.
  - Result: side chat, social glue, repeated explanations, and transcript noise should be removed.
  - Key insight: trial-and-error should survive only as "what failed and what we learned," not as a blow-by-blow story.

FAILED / REVERTED:
- Large default handoff sizes were rejected because they turn the transfer block into another bloated prompt.
- Reminder or nudge ideas around `/clear` were rejected; behavior education is valid, but automated nudging is not.
- Bundling handoff as a sub-command inside vibecheck was rejected; handoff should stay a separate triggerable skill/repo.

CURRENT STATE:
- `handoff` repo exists and is linked from `vibecheck`.
- Skill is intended to work in coding tools, CLI tools, GUI coding tools, and chat products.
- Current implementation direction: tighten `handoff/SKILL.md` so trigger behavior, compression behavior, and resume behavior are explicit and portable.
- No file I/O is part of the skill behavior; copy-paste only.

OPEN ISSUES:
1. Skill spec still needs final tightening around lossless-compression rules and resume compactness — in progress.
2. A lightweight reference example is still useful so future edits do not drift into verbose recap style — planned.

NEXT:
1. Update `handoff/SKILL.md` to enforce 2k-4k target, lossless compression rules, and compact resume behavior.
2. Add one reference example file showing target density and structure.

---END---
```
