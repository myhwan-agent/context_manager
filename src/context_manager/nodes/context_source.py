from __future__ import annotations

from ..core.graph_builder import CMState
from ..core.context_factory import ContextEvent


def ingest_event(state: CMState, event: ContextEvent) -> CMState:
    state.events.append(event)
    return state


def window_history(state: CMState, *, max_history: int) -> CMState:
    if len(state.events) > max_history:
        state.events = state.events[-max_history:]
    return state
