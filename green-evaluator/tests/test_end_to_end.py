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

"""End-to-end integration tests for the GAIA evaluator."""

import pytest
import time
import threading
from purple_baseline.a2a_mock_server import app
from agent.evaluator import GAIAEvaluator


@pytest.fixture(scope="module")
def mock_server():
    """Start the mock purple agent server in a background thread."""
    def run_server():
        app.run(host="localhost", port=8080, debug=False, use_reloader=False)
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield
    
    # Server will be automatically stopped when process exits


def test_end_to_end_evaluation(mock_server):
    """Test full end-to-end evaluation flow."""
    evaluator = GAIAEvaluator(
        data_dir="data/gaia",
        purple_agent_url="http://localhost:8080",
        results_dir="results/test"
    )
    
    try:
        # Run evaluation on a subset
        summary = evaluator.run_evaluation(max_questions=5)
        
        # Check results
        assert summary.total_questions == 5
        assert 0.0 <= summary.average_score <= 1.0
        assert len(summary.results) == 5
        
        # Check that each result has required fields
        for result in summary.results:
            assert result.task_id
            assert result.question
            assert result.gold_answer
            assert result.predicted_answer is not None
            assert 0.0 <= result.score <= 1.0
        
        # Save results
        evaluator.save_results(summary, "test_summary.json")
        
    finally:
        evaluator.cleanup()


def test_health_check(mock_server):
    """Test purple agent health check."""
    evaluator = GAIAEvaluator(
        data_dir="data/gaia",
        purple_agent_url="http://localhost:8080"
    )
    
    try:
        is_healthy = evaluator.protocol.health_check()
        assert is_healthy is True
    finally:
        evaluator.cleanup()


def test_evaluation_reproducibility(mock_server):
    """Test that evaluation produces reproducible results."""
    evaluator1 = GAIAEvaluator(
        data_dir="data/gaia",
        purple_agent_url="http://localhost:8080"
    )
    
    evaluator2 = GAIAEvaluator(
        data_dir="data/gaia",
        purple_agent_url="http://localhost:8080"
    )
    
    try:
        # Run same evaluation twice
        summary1 = evaluator1.run_evaluation(max_questions=3)
        summary2 = evaluator2.run_evaluation(max_questions=3)
        
        # Results should be identical
        assert summary1.total_questions == summary2.total_questions
        assert summary1.average_score == summary2.average_score
        
        # Individual results should match
        for r1, r2 in zip(summary1.results, summary2.results):
            assert r1.task_id == r2.task_id
            assert r1.score == r2.score
            
    finally:
        evaluator1.cleanup()
        evaluator2.cleanup()
