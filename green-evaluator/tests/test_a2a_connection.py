#!/usr/bin/env python3
"""Quick test to verify A2A connection works correctly."""

import asyncio
import sys
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart


async def test_connection(base_url: str = "http://localhost:8080"):
    """Test A2A connection to purple agent."""
    print(f"🔍 Testing A2A connection to: {base_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30) as httpx_client:
            # Step 1: Fetch agent card
            print("📋 Step 1: Fetching agent card...")
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=base_url,
            )
            agent_card = await resolver.get_agent_card()
            print(f"✅ Agent card fetched: {agent_card.name}")
            print(f"   Description: {agent_card.description}")
            print(f"   Version: {agent_card.version}")
            
            # Step 2: Create client
            print("\n🔧 Step 2: Creating A2A client...")
            config = ClientConfig(
                httpx_client=httpx_client,
                streaming=False,
            )
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            print("✅ Client created successfully")
            
            # Step 3: Send test message
            print("\n📤 Step 3: Sending test message...")
            test_question = "What is 2 + 2?"
            outbound_msg = Message(
                kind="message",
                role=Role.user,
                parts=[Part(TextPart(kind="text", text=test_question))],
                message_id=uuid4().hex,
            )
            
            print(f"   Question: {test_question}")
            
            # Step 4: Collect response
            print("\n📥 Step 4: Collecting response...")
            last_event = None
            async for event in client.send_message(outbound_msg):
                last_event = event
                print(f"   Event type: {type(event).__name__}")
            
            # Step 5: Extract text
            print("\n📝 Step 5: Extracting response text...")
            response_text = ""
            
            if isinstance(last_event, Message):
                for part in last_event.parts:
                    if isinstance(part.root, TextPart):
                        response_text += part.root.text
                print(f"✅ Got Message response")
            elif isinstance(last_event, tuple) and len(last_event) == 2:
                task, update = last_event
                if task.status and task.status.message:
                    for part in task.status.message.parts:
                        if isinstance(part.root, TextPart):
                            response_text += part.root.text
                print(f"✅ Got Task response")
            
            print(f"\n📋 Response: {response_text[:200]}...")
            print(f"\n🎉 SUCCESS! A2A connection working correctly.")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    success = asyncio.run(test_connection(base_url))
    sys.exit(0 if success else 1)
