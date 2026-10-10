import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from src.config import Config


class LLMError(Exception):
    """Exception raised when LLM communication fails."""
    pass


class LLMClient:
    """Unified Client supporting both OpenRouter API and Direct Google Gemini API."""

    def __init__(self, config: Config):
        self.config = config

    def generate_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to configured LLM Provider (Google Gemini Direct or OpenRouter).
        Returns normalized message dict: {"role": "assistant", "content": "...", "tool_calls": [...]}
        """
        if self.config.provider == "google_gemini":
            return self._generate_google_gemini_completion(messages, tools)
        else:
            return self._generate_openrouter_completion(messages, tools)

    def _generate_openrouter_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pydahsoft.com",
            "X-Title": "Pydah AI Engine"
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
                return self._extract_openrouter_choice(response_body)

        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            raise LLMError(f"OpenRouter API HTTP {e.code}: {self._parse_error_msg(error_body)}") from e
        except Exception as e:
            raise LLMError(f"OpenRouter communication error: {str(e)}") from e

    def _generate_google_gemini_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Direct Native Google Gemini API Adapter (Google AI Studio / Developer Console API Key).
        URL: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}
        """
        endpoint = f"{self.config.base_url}?key={self.config.api_key}"

        system_instruction = None
        gemini_contents = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            elif role in ("user", "human"):
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == "assistant":
                parts = []
                if content:
                    parts.append({"text": content})
                if msg.get("tool_calls"):
                    for call in msg["tool_calls"]:
                        fn = call.get("function", {})
                        parts.append({
                            "functionCall": {
                                "name": fn.get("name"),
                                "args": json.loads(fn.get("arguments", "{}")) if isinstance(fn.get("arguments"), str) else fn.get("arguments", {})
                            }
                        })
                if parts:
                    gemini_contents.append({"role": "model", "parts": parts})
            elif role == "tool":
                # Convert tool output message to Gemini functionResponse
                tool_name = msg.get("name", "tool")
                try:
                    resp_dict = json.loads(content) if isinstance(content, str) else content
                except Exception:
                    resp_dict = {"output": content}

                gemini_contents.append({
                    "role": "function",
                    "parts": [{
                        "functionResponse": {
                            "name": tool_name,
                            "response": resp_dict
                        }
                    }]
                })

        payload: Dict[str, Any] = {"contents": gemini_contents}

        if system_instruction:
            payload["systemInstruction"] = system_instruction

        if tools:
            function_declarations = []
            for t in tools:
                fn = t.get("function", {})
                function_declarations.append({
                    "name": fn.get("name"),
                    "description": fn.get("description", ""),
                    "parameters": fn.get("parameters", {"type": "object", "properties": {}})
                })
            payload["tools"] = [{"functionDeclarations": function_declarations}]

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                status_code = response.getcode()
                response_body = response.read().decode("utf-8")
                if status_code != 200:
                    raise LLMError(f"Google Gemini API returned HTTP status {status_code}.")
                return self._extract_gemini_choice(response_body)

        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            raise LLMError(f"Google Gemini API HTTP {e.code}: {self._parse_error_msg(error_body)}") from e
        except Exception as e:
            raise LLMError(f"Google Gemini communication error: {str(e)}") from e

    def _extract_openrouter_choice(self, response_json_str: str) -> Dict[str, Any]:
        data = json.loads(response_json_str)
        choices = data.get("choices", [])
        if not choices:
            raise LLMError("OpenRouter response contained no completion choices.")
        return choices[0].get("message", {})

    def _extract_gemini_choice(self, response_json_str: str) -> Dict[str, Any]:
        """Normalize Google Gemini response payload into OpenAI/OpenRouter message dict format."""
        data = json.loads(response_json_str)
        candidates = data.get("candidates", [])
        if not candidates:
            raise LLMError("Google Gemini response contained no candidates.")

        candidate = candidates[0]
        content_obj = candidate.get("content", {})
        parts = content_obj.get("parts", [])

        text_content = ""
        tool_calls = []

        for idx, part in enumerate(parts):
            if "text" in part:
                text_content += part["text"]
            elif "functionCall" in part:
                fn_call = part["functionCall"]
                tool_calls.append({
                    "id": f"call_gemini_{idx}",
                    "type": "function",
                    "function": {
                        "name": fn_call.get("name"),
                        "arguments": json.dumps(fn_call.get("args", {}))
                    }
                })

        result_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": text_content.strip()
        }

        if tool_calls:
            result_msg["tool_calls"] = tool_calls

        return result_msg

    def generate_response(self, messages: List[Dict[str, Any]]) -> str:
        msg_choice = self.generate_completion(messages)
        content = msg_choice.get("content")
        return (content or "").strip()

    def _parse_error_msg(self, body_str: str) -> str:
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
