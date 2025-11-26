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

"""Main evaluator agent for GAIA benchmark."""

import json
import logging
import os
import pathlib
import random
from datetime import datetime
from typing import Any, Dict, Optional

from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.agents.callback_context import CallbackContext

from .a2a_protocol import A2AProtocol
from .gaia_loader import GAIALoader
from .schemas import A2ATask, EvaluationResult, EvaluationSummary
from .scoring import GAIAScorer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


class GAIAEvaluator:
    """Green Agent: Evaluator for A2A-compatible purple agents on GAIA benchmark."""
    
    def __init__(
        self,
        data_dir: str,
        purple_agent_url: str,
        results_dir: str = "results",
        numerical_tolerance: float = 0.01,
        task_timeout: int = 60
    ):
        """Initialize the GAIA evaluator.
        
        Args:
            data_dir: Directory containing GAIA questions
            purple_agent_url: Base URL of the purple agent
            results_dir: Directory to save evaluation results
            numerical_tolerance: Tolerance for numerical comparisons
            task_timeout: Timeout for each task in seconds
        """
        self.data_dir = pathlib.Path(data_dir)
        self.results_dir = pathlib.Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = GAIALoader(data_dir)
        self.protocol = A2AProtocol(purple_agent_url, timeout=task_timeout)
        self.scorer = GAIAScorer(numerical_tolerance=numerical_tolerance)
        
        logger.info(f"Initialized GAIA Evaluator")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Purple agent URL: {purple_agent_url}")
        logger.info(f"Results directory: {self.results_dir}")
    
    def run_evaluation(
        self, 
        filename: str = "sample_questions.json",
        max_questions: Optional[int] = None
    ) -> EvaluationSummary:
        """Run full evaluation on GAIA questions.
        
        Args:
            filename: Name of the questions file to load
            max_questions: Maximum number of questions to evaluate (None for all)
            
        Returns:
            EvaluationSummary with results and metrics
        """
        logger.info(f"Starting evaluation with file: {filename}")
        
        # Check purple agent health
        if not self.protocol.health_check():
            logger.warning("Purple agent health check failed - proceeding anyway")
        
        # Load questions
        questions = self.loader.load_questions(filename)
        if max_questions:
            questions = questions[:max_questions]
        
        logger.info(f"Loaded {len(questions)} questions")
        
        # Evaluate each question
        results = []
        for idx, question in enumerate(questions):
            logger.info(f"Evaluating question {idx + 1}/{len(questions)}: {question.id}")
            
            # Create A2A task
            task = A2ATask(
                task_id=question.id,
                question=question.question,
                metadata=question.metadata
            )
            
            # Send task and receive response
            response = self.protocol.send_and_receive(task)
            
            if response is None:
                logger.error(f"No response received for task {task.task_id}")
                predicted_answer = ""
            else:
                predicted_answer = response.answer
            
            # Score the answer
            score, exact_match, normalized_match = self.scorer.score(
                predicted_answer, 
                question.gold_answer
            )
            
            # Create evaluation result
            result = EvaluationResult(
                task_id=question.id,
                question=question.question,
                gold_answer=question.gold_answer,
                predicted_answer=predicted_answer,
                score=score,
                exact_match=exact_match,
                normalized_match=normalized_match,
                metadata=question.metadata
            )
            results.append(result)
            
            logger.info(
                f"Question {question.id} - Score: {score:.2f}, "
                f"Exact: {exact_match}, Normalized: {normalized_match}"
            )
        
        # Compute summary statistics
        total_questions = len(results)
        total_score = sum(r.score for r in results)
        average_score = total_score / total_questions if total_questions > 0 else 0.0
        exact_match_count = sum(1 for r in results if r.exact_match)
        exact_match_rate = exact_match_count / total_questions if total_questions > 0 else 0.0
        normalized_match_count = sum(1 for r in results if r.normalized_match)
        normalized_match_rate = normalized_match_count / total_questions if total_questions > 0 else 0.0
        
        summary = EvaluationSummary(
            total_questions=total_questions,
            total_score=total_score,
            average_score=average_score,
            exact_match_count=exact_match_count,
            exact_match_rate=exact_match_rate,
            normalized_match_count=normalized_match_count,
            normalized_match_rate=normalized_match_rate,
            results=results,
            metadata={
                "filename": filename,
                "timestamp": datetime.utcnow().isoformat(),
                "random_seed": RANDOM_SEED,
                "numerical_tolerance": self.scorer.numerical_tolerance
            }
        )
        
        logger.info("=" * 60)
        logger.info("EVALUATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Questions: {total_questions}")
        logger.info(f"Average Score: {average_score:.4f}")
        logger.info(f"Exact Match Rate: {exact_match_rate:.2%}")
        logger.info(f"Normalized Match Rate: {normalized_match_rate:.2%}")
        logger.info("=" * 60)
        
        return summary
    
    def save_results(self, summary: EvaluationSummary, filename: str = "summary.json") -> None:
        """Save evaluation results to JSON file.
        
        Args:
            summary: EvaluationSummary to save
            filename: Output filename
        """
        output_path = self.results_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self.protocol.close()


def run_evaluation_cli() -> None:
    """CLI entry point for running evaluation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GAIA Benchmark Evaluator")
    parser.add_argument(
        "--data-dir",
        default="data/gaia",
        help="Directory containing GAIA questions"
    )
    parser.add_argument(
        "--purple-agent-url",
        default="http://localhost:8080",
        help="Base URL of the purple agent"
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory to save results"
    )
    parser.add_argument(
        "--filename",
        default="sample_questions.json",
        help="Questions file to load"
    )
    parser.add_argument(
        "--max-questions",
        type=int,
        default=None,
        help="Maximum number of questions to evaluate"
    )
    parser.add_argument(
        "--numerical-tolerance",
        type=float,
        default=0.01,
        help="Tolerance for numerical comparisons"
    )
    parser.add_argument(
        "--task-timeout",
        type=int,
        default=60,
        help="Timeout for each task in seconds"
    )
    
    args = parser.parse_args()
    
    evaluator = GAIAEvaluator(
        data_dir=args.data_dir,
        purple_agent_url=args.purple_agent_url,
        results_dir=args.results_dir,
        numerical_tolerance=args.numerical_tolerance,
        task_timeout=args.task_timeout
    )
    
    try:
        summary = evaluator.run_evaluation(
            filename=args.filename,
            max_questions=args.max_questions
        )
        evaluator.save_results(summary)
    finally:
        evaluator.cleanup()


if __name__ == "__main__":
    run_evaluation_cli()
