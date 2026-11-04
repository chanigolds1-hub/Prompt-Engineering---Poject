import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Maximum time to wait for a Gemini response (milliseconds)
REQUEST_TIMEOUT_MS = 60_000


class GeminiServiceError(Exception):
    """Raised when Gemini cannot generate a response."""


class GeminiService:
    """
    Service responsible for communicating with Gemini.
    """

    def __init__(self, client: Any, model_name: str):
        if client is None:
            raise GeminiServiceError(
                "Gemini client is not configured."
            )

        if not model_name:
            raise GeminiServiceError(
                "Model name is missing."
            )

        self.client = client
        self.model_name = model_name

    @classmethod
    def from_environment(cls):
        """Create a Gemini service using environment variables."""

        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL")

        if not api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is missing."
            )

        if not model_name:
            raise GeminiServiceError(
                "GEMINI_MODEL is missing."
            )

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=REQUEST_TIMEOUT_MS
            )
        )

        return cls(
            client=client,
            model_name=model_name
        )

    def generate(
        self,
        system_prompt: str,
        user_request: str
    ) -> str:
        """Send a request to Gemini and return its response."""

        if not system_prompt.strip():
            raise ValueError(
                "System prompt cannot be empty."
            )

        if not user_request.strip():
            raise ValueError(
                "User request cannot be empty."
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_request,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0
                )
            )

            result = response.text

            if not result:
                raise GeminiServiceError(
                    "Gemini returned an empty response."
                )

            return result.strip()

        except GeminiServiceError:
            raise

        except Exception as error:
            raise GeminiServiceError(
                f"Gemini request failed: {error}"
            ) from error