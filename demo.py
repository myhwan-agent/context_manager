"""Demo entrypoint (kept at repo root).

This file is intentionally lightweight. It demonstrates how to build and invoke
our LangGraph-based context manager graph.

Run (recommended):
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  python demo.py
"""

from context_manager.core.graph_builder import CMState, build_graph
from context_manager.core.context_factory import ContextEvent


def main() -> None:
    graph = build_graph(max_history=20)
    state = CMState()

    state = graph.invoke(state, ContextEvent(type="observation", text="frame: desk, laptop, mug"))
    state = graph.invoke(state, ContextEvent(type="plan", text="Pick up the mug and place it on coaster"))
    state = graph.invoke(state, ContextEvent(type="action", text="move_arm(to=mug)"))

    print("\n=== planning_context ===\n")
    print(state.planning_context)


if __name__ == "__main__":
    main()
