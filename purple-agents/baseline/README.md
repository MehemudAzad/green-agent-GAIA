# Purple Baseline Agent

A simple baseline purple agent for the GAIA benchmark evaluation using Google ADK.

## Features

- Simple LLM-based agent using `gemini-2.0-flash-exp`
- ADK A2A protocol compliant
- Auto-generates agent card at `/.well-known/agent-card.json`

## Installation

```bash
cd purple-agents/baseline
pip install -e .
```

Or using requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage

### Start A2A Server

```bash
cd purple-agents/baseline
uvicorn purple_baseline.a2a_server:a2a_app --port 8080
```

The agent will be available at:
- A2A endpoint: `http://localhost:8080`
- Agent card: `http://localhost:8080/.well-known/agent-card.json`

### Test Agent Directly

```bash
cd purple-agents/baseline
python -m purple_baseline.agent
```

## Configuration

Set your Google API key:

```bash
export GOOGLE_API_KEY="your-api-key"
```

Or create a `.env` file:

```
GOOGLE_API_KEY=your-api-key
```

## Architecture

- **agent.py**: Core agent using ADK `Agent` with simple LLM instructions
- **a2a_server.py**: A2A protocol server using ADK `to_a2a()` wrapper
- **prompt.py**: Agent instruction templates (legacy, now inline in agent.py)
