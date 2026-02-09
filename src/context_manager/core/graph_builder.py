from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from ..nodes.context_source import ingest_event, window_history
from ..nodes.planner import build_planning_context
from ..nodes.summarizer import default_should_summarize, summarize
from .context_factory import ContextEvent


@dataclass
class CMState:
    """LangGraph state for ContextManager."""

    events: list[ContextEvent] = field(default_factory=list)
    summary: str = ""
    planning_context: str = ""


def build_graph(
    *,
    max_history: int = 50,
    should_summarize: Callable[[ContextEvent], bool] = default_should_summarize,
    summarizer: Optional[Callable[[str, list[ContextEvent]], str]] = None,
):
    """Return a compiled LangGraph graph.

    We keep the graph builder in core/, while node implementations live in nodes/.
    """

    # Import inside to keep package importable without langgraph installed.
    from langgraph.graph import StateGraph

    g = StateGraph(CMState)

    # wrap nodes to inject config args
    g.add_node("ingest_event", ingest_event)
    g.add_node("window_history", lambda state: window_history(state, max_history=max_history))
    g.add_node(
        "summarize",
        lambda state, event: summarize(
            state,
            event,
            should_summarize=should_summarize,
            summarizer=summarizer,
        ),
    )
    g.add_node("build_planning_context", build_planning_context)

    g.set_entry_point("ingest_event")
    g.add_edge("ingest_event", "window_history")
    g.add_edge("window_history", "summarize")
    g.add_edge("summarize", "build_planning_context")
    g.set_finish_point("build_planning_context")

    return g.compile()
