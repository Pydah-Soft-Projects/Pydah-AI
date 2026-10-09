import json
import urllib.request
import urllib.error
from typing import List, Dict, Any
from src.config import Config


class LLMError(Exception):
    """Exception raised when OpenRouter communication fails."""
    pass


class LLMClient:
    """Client for interacting with OpenRouter LLM completion API."""

    def __init__(self, config: Config):
        self.config = config

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Send chat completion request to OpenRouter API and return generated text answer.

        :param messages: List of message objects with 'role' and 'content' keys.
        :return: Extracted answer string from assistant.
        :raises LLMError: If request fails, times out, or returns invalid response.
        """
        payload = {
            "model": self.config.model,
            "messages": messages
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pydahsoft.com",
            "X-Title": "Pydah AI Console"
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.config.base_url,
            data=data_bytes,
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                status_code = response.getcode()
                response_body = response.read().decode("utf-8")

                if status_code != 200:
                    raise LLMError(f"OpenRouter API returned HTTP status {status_code}.")

                return self._extract_content(response_body)

        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass

            if e.code == 401:
                raise LLMError("Authentication failed (HTTP 401). Please check your OPENROUTER_API_KEY.") from e
            elif e.code == 429:
                raise LLMError("Rate limit exceeded (HTTP 429). Please try again later or check your model limits.") from e
            elif e.code == 400:
                raise LLMError(f"Bad request sent to OpenRouter (HTTP 400): {self._parse_error_msg(error_body)}") from e
            elif e.code >= 500:
                raise LLMError(f"OpenRouter server error (HTTP {e.code}). Model or service may be temporarily unavailable.") from e
            else:
                raise LLMError(f"HTTP request failed with status {e.code}: {self._parse_error_msg(error_body)}") from e

        except urllib.error.URLError as e:
            raise LLMError(f"Network error while connecting to OpenRouter: {e.reason}") from e

        except TimeoutError as e:
            raise LLMError(f"Request timed out after {self.config.timeout_seconds} seconds.") from e

        except Exception as e:
            if isinstance(e, LLMError):
                raise e
            raise LLMError(f"An unexpected error occurred during LLM communication: {str(e)}") from e

    def _extract_content(self, response_json_str: str) -> str:
        """Parse raw JSON response from OpenRouter and extract content string."""
        try:
            data = json.loads(response_json_str)
            choices = data.get("choices", [])
            if not choices:
                raise LLMError("OpenRouter response contained no completion choices.")
            
            message = choices[0].get("message", {})
            content = message.get("content")

            if content is None:
                raise LLMError("OpenRouter response choice contains empty or null message content.")
            
            return content.strip()
        except json.JSONDecodeError as e:
            raise LLMError("Received invalid non-JSON response from OpenRouter API.") from e

    def _parse_error_msg(self, body_str: str) -> str:
        """Extract user-readable error message from OpenRouter error payload if present."""
        if not body_str:
            return "No additional error details provided."
        try:
            parsed = json.loads(body_str)
            if "error" in parsed and isinstance(parsed["error"], dict):
                return parsed["error"].get("message", body_str[:200])
            elif "message" in parsed:
                return str(parsed["message"])
        except Exception:
            pass
        return body_str[:200]
