from typing import Dict, List, Any


ALL_TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    # Student Assistant Tools
    "get_my_student_profile": {
        "type": "function",
        "function": {
            "name": "get_my_student_profile",
            "description": "Fetch student profile details including name, roll number, department, semester, email, phone, and guardian info.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    "get_my_attendance_summary": {
        "type": "function",
        "function": {
            "name": "get_my_attendance_summary",
            "description": "Fetch student attendance percentage, total classes held/attended, subject breakdown, and exam eligibility status.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    "get_my_academic_marks": {
        "type": "function",
        "function": {
            "name": "get_my_academic_marks",
            "description": "Fetch academic grades, CGPA, SGPA, and subject grade breakdown for the authenticated student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "semester": {
                        "type": "string",
                        "description": "Optional semester filter, e.g., 'Semester 5' or 'latest'."
                    }
                },
                "required": []
            }
        }
    },
    "get_my_timetable": {
        "type": "function",
        "function": {
            "name": "get_my_timetable",
            "description": "Fetch the authenticated student's weekly timetable, daily class schedule, periods, subjects, assigned faculty, and room locations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "Optional day of the week filter, e.g., 'Monday', 'Tuesday', 'today'."
                    },
                    "semester": {
                        "type": "string",
                        "description": "Optional semester filter, e.g., 'Semester 6' or 'current'."
                    }
                },
                "required": []
            }
        }
    },
    "get_my_time_table": {
        "type": "function",
        "function": {
            "name": "get_my_time_table",
            "description": "Fetch the authenticated student's weekly timetable, daily class schedule, periods, subjects, assigned faculty, and room locations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "Optional day of the week filter, e.g., 'Monday', 'Tuesday', 'today'."
                    },
                    "semester": {
                        "type": "string",
                        "description": "Optional semester filter, e.g., 'Semester 6' or 'current'."
                    }
                },
                "required": []
            }
        }
    },

    # Fee Assistant Tools
    "get_my_fee_summary": {
        "type": "function",
        "function": {
            "name": "get_my_fee_summary",
            "description": "Fetch overall fee breakdown, total paid amount, balance due, and due date for the authenticated student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "academic_year": {
                        "type": "string",
                        "description": "Optional academic year string, e.g., '2025-2026' or 'current'."
                    }
                },
                "required": []
            }
        }
    },
    "get_my_pending_dues": {
        "type": "function",
        "function": {
            "name": "get_my_pending_dues",
            "description": "Fetch itemized pending dues list and due dates for the authenticated student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter, e.g., 'tuition', 'library', 'transport'."
                    }
                },
                "required": []
            }
        }
    },

    # Transport Assistant Tools
    "get_my_bus_details": {
        "type": "function",
        "function": {
            "name": "get_my_bus_details",
            "description": "Fetch assigned bus number, route name, seat number, driver contact, and pickup point timing.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    "get_my_route": {
        "type": "function",
        "function": {
            "name": "get_my_route",
            "description": "Fetch full transport route stop list and schedule timings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "route_id": {
                        "type": "string",
                        "description": "Optional route identifier."
                    }
                },
                "required": []
            }
        }
    }
}


def get_tool_schemas(allowed_tool_names: List[str]) -> List[Dict[str, Any]]:
    """
    Return list of OpenAPI/OpenRouter function schemas matching permitted tool names.
    Ensures strict enforcement: non-permitted tool schemas are omitted from LLM prompt context.
    """
    schemas = []
    for name in allowed_tool_names:
        if name in ALL_TOOL_SCHEMAS:
            schemas.append(ALL_TOOL_SCHEMAS[name])
    return schemas
