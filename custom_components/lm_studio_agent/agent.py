"""The AI Agent implementation with LM Studio support."""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .client import LMStudioClient
from .const import CONF_LM_STUDIO_URL, CONF_MODEL
from .prompts import SYSTEM_PROMPT
from .tools import ToolsHandler
from .utils import sanitize_for_logging

_LOGGER = logging.getLogger(__name__)

class LMStudioAgent:
    """Agent for handling queries with dynamic data requests."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the agent with LM Studio configuration."""
        self.hass = hass
        self.config = config
        self.conversation_history: List[Dict[str, Any]] = []
        self._cache: Dict[str, Any] = {}
        self._cache_timeout = 300  # 5 minutes
        self._max_retries = 10
        self._retry_delay = 1  # seconds
        self._rate_limit = 60  # requests per minute
        self._last_request_time = 0
        self._request_count = 0
        self._request_window_start = time.time()

        url = config.get(CONF_LM_STUDIO_URL)

        _LOGGER.debug("Initializing LMStudioAgent with LM Studio URL: %s", url)
        # Use standard system prompt
        self.system_prompt = SYSTEM_PROMPT

        # Initialize LM Studio client
        url = self.config.get(CONF_LM_STUDIO_URL, "http://localhost:1234/v1")
        model = self.config.get(CONF_MODEL, "auto")

        _LOGGER.debug("Initializing LMStudioAgent with LM Studio URL: %s, Model: %s", url, model)

        self.ai_client = LMStudioClient(url=url, model=model)
        self.tools_handler = ToolsHandler(hass)

        _LOGGER.debug("LMStudioAgent initialized successfully")

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        if current_time - self._request_window_start >= 60:
            self._request_count = 0
            self._request_window_start = current_time

        if self._request_count >= self._rate_limit:
            return False

        self._request_count += 1
        return True

    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if it's still valid."""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self._cache_timeout:
                return data
            del self._cache[key]
        return None

    def _set_cached_data(self, key: str, data: Any) -> None:
        """Store data in cache with timestamp."""
        self._cache[key] = (time.time(), data)

    async def _get_ai_response(self) -> str:
        """Get response from the LM Studio client."""
        # Include system prompt + conversation history
        messages = []
        if isinstance(self.system_prompt, dict):
             messages.append(self.system_prompt)
        
        messages.extend(self.conversation_history)
        
        return await self.ai_client.get_response(messages)

    async def unload_model(self) -> Dict[str, Any]:
        """Unload the current model."""
        return await self.ai_client.unload_model()

    async def process_query(
        self, user_query: str, provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user query with input validation and rate limiting."""
        try:
            if not user_query or not isinstance(user_query, str):
                return {"success": False, "error": "Invalid query format"}

            # Log sanitized config
            _LOGGER.debug(
                f"Processing query using LM Studio Agent. Config: {json.dumps(sanitize_for_logging(self.config), default=str)}"
            )

            # Ensure client is initialized
            if not self.ai_client:
                _LOGGER.error("LM Studio client not initialized")
                return {"success": False, "error": "LM Studio client not initialized"}

            _LOGGER.debug(f"Using initialized LM Studio client with URL: {self.ai_client.base_url}")

            # Process the query with rate limiting and retries
            if not self._check_rate_limit():
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please wait before trying again.",
                }

            # Sanitize user input
            user_query = user_query.strip()[:1000]  # Limit length and trim whitespace

            _LOGGER.debug("Processing new query: %s", user_query)

            # Check cache for identical query
            cache_key = f"query_{hash(user_query)}"
            cached_result = self._get_cached_data(cache_key)
            if cached_result:
                return (
                    dict(cached_result)
                    if isinstance(cached_result, dict)
                    else {"error": "Invalid cached result"}
                )

            # Add system message to conversation if it's the first message
            if not self.conversation_history:
                _LOGGER.debug("Adding system message to new conversation")
                # System prompt is handled in _get_ai_response now, but we can verify here if needed
                pass

            # Add user query to conversation
            self.conversation_history.append({"role": "user", "content": user_query})
            _LOGGER.debug("Added user query to conversation history")

            max_iterations = 5  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                _LOGGER.debug(f"Processing iteration {iteration} of {max_iterations}")

                try:
                    # Get AI response
                    _LOGGER.debug("Requesting response from AI provider")
                    response = await self._get_ai_response()
                    _LOGGER.debug("Received response from AI provider: %s", response)

                    try:
                        # Try to parse the response as JSON with simplified approach
                        response_clean = response.strip()

                        # Remove potential BOM and other invisible characters
                        import codecs

                        if response_clean.startswith(codecs.BOM_UTF8.decode("utf-8")):
                            response_clean = response_clean[1:]

                        # Remove other common invisible characters
                        invisible_chars = [
                            "\ufeff",
                            "\u200b",
                            "\u200c",
                            "\u200d",
                            "\u2060",
                        ]
                        for char in invisible_chars:
                            response_clean = response_clean.replace(char, "")

                        # Simple strategy: try to parse the cleaned response directly
                        response_data = None
                        try:
                            response_data = json.loads(response_clean)
                        except json.JSONDecodeError as e:
                            # Fallback: try to extract JSON by finding the first { and last }
                            json_start = response_clean.find("{")
                            json_end = response_clean.rfind("}")

                            if (
                                json_start != -1
                                and json_end != -1
                                and json_end > json_start
                            ):
                                json_part = response_clean[json_start : json_end + 1]
                                try:
                                    response_data = json.loads(json_part)
                                except json.JSONDecodeError:
                                    raise e  # Re-raise the original error
                            else:
                                raise e  # Re-raise the original error

                        if response_data is None:
                            raise json.JSONDecodeError(
                                "All parsing strategies failed", response_clean, 0
                            )

                        _LOGGER.debug("Successfully parsed JSON response")
                        _LOGGER.debug(
                            "Parsed response type: %s",
                            response_data.get("request_type", "unknown"),
                        )

                        # Handle data request
                        if (
                            response_data.get("request_type") == "data_request"
                            or response_data.get("request_type") in [
                                "get_entity_state",
                                "get_entities_by_domain",
                                "get_entities_by_device_class",
                                "get_climate_related_entities",
                                "get_entities_by_area",
                                "get_entities",
                                "get_calendar_events",
                                "get_automations",
                                "get_entity_registry",
                                "get_device_registry",
                                "get_weather_data",
                                "get_area_registry",
                                "get_history",
                                "get_person_data",
                                "get_statistics",
                                "get_scenes",
                                "get_dashboards",
                                "get_dashboard_config",
                                "set_entity_state",
                                "create_automation",
                                "create_dashboard",
                                "update_dashboard",
                            ]
                        ):
                            # Add AI's response to conversation history (the clean JSON)
                            self.conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": json.dumps(
                                        response_data
                                    ), 
                                }
                            )

                            # Determine request type and params
                            if response_data.get("request_type") == "data_request":
                                request_type = response_data.get("request")
                            else:
                                request_type = response_data.get("request_type")
                            
                            parameters = response_data.get("parameters", {})
                            
                            _LOGGER.debug(
                                "Processing data request: %s with parameters: %s",
                                request_type,
                                json.dumps(parameters),
                            )

                            # Execute request via tools handler
                            data: Any = None
                            
                            # Mapping request types to tool handler methods
                            if request_type == "get_entity_state":
                                data = await self.tools_handler.get_entity_state(parameters.get("entity_id"))
                            elif request_type == "get_entities_by_domain":
                                data = await self.tools_handler.get_entities_by_domain(parameters.get("domain"))
                            elif request_type == "get_entities_by_area":
                                data = await self.tools_handler.get_entities_by_area(parameters.get("area_id"))
                            elif request_type == "get_entities":
                                data = await self.tools_handler.get_entities(
                                    area_id=parameters.get("area_id"),
                                    area_ids=parameters.get("area_ids"),
                                )
                            elif request_type == "get_entities_by_device_class":
                                data = await self.tools_handler.get_entities_by_device_class(
                                    parameters.get("device_class"),
                                    parameters.get("domain"),
                                )
                            elif request_type == "get_climate_related_entities":
                                data = await self.tools_handler.get_climate_related_entities()
                            elif request_type == "get_calendar_events":
                                data = await self.tools_handler.get_calendar_events(parameters.get("entity_id"))
                            elif request_type == "get_automations":
                                data = await self.tools_handler.get_automations()
                            elif request_type == "get_entity_registry":
                                data = await self.tools_handler.get_entity_registry()
                            elif request_type == "get_device_registry":
                                data = await self.tools_handler.get_device_registry()
                            elif request_type == "get_weather_data":
                                data = await self.tools_handler.get_weather_data()
                            elif request_type == "get_area_registry":
                                data = await self.tools_handler.get_area_registry()
                            elif request_type == "get_history":
                                data = await self.tools_handler.get_history(
                                    parameters.get("entity_id"),
                                    parameters.get("hours", 24),
                                )
                            elif request_type == "get_person_data":
                                data = await self.tools_handler.get_person_data()
                            elif request_type == "get_statistics":
                                data = await self.tools_handler.get_statistics(parameters.get("entity_id"))
                            elif request_type == "get_scenes":
                                data = await self.tools_handler.get_scenes()
                            elif request_type == "get_dashboards":
                                data = await self.tools_handler.get_dashboards()
                            elif request_type == "get_dashboard_config":
                                data = await self.tools_handler.get_dashboard_config(parameters.get("dashboard_url"))
                            elif request_type == "set_entity_state":
                                data = await self.tools_handler.set_entity_state(
                                    parameters.get("entity_id"),
                                    parameters.get("state"),
                                    parameters.get("attributes"),
                                )
                            elif request_type == "create_automation":
                                data = await self.tools_handler.create_automation(parameters.get("automation"))
                            elif request_type == "create_dashboard":
                                data = await self.tools_handler.create_dashboard(parameters.get("dashboard_config"))
                            elif request_type == "update_dashboard":
                                data = await self.tools_handler.update_dashboard(
                                    parameters.get("dashboard_url"),
                                    parameters.get("dashboard_config"),
                                )
                            else:
                                data = {"error": f"Unknown request type: {request_type}"}
                                _LOGGER.warning("Unknown request type: %s", request_type)

                            # Handling data errors
                            if isinstance(data, dict) and "error" in data:
                                return {"success": False, "error": data["error"]}
                            elif isinstance(data, list) and any(
                                "error" in item for item in data if isinstance(item, dict)
                            ):
                                errors = [
                                    item["error"]
                                    for item in data
                                    if isinstance(item, dict) and "error" in item
                                ]
                                return {"success": False, "error": "; ".join(errors)}

                            _LOGGER.debug(
                                "Retrieved data for request: %s",
                                json.dumps(data, default=str),
                            )

                            # Add data to conversation as user message
                            self.conversation_history.append(
                                {
                                    "role": "user",
                                    "content": json.dumps({"data": data}, default=str),
                                }
                            )
                            continue

                        elif response_data.get("request_type") == "final_response":
                            # Add final response to conversation history
                            self.conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": json.dumps(
                                        response_data
                                    ),  
                                }
                            )

                            result = {
                                "success": True,
                                "answer": response_data.get("response", ""),
                            }
                            self._set_cached_data(cache_key, result)
                            return result

                        elif (
                            response_data.get("request_type") == "automation_suggestion"
                        ):
                             # Add automation suggestion to conversation history
                            self.conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": json.dumps(
                                        response_data
                                    ), 
                                }
                            )

                            result = {
                                "success": True,
                                "answer": json.dumps(response_data),
                            }
                            self._set_cached_data(cache_key, result)
                            return result
                            
                        elif (
                            response_data.get("request_type") == "dashboard_suggestion"
                        ):
                             # Add suggestion to conversation history
                            self.conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": json.dumps(
                                        response_data
                                    ), 
                                }
                            )

                            result = {
                                "success": True,
                                "answer": json.dumps(response_data),
                            }
                            self._set_cached_data(cache_key, result)
                            return result

                        elif response_data.get("request_type") == "call_service":
                             # Handle service call request
                            domain = response_data.get("domain")
                            service = response_data.get("service")
                            target = response_data.get("target", {})
                            service_data_params = response_data.get("service_data", {})

                            # Resolve nested requests in target (simplified from original logic for now)
                            # Original logic had complex recursion for entity resolution.
                            # For now, we will trust the LLM or implement the same logic if needed.
                            # Assuming basic target for this refactor to keep it clean.
                            
                            # We can just pass it to tools_handler
                            
                             # Add AI's response to conversation history
                            self.conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": json.dumps(
                                        response_data
                                    ),  
                                }
                            )

                            data = await self.tools_handler.call_service(
                                domain, service, target, service_data_params
                            )

                            if isinstance(data, dict) and "error" in data:
                                return {"success": False, "error": data["error"]}

                            _LOGGER.debug(
                                "Service call completed: %s",
                                json.dumps(data, default=str),
                            )

                            self.conversation_history.append(
                                {
                                    "role": "user",
                                    "content": json.dumps({"data": data}, default=str),
                                }
                            )
                            continue

                        else:
                            _LOGGER.warning(
                                "Unknown response type: %s",
                                response_data.get("request_type"),
                            )
                            return {
                                "success": False,
                                "error": f"Unknown response type: {response_data.get('request_type')}",
                            }

                    except json.JSONDecodeError as e:
                        # Log the response to help with debugging
                        response_preview = (
                            response[:1000] if len(response) > 1000 else response
                        )
                        _LOGGER.warning(
                            "Failed to parse response as JSON: %s. Response length: %d. Response preview: %s",
                            str(e),
                            len(response),
                            response_preview,
                        )
                         # Check for repetitive loop failure
                        if (
                            response_preview.startswith(
                                '{"request_type": "automation_suggestion'
                            )
                            and len(response) > 10000
                        ):
                             _LOGGER.warning(
                                "Detected corrupted automation suggestion response"
                            )
                             return {
                                "success": False,
                                "error": "AI generated corrupted automation response. Please try again with a more specific request.",
                            }
                        
                        raise e # re-raise to catch below and retry if needed

                except Exception as e:
                    _LOGGER.error(
                        "AI client error on attempt %d: %s", iteration, str(e)
                    )
                    await asyncio.sleep(self._retry_delay * iteration)
                    if iteration == max_iterations:
                         return {"success": False, "error": f"Failed after multiple retries: {str(e)}"}
                    continue
            
            return {"success": False, "error": "Max iterations reached without final response"}

        except Exception as e:
            _LOGGER.exception("Error processing query: %s", str(e))
            return {"success": False, "error": f"Error: {str(e)}"}

    def clear_conversation_history(self) -> None:
        """Clear the conversation history and cache."""
        self.conversation_history = []
        self._cache.clear()
        _LOGGER.debug("Conversation history and cache cleared")
