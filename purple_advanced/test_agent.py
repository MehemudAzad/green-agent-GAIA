#!/usr/bin/env python3
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

"""Quick test script for the Purple Advanced Agent."""

import sys
from purple_advanced import gaia_coordinator

def main():
    """Test the agent with sample questions."""
    
    test_questions = [
        # Simple factual question (should use web search)
        "What is the capital of Japan?",
        
        # Mathematical question (should use calculator)
        "What is 15% of 340?",
        
        # Current event question (should use web search)
        "Who won the Nobel Prize in Literature in 2023?",
        
        # Multi-step reasoning (should use deep analyzer)
        "If a train travels at 60 mph for 2.5 hours, how far does it go?",
        
        # Complex question (may use multiple agents)
        "What is the population density of Tokyo in people per square kilometer?",
    ]
    
    print("\n" + "=" * 80)
    print("PURPLE ADVANCED AGENT - QUICK TEST")
    print("=" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}] Question: {question}")
        print("-" * 80)
        
        try:
            result = gaia_coordinator.run(question)
            
            if isinstance(result, dict):
                answer = result.get("final_answer", str(result))
            else:
                answer = str(result)
            
            print(f"Answer: {answer}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
