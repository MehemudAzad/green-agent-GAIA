#!/usr/bin/env python3
"""Test script to verify LLM-enhanced evaluation."""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'green-evaluator'))

from agent.green_coordinator import green_coordinator


async def test_coordinator():
    """Test the green coordinator with sub-agents."""
    
    test_cases = [
        {
            "question": "What is the square root of 144?",
            "gold_answer": "12",
            "predicted_answer": "twelve",
            "expected": "Should recognize semantic equivalence"
        },
        {
            "question": "What is the capital of France?",
            "gold_answer": "Paris",
            "predicted_answer": "Paris, France",
            "expected": "Should handle extra location info"
        },
        {
            "question": "What is 2 + 2?",
            "gold_answer": "4",
            "predicted_answer": "The answer is four",
            "expected": "Should extract number from sentence"
        }
    ]
    
    print("=" * 70)
    print("LLM-Enhanced Evaluation Test")
    print("=" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test['expected']}")
        print(f"{'='*70}")
        print(f"Question: {test['question']}")
        print(f"Gold Answer: {test['gold_answer']}")
        print(f"Predicted Answer: {test['predicted_answer']}")
        print(f"\nInvoking Green Coordinator...")
        print("-" * 70)
        
        prompt = f"""Evaluate this GAIA benchmark response:

**Question:** {test['question']}

**Gold Answer:** {test['gold_answer']}

**Predicted Answer:** {test['predicted_answer']}

**Deterministic Score:** 0.0

Please coordinate with your sub-agents to provide a comprehensive evaluation.
Use answer_analyzer to assess quality, semantic_scorer to check equivalence, and quality_assessor for final judgment."""
        
        try:
            result = green_coordinator.run(prompt)
            output = result.get("final_evaluation", "No output")
            
            print("\n🤖 GREEN COORDINATOR OUTPUT:")
            print(output)
            print("-" * 70)
            
            # Parse score
            for line in output.split("\n"):
                if line.startswith("FINAL_SCORE:"):
                    score = line.split(":", 1)[1].strip()
                    emoji = "✅" if score == "1.0" else "❌"
                    print(f"\n{emoji} Final Score: {score}")
                    break
        
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-key-here'")
        sys.exit(1)
    
    print("✓ GOOGLE_API_KEY found")
    print("Starting LLM evaluation test...\n")
    
    asyncio.run(test_coordinator())
