#!/usr/bin/env python3
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

"""Quick start script for running the Green GAIA Agent evaluation."""

import subprocess
import sys
import time
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version < (3, 10) or version >= (3, 13):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  Requires Python 3.10-3.12")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def start_purple_agent():
    """Start the purple agent mock server."""
    print("\n🟣 Starting purple agent mock server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "purple_baseline.a2a_mock_server", "--host", "0.0.0.0", "--port", "8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to be ready
        print("⏳ Waiting for purple agent to be ready...")
        for i in range(30):
            try:
                import requests
                response = requests.get("http://localhost:8080/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Purple agent is ready")
                    return process
            except:
                time.sleep(1)
        
        print("❌ Purple agent failed to start")
        process.kill()
        return None
        
    except Exception as e:
        print(f"❌ Error starting purple agent: {e}")
        return None


def run_evaluation():
    """Run the green evaluator."""
    print("\n🟢 Running green evaluator...")
    try:
        subprocess.run([
            sys.executable, "-m", "agent.evaluator",
            "--data-dir", "data/gaia",
            "--purple-agent-url", "http://localhost:8080",
            "--results-dir", "results",
            "--max-questions", "5"  # Run on subset for quick demo
        ], check=True)
        print("\n✅ Evaluation completed successfully!")
        print("📊 Results saved to: results/summary.json")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Evaluation failed")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("🚀 Green GAIA Agent - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if in correct directory
    if not Path("pyproject.toml").exists():
        print("❌ Please run this script from the green-gaia-agent directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start purple agent
    purple_process = start_purple_agent()
    if purple_process is None:
        sys.exit(1)
    
    try:
        # Run evaluation
        success = run_evaluation()
        
        if success:
            print("\n" + "=" * 60)
            print("✨ Quick Start Complete!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Check results/summary.json for evaluation metrics")
            print("2. Run full evaluation: python -m agent.evaluator")
            print("3. Connect your own purple agent")
            print("\nFor more info, see README.md")
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        purple_process.kill()
        print("✅ Purple agent stopped")


if __name__ == "__main__":
    main()
