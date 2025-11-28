#!/bin/bash
# Demo script to show improved logging for all agents

echo ""
echo "========================================================================"
echo "           🎨 Agent Logging Demo - Clean & Colorful Output"
echo "========================================================================"
echo ""
echo "This demo shows the improved logging for:"
echo "  1. 🟣 Purple Baseline Agent (port 8080)"
echo "  2. 🟣 Purple Advanced Agent (port 8081)" 
echo "  3. 🟢 Green Evaluator Agent"
echo ""
echo "========================================================================"
echo ""

# Check if virtual environments exist
if [ ! -d "purple-agents/baseline/venv" ]; then
    echo "❌ Purple baseline venv not found. Run setup first."
    exit 1
fi

if [ ! -d "purple-agents/advanced/venv" ]; then
    echo "❌ Purple advanced venv not found. Run setup first."
    exit 1
fi

if [ ! -d "green-evaluator/venv" ]; then
    echo "❌ Green evaluator venv not found. Run setup first."
    exit 1
fi

echo "✓ All virtual environments found"
echo ""

# Demo 1: Purple Baseline Agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 1: Purple Baseline Agent Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd purple-agents/baseline
source venv/bin/activate
echo ""
timeout 3 python -m purple_baseline.a2a_server 2>&1 || true
deactivate
cd ../..
echo ""

# Demo 2: Purple Advanced Agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 2: Purple Advanced Agent Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd purple-agents/advanced
source venv/bin/activate
echo ""
timeout 3 python -m purple_advanced.a2a_server 2>&1 || true
deactivate
cd ../..
echo ""

# Demo 3: Green Evaluator (logging demo)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 3: Green Evaluator Logging"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd green-evaluator
source venv/bin/activate
echo ""
python ../scripts/demo_logging.py
deactivate
cd ..
echo ""

echo "========================================================================"
echo "                    ✨ Demo Complete!"
echo "========================================================================"
echo ""
echo "Key Improvements:"
echo "  ✓ No timestamps or module names (clean)"
echo "  ✓ Color-coded log levels (green/yellow/red)"
echo "  ✓ Contextual emojis for quick scanning"
echo "  ✓ Better visual hierarchy with separators"
echo "  ✓ Confidence indicators with colored dots"
echo ""
echo "To run agents normally:"
echo "  Terminal 1: cd purple-agents/baseline && source venv/bin/activate && python -m purple_baseline.a2a_server"
echo "  Terminal 2: cd green-evaluator && source venv/bin/activate && python -m agent.evaluator --purple-agent-url http://localhost:8080"
echo ""
