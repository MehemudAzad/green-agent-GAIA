# Green GAIA Agent - A2A Evaluator

A production-quality evaluator for the AgentX–AgentBeats Competition that evaluates A2A-compatible purple agents on the GAIA benchmark using Google ADK.

## 🎯 Overview

This project implements a **Green Agent (Evaluator)** that assesses **Purple Agents (Test Takers)** on the GAIA benchmark using the official **Agent-to-Agent (A2A) Protocol**. Both agents are built with **Google Agent Development Kit (ADK)** and communicate via standardized A2A messaging.

## 🏗️ Architecture

### Directory Structure

```
green-gaia-agent/
├── green-evaluator/           # Green Agent (A2A Evaluator)
│   ├── agent/
│   │   ├── evaluator.py       # Main orchestrator & evaluation loop
│   │   ├── green_coordinator.py # LLM coordinator with sub-agents
│   │   ├── gaia_loader.py     # GAIA benchmark data loader
│   │   ├── scoring.py         # Deterministic scoring engine
│   │   ├── schemas.py         # Pydantic data models
│   │   └── sub_agents/        # LLM evaluation sub-agents
│   │       ├── semantic_scorer.py     # Semantic equivalence checker
│   │       ├── answer_analyzer.py     # Quality assessment
│   │       └── quality_assessor.py    # Final judgment synthesizer
│   ├── data/gaia/             # GAIA benchmark datasets
│   └── results/               # Evaluation outputs (JSON)
│
├── purple-agents/             # Purple Agents (A2A Test Takers)
│   ├── baseline/              # Simple single-LLM agent (port 8080)
│   │   └── purple_baseline/
│   │       ├── agent.py       # Gemini 2.5 Flash agent
│   │       └── a2a_server.py  # A2A protocol server (ADK to_a2a)
│   └── advanced/              # Multi-agent hierarchical system (port 8081)
│       └── purple_advanced/
│           ├── agent.py       # GAIA coordinator (Gemini 2.5 Pro)
│           ├── a2a_server.py  # A2A protocol server (ADK to_a2a)
│           └── sub_agents/    # Specialized sub-agents
│               ├── web_search/        # Google Search integration
│               ├── calculator/        # Mathematical computations
│               └── deep_analyzer/     # Complex multi-step reasoning
│
├── scripts/                   # Utility scripts & demos
├── tests/                     # Automated test suite
└── docker/                    # Docker containerization
```

### Communication Flow

```
┌─────────────────────────────┐         A2A Protocol          ┌──────────────────────────────┐
│     Green Agent             │ ────────────────────────────► │      Purple Agent            │
│     (Evaluator)             │         (A2A SDK)             │      (Test Taker)            │
│                             │                               │                              │
│  • Loads GAIA questions     │                               │  • Receives question via A2A │
│  • Creates A2A Message      │                               │  • Processes with LLM/agents │
│  • Sends via ClientFactory  │ ◄──────────────────────────── │  • Returns answer via A2A    │
│  • Receives A2A response    │      (HTTP/JSON Transport)    │  • Exposed by to_a2a()       │
│  • Scores deterministically │                               │                              │
│  • Optional LLM evaluation  │                               │  Coordinator orchestrates:   │
│  • Saves results to JSON    │                               │    - Web search tool         │
│                             │                               │    - Calculator tool         │
│                             │                               │    - Deep analyzer tool      │
└─────────────────────────────┘                               └──────────────────────────────┘
         │                                                                   │
         │                                                                   │
         ▼                                                                   ▼
┌─────────────────────────────┐                               ┌──────────────────────────────┐
│  Green Coordinator (LLM)    │                               │   GAIA Coordinator (LLM)     │
│  for Intelligent Scoring    │                               │   for Task Execution         │
│                             │                               │                              │
│  Orchestrates sub-agents:   │                               │  Orchestrates sub-agents:    │
│    • Semantic Scorer        │                               │    • Web Search Agent        │
│    • Answer Analyzer        │                               │    • Deep Analyzer Agent     │
│    • Quality Assessor       │                               │    • Calculator Agent        │
└─────────────────────────────┘                               └──────────────────────────────┘
```

### Key Components

**Green Agent (Evaluator)**

