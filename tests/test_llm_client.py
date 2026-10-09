import json
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

from src.config import Config
from src.llm_client import LLMClient, LLMError


class TestLLMClient(unittest.TestCase):

    def setUp(self):
        self.config = Config(
            api_key="sk-or-test-key-mock",
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            timeout_seconds=5
        )
        self.client = LLMClient(self.config)

    @patch("urllib.request.urlopen")
    def test_successful_response(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_body = json.dumps({
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Artificial Intelligence is the simulation of human intelligence by machines."
                    }
                }
            ]
        }).encode("utf-8")
        mock_response.read.return_value = mock_response_body
        mock_urlopen.return_value.__enter__.return_value = mock_response

        messages = [{"role": "user", "content": "What is AI?"}]
        answer = self.client.generate_response(messages)
        self.assertEqual(answer, "Artificial Intelligence is the simulation of human intelligence by machines.")

    @patch("urllib.request.urlopen")
    def test_http_401_unauthorized(self, mock_urlopen):
        error_resp = MagicMock()
        error_resp.read.return_value = b'{"error": {"message": "Invalid API Key"}}'
        http_error = urllib.error.HTTPError(
            url=self.config.base_url,
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=error_resp
        )
        mock_urlopen.side_effect = http_error

        messages = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(LLMError) as ctx:
            self.client.generate_response(messages)
        self.assertIn("Authentication failed", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_http_429_rate_limit(self, mock_urlopen):
        error_resp = MagicMock()
        error_resp.read.return_value = b'{"error": {"message": "Rate limit reached"}}'
        http_error = urllib.error.HTTPError(
            url=self.config.base_url,
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=error_resp
        )
        mock_urlopen.side_effect = http_error

        messages = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(LLMError) as ctx:
            self.client.generate_response(messages)
        self.assertIn("Rate limit exceeded", str(ctx.exception))

    @patch("urllib.request.urlopen")
    def test_timeout_error(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError()

        messages = [{"role": "user", "content": "Hello"}]
        with self.assertRaises(LLMError) as ctx:
            self.client.generate_response(messages)
        self.assertIn("timed out", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
