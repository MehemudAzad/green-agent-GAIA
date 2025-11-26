#!/bin/bash

set -e

echo "=========================================="
echo "Green Agent Local Test"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Activate virtual environment
echo -e "${YELLOW}[1/4] Setting up environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# 2. Start baseline purple agent in background
echo -e "${YELLOW}[2/4] Starting baseline purple agent on http://localhost:8080${NC}"
python3 -m purple_baseline.a2a_mock_server &
PURPLE_PID=$!
sleep 2

# Check if purple agent started
if ! kill -0 $PURPLE_PID 2>/dev/null; then
    echo -e "${RED}Failed to start purple agent${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Purple agent running (PID: $PURPLE_PID)${NC}"

# 3. Run evaluation
echo -e "${YELLOW}[3/4] Running green agent evaluation...${NC}"
python3 -m agent.evaluator \
    --data-dir data/gaia \
    --purple-agent-url http://localhost:8080 \
    --results-dir results \
    --filename sample_questions.json \
    --max-questions 5

# 4. Cleanup
echo -e "${YELLOW}[4/4] Cleaning up...${NC}"
kill $PURPLE_PID 2>/dev/null || true
wait $PURPLE_PID 2>/dev/null || true

echo -e "${GREEN}=========================================="
echo "Test Complete!"
echo "Results saved to: results/summary.json"
echo "==========================================${NC}"