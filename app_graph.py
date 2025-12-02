import os
import sys

# Ensure the current directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.pipeline import build_mdt_graph

# Define all agents for the studio visualization
# This configuration enables all agents to show the full potential of the graph
ALL_AGENTS = [
    "Case Organizer",
    "Radiologist",
    "Pathologist",
    "Pulmonologist",
    "Rheumatologist",
    "Moderator"
]

# Build the graph without UI callbacks (they will be None, which is handled gracefully in pipeline.py)
# This 'graph' object is what LangGraph Studio will load and visualize
graph = build_mdt_graph(enabled_agents=ALL_AGENTS)