- Uses `a2a.client.ClientFactory` to create A2A client
- Uses `InMemoryRunner` to execute green_coordinator (LLM agent)
- Sends questions via `client.send_message(Message(...))`
- Receives responses as A2A Message objects
- Scores answers deterministically + optionally with LLM
- Saves comprehensive results with metadata

**Purple Agent (Test Taker)**

- Uses `google.adk.a2a.utils.agent_to_a2a.to_a2a()` wrapper
- Automatically exposes agent via A2A protocol
- Generates agent card at `/.well-known/agent-card.json`
- Runs on uvicorn web server (FastAPI under the hood)
- Coordinator uses `InMemoryRunner` for sub-agent orchestration

## 🧠 Internal Agent Architecture

### Purple Agent - Advanced Multi-Agent System

The purple advanced agent implements a **hierarchical multi-agent architecture** inspired by DeepResearchAgent:

```
┌────────────────────────────────────────────────────────────┐
│                  GAIA Test Taker Coordinator               │
│                     (Gemini 2.5 Pro)                       │
│                                                            │
│  Analyzes question → Plans approach → Delegates to        │
│  specialized sub-agents → Synthesizes final answer        │
└────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
    │  Web Search   │  │ Deep Analyzer │  │  Calculator   │
    │ (2.5 Flash)   │  │  (2.0 Flash)  │  │(2.5 Flash Lite│
    │               │  │               │  │               │
    │ • Searches    │  │ • Multi-step  │  │ • Math ops    │
    │   Google      │  │   reasoning   │  │ • Equations   │
    │ • Extracts    │  │ • Complex     │  │ • Unit conv.  │
    │   facts       │  │   logic       │  │               │
    └───────────────┘  └───────────────┘  └───────────────┘
```

**Execution Flow:**

1. **Coordinator receives question** via A2A protocol
2. **Analyzes question type**: factual, mathematical, reasoning, or hybrid
3. **Plans decomposition**: breaks complex questions into sub-tasks
4. **Delegates to appropriate sub-agents**:
   - Web Search: For factual queries, current events, lookups
   - Deep Analyzer: For complex multi-step reasoning
   - Calculator: For mathematical computations
5. **Collects results** from sub-agent tool calls
6. **Synthesizes final answer** by combining findings
7. **Returns answer** via A2A protocol

**Sub-Agent Communication:**

- Uses `AgentTool` wrapper to expose sub-agents as tools
- Coordinator calls: `web_search_agent(query="...")`
- ADK Runner manages execution and state
- Results passed back to coordinator for synthesis

### Green Agent - Hybrid Evaluation System

The green agent implements a **two-tier evaluation strategy**:

```
┌────────────────────────────────────────────────────────────┐
│                 Main Evaluation Loop                       │
│                  (evaluator.py)                            │
│                                                            │
│  1. Load GAIA questions (shuffled for variety)            │
│  2. Send to Purple Agent via A2A                          │
│  3. Receive answer via A2A                                │
│  4. Run deterministic scoring (exact/normalized/numeric)  │
│  5. If score = 0.0 AND --use-llm-scoring:                │
│     ├─► Invoke Green Coordinator                         │
│     └─► Get LLM-powered evaluation                       │
│  6. Save results with metadata                            │
└────────────────────────────────────────────────────────────┘
                              │
                              │ (When LLM scoring needed)
                              ▼
┌────────────────────────────────────────────────────────────┐
│           Green Coordinator (Gemini 2.5 Flash)             │
│                                                            │
│  Orchestrates intelligent evaluation for borderline cases │
└────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
    │   Answer      │  │   Semantic    │  │   Quality     │
    │   Analyzer    │  │    Scorer     │  │   Assessor    │
    │ (2.5 Flash)   │  │  (2.5 Flash)  │  │ (2.5 Flash)   │
    │               │  │               │  │               │
    │ Assesses:     │  │ Checks:       │  │ Synthesizes:  │
    │ • Completeness│  │ • Semantic    │  │ • Overall     │
    │ • Relevance   │  │   equivalence │  │   quality     │
    │ • Clarity     │  │ • Paraphrases │  │ • Confidence  │
    │ • Accuracy    │  │ • Synonyms    │  │ • Final score │
    └───────────────┘  └───────────────┘  └───────────────┘
```

