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
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4
import asyncio

import httpx
from a2a.client import (
    A2ACardResolver,
    ClientConfig,
    ClientFactory,
)
from a2a.types import (
    Message,
    Part,
    Role,
    TextPart,
    DataPart,
)

from .gaia_loader import GAIALoader
from .schemas import EvaluationResult, EvaluationSummary
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
            purple_agent_url: Base URL of the purple agent (e.g., http://localhost:8080)
            results_dir: Directory to save evaluation results
            numerical_tolerance: Tolerance for numerical comparisons
            task_timeout: Timeout for each task in seconds
        """
        self.data_dir = pathlib.Path(data_dir)
        self.results_dir = pathlib.Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = GAIALoader(data_dir)
        self.scorer = GAIAScorer(numerical_tolerance=numerical_tolerance)
        self.task_timeout = task_timeout
        self.purple_agent_url = purple_agent_url
        
        # Initialize httpx client and A2A client (will be set up async)
        self.httpx_client: Optional[httpx.AsyncClient] = None
        self.a2a_client = None  # Will be created by ClientFactory
        
        logger.info(f"Will connect to purple agent at: {purple_agent_url}")
        
        logger.info(f"Initialized GAIA Evaluator")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Purple agent URL: {purple_agent_url}")
        logger.info(f"Results directory: {self.results_dir}")
    
    async def _setup_client(self) -> None:
        """Setup async httpx client and A2A client using ClientFactory."""
        if self.a2a_client is not None:
            return  # Already initialized
            
        logger.info("Setting up A2A client...")
        self.httpx_client = httpx.AsyncClient(timeout=self.task_timeout)
        
        # Fetch agent card
        resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url=self.purple_agent_url,
        )
        
        agent_card = await resolver.get_agent_card()
        logger.info(f"Successfully fetched agent card: {agent_card.name}")
        
        # Create A2A client using ClientFactory
        config = ClientConfig(
            httpx_client=self.httpx_client,
            streaming=False,  # We'll use non-streaming for simplicity
        )
        factory = ClientFactory(config)
        self.a2a_client = factory.create(agent_card)
        logger.info("A2A client initialized successfully")
    
    async def _send_question(self, question_text: str) -> str:
        """Send a question to the purple agent via A2A.
        
        Args:
            question_text: The question to send
            
        Returns:
            The agent's response text
        """
        if self.a2a_client is None:
            await self._setup_client()
        
        # Create message using Message class
        outbound_msg = Message(
            kind="message",
            role=Role.user,
            parts=[Part(TextPart(kind="text", text=question_text))],
            message_id=uuid4().hex,
        )
        
        # Send message and collect events
        last_event = None
        response_text = ""
        
        async for event in self.a2a_client.send_message(outbound_msg):
            last_event = event
        
        # Extract text from the last event
        if isinstance(last_event, Message):
            # Direct message response
            for part in last_event.parts:
                if isinstance(part.root, TextPart):
                    response_text += part.root.text
                elif isinstance(part.root, DataPart):
                    response_text += part.root.data
        elif isinstance(last_event, tuple) and len(last_event) == 2:
            # Task response (task, update)
            task, update = last_event
            if task.status and task.status.message:
                for part in task.status.message.parts:
                    if isinstance(part.root, TextPart):
                        response_text += part.root.text
                    elif isinstance(part.root, DataPart):
                        response_text += part.root.data
            # Also check artifacts
            if task.artifacts:
                for artifact in task.artifacts:
                    for part in artifact.parts:
                        if isinstance(part.root, TextPart):
                            response_text += part.root.text
                        elif isinstance(part.root, DataPart):
                            response_text += part.root.data
        
        if not response_text:
            logger.warning("No text found in response")
        
        return response_text.strip()
    
    async def run_evaluation_async(
        self, 
        filename: str = "sample_questions.json",
        max_questions: Optional[int] = None
    ) -> EvaluationSummary:
        """Run full evaluation on GAIA questions (async).
        
        Args:
            filename: Name of the questions file to load
            max_questions: Maximum number of questions to evaluate (None for all)
            
        Returns:
            EvaluationSummary with results and metrics
        """
        logger.info(f"Starting evaluation with file: {filename}")
        
        # Load questions
        questions = self.loader.load_questions(filename)
        if max_questions:
            questions = questions[:max_questions]
        
        logger.info(f"Loaded {len(questions)} questions")
        
        # Evaluate each question using a2a-sdk
        results = []
        for idx, question in enumerate(questions):
            logger.info(f"Evaluating question {idx + 1}/{len(questions)}: {question.id}")
            
            try:
                logger.debug("Sending question to purple agent via A2A")
                predicted_answer = await self._send_question(question.question)
                logger.debug(f"Received response: {predicted_answer[:100] if predicted_answer else 'empty'}...")
                
            except Exception as e:
                logger.error(f"Error calling purple agent for task {question.id}: {e}", exc_info=True)
                predicted_answer = ""
            
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
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
    
    def run_evaluation(
        self, 
        filename: str = "sample_questions.json",
        max_questions: Optional[int] = None
    ) -> EvaluationSummary:
        """Run full evaluation on GAIA questions (sync wrapper).
        
        Args:
            filename: Name of the questions file to load
            max_questions: Maximum number of questions to evaluate (None for all)
            
        Returns:
            EvaluationSummary with results and metrics
        """
        return asyncio.run(self.run_evaluation_async(filename, max_questions))
    
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
    
    async def cleanup_async(self) -> None:
        """Cleanup resources async."""
        if self.httpx_client:
            try:
                await self.httpx_client.aclose()
                logger.info("Closed httpx client")
            except RuntimeError as e:
                # Event loop already closed, ignore
                if "Event loop is closed" not in str(e):
                    raise
    
    def cleanup(self) -> None:
        """Cleanup resources (sync wrapper)."""
        if self.httpx_client:
            try:
                # Check if there's already a running event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're inside an async context, schedule cleanup
                    loop.create_task(self.cleanup_async())
                else:
                    # No running loop, safe to use asyncio.run
                    asyncio.run(self.cleanup_async())
            except RuntimeError:
                # Event loop is closed or doesn't exist, that's fine
                logger.info("Cleanup skipped (event loop unavailable)")
        logger.info("Cleanup complete")


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
