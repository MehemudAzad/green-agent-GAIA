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

"""Tests for the GAIA scoring module."""

import pytest
from agent.scoring import GAIAScorer


class TestGAIAScorer:
    """Test suite for GAIAScorer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = GAIAScorer(numerical_tolerance=0.01)
    
    def test_exact_match(self):
        """Test exact string matching."""
        score, exact, normalized = self.scorer.score("Paris", "Paris")
        assert score == 1.0
        assert exact is True
        assert normalized is True
    
    def test_exact_match_case_sensitive(self):
        """Test that exact match is case-sensitive."""
        score, exact, normalized = self.scorer.score("Paris", "paris")
        assert score == 1.0
        assert exact is False
        assert normalized is True  # Normalized match succeeds
    
    def test_normalized_match(self):
        """Test normalized string matching."""
        score, exact, normalized = self.scorer.score("Paris", "paris")
        assert score == 1.0
        assert exact is False
        assert normalized is True
    
    def test_normalized_match_with_punctuation(self):
        """Test normalized matching with punctuation."""
        score, exact, normalized = self.scorer.score("Hello, World!", "hello world")
        assert score == 1.0
        assert exact is False
        assert normalized is True
    
    def test_normalized_match_with_whitespace(self):
        """Test normalized matching with extra whitespace."""
        score, exact, normalized = self.scorer.score("  New  York  ", "new york")
        assert score == 1.0
        assert exact is False
        assert normalized is True
    
    def test_numerical_match_exact(self):
        """Test numerical matching with exact values."""
        score, exact, normalized = self.scorer.score("42", "42")
        assert score == 1.0
        assert exact is True
        assert normalized is True
    
    def test_numerical_match_within_tolerance(self):
        """Test numerical matching within tolerance."""
        score, exact, normalized = self.scorer.score("100", "100.5")
        # 0.5% difference, within 1% tolerance
        assert score == 1.0
        assert exact is False
        assert normalized is False
    
    def test_numerical_match_outside_tolerance(self):
        """Test numerical matching outside tolerance."""
        score, exact, normalized = self.scorer.score("100", "150")
        # 50% difference, outside 1% tolerance
        assert score == 0.0
        assert exact is False
        assert normalized is False
    
    def test_numerical_match_with_text(self):
        """Test numerical extraction from text."""
        score, exact, normalized = self.scorer.score("The answer is 42", "42")
        assert score == 1.0
        assert exact is False
        assert normalized is False
    
    def test_numerical_match_decimal(self):
        """Test numerical matching with decimals."""
        score, exact, normalized = self.scorer.score("3.14", "3.14")
        assert score == 1.0
        assert exact is True
        assert normalized is True
    
    def test_numerical_match_zero(self):
        """Test numerical matching with zero."""
        score, exact, normalized = self.scorer.score("0", "0")
        assert score == 1.0
        assert exact is True
        assert normalized is True
    
    def test_no_match(self):
        """Test when there's no match."""
        score, exact, normalized = self.scorer.score("Paris", "London")
        assert score == 0.0
        assert exact is False
        assert normalized is False
    
    def test_batch_scoring(self):
        """Test batch scoring."""
        predictions = ["Paris", "42", "London"]
        golds = ["Paris", "42", "Berlin"]
        
        results = self.scorer.batch_score(predictions, golds)
        
        assert len(results) == 3
        assert results[0] == (1.0, True, True)  # Exact match
        assert results[1] == (1.0, True, True)  # Exact match
        assert results[2] == (0.0, False, False)  # No match
    
    def test_batch_scoring_length_mismatch(self):
        """Test batch scoring with mismatched lengths."""
        predictions = ["Paris", "42"]
        golds = ["Paris"]
        
        with pytest.raises(ValueError):
            self.scorer.batch_score(predictions, golds)
    
    def test_normalize_helper(self):
        """Test the normalize helper method."""
        assert self.scorer._normalize("Hello, World!") == "hello world"
        assert self.scorer._normalize("  Multiple   Spaces  ") == "multiple spaces"
        assert self.scorer._normalize("UPPERCASE") == "uppercase"
        assert self.scorer._normalize("123-456-789") == "123456789"
    
    def test_extract_number_helper(self):
        """Test the extract_number helper method."""
        assert self.scorer._extract_number("42") == 42.0
        assert self.scorer._extract_number("3.14") == 3.14
        assert self.scorer._extract_number("The answer is 42") == 42.0
        assert self.scorer._extract_number("-17") == -17.0
        assert self.scorer._extract_number("1.5e3") == 1500.0
        assert self.scorer._extract_number("No number here") is None
