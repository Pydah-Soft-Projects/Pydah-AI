import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.api import app
from src.llm_client import LLMError


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "healthy")
        self.assertEqual(json_data.get("service"), "ai-core-service-api")

    @patch("src.api.LLMClient.generate_response")
    @patch("src.api.Config.load")
    def test_chat_completion_success(self, mock_config_load, mock_generate_response):
        mock_config = MagicMock()
        mock_config.model = "nvidia/nemotron-3.5-lightning:free"
        mock_config.max_history_messages = 10
        mock_config_load.return_value = mock_config

        mock_generate_response.return_value = "Artificial intelligence is a branch of computer science."

        payload = {
            "message": "What is artificial intelligence?",
            "conversation_id": "test-conv-123"
        }
        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("answer"), "Artificial intelligence is a branch of computer science.")
        self.assertEqual(data.get("model"), "nvidia/nemotron-3.5-lightning:free")
        self.assertEqual(data.get("conversation_id"), "test-conv-123")

    @patch("src.api.LLMClient.generate_response")
    @patch("src.api.Config.load")
    def test_chat_completion_llm_error(self, mock_config_load, mock_generate_response):
        mock_config = MagicMock()
        mock_config.model = "nvidia/nemotron-3.5-lightning:free"
        mock_config.max_history_messages = 10
        mock_config_load.return_value = mock_config

        mock_generate_response.side_effect = LLMError("Authentication failed (HTTP 401). Please check your OPENROUTER_API_KEY.")

        payload = {
            "message": "Hello"
        }
        response = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(response.status_code, 401)

        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error"), "LLM Provider Error")
        self.assertIn("Authentication failed", data.get("details", ""))


if __name__ == "__main__":
    unittest.main()
