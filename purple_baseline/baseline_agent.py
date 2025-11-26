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

"""Baseline purple agent for demonstration."""

import logging
import re
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaselinePurpleAgent:
    """Simple baseline agent that answers questions heuristically."""
    
    def __init__(self):
        """Initialize the baseline agent."""
        self.name = "baseline_purple_agent"
        logger.info(f"Initialized {self.name}")
    
    def answer_question(self, question: str, metadata: Dict[str, Any] | None = None) -> str:
        """Generate a heuristic answer to a question.
        
        This baseline uses simple pattern matching and heuristics to generate answers.
        It's meant for demonstration and testing purposes only.
        
        Args:
            question: The question to answer
            metadata: Optional metadata about the question
            
        Returns:
            Answer string
        """
        logger.info(f"Answering question: {question[:100]}...")
        
        question_lower = question.lower()
        
        # Simple pattern matching heuristics
        
        # Yes/No questions
        if any(q in question_lower for q in ["is it", "are there", "does it", "do they", "can you"]):
            if "not" in question_lower or "never" in question_lower:
                return "No"
            return "Yes"
        
        # Counting questions
        if question_lower.startswith("how many"):
            # Default guess
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
        
        # What questions
        if question_lower.startswith("what"):
            # Try to extract potential answers from the question itself
            words = question.split()
            if len(words) > 3:
                return words[-2]  # Return second-to-last word as a guess
            return "Unknown"
        
        # Calculation questions
        if any(op in question for op in ["+", "-", "*", "/", "×", "÷"]):
            return self._simple_calculation(question)
        
        # Default response
        return "I don't know"
    
    def _simple_calculation(self, question: str) -> str:
        """Attempt simple arithmetic calculation.
        
        Args:
            question: Question containing arithmetic
            
        Returns:
            Result of calculation or "Unknown"
        """
        try:
            # Extract numbers
            numbers = re.findall(r'-?\d+\.?\d*', question)
            if len(numbers) < 2:
                return "Unknown"
            
            num1, num2 = float(numbers[0]), float(numbers[1])
            
            # Try different operations
            if "+" in question or "plus" in question.lower() or "add" in question.lower():
                result = num1 + num2
            elif "-" in question or "minus" in question.lower() or "subtract" in question.lower():
                result = num1 - num2
            elif "*" in question or "×" in question or "times" in question.lower() or "multiply" in question.lower():
                result = num1 * num2
            elif "/" in question or "÷" in question or "divide" in question.lower():
                if num2 != 0:
                    result = num1 / num2
                else:
                    return "Undefined"
            else:
                return "Unknown"
            
            # Return as integer if it's a whole number
            if result == int(result):
                return str(int(result))
            return str(round(result, 2))
            
        except (ValueError, IndexError):
            return "Unknown"


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
