"""Test script for LM Studio streaming events API.

This script tests the new streaming functionality including:
- Model loading detection
- Progress reporting
- Response aggregation
- Tool calling with streaming
"""

import asyncio
import json
import logging
import sys

from pathlib import Path

# Add parent directory to path to import the agent module
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from custom_components.ai_agent_ha.agent import LMStudioClient  # noqa: E402


# Configure logging to see the model loading progress
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_streaming_basic():
    """Test basic streaming with a simple query."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Streaming (Model Already Loaded)")
    print("=" * 60)

    client = LMStudioClient(
        url="http://localhost:1234/v1",
        model="your-model-name-here",  # Replace with your actual model
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2? Give a brief answer."},
    ]

    try:
        response = await client.get_response(messages)
        print(f"\nResponse received: {response}")

        # Parse and display
        data = json.loads(response)
        if data.get("request_type") == "final_response":
            print(f"Final answer: {data.get('response')}")

    except Exception as e:
        print(f"Error: {e}")


async def test_streaming_with_tools():
    """Test streaming with tool calls."""
    print("\n" + "=" * 60)
    print("TEST 2: Streaming with Tool Calls")
    print("=" * 60)

    client = LMStudioClient(
        url="http://localhost:1234/v1",
        model="your-model-name-here",  # Replace with your actual model
    )

    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant integrated with Home Assistant. Use the available tools to control devices and retrieve information.",
        },
        {"role": "user", "content": "Get the weather data"},
    ]

    try:
        response = await client.get_response(messages)
        print(f"\nResponse received: {response}")

        # Parse and display
        data = json.loads(response)
        if data.get("request_type") == "get_weather_data":
            print(f"Tool call detected: {data.get('request_type')}")
            print(f"Parameters: {data.get('parameters', {})}")

    except Exception as e:
        print(f"Error: {e}")


async def test_model_loading():
    """Test model loading detection.

    Note: To test this properly, you should:
    1. Unload the model in LM Studio first
    2. Run this test
    3. Watch for model loading progress messages
    """
    print("\n" + "=" * 60)
    print("TEST 3: Model Loading Detection")
    print("=" * 60)
    print("For best results, unload the model in LM Studio first")
    print("    Then run this test to see loading progress")
    print("=" * 60)

    client = LMStudioClient(
        url="http://localhost:1234/v1",
        model="your-model-name-here",  # Replace with your actual model
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Just say hi back."},
    ]

    try:
        print("\nSending request (watch for loading messages)...\n")
        response = await client.get_response(messages)
        print(f"\nResponse received: {response}")

    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LM Studio Streaming Events Test Suite")
    print("=" * 60)
    print("\nConfiguration:")
    print("   - LM Studio URL: http://localhost:1234/v1")
    print("   - Update the model name in the test functions")
    print("\nNote: Make sure LM Studio is running before testing")
    print("=" * 60)

    # Run tests
    await test_streaming_basic()
    await asyncio.sleep(1)  # Brief pause between tests

    await test_streaming_with_tools()
    await asyncio.sleep(1)

    await test_model_loading()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
