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
from typing import List

from .schemas import GAIAQuestion


class GAIALoader:
    """Loads and normalizes GAIA benchmark questions from JSON files."""
    
    def __init__(self, data_dir: str | pathlib.Path):
        """Initialize the GAIA loader.
        
        Args:
            data_dir: Path to the directory containing GAIA JSON files
        """
        self.data_dir = pathlib.Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(f"Data directory does not exist: {self.data_dir}")
    
    def load_questions(self, filename: str = "sample_questions.json") -> List[GAIAQuestion]:
        """Load questions from a JSON file.
        
        Args:
            filename: Name of the JSON file to load
            
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
        question_id = item.get("id") or item.get("question_id") or str(hash(item.get("question", "")))
        question_text = item.get("question") or item.get("query") or ""
        gold_answer = item.get("gold_answer") or item.get("answer") or item.get("ground_truth") or ""
        
        # Extract metadata
        metadata = {}
        if "difficulty" in item:
            metadata["difficulty"] = item["difficulty"]
        if "topic" in item:
            metadata["topic"] = item["topic"]
        if "level" in item:
            metadata["level"] = item["level"]
        
        # Add any extra fields to metadata
        excluded_keys = {"id", "question_id", "question", "query", "gold_answer", "answer", "ground_truth"}
        for key, value in item.items():
            if key not in excluded_keys and key not in metadata:
                metadata[key] = value
        
        return GAIAQuestion(
            id=question_id,
            question=question_text,
            gold_answer=gold_answer,
            metadata=metadata
        )
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[GAIAQuestion]:
        """Filter questions by difficulty level.
        
        Args:
            difficulty: Difficulty level to filter by
            
        Returns:
            List of questions matching the difficulty
        """
        all_questions = self.load_questions()
        return [
            q for q in all_questions 
            if q.metadata.get("difficulty") == difficulty
        ]
    
    def get_questions_by_topic(self, topic: str) -> List[GAIAQuestion]:
        """Filter questions by topic.
        
        Args:
            topic: Topic to filter by
            
        Returns:
            List of questions matching the topic
        """
        all_questions = self.load_questions()
        return [
            q for q in all_questions 
            if q.metadata.get("topic") == topic
        ]
