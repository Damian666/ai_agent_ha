"""Config flow for LM Studio Agent integration."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
)

from .client import LMStudioClient
from .const import CONF_LM_STUDIO_URL, CONF_MODEL, DEFAULT_LM_STUDIO_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LMStudioAgentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg,misc]
    """Handle a config flow for LM Studio Agent."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize the config flow."""
        self.lm_studio_url: Optional[str] = None
        self.available_models: Dict[str, str] = {} # id -> id (or name)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        try:
            return LMStudioAgentOptionsFlowHandler(config_entry)
        except Exception as e:
            _LOGGER.error("Error creating options flow: %s", e)
            return None

    async def async_step_user(self, user_input=None):
        """Handle the initial step (URL input)."""
        errors = {}

        if user_input is not None:
            self.lm_studio_url = user_input.get(CONF_LM_STUDIO_URL, DEFAULT_LM_STUDIO_URL)
            
            # Helper to validate URL and fetch models
            try:
                client = LMStudioClient(self.lm_studio_url)
                models = await client.get_models()
                
                if not models:
                    errors["base"] = "no_models_found"
                else:
                    self.available_models = {m["id"]: m["id"] for m in models}
                    return await self.async_step_model()
                    
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LM_STUDIO_URL, default=DEFAULT_LM_STUDIO_URL): TextSelector(
                        TextSelectorConfig(type="url")
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_model(self, user_input=None):
        """Handle the model selection step."""
        errors = {}
        
        # Add "Auto-detect" option
        options = ["auto"] + list(self.available_models.keys())
        
        if user_input is not None:
            # Check if already configured (singleton-like per provider, but we only have one now)
            await self.async_set_unique_id("lm_studio_agent_lm_studio")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="LM Studio Agent",
                data={
                    CONF_LM_STUDIO_URL: self.lm_studio_url,
                    CONF_MODEL: user_input.get(CONF_MODEL, "auto"),
                },
            )

        return self.async_show_form(
            step_id="model",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODEL, default="auto"): SelectSelector(
                        SelectSelectorConfig(
                            options=options,
                            mode="dropdown",
                        )
                    ),
                }
            ),
            errors=errors,
        )


class LMStudioAgentOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for LM Studio Agent."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial options step."""
        if user_input is not None:
            # Update the config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(title="", data={})

        current_url = self.config_entry.data.get(CONF_LM_STUDIO_URL, DEFAULT_LM_STUDIO_URL)
        current_model = self.config_entry.data.get(CONF_MODEL, "auto")

        # Fetch models to populate dropdown
        models_options = ["auto"]
        try:
            client = LMStudioClient(current_url)
            models = await client.get_models()
            if models:
                 models_options.extend([m["id"] for m in models])
            # Ensure current model is in options if it's custom
            if current_model not in models_options:
                models_options.append(current_model)
        except Exception:
            # If fail to connect, show text input or just current value
            pass

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LM_STUDIO_URL, default=current_url): TextSelector(
                        TextSelectorConfig(type="url")
                    ),
                    vol.Required(CONF_MODEL, default=current_model): SelectSelector(
                        SelectSelectorConfig(
                            options=models_options,
                            mode="dropdown",
                            custom_value=True # Allow custom value if API down
                        )
                    )
                }
            ),
        )
