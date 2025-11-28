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

from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Suppress app name mismatch warnings
import warnings
warnings.filterwarnings('ignore', message='.*App name mismatch.*')

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

# ANSI color codes for clean logging
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Custom formatter with colors and clean format
class CleanFormatter(logging.Formatter):
    def format(self, record):
        level_colors = {
            'DEBUG': Colors.CYAN,
            'INFO': Colors.GREEN,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'CRITICAL': Colors.RED + Colors.BOLD
        }
        color = level_colors.get(record.levelname, Colors.RESET)
        level_prefix = f"{color}[{record.levelname}]{Colors.RESET}"
        return f"{level_prefix} {record.getMessage()}"

# Setup clean logging
handler = logging.StreamHandler()
handler.setFormatter(CleanFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# Filter for ADK logs to suppress app name mismatch warnings
class ADKFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        
        # Filter out app name mismatch warnings completely
        if 'App name mismatch' in msg:
            return None
        
        # Clean up LLM request logs
        if 'Sending out request' in msg:
            return f"{Colors.CYAN}🤔 Green coordinator evaluating...{Colors.RESET}"
        
        # Clean up response logs
        elif 'Response received' in msg:
            return f"{Colors.GREEN}✓ Evaluation complete{Colors.RESET}"
        
        # Clean up runner logs
        elif 'Closing runner' in msg:
            return None  # Skip this message
        elif 'Runner closed' in msg:
            return None  # Skip this redundant message
        
        return msg

class SkipNoneFilter(logging.Filter):
    """Filter out None messages from ADK formatter."""
    def filter(self, record):
        formatter = ADKFormatter()
        return formatter.format(record) is not None

# Setup logging for ADK libraries to suppress warnings
adk_handler = logging.StreamHandler()
adk_handler.setFormatter(ADKFormatter())
adk_handler.addFilter(SkipNoneFilter())

for logger_name in ['google_adk', 'google.adk', 'google_adk.llms.google_llm', 'google.adk.agents.runners']:
    lib_logger = logging.getLogger(logger_name)
    lib_logger.handlers = []
    lib_logger.addHandler(adk_handler)
    lib_logger.setLevel(logging.INFO)
    lib_logger.propagate = False

# Suppress noisy logs completely
logging.getLogger('google_genai').setLevel(logging.ERROR)
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)

# Set random seed for reproducibility
RANDOM_SEED = 30
random.seed(RANDOM_SEED)