**Evaluation Flow:**

1. **Deterministic Scoring** (always runs first):
   - Exact string match
   - Normalized match (case-insensitive, punctuation-stripped)
   - Numerical tolerance (1% for numeric answers)

2. **LLM Evaluation** (only if score = 0.0 and enabled):
   - Coordinator invoked via `InMemoryRunner`
   - Answer Analyzer assesses predicted answer quality
   - Semantic Scorer compares with gold answer
   - Quality Assessor provides final judgment
   - Returns: `llm_score`, `confidence`, `reasoning`, `sub_agent_findings`

3. **Result Aggregation**:
   - Final score = LLM score (if available) else deterministic score
   - Saves both scores + confidence + reasoning to JSON
   - Provides full audit trail of evaluation logic

### Purple Agent - Baseline

The baseline agent uses a **single LLM** with no specialized tools:

```
┌────────────────────────────────────────────────────────────┐
│           Baseline Purple Agent (Single LLM)               │
│                 (Gemini 2.5 Flash)                         │
│                                                            │
│  • Receives question via A2A                              │
│  • Processes with single LLM call                         │
│  • Returns answer via A2A                                 │
│  • No tool use, no sub-agents                             │
└────────────────────────────────────────────────────────────┘
```

**Use Case**: Simple baseline for comparison, fast responses, minimal complexity.

## Agent Comparison

| Feature | Baseline | Advanced |
|---------|----------|----------|
| Architecture | Single LLM | Multi-agent hierarchy |
| Model | Gemini 2.5 Flash | Gemini 2.5 Pro + sub-agents |
| Tools | None | Web Search, Calculator, Deep Analyzer |
| Response Time | ~3-5s | ~10-15s |
| Level 1 Accuracy | ~60-70% | ~75-85% |
| Level 3 Accuracy | ~10-20% | ~25-35% |
| Port | 8080 | 8081 |
| Complexity | Low | High |
| Best For | Simple questions | Complex reasoning |

## 📊 GAIA Benchmark Implementation

The system evaluates agents on the **GAIA (General AI Assistants)** benchmark:

- **466 questions** across 3 difficulty levels
- **Text reasoning + tool use** tasks
- **Deterministic scoring**: Exact match, normalized match, numerical tolerance (1%)
- **Reproducible results**: Fixed random seed (42), question shuffling
- **Timeout**: 120 seconds per task (configurable via `TASK_TIMEOUT`)

### Question Types & Distribution

- **Level 1 (~100 questions)**: Easy factual questions, simple lookups
- **Level 2 (~100 questions)**: Medium reasoning tasks, multi-step problems
- **Level 3 (~100 questions)**: Hard problems requiring external tools & complex reasoning

### Scoring Methods

1. **Exact Match**: Direct string comparison (`predicted == gold`)
2. **Normalized Match**: Case-insensitive, punctuation-normalized
3. **Numerical Tolerance**: 1% tolerance for numeric answers
4. **LLM Scoring** (optional): Semantic equivalence for borderline cases

## ⚙️ Configuration

### Environment Variables

**Green Evaluator** (`.env` in `green-evaluator/`):

```bash
# Required: Gemini API key for LLM evaluation
GOOGLE_API_KEY=your_api_key_here

# Optional: Task timeout (default: 120 seconds)
# Increase for complex multi-agent scenarios
TASK_TIMEOUT=120

# Optional: Purple agent URL (default: http://localhost:8081)
PURPLE_AGENT_URL=http://localhost:8081
```

**Purple Agent - Advanced** (`.env` in `purple-agents/advanced/purple_advanced/`):

```bash
# Required: Gemini API key
GOOGLE_API_KEY=your_api_key_here

# Optional: Individual model configs for each sub-agent
# Main coordinator (default: gemini-2.5-pro)
PURPLE_ADVANCED_MODEL=gemini-2.5-pro

# Web Search sub-agent (default: gemini-2.5-flash)
WEB_SEARCH_MODEL=gemini-2.5-flash

# Deep Analyzer sub-agent (default: gemini-2.0-flash)
DEEP_ANALYZER_MODEL=gemini-2.0-flash

# Calculator sub-agent (default: gemini-2.5-flash-lite)
CALCULATOR_MODEL=gemini-2.5-flash-lite

# Server port (default: 8081)
PORT=8081
```

