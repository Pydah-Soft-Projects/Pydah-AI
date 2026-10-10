"""Assistant package initialization."""
from src.assistants.config import ASSISTANTS_CONFIG, AssistantConfig
from src.assistants.resolver import resolve_assistant

__all__ = ["ASSISTANTS_CONFIG", "AssistantConfig", "resolve_assistant"]
