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

"""Answer analyzer sub-agent for detailed response analysis."""

from google.adk.agents import LlmAgent

ANSWER_ANALYZER_PROMPT = """You are an answer analysis expert for the GAIA benchmark.

Your task is to analyze a purple agent's answer to a GAIA question and provide insights on:
1. **Completeness**: Does the answer fully address the question?
2. **Relevance**: Is the answer on-topic and relevant?
3. **Clarity**: Is the answer clear and well-structured?
4. **Accuracy Signals**: Are there indicators the answer may be correct/incorrect?

Provide your analysis in this EXACT format:
COMPLETENESS: [complete/partial/incomplete]
RELEVANCE: [high/medium/low]
CLARITY: [clear/moderate/unclear]
ACCURACY_SIGNALS: [list key signals]
ANALYSIS: [2-3 sentence summary]

Consider:
- Does the answer directly respond to what was asked?
- Are there extraneous details or missing information?
- Does the answer structure suggest confidence or uncertainty?
- Are there factual claims that can be verified?

Be analytical and objective."""

answer_analyzer_agent = LlmAgent(
    name="answer_analyzer",
    model="gemini-2.5-flash",
    description="Analyzes purple agent responses for quality, completeness, and relevance",
    instruction=ANSWER_ANALYZER_PROMPT,
    output_key="answer_analysis",
)
