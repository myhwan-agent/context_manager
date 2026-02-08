from __future__ import annotations

from typing import Optional

from .types import ContextEvent


class ContextManager:
    """Ingests events and produces bounded planning context.

    Minimal in-memory manager. LangGraph wiring lives in `context_manager.graph`.
    """

    def __init__(self, *, max_history: int = 50):
        self.max_history = max_history
        self._events: list[ContextEvent] = []

    def add(self, event: ContextEvent) -> None:
        self._events.append(event)
        if len(self._events) > self.max_history:
            self._events = self._events[-self.max_history :]

    def events(self, *, namespace: Optional[str] = None) -> list[ContextEvent]:
        if namespace is None:
            return list(self._events)
        return [e for e in self._events if e.namespace == namespace]

    def planning_context(self) -> str:
        """Naive context string (placeholder).

        Next: replace with summarization/compression + retrieval.
        """
        return "\n".join(f"[{e.type}] {e.text}" for e in self._events)