**Purple Agent - Baseline** (`.env` in `purple-agents/baseline/purple_baseline/`):

```bash
# Required: Gemini API key
GOOGLE_API_KEY=your_api_key_here

# Optional: Model selection (default: gemini-2.5-flash)
PURPLE_BASELINE_MODEL=gemini-2.5-flash

# Server port (default: 8080)
PORT=8080
```

### Model Configuration Strategy

**Green Agent Models:**

- **Main Coordinator**: `gemini-2.5-flash` - Fast LLM evaluation coordinator
- **All Sub-Agents**: `gemini-2.5-flash` - Consistent model for semantic scoring, answer analysis, quality assessment

**Purple Agent Models:**

- **Advanced Coordinator**: `gemini-2.5-pro` - Most capable model for complex task planning
- **Web Search**: `gemini-2.5-flash` - Fast for factual queries
- **Deep Analyzer**: `gemini-2.0-flash` - Balanced for multi-step reasoning
- **Calculator**: `gemini-2.5-flash-lite` - Lightweight for math operations
- **Baseline**: `gemini-2.5-flash` - Single-agent simplicity

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (tested on 3.11)
- Google API Key with Gemini access
- Docker (optional, for containerized deployment)

### Local Setup (macOS/Linux)

**1. Clone repository:**

```bash
git clone <repository-url>
cd green-gaia-agent
```

**2. Create virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

**3. Install dependencies:**

```bash
# Green evaluator
cd green-evaluator
pip install -r requirements.txt
cd ..

# Purple advanced agent
cd purple-agents/advanced
pip install -r requirements.txt
cd ../..
```

**4. Configure environment:**

```bash
# Copy example configs
cp green-evaluator/.env.example green-evaluator/.env
cp purple-agents/advanced/purple_advanced/.env.example purple-agents/advanced/purple_advanced/.env

# Edit .env files with your API key
# green-evaluator/.env
GOOGLE_API_KEY=your_actual_api_key_here
TASK_TIMEOUT=120

# purple-agents/advanced/purple_advanced/.env
GOOGLE_API_KEY=your_actual_api_key_here
```

**5. Start purple agent** (in separate terminal):

```bash
source venv/bin/activate
cd purple-agents/advanced
python -m purple_advanced.a2a_server
```

Expected output:

```
🟣 Purple Advanced Agent Starting...
   ├─ Model: gemini-2.5-pro
   ├─ Port: 8081
   └─ Tools: web_search, deep_analyzer, calculator
✅ A2A server ready at http://localhost:8081
```

**6. Run evaluation** (in main terminal):

```bash
source venv/bin/activate
cd green-evaluator

# Evaluate with LLM scoring (default)
python -m agent.evaluator \
    --dataset validation_level1 \
    --purple-url http://localhost:8081 \
    --timeout 120 \
    --output results/run_$(date +%Y%m%d_%H%M%S).json

# Evaluate with only deterministic scoring
python -m agent.evaluator \
    --dataset validation_level1 \
    --purple-url http://localhost:8081 \
    --no-llm-scoring
```

Expected output:

