# Green GAIA Agent - Evaluator for A2A-Compatible Purple Agents

## Abstract

The Green GAIA Agent is a production-quality evaluator designed for the AgentX–AgentBeats Competition using the GAIA (General AI Assistants) benchmark. This green agent evaluates A2A (Agent-to-Agent) compatible purple agents end-to-end by:

- Loading GAIA benchmark questions (text reasoning + tool use tasks)
- Sending tasks to external purple agents via A2A protocol
- Receiving and scoring answers deterministically
- Producing reproducible aggregate metrics
- Running fully automated in Docker

The system is built using the **Google Agent Developer Kit (ADK)** and follows clean architecture principles with modular, extensible code.

## Key Features

✅ **GAIA Benchmark Integration** - Loads and normalizes GAIA questions  
✅ **A2A Protocol** - HTTP-based agent-to-agent communication  
✅ **Deterministic Scoring** - Exact match, normalized string, and numerical tolerance  
✅ **Reproducibility** - Fixed random seeds, no external API calls (except A2A)  
✅ **Google ADK** - State-of-the-art agent orchestration  
✅ **Docker Support** - Fully containerized with docker-compose  
✅ **Two Purple Agent Implementations** - Baseline and Advanced with sub-agents  
✅ **Comprehensive Testing** - Unit and integration tests  

## Architecture

```
green-gaia-agent/
├── agent/                      # Core green agent implementation
│   ├── __init__.py
│   ├── evaluator.py           # Main evaluator orchestration
│   ├── gaia_loader.py         # GAIA benchmark data loader
│   ├── a2a_protocol.py        # A2A HTTP protocol client
│   ├── scoring.py             # Deterministic scoring logic
│   └── schemas.py             # Pydantic data models
├── purple_baseline/            # Baseline purple agent (single LLM)
│   ├── __init__.py
│   ├── agent.py               # LLM-based agent
│   ├── prompt.py              # System prompts
│   └── a2a_mock_server.py     # A2A HTTP server
├── purple_advanced/            # Advanced purple agent (multi-agent)
│   ├── __init__.py
│   ├── agent.py               # GAIA coordinator
│   ├── prompt.py              # Coordinator prompts
│   ├── a2a_server.py          # A2A HTTP server
│   └── sub_agents/            # Specialized sub-agents
│       ├── web_search/        # Google Search integration
│       ├── deep_analyzer/     # Complex reasoning
│       └── calculator/        # Math computations
├── data/
│   └── gaia/
│       ├── sample_questions.json       # Sample questions
│       ├── validation_complete.json    # Full validation set (466 questions)
│       ├── validation_level1.json      # Easy questions
│       ├── validation_level2.json      # Medium questions
│       └── validation_level3.json      # Hard questions
├── tests/                      # Test suite
│   ├── test_scoring.py
│   ├── test_loader.py
│   └── test_end_to_end.py
├── docker/                     # Docker configuration
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── docker-compose.yml
├── results/                    # Evaluation outputs
├── pyproject.toml             # Python project config
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.10-3.12
- Docker (optional, for containerized execution)
- Google Cloud credentials (for ADK)

### Local Setup

1. **Clone the repository:**
```bash
cd green-gaia-agent
```

2. **Install dependencies:**
```bash
pip install -e .
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up Google Cloud credentials:**
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

## Purple Agent Implementations

This project includes **two purple agent implementations**:

### 1. Baseline Purple Agent (`purple_baseline/`)

A simple LLM-based agent for testing and baseline measurement:
- Single Gemini 2.5 Pro model
- Direct prompting without tools
- Fast responses (~2-5 seconds)
- Expected accuracy: 2-5% on GAIA
- **Use for**: Infrastructure testing, baseline comparison

```bash
# Start baseline agent
python -m purple_baseline.a2a_mock_server
# Runs on port 8080
```

### 2. Advanced Purple Agent (`purple_advanced/`)

