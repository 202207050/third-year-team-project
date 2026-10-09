import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.analyzers.base import AnalyzerError, AnalyzerResponseError, AnalyzerUnavailableError
from app.analyzers.gemini import GeminiNewsAnalyzer
from app.schemas import Article


class StubModels:
    def __init__(self, response_text=None, error=None):
        self.response_text = response_text
        self.error = error
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.response_text)


def result(article_id, label="NEUTRAL", confidence=0.8):
    return {
        "article_id": article_id,
        "sentiment": {"label": label, "confidence": confidence},
        "importance_score": 0.5,
    }


def analyzer_for(results):
    models = StubModels(json.dumps({"articles": results}))
    return GeminiNewsAnalyzer(api_key="test-key", client=SimpleNamespace(models=models)), models


@pytest.mark.parametrize("label", ["POSITIVE", "NEUTRAL", "NEGATIVE"])
def test_valid_sentiment_labels(label):
    analyzer, _ = analyzer_for([result("a", label)])
    output = analyzer.analyze([Article(article_id="a", title="Sample news")])
    assert output[0].sentiment.label.value == label
    assert output[0].sentiment.confidence == 0.8
    assert output[0].importance.score == 0.5
    assert output[0].importance.label.value == "MEDIUM"


def test_gemini_importance_score_maps_to_server_label():
    item = result("a", "NEGATIVE")
    item["importance_score"] = 0.70
    analyzer, _ = analyzer_for([item])
    output = analyzer.analyze([Article(article_id="a", title="Sample news")])
    assert output[0].importance.score == 0.70
    assert output[0].importance.label.value == "HIGH"


def test_batch_sentiment_analysis():
    analyzer, models = analyzer_for([result("a", "POSITIVE"), result("b", "NEGATIVE")])
    output = analyzer.analyze([
        Article(article_id="a", title="Results beat estimates"),
        Article(article_id="b", title="Large operating loss"),
    ])
    assert len(output) == 2
    assert len(models.calls) == 1
    config = models.calls[0]["config"].to_json_dict()
    assert config["response_mime_type"] == "application/json"
    assert "response_json_schema" in config


def test_article_id_mapping_preserves_request_order():
    analyzer, _ = analyzer_for([result("b", "NEGATIVE"), result("a", "POSITIVE")])
    output = analyzer.analyze([
        Article(article_id="a", title="Positive news"),
        Article(article_id="b", title="Negative news"),
    ])
    assert [(item.article_id, item.sentiment.label.value) for item in output] == [
        ("a", "POSITIVE"), ("b", "NEGATIVE"),
    ]


@pytest.mark.parametrize("results", [
    [result("a")],
    [result("a"), result("unknown")],
    [result("a"), result("a")],
])
def test_missing_unknown_or_duplicate_response_ids_fail(results):
    analyzer, _ = analyzer_for(results)
    with pytest.raises(AnalyzerResponseError):
        analyzer.analyze([
            Article(article_id="a", title="One"),
            Article(article_id="b", title="Two"),
        ])


def test_invalid_label_fails():
    analyzer, _ = analyzer_for([result("a", "BULLISH")])
    with pytest.raises(AnalyzerResponseError):
        analyzer.analyze([Article(article_id="a", title="Sample")])


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_invalid_confidence_fails(confidence):
    analyzer, _ = analyzer_for([result("a", confidence=confidence)])
    with pytest.raises(AnalyzerResponseError):
        analyzer.analyze([Article(article_id="a", title="Sample")])


def test_malformed_output_fails():
    models = StubModels("not-json")
    analyzer = GeminiNewsAnalyzer(api_key="test-key", client=SimpleNamespace(models=models))
    with pytest.raises(AnalyzerResponseError):
        analyzer.analyze([Article(article_id="a", title="Sample")])


def test_gemini_exception_is_an_error():
    models = StubModels(error=RuntimeError("private provider details"))
    analyzer = GeminiNewsAnalyzer(api_key="test-key", client=SimpleNamespace(models=models))
    with pytest.raises(AnalyzerError, match="Gemini sentiment request failed"):
        analyzer.analyze([Article(article_id="a", title="Sample")])


def test_api_key_missing_fails(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(AnalyzerUnavailableError):
        GeminiNewsAnalyzer()


def test_duplicate_request_ids_rejected():
    from app.schemas import NewsAnalysisRequest

    with pytest.raises(ValidationError):
        NewsAnalysisRequest(articles=[
            Article(article_id="a", title="One"),
            Article(article_id="a", title="Two"),
        ])
