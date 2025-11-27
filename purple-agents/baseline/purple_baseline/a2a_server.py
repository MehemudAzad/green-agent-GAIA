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

"""A2A Server for Purple Baseline Agent using ADK to_a2a()."""

import logging
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .agent import baseline_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Wrap the baseline agent with A2A protocol
# This auto-generates an agent card and exposes it at /.well-known/agent-card.json
a2a_app = to_a2a(baseline_agent, port=8080)

logger.info("Purple Baseline Agent A2A server created")
logger.info("Agent: baseline_purple_agent")
logger.info("Port: 8080")
logger.info("Agent card will be available at: http://localhost:8080/.well-known/agent-card.json")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Purple Baseline Agent A2A server on http://0.0.0.0:8080")
    logger.info("Press CTRL+C to quit")
    
    # Run the A2A app with uvicorn
    uvicorn.run(
        "purple_baseline.a2a_server:a2a_app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )
