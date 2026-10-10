import json
from typing import List, Dict, Any, Tuple
from src.config import Config
from src.llm_client import LLMClient
from src.schemas import ChatRequest
from src.assistants.resolver import resolve_assistant
from src.tools.registry import get_tool_schemas
from src.tools.executor import execute_tool, ToolExecutionError


def run_assistant_chat(
    payload: ChatRequest,
    user_context: Dict[str, Any],
    config: Config,
    client: LLMClient
) -> Tuple[str, List[str], str]:
    """
    Core GenAI Orchestration Loop:
    1. Resolve assistant persona & allowed tool scope.
    2. Format prompt context and apply sliding history window truncation.
    3. Query OpenRouter model with allowed tool schemas.
    4. If model requests tool calls, validate, execute via tool executor, and send results back.
    5. Generate final natural language response.

    :return: Tuple of (final_answer, executed_tool_names, resolved_assistant_id)
    """
    # 1. Resolve Assistant Persona & Scope
    assistant_config = resolve_assistant(payload.assistant_id)
    system_text = payload.system_prompt or assistant_config.system_prompt
    allowed_tools = assistant_config.allowed_tools

    # 2. Build Message List
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_text}]

    if payload.history:
        for item in payload.history:
            msg_dict: Dict[str, Any] = {"role": item.role, "content": item.content or ""}
            if item.name:
                msg_dict["name"] = item.name
            if item.tool_call_id:
                msg_dict["tool_call_id"] = item.tool_call_id
            if item.tool_calls:
                msg_dict["tool_calls"] = item.tool_calls
            messages.append(msg_dict)

    # Append current user prompt
    messages.append({"role": "user", "content": payload.message})

    # Apply History Slicing (retaining system prompt at index 0)
    system_msg = messages[0]
    conversation = messages[1:]
    if len(conversation) > config.max_history_messages:
        conversation = conversation[-config.max_history_messages:]
    final_messages = [system_msg] + conversation

    # 3. Retrieve Permitted Tool Schemas
    tool_schemas = get_tool_schemas(allowed_tools) if allowed_tools else None

    # 4. Generate Initial Completion
    assistant_choice = client.generate_completion(final_messages, tools=tool_schemas)

    executed_tools: List[str] = []

    # 5. Handle Tool Calling Loop (Iterative multi-turn execution)
    max_tool_turns = 3
    turn = 0

    while turn < max_tool_turns:
        tool_calls = assistant_choice.get("tool_calls")
        if not tool_calls:
            break

        # Append assistant message with tool calls to conversation history
        final_messages.append(assistant_choice)

        for call in tool_calls:
            call_id = call.get("id", "call_default")
            func_obj = call.get("function", {})
            tool_name = func_obj.get("name", "")
            raw_args = func_obj.get("arguments", "{}")

            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except Exception:
                args = {}

            # Execute permitted tool securely
            try:
                tool_output = execute_tool(
                    tool_name=tool_name,
                    arguments=args,
                    user_context=user_context,
                    allowed_tools=allowed_tools
                )
                executed_tools.append(tool_name)
                output_str = json.dumps(tool_output)
            except ToolExecutionError as err:
                output_str = json.dumps({"error": str(err)})

            # Append tool result message back to LLM context
            final_messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": tool_name,
                "content": output_str
            })

        # Re-query LLM with tool execution output
        assistant_choice = client.generate_completion(final_messages, tools=tool_schemas)
        turn += 1

    final_content = assistant_choice.get("content") or "I have processed your request."
    return final_content.strip(), executed_tools, assistant_config.id
