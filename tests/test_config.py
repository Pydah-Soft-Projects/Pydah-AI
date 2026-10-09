import os
import unittest
from unittest.mock import patch
from src.config import Config, ConfigError


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_missing_api_key_raises_config_error(self):
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]

        with self.assertRaises(ConfigError) as ctx:
            Config.load(env_path=None)
        
        self.assertIn("OPENROUTER_API_KEY", str(ctx.exception))

    def test_valid_config_loading(self):
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test-key-1234567890"
        os.environ["OPENROUTER_MODEL"] = "meta-llama/llama-3.3-70b-instruct:free"

        config = Config.load(env_path=None)
        self.assertEqual(config.api_key, "sk-or-test-key-1234567890")
        self.assertEqual(config.model, "meta-llama/llama-3.3-70b-instruct:free")
        self.assertEqual(config.timeout_seconds, 30)

    def test_api_key_masked_in_repr(self):
        config = Config(api_key="secret-api-key-9999", model="test-model")
        repr_str = repr(config)
        self.assertNotIn("secret-api-key-9999", repr_str)
        self.assertIn("secr...9999", repr_str)


if __name__ == "__main__":
    unittest.main()
