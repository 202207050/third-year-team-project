from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


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


class ImportanceLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


def importance_label_for_score(score: float) -> ImportanceLabel:
    # Keep importance band boundaries in one place for every provider.
    if score < 0.35:
        return ImportanceLabel.LOW
    if score < 0.70:
        return ImportanceLabel.MEDIUM
    return ImportanceLabel.HIGH


class Importance(Schema):
    score: float = Field(ge=0, le=1)

    @computed_field
    @property
    def label(self) -> ImportanceLabel:
        return importance_label_for_score(self.score)


class ArticleAnalysis(Schema):
    article_id: str = Field(min_length=1)
    sentiment: Sentiment
    importance: Importance


class ArticlePrediction(Schema):
    article_id: str = Field(min_length=1)
    sentiment: Sentiment
    importance_score: float = Field(ge=0, le=1)


class NewsSentimentBatch(Schema):
    articles: list[ArticlePrediction]


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
