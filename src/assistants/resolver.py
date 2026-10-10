from typing import Optional
from src.assistants.config import ASSISTANTS_CONFIG, AssistantConfig


def resolve_assistant(assistant_id: Optional[str] = None) -> AssistantConfig:
    """
    Resolve requested assistant_id against configured registry.
    Falls back gracefully to 'general-assistant' if assistant_id is unknown or omitted.
    """
    if not assistant_id:
        return ASSISTANTS_CONFIG["general-assistant"]

    clean_id = assistant_id.strip().lower()
    if clean_id in ASSISTANTS_CONFIG:
        return ASSISTANTS_CONFIG[clean_id]

    return ASSISTANTS_CONFIG["general-assistant"]
