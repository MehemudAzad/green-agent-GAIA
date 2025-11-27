# Purple Advanced Agent

A hierarchical multi-agent system for answering GAIA benchmark questions, built with Google ADK.

## Architecture

This agent follows the **DeepResearchAgent** pattern with a coordinator that orchestrates specialized sub-agents:

```
┌─────────────────────────────────────────┐
│      GAIA Coordinator (LLM Agent)       │
│  - Analyzes questions                   │
│  - Decomposes tasks                     │
│  - Delegates to sub-agents              │
│  - Synthesizes final answers            │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │   Web   │ │  Deep   │ │  Calc   │
  │ Search  │ │Analyzer │ │  Agent  │
  └─────────┘ └─────────┘ └─────────┘
```

### Sub-Agents

1. **Web Search Agent**: Finds information online using Google Search
   - Current events and factual data
   - Verifiable information from reliable sources
   - Direct answers to specific queries

2. **Deep Analyzer Agent**: Performs complex reasoning
   - Multi-step problem decomposition
   - Logical deduction and inference
   - Information synthesis

3. **Calculator Agent**: Handles mathematical computations
   - Arithmetic operations
   - Unit conversions
   - Statistical calculations
   - Uses code interpreter for complex math

## Setup

### Prerequisites

- Python 3.11+
- Google API key (for Gemini models)

### Installation

```bash
# Install dependencies
pip install -e .

# Or install from requirements
pip install google-adk google-genai flask python-dotenv
```

### Configuration

Create a `.env` file in the project root:

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional
PURPLE_ADVANCED_PORT=8081
GOOGLE_CLOUD_PROJECT=your_project_id
```

## Usage

### Running the A2A Server

Start the server to accept tasks via the A2A protocol:

```bash
python -m purple_advanced.a2a_server
```

The server will start on port 8081 (configurable via `PURPLE_ADVANCED_PORT`).

### Testing with Green Agent

Once running, the green agent can evaluate this purple agent:

```bash
# In another terminal, start the green evaluator
python -m agent.evaluator --agent-url http://localhost:8081
```

### Direct Usage (Python)

You can also use the agent directly in Python:

```python
from purple_advanced import gaia_coordinator

# Ask a question
result = gaia_coordinator.run("What is the capital of France?")
print(result["final_answer"])  # "Paris"

# Complex question requiring web search
result = gaia_coordinator.run(
    "Who won the Nobel Prize in Physics in 2023?"
)
print(result["final_answer"])

# Mathematical question
result = gaia_coordinator.run(
    "What is 15% of 240?"
)
print(result["final_answer"])  # "36"
```

## Architecture Details

### GAIA Coordinator

The coordinator is an `LlmAgent` that:
- Receives questions from the evaluator
- Analyzes the question type and requirements
- Selects appropriate sub-agents using `AgentTool`
- Synthesizes results into concise answers

### Sub-Agent Selection

The coordinator intelligently chooses sub-agents based on question characteristics:

- **Web search needed**: Questions about current events, specific facts, recent data
- **Complex reasoning needed**: Multi-step problems, logical deduction, synthesis
- **Calculation needed**: Mathematical operations, unit conversions, numerical analysis

### Answer Format

All answers are optimized for GAIA scoring:
- Concise and direct
- No explanations or reasoning steps in final output
- Format matches expected answer type (yes/no, number, name, etc.)

## Comparison with Baseline

| Feature | Baseline Purple Agent | Advanced Purple Agent |
|---------|----------------------|----------------------|
| Architecture | Single LLM | Hierarchical multi-agent |
| Web Search | ❌ No | ✅ Yes |
| Complex Reasoning | Limited | ✅ Enhanced |
| Mathematical Tools | ❌ No | ✅ Code interpreter |
| Expected Accuracy | ~5-10% | ~50-70% |

## Development

### Project Structure

```
purple_advanced/
├── __init__.py           # Package initialization
├── agent.py              # Main coordinator agent
├── prompt.py             # Coordinator prompts
├── a2a_server.py         # A2A protocol server
├── pyproject.toml        # Package configuration
├── README.md             # This file
└── sub_agents/
    ├── web_search/
    │   ├── __init__.py
    │   ├── agent.py      # Web search implementation
    │   └── prompt.py
    ├── deep_analyzer/
    │   ├── __init__.py
    │   ├── agent.py      # Deep analysis implementation
    │   └── prompt.py
    └── calculator/
        ├── __init__.py
        ├── agent.py      # Calculator implementation
        └── prompt.py
```

### Adding New Sub-Agents

To add a new sub-agent:

1. Create a new directory in `sub_agents/`
2. Implement `agent.py` with your agent logic
3. Create `prompt.py` with specialized instructions
4. Import and add to coordinator's tools in `agent.py`

Example:

```python
# In agent.py
from .sub_agents.new_agent import new_agent

gaia_coordinator = LlmAgent(
    # ... existing config ...
    tools=[
        # ... existing tools ...
        AgentTool(agent=new_agent),
    ],
)
```

## Performance

Expected performance on GAIA validation set:

- **Level 1 (Easy)**: 70-80% accuracy
- **Level 2 (Medium)**: 50-60% accuracy
- **Level 3 (Hard)**: 30-40% accuracy
- **Overall**: 50-60% accuracy

These estimates assume:
- Working web search integration
- Code interpreter available
- Proper Google API credentials

## Limitations

Current limitations:
- No file attachment handling (24 questions in GAIA require this)
- No browser automation (DeepResearchAgent uses this for complex web tasks)
- No multi-modal capabilities (images, PDFs)
- Synchronous processing (no background workers)

## Future Enhancements

Planned improvements:
1. **File handling sub-agent**: For questions with attachments
2. **Browser automation**: Using playwright for complex web interactions
3. **Multi-modal support**: Image and PDF analysis
4. **Async processing**: Background task queue
5. **Caching**: Store intermediate results
6. **Self-reflection**: Agent reviews and refines answers

## License

Apache License 2.0

## References

- [GAIA Benchmark](https://huggingface.co/datasets/gaia-benchmark/GAIA)
- [DeepResearchAgent](https://github.com/SkyworkAI/DeepResearchAgent)
- [Google ADK Documentation](https://developers.google.com/adk)
