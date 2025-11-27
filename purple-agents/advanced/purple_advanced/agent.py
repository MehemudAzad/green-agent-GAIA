# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

gaia_coordinator = LlmAgent(
    name="gaia_coordinator",
    model=MODEL,
    description=(
        "Orchestrates specialized sub-agents to answer GAIA benchmark questions. "
        "Analyzes questions, decomposes tasks, delegates to appropriate agents "
        "(web search, deep analysis, calculation), and synthesizes results into "
        "concise final answers."
    ),
    instruction=prompt.GAIA_COORDINATOR_PROMPT,
    output_key="final_answer",
    tools=[
        AgentTool(agent=web_search_agent),
        AgentTool(agent=deep_analyzer_agent),
        AgentTool(agent=calculator_agent),
    ],
)

# Export as root_agent for compatibility with ADK patterns
root_agent = gaia_coordinator
