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
    "and payment deadlines. Use approved tools to fetch real data when required. "
    "Be polite, professional, and clear with monetary breakdown amounts."
)

DEFAULT_TRANSPORT_SYSTEM_PROMPT = (
    "You are the Pydah Transport Assistant. Help students and staff check bus routes, "
    "pick-up/drop-off schedules, driver contact details, and vehicle status. "
    "Always rely on official transport tools for real-time information."
)

DEFAULT_STUDENT_SYSTEM_PROMPT = (
    "You are the Pydah Student Portal Assistant. Help authenticated students check "
    "their personal profile details, enrolled department/branch, attendance breakdown, "
    "grade reports, and academic standing using official student tools."
)


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
        allowed_tools=["get_my_student_profile", "get_my_attendance_summary", "get_my_academic_marks"]
    ),
    "fee-assistant": AssistantConfig(
        id="fee-assistant",
        name="Fee Management Assistant",
        description="Handles student fee queries, pending dues, and payment statements.",
        system_prompt=DEFAULT_FEE_SYSTEM_PROMPT,
        allowed_tools=["get_my_fee_summary", "get_my_pending_dues"]
    ),
    "transport-assistant": AssistantConfig(
        id="transport-assistant",
        name="Transport Assistant",
        description="Handles bus routes, pickup points, timings, and transport queries.",
        system_prompt=DEFAULT_TRANSPORT_SYSTEM_PROMPT,
        allowed_tools=["get_my_bus_details", "get_my_route"]
    )
}
