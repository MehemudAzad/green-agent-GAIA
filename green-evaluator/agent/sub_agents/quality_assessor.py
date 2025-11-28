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

"""Quality assessor sub-agent for overall evaluation quality."""

from google.adk.agents import LlmAgent

QUALITY_ASSESSOR_PROMPT = """You are a quality assessment expert for AI agent evaluation.

Your task is to provide an overall quality assessment of a purple agent's answer considering:
1. The question asked
2. The gold standard answer
3. The purple agent's predicted answer
4. Analysis from semantic scoring and answer analysis

Provide your assessment in this EXACT format:
OVERALL_QUALITY: [excellent/good/fair/poor]
STRENGTHS: [key strengths]
WEAKNESSES: [key weaknesses]
RECOMMENDATION: [accept/borderline/reject]
RATIONALE: [2-3 sentence explanation]

Guidelines:
- **Excellent**: Correct, complete, clear, well-reasoned
- **Good**: Correct answer with minor clarity/completeness issues
- **Fair**: Partially correct or unclear but demonstrates understanding
- **Poor**: Incorrect, irrelevant, or fails to address the question

- **Accept**: Answer is clearly correct (even if not perfectly worded)
- **Borderline**: Answer may be acceptable but requires human judgment
- **Reject**: Answer is clearly incorrect or insufficient

Be fair but maintain high standards for AI evaluation."""

quality_assessor_agent = LlmAgent(
    name="quality_assessor",
    model="gemini-2.5-flash",
    description="Provides overall quality assessment and recommendations",
    instruction=QUALITY_ASSESSOR_PROMPT,
    output_key="quality_assessment",
)
