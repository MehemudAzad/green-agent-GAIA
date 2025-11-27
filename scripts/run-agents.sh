#!/bin/bash

# Quick start script for running Green Agent + Purple Agent locally
# Usage: ./run-local.sh [baseline|advanced] [questions-file] [max-questions]

set -e

# Defaults
AGENT_TYPE="${1:-baseline}"
QUESTIONS_FILE="${2:-validation_level1.json}"
MAX_QUESTIONS="${3:-5}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Green Agent + Purple Agent Local Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Validate agent type
if [[ "$AGENT_TYPE" != "baseline" && "$AGENT_TYPE" != "advanced" ]]; then
    echo -e "${YELLOW}Error: AGENT_TYPE must be 'baseline' or 'advanced'${NC}"
    echo "Usage: ./run-local.sh [baseline|advanced] [questions-file] [max-questions]"
    exit 1
fi

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}Warning: .env file not found. Create one from .env.example${NC}"
    echo "Copy: cp .env.example .env"
    echo ""
fi

echo -e "${BLUE}Configuration:${NC}"
echo "  Agent Type:      $AGENT_TYPE"
echo "  Questions File:  $QUESTIONS_FILE"
echo "  Max Questions:   $MAX_QUESTIONS"
echo ""

# Determine port and startup command
if [[ "$AGENT_TYPE" == "baseline" ]]; then
    PORT=8080
    AGENT_CMD="python -m purple_baseline.a2a_mock_server --port $PORT"
    AGENT_NAME="Baseline (Gemini 2.0 Flash)"
else
    PORT=8081
    AGENT_CMD="cd purple-agents/advanced && python -m purple_advanced.a2a_server"
    AGENT_NAME="Advanced (Multi-Agent with Gemini 2.5 Pro)"
fi

echo -e "${GREEN}Step 1: Starting Purple Agent${NC}"
echo -e "  Type: $AGENT_NAME"
echo -e "  Port: $PORT"
echo ""
echo -e "${YELLOW}Open another terminal and run:${NC}"
echo ""
echo -e "${BLUE}$AGENT_CMD${NC}"
echo ""
echo -e "${YELLOW}After agent is ready, run in another terminal:${NC}"
echo ""
eval_cmd="cd green-evaluator && python -m agent.evaluator --purple-agent-url http://localhost:$PORT --filename $QUESTIONS_FILE --max-questions $MAX_QUESTIONS"
echo -e "${BLUE}$eval_cmd${NC}"
echo ""
echo -e "${YELLOW}Or press CTRL+C to exit and run the evaluator command above.${NC}"
echo ""

# Show health check command
echo -e "${GREEN}Step 2: Verify Agent Health${NC}"
echo "  Run in yet another terminal:"
echo -e "${BLUE}  curl http://localhost:$PORT/health${NC}"
echo ""

echo -e "${GREEN}Ready? Start the purple agent with:${NC}"
echo -e "${BLUE}$AGENT_CMD${NC}"
echo ""
echo "Then run the evaluator in another terminal with:"
echo -e "${BLUE}$eval_cmd${NC}"
echo ""

# Prompt to continue
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Start the agent
echo ""
echo -e "${GREEN}Starting $AGENT_NAME on port $PORT...${NC}"
echo ""

if [[ "$AGENT_TYPE" == "baseline" ]]; then
    python -m purple_baseline.a2a_mock_server --port $PORT
else
    cd purple-agents/advanced
    python -m purple_advanced.a2a_server
fi
