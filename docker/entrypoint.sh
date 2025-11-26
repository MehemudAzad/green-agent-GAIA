#!/bin/bash
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

# Entrypoint script for Docker container
# This script handles starting the purple agent mock server and running the evaluator

set -e

echo "=========================================="
echo "Green GAIA Agent - Evaluator"
echo "=========================================="

# Check if we should start the purple agent server
if [ "${START_PURPLE_AGENT}" = "true" ]; then
    echo "Starting purple agent mock server..."
    python -m purple_baseline.a2a_mock_server --host 0.0.0.0 --port 8080 &
    PURPLE_PID=$!
    echo "Purple agent started with PID: $PURPLE_PID"
    
    # Wait for server to be ready
    echo "Waiting for purple agent to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo "Purple agent is ready!"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 1
    done
fi

# Set default values if not provided
DATA_DIR="${DATA_DIR:-/app/data/gaia}"
PURPLE_AGENT_URL="${PURPLE_AGENT_URL:-http://localhost:8080}"
RESULTS_DIR="${RESULTS_DIR:-/app/results}"
MAX_QUESTIONS="${MAX_QUESTIONS:-}"
NUMERICAL_TOLERANCE="${NUMERICAL_TOLERANCE:-0.01}"
TASK_TIMEOUT="${TASK_TIMEOUT:-60}"

echo ""
echo "Configuration:"
echo "  Data Directory: $DATA_DIR"
echo "  Purple Agent URL: $PURPLE_AGENT_URL"
echo "  Results Directory: $RESULTS_DIR"
echo "  Max Questions: ${MAX_QUESTIONS:-all}"
echo "  Numerical Tolerance: $NUMERICAL_TOLERANCE"
echo "  Task Timeout: ${TASK_TIMEOUT}s"
echo "=========================================="
echo ""

# Build the command
CMD="python -m agent.evaluator --data-dir $DATA_DIR --purple-agent-url $PURPLE_AGENT_URL --results-dir $RESULTS_DIR --numerical-tolerance $NUMERICAL_TOLERANCE --task-timeout $TASK_TIMEOUT"

if [ -n "$MAX_QUESTIONS" ]; then
    CMD="$CMD --max-questions $MAX_QUESTIONS"
fi

# Run the evaluator
echo "Starting evaluation..."
eval $CMD

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "Evaluation completed successfully!"
    echo "Results saved to: $RESULTS_DIR/summary.json"
else
    echo "Evaluation failed with exit code: $EXIT_CODE"
fi
echo "=========================================="

# Cleanup
if [ -n "$PURPLE_PID" ]; then
    echo "Stopping purple agent..."
    kill $PURPLE_PID 2>/dev/null || true
fi

exit $EXIT_CODE
