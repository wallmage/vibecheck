# Waste Patterns

Use these when explaining spend to non-technical users. Each pattern has a plain-language description, an analogy, and a teaching script.

## The 15 Patterns

### Tier 1 — The Big 3 (70-80% of waste)

#### 1. Idle narration (30-40%)

The AI says it is about to act, then acts in the next turn. The narration turn added cost without changing the repo.

**Analogy:** A mechanic announcing "now I'll open the hood" before opening the hood.

**Teaching script:** "The AI said 'OK, now I'll fix that for you' — then actually fixed it in the NEXT message. That 'OK now I'll' message did nothing but cost you money."

#### 2. Context rot (15-25%)

Long sessions become expensive because every later turn re-reads more old context. Sessions over 40 turns cost 3-5x what shorter sessions cost per turn.

**Analogy:** A meeting where everyone re-reads all previous meeting notes before speaking.

**Teaching script:** "Your conversation went on for 60+ messages without starting fresh. Each new message got more expensive because the AI re-read all 59 previous messages."

#### 3. Ping-pong debugging (10-20%)

Fix, break, retry loops compound cost because each attempt carries the whole failed history forward.

**Analogy:** Fixing one leak, causing another, then charging for a full inspection each time.

**Teaching script:** "The AI tried to fix something, broke it differently, tried again, broke it again... each attempt re-read the entire conversation including all the failed attempts."

### Tier 2 — The Mechanics (15-20%)

#### 4. Verbose tool output (5-10%)

Large command output enters the conversation and gets re-read on future turns.

**Analogy:** Carrying a 500-page report in your backpack all day.

**Teaching script:** "The AI ran a command that spit out 500 lines of technical output. That output stayed in the conversation and got re-read on EVERY future message."

#### 5. Unchained commands (5-10%)

Independent shell commands are run in separate turns instead of one combined action.

**Analogy:** Making two trips to the grocery store instead of carrying both bags once.

**Teaching script:** "The AI ran one command, waited for your response, then ran another. It could have run both at once."

#### 6. Codebase wandering (5-10%)

The agent explores many files before taking action. 5+ consecutive read/search turns before any edit.

**Analogy:** Opening every drawer in an office to find one stapler.

**Teaching script:** "The AI didn't know where things were, so it opened file after file looking around — 8 files before actually doing anything."

#### 7. Unbatched edits (3-5%)

The agent edits multiple files in separate turns when one grouped turn would do.

**Analogy:** A tailor making one stitch, putting down the needle, then picking it up again.

**Teaching script:** "The AI edited three different files in three separate messages instead of all at once."

### Tier 3 — The Tail (5-10%)

#### 8. File re-reads (2-4%)

Same file read 2+ times per session. Content is already in context after the first read.

**Analogy:** Re-reading a page in a book you just read 30 seconds ago.

**Teaching script:** "The AI opened the same file twice in one conversation. It already had the content — reading it again just cost you more money for zero new information."

#### 9. Sleep/poll loops (2-4%)

Waiting with sleep+check instead of using --wait flags or run_in_background.

**Analogy:** Calling the restaurant every 2 minutes to ask if your table is ready, instead of just leaving your number.

**Teaching script:** "The AI kept checking 'is it done yet?' every few seconds instead of just waiting for a notification. Each check re-read your entire conversation."

#### 10. Failed retries (2-4%)

Broken command retried without fixing the underlying issue.

**Analogy:** Pushing a locked door harder instead of looking for the key.

**Teaching script:** "The AI ran a broken command, got an error, and ran the exact same command again hoping for a different result. The error message stayed in the conversation being re-read on every future turn."

#### 11. Schema lookups (1-3%)

Looking up tool schemas the AI already knows.

**Analogy:** Googling your own phone number.

**Teaching script:** "The AI looked up what tools it has access to — but it already knows that. The lookup result entered the conversation and got re-read on every message after."

#### 12. Git ceremony (1-2%)

Consecutive git-only turns that could be chained with `&&`.

