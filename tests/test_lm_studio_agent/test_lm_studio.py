"""Test LM Studio client."""
import pytest
from unittest.mock import MagicMock, patch
from custom_components.lm_studio_agent.agent import LMStudioClient

@pytest.mark.asyncio
async def test_lm_studio_client_init():
    """Test initialization."""
    client = LMStudioClient("http://localhost:1234/v1")
    assert client.url == "http://localhost:1234/v1"
    assert client.model == "local-model"
