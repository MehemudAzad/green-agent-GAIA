"""Calculator Agent for mathematical computations."""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from . import prompt

load_dotenv()
# Use Gemini 2.5 Flash-Lite for calculations (ultra-fast)
MODEL = os.getenv("CALCULATOR_MODEL", "gemini-2.5-flash-lite")

calculator_agent = LlmAgent(
    model=MODEL,
    name="calculator_agent",
    description=(
        "Performs mathematical computations, arithmetic operations, "
        "unit conversions, and numerical analysis"
    ),
    instruction=prompt.CALCULATOR_PROMPT,
    output_key="calculation_result",
)
