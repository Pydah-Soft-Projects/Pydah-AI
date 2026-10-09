import os
from dataclasses import dataclass
from typing import Optional


class ConfigError(Exception):
    """Exception raised when configuration is invalid or missing."""
    pass


def load_env_file(filepath: str = ".env") -> None:
    """
    Parse a simple .env file manually into os.environ if present.
    Will not overwrite existing environment variables.
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
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception:
        # Ignore issues reading .env file gracefully
        pass


@dataclass
class Config:
    api_key: str
    model: str
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    timeout_seconds: int = 30
    max_history_messages: int = 10

    def __repr__(self) -> str:
        # Safely hide API key in string representation
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
        return (
            f"Config(model='{self.model}', base_url='{self.base_url}', "
            f"timeout={self.timeout_seconds}s, max_history={self.max_history_messages}, "
            f"api_key='{masked_key}')"
        )

    @classmethod
    def load(cls, env_path: Optional[str] = ".env") -> "Config":
        """Load configuration from environment variables and optional .env file."""
        if env_path:
            load_env_file(env_path)

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free").strip()
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions").strip()
        
        timeout_str = os.getenv("REQUEST_TIMEOUT_SECONDS", "30").strip()
        max_history_str = os.getenv("MAX_HISTORY_MESSAGES", "10").strip()

        if not api_key:
            raise ConfigError(
                "Missing required configuration: 'OPENROUTER_API_KEY'. "
                "Please set OPENROUTER_API_KEY in your environment or .env file."
            )

        if not model:
            raise ConfigError(
                "Missing required configuration: 'OPENROUTER_MODEL'. "
                "Please set OPENROUTER_MODEL in your environment or .env file."
            )

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
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_history_messages=max_history_messages
        )
