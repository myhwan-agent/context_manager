from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, TypedDict


# -------------------------
# IO / state shapes
# -------------------------

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
    - Upstream may encode image/video into text (captions, tags, embeddings-as-text, etc.).
    - This layer treats payload as text, but keeps `meta` for structured data.
    """

    type: EventType
    text: str
    meta: dict[str, Any] | None = None
    namespace: str = "default"  # optional isolation: perception|planning|tools|human


class SensorData(TypedDict, total=False):
    """Raw sensor inputs (already base64-encoded bytes as str)."""

    image: str
    video: str
    scene_graph: str


class AdditionalContext(TypedDict, total=False):
    robot_mode: str
    task_description: str
    allowed_actions: list[str]
    objects: list[str]
    use_task_example: bool


class RequestContext(TypedDict, total=False):
    """Primary state passed through the ContextManager graph."""

    sensor_data: SensorData
    user_input: str
    additional_context: AdditionalContext

    # graph outputs
    summary: str
    plan: str
    history: list[ContextEvent]


# -------------------------
# helpers
# -------------------------

def b64_encode(path: Optional[str]) -> str:
    """Encode a local file to base64 string.

    If path is None, returns an empty string.
    """

    if not path:
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
