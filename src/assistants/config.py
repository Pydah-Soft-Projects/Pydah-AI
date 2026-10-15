from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AssistantConfig:
    """Definition and scope boundaries for an AI Assistant persona."""
    id: str
    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str] = field(default_factory=list)


DEFAULT_GENERAL_SYSTEM_PROMPT = (
    "You are Pydah AI, a helpful, respectful, and intelligent AI assistant. "
    "Provide clear, accurate, and concise answers to user queries."
)

DEFAULT_FEE_SYSTEM_PROMPT = (
    "You are the Pydah Fee Management Assistant. Your task is to assist students, "
    "parents, and administration with fee summaries, pending dues, receipt details, "
    "and payment deadlines. "
    "CRITICAL MANDATE: Whenever the user asks about fees, pending dues, or payment details, "
    "NEVER guess or reply conversationally. You MUST call the appropriate fee tool immediately "
    "to fetch real data before forming your answer. Be polite, professional, and clear with breakdown amounts."
)

DEFAULT_TRANSPORT_SYSTEM_PROMPT = (
    "You are the Pydah Transport Assistant. Help students and staff check bus routes, "
    "pick-up/drop-off schedules, driver contact details, and vehicle status. "
    "CRITICAL MANDATE: Whenever the user asks about bus routes, pickup points, timings, or driver details, "
    "NEVER reply conversationally without data. You MUST call the appropriate transport tool immediately."
)

DEFAULT_STUDENT_SYSTEM_PROMPT = (
    "You are the Pydah Student Portal Assistant. Help authenticated students check "
    "their personal profile details, enrolled department/branch, attendance breakdown, "
    "grade reports, class timetable / daily schedule, and academic standing. "
    "CRITICAL MANDATE: Whenever the user asks for their name, who they are, profile, roll number, "
    "attendance percentage, academic grades, or class timetable / schedule, NEVER guess or reply conversationally. "
    "You MUST call the corresponding student tool immediately to fetch their official records."
)


# Allowed tools list including standard names and common aliases
STUDENT_ALLOWED_TOOLS = [
    "get_my_student_profile", "get_student_profile", "get_my_profile", "get_profile",
    "fetch_student_profile", "student_profile", "get_user_profile", "get_student_details", "get_my_details",
    "get_my_attendance_summary", "get_student_attendance", "get_my_attendance", "get_attendance",
    "fetch_attendance", "student_attendance", "get_attendance_summary",
    "get_my_academic_marks", "get_student_marks", "get_my_marks", "get_marks",
    "get_internal_marks", "get_grades", "get_academic_performance", "student_marks",
    "get_my_timetable", "get_my_time_table", "get_student_timetable", "get_timetable",
    "get_time_table", "fetch_timetable", "student_timetable", "get_class_schedule", "get_schedule"
]

FEE_ALLOWED_TOOLS = [
    "get_my_fee_summary", "get_my_pending_dues", "get_student_fees", "get_my_fees",
    "get_pending_dues", "get_fee_details", "get_fees", "fetch_pending_dues", "student_fees"
]

TRANSPORT_ALLOWED_TOOLS = [
    "get_my_bus_details", "get_my_route", "get_student_transport", "get_my_transport",
    "get_transport", "student_transport"
]


ASSISTANTS_CONFIG: Dict[str, AssistantConfig] = {
    "general-assistant": AssistantConfig(
        id="general-assistant",
        name="Pydah AI General Assistant",
        description="General assistant for institution queries and overall guidance.",
        system_prompt=DEFAULT_GENERAL_SYSTEM_PROMPT,
        allowed_tools=[]
    ),
    "student-assistant": AssistantConfig(
        id="student-assistant",
        name="Student Portal Assistant",
        description="Handles student profile details, attendance records, and academic grade summaries.",
        system_prompt=DEFAULT_STUDENT_SYSTEM_PROMPT,
        allowed_tools=STUDENT_ALLOWED_TOOLS
    ),
    "fee-assistant": AssistantConfig(
        id="fee-assistant",
        name="Fee Management Assistant",
        description="Handles student fee queries, pending dues, and payment statements.",
        system_prompt=DEFAULT_FEE_SYSTEM_PROMPT,
        allowed_tools=FEE_ALLOWED_TOOLS
    ),
    "transport-assistant": AssistantConfig(
        id="transport-assistant",
        name="Transport Assistant",
        description="Handles bus routes, pickup points, timings, and transport queries.",
        system_prompt=DEFAULT_TRANSPORT_SYSTEM_PROMPT,
        allowed_tools=TRANSPORT_ALLOWED_TOOLS
    )
}
