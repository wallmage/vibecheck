# Lossless Prompt Compressor — Technique Catalog

Read this after SKILL.md. Use it as a diagnostic menu when applying each pass — not every technique will apply to every document. Before/after pairs are teaching examples showing good compression patterns.

## Pass 1 Techniques (Mechanical — automatic)

### 1. Strip All Markdown Formatting

System prompts don't need to be pretty — they need to be parseable. LLMs extract the same information from `## Section Title` as from `Section Title`. Every `#`, `**`, `- `, `| |`, and ` ``` ` costs tokens for zero AI benefit.

Remove: header markers, bold/italic markers, bullet markers, table pipe syntax, code fence markers (preserve code content verbatim), blockquote markers, horizontal rules, inline list numbering, link syntax.

Table conversion:

Before (Markdown table):
| Platform | Framework | Language |
|----------|-----------|----------|
| iOS      | SwiftUI   | Swift    |

After (plain text):
Platform; Framework; Language
iOS; SwiftUI; Swift

Bullet list conversion:

Before:
- Fast and purposeful
- Physics-based
- Confirm, don't decorate

After:
Fast and purposeful; Physics-based; Confirm, don't decorate

Watch closely:
- `---` at document start is YAML frontmatter, not a horizontal rule. Preserve it.
- `#` followed by a hex digit (#FF0000) is a color, not a header. Preserve.
- `*` in regex or glob patterns (*.txt) is not italic. Preserve.
- `|` in shell commands, boolean expressions, or truth tables is not a table. Preserve.
- Python `#` comments, shell `|` pipes inside code blocks are content. Preserve.

### 2. Verify Zero Markdown Remains

After stripping, search the entire document for stray Markdown syntax. Common survivors: leftover `**`, `#` at line starts, `|` from unconverted tables, backticks around inline code.

Exclude content inside preserved code blocks — those characters are legitimate.

## Pass 2 Techniques (Creative — requires approval)

### 3. Cross-Reference Deduplication

Find facts stated multiple times. State each fact once in its canonical location, then replace all others with a short cross-reference.

Before (fact in 3 locations):
Line 196: "cap total free-tier subsidies at 3% of monthly revenue"
Line 542: "Free-tier is capped at 3% monthly revenue for cloud LLM subsidies"
Line 688: "Cap cloud LLM subsidy at 3% of monthly revenue"

After:
Line 196: "cap total free-tier subsidies at 3% of monthly revenue" (canonical)
Lines 542, 688: "Free-tier capped per S6" (compressed)

How to find duplicates: search for key numbers, percentages, time durations, and branded terms that appear more than once. Common culprits: pricing figures, performance targets, time limits, feature names repeated in overview + detail sections.

### 4. Compress Code Blocks to Inline Descriptions

Code samples in system prompts are reference material, not executable code. The AI uses the information to guide its own code generation — it doesn't copy-paste from the prompt. Replace code blocks with compact natural-language descriptions preserving all field names, types, and relationships.

Before (20+ lines of code):
struct UserProfile {
    var name: String
    var email: String
    var role: Role  // enum: admin, editor, viewer
    var createdAt: Date
}

After (2 lines):
struct UserProfile fields: name (String), email (String), role (Role enum: admin/editor/viewer), createdAt (Date).

Preserve: all field names, types, annotations, enum values, import statements, class/protocol names.
Remove: syntactic scaffolding (braces, indentation, decorative comments).

Exception: whitespace-semantic languages (Python, YAML, Makefile) — preserve these code blocks verbatim. Only compress code that uses braces/indentation for purely syntactic structure (Swift, JSON, TypeScript).

### 5. Compress JSON Config Blocks

Same principle as code blocks. Replace full JSON examples with compact schema descriptions.

Before (30+ lines of JSON):
{ "version": "1.0", "regions": [ { "region": "CN", "providers": [...] } ] ... }

After (1 paragraph):
Provider config: JSON with version, updated date, regions array. Each region: region code (CN/US/EU), strategy ("direct"/"aggregator"), providers array (name, endpoint, priority, max_latency_ms, cost_per_1k_tokens), fallback_timeout_ms.

### 6. Cut Version-Specific Breakdowns That Duplicate a Summary

If the document has both a summary table AND a per-version detailed breakdown covering the same information, propose cutting the detail and keeping the summary. If any information in the detail ISN'T in the summary, compress to 1-2 lines and append.

### 7. Summarize "Why This Matters" / Motivational Blocks

Product specs often include motivational explanations. Compress each to 1-2 sentences preserving the core insight:

Before (6 lines):
Why This Must Be Right From Day One: We need multi-region
support because the Great Firewall blocks all US providers. At maturity the
router manages 20-30 endpoints... (lengthy justification)

After (2 lines):
Why day one: GFW blocks US providers; at maturity router
manages 20-30 endpoints for 100+ countries; 2x cost difference at scale =
profit vs loss.

### 8. Compress Design Decision Rationales

Design decisions often include 3-4 paragraphs of reasoning where 1 sentence with key reasons suffices. Keep the decision and the top 2-3 reasons. Cut the narrative.

### 9. Compress Verbose Use Case Lists

When the document lists 5+ detailed use cases, compress each to a one-liner. The AI needs the pattern, not full paragraphs per use case.

### 10. Compress ASCII Art / UI Mockups

ASCII mockups cost many tokens. Replace with compact text descriptions that capture layout, key elements, and spec requirements embedded in the visual.

Before (10-line ASCII UI mockup):
+---------------------+
|  Welcome!           |
|  Your data matters. |
|  [Got it]           |
+---------------------+

After (1 line):
Welcome screen: "Your data matters" message with [Got it] button.

## Pass 3 Techniques (High-Fidelity — requires approval)

Pass 3 targets content that exists to serve a human reader but has zero impact on AI coding quality. The key question: "If I remove this, will the AI produce worse code or miss a spec requirement?"

### 11. Beginner Tutorials and Tool Installation Guides

Step-by-step instructions for installing tools, creating accounts, or learning IDEs. The AI doesn't need to know how to install software.

Before (800 words):
Day -2 — Tool Installation
Install your IDE from the app store. This takes 30-60 minutes...
Create a developer account ($99/year)...
If anything fails: Don't panic...

After (2 lines):
Day -2 — Tool Installation: Install and verify IDE, developer account, AI
coding tools, API keys, version control, analytics.

The compressed version preserves WHAT but removes HOW (human-only tutorial).

### 12. Practice Prompts and Learning Exercises

Prompts designed to help a beginner learn tools ("Try this practice prompt..."). The AI doesn't need someone else's practice exercises.

### 13. Day-by-Day Scheduling and Human Routines

Detailed schedules with wake-up times, breaks, and sleep times. The AI needs to know WHAT gets built each phase and any technical details, not WHEN the human eats dinner.

Compress day-by-day breakdowns into weekly summaries. Keep: feature names, technical requirements, key implementation details. Remove: time blocks, motivational pep talks, "commit message" suggestions, rest day descriptions.

Before (800 words):
11:00am: Wake up. Coffee.
12:00pm: Open document. Read the goals.
12:15pm: Open AI tool. Ask for guidance...

After (2 lines):
Daily pattern: read goals -> get AI guidance -> write code -> build -> fix
errors -> test -> commit. Build every 30min, commit every 2hr max.

### 14. Coaching and Motivational Content

"Don't panic," "Celebrate!", "Don't get discouraged" — these support a human's emotional state but have no impact on AI output quality.

Compress to the actionable core only. If there is no actionable core, remove entirely.

Boundary with Pass 2: Technique 7 (Pass 2) compresses motivational blocks whose primary purpose is factual — spec facts, numbers, or technical rationale buried in motivational prose. Technique 14 (Pass 3) removes blocks whose primary purpose is emotional support. For mixed blocks (90% motivation with one incidental fact): extract the fact into the nearest relevant section, then remove the motivational block in Pass 3.

### 15. Validation Tables and Checklists Already Implied by Specs

If the document has a table that validates every feature against design principles (and every feature passes), the table adds no information — features are already specified elsewhere.

Before (30-row validation table):
Feature; Criteria 1; Criteria 2; Score; Verdict
Feature A; YES; YES; 6/6; SHIP
Feature B; YES; YES; 5/6; SHIP
... (26 more rows all saying SHIP)

After (2 lines):
All 26 features passed the Design Principles Checklist.
Every feature scores YES on all Tier 1 and >=4/6 Tier 2. Verdict: SHIP all.

### 16. Competitive Comparison Tables (Motivational)

"We win on every dimension" tables motivate the human builder but the AI builds features based on specs, not competitive positioning.

Compress to 1-2 lines capturing the competitive stance, or remove if specs already define what to build.

### 17. Step-by-Step Workflow Examples for Humans

Minute-by-minute examples of "what your day looks like" — meant to teach a human the workflow rhythm. The AI doesn't follow a daily schedule.

## Pass 4 Techniques (Telegram — requires explicit permission)

Core principle: every word must carry information. If a word exists only to make text flow nicely for a human reader, it gets cut. LLMs reconstruct meaning from context without grammatical scaffolding.

### 18. Eliminate Bridge Phrases and Connective Tissue

Remove words that connect ideas for human readability but carry zero information.

Before: "This means that the user will be able to access their data from any device,
which is important because it enables a seamless cross-platform experience."

After: "User data accessible from any device; enables cross-platform experience."

Common bridge phrases to eliminate: "this means that", "which allows", "in order to", "the reason for this is", "it's important to note that", "as mentioned earlier", "for example", "in other words", "what this enables is", "the benefit of this approach is".

### 19. Convert Prose to Semicolon-Delimited Fragments

Full sentences become comma or semicolon-separated key-value fragments. Drop articles (a, an, the), drop "is/are/will be" where meaning is clear from context, drop "users can" padding.

Before: "The application uses a local-first architecture where all data is stored
on the device. This ensures the app works offline and provides instant response
times. Cloud sync happens in the background when connectivity is available."

After: "Local-first architecture; all data on-device; works offline, instant
response; background cloud sync when connected."

### 20. Collapse Multi-Sentence Explanations

When a paragraph uses 3-5 sentences to explain one concept, collapse to the essential fact.

Before: "The notification system is designed to be non-intrusive. Rather than
bombarding users with alerts, it uses a gentle reminder approach. Notifications
are batched and delivered at user-preferred times. Users can customize their
preferences, choosing between immediate, batched, or silent modes."

After: "Notifications: non-intrusive, batched at user-preferred times; modes:
immediate/batched/silent, configurable in settings."

### 21. Drop Implied Subjects and Obvious Context

When the subject is obvious from the section heading or context, don't repeat it.

Section: "8.3 Search Feature"

Before: "The search feature supports full-text search across all captured items.
The search feature also supports filtering by content type, date range, and tags."

After: "Full-text across all items; filter by type/date/tags; results list
with relevance ranking."

### 22. Use Compact Notation Patterns

Adopt shorthand patterns that LLMs parse effortlessly:

- Lists of options: use slashes — "immediate/batched/silent" not "immediate, batched, or silent"
- Conditional logic: use arrows — "offline -> local queue -> sync on reconnect"
- Ranges: use dashes — "3-5 items" not "three to five items"
- Relationships: use colons — "Auth: JWT + refresh tokens" not "Authentication uses JWT with refresh tokens"
- Enumerations: use parenthetical lists — "contentType (schedule/reminder/expense/article/note)"

### 23. Compress Repetitive Structural Patterns

When the document describes many similar items (features, screens, API endpoints), establish the pattern once, then use shorthand.

Before (5 paragraphs, each describing a screen):
"The Timeline screen displays a chronological list of all captured items.
At the top is a date filter bar. Each item shows a thumbnail, title, and
timestamp. Users can tap to view details or swipe to delete..."

After:
"Screen pattern: header component + scrollable list + item cards with actions.

Timeline: date filter bar; cards show thumbnail/title/timestamp; tap->detail, swipe->delete.
Search: search bar with real-time filter; cards show title/preview/relevance."
