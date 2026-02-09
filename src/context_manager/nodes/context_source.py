from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from ..core.context_factory import ContextEvent, RequestContext


# -------------------------
# Knowledge source (mock)
# -------------------------


@dataclass(frozen=True)
class ObjectAtGlobal:
    """A simple knowledge record: what object is at which global coordinate."""

    object: str
    x: float
    y: float
    z: float
    confidence: float = 1.0


class KnowledgeSource(Protocol):
    def query(
        self,
        *,
        objects: list[str] | None = None,
        robot_mode: str | None = None,
        limit: int = 20,
    ) -> list[ObjectAtGlobal]:  # pragma: no cover
        ...


class MockExternalDB(KnowledgeSource):
    """Mock of an external DB.

    Assumption: an external DB exists and can be queried for object positions.
    For now we return a small fixed set.
    """

    def __init__(self) -> None:
        self._rows = [
            ObjectAtGlobal("mug", x=1.2, y=0.4, z=0.75, confidence=0.92),
            ObjectAtGlobal("bottle", x=0.9, y=-0.2, z=0.75, confidence=0.88),
            ObjectAtGlobal("door", x=5.0, y=1.0, z=0.0, confidence=0.99),
        ]

    def query(
        self,
        *,
        objects: list[str] | None = None,
        robot_mode: str | None = None,
        limit: int = 20,
    ) -> list[ObjectAtGlobal]:
        rows = self._rows
        if objects:
            allow = set(objects)
            rows = [r for r in rows if r.object in allow]
        return rows[:limit]


# Registry (A 방향): nodes/context_source.py 내부에 소스들을 등록
KNOWLEDGE_SOURCES: dict[str, KnowledgeSource] = {
    "external_db": MockExternalDB(),
}


def _get_knowledge_source(name: str = "external_db") -> KnowledgeSource:
    if name not in KNOWLEDGE_SOURCES:
        raise KeyError(f"Unknown knowledge source: {name}")
    return KNOWLEDGE_SOURCES[name]


# -------------------------
# Node: context collect
# -------------------------


def context_collect(state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
    """Collect context from provided sensor_data/user_input + (mocked) external DB.

    Runnable behavior:
    - builds `history` (list[ContextEvent])
    - queries knowledge source for object positions and appends to history

    Later:
    - make this conditional/triggered and allow multiple sources.
    """

    sensor_data = state.get("sensor_data", {}) or {}
    user_input = state.get("user_input", "")
    additional = state.get("additional_context", {}) or {}

    history: list[ContextEvent] = []

    # --- perception inputs ---
    if sensor_data.get("scene_graph"):
        history.append(
            ContextEvent(
                type="observation",
                text=f"scene_graph: {sensor_data['scene_graph']}",
                meta={"source": "scene_graph"},
                namespace="perception",
            )
        )

    # We do not decode b64; treat as opaque payload and just record presence.
    if sensor_data.get("image"):
        history.append(
            ContextEvent(
                type="observation",
                text="image: <b64_present>",
                meta={"source": "image", "bytes_b64": True},
                namespace="perception",
            )
        )

    if sensor_data.get("video"):
        history.append(
            ContextEvent(
                type="observation",
                text="video: <b64_present>",
                meta={"source": "video", "bytes_b64": True},
                namespace="perception",
            )
        )

    # --- human input ---
    if user_input:
        history.append(
            ContextEvent(
                type="note",
                text=f"user_input: {user_input}",
                meta={"source": "user"},
                namespace="human",
            )
        )

    # --- knowledge source (mock external DB) ---
    objects: Optional[list[str]] = additional.get("objects")
    robot_mode: Optional[str] = additional.get("robot_mode")

    ks = _get_knowledge_source("external_db")
    rows = ks.query(objects=objects, robot_mode=robot_mode, limit=20)

    # store raw knowledge for downstream nodes
    state["knowledge_source"] = [r.__dict__ for r in rows]

    for r in rows:
        history.append(
            ContextEvent(
                type="observation",
                text=f"knowledge: {r.object} at global=({r.x:.2f}, {r.y:.2f}, {r.z:.2f}), conf={r.confidence:.2f}",
                meta={"source": "external_db", **r.__dict__},
                namespace="knowledge",
            )
        )

    state["history"] = history
    return state  # type: ignore[return-value]
