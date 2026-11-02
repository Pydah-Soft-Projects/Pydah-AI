import json
import base64
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


def safe_decode_jwt_claims(token: Optional[str]) -> Dict[str, Any]:
    """
    Safely inspect unverified JWT claims to extract user identity and role
    when explicit headers (x-user-id, x-user-role) are not provided by client.
    Note: Strict cryptographic verification is always enforced by the application backend.
    """
    if not token or "." not in token:
        return {}
    
    try:
        parts = token.split(".")
        if len(parts) == 3:
            payload_segment = parts[1]
            rem = len(payload_segment) % 4
            if rem > 0:
                payload_segment += "=" * (4 - rem)
            decoded = base64.urlsafe_b64decode(payload_segment.encode("utf-8"))
            return json.loads(decoded.decode("utf-8"))
    except Exception:
        pass
    return {}


def get_user_context(request: Optional[Request] = None, payload: Optional[ChatRequest] = None) -> Dict[str, Any]:
    """
    Extract authenticated user context and delegated access token from HTTP request headers or payload.
    Supports students, faculty, and administrative staff seamlessly.
    Ensures secure data retrieval delegation when invoking application tool APIs.
    """
    token: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    service_url: Optional[str] = None
    headers_dict: Dict[str, str] = {}

    if request is not None:
        auth_header = request.headers.get("authorization")
        token = extract_bearer_token(auth_header)
        
        user_id = (
            request.headers.get("x-user-id") or
            request.headers.get("x-student-id") or
            request.headers.get("x-faculty-id") or
            request.headers.get("x-admin-id") or
            request.headers.get("x-employee-id")
        )
        role = request.headers.get("x-user-role") or request.headers.get("x-role")
        service_url = (
            request.headers.get("x-service-url") or
            request.headers.get("x-backend-url") or
            request.headers.get("x-portal-url") or
            request.headers.get("x-application-url")
        )
        
        # Copy safe headers for potential service-to-service forwarding
        for k, v in request.headers.items():
            if k.lower().startswith("x-"):
                headers_dict[k.lower()] = v

    # Payload token & service_url fallback if not provided via HTTP header
    if payload:
        if not token and payload.user_token:
            token = payload.user_token
        if not service_url and payload.service_url:
            service_url = payload.service_url

    # If user_id, role, or service_url wasn't explicitly supplied, inspect JWT payload claims
    if token and (not user_id or not role or not service_url):
        claims = safe_decode_jwt_claims(token)
        if not user_id:
            user_id = claims.get("user_id") or claims.get("student_id") or claims.get("sub") or claims.get("id")
        if not role:
            role = claims.get("role") or claims.get("user_role") or claims.get("type")
        if not service_url:
            service_url = claims.get("service_url") or claims.get("backend_url") or claims.get("iss")

    if service_url:
        service_url = service_url.strip().rstrip('/')

    return {
        "delegated_access_token": token,
        "user_id": user_id,
        "role": role or "user",
        "service_url": service_url,
        "headers": headers_dict
    }
