#!/usr/bin/env python3
"""Quick test of the updated GAIALoader with real GAIA data."""

from agent.gaia_loader import GAIALoader

def main():
    print("Testing GAIALoader with real GAIA data\n")
    
    loader = GAIALoader("data/gaia")
    
    # Test 1: Get statistics
    print("=== Dataset Statistics ===")
    stats = loader.get_statistics()
    print(f"Total questions: {stats['total']}")
    print(f"By level: {stats['by_level']}")
    print(f"With file attachments: {stats['with_files']}\n")
    
    # Test 2: Load by level
    print("=== Loading by Level ===")
    for level in [1, 2, 3]:
        questions = loader.load_by_level(level)
        print(f"Level {level}: {len(questions)} questions")
    print()
    
    # Test 3: Load questions with files
    print("=== Questions with File Attachments ===")
    file_questions = loader.get_questions_with_files()
    print(f"Found {len(file_questions)} questions with files")
    if file_questions:
        sample = file_questions[0]
        print(f"\nSample question:")
        print(f"  ID: {sample.id}")
        print(f"  File: {sample.metadata.get('file_name', 'N/A')}")
        print(f"  Question: {sample.question[:100]}...")
    print()
    
    # Test 4: Load sample questions
    print("=== Sample Questions ===")
    sample_questions = loader.load_questions("sample_questions.json")
    print(f"Loaded {len(sample_questions)} sample questions")
    if sample_questions:
        q = sample_questions[0]
        print(f"\nFirst sample:")
        print(f"  ID: {q.id}")
        print(f"  Level: {q.metadata.get('level', 'N/A')}")
        print(f"  Question: {q.question[:100]}...")
        print(f"  Gold Answer: {q.gold_answer[:100]}...")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    main()
