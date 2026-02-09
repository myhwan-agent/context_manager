from __future__ import annotations

from ..core.graph_builder import CMState


def build_planning_context(state: CMState) -> CMState:
    """Build the final context string given to the planner model."""

    timeline = "\n".join(f"[{e.type}] {e.text}" for e in state.events)
    if state.summary.strip():
        state.planning_context = f"# SUMMARY\n{state.summary}\n\n# TIMELINE\n{timeline}".strip()
    else:
        state.planning_context = timeline
    return state
