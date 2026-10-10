import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any


# Map tool names to their target application service base environment variables ONLY.
# NO endpoint paths are stored here!
TOOL_SERVICE_MAPPING: Dict[str, str] = {
    # Student Assistant Tools -> STUDENT_SERVICE_URL
    "get_my_student_profile": "STUDENT_SERVICE_URL",
    "get_my_attendance_summary": "STUDENT_SERVICE_URL",
    "get_my_academic_marks": "STUDENT_SERVICE_URL",

    # Fee Assistant Tools -> FEE_SERVICE_URL
    "get_my_fee_summary": "FEE_SERVICE_URL",
    "get_my_pending_dues": "FEE_SERVICE_URL",

    # Transport Assistant Tools -> TRANSPORT_SERVICE_URL
    "get_my_bus_details": "TRANSPORT_SERVICE_URL",
    "get_my_route": "TRANSPORT_SERVICE_URL",
}


def dispatch_tool_to_application(
    tool_name: str,
    arguments: Dict[str, Any],
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Pure Tool Dispatcher:
    - Sends tool execution request to target application's single '/execute-tool' dispatcher endpoint.
    - Application runs the tool on its side and returns the resulting data.
    """
    env_var_name = TOOL_SERVICE_MAPPING.get(tool_name)
    if not env_var_name:
        return {"error": f"No application service mapping configured for tool '{tool_name}'"}

    base_url = os.getenv(env_var_name, "").strip()
    if not base_url:
        # Development fallback response when target application URL is not configured
        return {
            "status": "dev_mock",
            "message": f"Service URL environment variable '{env_var_name}' is not configured in .env",
            "dispatched_tool": tool_name,
            "arguments": arguments,
            "user_id": user_context.get("user_id") or "STU-2025-0842"
        }

    # Dispatch request directly to application's execute-tool runner
    dispatch_url = f"{base_url.rstrip('/')}/execute-tool"
    token = user_context.get("delegated_access_token")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "tool_name": tool_name,
        "arguments": arguments
    }

    data_bytes = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(dispatch_url, data=data_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as response:
            resp_body = response.read().decode("utf-8")
            try:
                return json.loads(resp_body)
            except json.JSONDecodeError:
                return {"result": resp_body}

    except urllib.error.HTTPError as e:
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
        return {
            "error": f"Failed to dispatch tool '{tool_name}' to target application at '{dispatch_url}'",
            "details": str(e)
        }
