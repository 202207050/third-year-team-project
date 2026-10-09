import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
DEFAULT_OPENAI_MODEL = "gpt-6-luna"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "none")


def get_gemini_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")


class InvalidAIProviderError(ValueError):
    """AI_PROVIDER must select one of the supported analyzers."""


def get_ai_provider() -> str:
    provider = os.getenv("AI_PROVIDER", "openai").strip().lower()
    if provider not in {"openai", "gemini"}:
        raise InvalidAIProviderError(
            "AI_PROVIDER must be either 'openai' or 'gemini'"
        )
    return provider


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")