**Analogy:** Making four separate phone calls when one would do.

**Teaching script:** "The AI ran `git add`, then `git status`, then `git commit`, then `git push` — four separate messages. `git add -A && git commit -m 'done' && git push` is one message."

### Tier 4 — Always-On Agents (OpenClaw, etc.)

#### 13. Idle heartbeats (20-40% of always-on cost)

Agent wakes up every 5 minutes, re-reads SOUL.md + full memory, finds nothing to do. A no-op heartbeat costs $0.01-0.10.

**Analogy:** A security guard who walks the entire building every 5 minutes, reads every sign on every door, and reports "nothing happened" every time.

**Teaching script:** "Your agent woke up 288 times today. 280 of those times, nothing had changed — but each wake-up re-read your entire personality file and memory. That's like paying for 280 full inspections when 8 would have been enough."

#### 14. Workspace file bloat (10-20% of always-on cost)

SOUL.md + AGENTS.md + USER.md injected into every wake-up. Typical setup = 35K tokens re-read per message.

**Analogy:** Carrying a 50-page employee handbook everywhere you go — even to get coffee.

**Teaching script:** "Every time your agent wakes up, it re-reads 35,000 words of personality files. Most of that text is coaching and explanation that was useful when you wrote it, but the AI only needs the behavioral rules. Compressing those files can cut wake-up cost by 60%."

#### 15. Memory accumulation (10-15% of always-on cost)

Session history grows without pruning. After 100+ messages, every new message re-reads everything.

**Analogy:** A diary that you have to read cover-to-cover before writing today's entry.

**Teaching script:** "Your agent's memory has grown to 100+ entries. Every new wake-up re-reads ALL of them. It's like reading 3 months of diary entries just to write what happened today. Archiving old entries and keeping a summary would cost a fraction."

## Subscription Tier Reference

Use these when explaining "subscription vs reality" in Lesson 1:

| Provider | Tier | Monthly | Approximate API Value |
|---|---|---|---|
| Claude | Pro | $20 | ~$200 |
| Claude | 5x | $100 | ~$1,000 |
| Claude | Max | $200 | ~$4,000 |
| OpenAI | Plus | $20 | ~$100 |
| OpenAI | Pro | $200 | ~$3,000 |
| Cursor | Pro | $20 | ~200 premium requests |

If the tier is unknown, say "Your subscription covers a certain amount of AI usage per month."

## Plain English Glossary

Use these definitions when the user doesn't know a term. Drop them naturally into conversation — don't dump a glossary on them.

- **Token**: Roughly one word. "Hello, how are you?" is about 6 tokens. You pay per token.
- **Context**: Everything the AI is currently holding in its head — your messages, its responses, any files it read, any command output. It all adds up.
- **Context window**: The maximum amount the AI can hold at once. Think of it like a whiteboard — when it fills up, old stuff falls off.
- **Turn / message**: One back-and-forth. You send something → AI responds. That's one turn. Each turn re-reads the entire context.
- **Instruction file**: A file in your project that tells the AI how to behave (CLAUDE.md, AGENTS.md, .cursorrules, etc.). It gets re-read every single turn.
- **Cache**: When the AI re-reads your conversation, the provider can skip re-processing parts it's already seen — like a speed-reader skimming pages they've read before. This "cache read" is cheaper than reading fresh, but still not free.
- **Session**: One continuous conversation from start to finish. Starting a new session resets the context — that's why clearing helps.

## What Tokens Are

Use this when explaining in Lesson 1:
"A token is roughly one word. This sentence is about 12 tokens. Every time you send a message, the AI reads ALL your previous messages (costs tokens) and writes a response (costs more tokens). The reading part is cheap per-word, but the AI re-reads EVERYTHING every single time."

## The Punchline

Use at the end of Lesson 2:
"The AI spends most of your money RE-READING, not THINKING. The cost of one unnecessary message isn't just that message — it's the cost of re-reading everything that came before it. Message #50 in a conversation costs roughly 50x what message #1 costs."
