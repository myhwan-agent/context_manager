# Context Manager — Goals (Draft)

Target use-case: Vision-Language Model (VLM) driving robot actions.
- Model: qwen3-vl-32b
- Runtime target: ~1 FPS loop
- Problem: context window grows quickly; long contexts degrade understanding + cost.

## Core responsibilities

1) **Context summarization / compression**
- Produce a compact state representation suitable for planning.
- Preserve task-relevant details; drop noise.

2) **Context record / memory**
- Store observations, decisions, actions, outcomes.
- Support retrieval by relevance and recency.

3) **Context history**
- Provide recent timeline and key turning points.
- Allow bounded “N steps back” reconstruction.

4) **Context isolate (optional)**
- Separate concerns: planning vs perception vs tool outputs.
- Prevent contamination/overfitting to tool chatter.

## Non-goals (for now)
- Full agent framework.
- Heavy external dependencies unless needed.

## First milestones
- M1: Minimal LangGraph pipeline that ingests events and outputs a planning context.
- M2: Add pluggable summarizer + memory store interfaces.
- M3: Add history windowing + isolation namespaces.
