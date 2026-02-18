# Context History Strategy (Plan–Act loop)

Goal: keep context small, relevant, and robust during a long-horizon Plan→Act→Verify→(Replan) loop.

## Problem framing
- Initial long-horizon plan: generate within ~10s.
- Per-step verify: within ~1s using latest observation + execution result.
- History grows quickly (frames + tool chatter + errors).

## Practical “hot” patterns (2023–2025)

### 1) Event sourcing + **dual memory** (working set + long-term)
- Maintain a small *working context* (recent window + rolling summary).
- Persist full event log elsewhere (future DB) and retrieve selectively.
- This maps to **virtual context / hierarchical memory** ideas.

Reference:
- MemGPT (virtual context management / hierarchical memory): https://arxiv.org/abs/2310.08560

### 2) Trigger-based summarization at **boundaries**, not per frame
Summarize only when it matters:
- action boundary (after executor result)
- plan boundary (subtask completion / phase change)
- failure boundary (error or verification fail)

This is the simplest way to hit ~1 FPS without constantly paying summarization.

### 3) Hierarchical summaries (episode → session)
- Episode summary: per subtask / per action chunk
- Session summary: roll-up of episodes
- Keep “key-value state” style facts (object locations, constraints, last known goal)

Related inspiration:
- Generative Agents (memory stream + reflection): https://arxiv.org/abs/2304.03442

### 4) Plan–Act interleaving (ReAct-style traces)
Keep “thought-like” traces short and structured:
- PLAN: what we’re trying
- ACT: what we did
- OBS/RESULT: what happened
- NEXT: what to do next

Reference:
- ReAct: https://arxiv.org/abs/2210.03629

### 5) Failure-driven reflection (replanning trigger)
On failure, add a short “reflection record” (why failed / what to try next) and then replan.

Reference:
- Reflexion: https://arxiv.org/abs/2303.11366

## Proposed spec for this repo (first cut)

### State representation
- `recent_events`: last N events (bounded)
- `rolling_summary`: compressed text for older events
- `facts`: structured key facts (e.g., object→global pose) extracted from knowledge source + updates
- `current_plan`: current long-horizon plan (may be chunked)
- `step_index`: current step

### Compression policy (cheap, effective)
- Always append full events to the *event log* (future DB)
- In working state:
  - keep last N events verbatim
  - when size exceeds budget, fold oldest K events into `rolling_summary`
  - maintain `facts` separately so compression doesn’t lose critical state

### Verification context
Verifier sees only:
- last action
- executor result
- latest observation (encoded text)
- current subtask + constraints
- minimal facts

This keeps verification under 1s.
