from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .context_factory import ContextEvent


@dataclass
class HistoryBuffer:
    """Working-set history buffer.

    Keeps a small recent window + a rolling summary of older events.

    This is intentionally model-agnostic; summarization can be plugged later.
    """

    max_recent_events: int = 30
    max_summary_chars: int = 4000

    recent: list[ContextEvent] = field(default_factory=list)
    rolling_summary: str = ""

    def append(self, event: ContextEvent) -> None:
        self.recent.append(event)
        if len(self.recent) > self.max_recent_events:
            # move oldest 1 event into summary (cheap heuristic)
            old = self.recent.pop(0)
            self._fold_into_summary([old])

    def extend(self, events: list[ContextEvent]) -> None:
        for e in events:
            self.append(e)

    def _fold_into_summary(self, events: list[ContextEvent]) -> None:
        # naive fold: append line(s)
        add = "\n".join(f"[{e.type}] {e.text}" for e in events)
        if self.rolling_summary:
            self.rolling_summary = (self.rolling_summary + "\n" + add).strip()
        else:
            self.rolling_summary = add.strip()

        # enforce summary budget
        if len(self.rolling_summary) > self.max_summary_chars:
            # trim from the front
            self.rolling_summary = self.rolling_summary[-self.max_summary_chars :]

    def build_planner_context(self) -> str:
        """Planner context: rolling_summary + recent timeline."""

        recent_txt = "\n".join(f"[{e.type}] {e.text}" for e in self.recent)
        if self.rolling_summary.strip():
            return f"# ROLLING_SUMMARY\n{self.rolling_summary}\n\n# RECENT\n{recent_txt}".strip()
        return recent_txt

    def last_event(self, *, type: Optional[str] = None) -> Optional[ContextEvent]:
        for e in reversed(self.recent):
            if type is None or e.type == type:
                return e
        return None
