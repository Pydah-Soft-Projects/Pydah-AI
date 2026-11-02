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
    "You are Nemo, a helpful, respectful, and intelligent AI assistant. "
    "Provide clear, accurate, and concise answers to user queries."
)

DEFAULT_FEE_SYSTEM_PROMPT = (
    "You are Nemo, the Fee Management Assistant. Your task is to assist students, "
    "parents, and administration with fee summaries, pending dues, receipt details, "
    "and payment deadlines. "
    "CRITICAL MANDATE: Whenever the user asks about fees, pending dues, or payment details, "
    "NEVER guess or reply conversationally. You MUST call the appropriate fee tool immediately "
    "to fetch real data before forming your answer. Be polite, professional, and clear with breakdown amounts."
)

DEFAULT_TRANSPORT_SYSTEM_PROMPT = (
    "You are Nemo, the Transport Assistant. Help students and staff check bus routes, "
    "pick-up/drop-off schedules, driver contact details, and vehicle status. "
    "CRITICAL MANDATE: Whenever the user asks about bus routes, pickup points, timings, or driver details, "
    "NEVER reply conversationally without data. You MUST call the appropriate transport tool immediately."
)

DEFAULT_STUDENT_SYSTEM_PROMPT = (
    "You are Nemo, the Portal Assistant. You assist authenticated users including students, "
    "faculty, and administrative staff. You have access to real-time tools provided by the portal backend. "
    "CRITICAL MANDATE: Whenever answering queries regarding user profiles, attendance, grades, "
    "class timetables, daily schedules, fees, student clubs, club members, club activities, faculty details, or institutional records, NEVER guess or reply conversationally without data. "
    "You MUST call the corresponding tool immediately to fetch authentic records before formulating your response. "
    "Format tabular breakdowns cleanly using markdown tables when multiple items or records are returned."
)


# Allowed tools list: wildcard '*' dynamically discovers and permits all tools from the portal backend
PORTAL_ALLOWED_TOOLS = ["*"]

STUDENT_ALLOWED_TOOLS = PORTAL_ALLOWED_TOOLS
FEE_ALLOWED_TOOLS = PORTAL_ALLOWED_TOOLS
TRANSPORT_ALLOWED_TOOLS = PORTAL_ALLOWED_TOOLS


ASSISTANTS_CONFIG: Dict[str, AssistantConfig] = {
    "general-assistant": AssistantConfig(
        id="general-assistant",
        name="Nemo Assistant",
        description="General institutional and portal assistant with tool execution access.",
        system_prompt=DEFAULT_STUDENT_SYSTEM_PROMPT,
        allowed_tools=["*"]
    ),
    "student-assistant": AssistantConfig(
        id="student-assistant",
        name="Nemo Portal & Student Assistant",
        description="Handles portal queries for students, faculty, and staff with real-time tool execution.",
        system_prompt=DEFAULT_STUDENT_SYSTEM_PROMPT,
        allowed_tools=STUDENT_ALLOWED_TOOLS
    ),
    "admin-assistant": AssistantConfig(
        id="admin-assistant",
        name="Nemo Admin Assistant",
        description="Handles administration queries, portal overview statistics, student records, and institutional data with real-time tool execution.",
        system_prompt=DEFAULT_STUDENT_SYSTEM_PROMPT,
        allowed_tools=STUDENT_ALLOWED_TOOLS
    ),
    "portal-assistant": AssistantConfig(
        id="portal-assistant",
        name="Nemo Portal & Student Assistant",
        description="Handles portal queries for students, faculty, and staff with real-time tool execution.",
        system_prompt=DEFAULT_STUDENT_SYSTEM_PROMPT,
        allowed_tools=STUDENT_ALLOWED_TOOLS
    ),
    "fee-assistant": AssistantConfig(
        id="fee-assistant",
        name="Nemo Fee Management Assistant",
        description="Handles student fee queries, pending dues, and payment statements.",
        system_prompt=DEFAULT_FEE_SYSTEM_PROMPT,
        allowed_tools=FEE_ALLOWED_TOOLS
    ),
    "transport-assistant": AssistantConfig(
        id="transport-assistant",
        name="Nemo Transport Assistant",
        description="Handles bus routes, pickup points, timings, and transport queries.",
        system_prompt=DEFAULT_TRANSPORT_SYSTEM_PROMPT,
        allowed_tools=TRANSPORT_ALLOWED_TOOLS
    )
}
