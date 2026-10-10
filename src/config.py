import os
from dataclasses import dataclass
from typing import Optional


class ConfigError(Exception):
    """Exception raised when configuration is invalid or missing."""
    pass


def load_env_file(filepath: str = ".env") -> None:
    """
    Parse a simple .env file manually into os.environ if present.
    Overwrites existing process environment variables so .env always takes priority.
    """
    if not os.path.exists(filepath):
        return
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key:
                        os.environ[key] = val
    except Exception:
        pass


@dataclass
class Config:
    api_key: str
    model: str
    provider: str = "openrouter"  # "openrouter" or "google_gemini"
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    timeout_seconds: int = 30
    max_history_messages: int = 10

    def __repr__(self) -> str:
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
        return (
            f"Config(provider='{self.provider}', model='{self.model}', base_url='{self.base_url}', "
            f"timeout={self.timeout_seconds}s, max_history={self.max_history_messages}, "
            f"api_key='{masked_key}')"
        )

    @classmethod
    def load(cls, env_path: Optional[str] = ".env") -> "Config":
        """Load configuration from environment variables and optional .env file."""
        if env_path:
            load_env_file(env_path)

        gemini_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        
        provider = "openrouter"
        api_key = ""
        model = ""
        base_url = ""

        # Priority 1: Direct Google Gemini API Key
        if gemini_key:
            provider = "google_gemini"
            api_key = gemini_key
            model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
            clean_model = model.replace("models/", "")
            base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent"
        # Priority 2: OpenRouter API Key
        elif openrouter_key:
            provider = "openrouter"
            api_key = openrouter_key
            model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free").strip()
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions").strip()
        else:
            raise ConfigError(
                "Missing required API key configuration. "
                "Please set GEMINI_API_KEY (from Google Developer Console / AI Studio) or OPENROUTER_API_KEY in your .env file."
            )

        timeout_str = os.getenv("REQUEST_TIMEOUT_SECONDS", "30").strip()
        max_history_str = os.getenv("MAX_HISTORY_MESSAGES", "10").strip()

        try:
            timeout_seconds = int(timeout_str)
        except ValueError:
            timeout_seconds = 30

        try:
            max_history_messages = int(max_history_str)
        except ValueError:
            max_history_messages = 10

        return cls(
            api_key=api_key,
            model=model,
            provider=provider,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_history_messages=max_history_messages
        )
