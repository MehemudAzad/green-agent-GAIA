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

"""Baseline purple agent using LLM for answering questions."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaselinePurpleAgent:
    """Purple agent that uses Google Gemini LLM to answer questions."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-pro"):
        """Initialize the baseline agent with LLM.
        
        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var
            model_name: Gemini model to use (default: gemini-2.5-pro)
        """
        self.name = "baseline_purple_agent_llm"
        self.model_name = model_name
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("No GOOGLE_API_KEY found. Agent will use fallback mode.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized {self.name} with model {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")
                self.client = None
    
    def answer_question(self, question: str, metadata: Dict[str, Any] | None = None) -> str:
        """Generate an answer to a question using LLM.
        
        This agent uses Google Gemini to answer questions. If the LLM is unavailable,
        it falls back to a simple heuristic mode.
        
        Args:
            question: The question to answer
            metadata: Optional metadata about the question
            
        Returns:
            Answer string
        """
        logger.info(f"Answering question: {question[:100]}...")
        
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
    
    def _answer_with_llm(self, question: str, metadata: Dict[str, Any] | None = None) -> str:
        """Answer question using the LLM.
        
        Args:
            question: The question to answer
            metadata: Optional metadata
            
        Returns:
            LLM-generated answer
        """
        # Build system prompt
        system_prompt = """You are a helpful assistant answering questions from the GAIA benchmark.
        
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
        
        # Add metadata context if available
        if metadata:
            difficulty = metadata.get("difficulty", "unknown")
            system_prompt += f"\n\nQuestion difficulty: {difficulty}"
        
        try:
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.1,  # Low temperature for more deterministic answers
                    max_output_tokens=2048,  # Increased to account for extended thinking tokens
                )
            )
            
            # Extract answer
            if response and response.text:
                answer = response.text.strip()
                # Remove common prefixes that might slip through
                for prefix in ["The answer is ", "Answer: ", "A: "]:
                    if answer.startswith(prefix):
                        answer = answer[len(prefix):].strip()
                return answer
            else:
                # Log detailed response info for debugging
                logger.warning(f"Empty response from LLM. Response object: {response}")
                if hasattr(response, 'candidates') and response.candidates:
                    logger.warning(f"Candidates: {response.candidates}")
                if hasattr(response, 'prompt_feedback'):
                    logger.warning(f"Prompt feedback: {response.prompt_feedback}")
                return "Unable to generate answer"
                
        except Exception as e:
            logger.error(f"Error calling LLM: {type(e).__name__}: {e}")
            return "Unable to generate answer"
    
    def _fallback_answer(self, question: str) -> str:
        """Fallback heuristic answering when LLM is unavailable.
        
        Args:
            question: The question to answer
            
        Returns:
            Heuristic answer
        """
        question_lower = question.lower()
        
        # Yes/No questions
        if any(q in question_lower for q in ["is it", "are there", "does it", "do they", "can you"]):
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


def main() -> None:
    """Test the baseline agent with sample questions."""
    agent = BaselinePurpleAgent()
    
    test_questions = [
        "What is 2 + 2?",
        "How many continents are there?",
        "What year did World War II end?",
        "Is Paris the capital of France?",
        "Who wrote Hamlet?",
        "Where is the Eiffel Tower located?",
    ]
    
    print("\n" + "=" * 60)
    print("BASELINE PURPLE AGENT TEST")
    print("=" * 60)
    
    for question in test_questions:
        answer = agent.answer_question(question)
        print(f"\nQ: {question}")
        print(f"A: {answer}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
