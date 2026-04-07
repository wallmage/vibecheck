# Waste Patterns

Use these analogies when explaining spend to non-technical users.

## Core patterns

### Idle narration

The AI says it is about to act, then acts in the next turn. The narration turn added cost without changing the repo.

Analogy: a mechanic announcing "now I'll open the hood" before opening the hood.

### Context rot

Long sessions become expensive because every later turn re-reads more old context.

Analogy: a meeting where everyone re-reads all previous notes before speaking.

### Verbose output

Large command output enters the conversation and gets re-read on future turns.

Analogy: carrying a 500-page report in your backpack all day.

### Codebase wandering

The agent explores many files before taking action.

Analogy: opening every drawer in an office to find one stapler.

### Ping-pong debugging

Fix, break, retry loops compound cost because each attempt carries the whole failed history forward.

Analogy: fixing one leak, causing another, then charging for a full inspection each time.

### Unchained commands

Independent shell commands are run in separate turns instead of one combined action.

Analogy: making two trips to the store instead of carrying both bags once.

### Unbatched edits

The agent edits multiple files in separate turns when one grouped turn would do.

Analogy: a tailor making one stitch, putting down the needle, then picking it up again.

## Always-on patterns

### Idle heartbeats

An always-on agent wakes up, rereads its memory, and finds nothing to do.

### Workspace file bloat

Large personality and rules files are reread on every wake-up.

### Memory accumulation

The session history grows without pruning, so each new wake-up gets more expensive.
