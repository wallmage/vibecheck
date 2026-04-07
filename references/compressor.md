# Instruction File Compressor

Compress AI-facing instruction files without deleting information the model needs. Four-pass process with increasing aggressiveness. Pass 1 removes packaging. Pass 2 vacuum-seals. Pass 3 removes what only a human would read. Pass 4 converts everything to shorthand.

## Modes

- Strict Lossless: Pass 1 plus approved Pass 2 edits. Preserve all facts and keep the document human-usable. This is the default.
- AI-Lossless: Pass 3 on top of Strict Lossless. Remove or compress human-only scaffolding while preserving what the model needs.
- AI-Only: Pass 4 on top of earlier passes. Rewrite for maximum density, not pleasant human reading.

Do not move beyond Strict Lossless unless the user clearly wants more compression.

## Hard Preservation Rules

1. Never renumber sections or subsections, even if sections are removed. Section numbers are cross-reference anchors ("see S8.7.3", "per S6"), not formatting.
2. Never delete a fact just because it feels repetitive unless the same fact survives canonically elsewhere and the replacement clearly points back to it.
3. Never strip URLs, file paths, identifiers, API names, class names, field names, enum values, version numbers, limits, percentages, or dates unless the user explicitly approves.
4. Never treat literal Markdown examples as disposable formatting when the document teaches Markdown or contains syntax examples.
5. Never compress whitespace-semantic code blocks (Python, YAML, Makefile) into prose unless the user explicitly asks for that tradeoff.
6. Prefer keeping a few extra tokens over introducing ambiguity.

Additional vibecheck-specific preservation rules:
- Trigger patterns, shell commands, file paths — exact syntax, no abbreviation
- Migration tables — compress format but keep EVERY row AND every note with behavioral meaning (e.g., "Single-arg compiles but wrong semantics" warns about a subtle bug; "Chrome only" IS the rule)
- Concurrency annotations (nonisolated, @concurrent, Sendable, actor isolation)
- Platform/region constraints (e.g., "unavailable China")
- Decision references (e.g., "DEC-003") — these link to design decisions
- When in doubt, keep it. Dropping a behavioral rule silently is worse than keeping 10 extra lines.

## Pass 1: Mechanical Compression (automatic)

These transformations never delete semantic content — safe to apply immediately.

### What to Remove

- `#`, `##`, `###` header markers (keep heading text and any section number)
- `**bold**` and `*italic*` markers
- `- ` bullet markers (use semicolons or natural prose instead)
- `| table |` pipe syntax (convert to semicolon-delimited inline format)
- ` ``` ` code fences (strip the fence markers, preserve all code content verbatim — code compression happens in Pass 2)
- `> ` blockquote markers
- `---` horizontal rules (NOT YAML frontmatter delimiters — if the document begins with `---`, preserve the frontmatter block intact)
- Numbered list formatting (`1. `, `2. `) ONLY for inline lists — NEVER for section/subsection headers
- Link syntax `[text](url)` (keep the URL or text, whichever is useful)

Keep blank lines between sections and paragraphs — they cost ~1 token each but provide structural signal that helps AI parse long prompts.

### Watch Closely

- Distinguish section numbering from list numbering. Before Pass 1, catalog all section/subsection numbers. After Pass 1, verify every one survived.
- Hash in hex colors (#FF0000), asterisks in regex or globs (*.txt), pipes in shell commands or truth tables — these are content, not Markdown. When uncertain, preserve.
- Preserve YAML frontmatter if it exists at the top of the file.
- Content inside preserved code blocks: Python comments (#), shell pipes (|), and inline code references are legitimate content, not Markdown survivors.

## Pass 2: Fact-Preserving Compression (requires approval)

These transformations involve judgment. Propose as a numbered list with estimated savings and wait for per-item approval.

Technique categories:
- Deduplicate repeated facts: keep one canonical statement, replace others with cross-references
- Compress code blocks to inline descriptions: preserve field names, types, and relationships
- Compress JSON config blocks to compact schema descriptions
- Cut version-specific breakdowns that duplicate a summary
- Collapse long rationales to one sentence preserving the real reasons
- Compress verbose use-case lists to one-liners per case
- Replace ASCII mockups with compact layout descriptions
- Compress motivational blocks that also contain real technical facts

Proposal format:
```text
1. [Dedup] S6, lines 542 and 688
   Original: two repeated statements of the same subsidy cap.
   Replacement: "Free-tier subsidy cap: per S6."
   Reason: canonical fact already exists in S6; removes duplication only.
   Est. savings: ~40 words. Risk: low.
