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

"""Tests for the GAIA loader module."""

import json
import pathlib
import pytest
import tempfile
from agent.gaia_loader import GAIALoader
from agent.schemas import GAIAQuestion


class TestGAIALoader:
    """Test suite for GAIALoader."""
    
    def create_temp_questions_file(self, data: dict, filename: str = "test_questions.json") -> pathlib.Path:
        """Helper to create a temporary questions file."""
        temp_dir = pathlib.Path(tempfile.mkdtemp())
        filepath = temp_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        return temp_dir
    
    def test_loader_initialization(self):
        """Test loader initialization with valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = GAIALoader(temp_dir)
            assert loader.data_dir == pathlib.Path(temp_dir)
    
    def test_loader_initialization_invalid_dir(self):
        """Test loader initialization with invalid directory."""
        with pytest.raises(ValueError):
            GAIALoader("/nonexistent/directory")
    
    def test_load_questions_list_format(self):
        """Test loading questions from list format."""
        data = [
            {
                "id": "q1",
                "question": "What is 2+2?",
                "gold_answer": "4",
                "difficulty": "easy"
            }
        ]
        
        temp_dir = self.create_temp_questions_file(data, "test.json")
        loader = GAIALoader(temp_dir)
        questions = loader.load_questions("test.json")
        
        assert len(questions) == 1
        assert questions[0].id == "q1"
        assert questions[0].question == "What is 2+2?"
        assert questions[0].gold_answer == "4"
        assert questions[0].metadata["difficulty"] == "easy"
    
    def test_load_questions_dict_format(self):
        """Test loading questions from dict format with 'questions' key."""
        data = {
            "questions": [
                {
                    "id": "q1",
                    "question": "What is the capital?",
                    "gold_answer": "Paris"
                }
            ]
        }
        
        temp_dir = self.create_temp_questions_file(data, "test.json")
        loader = GAIALoader(temp_dir)
        questions = loader.load_questions("test.json")
        
        assert len(questions) == 1
        assert questions[0].id == "q1"
    
    def test_load_questions_file_not_found(self):
        """Test loading from nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = GAIALoader(temp_dir)
            
            with pytest.raises(FileNotFoundError):
                loader.load_questions("nonexistent.json")
    
    def test_normalize_question_alternate_keys(self):
        """Test question normalization with alternate key names."""
        data = [
            {
                "question_id": "alt_q1",
                "query": "What is this?",
                "answer": "This is a test",
                "difficulty": "medium"
            }
        ]
        
        temp_dir = self.create_temp_questions_file(data, "test.json")
        loader = GAIALoader(temp_dir)
        questions = loader.load_questions("test.json")
        
        assert len(questions) == 1
        assert questions[0].id == "alt_q1"
        assert questions[0].question == "What is this?"
        assert questions[0].gold_answer == "This is a test"
    
    def test_normalize_question_metadata_extraction(self):
        """Test that extra fields are added to metadata."""
        data = [
            {
                "id": "q1",
                "question": "Test?",
                "gold_answer": "Test",
                "difficulty": "hard",
                "topic": "science",
                "level": 3,
                "custom_field": "custom_value"
            }
        ]
        
        temp_dir = self.create_temp_questions_file(data, "test.json")
        loader = GAIALoader(temp_dir)
        questions = loader.load_questions("test.json")
        
        assert questions[0].metadata["difficulty"] == "hard"
        assert questions[0].metadata["topic"] == "science"
        assert questions[0].metadata["level"] == 3
        assert questions[0].metadata["custom_field"] == "custom_value"
    
    def test_get_questions_by_difficulty(self):
        """Test filtering questions by difficulty."""
        data = [
            {"id": "q1", "question": "Q1?", "gold_answer": "A1", "difficulty": "easy"},
            {"id": "q2", "question": "Q2?", "gold_answer": "A2", "difficulty": "hard"},
            {"id": "q3", "question": "Q3?", "gold_answer": "A3", "difficulty": "easy"},
        ]
        
        temp_dir = self.create_temp_questions_file(data, "sample_questions.json")
        loader = GAIALoader(temp_dir)
        
        easy_questions = loader.get_questions_by_difficulty("easy")
        assert len(easy_questions) == 2
        assert all(q.metadata.get("difficulty") == "easy" for q in easy_questions)
    
    def test_get_questions_by_topic(self):
        """Test filtering questions by topic."""
        data = [
            {"id": "q1", "question": "Q1?", "gold_answer": "A1", "topic": "math"},
            {"id": "q2", "question": "Q2?", "gold_answer": "A2", "topic": "science"},
            {"id": "q3", "question": "Q3?", "gold_answer": "A3", "topic": "math"},
        ]
        
        temp_dir = self.create_temp_questions_file(data, "sample_questions.json")
        loader = GAIALoader(temp_dir)
        
        math_questions = loader.get_questions_by_topic("math")
        assert len(math_questions) == 2
        assert all(q.metadata.get("topic") == "math" for q in math_questions)
    
    def test_multiple_questions(self):
        """Test loading multiple questions."""
        data = [
            {"id": f"q{i}", "question": f"Question {i}?", "gold_answer": f"Answer {i}"}
            for i in range(10)
        ]
        
        temp_dir = self.create_temp_questions_file(data, "test.json")
        loader = GAIALoader(temp_dir)
        questions = loader.load_questions("test.json")
        
        assert len(questions) == 10
        assert all(isinstance(q, GAIAQuestion) for q in questions)
