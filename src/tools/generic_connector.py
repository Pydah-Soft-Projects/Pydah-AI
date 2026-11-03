import os
import time
import json
import ssl
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple


def _open_url_resilient(req: urllib.request.Request, timeout: int = 10):
    """
    Open HTTP/HTTPS request with automatic SSL verification fallback.
    Ensures connectivity across cloud environments, intermediate cert renewals, or private VPCs.
    """
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except (urllib.error.URLError, ssl.SSLError) as e:
        err_str = str(e)
        if "CERTIFICATE_VERIFY_FAILED" in err_str or "certificate has expired" in err_str or isinstance(getattr(e, "reason", None), ssl.SSLError):
            unverified_ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, context=unverified_ctx, timeout=timeout)
        raise


# In-memory manifest cache: { service_url: (timestamp, tools_list) }
_MANIFEST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL_SECONDS = 60.0  # Refresh tools from portal every 60 seconds


# Optional explicit tool-to-service environment variable overrides
# By default, dispatch_tool_to_application automatically routes tools dynamically based on keywords:
# - 'fee', 'due', 'payment', 'receipt' -> FEE_SERVICE_URL
# - 'bus', 'transport', 'route', 'driver' -> TRANSPORT_SERVICE_URL
# - default -> STUDENT_SERVICE_URL or APPLICATION_SERVICE_URL
TOOL_SERVICE_MAPPING: Dict[str, str] = {}


def fetch_application_tools(
    service_url: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None,
    force_refresh: bool = False
) -> List[Dict[str, Any]]:
    """
    Dynamically discover available tools from an application backend.
    Queries the host portal (e.g. Student / Campus Portal) manifest endpoint:
      - /ai-tools
      - /api/v1/ai-tools
      - /ai/tools
      - /api/ai/manifest
      - /execute-tool/manifest
    
    Returns normalized tool definitions to feed directly into the LLM.
    Caches results in memory for CACHE_TTL_SECONDS to avoid latency on every turn.
    """
    target_url = (
        service_url or
        (user_context.get("service_url") if user_context else None) or
        os.getenv("STUDENT_SERVICE_URL") or
        os.getenv("APPLICATION_SERVICE_URL")
    )
    if not target_url:
        return []

    target_url = target_url.strip().rstrip('/')
    now = time.time()

    # Check in-memory cache
    if not force_refresh and target_url in _MANIFEST_CACHE:
        cached_time, cached_tools = _MANIFEST_CACHE[target_url]
        if (now - cached_time) < CACHE_TTL_SECONDS:
            return cached_tools

    token = user_context.get("delegated_access_token") if user_context else None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["x-access-token"] = token
        headers["x-user-token"] = token
    if user_context and user_context.get("role"):
        headers["x-user-role"] = str(user_context.get("role"))

    manifest_paths = [
        "/api/ai-tools",
        "/api/ai/ai-tools",
        "/api/tools",
        "/ai-tools",
        "/api/v1/ai-tools",
        "/ai/tools",
        "/api/ai/manifest",
        "/execute-tool/manifest",
        "/ai_integration/tools"
    ]

    discovered_tools: List[Dict[str, Any]] = []

    clean_target = target_url.rstrip('/')
    candidate_urls = [clean_target]
    if clean_target.endswith("/api"):
        candidate_urls.append(clean_target[:-4])
    else:
        candidate_urls.append(f"{clean_target}/api")

    if "://localhost" in target_url:
        candidate_urls.append(clean_target.replace("://localhost", "://127.0.0.1"))
    elif "://127.0.0.1" in target_url:
        candidate_urls.append(clean_target.replace("://127.0.0.1", "://localhost"))

    # Deduplicate candidate base URLs while preserving order
    seen_bases = set()
    unique_candidates = []
    for b in candidate_urls:
        if b not in seen_bases:
            seen_bases.add(b)
            unique_candidates.append(b)

    last_discovery_error = None
    for base in unique_candidates:
        for path in manifest_paths:
            # Avoid duplicate /api/api
            if base.endswith("/api") and path.startswith("/api/"):
                url = f"{base[:-4]}{path}"
            else:
                url = f"{base}{path}"
            try:
                req = urllib.request.Request(url, headers=headers, method="GET")
                with _open_url_resilient(req, timeout=10) as resp:
                    if resp.status == 200:
                        raw_data = json.loads(resp.read().decode("utf-8"))
                        raw_list = []
                        if isinstance(raw_data, list):
                            raw_list = raw_data
                        elif isinstance(raw_data, dict):
                            raw_list = (
                                raw_data.get("tools") or 
                                raw_data.get("functions") or 
                                raw_data.get("manifest") or 
                                raw_data.get("data") or 
                                []
                            )

                        # Normalize into standard OpenAI tool function schema
                        for item in raw_list:
                            normalized = _normalize_manifest_tool(item)
                            if normalized:
                                discovered_tools.append(normalized)

                        if discovered_tools:
                            # Successfully discovered tools; store in cache
                            print(f"[NemoAI] Discovered {len(discovered_tools)} dynamic tools from {url}")
                            _MANIFEST_CACHE[target_url] = (now, discovered_tools)
                            return discovered_tools
            except Exception as e:
                last_discovery_error = e
                continue

    if not discovered_tools:
        print(f"[NemoAI Warning] Could not discover dynamic tools from {target_url} (last error: {last_discovery_error})")

    return discovered_tools


