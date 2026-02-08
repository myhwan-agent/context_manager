# Architecture (Draft)

We will build this around **LangGraph**.

## Concepts

### Event
An append-only record of what happened.
- observation / action / plan / tool / note

### Views (bounded context outputs)
Different consumers need different views:
- Planner context (compact, task-relevant)
- Debug context (richer logs)
- Retrieval context (memory hits)

### Namespaces (optional isolation)
Events can be tagged:
- perception
- planning
- tools
- human

Isolation can mean:
- separate summary streams per namespace
- or selectively include/exclude namespaces per view

## Proposed LangGraph pipeline (M1)

State:
- events (bounded list)
- summaries (per namespace + global)
- memory_store handle (pluggable)

Nodes (initial):
1) ingest_event
2) window_history (keep last N events)
3) summarize (stub for now)
4) build_planning_context

Outputs:
- planning_context: str

## Open questions to lock with you
1) Language/runtime: Python only? (LangGraph is best-supported in Python)
2) Do we need persistence now (sqlite/jsonl) or later?
3) For 1 FPS: do we summarize every frame or on triggers (e.g., action boundaries)?
