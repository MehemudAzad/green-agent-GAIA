PROMPT START

Create a full implementation scaffold for a Green Agent (Evaluator) for the AgentX–AgentBeats Competition using the GAIA benchmark and the Google Agent Developer Kit (ADK).
This green agent must evaluate A2A-compatible purple agents end-to-end.

Follow these requirements precisely:

1. Project Goal
We are building a “green agent” that:
Loads GAIA benchmark questions (text reasoning + tool use tasks)
Sends tasks to an external purple agent via A2A protocol
Receives the purple agent’s answers
Scores them deterministically
Produces aggregate metrics
Runs fully automated in Docker, reproducibly
Provides a baseline purple agent implementation to demonstrate evaluation

2. Use the Google ADK
Generate code using:
Python
Google ADK (Agent Orchestration, PromptGraph, ToolGraph)
ADK runtimes + state management
Minimal external dependencies
Avoid any local state that breaks reproducibility
The green agent must be “stateless per run” except for GAIA data.


3. Benchmark Implementation Requirements

Implement a GAIA-style benchmark pipeline:

3.1 Loader

A module for loading GAIA questions from data/gaia/

Normalize into:

{
  "id": "...",
  "question": "...",
  "metadata": { "difficulty": "...", "topic": "..." },
  "gold_answer": "..."
}

3.2 Task Dispatcher (A2A)

Create an A2A interface:

send_task(question) → sends prompt to purple agent

receive_response() → returns answer from purple agent

Validate that the purple agent stays within format

3.3 Scoring

Implement deterministic scoring:

Exact match

Normalized string match

Optional numerical tolerance for numeric questions

Produce per-question scores + final aggregate

3.4 Reproducibility

No randomness

Each run must produce identical results

Random seeds fixed

No calls to external APIs except A2A purple agent


General directory structure:
green-gaia-agent/
    README.md
    docker/
        Dockerfile
        entrypoint.sh
    agent/
        __init__.py
        evaluator.py
        gaia_loader.py
        scoring.py
        a2a_protocol.py
        schemas.py
    purple_baseline/
        baseline_agent.py
        a2a_mock_server.py
    data/
        gaia/
            sample_questions.json
    tests/
        test_scoring.py
        test_loader.py
        test_end_to_end.py

5. Provide the following files:
5.1 README.md

Abstract

Execution instructions

How to connect purple agents via A2A

How to run dockerized evaluator

How scoring works

Reproducibility guarantees

5.2 evaluator.py

The main green agent runnable:

Loads GAIA tasks

Runs evaluation loop

Logs outputs

Dumps metrics to results/summary.json

5.3 Baseline Purple Agent

Provide a minimal purple agent that:

Accepts A2A tasks

Echoes or heuristically answers

Demonstrates end-to-end connectivity


5.4 A2A protocol

Create a minimal HTTP-based protocol:
POST /a2a/task
{
  "task_id": "...",
  "question": "..."
}

POST /a2a/response
{
  "task_id": "...",
  "answer": "..."
}


6. Docker Requirements

Create a Dockerfile that:

Installs Python environment

Installs Google ADK

Copies project files

Runs evaluator end-to-end

Requires no manual interaction

7. Style

Production-quality, modular Python

Clean architecture

Extensible so new benchmarks can be plugged in