```

On large documents (30+ proposals), batch into groups of 5-10 by type for easier review.

### Validation Criteria

Approve a Pass 2 item only if all of these remain true:
- Every fact still exists.
- The AI could make the same coding and architecture decisions after the edit.
- The rewrite is not ambiguous.
- A human could still trace the fact back to its canonical section.

If any are uncertain, keep the original.

## Pass 3: High-Fidelity Compression (optional, requires approval)

Pass 3 removes or sharply compresses material that helps human readers but does not improve model output. The key question: "If I remove this, will the AI produce worse code or miss a spec requirement?" If no — it's a candidate.

Typical targets:
- Beginner tutorials and tool installation guides
- Practice prompts and learning exercises
- Day-by-day schedules, wake/sleep routines
- Coaching and motivational content
- Validation matrices that only confirm what specs already say
- Competitive comparison tables that add positioning but no implementation guidance
- Step-by-step workflow examples for humans

Decision test for each candidate:
1. Does it contain a requirement, constraint, field, number, or architecture decision? Keep the useful content.
2. Would removing it make the AI produce worse code, plans, or miss a spec? Keep it.
3. Is the remaining value mostly emotional support, tutorial scaffolding, or human scheduling? Propose removal or heavy compression.

When compressing (not removing), keep WHAT and WHY. Remove HOW-for-humans.

### Pass 2 vs Pass 3 Boundary

Pass 2 compresses motivational blocks whose primary purpose is factual — spec facts, numbers, or technical rationale buried in motivational prose. Pass 3 removes blocks whose primary purpose is emotional support. For mixed blocks (90% motivation with one incidental fact): extract the fact into the nearest relevant section, then remove the block in Pass 3.

## Pass 4: Telegram Rewrite (optional, requires explicit permission)

Pass 4 rewrites the entire document top to bottom in telegram-style shorthand. Unlike Passes 1-3 (surgical, section-by-section edits), this is a full rewrite. Only for documents where the AI is the sole consumer.

### When to Offer

After completing earlier passes, if the user wants further compression:

"Pass 4 rewrites everything in ultra-dry telegram style — fragments instead of sentences, no bridge phrases, maximum density. It typically cuts an additional 25-40% on top of Pass 1-3. The result reads like shorthand notes, not prose — but modern LLMs parse it with full fidelity. Want me to proceed?"

### Style Rules

- Drop bridge phrases and connective tissue ("this means that", "which allows", "in order to")
- Prefer semicolon-delimited fragments over full sentences
- Drop articles (a, an, the) and "is/are/will be" where meaning is clear from context
- Drop obvious subjects when the section heading provides context
- Use compact notation: slashes for options (immediate/batched/silent), arrows for flow (offline -> local queue -> sync), dashes for ranges (3-5), colons for relationships (Auth: JWT + refresh)
- Keep proper nouns, numbers, URLs, file paths, field names, and section numbers exact
- Add a few words back if a fragment could be interpreted two ways — precision beats brevity

### Quality Check

Verify:
- All section/subsection numbers survived
- All cross-references still point to valid sections
- No facts, specs, numbers, or names were lost
- Fragments are unambiguous even without full sentences
- Any modern LLM would produce identical code and architecture decisions from this version as from the original

## Edge Cases

- **Short documents (under 1,000 words):** Warn that savings will be minimal.
- **Code-heavy prompts (>50% code):** Preserve Python/YAML/Makefile code blocks verbatim — whitespace is semantic. Only compress code with braces/indentation for purely syntactic structure (Swift, JSON, TypeScript).
- **Already-compressed input:** Check for compression indicators: no Markdown, telegram-style fragments, semicolon-delimited lists. Report diminishing returns.
- **Non-English prompts:** Word count is approximate for CJK languages. Report character count alongside word count. Token estimation: words x 1.3 for English, x 2.5 for CJK.
- **Embedded URLs and file paths:** Keep ALL URLs and file paths intact. Only strip the Markdown link syntax `[text](url)`, never the URL itself.
- **Pass skipping:** Pass 1 is always required. Passes 2, 3, and 4 can each be skipped independently.
- **Mixed-language documents:** Preserve non-English content verbatim — compress the English scaffolding around it.
- **Documents about Markdown:** Treat literal Markdown syntax inside examples and instructional passages as semantic content.
- **Non-Markdown uses of Markdown characters:** Hash in hex colors (#FF0000), asterisks in regex or globs (*.txt), pipes in truth tables or shell commands — scan for these before stripping. When uncertain, preserve.
- **Very large documents (exceeding context window):** Process in chunks by top-level section. Apply Pass 1 to each chunk independently, then reassemble before Passes 2-4 (which need full-document context for deduplication).
- **Rollback:** Keep a backup before each pass. Restore from backup rather than trying to reverse individual edits.

## Operating Sequence

1. Measure baseline: lines, words, estimated tokens (words x 1.3 for English, x 2.5 for CJK).
2. Copy to working file. Never edit the original in place.
3. Apply Pass 1. Report results.
4. Propose Pass 2 candidates grouped by type, with estimated savings per item.
5. Apply only user-approved items. Re-measure and report the Strict Lossless result.
6. If the user wants more: propose Pass 3 candidates. Apply only approved items. Report.
7. If the user wants maximum compression: offer Pass 4. Back up before rewriting. Report.
8. Deliver final summary table with all stages.

## Reporting

Always finish with a summary table:

Stage; Words; Est. Tokens; Reduction
Original; 37,237; ~48,400; -
After Pass 1; 33,472; ~43,500; 10%
After Pass 2; 31,126; ~40,500; 16%
After Pass 3; 25,730; ~33,400; 31%
After Pass 4; 16,200; ~21,100; 56%

Also report:
- Mode delivered: Strict Lossless, AI-Lossless, or AI-Only
- What was approved vs skipped
- Whether any sections were preserved due to ambiguity risk
- Whether the final output is still human-friendly or now AI-only

## Expected Savings

Typical compression ratios on product specs and master plans:

- Pass 1 (Markdown stripping): 10-25% word reduction
- Pass 2 (creative compression): additional 5-15%
- Pass 3 (high-fidelity, human-only removal): additional 15-25%
- Pass 4 (ultra-dry telegram rewrite): additional 25-40% on top of Pass 1-3
- Total (all 4 passes): 50-65% reduction

Do not promise these numbers on already-lean inputs.

## Rules

1. Never delete spec information. A few extra tokens are cheaper than a missing detail that causes the AI to hallucinate.
2. Never touch section/subsection numbering. When deleting sections in Pass 2/3, keep original numbers — never renumber.
3. Preserve blank lines between sections. They cost almost nothing and help AI attention.
4. Don't reorder sections. The document's structure is intentional. Compress in-place.
5. In Passes 1-3, don't use lossy abbreviations like "dev" for "development". Pass 4 permits common technical abbreviations (dev, config, auth, impl, etc.).
6. Pass 1 is automatic. Pass 2 and 3 require approval. Always present proposals and wait.
7. Pass 4 requires explicit user permission. Always back up the pre-Pass-4 version.
8. Work section by section. Systematic work catches more and makes fewer mistakes.
9. Measure at every stage. Report word count and estimated token reduction with percentages.
10. Precision over brevity in Pass 4. If a telegram fragment is ambiguous, add words.

## Technique Reference

For the full catalog of 23 numbered techniques with before/after examples, see [compression-techniques.md](compression-techniques.md).
