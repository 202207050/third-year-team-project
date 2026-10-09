import json
from typing import Protocol

from ..schemas import Article, ArticleAnalysis


class AnalyzerError(Exception):
    """A configured analyzer failed to return a valid analysis."""


class AnalyzerUnavailableError(AnalyzerError):
    """Required analyzer configuration is unavailable."""


class AnalyzerResponseError(AnalyzerError):
    """The analyzer response is malformed or does not match the request."""


class NewsAnalyzer(Protocol):
    def analyze(self, articles: list[Article]) -> list[ArticleAnalysis]:
        """Return validated results in input order, without masking invalid data."""
        ...


def build_news_analysis_prompt(
    articles: list[Article], *, minimal_input: bool = False
) -> str:
    if minimal_input:
        source_articles = [
            article.model_dump(mode="json", include={"article_id", "title", "content"})
            for article in articles
        ]
    else:
        source_articles = [article.model_dump(mode="json") for article in articles]
    return (
        "Analyze the investment impact direction of each news article on its named "
        "company or market, not the emotional tone of its wording. POSITIVE means "
        "materially favorable expected impact, NEGATIVE means materially adverse "
        "expected impact, and NEUTRAL means unclear, balanced, or insufficient impact. "
        "Importance is a separate axis: score how material the event is to an "
        "investment decision, regardless of its sentiment. A major loss can be "
        "NEGATIVE with high importance; a routine positive item can be POSITIVE with "
        "low importance. Return an importance_score from 0 to 1. Return exactly one "
        "result for every input article and copy each article_id exactly. Confidence "
        "must be between 0 and 1. Do not infer facts absent from the supplied text.\n\n"
        "Articles:\n" + json.dumps(source_articles, ensure_ascii=False)
    )
