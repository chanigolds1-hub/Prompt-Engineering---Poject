import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from prompt_engineering_poject.gemini_service import (
    REQUEST_TIMEOUT_MS,
    GeminiService,
)


class TestGeminiService(unittest.TestCase):

    def setUp(self):
        self.client = Mock()
        self.client.models.generate_content.return_value = (
            SimpleNamespace(text="ipconfig")
        )

        self.service = GeminiService(
            client=self.client,
            model_name="test-model"
        )

    def test_generate_returns_response(self):
        result = self.service.generate(
            "You are a CMD agent",
            "What is my IP address?"
        )

        self.assertEqual(result, "ipconfig")

    def test_empty_request_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.generate("Prompt", "")

    def test_empty_prompt_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.generate("", "Show my IP")

    def test_client_is_created_with_timeout(self):
        env = {
            "GEMINI_API_KEY": "test-key",
            "GEMINI_MODEL": "test-model",
        }

        with (
            patch.dict("os.environ", env),
            patch(
                "prompt_engineering_poject.gemini_service.genai.Client"
            ) as client_class,
        ):
            GeminiService.from_environment()

        http_options = client_class.call_args.kwargs["http_options"]
        self.assertEqual(http_options.timeout, REQUEST_TIMEOUT_MS)


if __name__ == "__main__":
    unittest.main()