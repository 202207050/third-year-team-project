import pytest

from app.settings import InvalidAIProviderError, get_ai_provider


def test_ai_provider_defaults_to_openai(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    assert get_ai_provider() == "openai"


@pytest.mark.parametrize("value", ["openai", "gemini", " GEMINI "])
def test_ai_provider_accepts_supported_values(monkeypatch, value):
    monkeypatch.setenv("AI_PROVIDER", value)
    assert get_ai_provider() == value.strip().lower()


@pytest.mark.parametrize("value", ["", "other", "local"])
def test_ai_provider_rejects_unsupported_values(monkeypatch, value):
    monkeypatch.setenv("AI_PROVIDER", value)
    with pytest.raises(InvalidAIProviderError, match="AI_PROVIDER"):
        get_ai_provider()
