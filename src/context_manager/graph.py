from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .types import ContextEvent


@dataclass
class CMState:
    """LangGraph state for ContextManager.

    - events: bounded recent history (for planner context)
    - summary: compressed representation (trigger-based updates)
    - planning_context: final string handed to the planner model

    Memory persistence is intentionally excluded for now; later we'll add a node
    that POSTs to an external local-memory DB.
    """

    events: list[ContextEvent] = field(default_factory=list)
    summary: str = ""
    planning_context: str = ""


# ---------- policies ----------

def default_should_summarize(event: ContextEvent) -> bool:
    """Trigger-based summarization policy.

    Designed for 1 FPS loops: avoid per-frame summarization.

    Triggers (default):
    - action / plan events
    - meta.trigger_summary == True
    """

    if event.type in ("action", "plan"):
        return True
    if event.meta and event.meta.get("trigger_summary") is True:
        return True
    return False


# ---------- graph builder ----------

def build_graph(
    *,
    max_history: int = 50,
    should_summarize: Callable[[ContextEvent], bool] = default_should_summarize,
    summarizer: Optional[Callable[[str, list[ContextEvent]], str]] = None,
):
    """Return a compiled LangGraph graph.

    `summarizer(prev_summary, new_events)->summary` can be plugged later.
    If omitted, we keep a simple heuristic summary.
    """

    # Import inside to keep package importable without langgraph installed.
    from langgraph.graph import StateGraph

    def ingest_event(state: CMState, event: ContextEvent) -> CMState:
        state.events.append(event)
        return state

    def window_history(state: CMState) -> CMState:
        if len(state.events) > max_history:
            state.events = state.events[-max_history:]
        return state

    def summarize(state: CMState, event: ContextEvent) -> CMState:
        if not should_summarize(event):
            return state

        if summarizer is not None:
            state.summary = summarizer(state.summary, state.events)
            return state

        # Heuristic placeholder summary: keep last action/plan + last observation.
        last_action = next((e for e in reversed(state.events) if e.type == "action"), None)
        last_plan = next((e for e in reversed(state.events) if e.type == "plan"), None)
        last_obs = next((e for e in reversed(state.events) if e.type == "observation"), None)

        parts: list[str] = []
        if last_plan:
            parts.append(f"PLAN: {last_plan.text}")
        if last_action:
            parts.append(f"LAST_ACTION: {last_action.text}")
        if last_obs:
            parts.append(f"LAST_OBS: {last_obs.text}")

        state.summary = "\n".join(parts)
        return state

    def build_planning_context(state: CMState) -> CMState:
        # planner gets: summary + bounded timeline
        timeline = "\n".join(f"[{e.type}] {e.text}" for e in state.events)
        if state.summary.strip():
            state.planning_context = f"# SUMMARY\n{state.summary}\n\n# TIMELINE\n{timeline}".strip()
        else:
            state.planning_context = timeline
        return state

    g = StateGraph(CMState)
    g.add_node("ingest_event", ingest_event)
    g.add_node("window_history", window_history)
    g.add_node("summarize", summarize)
    g.add_node("build_planning_context", build_planning_context)

    # Linear pipeline for now.
    # We'll add branching later (e.g., isolate namespaces, memory-post node).
    g.set_entry_point("ingest_event")
    g.add_edge("ingest_event", "window_history")
    g.add_edge("window_history", "summarize")
    g.add_edge("summarize", "build_planning_context")
    g.set_finish_point("build_planning_context")

    return g.compile()
