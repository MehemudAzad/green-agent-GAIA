"""A2A Server for Purple Advanced Agent using ADK to_a2a()."""

import logging
import os
import warnings
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .agent import gaia_test_taker

# Load environment variables
load_dotenv()

# ANSI color codes for clean logging
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Custom formatter with colors and clean format
class CleanFormatter(logging.Formatter):
    def format(self, record):
        level_colors = {
            'DEBUG': Colors.CYAN,
            'INFO': Colors.GREEN,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'CRITICAL': Colors.RED + Colors.BOLD
        }
        color = level_colors.get(record.levelname, Colors.RESET)
        level_prefix = f"{color}[{record.levelname}]{Colors.RESET}"
        return f"{level_prefix} {record.getMessage()}"

# Setup clean logging for our module only
handler = logging.StreamHandler()
handler.setFormatter(CleanFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# Custom handler for Google ADK/LLM logs to make them beautiful
class LLMFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        
        # Filter out app name mismatch warnings completely
        if 'App name mismatch' in msg:
            return None
        
        # Clean up LLM request logs with sub-agent identification
        if 'Sending out request' in msg:
            if 'gemini-2.5-pro' in msg:
                return f"{Colors.CYAN}🧠 Main agent thinking...{Colors.RESET}"
            elif 'gemini-2.5-flash' in msg and 'lite' not in msg.lower():
                return f"{Colors.MAGENTA}🔍 Web search agent...{Colors.RESET}"
            elif 'gemini-2.0-flash' in msg:
                return f"{Colors.BLUE}🤔 Deep analyzer agent...{Colors.RESET}"
            elif 'flash-lite' in msg.lower():
                return f"{Colors.YELLOW}🔢 Calculator agent...{Colors.RESET}"
            else:
                return f"{Colors.CYAN}🤔 LLM processing...{Colors.RESET}"
        
        # Clean up response logs
        elif 'Response received' in msg:
            return f"{Colors.GREEN}✓ Response ready{Colors.RESET}"
        
        # Clean up runner logs
        elif 'Closing runner' in msg:
            return f"{Colors.YELLOW}🔄 Resetting agent state{Colors.RESET}"
        elif 'Runner closed' in msg:
            return None  # Skip this redundant message
        
        return msg

class SkipNoneFilter(logging.Filter):
    """Filter out None messages from LLM formatter."""
    def filter(self, record):
        formatter = LLMFormatter()
        return formatter.format(record) is not None

# Setup clean logging for ADK libraries
llm_handler = logging.StreamHandler()
llm_handler.setFormatter(LLMFormatter())
llm_handler.addFilter(SkipNoneFilter())

# Apply to ADK and LLM loggers with custom formatter
for logger_name in ['google_adk', 'google.adk', 'google_adk.llms.google_llm', 'google.adk.agents.runners']:
    lib_logger = logging.getLogger(logger_name)
    lib_logger.handlers = []
    lib_logger.addHandler(llm_handler)
    lib_logger.setLevel(logging.INFO)
    lib_logger.propagate = False

# Suppress completely noisy logs
logging.getLogger('google_genai').setLevel(logging.ERROR)
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('a2a').setLevel(logging.ERROR)

# Suppress experimental warnings and ADK internal warnings
warnings.filterwarnings('ignore', message='.*EXPERIMENTAL.*')
warnings.filterwarnings('ignore', message='.*App name mismatch.*')

# Get port from environment or use default
PORT = int(os.getenv("PURPLE_ADVANCED_PORT", "8081"))

# Get model from environment or use default
MODEL = os.getenv("PURPLE_ADVANCED_MODEL", "gemini-2.5-pro")

# Update agent model if configured
if hasattr(gaia_test_taker, 'model'):
    gaia_test_taker.model = MODEL

# Wrap the agent with A2A protocol
# This auto-generates an agent card and exposes it at /.well-known/agent-card.json
a2a_app = to_a2a(gaia_test_taker, port=PORT)

# Get sub-agent models for display
web_model = os.getenv("WEB_SEARCH_MODEL", "gemini-2.5-flash")
deep_model = os.getenv("DEEP_ANALYZER_MODEL", "gemini-1.5-flash")
calc_model = os.getenv("CALCULATOR_MODEL", "gemini-2.5-flash-lite")

logger.info(f"🎯 {Colors.BOLD}Purple Advanced Agent (Test Taker){Colors.RESET}")
logger.info(f"   🤖 Agent: {Colors.CYAN}{gaia_test_taker.name}{Colors.RESET}")
logger.info(f"   🔌 Port: {Colors.YELLOW}{PORT}{Colors.RESET}")
logger.info(f"   🧠 Main Model: {Colors.CYAN}{MODEL}{Colors.RESET}")
logger.info(f"   📋 Agent card: {Colors.BLUE}http://localhost:{PORT}/.well-known/agent-card.json{Colors.RESET}")
logger.info(f"   🔧 Sub-agents:")
logger.info(f"      🔍 Web Search: {Colors.MAGENTA}{web_model}{Colors.RESET}")
logger.info(f"      🤔 Deep Analyzer: {Colors.BLUE}{deep_model}{Colors.RESET}")
logger.info(f"      🔢 Calculator: {Colors.YELLOW}{calc_model}{Colors.RESET}")


def main():
    """Run the A2A server."""
    import uvicorn
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 {Colors.BOLD}Starting Purple Advanced Agent (Test Taker){Colors.RESET}")
    logger.info(f"{'='*70}")
    logger.info(f"   🌐 Server: {Colors.GREEN}http://0.0.0.0:{PORT}{Colors.RESET}")
    logger.info(f"   🤖 Type: Multi-agent test taker")
    logger.info(f"   🧠 Model: {Colors.CYAN}{MODEL}{Colors.RESET}")
    logger.info(f"   ⚡ Sub-agents: web_search, deep_analyzer, calculator")
    logger.info(f"{'='*70}")
    logger.info(f"   {Colors.YELLOW}Press CTRL+C to quit{Colors.RESET}\n")
    
    # Run the A2A app with uvicorn
    uvicorn.run(
        "purple_advanced.a2a_server:a2a_app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )


if __name__ == "__main__":
    main()
