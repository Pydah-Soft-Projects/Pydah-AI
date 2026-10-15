import inspect
from typing import Dict, Any, Callable, List, Optional
from src.tools.generic_connector import dispatch_tool_to_application, TOOL_SERVICE_MAPPING
from src.tools.handlers.student_tools import (
    get_my_student_profile,
    get_my_attendance_summary,
    get_my_academic_marks,
    get_my_timetable
)
from src.tools.handlers.fee_tools import get_my_fee_summary, get_my_pending_dues
from src.tools.handlers.transport_tools import get_my_bus_details, get_my_route


class ToolExecutionError(Exception):
    """Raised when tool execution is unpermitted or fails."""
    pass


FALLBACK_HANDLERS: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = {
    "get_my_student_profile": get_my_student_profile,
    "get_my_attendance_summary": get_my_attendance_summary,
    "get_my_academic_marks": get_my_academic_marks,
    "get_my_timetable": get_my_timetable,
    "get_my_time_table": get_my_timetable,
    "get_my_fee_summary": get_my_fee_summary,
    "get_my_pending_dues": get_my_pending_dues,
    "get_my_bus_details": get_my_bus_details,
    "get_my_route": get_my_route,
}


def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    user_context: Dict[str, Any],
    allowed_tools: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Pure Tool Dispatcher Executor:
    1. Enforces permission check (tool must be allowed for persona).
    2. Dispatches (tool_name, arguments, user_token) to target application's single /execute-tool endpoint.
    3. Application executes tool on its side and returns data.
    """
    if allowed_tools is not None and tool_name not in allowed_tools:
        raise ToolExecutionError(
            f"Security Policy Violation: Tool '{tool_name}' is not permitted for this assistant persona."
        )

    # 1. Dispatch tool execution to target application runner
    if tool_name in TOOL_SERVICE_MAPPING:
        result = dispatch_tool_to_application(tool_name, arguments, user_context)
        # Fallback to local dev handler if service URL is not set in environment
        if isinstance(result, dict) and result.get("status") == "dev_mock":
            handler = FALLBACK_HANDLERS.get(tool_name)
            if handler:
                return handler(arguments, user_context)
        return result

    # 2. Local Fallback Handler Execution
    handler = FALLBACK_HANDLERS.get(tool_name)
    if handler is None:
        raise ToolExecutionError(f"No application mapping or fallback handler found for tool: '{tool_name}'")

    try:
        if inspect.iscoroutinefunction(handler):
            import asyncio
            return asyncio.run(handler(arguments=arguments, user_context=user_context))
        else:
            return handler(arguments=arguments, user_context=user_context)
    except Exception as e:
        raise ToolExecutionError(f"Error executing tool '{tool_name}': {str(e)}") from e
