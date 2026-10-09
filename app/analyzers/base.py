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
