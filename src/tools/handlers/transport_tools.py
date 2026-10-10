import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any


def get_my_bus_details(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch bus route and driver allocation details for authenticated student.
    """
    transport_service_url = os.getenv("TRANSPORT_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if transport_service_url:
        endpoint = f"{transport_service_url.rstrip('/')}/api/ai/bus-details"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            req = urllib.request.Request(endpoint, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {
                "error": f"Unable to reach Transport Backend at {transport_service_url}",
                "details": str(e)
            }

    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "bus_number": "AP-39-TV-1042",
        "route_name": "Route 14 - Kakinada Main Town to Campus",
        "seat_number": "22B",
        "driver_name": "Ramesh Kumar",
        "driver_phone": "+91-9848012345",
        "pickup_point": "RTC Complex, Platform 3",
        "pickup_time": "07:45 AM",
        "status": "ON_TIME"
    }


def get_my_route(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch complete route stop list and schedule.
    """
    transport_service_url = os.getenv("TRANSPORT_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if transport_service_url:
        endpoint = f"{transport_service_url.rstrip('/')}/api/ai/route"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            req = urllib.request.Request(endpoint, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {
                "error": f"Unable to fetch transport route schedule ({transport_service_url})",
                "details": str(e)
            }

    return {
        "route_id": "R-14",
        "route_name": "Route 14 - Kakinada Main Town",
        "bus_number": "AP-39-TV-1042",
        "stops": [
            {"stop_name": "Bhanugudi Junction", "time": "07:35 AM"},
            {"stop_name": "RTC Complex", "time": "07:45 AM"},
            {"stop_name": "Cinema Road", "time": "07:55 AM"},
            {"stop_name": "Pydah College Campus", "time": "08:25 AM"}
        ]
    }
