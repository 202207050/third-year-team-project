"""Deterministic, test-only sentiment analyzer."""

from ..schemas import Article, ArticleAnalysis, Importance, Sentiment


class FakeAnalyzer:
    def analyze(self, articles: list[Article]) -> list[ArticleAnalysis]:
        return [
            ArticleAnalysis(
                article_id=article.article_id,
                sentiment=Sentiment(label="NEUTRAL", confidence=0.5),
                importance=Importance(score=0.5),
            )
            for article in articles
        ]
