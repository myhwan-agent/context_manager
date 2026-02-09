from __future__ import annotations

from typing import Any, Dict

from ..core.context_factory import ContextEvent, RequestContext


def plan_actions(state: Dict[str, Any] | RequestContext) -> Dict[str, Any]:
    """Produce a plan string.

    Runnable skeleton: build a naive plan using allowed_actions/objects.

    Later:
    - call VLM planner
    - ensure plan adheres to allowed actions schema
    """

    additional = state.get("additional_context", {}) or {}
    allowed = additional.get("allowed_actions") or []
    objects = additional.get("objects") or []

    task_description = additional.get("task_description") or ""

    # naive plan
    plan_lines: list[str] = []
    if task_description:
        plan_lines.append(f"# TASK\n{task_description}")

    plan_lines.append("# PLAN")
    if allowed:
        plan_lines.append(f"- [look] confirm scene (allowed={len(allowed)})")
    else:
        plan_lines.append("- [look] confirm scene")

    if objects:
        plan_lines.append(f"- [note] objects_hint: {', '.join(objects[:6])}")

    plan_lines.append("- [plan] decide next action")

    plan = "\n".join(plan_lines).strip()
    state["plan"] = plan

    # also append into history as a plan event
    history: list[ContextEvent] = state.get("history", []) or []
    history.append(ContextEvent(type="plan", text=plan, meta={"source": "planner"}, namespace="planning"))
    state["history"] = history

    return state  # type: ignore[return-value]
