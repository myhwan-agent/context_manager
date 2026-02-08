from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Optional


EventType = Literal[
    "observation",  # perception results (e.g., VLM frame understanding)
    "action",       # action executed
    "plan",         # plan proposed
    "tool",         # tool output
    "note",         # human/operator note
]


@dataclass(frozen=True)
class ContextEvent:
    type: EventType
    text: str
    ts: datetime = datetime.utcnow()
    meta: dict[str, Any] | None = None
    namespace: str = "default"  # for optional isolation (e.g., "perception"|"planning"|"tools")


class ContextManager:
    """Ingests events and produces bounded planning context.

    This is intentionally minimal. We will wire it into LangGraph once we lock the
    state shape + node responsibilities.
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
        """Return a naive context string (placeholder).

        Next: replace with summarization/compression + memory retrieval.
        """
        lines: list[str] = []
        for e in self._events:
            lines.append(f"[{e.type}] {e.text}")
        return "\n".join(lines)