class GAIAEvaluator:
    """Green Agent: Evaluator for A2A-compatible purple agents on GAIA benchmark."""
    
    def __init__(
        self,
        data_dir: str,
        purple_agent_url: str,
        results_dir: str = "results",
        numerical_tolerance: float = 0.01,
        task_timeout: int = 120,
        use_llm_scoring: bool = False,
        llm_model: str = "gemini-2.5-flash"
    ):
        """Initialize the GAIA evaluator.
        
        Args:
            data_dir: Directory containing GAIA questions
            purple_agent_url: Base URL of the purple agent (e.g., http://localhost:8080)
            results_dir: Directory to save evaluation results
            numerical_tolerance: Tolerance for numerical comparisons
            task_timeout: Timeout for each task in seconds
            use_llm_scoring: Whether to use LLM-powered intelligent scoring
            llm_model: LLM model to use for scoring (if enabled)
        """
        self.data_dir = pathlib.Path(data_dir)
        self.results_dir = pathlib.Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = GAIALoader(data_dir)
        self.scorer = GAIAScorer(numerical_tolerance=numerical_tolerance)
        self.task_timeout = task_timeout
        self.purple_agent_url = purple_agent_url
        self.use_llm_scoring = use_llm_scoring
        self.llm_model = llm_model
        
        # Initialize httpx client and A2A client (will be set up async)
        self.httpx_client: Optional[httpx.AsyncClient] = None
        self.a2a_client = None  # Will be created by ClientFactory
        
        # Initialize LLM coordinator if enabled
        self.green_coordinator = None
        if use_llm_scoring:
            from .green_coordinator import green_coordinator
            self.green_coordinator = green_coordinator
        
        logger.info(f"🎯 {Colors.BOLD}Green Agent (GAIA Evaluator/Coordinator) Initialized{Colors.RESET}")
        logger.info(f"   📁 Data: {self.data_dir}")
        logger.info(f"   🌐 Purple agent (test taker): {purple_agent_url}")
        logger.info(f"   💾 Results: {self.results_dir}")
        logger.info(f"   ⏱️  Timeout: {task_timeout}s per task")
        if use_llm_scoring:
            logger.info(f"   🧠 LLM mode: {Colors.GREEN}ON{Colors.RESET} ({Colors.CYAN}{llm_model}{Colors.RESET})")
        else:
            logger.info(f"   🧠 LLM mode: {Colors.YELLOW}OFF{Colors.RESET} (deterministic only)")
    
    async def _setup_client(self) -> None:
        """Setup async httpx client and A2A client using ClientFactory."""
        if self.a2a_client is not None:
            return  # Already initialized
            
        logger.info(f"🔌 Connecting to purple agent...")
        self.httpx_client = httpx.AsyncClient(timeout=self.task_timeout)
        
        # Fetch agent card
        resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url=self.purple_agent_url,
        )
        
        agent_card = await resolver.get_agent_card()
        logger.info(f"✓ Connected to: {Colors.CYAN}{agent_card.name}{Colors.RESET}")
        
        # Create A2A client using ClientFactory
        config = ClientConfig(
            httpx_client=self.httpx_client,
            streaming=False,  # We'll use non-streaming for simplicity
        )
        factory = ClientFactory(config)
        self.a2a_client = factory.create(agent_card)
    
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
            logger.warning("⚠️  Empty response from purple agent")
        
        return response_text.strip()
    
    async def _llm_evaluate(
        self,
        question: str,
        predicted_answer: str,
        gold_answer: str,
        deterministic_score: float
    ) -> Dict[str, Any]:
        """Use LLM coordinator to evaluate answer quality.
        
        Args:
            question: The original question
            predicted_answer: The purple agent's answer
            gold_answer: The correct answer
            deterministic_score: Score from deterministic matching
            
        Returns:
            Dictionary with LLM evaluation results
        """
        if self.green_coordinator is None:
            return {
                "llm_score": deterministic_score,
                "confidence": "n/a",
                "reasoning": "LLM scoring disabled",
                "sub_agent_findings": "n/a"
            }
        
        # Construct evaluation prompt
        eval_prompt = f"""Evaluate this GAIA benchmark response:

**Question:** {question}

**Gold Answer:** {gold_answer}

**Predicted Answer:** {predicted_answer}

**Deterministic Score:** {deterministic_score}

Please coordinate with your sub-agents to provide a comprehensive evaluation.
Use answer_analyzer to assess quality, semantic_scorer to check equivalence, and quality_assessor for final judgment."""

        try:
            # Use InMemoryRunner pattern from academic-research agent
            from google.adk.runners import InMemoryRunner
            from google.genai import types
            import hashlib
            
            # Create runner for the coordinator
            runner = InMemoryRunner(agent=self.green_coordinator, app_name="green_evaluator")
            
            # Create or get session
            session_id = f"eval_{hashlib.md5(question.encode()).hexdigest()[:8]}"
            session = await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id="evaluator",
                session_id=session_id
            )
            
            # Create message content
            content = types.Content(parts=[types.Part(text=eval_prompt)])
            
            # Run agent and collect response
            output = ""
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            output += part.text
            
            # Extract structured fields
            llm_score = deterministic_score  # fallback
            confidence = "medium"
            reasoning = ""
            sub_agent_findings = ""
            
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("FINAL_SCORE:"):
                    try:
                        llm_score = float(line.split(":", 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("CONFIDENCE:"):
                    confidence = line.split(":", 1)[1].strip()
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
                elif line.startswith("SUB_AGENT_FINDINGS:"):
                    sub_agent_findings = line.split(":", 1)[1].strip()
            
            return {
                "llm_score": llm_score,
                "confidence": confidence,
                "reasoning": reasoning,
                "sub_agent_findings": sub_agent_findings
            }
            
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            return {
                "llm_score": deterministic_score,
                "confidence": "error",
                "reasoning": f"LLM evaluation failed: {str(e)}",
                "sub_agent_findings": "n/a"
            }
    
    async def run_evaluation_async(
        self, 
        filename: str = "validation_complete.json",
        max_questions: Optional[int] = None
    ) -> EvaluationSummary:
        """Run full evaluation on GAIA questions (async).
        
        Args:
            filename: Name of the questions file to load
            max_questions: Maximum number of questions to evaluate (None for all)
            
        Returns:
            EvaluationSummary with results and metrics
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 {Colors.BOLD}Green Agent: Starting GAIA Evaluation{Colors.RESET}")
        logger.info(f"{'='*70}")
        
        # Load questions
        questions = self.loader.load_questions(filename)
        
        # Shuffle questions randomly for variety
        random.shuffle(questions)
        logger.info(f"🔀 Questions shuffled randomly (seed: {RANDOM_SEED})")
        
        if max_questions:
            questions = questions[:max_questions]
        
        logger.info(f"📋 Loaded {Colors.CYAN}{len(questions)}{Colors.RESET} questions from {Colors.YELLOW}{filename}{Colors.RESET}")
        
        # Evaluate each question using a2a-sdk
        results = []
        logger.info("")
        for idx, question in enumerate(questions):
            logger.info(f"\n{'─'*70}")
            logger.info(f"📝 {Colors.BOLD}Question {idx + 1}/{len(questions)}{Colors.RESET} (ID: {question.id})")
            logger.info(f"   {question.question[:80]}{'...' if len(question.question) > 80 else ''}")
            logger.info(f"   🎯 Gold answer: {Colors.YELLOW}{question.gold_answer}{Colors.RESET}")
            
            try:
                predicted_answer = await self._send_question(question.question)
                preview = predicted_answer[:60] if predicted_answer else 'empty'
                logger.info(f"   💬 Response: {preview}{'...' if len(predicted_answer) > 60 else ''}")
                
            except Exception as e:
                logger.error(f"❌ Purple agent error: {e}")
                predicted_answer = ""
            
            # Score the answer
            score, exact_match, normalized_match = self.scorer.score(
                predicted_answer, 
                question.gold_answer
            )
            
            # Use LLM scoring if enabled and deterministic score is 0.0
            llm_eval = None
            final_score = score
            
            if self.use_llm_scoring and score == 0.0 and predicted_answer:
                logger.info(f"   🤖 {Colors.MAGENTA}Invoking LLM evaluation...{Colors.RESET}")
                llm_eval = await self._llm_evaluate(
                    question=question.question,
                    predicted_answer=predicted_answer,
                    gold_answer=question.gold_answer,
                    deterministic_score=score
                )
                final_score = llm_eval["llm_score"]
                conf_emoji = "🟢" if llm_eval['confidence'] == "high" else "🟡" if llm_eval['confidence'] == "medium" else "🔴"
                logger.info(
                    f"   {conf_emoji} LLM Score: {Colors.CYAN}{final_score}{Colors.RESET} "
                    f"(confidence: {llm_eval['confidence']})"
                )
            
            # Create evaluation result
            result_data = {
                "task_id": question.id,
                "question": question.question,
                "gold_answer": question.gold_answer,
                "predicted_answer": predicted_answer,
                "score": final_score,
                "exact_match": exact_match,
                "normalized_match": normalized_match,
                "metadata": question.metadata
            }
            
            # Add LLM evaluation data if available
            if llm_eval:
                result_data["llm_evaluation"] = llm_eval
            
            result = EvaluationResult(**result_data)
            results.append(result)
            
            # Result summary
            score_emoji = "✅" if final_score == 1.0 else "❌" if final_score == 0.0 else "⚠️"
            score_color = Colors.GREEN if final_score == 1.0 else Colors.RED if final_score == 0.0 else Colors.YELLOW
            logger.info(
                f"   {score_emoji} {Colors.BOLD}Score: {score_color}{final_score:.2f}{Colors.RESET} "
                f"(exact: {exact_match}, norm: {normalized_match})"
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
        
        logger.info(f"\n\n{'='*70}")
        logger.info(f"📊 {Colors.BOLD}{Colors.CYAN}EVALUATION SUMMARY{Colors.RESET}")
        logger.info(f"{'='*70}")
        logger.info(f"   Total Questions:      {Colors.BOLD}{total_questions}{Colors.RESET}")
        logger.info(f"   Average Score:        {Colors.BOLD}{Colors.GREEN}{average_score:.4f}{Colors.RESET}")
        logger.info(f"   Exact Match Rate:     {Colors.BOLD}{exact_match_rate:.2%}{Colors.RESET} ({exact_match_count}/{total_questions})")
        logger.info(f"   Normalized Match:     {Colors.BOLD}{normalized_match_rate:.2%}{Colors.RESET} ({normalized_match_count}/{total_questions})")
        logger.info(f"{'='*70}\n")
        
        return summary
    
    def run_evaluation(
        self, 
        filename: str = "validation_complete.json",
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
        
        logger.info(f"💾 Results saved to: {Colors.GREEN}{output_path}{Colors.RESET}")
    
    async def cleanup_async(self) -> None:
        """Cleanup resources async."""
        if self.httpx_client:
            try:
                await self.httpx_client.aclose()
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
                pass


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
        default="validation_complete.json",
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
        default=120,
        help="Timeout for each task in seconds (default: 120s for complex reasoning)"
    )
    parser.add_argument(
        "--use-llm-scoring",
        action="store_true",
        default=True,
        help="Enable LLM-powered intelligent scoring (default: enabled)"
    )
    parser.add_argument(
        "--no-llm-scoring",
        dest="use_llm_scoring",
        action="store_false",
        help="Disable LLM scoring (use deterministic only)"
    )
    parser.add_argument(
        "--llm-model",
        default="gemini-2.5-flash",
        help="LLM model to use for scoring (default: gemini-2.5-flash)"
    )
    
    args = parser.parse_args()
    
    evaluator = GAIAEvaluator(
        data_dir=args.data_dir,
        purple_agent_url=args.purple_agent_url,
        results_dir=args.results_dir,
        numerical_tolerance=args.numerical_tolerance,
        task_timeout=args.task_timeout,
        use_llm_scoring=args.use_llm_scoring,
        llm_model=args.llm_model
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
