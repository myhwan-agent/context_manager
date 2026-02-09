from __future__ import annotations

from typing import Callable, Optional

from ..core.context_factory import ContextEvent
from ..core.graph_builder import CMState


def default_should_summarize(event: ContextEvent) -> bool:
    """Trigger-based summarization policy.

    Designed for ~1 FPS loops: avoid per-frame summarization.

    Triggers (default):
    - action / plan events
    - meta.trigger_summary == True
    """

    if event.type in ("action", "plan"):
        return True
    if event.meta and event.meta.get("trigger_summary") is True:
        return True
    return False


def summarize(
    state: CMState,
    event: ContextEvent,
    *,
    should_summarize: Callable[[ContextEvent], bool] = default_should_summarize,
    summarizer: Optional[Callable[[str, list[ContextEvent]], str]] = None,
) -> CMState:
    if not should_summarize(event):
        return state

    if summarizer is not None:
        state.summary = summarizer(state.summary, state.events)
        return state

    # Heuristic placeholder summary: keep last action/plan + last observation.
    last_action = next((e for e in reversed(state.events) if e.type == "action"), None)
    last_plan = next((e for e in reversed(state.events) if e.type == "plan"), None)
    last_obs = next((e for e in reversed(state.events) if e.type == "observation"), None)

    parts: list[str] = []
    if last_plan:
        parts.append(f"PLAN: {last_plan.text}")
    if last_action:
        parts.append(f"LAST_ACTION: {last_action.text}")
    if last_obs:
        parts.append(f"LAST_OBS: {last_obs.text}")

    state.summary = "\n".join(parts)
    return state
