import unittest
from unittest.mock import MagicMock
from src.config import Config
from src.console import ConsoleApp, DEFAULT_SYSTEM_PROMPT
from src.llm_client import LLMClient


class TestConsoleApp(unittest.TestCase):

    def setUp(self):
        self.config = Config(
            api_key="sk-or-test-key",
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            max_history_messages=4
        )
        self.mock_llm_client = MagicMock(spec=LLMClient)
        self.app = ConsoleApp(self.config, llm_client=self.mock_llm_client)

    def test_initial_state_has_system_prompt(self):
        self.assertEqual(len(self.app.messages), 1)
        self.assertEqual(self.app.messages[0]["role"], "system")
        self.assertEqual(self.app.messages[0]["content"], DEFAULT_SYSTEM_PROMPT)

    def test_history_truncation(self):
        # Populate history with 6 messages (3 turns: user/assistant pairs)
        self.app.messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
            {"role": "user", "content": "Q3"},
            {"role": "assistant", "content": "A3"}
        ]

        truncated = self.app._truncate_history()
        # max_history_messages = 4, so truncated should have system prompt + last 4 messages
        self.assertEqual(len(truncated), 5)
        self.assertEqual(truncated[0]["role"], "system")
        self.assertEqual(truncated[1]["content"], "Q2")
        self.assertEqual(truncated[2]["content"], "A2")
        self.assertEqual(truncated[3]["content"], "Q3")
        self.assertEqual(truncated[4]["content"], "A3")


if __name__ == "__main__":
    unittest.main()
