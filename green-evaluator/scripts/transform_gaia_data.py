#!/usr/bin/env python3
"""
Transform GAIA dataset from Hugging Face format to normalized JSON.
"""

import json
import pathlib
from typing import List, Dict, Any


def normalize_question(row_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a GAIA row into our schema."""
    
    # Map difficulty level
    level = row_data.get("Level", "1")
    difficulty_map = {"1": "level1", "2": "level2", "3": "level3"}
    difficulty = difficulty_map.get(str(level), "level1")
    
    # Build normalized question
    question = {
        "id": row_data.get("task_id", ""),
        "question": row_data.get("Question", ""),
        "gold_answer": row_data.get("Final answer", ""),
        "metadata": {
            "difficulty": difficulty,
            "level": int(level) if level else 1,
            "file_name": row_data.get("file_name", ""),
            "file_path": row_data.get("file_path", ""),
        }
    }
    
    # Add annotator metadata if available
    if "Annotator Metadata" in row_data:
        annotator_meta = row_data["Annotator Metadata"]
        if isinstance(annotator_meta, dict):
            question["metadata"]["annotator_steps"] = annotator_meta.get("Steps", "")
            question["metadata"]["time_taken"] = annotator_meta.get("How long did this take?", "")
            question["metadata"]["tools_used"] = annotator_meta.get("Tools", "")
            question["metadata"]["num_tools"] = annotator_meta.get("Number of tools", "")
    
    return question


def transform_gaia_data(input_file: pathlib.Path, output_dir: pathlib.Path):
    """Transform GAIA data and create multiple output files."""
    
    print(f"Loading data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all questions
    all_questions = []
    rows = data.get("rows", [])
    
    for item in rows:
        row_data = item.get("row", {})
        if row_data:
            question = normalize_question(row_data)
            all_questions.append(question)
    
    print(f"Processed {len(all_questions)} questions")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save complete dataset
    all_file = output_dir / "validation_complete.json"
    with open(all_file, 'w', encoding='utf-8') as f:
        json.dump({"questions": all_questions}, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(all_questions)} questions to {all_file}")
    
    # Split by difficulty level
    for level_num in [1, 2, 3]:
        level_questions = [
            q for q in all_questions 
            if q["metadata"].get("level") == level_num
        ]
        
        level_file = output_dir / f"validation_level{level_num}.json"
        with open(level_file, 'w', encoding='utf-8') as f:
            json.dump({"questions": level_questions}, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(level_questions)} level {level_num} questions to {level_file}")
    
    # Create a small sample for testing (first 10 questions)
    sample_questions = all_questions[:10]
    sample_file = output_dir / "sample_questions.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump({"questions": sample_questions}, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(sample_questions)} sample questions to {sample_file}")
    
    # Print statistics
    print("\n=== Dataset Statistics ===")
    print(f"Total questions: {len(all_questions)}")
    print(f"Level 1: {len([q for q in all_questions if q['metadata'].get('level') == 1])}")
    print(f"Level 2: {len([q for q in all_questions if q['metadata'].get('level') == 2])}")
    print(f"Level 3: {len([q for q in all_questions if q['metadata'].get('level') == 3])}")
    
    # Questions with file attachments
    with_files = [q for q in all_questions if q["metadata"].get("file_name")]
    print(f"Questions with file attachments: {len(with_files)}")
    

if __name__ == "__main__":
    # Paths
    base_dir = pathlib.Path(__file__).parent.parent
    input_file = base_dir / "gaia.txt"
    output_dir = base_dir / "data" / "gaia"
    
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        exit(1)
    
    transform_gaia_data(input_file, output_dir)
    print("\n✓ Transformation complete!")
