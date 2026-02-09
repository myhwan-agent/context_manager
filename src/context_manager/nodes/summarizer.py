from __future__ import annotations

from typing import Any, Dict

from ..core.context_factory import ContextEvent, RequestContext


def summarize_context(state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
    """Summarize current context.

    Runnable skeleton: generate a compact text summary from history.

    Later:
    - trigger-based summarization policy
    - model-based summarization (qwen3-vl-32b or a smaller summarizer)
    """

    history: list[ContextEvent] = state.get("history", []) or []

    # simple heuristic summary
    obs = [e for e in history if e.type == "observation"]
    notes = [e for e in history if e.type == "note"]

    parts: list[str] = []
    if obs:
        parts.append("OBS:")
        for e in obs[:3]:
            parts.append(f"- {e.text}")
    if notes:
        parts.append("NOTES:")
        for e in notes[:2]:
            parts.append(f"- {e.text}")

    state["summary"] = "\n".join(parts).strip()
    return state  # type: ignore[return-value]
