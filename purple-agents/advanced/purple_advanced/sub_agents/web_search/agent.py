"""Web Search Agent for finding information online using Google Search."""

import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

load_dotenv()
# Use Gemini 2.5 Flash for web search (fast, efficient)
MODEL = os.getenv("WEB_SEARCH_MODEL", "gemini-2.5-flash")

web_search_agent = Agent(
    model=MODEL,
    name="web_search_agent",
    instruction=prompt.WEB_SEARCH_PROMPT,
    output_key="search_results",
    tools=[google_search],
)
