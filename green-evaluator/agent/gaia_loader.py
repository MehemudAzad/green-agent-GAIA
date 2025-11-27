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

"""GAIA benchmark question loader."""

import json
import pathlib
from typing import List, Optional

from .schemas import GAIAQuestion


class GAIALoader:
    """Loads and normalizes GAIA benchmark questions from JSON files.
    
    The loader expects JSON files in the format:
    {
        "questions": [
            {
                "id": "task_id",
                "question": "question text",
                "gold_answer": "expected answer",
                "metadata": {...}
            }
        ]
    }
    """
    
    def __init__(self, data_dir: str | pathlib.Path):
        """Initialize the GAIA loader.
        
        Args:
            data_dir: Path to the directory containing GAIA JSON files
        """
        self.data_dir = pathlib.Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"Data directory does not exist: {self.data_dir}")
    
    def load_questions(
        self, 
        filename: str = "validation_complete.json",
        level: Optional[int] = None
    ) -> List[GAIAQuestion]:
        """Load questions from a JSON file.
        
        Args:
            filename: Name of the JSON file to load
            level: Optional difficulty level filter (1, 2, or 3)
            
        Returns:
            List of GAIAQuestion objects
            
        Raises:
            FileNotFoundError: If the specified file does not exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Question file not found: {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Normalize the data structure
        questions = []
        if isinstance(data, list):
            # Direct list of questions
            questions_data = data
        elif isinstance(data, dict) and "questions" in data:
            # Wrapped in a "questions" key
            questions_data = data["questions"]
        else:
            raise ValueError(f"Unexpected JSON structure in {filepath}")
        
        for item in questions_data:
            question = self._normalize_question(item)
            
            # Apply level filter if specified
            if level is not None:
                if question.metadata.get("level") != level:
                    continue
            
            questions.append(question)
        
        return questions
    
    def _normalize_question(self, item: dict) -> GAIAQuestion:
        """Normalize a raw question dict into a GAIAQuestion object.
        
        Args:
            item: Raw question dictionary
            
        Returns:
            Normalized GAIAQuestion object
        """
        # Extract required fields
        question_id = item.get("id", "")
        question_text = item.get("question", "")
        gold_answer = item.get("gold_answer", "")
        
        # Extract or merge metadata
        if "metadata" in item:
            metadata = dict(item["metadata"])
        else:
            metadata = {}
            # Legacy format support
            if "difficulty" in item:
                metadata["difficulty"] = item["difficulty"]
            if "topic" in item:
                metadata["topic"] = item["topic"]
            if "level" in item:
                metadata["level"] = item["level"]
        
        return GAIAQuestion(
            id=question_id,
            question=question_text,
            gold_answer=gold_answer,
            metadata=metadata
        )
    
    def load_by_level(self, level: int) -> List[GAIAQuestion]:
        """Load questions for a specific difficulty level.
        
        Args:
            level: Difficulty level (1, 2, or 3)
            
        Returns:
            List of questions for the specified level
        """
        if level not in [1, 2, 3]:
            raise ValueError(f"Invalid level: {level}. Must be 1, 2, or 3.")
        
        # Try to load from level-specific file first
        level_file = f"validation_level{level}.json"
        if (self.data_dir / level_file).exists():
            return self.load_questions(level_file)
        
        # Fall back to filtering from complete dataset
        return self.load_questions(level=level)
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[GAIAQuestion]:
        """Filter questions by difficulty level.
        
        Args:
            difficulty: Difficulty level string (e.g., "level1", "level2", "level3")
            
        Returns:
            List of questions matching the difficulty
        """
        all_questions = self.load_questions()
        return [
            q for q in all_questions 
            if q.metadata.get("difficulty") == difficulty
        ]
    
    def get_questions_with_files(self) -> List[GAIAQuestion]:
        """Get questions that require file attachments.
        
        Returns:
            List of questions that have file_name or file_path in metadata
        """
        all_questions = self.load_questions()
        return [
            q for q in all_questions 
            if q.metadata.get("file_name") or q.metadata.get("file_path")
        ]
    
    def get_statistics(self) -> dict:
        """Get statistics about the loaded dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        all_questions = self.load_questions()
        
        stats = {
            "total": len(all_questions),
            "by_level": {},
            "with_files": 0
        }
        
        for level in [1, 2, 3]:
            level_questions = [q for q in all_questions if q.metadata.get("level") == level]
            stats["by_level"][level] = len(level_questions)
        
        stats["with_files"] = len(self.get_questions_with_files())
        
        return stats
