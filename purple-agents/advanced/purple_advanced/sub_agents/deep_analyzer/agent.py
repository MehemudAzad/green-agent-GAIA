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

"""Deep Analyzer Agent for complex reasoning and multi-step problem solving."""

from google.adk.agents import LlmAgent

from . import prompt

MODEL = "gemini-2.5-pro"

deep_analyzer_agent = LlmAgent(
    model=MODEL,
    name="deep_analyzer_agent",
    description=(
        "Performs in-depth analysis of complex problems, "
        "breaks down multi-step reasoning tasks, and synthesizes "
        "information to provide well-reasoned conclusions"
    ),
    instruction=prompt.DEEP_ANALYZER_PROMPT,
    output_key="analysis_result",
)
