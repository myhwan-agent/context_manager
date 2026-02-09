from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


EventType = Literal[
    "observation",  # perception results (frame understanding)
    "action",  # action executed
    "plan",  # plan proposed
    "tool",  # tool output
    "note",  # human/operator note
]


@dataclass(frozen=True)
class ContextEvent:
    """Atomic unit of context.

    Notes on multimodal inputs:
    - Upstream may encode image/video/audio into text (captions, tags, embeddings-as-text, etc.).
    - This layer treats payload as text, but keeps `meta` for structured data.
    """

    type: EventType
    text: str
    ts: datetime = datetime.utcnow()
    meta: dict[str, Any] | None = None
    namespace: str = "default"  # optional isolation: perception|planning|tools|human