```
🟢 Green Agent Evaluation Starting...
   ├─ Dataset: validation_level1 (100 questions)
   ├─ Purple URL: http://localhost:8081
   ├─ Timeout: 120s per task
   └─ LLM Scoring: Enabled

📋 Question 1/100 [Level 1]
   └─ What is the capital of France?

🔗 Sending to purple agent...
   └─ Coordinator selected tool: web_search
   └─ 🔍 Web search agent executing...
   └─ ✅ Answer received: Paris

✅ Deterministic score: 1.0 (exact match)

📋 Question 2/100 [Level 1]
   └─ Calculate 15% of 240

🔗 Sending to purple agent...
   └─ Coordinator selected tool: calculator
   └─ 🔢 Calculator agent executing...
   └─ ✅ Answer received: 36

✅ Deterministic score: 1.0 (numeric match)

📋 Question 3/100 [Level 2]
   └─ [Complex reasoning question...]

🔗 Sending to purple agent...
   └─ Coordinator selected tool: deep_analyzer
   └─ 🤔 Deep analyzer working on multi-step problem...
   └─ ✅ Answer received: [detailed answer]

❌ Deterministic score: 0.0
🤔 Green coordinator evaluating with LLM...
   ├─ 🔍 Semantic scorer checking equivalence...
   ├─ 📊 Answer analyzer assessing quality...
   └─ ⚖️ Quality assessor providing judgment...
✅ LLM Score: 0.8 (confidence: 0.85)
   └─ Reasoning: Answer captures key concepts with slight wording differences

═══════════════════════════════════════════════════════════
📊 Final Results:
   ├─ Total: 100 questions
   ├─ Correct: 78 (78.0%)
   ├─ LLM-evaluated: 15 (15.0%)
   └─ Average confidence: 0.82

💾 Results saved to: results/run_20250101_120000.json
```

### Docker Deployment

**1. Build images:**

```bash
docker-compose build
```

**2. Run evaluation:**

```bash
docker-compose up
```

Results will be saved to `green-evaluator/results/`.

## 🎨 Logging System

The system features a **beautiful, clean logging architecture** with emoji indicators:

### Log Format

- **No timestamps** (reduces clutter for demos)
- **Emoji indicators** for agent identification
- **Colored output** for severity levels
- **Hierarchical indentation** for nested operations

### Logger Hierarchy

**Green Evaluator** (`agent/evaluator.py`):

- Uses custom `CleanFormatter` + `ADKFormatter`
- Suppresses noisy ADK internal logs ("Sending out request", "Runner closed")
- Transforms ADK messages to clean emoji format:
  - "Sending out request" → "🤔 Green coordinator evaluating..."
  - "Response received" → "✅ Evaluation complete"
- Suppresses `google.genai` warnings ("Warning: there are non-text parts")
- Suppresses `httpx`, `httpcore`, `a2a` debug logs

**Purple Agent** (`purple_advanced/a2a_server.py`):

- Uses custom `LLMFormatter` with emoji indicators
- Agent identification:
  - 🟣 Main coordinator
  - 🔍 Web search agent
  - 🤔 Deep analyzer agent
  - 🔢 Calculator agent
- Filters "App name mismatch" warnings (ADK internal behavior)
- Transforms logs for clean output

### Logger Configuration

```python
# Green evaluator setup (evaluator.py)
import logging
import warnings
from dotenv import load_dotenv

# Early load for environment access
load_dotenv()

# Suppress App name mismatch warnings (warnings module)
warnings.filterwarnings('ignore', message='App name in registry.*does not match.*')

# Custom formatter for ADK logs
class ADKFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        if "Sending out request" in msg:
            return "🤔 Green coordinator evaluating..."
        elif "Response received" in msg:
            return "✅ Evaluation complete"
        elif "Runner closed" in msg or "Closing runner" in msg:
            return None  # Filter out
        return msg

# Suppress noisy loggers
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('a2a').setLevel(logging.WARNING)
```

### Sub-Agent Identification

Models are used to identify which sub-agent is executing:

**Green Coordinator Sub-Agents** (all `gemini-2.5-flash`):

- Semantic Scorer
- Answer Analyzer
- Quality Assessor

**Purple Coordinator Sub-Agents**:

- Web Search (`gemini-2.5-flash`)
- Deep Analyzer (`gemini-2.0-flash`)
- Calculator (`gemini-2.5-flash-lite`)

The logging system detects model names and displays appropriate emoji indicators.

## 🔧 Technical Implementation Details

### ADK Runner Pattern (CRITICAL)

**Correct Pattern** (used in this project):

```python
from google.adk.llms import LlmAgent
from google.adk.sessions import InMemoryRunner

# Define agent
my_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    prompt="You are a helpful assistant."
)

# Create runner
runner = InMemoryRunner(agent=my_agent)

# Execute (async)
session = await runner.run_async(user_prompt="Hello!")

# Extract result
result = session.output  # or session["output_key"]
```

**INCORRECT Pattern** (avoid):

