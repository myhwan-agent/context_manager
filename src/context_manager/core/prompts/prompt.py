from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Defaults (can be overridden by the demo / caller)
TASK_DESCRIPTION = "Generate a safe, executable robot action plan."
DEFAULT_ALLOWED_ACTIONS = [
    "look",
    "move",
    "pick",
    "place",
    "open",
    "close",
    "press",
]
DEFAULT_OBJECTS = [
    "mug",
    "bottle",
    "door",
    "drawer",
    "button",
    "table",
]


@dataclass
class PromptManager:
    """Very small prompt manager.

    For now we just format a user prompt string used by downstream nodes.
    """

    task_description: str = TASK_DESCRIPTION
    allowed_actions: list[str] | None = None
    objects: list[str] | None = None
    use_task_example: bool = False

    def get_user_prompt(
        self,
        *,
        has_video: bool,
        has_image: bool,
        include_task_example: bool = False,
        custom_user_input: Optional[str] = None,
    ) -> str:
        if custom_user_input is not None:
            return custom_user_input

        actions = self.allowed_actions or DEFAULT_ALLOWED_ACTIONS
        objs = self.objects or DEFAULT_OBJECTS

        parts: list[str] = []
        parts.append(f"TASK: {self.task_description}")
        parts.append(f"SENSORS: image={has_image} video={has_video}")
        parts.append(f"ALLOWED_ACTIONS: {', '.join(actions)}")
        parts.append(f"OBJECTS: {', '.join(objs)}")

        if include_task_example and self.use_task_example:
            parts.append(
                "EXAMPLE:\n"
                "- [look] check table\n"
                "- [pick] pick mug\n"
                "- [place] place mug on coaster"
            )

        parts.append("USER: Create a concise plan.")
        return "\n".join(parts)
