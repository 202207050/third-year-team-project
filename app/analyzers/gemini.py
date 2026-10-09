import json
from typing import Any

from ..schemas import Article, ArticleAnalysis, NewsSentimentBatch
from ..settings import GEMINI_MODEL, get_gemini_api_key
from .base import AnalyzerError, AnalyzerResponseError, AnalyzerUnavailableError


def _build_prompt(articles: list[Article]) -> str:
    source_articles = [article.model_dump(mode="json") for article in articles]
    return (
        "Analyze the investment impact direction of each news article on its named "
        "company or market, not the emotional tone of its wording. POSITIVE means "
        "materially favorable expected impact, NEGATIVE means materially adverse "
        "expected impact, and NEUTRAL means unclear, balanced, or insufficient impact. "
        "Return exactly one result for every input article and copy each article_id "
        "exactly. Confidence must be between 0 and 1. Do not infer facts absent from "
        "the supplied text.\n\nArticles:\n"
        + json.dumps(source_articles, ensure_ascii=False)
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
                contents=_build_prompt(articles),
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
        return [by_id[article_id] for article_id in requested_ids]
