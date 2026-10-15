import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any


def get_my_student_profile(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch student profile details for the authenticated user.
    """
    student_service_url = os.getenv("STUDENT_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if student_service_url:
        endpoint = f"{student_service_url.rstrip('/')}/api/ai/student-profile"
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
                "error": f"Unable to reach Student Service backend at {student_service_url}",
                "details": str(e)
            }

    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "full_name": "Sai Ram Krishna",
        "roll_number": "22PY1A0584",
        "branch": "Computer Science & Engineering",
        "section": "CSE-B",
        "semester": "Semester 6 (3rd Year)",
        "admission_year": 2022,
        "email": "sairam.k@pydah.edu.in",
        "phone": "+91-9876543210",
        "guardian_name": "K. Venkateswara Rao",
        "status": "ACTIVE"
    }


def get_my_attendance_summary(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch attendance record breakdown for the authenticated student.
    """
    student_service_url = os.getenv("STUDENT_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if student_service_url:
        endpoint = f"{student_service_url.rstrip('/')}/api/ai/attendance-summary"
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
                "error": f"Unable to fetch attendance summary from Student Backend ({student_service_url})",
                "details": str(e)
            }

    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "overall_percentage": 87.5,
        "total_classes_held": 240,
        "total_classes_attended": 210,
        "status": "ELIGIBLE_FOR_EXAMS",
        "subject_breakdown": [
            {"subject": "Artificial Intelligence & ML", "percentage": 90.0, "attended": 45, "held": 50},
            {"subject": "Database Management Systems", "percentage": 85.0, "attended": 42, "held": 50},
            {"subject": "Web Technologies", "percentage": 88.0, "attended": 44, "held": 50},
            {"subject": "Computer Networks", "percentage": 86.0, "attended": 43, "held": 50}
        ]
    }


def get_my_academic_marks(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch academic grades, CGPA, and semester marks.
    """
    student_service_url = os.getenv("STUDENT_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if student_service_url:
        endpoint = f"{student_service_url.rstrip('/')}/api/ai/academic-marks"
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
                "error": f"Unable to fetch marks from Student Backend ({student_service_url})",
                "details": str(e)
            }

    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "cgpa": 8.42,
        "latest_sgpa": 8.65,
        "current_semester": "Semester 5 Results",
        "grades": [
            {"subject": "Artificial Intelligence", "grade": "A+", "grade_points": 10},
            {"subject": "Data Mining", "grade": "A", "grade_points": 9},
            {"subject": "Operating Systems", "grade": "B+", "grade_points": 8},
            {"subject": "Software Engineering", "grade": "A", "grade_points": 9}
        ]
    }


def get_my_timetable(arguments: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch the authenticated student's weekly schedule / timetable.
    """
    student_service_url = os.getenv("STUDENT_SERVICE_URL", "").strip()
    token = user_context.get("delegated_access_token")

    if student_service_url:
        endpoint = f"{student_service_url.rstrip('/')}/api/ai/timetable"
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
                "error": f"Unable to fetch timetable from Student Backend ({student_service_url})",
                "details": str(e)
            }

    day = arguments.get("day") or "Monday"
    return {
        "student_id": user_context.get("user_id") or "STU-2025-0842",
        "branch": "Computer Science & Engineering",
        "section": "CSE-B",
        "semester": "Semester 6",
        "day": day,
        "schedule": [
            {"period": 1, "time": "09:00 AM - 10:00 AM", "subject": "Artificial Intelligence", "faculty": "Dr. K. Srinivas", "room": "CS-301"},
            {"period": 2, "time": "10:00 AM - 11:00 AM", "subject": "Data Mining & Warehousing", "faculty": "Prof. M. Rama Devi", "room": "CS-301"},
            {"period": 3, "time": "11:15 AM - 12:15 PM", "subject": "Web Technologies", "faculty": "Mr. P. V. Suresh", "room": "CS-301"},
            {"period": 4, "time": "01:00 PM - 02:00 PM", "subject": "Library / Seminar", "faculty": "Staff", "room": "Library"},
            {"period": 5, "time": "02:00 PM - 04:00 PM", "subject": "AI & ML Lab", "faculty": "Dr. K. Srinivas / Lab Asst", "room": "Lab-2"}
        ]
    }

