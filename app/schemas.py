from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Article(Schema):
    article_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str | None = None
    url: str | None = None
    source: str | None = None
    published_at: datetime | None = None
    symbol_code: str | None = None


class SentimentLabel(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class Sentiment(Schema):
    label: SentimentLabel
    confidence: float = Field(ge=0, le=1)


class ArticleAnalysis(Schema):
    article_id: str = Field(min_length=1)
    sentiment: Sentiment


class NewsSentimentBatch(Schema):
    articles: list[ArticleAnalysis]


class NewsAnalysisRequest(Schema):
    articles: list[Article] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def article_ids_are_unique(self):
        ids = [article.article_id for article in self.articles]
        if len(ids) != len(set(ids)):
            raise ValueError("article_id values must be unique within a request")
        return self


class NewsAnalysisResponse(Schema):
    articles: list[ArticleAnalysis]
