"""GAIA Coordinator: Hierarchical agent system for GAIA benchmark questions.

This module implements the main coordinator agent that orchestrates specialized
sub-agents to answer GAIA benchmark questions. The architecture follows the
DeepResearchAgent pattern with:

- Planning and task decomposition by the coordinator
- Specialized sub-agents for specific capabilities:
  - web_search_agent: Finds information online
  - deep_analyzer_agent: Performs complex reasoning
  - calculator_agent: Handles mathematical computations
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.web_search import web_search_agent
from .sub_agents.deep_analyzer import deep_analyzer_agent
from .sub_agents.calculator import calculator_agent

MODEL = "gemini-2.5-pro"

gaia_test_taker = LlmAgent(
    name="gaia_test_taker",
    model=MODEL,
    description=(
        "Advanced multi-agent test taker for GAIA benchmark questions. "
        "Analyzes questions, decomposes tasks, delegates to specialized agents "
        "(web search, deep analysis, calculation), and synthesizes results into "
        "accurate final answers."
    ),
    instruction=prompt.GAIA_COORDINATOR_PROMPT,
    output_key="final_answer",
    tools=[
        AgentTool(agent=web_search_agent),
        AgentTool(agent=deep_analyzer_agent),
        AgentTool(agent=calculator_agent),
    ],
)

# Export both names for compatibility
gaia_coordinator = gaia_test_taker  # Backward compatibility
root_agent = gaia_test_taker
