import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.analyzers.fake import FakeAnalyzer
from app.main import app, get_analyzer
from app.schemas import Sentiment


@pytest.fixture
def client():
    app.dependency_overrides[get_analyzer] = lambda: FakeAnalyzer()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_single_article(client):
    response = client.post("/analyze/news", json={
        "articles": [{"article_id": "a", "title": "Earnings"}],
    })
    assert response.status_code == 200
    result = response.json()["articles"][0]
    assert result["article_id"] == "a"
    assert result["sentiment"] == {"label": "NEUTRAL", "confidence": 0.5}
    assert set(result) == {"article_id", "sentiment"}


def test_multiple_articles_deterministic(client):
    payload = {"articles": [
        {"article_id": "a", "title": "Earnings"},
        {"article_id": "b", "title": "Merger"},
    ]}
    first = client.post("/analyze/news", json=payload)
    assert first.status_code == 200
    assert [a["article_id"] for a in first.json()["articles"]] == ["a", "b"]
    assert first.json() == client.post("/analyze/news", json=payload).json()


@pytest.mark.parametrize("field", ["title", "article_id"])
@pytest.mark.parametrize("value", ["", "   "])
def test_blank_fields_rejected(client, field, value):
    article = {"article_id": "a", "title": "Earnings", field: value}
    assert client.post("/analyze/news", json={"articles": [article]}).status_code == 422


@pytest.mark.parametrize("count", [0, 51])
def test_article_count_limit(client, count):
    articles = [{"article_id": str(i), "title": "Earnings"} for i in range(count)]
    assert client.post("/analyze/news", json={"articles": articles}).status_code == 422


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_confidence_range(confidence):
    with pytest.raises(ValidationError):
        Sentiment(label="NEUTRAL", confidence=confidence)


@pytest.mark.parametrize("confidence", [-1, 2])
def test_sentiment_confidence_rejects_out_of_range(confidence):
    with pytest.raises(ValidationError):
        Sentiment(label="NEUTRAL", confidence=confidence)


def test_enum_validation():
    with pytest.raises(ValidationError):
        Sentiment(label="UNKNOWN", confidence=0.5)


def test_response_contains_only_implemented_sentiment_fields(client):
    response = client.post("/analyze/news", json={"articles": [
        {"article_id": "a", "title": "Earnings", "content": "Revenue"},
        {"article_id": "b", "title": "Earnings", "content": "Revenue"},
        {"article_id": "c", "title": "Earnings", "content": "New guidance"},
    ]})
    assert response.status_code == 200
    results = response.json()["articles"]
    assert len(results) == 3
    assert all(set(item) == {"article_id", "sentiment"} for item in results)


def test_analyzer_unavailable(monkeypatch):
    import app.analyzers.gemini as gemini_module

    monkeypatch.setattr(gemini_module, "get_gemini_api_key", lambda: None)
    with TestClient(app) as client:
        response = client.post("/analyze/news", json={
            "articles": [{"article_id": "a", "title": "Earnings"}],
        })
    assert response.status_code == 503
    assert response.json() == {"detail": "News analyzer unavailable"}
