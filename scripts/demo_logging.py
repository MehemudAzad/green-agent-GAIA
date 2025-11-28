#!/usr/bin/env python3
"""Demo script to show the improved logging output."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'green-evaluator'))

from agent.evaluator import Colors, logger

print("\n" + "="*70)
print(f"{Colors.BOLD}{Colors.CYAN}Green Agent - Enhanced Logging Demo{Colors.RESET}")
print("="*70 + "\n")

logger.info("🎯 GAIA Evaluator Initialized")
logger.info("   📁 Data: data/gaia")
logger.info("   🌐 Purple agent: http://localhost:8080")
logger.info("   💾 Results: results/")
logger.info("   🧠 LLM mode: ON")

logger.info("\n" + "="*70)
logger.info(f"🚀 {Colors.BOLD}Starting GAIA Evaluation{Colors.RESET}")
logger.info("="*70)

logger.info(f"📋 Loaded {Colors.CYAN}5{Colors.RESET} questions from {Colors.YELLOW}sample_questions.json{Colors.RESET}")

logger.info(f"\n{'─'*70}")
logger.info(f"📝 {Colors.BOLD}Question 1/5{Colors.RESET} (ID: gaia_001)")
logger.info("   What is the capital of France?")
logger.info("   💬 Response: Paris")
logger.info(f"   ✅ {Colors.BOLD}Score: {Colors.GREEN}1.00{Colors.RESET} (exact: True, norm: True)")

logger.info(f"\n{'─'*70}")
logger.info(f"📝 {Colors.BOLD}Question 2/5{Colors.RESET} (ID: gaia_002)")
logger.info("   What is the square root of 144?")
logger.info("   💬 Response: twelve")
logger.info(f"   🤖 {Colors.MAGENTA}Invoking LLM evaluation...{Colors.RESET}")
logger.info(f"   🟢 LLM Score: {Colors.CYAN}1.0{Colors.RESET} (confidence: high)")
logger.info(f"   ✅ {Colors.BOLD}Score: {Colors.GREEN}1.00{Colors.RESET} (exact: False, norm: False)")

logger.info(f"\n{'─'*70}")
logger.info(f"📝 {Colors.BOLD}Question 3/5{Colors.RESET} (ID: gaia_003)")
logger.info("   What is the meaning of life?")
logger.info("   💬 Response: 42")
logger.warning("⚠️  Empty response from purple agent")
logger.info(f"   ❌ {Colors.BOLD}Score: {Colors.RED}0.00{Colors.RESET} (exact: False, norm: False)")

logger.info("\n\n" + "="*70)
logger.info(f"📊 {Colors.BOLD}{Colors.CYAN}EVALUATION SUMMARY{Colors.RESET}")
logger.info("="*70)
logger.info(f"   Total Questions:      {Colors.BOLD}5{Colors.RESET}")
logger.info(f"   Average Score:        {Colors.BOLD}{Colors.GREEN}0.8000{Colors.RESET}")
logger.info(f"   Exact Match Rate:     {Colors.BOLD}60.00%{Colors.RESET} (3/5)")
logger.info(f"   Normalized Match:     {Colors.BOLD}80.00%{Colors.RESET} (4/5)")
logger.info("="*70 + "\n")

logger.info(f"💾 Results saved to: {Colors.GREEN}results/summary.json{Colors.RESET}")

logger.error("❌ LLM evaluation failed: Connection timeout")
logger.warning("⚠️  Falling back to deterministic scoring")

print("\n" + "="*70)
print(f"{Colors.BOLD}Demo Complete!{Colors.RESET}")
print("="*70 + "\n")
