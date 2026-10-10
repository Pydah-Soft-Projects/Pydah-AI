import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List


# Comprehensive Tool Service Mapping including function name aliases
TOOL_SERVICE_MAPPING: Dict[str, str] = {
    # Student Profile Aliases -> STUDENT_SERVICE_URL
    "get_my_student_profile": "STUDENT_SERVICE_URL",
    "get_student_profile": "STUDENT_SERVICE_URL",
    "get_my_profile": "STUDENT_SERVICE_URL",
    "get_profile": "STUDENT_SERVICE_URL",
    "fetch_student_profile": "STUDENT_SERVICE_URL",
    "student_profile": "STUDENT_SERVICE_URL",
    "get_user_profile": "STUDENT_SERVICE_URL",
    "get_student_details": "STUDENT_SERVICE_URL",
    "get_my_details": "STUDENT_SERVICE_URL",

    # Attendance Aliases -> STUDENT_SERVICE_URL
    "get_my_attendance_summary": "STUDENT_SERVICE_URL",
    "get_student_attendance": "STUDENT_SERVICE_URL",
    "get_my_attendance": "STUDENT_SERVICE_URL",
    "get_attendance": "STUDENT_SERVICE_URL",
    "fetch_attendance": "STUDENT_SERVICE_URL",
    "student_attendance": "STUDENT_SERVICE_URL",
    "get_attendance_summary": "STUDENT_SERVICE_URL",

    # Academic Marks Aliases -> STUDENT_SERVICE_URL
    "get_my_academic_marks": "STUDENT_SERVICE_URL",
    "get_student_marks": "STUDENT_SERVICE_URL",
    "get_my_marks": "STUDENT_SERVICE_URL",
    "get_marks": "STUDENT_SERVICE_URL",
    "get_internal_marks": "STUDENT_SERVICE_URL",
    "get_grades": "STUDENT_SERVICE_URL",
    "get_academic_performance": "STUDENT_SERVICE_URL",
    "student_marks": "STUDENT_SERVICE_URL",

    # Fee & Dues Aliases -> FEE_SERVICE_URL
    "get_my_fee_summary": "FEE_SERVICE_URL",
    "get_my_pending_dues": "FEE_SERVICE_URL",
    "get_student_fees": "FEE_SERVICE_URL",
    "get_my_fees": "FEE_SERVICE_URL",
    "get_pending_dues": "FEE_SERVICE_URL",
    "get_fee_details": "FEE_SERVICE_URL",
    "get_fees": "FEE_SERVICE_URL",
    "fetch_pending_dues": "FEE_SERVICE_URL",
    "student_fees": "FEE_SERVICE_URL",

    # Transport Aliases -> TRANSPORT_SERVICE_URL
    "get_my_bus_details": "TRANSPORT_SERVICE_URL",
    "get_my_route": "TRANSPORT_SERVICE_URL",
    "get_student_transport": "TRANSPORT_SERVICE_URL",
    "get_my_transport": "TRANSPORT_SERVICE_URL",
    "get_transport": "TRANSPORT_SERVICE_URL",
    "student_transport": "TRANSPORT_SERVICE_URL",
}


def dispatch_tool_to_application(
    tool_name: str,
    arguments: Dict[str, Any],
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Robust Tool Dispatcher:
    - Normalizes tool names and handles function name aliases.
    - Sends request to application execute-tool endpoint.
    - Retries across common route path variants (/execute-tool, /api/v1/execute-tool, /api/execute-tool, /ai_integration/execute-tool) if 404 is encountered.
    - Forwards auth token across multiple headers (Authorization, x-access-token, x-user-token) and payload body.
    """
    clean_tool_name = tool_name.strip().lower()
    env_var_name = TOOL_SERVICE_MAPPING.get(clean_tool_name) or TOOL_SERVICE_MAPPING.get(tool_name)

    if not env_var_name:
        # Fallback to STUDENT_SERVICE_URL if tool contains student keywords
        if "student" in clean_tool_name or "profile" in clean_tool_name or "attendance" in clean_tool_name or "marks" in clean_tool_name:
            env_var_name = "STUDENT_SERVICE_URL"
        elif "fee" in clean_tool_name or "due" in clean_tool_name:
            env_var_name = "FEE_SERVICE_URL"
        elif "bus" in clean_tool_name or "transport" in clean_tool_name or "route" in clean_tool_name:
            env_var_name = "TRANSPORT_SERVICE_URL"
        else:
            return {"error": f"No application service mapping configured for tool '{tool_name}'"}

    base_url = os.getenv(env_var_name, "").strip()
    if not base_url:
        return {
            "status": "dev_mock",
            "message": f"Service URL environment variable '{env_var_name}' is not configured in .env",
            "dispatched_tool": tool_name,
            "arguments": arguments,
            "user_id": user_context.get("user_id") or "STU-2025-0842"
        }

    token = user_context.get("delegated_access_token")

    # Flexible headers for auth resolution in target app
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["x-access-token"] = token
        headers["x-user-token"] = token

    payload = {
        "tool_name": tool_name,
        "function_name": tool_name,
        "arguments": arguments,
        "token": token,
        "user_context": user_context
    }

    data_bytes = json.dumps(payload).encode("utf-8")

    # Common application route path variants to try
    endpoint_paths: List[str] = [
        "/execute-tool",
        "/api/v1/execute-tool",
        "/api/execute-tool",
        "/execute_tool",
        "/api/v1/execute_tool",
        "/ai_integration/execute-tool"
    ]

    last_error: Optional[Exception] = None

    for path in endpoint_paths:
        dispatch_url = f"{base_url.rstrip('/')}{path}"
        try:
            req = urllib.request.Request(dispatch_url, data=data_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as response:
                resp_body = response.read().decode("utf-8")
                try:
                    return json.loads(resp_body)
                except json.JSONDecodeError:
                    return {"result": resp_body}
        except urllib.error.HTTPError as e:
            last_error = e
            # If 404, try the next path variant in the loop
            if e.code == 404:
                continue
            
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            return {
                "error": f"Application tool runner returned HTTP {e.code}",
                "details": error_body or str(e)
            }
        except Exception as e:
            last_error = e
            break

    return {
        "error": f"Failed to dispatch tool '{tool_name}' to application at {base_url}",
        "details": str(last_error) if last_error else "All endpoint path variants returned HTTP 404"
    }
