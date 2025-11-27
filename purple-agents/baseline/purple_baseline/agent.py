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

"""Purple Baseline Agent: GAIA benchmark question answering using ADK Agent."""

import logging
import os
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.genai import types
import google.genai as genai

from . import prompt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration
MODEL = "gemini-2.0-flash-exp"
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.1

# Agent instructions
BASELINE_AGENT_INSTRUCTION = """You are a helpful assistant answering questions from the GAIA benchmark.

CRITICAL INSTRUCTIONS:
1. Provide ONLY the final answer - no explanations, no reasoning, no additional text
2. Be as concise as possible
3. For yes/no questions, answer ONLY "Yes" or "No"
4. For numerical answers, provide ONLY the number
5. For names/places, provide ONLY the name/place
6. Do NOT include phrases like "The answer is" or "According to"
7. Your response should be directly usable as the answer

Examples:
Question: "What is 2+2?"
Answer: "4"

Question: "Is Paris the capital of France?"
Answer: "Yes"

Question: "Who wrote Hamlet?"
Answer: "William Shakespeare"
"""

# Create ADK Agent for baseline
baseline_agent = Agent(
    model=MODEL,
    name="baseline_purple_agent",
    description="A baseline agent that answers GAIA benchmark questions using a single LLM without specialized tools",
    instruction=BASELINE_AGENT_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
)


# Legacy class for backward compatibility (if needed)
class PurpleBaselineAgent:
    """Purple agent that uses Google Gemini LLM to answer GAIA questions."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = MODEL,
        max_tokens: int = MAX_OUTPUT_TOKENS,
        temperature: float = TEMPERATURE
    ):
        """Initialize the purple baseline agent.
        
        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var
            model_name: Gemini model to use
            max_tokens: Maximum tokens for output
            temperature: Temperature for generation
        """
        self.name = "purple_baseline_agent"
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("No GOOGLE_API_KEY found. Agent will use fallback mode.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(
                    f"Initialized {self.name} with model {self.model_name} "
                    f"(max_tokens={self.max_tokens}, temperature={self.temperature})"
                )
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")
                self.client = None
    
    def answer_question(
        self,
        question: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate an answer to a question using LLM.
        
        Args:
            question: The question to answer
            metadata: Optional metadata about the question
            
        Returns:
            Answer string
        """
        logger.info(f"Processing question: {question[:100]}...")
        
        # Try LLM first
        if self.client:
            try:
                answer = self._answer_with_llm(question, metadata)
                logger.info(f"LLM answer: {answer[:100]}...")
                return answer
            except Exception as e:
                logger.error(f"LLM failed: {e}. Falling back to heuristics.")
        
        # Fallback to heuristics
        return self._fallback_answer(question)
    
    def _answer_with_llm(
        self,
        question: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answer question using the LLM.
        
        Args:
            question: The question to answer
            metadata: Optional metadata
            
        Returns:
            LLM-generated answer
        """
        # Build system prompt
        system_prompt = prompt.GAIA_AGENT_PROMPT
        
        # Add metadata context if available
        if metadata:
            difficulty = metadata.get("difficulty", "unknown")
            level = metadata.get("level", "unknown")
            system_prompt += f"\n\nQuestion difficulty: {difficulty} (Level {level})"
        
        try:
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            # Extract answer
            if response and response.text:
                answer = response.text.strip()
                # Remove common prefixes that might slip through
                for prefix in ["The answer is ", "Answer: ", "A: ", "Response: "]:
                    if answer.startswith(prefix):
                        answer = answer[len(prefix):].strip()
                return answer
            else:
                # Log detailed response info for debugging
                logger.warning(f"Empty response from LLM")
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    logger.warning(f"Finish reason: {candidate.finish_reason}")
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    logger.warning(
                        f"Token usage - Prompt: {usage.prompt_token_count}, "
                        f"Thoughts: {getattr(usage, 'thoughts_token_count', 0)}, "
                        f"Total: {usage.total_token_count}"
                    )
                return "Unable to generate answer"
                
        except Exception as e:
            logger.error(f"Error calling LLM: {type(e).__name__}: {e}")
            raise
    
    def _fallback_answer(self, question: str) -> str:
        """Fallback heuristic answering when LLM is unavailable.
        
        Args:
            question: The question to answer
            
        Returns:
            Heuristic answer
        """
        logger.info("Using fallback heuristic mode")
        question_lower = question.lower()
        
        # Yes/No questions
        if any(q in question_lower for q in ["is it", "are there", "does it", "do they", "can you", "is "]):
            if "not" in question_lower or "never" in question_lower:
                return "No"
            return "Yes"
        
        # Counting questions
        if question_lower.startswith("how many"):
            return "5"
        
        # Year questions
        if "what year" in question_lower or "when was" in question_lower:
            return "2020"
        
        # Who questions
        if question_lower.startswith("who"):
            return "Unknown"
        
        # Where questions
        if question_lower.startswith("where"):
            return "United States"
        
        # Default
        return "I don't know"


# Create legacy root agent instance for backward compatibility
root_agent = PurpleBaselineAgent()


def main() -> None:
    """Test the baseline agent with sample questions using ADK runtime."""
    from google.adk.runtime import run_sync
    
    test_questions = [
        "What is 2 + 2?",
        "How many continents are there?",
        "What year did World War II end?",
        "Is Paris the capital of France?",
        "Who wrote Hamlet?",
        "Where is the Eiffel Tower located?",
    ]
    
    print("\n" + "=" * 70)
    print("PURPLE BASELINE AGENT TEST (ADK)")
    print("=" * 70)
    
    for question in test_questions:
        try:
            response = run_sync(baseline_agent, question)
            answer = response.text.strip()
            print(f"\nQ: {question}")
            print(f"A: {answer}")
        except Exception as e:
            print(f"\nQ: {question}")
            print(f"A: Error - {e}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
