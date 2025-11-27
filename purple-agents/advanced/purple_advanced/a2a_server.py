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

"""A2A Mock Server for Purple Advanced Agent.

This server wraps the GAIA coordinator agent and exposes it via the A2A protocol
for evaluation by the green agent.
"""

import logging
import os
import uuid
from typing import Any, Dict

from flask import Flask, jsonify, request

from .agent import gaia_coordinator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage for tasks and responses
tasks: Dict[str, Dict[str, Any]] = {}


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "agent": "purple_advanced_gaia_coordinator"})


@app.route("/a2a/task", methods=["POST"])
def receive_task():
    """Receive a task from the green agent via A2A protocol.
    
    Expected JSON format:
    {
        "task_id": "...",
        "question": "...",
        "metadata": {...}
    }
    """
    data = request.json
    task_id = data.get("task_id") or str(uuid.uuid4())
    question = data.get("question", "")
    metadata = data.get("metadata", {})
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    # Store task
    tasks[task_id] = {
        "question": question,
        "metadata": metadata,
        "status": "processing",
        "answer": None,
    }
    
    logger.info(f"Received task {task_id}: {question[:100]}...")
    
    # Process task synchronously (blocking)
    try:
        # For now, use a simple approach without the coordinator
        # TODO: Implement proper ADK agent invocation
        answer = f"Coordinator not yet implemented for question: {question[:50]}..."
        
        tasks[task_id]["answer"] = answer
        tasks[task_id]["status"] = "completed"
        logger.info(f"Task {task_id} completed: {answer[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}", exc_info=True)
        tasks[task_id]["status"] = "completed"  # Still return completed
        tasks[task_id]["answer"] = f"Error: {str(e)}"
    
    return jsonify({"task_id": task_id, "status": "accepted"}), 202


@app.route("/a2a/response/<task_id>", methods=["GET"])
def get_response(task_id: str):
    """Retrieve the response for a completed task.
    
    Returns:
        JSON with task status and answer (if completed)
    """
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = tasks[task_id]
    
    response = {
        "task_id": task_id,
        "status": task["status"],
    }
    
    if task["status"] == "completed":
        response["answer"] = task["answer"]
    elif task["status"] == "error":
        response["error"] = task["answer"]
    
    return jsonify(response)


@app.route("/a2a/tasks", methods=["GET"])
def list_tasks():
    """List all tasks (for debugging)."""
    return jsonify({
        "tasks": [
            {
                "task_id": tid,
                "question": task["question"][:50] + "...",
                "status": task["status"],
            }
            for tid, task in tasks.items()
        ]
    })


def main():
    """Run the A2A server."""
    port = int(os.getenv("PURPLE_ADVANCED_PORT", "8081"))
    logger.info(f"Starting Purple Advanced Agent A2A server on port {port}")
    logger.info("Agent: GAIA Coordinator with sub-agents (web_search, deep_analyzer, calculator)")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
