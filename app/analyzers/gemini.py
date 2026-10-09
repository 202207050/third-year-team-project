from typing import Any

from ..schemas import Article, ArticleAnalysis, Importance, NewsSentimentBatch
from ..settings import GEMINI_MODEL, get_gemini_api_key
from .base import (
    AnalyzerError,
    AnalyzerResponseError,
    AnalyzerUnavailableError,
    build_news_analysis_prompt,
)


class GeminiNewsAnalyzer:
    """One structured Gemini request per batch of articles."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = GEMINI_MODEL,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else get_gemini_api_key()
        if not self._api_key:
            raise AnalyzerUnavailableError("GEMINI_API_KEY is not configured")
        self._model = model
        if client is None:
            from google import genai

            client = genai.Client(api_key=self._api_key)
        self._client = client

    def analyze(self, articles: list[Article]) -> list[ArticleAnalysis]:
        from google.genai import types

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=build_news_analysis_prompt(articles),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=NewsSentimentBatch.model_json_schema(),
                    temperature=0,
                ),
            )
        except Exception as exc:
            raise AnalyzerError("Gemini sentiment request failed") from exc

        raw = getattr(response, "text", None)
        if not isinstance(raw, str) or not raw.strip():
            raise AnalyzerResponseError("Gemini returned an empty response")
        try:
            batch = NewsSentimentBatch.model_validate_json(raw)
        except Exception as exc:
            raise AnalyzerResponseError("Gemini returned an invalid sentiment response") from exc

        requested_ids = [article.article_id for article in articles]
        returned_ids = [result.article_id for result in batch.articles]
        if len(returned_ids) != len(set(returned_ids)):
            raise AnalyzerResponseError("Gemini returned duplicate article_id values")
        if set(returned_ids) != set(requested_ids) or len(returned_ids) != len(requested_ids):
            raise AnalyzerResponseError("Gemini response article_id values do not match request")

        by_id = {result.article_id: result for result in batch.articles}
        return [
            ArticleAnalysis(
                article_id=article_id,
                sentiment=by_id[article_id].sentiment,
                importance=Importance(score=by_id[article_id].importance_score),
            )
            for article_id in requested_ids
        ]
