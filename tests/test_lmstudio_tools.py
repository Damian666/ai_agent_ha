import sys
import json
import asyncio
import os
from unittest.mock import MagicMock, patch

# Mock Home Assistant imports BEFORE importing anything from the component
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.storage"] = MagicMock()
sys.modules["homeassistant.util"] = MagicMock()
sys.modules["homeassistant.util.dt"] = MagicMock()
sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.exceptions"] = MagicMock()
sys.modules["homeassistant.loader"] = MagicMock()
sys.modules["homeassistant.helpers.typing"] = MagicMock()

# Mock components as a package
components = MagicMock()
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.history"] = MagicMock()
sys.modules["homeassistant.components.logbook"] = MagicMock()
sys.modules["homeassistant.components.recorder"] = MagicMock()
sys.modules["homeassistant.components.lovelace"] = MagicMock()
sys.modules["homeassistant.components.frontend"] = MagicMock()
sys.modules["homeassistant.components.http"] = MagicMock()
sys.modules["homeassistant.components.websocket_api"] = MagicMock()

# Add project root to sys.path
project_root = os.path.abspath("s:/PycharmProjects/ai_agent_ha")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock const.py
const_mock = MagicMock()
const_mock.CONF_WEATHER_ENTITY = "weather.home"
const_mock.DOMAIN = "ai_agent_ha"
sys.modules["custom_components.ai_agent_ha.const"] = const_mock

# Let's try importing the module properly
try:
    print("Importing agent...")
    from custom_components.ai_agent_ha.agent import LMStudioClient

    print("Agent imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


async def test_tool_call_translation():
    print("Testing Tool Call Translation...")

    client = LMStudioClient(url="http://localhost:1234", model="llama-3.2-3b")

    # Mock aiohttp
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value.__aenter__.return_value = mock_session

        # Mock response for a tool call
        mock_response = MagicMock()
        mock_response.status = 200
        response_data = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": "call_123",
                                    "type": "function",
                                    "function": {
                                        "name": "get_weather_data",
                                        "arguments": "{}",
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        )

        # Make the mock awaitable
        async def async_text():
            return response_data

        mock_response.text = async_text
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Input messages (simulating agent history)
        messages = [
            {"role": "system", "content": "Original System Prompt"},
            {"role": "user", "content": "What is the weather?"},
        ]

        response = await client.get_response(messages)

        print(f"Response: {response}")

        # Verify the response was translated back to JSON command
        expected_response = json.dumps(
            {"request_type": "get_weather_data", "parameters": {}}
        )
        assert response == expected_response
        print("✅ Response translation verified")

        # Verify the request payload sent to API
        call_args = mock_session.post.call_args
        payload = call_args[1]["json"]

        # Check system prompt replacement
        assert payload["messages"][0]["role"] == "system"
        assert "Use the available tools" in payload["messages"][0]["content"]
        print("✅ System prompt replacement verified")

        # Check tools were sent
        assert "tools" in payload
        assert len(payload["tools"]) > 0
        print("✅ Tools presence verified")


async def test_history_translation():
    print("\nTesting History Translation...")

    client = LMStudioClient(url="http://localhost:1234", model="llama-3.2-3b")

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value.__aenter__.return_value = mock_session

        # Mock response (final answer)
        mock_response = MagicMock()
        mock_response.status = 200
        response_data = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "The weather is sunny.",
                        }
                    }
                ]
            }
        )

        async def async_text():
            return response_data

        mock_response.text = async_text
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Input messages with history of tool usage
        messages = [
            {"role": "system", "content": "Original System Prompt"},
            {"role": "user", "content": "What is the weather?"},
            {
                "role": "assistant",
                "content": json.dumps(
                    {"request_type": "get_weather_data", "parameters": {}}
                ),
            },
            {"role": "system", "content": 'TOOL RESULT: {"data": {"temperature": 20}}'},
        ]

        await client.get_response(messages)

        # Verify request payload
        call_args = mock_session.post.call_args
        payload = call_args[1]["json"]
        sent_messages = payload["messages"]

        # Check translation
        # Msg 0: System (replaced)
        # Msg 1: User
        # Msg 2: Assistant (Tool Call)
        # Msg 3: Tool (Result)

        assert sent_messages[2]["role"] == "assistant"
        assert (
            sent_messages[2]["tool_calls"][0]["function"]["name"] == "get_weather_data"
        )

        assert sent_messages[3]["role"] == "tool"
        assert (
            sent_messages[3]["tool_call_id"] == sent_messages[2]["tool_calls"][0]["id"]
        )
        assert '{"temperature": 20}' in sent_messages[3]["content"]

        print("✅ History translation verified")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_tool_call_translation())
    loop.run_until_complete(test_history_translation())
