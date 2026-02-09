from __future__ import annotations

from typing import Any, Dict

from ..core.context_factory import ContextEvent, RequestContext


def context_collect(state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
    """Collect context from provided sensor_data/user_input.

    Runnable skeleton:
    - creates `history` (list[ContextEvent])
    - preserves incoming fields

    Later this node will *request* additional context sources (e.g., DB, logs,
    map, object memory) based on planner needs.
    """

    sensor_data = state.get("sensor_data", {}) or {}
    user_input = state.get("user_input", "")

    history: list[ContextEvent] = []

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

    if user_input:
        history.append(
            ContextEvent(
                type="note",
                text=f"user_input: {user_input}",
                meta={"source": "user"},
                namespace="human",
            )
        )

    state["history"] = history
    return state  # type: ignore[return-value]
