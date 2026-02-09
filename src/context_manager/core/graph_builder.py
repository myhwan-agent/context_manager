from __future__ import annotations

from typing import Any, Dict

from .context_factory import RequestContext


class ContextManagerGraph:
    """LangGraph-based context manager graph.

    This is a runnable skeleton: it does not call a real VLM yet. It wires nodes
    so that data can flow end-to-end and produce summary/plan/history.
    """

    def __init__(self) -> None:
        try:
            self._graph = self._build().compile()
        except ModuleNotFoundError as e:
            if e.name == "langgraph":
                raise ModuleNotFoundError(
                    "langgraph is not installed. Create a venv and run: pip install -e ."
                ) from e
            raise

    def invoke(self, state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
        # LangGraph expects a dict-like state.
        return self._graph.invoke(state)  # type: ignore[return-value]

    @staticmethod
    def _build():
        # import inside to keep package importable without langgraph installed
        from langgraph.graph import StateGraph

        from ..nodes.context_source import context_collect
        from ..nodes.summarizer import summarize_context
        from ..nodes.planner import plan_actions

        g = StateGraph(dict)
        g.add_node("context_collect", context_collect)
        g.add_node("summarize", summarize_context)
        g.add_node("plan", plan_actions)

        g.set_entry_point("context_collect")
        g.add_edge("context_collect", "summarize")
        g.add_edge("summarize", "plan")
        g.set_finish_point("plan")
        return g
