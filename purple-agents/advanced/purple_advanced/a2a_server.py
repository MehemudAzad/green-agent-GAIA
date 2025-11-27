"""A2A Server for Purple Advanced Agent using ADK to_a2a()."""

import logging
import os
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .agent import gaia_coordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from environment or use default
PORT = int(os.getenv("PURPLE_ADVANCED_PORT", "8081"))

# Wrap the GAIA coordinator with A2A protocol
# This auto-generates an agent card and exposes it at /.well-known/agent-card.json
a2a_app = to_a2a(gaia_coordinator, port=PORT)

logger.info("Purple Advanced Agent (GAIA Coordinator) A2A server created")
logger.info(f"Agent: {gaia_coordinator.name}")
logger.info(f"Port: {PORT}")
logger.info(f"Agent card will be available at: http://localhost:{PORT}/.well-known/agent-card.json")
logger.info("Sub-agents: web_search, deep_analyzer, calculator")


def main():
    """Run the A2A server."""
    import uvicorn
    
    logger.info(f"Starting Purple Advanced Agent A2A server on http://0.0.0.0:{PORT}")
    logger.info("Agent: GAIA Coordinator with sub-agents (web_search, deep_analyzer, calculator)")
    logger.info("Press CTRL+C to quit")
    
    # Run the A2A app with uvicorn
    uvicorn.run(
        "purple_advanced.a2a_server:a2a_app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )


if __name__ == "__main__":
    main()
