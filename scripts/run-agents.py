#!/usr/bin/env python3
"""Run both purple and green agents together."""

import subprocess
import time
import sys
import signal
import os
from pathlib import Path

# Change to project directory
os.chdir(Path(__file__).parent)

def run_purple_agent():
    """Start purple agent server."""
    print("\n" + "="*70)
    print("STARTING PURPLE AGENT SERVER")
    print("="*70 + "\n")
    
    try:
        subprocess.run(
            ["python3", "-m", "purple_baseline.a2a_mock_server", "--port", "8080"],
            check=False
        )
    except KeyboardInterrupt:
        print("\nPurple agent stopped")

def run_green_agent():
    """Start green evaluator."""
    print("\n" + "="*70)
    print("STARTING GREEN EVALUATOR")
    print("="*70 + "\n")
    
    try:
        subprocess.run(
            ["python3", "-m", "agent.evaluator", "--max-questions", "10"],
            check=False
        )
    except KeyboardInterrupt:
        print("\nGreen agent stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "purple":
            run_purple_agent()
        elif sys.argv[1] == "green":
            # Wait a bit for purple agent to start
            print("Waiting for purple agent to be ready...")
            time.sleep(2)
            run_green_agent()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python run-agents.py [purple|green]")
    else:
        print("Starting BOTH agents...")
        print("\nUsage:")
        print("  Terminal 1: python3 run-agents.py purple")
        print("  Terminal 2: python3 run-agents.py green")
        print("\nOr just run docker-compose:")
        print("  cd docker && docker-compose up")
