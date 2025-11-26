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

"""A2A mock server for baseline purple agent."""

import logging
import sys
import os
from pathlib import Path
from typing import Dict
from flask import Flask, request, jsonify

# Add parent directory to path to import baseline_agent
sys.path.insert(0, str(Path(__file__).parent))
from baseline_agent import BaselinePurpleAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
agent = BaselinePurpleAgent()

# In-memory storage for tasks and responses
tasks: Dict[str, dict] = {}
responses: Dict[str, dict] = {}


@app.route("/health", methods=["GET"])
def health_check() -> tuple[dict, int]:
    """Health check endpoint.
    
    Returns:
        JSON response with status
    """
    return jsonify({"status": "healthy", "agent": agent.name}), 200


@app.route("/a2a/task", methods=["POST"])
def receive_task() -> tuple[dict, int]:
    """Receive a task from the green agent.
    
    Expected JSON body:
    {
        "task_id": "...",
        "question": "...",
        "metadata": {...}  # optional
    }
    
    Returns:
        JSON response acknowledging task receipt
    """
    try:
        data = request.get_json()
        
        if not data or "task_id" not in data or "question" not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        task_id = data["task_id"]
        question = data["question"]
        metadata = data.get("metadata", {})
        
        # Store the task
        tasks[task_id] = data
        
        logger.info(f"Received task {task_id}")
        
        # Process the task immediately and store response
        answer = agent.answer_question(question, metadata)
        
        responses[task_id] = {
            "task_id": task_id,
            "answer": answer,
            "metadata": {"processed": True}
        }
        
        logger.info(f"Processed task {task_id} - Answer: {answer}")
        
        return jsonify({"status": "received", "task_id": task_id}), 200
        
    except Exception as e:
        logger.error(f"Error receiving task: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/a2a/response/<task_id>", methods=["GET"])
def get_response(task_id: str) -> tuple[dict, int]:
    """Get the response for a specific task.
    
    Args:
        task_id: Task identifier
        
    Returns:
        JSON response with answer or 404 if not ready
    """
    if task_id in responses:
        logger.info(f"Returning response for task {task_id}")
        return jsonify(responses[task_id]), 200
    else:
        logger.info(f"Response not ready for task {task_id}")
        return jsonify({"error": "Response not ready"}), 404


@app.route("/a2a/tasks", methods=["GET"])
def list_tasks() -> tuple[dict, int]:
    """List all tasks (for debugging).
    
    Returns:
        JSON response with all tasks
    """
    return jsonify({
        "tasks": list(tasks.keys()),
        "responses": list(responses.keys())
    }), 200


def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Run the A2A mock server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting A2A Mock Server on {host}:{port}")
    logger.info(f"Using agent: {agent.name}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A2A Mock Server for Baseline Purple Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