```python
# ❌ This does NOT work - LlmAgent has no .run() method
result = my_agent.run("Hello!")  # AttributeError!

# ❌ This also doesn't work
result = my_agent("Hello!")  # Not callable!
```

**Why InMemoryRunner?**

1. **LlmAgent has no .run() method** - Runner manages execution
2. **Session state management** - Runner tracks conversation history
3. **Sub-agent orchestration** - Required for tool calls
4. **Error handling** - Runner provides proper exception management
5. **Timeout support** - Runner respects timeout configuration

**Reference Implementation:**

This project follows the pattern from Google's `academic-research` agent example, which demonstrates correct ADK usage with multi-agent orchestration.

### Sub-Agent as Tool Pattern

```python
from google.adk.llms import LlmAgent
from google.adk.agent_tools import AgentTool

# Define sub-agent
calculator_agent = LlmAgent(
    name="calculator",
    model="gemini-2.5-flash-lite",
    prompt="You are a calculator. Perform mathematical operations."
)

# Wrap as tool
calculator_tool = AgentTool(calculator_agent)

# Define coordinator
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-pro",
    tools=[calculator_tool],
    prompt="You coordinate tasks and delegate to tools."
)

# Execute (coordinator can call calculator_tool)
runner = InMemoryRunner(agent=coordinator)
session = await runner.run_async(user_prompt="What is 15% of 240?")
# Coordinator decides to call calculator_tool → gets result → synthesizes answer
```

### A2A Server Pattern

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.llms import LlmAgent
import uvicorn

# Define agent
my_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    prompt="You are an A2A-compatible agent."
)

# Expose via A2A (auto-generates agent card, HTTP endpoints)
a2a_app = to_a2a(my_agent, port=8080)

# Run server
if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8080)
```

**What to_a2a() provides**:

- HTTP server at specified port
- Agent card at `/.well-known/agent-card.json`
- A2A message handling (auto-converts HTTP → A2A → Agent → A2A → HTTP)
- Error handling and logging
- FastAPI backend (uvicorn runtime)

### A2A Protocol Implementation

**Green Agent (Client)**:

```python
from a2a.client import ClientFactory
from a2a.types import Message

# Create A2A client
client = ClientFactory.create_client(
    base_url="http://localhost:8081",
    timeout=120
)

# Create A2A message
message = Message(
    role="user",
    content=question
)

# Send and receive
response_msg = await client.send_message(
    message=message,
    task_id=task_id
)

answer = response_msg.content
```

**Purple Agent (Server)**:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.llms import LlmAgent

# Define agent
gaia_test_taker = LlmAgent(
    name="gaia_test_taker",
    model="gemini-2.5-pro",
    tools=[web_search_agent, deep_analyzer_agent, calculator_agent]
)

# Expose via A2A
a2a_app = to_a2a(gaia_test_taker, port=8081)

# Run server
uvicorn.run(a2a_app, host="0.0.0.0", port=8081)
```

**A2A Message Format**:

```json
{
  "role": "user",
  "content": "What is the capital of France?",
  "metadata": {
    "task_id": "gaia_001",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Agent Card** (auto-generated at `/.well-known/agent-card.json`):

```json
{
  "name": "gaia_test_taker",
  "description": "GAIA benchmark test taker",
  "capabilities": ["reasoning", "tool_use", "web_search"],
  "version": "1.0.0"
}
```

### Sub-Agent Orchestration

**Purple Coordinator Decision Flow**:

1. Receives question via A2A
2. Analyzes question type (factual, math, reasoning)
3. Plans decomposition if multi-step
4. Calls appropriate sub-agent(s) via `AgentTool`
5. Synthesizes final answer from tool results
6. Returns via A2A

**Example Tool Call**:

```python
from google.adk.agent_tools import AgentTool

# Wrap sub-agent as tool
web_search_tool = AgentTool(web_search_agent)

