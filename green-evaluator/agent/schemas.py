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

"""Pydantic schemas for GAIA evaluation."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class GAIAQuestion(BaseModel):
    """Schema for a GAIA benchmark question."""
    
    id: str = Field(..., description="Unique identifier for the question")
    question: str = Field(..., description="The question text")
    gold_answer: str = Field(..., description="The correct answer")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata (difficulty, topic, etc.)"
    )


class A2ATask(BaseModel):
    """Schema for an A2A task sent to the purple agent."""
    
    task_id: str = Field(..., description="Unique task identifier")
    question: str = Field(..., description="The question to be answered")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the task"
    )


class A2AResponse(BaseModel):
    """Schema for an A2A response from the purple agent."""
    
    task_id: str = Field(..., description="Task identifier matching the request")
    answer: str = Field(..., description="The agent's answer")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the response"
    )


class EvaluationResult(BaseModel):
    """Schema for a single evaluation result."""
    
    task_id: str = Field(..., description="Task identifier")
    question: str = Field(..., description="The question")
    gold_answer: str = Field(..., description="The correct answer")
    predicted_answer: str = Field(..., description="The agent's answer")
    score: float = Field(..., description="Score between 0 and 1")
    exact_match: bool = Field(..., description="Whether answer exactly matches")
    normalized_match: bool = Field(..., description="Whether normalized strings match")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional evaluation metadata"
    )
    llm_evaluation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="LLM-powered evaluation details (if enabled)"
    )


class EvaluationSummary(BaseModel):
    """Schema for aggregate evaluation metrics."""
    
    total_questions: int = Field(..., description="Total number of questions")
    total_score: float = Field(..., description="Sum of all scores")
    average_score: float = Field(..., description="Mean score across all questions")
    exact_match_count: int = Field(..., description="Number of exact matches")
    exact_match_rate: float = Field(..., description="Percentage of exact matches")
    normalized_match_count: int = Field(..., description="Number of normalized matches")
    normalized_match_rate: float = Field(..., description="Percentage of normalized matches")
    results: list[EvaluationResult] = Field(
        default_factory=list,
        description="Individual evaluation results"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional summary metadata"
    )
