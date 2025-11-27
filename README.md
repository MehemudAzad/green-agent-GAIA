# Green GAIA Agent - A2A Evaluator

A production-quality evaluator for the AgentX–AgentBeats Competition that evaluates A2A-compatible purple agents on the GAIA benchmark using Google ADK.

## Architecture

```
green-gaia-agent/
├── green-evaluator/           # Green Agent (A2A Client)
│   ├── agent/                 # Core evaluation logic
│   │   ├── evaluator.py       # Main orchestrator
│   │   ├── gaia_loader.py     # GAIA data loader
│   │   ├── a2a_protocol.py    # A2A HTTP client
│   │   ├── scoring.py         # Deterministic scoring
│   │   └── schemas.py         # Data models
│   ├── data/gaia/             # GAIA benchmark data
│   └── results/               # Evaluation outputs
├── purple-agents/             # Purple Agents (A2A Servers)
│   ├── baseline/              # Simple LLM agent (port 8080)
│   │   └── purple_baseline/
│   │       ├── agent.py       # Gemini 2.0 Flash agent
│   │       └── a2a_server.py # A2A HTTP server
│   └── advanced/              # Multi-agent system (port 8081)
│       └── purple_advanced/
│           ├── agent.py       # GAIA coordinator
│           ├── a2a_server.py # A2A HTTP server
│           └── sub_agents/    # Specialized agents
│               ├── web_search/# Google Search
│               ├── calculator/# Math computations
│               └── deep_analyzer/# Complex reasoning
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
└── docker/                    # Containerization
```

## Agent Flow

```
┌─────────────────┐    A2A Protocol    ┌─────────────────┐
│  Green Agent    │ ──────────────────►│  Purple Agent   │
│  (Evaluator)    │                    │  (LLM/Agents)   │
│                 │ ◄───────────────── │                 │
│ • Loads GAIA    │    HTTP/JSON       │ • Receives      │
│   questions     │                    │   questions     │
│ • Sends via A2A │                    │ • Processes      │
│ • Scores answers│                    │ • Returns        │
│ • Saves results │                    │   answers        │
└─────────────────┘                    └─────────────────┘
```

## GAIA Benchmark Implementation

The system evaluates agents on the **GAIA (General AI Assistants)** benchmark:

- **466 questions** across 3 difficulty levels
- **Text reasoning + tool use** tasks
- **Deterministic scoring**: Exact match, normalized match, numerical tolerance
- **Reproducible results**: Fixed seeds, no randomness

### Question Types
- **Level 1**: Easy factual questions
- **Level 2**: Medium reasoning tasks
- **Level 3**: Hard multi-step problems requiring tools

### Scoring Methods
1. **Exact Match**: Direct string comparison
2. **Normalized Match**: Case-insensitive, punctuation-normalized
3. **Numerical Tolerance**: 1% tolerance for numeric answers

## Quick Start

### Prerequisites
- Python 3.10+
- Google API Key (for Gemini models)

### Step 1: Setup Virtual Environments

```bash
# Setup Green Evaluator
cd green-evaluator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Setup Baseline Purple Agent
cd ../purple-agents/baseline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Setup Advanced Purple Agent (optional)
cd ../advanced
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Step 2: Configure API Keys

Create `.env` files in each agent directory:

```bash
# In purple-agents/baseline/.env
GOOGLE_API_KEY=your_api_key_here
PURPLE_BASELINE_PORT=8080

# In purple-agents/advanced/.env
GOOGLE_API_KEY=your_api_key_here
PURPLE_ADVANCED_PORT=8081
```

### Step 3: Run Agents

**Terminal 1: Start Purple Agent**

```bash
# Option A: Baseline (simple, fast)
cd purple-agents/baseline
source venv/bin/activate
python -m purple_baseline.a2a_server

# Option B: Advanced (multi-agent, accurate)
cd purple-agents/advanced
source venv/bin/activate
python -m purple_advanced.a2a_server
```

**Terminal 2: Run Green Evaluator**

```bash
cd green-evaluator
source venv/bin/activate
python -m agent.evaluator \
  --purple-agent-url http://localhost:8080 \
  --max-questions 1
```

### Step 4: View Results

```bash
cat results/summary.json | jq '.'
```

## Available Commands

### Evaluator Options

```bash
cd green-evaluator
python -m agent.evaluator --help

# Quick test (1 question)
python -m agent.evaluator --purple-agent-url http://localhost:8080 --max-questions 1

# Full evaluation (all 466 questions)
python -m agent.evaluator --purple-agent-url http://localhost:8080 --filename validation_complete.json

# Specific difficulty level
python -m agent.evaluator --purple-agent-url http://localhost:8080 --filename validation_level2.json --max-questions 50
```

### Purple Agent Options

```bash
# Baseline agent
cd purple-agents/baseline
python -m purple_baseline.a2a_server --port 8080

# Advanced agent
cd purple-agents/advanced
python -m purple_advanced.a2a_server --port 8081
```

## GAIA Datasets

| File | Questions | Difficulty | Use Case |
|------|-----------|------------|----------|
| `sample_questions.json` | 5 | Mixed | Quick testing |
| `validation_level1.json` | ~100 | Easy | Baseline validation |
| `validation_level2.json` | ~100 | Medium | Standard evaluation |
| `validation_level3.json` | ~100 | Hard | Challenge testing |
| `validation_complete.json` | 466 | All | Full benchmark |

## Agent Comparison

| Feature | Baseline Agent | Advanced Agent |
|---------|----------------|----------------|
| **Architecture** | Single LLM | Multi-agent coordinator |
| **Model** | Gemini 2.0 Flash | Gemini 2.5 Pro |
| **Tools** | None | Web Search, Calculator, Deep Analyzer |
| **Speed** | ~2-5s per question | ~10-30s per question |
| **Accuracy** | ~5-20% | ~50-60% |
| **Port** | 8080 | 8081 |
| **Use Case** | Testing/Baseline | Production evaluation |

## A2A Protocol

HTTP-based agent-to-agent communication:

### Send Task
```http
POST /a2a/task
{
  "task_id": "gaia_001",
  "question": "What is 2 + 2?"
}
```

### Get Response
```http
GET /a2a/response/gaia_001
{
  "answer": "4"
}
```

## Docker Support

```bash
# Build and run
cd docker
docker-compose up

# Or build manually
docker build -f docker/Dockerfile -t green-gaia-agent:latest
docker run -e PURPLE_AGENT_URL=http://localhost:8080 green-gaia-agent:latest
```

## Results Format

```json
{
  "total_questions": 1,
  "average_score": 0.0,
  "exact_match_rate": 0.0,
  "normalized_match_rate": 0.0,
  "results": [
    {
      "task_id": "gaia_001",
      "question": "What is the capital of France?",
      "gold_answer": "Paris",
      "predicted_answer": "Paris",
      "score": 1.0
    }
  ]
}
```

## Development

### Testing
```bash
pytest tests/ -v
```

### Code Quality
```bash
ruff format .
ruff check . --fix
mypy agent/ purple_baseline/ purple_advanced/
```

## License

Apache License 2.0

