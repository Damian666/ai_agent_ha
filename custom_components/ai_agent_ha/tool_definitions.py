"""Tool definitions for OpenAI-compatible APIs."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_entity_state",
            "description": "Get the state and attributes of a specific entity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The entity ID (e.g., light.living_room)",
                    }
                },
                "required": ["entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entities_by_domain",
            "description": "Get all entities in a specific domain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The domain name (e.g., light, switch, sensor)",
                    }
                },
                "required": ["domain"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entities_by_area",
            "description": "Get all entities in a specific area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {
                        "type": "string",
                        "description": "The area ID (e.g., living_room)",
                    }
                },
                "required": ["area_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entities",
            "description": "Get entities from one or multiple areas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "area_id": {
                        "type": "string",
                        "description": "Single area ID",
                    },
                    "area_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of area IDs",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Get calendar events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Optional specific calendar entity ID",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_automations",
            "description": "Get all automations.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_data",
            "description": "Get current weather and forecast data.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entity_registry",
            "description": "Get entity registry entries.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_registry",
            "description": "Get device registry entries.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_area_registry",
            "description": "Get room/area information.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_history",
            "description": "Get historical state changes for an entity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The entity ID",
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default 24)",
                    },
                },
                "required": ["entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_logbook_entries",
            "description": "Get recent logbook events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default 24)",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_person_data",
            "description": "Get person tracking information.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_statistics",
            "description": "Get sensor statistics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The entity ID",
                    }
                },
                "required": ["entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scenes",
            "description": "Get scene configurations.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboards",
            "description": "Get list of all dashboards.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboard_config",
            "description": "Get configuration of a specific dashboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dashboard_url": {
                        "type": "string",
                        "description": "The dashboard URL path",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_entity_state",
            "description": "Set state of an entity (e.g., turn on/off lights, open/close covers).",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The entity ID",
                    },
                    "state": {
                        "type": "string",
                        "description": "The new state",
                    },
                    "attributes": {
                        "type": "object",
                        "description": "Optional attributes to set",
                    },
                },
                "required": ["entity_id", "state"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_service",
            "description": "Call any Home Assistant service directly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "The service domain (e.g., light)",
                    },
                    "service": {
                        "type": "string",
                        "description": "The service name (e.g., turn_on)",
                    },
                    "target": {
                        "type": "object",
                        "description": "Target entities/areas/devices",
                    },
                    "service_data": {
                        "type": "object",
                        "description": "Service data parameters",
                    },
                },
                "required": ["domain", "service"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_automation",
            "description": "Create a new automation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "automation": {
                        "type": "object",
                        "description": "The automation configuration",
                    }
                },
                "required": ["automation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_dashboard",
            "description": "Create a new dashboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dashboard_config": {
                        "type": "object",
                        "description": "The dashboard configuration",
                    }
                },
                "required": ["dashboard_config"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_dashboard",
            "description": "Update an existing dashboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dashboard_url": {
                        "type": "string",
                        "description": "The dashboard URL path",
                    },
                    "dashboard_config": {
                        "type": "object",
                        "description": "The new dashboard configuration",
                    },
                },
                "required": ["dashboard_url", "dashboard_config"],
            },
        },
    },
]
