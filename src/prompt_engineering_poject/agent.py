from pathlib import Path

from .gemini_service import GeminiService


# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Location of the prompt file
PROMPT_PATH = PROJECT_ROOT / "prompts" / "prompt_v1.txt"


def load_prompt() -> str:
    """Load the prompt instructions from a text file."""

    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_command(
    user_request: str,
    service: GeminiService = None
) -> str:
    """Generate a CMD command using an AI model."""

    if not user_request or not user_request.strip():
        raise ValueError("Please enter a request.")

    # Load the prompt
    system_prompt = load_prompt()

    # Create the Gemini service if one was not provided
    if service is None:
        service = GeminiService.from_environment()

    # Send the prompt and user request to the AI
    response = service.generate(
        system_prompt,
        user_request
    )

    return response.strip()