def _normalize_manifest_tool(tool_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalizes arbitrary portal tool declarations into OpenAI-compatible tool definitions.
    Supports:
      - Standard OpenAI format: { "type": "function", "function": { "name": ..., ... } }
      - Simple manifest format: { "name": "...", "description": "...", "parameters": { ... } }
    """
    if not isinstance(tool_item, dict):
        return None

    # Already in { "type": "function", "function": { ... } } format
    if tool_item.get("type") == "function" and "function" in tool_item:
        return tool_item

    # Simple { "name": ..., "description": ..., "parameters": ... } format
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


def dispatch_tool_to_application(
    tool_name: str,
    arguments: Dict[str, Any],
    user_context: Dict[str, Any],
    target_service_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Robust Tool Dispatcher:
    - Normalizes tool names and handles function name aliases.
    - Sends request to application execute-tool endpoint.
    - Retries across common route path variants (/execute-tool, /api/v1/execute-tool, /api/execute-tool, /ai_integration/execute-tool) if 404 is encountered.
    - Forwards auth token across multiple headers (Authorization, x-access-token, x-user-token) and payload body.
    """
    normalized_tool_name = tool_name.split(":")[-1].strip()
    clean_tool_name = normalized_tool_name.lower()
    env_var_name = TOOL_SERVICE_MAPPING.get(clean_tool_name) or TOOL_SERVICE_MAPPING.get(normalized_tool_name)

    base_url = (
        target_service_url or
        (user_context.get("service_url") if isinstance(user_context, dict) else None) or
        (user_context.get("headers", {}).get("x-service-url") if isinstance(user_context, dict) else None)
    )

    if not base_url:
        if env_var_name:
            base_url = os.getenv(env_var_name, "").strip()
        else:
            # Fallback priority: STUDENT_SERVICE_URL -> APPLICATION_SERVICE_URL
            if any(k in clean_tool_name for k in ["fee", "due", "payment", "receipt"]):
                base_url = os.getenv("FEE_SERVICE_URL", "").strip()
            elif any(k in clean_tool_name for k in ["bus", "transport", "route", "driver"]):
                base_url = os.getenv("TRANSPORT_SERVICE_URL", "").strip()
            else:
                base_url = os.getenv("STUDENT_SERVICE_URL", "").strip() or os.getenv("APPLICATION_SERVICE_URL", "").strip()

    if not base_url:
        return {
            "status": "dev_mock",
            "message": f"Service URL for tool '{tool_name}' was not provided in request (service_url / X-Service-URL) or .env",
            "dispatched_tool": tool_name,
            "arguments": arguments,
            "user_id": user_context.get("user_id") if isinstance(user_context, dict) else "STU-2025-0842"
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

    if user_context.get("user_id"):
        headers["x-user-id"] = str(user_context.get("user_id"))
    if user_context.get("role"):
        headers["x-user-role"] = str(user_context.get("role"))

    # Also forward any additional incoming x-* headers
    custom_headers = user_context.get("headers", {})
    for k, v in custom_headers.items():
        if k not in headers:
            headers[k] = str(v)

    payload = {
        "tool_name": normalized_tool_name,
        "function_name": normalized_tool_name,
        "arguments": arguments,
        "token": token,
        "user_context": user_context
    }

    data_bytes = json.dumps(payload).encode("utf-8")

    # Common application route path variants to try
    endpoint_paths: List[str] = [
        "/api/execute-tool",
        "/api/ai/execute-tool",
        "/execute-tool",
        "/api/v1/execute-tool",
        "/execute_tool",
        "/api/v1/execute_tool",
        "/ai_integration/execute-tool"
    ]

    clean_base = base_url.rstrip('/')
    candidate_bases = [clean_base]
    if clean_base.endswith("/api"):
        candidate_bases.append(clean_base[:-4])
    else:
        candidate_bases.append(f"{clean_base}/api")

    if "://localhost" in base_url:
        candidate_bases.append(clean_base.replace("://localhost", "://127.0.0.1"))
    elif "://127.0.0.1" in base_url:
        candidate_bases.append(clean_base.replace("://127.0.0.1", "://localhost"))

    # Deduplicate candidate bases
    seen_cbases = set()
    unique_cbases = []
    for b in candidate_bases:
        if b not in seen_cbases:
            seen_cbases.add(b)
            unique_cbases.append(b)

    last_error: Optional[Exception] = None

    for base in unique_cbases:
        for path in endpoint_paths:
            # Avoid duplicate /api/api
            if base.endswith("/api") and path.startswith("/api/"):
                dispatch_url = f"{base[:-4]}{path}"
            else:
                dispatch_url = f"{base}{path}"
            try:
                req = urllib.request.Request(dispatch_url, data=data_bytes, headers=headers, method="POST")
                with _open_url_resilient(req, timeout=35) as response:
                    resp_body = response.read().decode("utf-8")
                    try:
                        parsed = json.loads(resp_body)
                        print(f"[NemoAI] Tool '{tool_name}' dispatched successfully to {dispatch_url}")
                        return parsed
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
                print(f"[NemoAI] Tool '{tool_name}' returned HTTP {e.code} from {dispatch_url}: {error_body}")
                return {
                    "error": f"Application tool runner returned HTTP {e.code}",
                    "details": error_body or str(e)
                }
            except Exception as e:
                last_error = e
                continue

    return {
        "error": f"Failed to dispatch tool '{tool_name}' to application at {base_url}",
        "details": str(last_error) if last_error else "All endpoint path variants returned HTTP 404"
    }
