import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any


def get_my_fee_summary(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch comprehensive fee summary for the authenticated student/user.
    Communicates with Fee Management Application backend.
    """
    fee_service_url = os.getenv("FEE_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if fee_service_url:
        endpoint = f"{fee_service_url.rstrip('/')}/api/ai/fee-summary"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            req = urllib.request.Request(endpoint, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            # Fallback gracefully or bubble error details
            return {
                "error": f"Unable to reach Fee Management Service at {fee_service_url}",
                "details": str(e)
            }

    # Structured response when application backend URL is in development mode
    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "academic_year": arguments.get("academic_year") or "2025-2026",
        "total_tuition_fee": 75000,
        "total_paid": 50000,
        "balance_due": 25000,
        "due_date": "2026-11-15",
        "status": "PARTIALLY_PAID",
        "currency": "INR"
    }


def get_my_pending_dues(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch pending dues itemized breakdown for the authenticated student.
    """
    fee_service_url = os.getenv("FEE_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if fee_service_url:
        endpoint = f"{fee_service_url.rstrip('/')}/api/ai/pending-dues"
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
                "error": f"Unable to fetch pending dues from Fee Backend ({fee_service_url})",
                "details": str(e)
            }

    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "total_pending_dues": 25000,
        "currency": "INR",
        "itemized_dues": [
            {"category": "Term 2 Tuition Fee", "amount": 20000, "due_date": "2026-11-15"},
            {"category": "Lab & Library Security Deposit", "amount": 5000, "due_date": "2026-11-30"}
        ]
    }
