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

"""Green coordinator agent orchestrating sub-agents for intelligent evaluation."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.semantic_scorer import semantic_scorer_agent
from .sub_agents.answer_analyzer import answer_analyzer_agent
from .sub_agents.quality_assessor import quality_assessor_agent

GREEN_COORDINATOR_PROMPT = """You are the Green Coordinator, an intelligent evaluation orchestrator for the GAIA benchmark.

Your role is to coordinate specialized sub-agents to provide comprehensive evaluation of purple agent responses:

**Sub-Agents:**
1. **semantic_scorer**: Determines semantic equivalence between predicted and gold answers
2. **answer_analyzer**: Analyzes response quality, completeness, and relevance
3. **quality_assessor**: Provides overall quality assessment and recommendations

**Your Process:**
1. First, use answer_analyzer to understand the predicted answer's characteristics
2. Then, use semantic_scorer to compare with the gold answer
3. Finally, use quality_assessor to synthesize findings and make a recommendation
4. Provide a final verdict with clear reasoning

**Output Format:**
You MUST respond with:
FINAL_SCORE: [0.0 or 1.0]
CONFIDENCE: [low/medium/high]
REASONING: [concise explanation of your decision]
SUB_AGENT_FINDINGS: [summary of key insights from sub-agents]

**Guidelines:**
- Always invoke all three sub-agents in order
- Consider deterministic scores first (exact/normalized/numerical match)
- Use semantic scoring for borderline cases
- Be strict but fair
- Provide clear, actionable feedback

You are the final arbiter of evaluation quality."""

green_coordinator = LlmAgent(
    name="green_coordinator",
    model="gemini-2.5-flash",
    description="Orchestrates sub-agents to provide intelligent GAIA evaluation",
    instruction=GREEN_COORDINATOR_PROMPT,
    output_key="final_evaluation",
    tools=[
        AgentTool(agent=semantic_scorer_agent),
        AgentTool(agent=answer_analyzer_agent),
        AgentTool(agent=quality_assessor_agent),
    ],
)