A hierarchical multi-agent system following the DeepResearchAgent pattern:
- GAIA Coordinator orchestrates specialized sub-agents
- **Web Search Agent**: Google Search for current information
- **Deep Analyzer Agent**: Complex multi-step reasoning
- **Calculator Agent**: Mathematical computations with code interpreter
- Expected accuracy: 50-60% on GAIA
- **Use for**: Production evaluation, competitive performance

```bash
# Start advanced agent
python -m purple_advanced.a2a_server
# Runs on port 8081
```

For detailed comparison, see [PURPLE_AGENTS_COMPARISON.md](./PURPLE_AGENTS_COMPARISON.md)

## Usage

### Quick Start with Docker Compose

The easiest way to run the full evaluation:

```bash
cd docker
docker-compose up
```

This will:
1. Start the purple agent mock server
2. Wait for it to be healthy
3. Run the green evaluator
4. Save results to `results/summary.json`

### Manual Execution

#### Step 1: Start a Purple Agent

**Option A: Baseline Agent**
```bash
python -m purple_baseline.a2a_mock_server --host 0.0.0.0 --port 8080
```

**Option B: Advanced Agent**
```bash
python -m purple_advanced.a2a_server
```

#### Step 2: Run the Evaluator

```bash
# Evaluate baseline agent
python -m agent.evaluator \
  --data-dir data/gaia \
  --purple-agent-url http://localhost:8080 \
  --results-dir results

# Evaluate advanced agent
python -m agent.evaluator \
  --data-dir data/gaia \
  --purple-agent-url http://localhost:8081 \
  --results-dir results/advanced
```

### Command-Line Options

```bash
python -m agent.evaluator --help

Options:
  --data-dir TEXT              Directory containing GAIA questions [default: data/gaia]
  --purple-agent-url TEXT      Base URL of purple agent [default: http://localhost:8080]
  --results-dir TEXT           Directory to save results [default: results]
  --filename TEXT              Questions file to load [default: sample_questions.json]
  --max-questions INTEGER      Maximum questions to evaluate [default: None (all)]
  --numerical-tolerance FLOAT  Tolerance for numerical comparisons [default: 0.01]
  --task-timeout INTEGER       Timeout for each task in seconds [default: 60]
```

### Docker Build

Build the Docker image manually:

```bash
docker build -f docker/Dockerfile -t green-gaia-agent:latest .
```

Run with environment variables:

```bash
docker run \
  -v $(pwd)/results:/app/results \
  -e PURPLE_AGENT_URL=http://localhost:8080 \
  -e MAX_QUESTIONS=10 \
  green-gaia-agent:latest
```

## A2A Protocol

### Protocol Specification

The A2A protocol uses HTTP for agent communication:

#### POST /a2a/task
Send a task to the purple agent.

**Request:**
```json
{
  "task_id": "gaia_001",
  "question": "What is 2 + 2?",
  "metadata": {
    "difficulty": "easy",
    "topic": "arithmetic"
  }
}
```

**Response:**
```json
{
  "status": "received",
  "task_id": "gaia_001"
}
```

#### GET /a2a/response/{task_id}
Retrieve the answer for a task.

**Response (when ready):**
```json
{
  "task_id": "gaia_001",
  "answer": "4",
  "metadata": {
    "processed": true
  }
}
```

