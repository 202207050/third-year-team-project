import json
from types import SimpleNamespace

import httpx
import pytest
from openai import OpenAI

from app.analyzers.base import AnalyzerError, AnalyzerResponseError, AnalyzerUnavailableError
from app.analyzers.openai import OpenAINewsAnalyzer
from app.schemas import Article, ArticlePrediction, Importance, NewsSentimentBatch, Sentiment
from app.settings import DEFAULT_OPENAI_MODEL


class StubResponses:
    def __init__(self, parsed=None, error=None):
        self.parsed = parsed
        self.error = error
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(
            output_parsed=self.parsed,
            usage=SimpleNamespace(
                input_tokens=120,
                output_tokens=24,
                output_tokens_details=SimpleNamespace(reasoning_tokens=0),
            ),
        )


def prediction(article_id, label, score):
    return ArticlePrediction(
        article_id=article_id,
        sentiment=Sentiment(label=label, confidence=0.8),
        importance_score=score,
    )


def test_openai_structured_result_maps_importance_and_preserves_order():
    responses = StubResponses(NewsSentimentBatch(articles=[
        prediction("b", "NEGATIVE", 0.9),
        prediction("a", "POSITIVE", 0.2),
    ]))
    analyzer = OpenAINewsAnalyzer(
        api_key="test-key", client=SimpleNamespace(responses=responses),
    )
    output = analyzer.analyze([
        Article(article_id="a", title="Good news", content="Text", url="https://example.test/a"),
        Article(article_id="b", title="Bad news", content="Text"),
    ])

    assert [(item.article_id, item.sentiment.label.value, item.importance.score,
             item.importance.label.value) for item in output] == [
        ("a", "POSITIVE", 0.2, "LOW"), ("b", "NEGATIVE", 0.9, "HIGH"),
    ]
    call = responses.calls[0]
    assert len(responses.calls) == 1
    assert call["model"] == "gpt-6-luna"
    assert call["reasoning"] == {"effort": "none"}
    assert call["text_format"] is NewsSentimentBatch
    assert "example.test" not in call["input"]


def test_openai_response_and_request_errors_are_wrapped():
    analyzer = OpenAINewsAnalyzer(
        api_key="test-key", client=SimpleNamespace(responses=StubResponses(error=RuntimeError("provider"))),
    )
    with pytest.raises(AnalyzerError, match="OpenAI news analysis request failed"):
        analyzer.analyze([Article(article_id="a", title="News")])

    analyzer = OpenAINewsAnalyzer(
        api_key="test-key", client=SimpleNamespace(responses=StubResponses(parsed=None)),
    )
    with pytest.raises(AnalyzerResponseError):
        analyzer.analyze([Article(article_id="a", title="News")])


def test_openai_missing_key_is_unavailable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AnalyzerUnavailableError):
        OpenAINewsAnalyzer()


def test_openai_defaults_to_luna_none():
    from app.settings import OPENAI_MODEL, OPENAI_REASONING_EFFORT

    assert DEFAULT_OPENAI_MODEL == "gpt-6-luna"
    assert OPENAI_MODEL == "gpt-6-luna"
    assert OPENAI_REASONING_EFFORT == "none"


def test_openai_official_sdk_structured_output_request_without_network():
    payload = {"articles": [{
        "article_id": "a",
        "sentiment": {"label": "POSITIVE", "confidence": 0.8},
        "importance_score": 0.8,
    }]}
    captured = {}

    def handler(request):
        captured["body"] = request.read().decode("utf-8")
        return httpx.Response(200, json={
            "id": "resp_test", "object": "response", "created_at": 1,
            "status": "completed", "model": "gpt-6-luna",
            "output": [{
                "type": "message", "id": "msg_test", "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "annotations": [], "text": json.dumps(payload)}],
            }],
            "usage": {"input_tokens": 10, "output_tokens": 15,
                      "output_tokens_details": {"reasoning_tokens": 0}},
        })

    sdk_client = OpenAI(
        api_key="test-key", max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    analyzer = OpenAINewsAnalyzer(api_key="test-key", client=sdk_client)
    result = analyzer.analyze([Article(article_id="a", title="News")])[0]
    request_body = json.loads(captured["body"])
    assert result.importance == Importance(score=0.8)
    assert request_body["text"]["format"]["type"] == "json_schema"
    assert request_body["reasoning"]["effort"] == "none"
    sdk_client.close()
