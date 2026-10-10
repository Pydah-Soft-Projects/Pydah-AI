from typing import Dict, Any, Optional
from fastapi import Request
from src.schemas import ChatRequest


def extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    """Extract Bearer token from HTTP Authorization header string."""
    if not authorization_header:
        return None
    
    parts = authorization_header.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_user_context(request: Optional[Request] = None, payload: Optional[ChatRequest] = None) -> Dict[str, Any]:
    """
    Extract authenticated user context and delegated access token from HTTP request headers or payload.
    Ensures secure data retrieval delegation when invoking application tool APIs.
    """
    token: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    headers_dict: Dict[str, str] = {}

    if request is not None:
        auth_header = request.headers.get("authorization")
        token = extract_bearer_token(auth_header)
        user_id = request.headers.get("x-user-id") or request.headers.get("x-student-id")
        role = request.headers.get("x-user-role", "student")
        
        # Copy safe headers for potential service-to-service forwarding
        for k, v in request.headers.items():
            if k.lower().startswith("x-"):
                headers_dict[k.lower()] = v

    # Payload token fallback if not provided via HTTP header
    if not token and payload and payload.user_token:
        token = payload.user_token

    return {
        "delegated_access_token": token,
        "user_id": user_id,
        "role": role,
        "headers": headers_dict
    }
