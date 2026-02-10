from __future__ import annotations

from typing import Any, Dict

from ..core.context_factory import ContextEvent, RequestContext
from ..core.history import HistoryBuffer


def init_history(state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
    """Initialize a HistoryBuffer in state if not present."""

    if "history_buffer" not in state:
        state["history_buffer"] = HistoryBuffer(max_recent_events=30, max_summary_chars=4000)
    return state  # type: ignore[return-value]


def update_history_from_events(state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
    """Take `history` events (list[ContextEvent]) and fold into HistoryBuffer."""

    hb: HistoryBuffer = state.get("history_buffer")  # type: ignore[assignment]
    events: list[ContextEvent] = state.get("history", []) or []

    # keep a copy of the raw recent list too, but main working set is hb
    hb.extend(events)

    state["planner_context"] = hb.build_planner_context()
    return state  # type: ignore[return-value]
