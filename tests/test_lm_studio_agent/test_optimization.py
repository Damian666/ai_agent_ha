"""Test LM Studio Optimizations."""
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add custom components to path so we can import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Mock dependencies that might be missing in the test environment
mock_hass = MagicMock()
mock_hass.core = MagicMock()
sys.modules["homeassistant"] = mock_hass
sys.modules["homeassistant.core"] = mock_hass
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.storage"] = MagicMock()
sys.modules["homeassistant.util"] = MagicMock()
sys.modules["homeassistant.util.dt"] = MagicMock()

# Mock aiohttp if missing (though we use it in the test, so we might need to mock it carefully if it's truly not there)
# If aiohttp is installed, this is fine. If not, we need to mock it too.
try:
    import aiohttp
except ImportError:
    mock_aiohttp = MagicMock()
    mock_aiohttp.ClientTimeout = MagicMock
    sys.modules["aiohttp"] = mock_aiohttp

# Mock voluptuous as it's likely used in __init__.py or config_flow
sys.modules["voluptuous"] = MagicMock()
sys.modules["yaml"] = MagicMock()

from custom_components.lm_studio_agent.agent import LMStudioClient

class TestLMStudioOptimizations(unittest.IsolatedAsyncioTestCase):
    
    async def test_context_trimming(self):
        """Test history trimming logic."""
        client = LMStudioClient("http://localhost:1234/v1")
        client.max_context_length = 2000
        
        # Create a long history
        messages = [{"role": "user", "content": "x" * 100} for _ in range(50)]
        # 50 * 100 = 5000 chars => ~1250 tokens
        # With buffer of 1500, we have 500 tokens available (2000 chars)
        
        trimmed = client._trim_history(messages)
        self.assertLess(len(trimmed), 50)
        self.assertGreater(len(trimmed), 0) # Should keep some
        
    async def test_smart_loading_jit(self):
        """Test JIT loading logic."""
        client = LMStudioClient("http://localhost:1234/v1")
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = {
                "data": [
                    {"id": "test-model", "state": "not-loaded"}
                ]
            }
            mock_get.return_value.__aenter__.return_value = mock_resp
            
            await client._ensure_model_loaded()
            self.assertEqual(client.model, "test-model") # Should pick it for JIT
            
    async def test_telemetry_parsing(self):
        """Test parsing of stats and model_info."""
        client = LMStudioClient("http://localhost:1234/v1")
        client.model = "test-model"
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Hello"}}],
                "model_info": {"max_context_length": 8192},
                "stats": {"tokens_per_second": 50.5}
            }
            mock_post.return_value.__aenter__.return_value = mock_resp
            
            await client.get_response([])
            self.assertEqual(client.max_context_length, 8192) # Should update from response

if __name__ == "__main__":
    unittest.main()
