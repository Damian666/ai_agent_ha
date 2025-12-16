import sys
import os
import traceback
from unittest.mock import MagicMock

def debug_import():
    try:
        # 1. Setup paths
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        sys.path.append(base_path)
        print(f"Added to sys.path: {base_path}")
        
        # 2. Mock dependencies
        print("Mocking dependencies...")
        mock_hass = MagicMock()
        mock_hass.core = MagicMock()
        sys.modules["homeassistant"] = mock_hass
        sys.modules["homeassistant.core"] = mock_hass
        sys.modules["homeassistant.helpers"] = MagicMock()
        sys.modules["homeassistant.helpers.storage"] = MagicMock()
        sys.modules["homeassistant.util"] = MagicMock()
        sys.modules["homeassistant.util"] = MagicMock()
        sys.modules["homeassistant.util.dt"] = MagicMock()
        
        # Mock components package which is imported by __init__.py
        mock_components = MagicMock()
        mock_components.frontend = MagicMock()
        sys.modules["homeassistant.components"] = mock_components
        sys.modules["homeassistant.components.frontend"] = mock_components.frontend
        sys.modules["homeassistant.components.http"] = MagicMock()
        
        # Mock aiohttp
        mock_aiohttp = MagicMock()
        mock_aiohttp.ClientTimeout = MagicMock
        sys.modules["aiohttp"] = mock_aiohttp
        
        # Mock yaml
        sys.modules["yaml"] = MagicMock()
        
        # Mock voluptuous
        sys.modules["voluptuous"] = MagicMock()

        # 3. Import
        print("Attempting import...")
        from custom_components.lm_studio_agent.agent import LMStudioClient
        print("Import successful!")
        
        # 4. Instantiate
        client = LMStudioClient("http://localhost:1234/v1")
        print(f"Client instantiated: {client.base_url}")
        
    except Exception as e:
        print(f"IMPORT ERROR: {e}")
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == "__main__":
    debug_import()
