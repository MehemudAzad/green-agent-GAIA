# A2A Implementation - Correction Summary

## Issue Found
The previous implementation was using Google ADK's internal `RemoteA2aAgent` class instead of the official `a2a-sdk` package.

## Changes Made

### 1. Green Evaluator (`green-evaluator/agent/evaluator.py`)

**Before (Incorrect):**
- Used `google.adk.agents.remote_a2a_agent.RemoteA2aAgent`
- Used `google.adk.runners.Runner` with sessions
- Used `google.adk.sessions.InMemorySessionService`
- Complex setup with root agent and sub-agents

**After (Correct):**
- Uses `a2a.client.ClientFactory` to create A2A client
- Uses `a2a.client.A2ACardResolver` to fetch agent card
- Uses `a2a.types.Message` for message creation
- Iterates over events from `client.send_message()`

**Key Pattern (from reference `agentbeats/client.py`):**
```python
# Setup
resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
agent_card = await resolver.get_agent_card()
config = ClientConfig(httpx_client=httpx_client, streaming=False)
factory = ClientFactory(config)
client = factory.create(agent_card)

# Send message
outbound_msg = Message(
    kind="message",
    role=Role.user,
    parts=[Part(TextPart(kind="text", text=question_text))],
    message_id=uuid4().hex,
)

async for event in client.send_message(outbound_msg):
    last_event = event

# Extract response from last_event
```

### 2. Purple Agent Server (`purple-agents/baseline/purple_baseline/a2a_server.py`)

**Status:** Already correct! ✅
- Uses `google.adk.a2a.utils.agent_to_a2a.to_a2a()` 
- This is the proper way to expose an ADK agent as an A2A server

### 3. Dependencies Updated

**pyproject.toml & requirements.txt:**
- Added: `a2a-sdk>=0.3.5` (official A2A SDK)
- Added: `httpx>=0.28.0` (async HTTP client)
- Removed: Complex ADK dependencies (only needed on server side)
- Kept: `google-adk>=1.14.1` for purple agent server only

## Architecture

```
┌─────────────────────┐
│  Green Evaluator    │
│  (a2a-sdk client)   │
│                     │
│  • ClientFactory    │
│  • A2ACardResolver  │
│  • Message types    │
└──────────┬──────────┘
           │
           │ HTTP/JSON-RPC
           │ (A2A Protocol)
           │
           ▼
┌─────────────────────┐
│  Purple Agent       │
│  (ADK + to_a2a())   │
│                     │
│  • ADK Agent        │
│  • to_a2a() wrapper │
│  • Agent Card       │
└─────────────────────┘
```

## Reference Implementation
Based on: `agentbeats/client.py` which shows the correct a2a-sdk usage pattern.

## Testing
1. Install dependencies: `pip install -r green-evaluator/requirements.txt`
2. Start purple agent: `cd purple-agents/baseline && python -m purple_baseline.a2a_server`
3. Run evaluator: `cd green-evaluator && python -m agent.evaluator --max-questions 1`

## Key Differences: ADK vs a2a-sdk

| Aspect | Google ADK (Wrong) | a2a-sdk (Correct) |
|--------|-------------------|-------------------|
| Client Creation | `RemoteA2aAgent(agent_card=url)` | `ClientFactory(config).create(agent_card)` |
| Message Type | ADK's internal message types | `a2a.types.Message` |
| Response | Event stream from Runner | Event stream from `client.send_message()` |
| Agent Card | Implicit via URL | Explicit fetch via `A2ACardResolver` |
| Use Case | ADK-to-ADK internal | Cross-framework A2A protocol |