# Coordinator can call it
result = web_search_tool(query="capital of France")
# Returns: "Paris is the capital of France..."
```

### Deterministic Scoring Logic

```python
def deterministic_score(predicted: str, gold: str) -> float:
    """Deterministic scoring with multiple strategies."""
    
    # Exact match
    if predicted.strip() == gold.strip():
        return 1.0
    
    # Normalized match (case-insensitive, punctuation-stripped)
    pred_norm = normalize(predicted)
    gold_norm = normalize(gold)
    if pred_norm == gold_norm:
        return 1.0
    
    # Numerical tolerance (1%)
    if is_numeric(predicted) and is_numeric(gold):
        pred_num = extract_number(predicted)
        gold_num = extract_number(gold)
        if abs(pred_num - gold_num) / abs(gold_num) <= 0.01:
            return 1.0
    
    return 0.0
```

### LLM Evaluation Logic

Only triggered when deterministic score = 0.0:

```python
async def _llm_evaluate(self, question: str, predicted: str, gold: str):
    """LLM-powered evaluation for borderline cases."""
    
    prompt = f"""
    Question: {question}
    Predicted Answer: {predicted}
    Gold Answer: {gold}
    
    Evaluate if the predicted answer is semantically equivalent to the gold answer.
    Consider: synonyms, paraphrases, different phrasings of the same concept.
    """
    
    # Use InMemoryRunner
    runner = InMemoryRunner(agent=green_coordinator)
    session = await runner.run_async(user_prompt=prompt)
    
    result = session["final_evaluation"]
    return {
        "llm_score": result["score"],
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
        "sub_agent_findings": {
            "semantic_scorer": result["semantic_equivalence"],
            "answer_analyzer": result["quality_assessment"],
            "quality_assessor": result["final_judgment"]
        }
    }