**Response (not ready):**
```json
{
  "error": "Response not ready"
}
```
HTTP Status: 404

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "baseline_purple_agent"
}
```

### Connecting Your Purple Agent

To connect your own purple agent:

1. Implement the A2A protocol endpoints (`/a2a/task`, `/a2a/response/{task_id}`, `/health`)
2. Start your agent on a port (e.g., 8080)
3. Run the evaluator pointing to your agent:
   ```bash
   python -m agent.evaluator --purple-agent-url http://localhost:8080
   ```

## Scoring

The evaluator uses **deterministic scoring** with three methods:

### 1. Exact Match
Direct string comparison (case-sensitive):
```python
predicted == gold  # Score: 1.0 if true, else 0.0
```

### 2. Normalized String Match
Case-insensitive, punctuation-removed, whitespace-normalized:
```python
normalize("Hello, World!") == normalize("hello world")  # Score: 1.0
```

### 3. Numerical Tolerance
For numerical answers with configurable tolerance (default: 1%):
```python
abs(predicted - gold) / abs(gold) <= 0.01  # Score: 1.0 if true
```

### Score Calculation

- **Score**: 1.0 if any method matches, else 0.0
- **Exact Match**: Boolean flag for exact string match
- **Normalized Match**: Boolean flag for normalized match

## Evaluation Results

Results are saved to `results/summary.json`:

```json
{
  "total_questions": 15,
  "total_score": 12.0,
  "average_score": 0.8,
  "exact_match_count": 8,
  "exact_match_rate": 0.5333,
  "normalized_match_count": 12,
  "normalized_match_rate": 0.8,
  "results": [
    {
      "task_id": "gaia_001",
      "question": "What is 15 + 27?",
      "gold_answer": "42",
      "predicted_answer": "42",
      "score": 1.0,
      "exact_match": true,
      "normalized_match": true,
      "metadata": {}
    }
  ],
  "metadata": {
    "filename": "sample_questions.json",
    "timestamp": "2025-11-27T12:00:00",
    "random_seed": 42,
    "numerical_tolerance": 0.01
  }
}
```

## Reproducibility Guarantees

The Green GAIA Agent ensures **100% reproducibility**:

✅ **Fixed Random Seed**: `RANDOM_SEED=42` is set globally  
✅ **Deterministic Scoring**: No randomness in evaluation  
✅ **Stateless Execution**: No persistent state between runs  
✅ **No External APIs**: Except for A2A protocol to purple agent  
✅ **Containerized**: Docker ensures consistent environment  

Running the same evaluation twice produces **identical results**.

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Scoring tests
pytest tests/test_scoring.py -v

# Loader tests
pytest tests/test_loader.py -v

# End-to-end tests
pytest tests/test_end_to_end.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=agent --cov=purple_baseline --cov-report=html
```

## Baseline Purple Agent

The included baseline agent uses **Google Gemini LLM** (gemini-2.0-flash-exp) to answer questions intelligently:

- **LLM-Powered**: Uses Google's Gemini model for reasoning
- **Fallback Mode**: Simple heuristics if API key is not provided
- **A2A Compatible**: Implements the full A2A protocol
- **Configurable**: Supports different Gemini models

### Setup

1. **Get a Google API Key**:
   - Visit https://aistudio.google.com/apikey
   - Create a new API key

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your-key-here
```

3. **Start the purple agent server**:
```bash
python -m purple_baseline.a2a_mock_server --port 8080
```

### Test Baseline Agent

Test directly without server:
```bash
python -m purple_baseline.baseline_agent
```

### Fallback Mode

If no API key is provided, the agent falls back to simple heuristics:
- **Yes/No questions**: Pattern matching
- **Counting questions**: Default guesses
- **Knowledge questions**: Default responses

**Note**: For best results with GAIA benchmark, use the LLM mode with a valid API key.

## Development

### Project Structure

- **agent/**: Core green agent logic
- **purple_baseline/**: Reference purple agent implementation
- **tests/**: Comprehensive test suite
- **docker/**: Container configuration

### Code Quality

Format code with Ruff:
```bash
ruff format .
ruff check . --fix
```

Type checking with mypy:
```bash
mypy agent/ purple_baseline/
```

## Extensibility

### Adding New Benchmarks

1. Implement a new loader in `agent/`
2. Follow the `GAIALoader` pattern
3. Return `GAIAQuestion` objects

### Custom Scoring

1. Extend `GAIAScorer` class
2. Add new scoring methods
3. Update `score()` method logic

### Alternative A2A Protocols

1. Implement new protocol in `agent/`
2. Follow the `A2AProtocol` interface
3. Update evaluator to use new protocol

## License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Support

For issues, questions, or contributions, please open an issue in the repository.

## Acknowledgments

- **Google Agent Developer Kit (ADK)** - Agent orchestration framework
- **GAIA Benchmark** - General AI Assistants evaluation suite
- **AgentBeats Competition** - Inspiration and requirements

---

**Built with ❤️ for the AgentX–AgentBeats Competition**
