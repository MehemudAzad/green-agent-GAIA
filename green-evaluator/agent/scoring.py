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

"""Deterministic scoring for GAIA evaluation."""

import re
from typing import Tuple


class GAIAScorer:
    """Deterministic scoring for GAIA benchmark answers."""
    
    def __init__(self, numerical_tolerance: float = 0.01):
        """Initialize the GAIA scorer.
        
        Args:
            numerical_tolerance: Tolerance for numerical answer comparison (default: 1%)
        """
        self.numerical_tolerance = numerical_tolerance
    
    def score(self, predicted: str, gold: str) -> Tuple[float, bool, bool]:
        """Score a predicted answer against the gold answer.
        
        Args:
            predicted: The predicted answer from the agent
            gold: The gold standard answer
            
        Returns:
            Tuple of (score, exact_match, normalized_match)
            - score: float between 0 and 1
            - exact_match: True if strings match exactly
            - normalized_match: True if normalized strings match
        """
        # Check exact match
        exact_match = self._exact_match(predicted, gold)
        if exact_match:
            return 1.0, True, True
        
        # Check normalized match
        normalized_match = self._normalized_match(predicted, gold)
        if normalized_match:
            return 1.0, False, True
        
        # Check numerical match
        numerical_score = self._numerical_match(predicted, gold)
        if numerical_score > 0:
            return numerical_score, False, False
        
        # No match
        return 0.0, False, False
    
    def _exact_match(self, predicted: str, gold: str) -> bool:
        """Check if two strings match exactly.
        
        Args:
            predicted: The predicted answer
            gold: The gold answer
            
        Returns:
            True if strings match exactly
        """
        return predicted == gold
    
    def _normalized_match(self, predicted: str, gold: str) -> bool:
        """Check if two strings match after normalization.
        
        Normalization includes:
        - Converting to lowercase
        - Removing extra whitespace
        - Removing punctuation
        - Stripping leading/trailing whitespace
        
        Args:
            predicted: The predicted answer
            gold: The gold answer
            
        Returns:
            True if normalized strings match
        """
        return self._normalize(predicted) == self._normalize(gold)
    
    def _normalize(self, text: str) -> str:
        """Normalize a text string for comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation (keep alphanumeric and spaces)
        text = re.sub(r'[^\w\s]', '', text)
        
        # Normalize whitespace (multiple spaces to single space)
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _numerical_match(self, predicted: str, gold: str) -> float:
        """Check if answers match numerically within tolerance.
        
        Args:
            predicted: The predicted answer
            gold: The gold answer
            
        Returns:
            1.0 if numbers match within tolerance, 0.0 otherwise
        """
        predicted_num = self._extract_number(predicted)
        gold_num = self._extract_number(gold)
        
        if predicted_num is None or gold_num is None:
            return 0.0
        
        # Avoid division by zero
        if gold_num == 0:
            if predicted_num == 0:
                return 1.0
            else:
                return 0.0
        
        # Check if within relative tolerance
        relative_error = abs(predicted_num - gold_num) / abs(gold_num)
        if relative_error <= self.numerical_tolerance:
            return 1.0
        
        return 0.0
    
    def _extract_number(self, text: str) -> float | None:
        """Extract a numerical value from text.
        
        Args:
            text: Text potentially containing a number
            
        Returns:
            Extracted number as float, or None if no number found
        """
        # Try to parse the entire string as a number
        try:
            return float(text.strip())
        except ValueError:
            pass
        
        # Try to find a number in the string
        # Match integers, decimals, and scientific notation
        number_pattern = r'-?\d+\.?\d*(?:[eE][-+]?\d+)?'
        matches = re.findall(number_pattern, text)
        
        if matches:
            try:
                # Return the first number found
                return float(matches[0])
            except ValueError:
                pass
        
        return None
    
    def batch_score(self, predictions: list[str], golds: list[str]) -> list[Tuple[float, bool, bool]]:
        """Score a batch of predictions.
        
        Args:
            predictions: List of predicted answers
            golds: List of gold answers
            
        Returns:
            List of (score, exact_match, normalized_match) tuples
            
        Raises:
            ValueError: If lists have different lengths
        """
        if len(predictions) != len(golds):
            raise ValueError(
                f"Predictions and golds must have same length: "
                f"{len(predictions)} != {len(golds)}"
            )
        
        return [self.score(pred, gold) for pred, gold in zip(predictions, golds)]