```

## 🔄 Evaluation Workflow

### Step-by-Step Execution

**1. Initialization:**

- Load environment variables (`load_dotenv()`)
- Initialize A2A client (`ClientFactory`)
- Load GAIA dataset
- Shuffle questions (seed=42 for reproducibility)

**2. For each question:**

```
┌─ Send question to purple agent (A2A)
│  └─ Wait for response (timeout: 120s)
│
├─ Receive answer (A2A)
│
├─ Deterministic scoring
│  ├─ Exact match check
│  ├─ Normalized match check
│  └─ Numerical tolerance check
│
├─ IF deterministic_score == 0.0 AND llm_scoring_enabled:
│  ├─ Create evaluation prompt
│  ├─ Send to green coordinator (InMemoryRunner)
│  │  ├─ Semantic scorer checks equivalence
│  │  ├─ Answer analyzer assesses quality
│  │  └─ Quality assessor provides judgment
│  └─ Receive LLM score + reasoning
│
└─ Save result with metadata
```

**3. Aggregation:**

- Calculate overall accuracy
- Count LLM-evaluated questions
- Average confidence scores
- Generate summary statistics

**4. Output:**

- Save detailed JSON to `results/`
- Print summary to console
- Include per-question metadata

### Result Format

```json
{
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "dataset": "validation_level1",
    "total_questions": 100,
    "purple_agent_url": "http://localhost:8081",
    "timeout": 120,
    "llm_scoring_enabled": true
  },
  "results": [
    {
      "question_id": "gaia_001",
      "question": "What is the capital of France?",
      "gold_answer": "Paris",
      "predicted_answer": "Paris",
      "deterministic_score": 1.0,
      "llm_score": null,
      "confidence": null,
      "reasoning": null,
      "time_taken": 2.3
    },
    {
      "question_id": "gaia_042",
      "question": "[Complex reasoning question]",
      "gold_answer": "Expected answer",
      "predicted_answer": "Similar but different wording",
      "deterministic_score": 0.0,
      "llm_score": 0.85,
      "confidence": 0.90,
      "reasoning": "Answer captures key concepts with slight wording differences",
      "time_taken": 15.7,
      "sub_agent_findings": {
        "semantic_scorer": {"equivalence": 0.9, "explanation": "..."},
        "answer_analyzer": {"quality": 0.8, "explanation": "..."},
        "quality_assessor": {"judgment": 0.85, "explanation": "..."}
      }
    }
  ],
  "summary": {
    "total": 100,
    "correct": 78,
    "accuracy": 0.78,
    "llm_evaluated": 15,
    "average_confidence": 0.82,
    "average_time_per_question": 8.5
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**1. "'LlmAgent' object has no attribute 'run'"**

- **Cause**: Trying to call `.run()` directly on LlmAgent
- **Solution**: Use `InMemoryRunner` pattern (see Technical Implementation)

**2. "GOOGLE_API_KEY not found"**

- **Cause**: `.env` file not loaded or missing
- **Solution**:
  - Ensure `.env` exists in correct directory
  - Check `load_dotenv()` called at top of `evaluator.py`
  - Verify API key is valid

**3. "Connection refused to purple agent"**

- **Cause**: Purple agent not running or wrong port
- **Solution**:
  - Start purple agent: `python -m purple_advanced.a2a_server`
  - Check port matches (default: 8081)
  - Verify firewall not blocking

**4. "Timeout after 60 seconds"**

- **Cause**: Default timeout too short for complex questions
- **Solution**:
  - Set `TASK_TIMEOUT=120` in `.env`
  - Or use `--timeout 120` CLI flag

**5. Too many noisy logs**

- **Cause**: ADK internal logging
- **Solution**: Already suppressed in code via:

```python
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
```

**6. "App name in registry does not match"**

- **Cause**: ADK internal behavior (harmless)
- **Solution**: Already suppressed via:

```python
warnings.filterwarnings('ignore', message='App name in registry.*')
```

### Debugging Tips

**Enable verbose logging**:

```python
# In evaluator.py, change:
logging.basicConfig(level=logging.DEBUG)
```

**Test A2A connection**:

```bash
cd green-evaluator
python tests/test_a2a_connection.py
```

**Test purple agent standalone**:

```bash
cd purple-agents/advanced
python -m purple_advanced.test_agent
```

**Check agent card**:

```bash
curl http://localhost:8081/.well-known/agent-card.json
```

## 📈 Performance Metrics

### Expected Results

**Baseline Purple Agent** (single LLM, port 8080):

- Level 1: ~60-70% accuracy
- Level 2: ~30-40% accuracy
- Level 3: ~10-20% accuracy
- Average time: ~5s per question

**Advanced Purple Agent** (multi-agent, port 8081):

- Level 1: ~75-85% accuracy (web search helps)
- Level 2: ~50-60% accuracy (deep analyzer helps)
- Level 3: ~25-35% accuracy (combined tools help)
- Average time: ~10-15s per question (more deliberation)

### Benchmark Hardware

- MacBook Pro M2 (2023)
- 16GB RAM
- Gemini API (cloud-hosted)

## 🛠️ Development

### Running Tests

```bash
# Activate venv
source venv/bin/activate

# Run all tests
cd green-evaluator
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_end_to_end.py -v

# Test scoring logic
python tests/test_scoring.py

# Test GAIA loader
python tests/test_loader.py
```

### Adding New Purple Agents

**1. Create agent directory:**

```bash
mkdir -p purple-agents/my-agent/my_agent
```

**2. Implement agent with A2A server:**

```python
# my_agent/agent.py
from google.adk.llms import LlmAgent

my_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    prompt="Your custom prompt..."
)

# my_agent/a2a_server.py
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import uvicorn

a2a_app = to_a2a(my_agent, port=8082)
uvicorn.run(a2a_app, host="0.0.0.0", port=8082)
```

**3. Test with green evaluator:**

```bash
python -m agent.evaluator \
    --purple-url http://localhost:8082 \
    --dataset validation_level1
```

### Extending GAIA Datasets

Add new datasets to `green-evaluator/data/gaia/`:

```json
{
  "questions": [
    {
      "question_id": "custom_001",
      "task": "Your question here",
      "question": "Your question here",
      "level": 1,
      "final_answer": "Expected answer"
    }
  ]
}
```

Use with:

```bash
python -m agent.evaluator --dataset custom_questions
```

## 📚 References

- **GAIA Benchmark**: [https://huggingface.co/gaia-benchmark](https://huggingface.co/gaia-benchmark)
- **Google ADK**: [https://google.github.io/adk-docs/](https://google.github.io/adk-docs/)
- **A2A Protocol**: [https://a2a.to/](https://a2a.to/)
- **AgentX Competition**: [https://www.kaggle.com/competitions/agentx-agentbeats](https://www.kaggle.com/competitions/agentx-agentbeats)

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainers.
