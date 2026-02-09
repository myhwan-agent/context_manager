"""Demonstration script for the LangGraph-based context manager.

This script initializes the graph, runs it with example inputs, and prints the
resulting summary, plan, and history.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Allow running `python demo.py` without installing the package.
_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from context_manager.core.context_factory import RequestContext, b64_encode
from context_manager.core.graph_builder import ContextManagerGraph
from context_manager.core.prompts.prompt import (
    DEFAULT_ALLOWED_ACTIONS,
    DEFAULT_OBJECTS,
    TASK_DESCRIPTION,
    PromptManager,
)
from context_manager.utils.evaluation import compute_action_count, compute_summary_length


def build_init_state(
    image_path: Optional[str],
    video_path: Optional[str],
    task_description: str,
    allowed_actions: Optional[list[str]],
    objects: Optional[list[str]],
    robot_mode: str,
    use_task_example: bool,
    custom_user_input: Optional[str],
) -> Dict[str, Any] | RequestContext:
    prompt_manager = PromptManager(
        task_description,
        allowed_actions=allowed_actions or DEFAULT_ALLOWED_ACTIONS,
        objects=objects or DEFAULT_OBJECTS,
        use_task_example=use_task_example,
    )

    if custom_user_input is None:
        user_input = prompt_manager.get_user_prompt(
            has_video=video_path is not None,
            has_image=image_path is not None,
            include_task_example=False,
        )
    else:
        user_input = custom_user_input

    state: Dict[str, Any] = {
        "sensor_data": {
            "image": b64_encode(image_path),
            "video": b64_encode(video_path),
            "scene_graph": "knowledge",
        },
        "user_input": user_input,
        "additional_context": {
            "robot_mode": robot_mode,
            "task_description": task_description,
            "allowed_actions": allowed_actions or DEFAULT_ALLOWED_ACTIONS,
            "objects": objects or DEFAULT_OBJECTS,
            "use_task_example": use_task_example,
        },
    }
    return state


def run_demo(image: Optional[str] = None, video: Optional[str] = None) -> None:
    cmg = ContextManagerGraph()

    init_state = build_init_state(
        image_path=image,
        video_path=video,
        task_description=TASK_DESCRIPTION,
        allowed_actions=None,
        objects=None,
        robot_mode="sim",
        use_task_example=False,
        custom_user_input=None,
    )

    result = cmg.invoke(init_state)

    summary = result.get("summary", "")
    plan = result.get("plan", "")
    history = result.get("history", [])

    print("\n=== SUMMARY ===\n")
    print(summary)

    print("\n=== PLAN ===\n")
    print(plan)

    print("\n=== HISTORY ===\n")
    for e in history:
        # ContextEvent prints as dataclass repr; keep readable.
        try:
            print(f"[{e.type}] ({e.namespace}) {e.text}")
        except Exception:
            print(e)

    print("\n=== EVAL ===\n")
    print(f"summary_length: {compute_summary_length(summary)}")
    print(f"action_count: {compute_action_count(plan)}")


if __name__ == "__main__":
    run_demo()
