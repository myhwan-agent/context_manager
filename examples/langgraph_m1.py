"""M1 example: trigger-based summarization with LangGraph.

Usage (recommended):
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e .
  python examples/langgraph_m1.py
"""

from context_manager.core.graph_builder import CMState, build_graph
from context_manager.core.context_factory import ContextEvent


graph = build_graph(max_history=10)

state = CMState()

# Simulate frames
for i in range(3):
    state = graph.invoke(state, ContextEvent(type="observation", text=f"frame {i}: scene looks stable"))

# Trigger summary on action
state = graph.invoke(state, ContextEvent(type="action", text="move forward 1m"))

print(state.planning_context)
