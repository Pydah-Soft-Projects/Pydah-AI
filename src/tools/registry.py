from typing import Dict, List, Any, Optional

# Dynamic Self-Describing Tool Architecture:
# All tool schemas are dynamically discovered at runtime from the connected application backend (GET /ai-tools).
# No static/hardcoded tool definitions are maintained here.
ALL_TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {}


def normalize_tool_schema(tool_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Ensure any tool schema conforms to OpenAI / Gemini function definition format."""
    if not isinstance(tool_item, dict):
        return None

    # Already valid { "type": "function", "function": { "name": ... } }
    if tool_item.get("type") == "function" and "function" in tool_item:
        return tool_item

    name = tool_item.get("name")
    if not name or not isinstance(name, str):
        return None

    return {
        "type": "function",
        "function": {
            "name": name.strip(),
            "description": tool_item.get("description", f"Execute {name}"),
            "parameters": tool_item.get("parameters") or {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }


def get_tool_schemas(
    allowed_tool_names: Optional[List[str]] = None,
    dynamic_tools: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Return list of OpenAPI/OpenRouter function schemas matching permitted tool names and discovered dynamic tools.
    - If allowed_tool_names is None or contains "*", all relevant tools are permitted.
    - Merges statically defined tools with dynamically discovered application tools.
    - Deduplicates by function name (dynamic tools take priority over static schemas).
    """
    merged_tools: Dict[str, Dict[str, Any]] = {}

    # 1. Add static schemas if permitted
    allow_all = not allowed_tool_names or "*" in allowed_tool_names
    allowed_set = set(allowed_tool_names) if allowed_tool_names else set()

    for name, schema in ALL_TOOL_SCHEMAS.items():
        if allow_all or name in allowed_set:
            norm_schema = normalize_tool_schema(schema)
            if norm_schema:
                fn_name = norm_schema["function"]["name"]
                merged_tools[fn_name] = norm_schema

    # 2. Add dynamically discovered tools from application backend
    if dynamic_tools:
        for dyn_tool in dynamic_tools:
            norm_tool = normalize_tool_schema(dyn_tool)
            if not norm_tool:
                continue

            fn_name = norm_tool["function"]["name"]

            # Allow if allow_all or explicitly whitelisted
            if allow_all or fn_name in allowed_set:
                merged_tools[fn_name] = norm_tool

    return list(merged_tools.values())
