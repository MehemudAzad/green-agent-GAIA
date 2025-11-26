#!/usr/bin/env python3
"""Test the LLM-powered purple agent."""

import os
from purple_baseline.baseline_agent import BaselinePurpleAgent


def main():
    print("=" * 70)
    print("LLM-POWERED PURPLE AGENT TEST")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✓ GOOGLE_API_KEY found")
        print(f"  Using LLM mode with key: {api_key[:10]}...")
    else:
        print("⚠ GOOGLE_API_KEY not found")
        print("  Agent will use fallback heuristics")
    
    print("\nInitializing agent...")
    agent = BaselinePurpleAgent()
    
    # Test questions from GAIA-style benchmark
    test_questions = [
        {
            "question": "What is 2 + 2?",
            "expected": "4"
        },
        {
            "question": "How many continents are there?",
            "expected": "7"
        },
        {
            "question": "What year did World War II end?",
            "expected": "1945"
        },
        {
            "question": "Is Paris the capital of France?",
            "expected": "Yes"
        },
        {
            "question": "Who wrote Hamlet?",
            "expected": "William Shakespeare"
        },
        {
            "question": "Where is the Eiffel Tower located?",
            "expected": "Paris"
        },
        {
            "question": "What is the square root of 144?",
            "expected": "12"
        }
    ]
    
    print("\n" + "-" * 70)
    print("RUNNING TEST QUESTIONS")
    print("-" * 70)
    
    correct = 0
    total = len(test_questions)
    
    for i, test in enumerate(test_questions, 1):
        question = test["question"]
        expected = test["expected"]
        
        print(f"\n[{i}/{total}] Q: {question}")
        
        answer = agent.answer_question(question)
        
        # Simple comparison (case-insensitive)
        is_correct = answer.lower().strip() == expected.lower().strip()
        if is_correct:
            correct += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"     A: {answer}")
        print(f"     Expected: {expected}")
        print(f"     {status} {'CORRECT' if is_correct else 'INCORRECT'}")
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {correct}/{total} correct ({correct/total*100:.1f}%)")
    print("=" * 70)
    
    if api_key:
        print("\n✓ LLM mode active - results should be more accurate")
    else:
        print("\n⚠ Fallback mode - install GOOGLE_API_KEY for better results")
        print("  Get your key at: https://aistudio.google.com/apikey")


if __name__ == "__main__":
    main()
