from fastapi import Depends, FastAPI, HTTPException

from .analyzers.base import AnalyzerError, AnalyzerUnavailableError, NewsAnalyzer
from .analyzers.gemini import GeminiNewsAnalyzer
from .schemas import NewsAnalysisRequest, NewsAnalysisResponse


def get_analyzer() -> NewsAnalyzer:
    try:
        return GeminiNewsAnalyzer()
    except AnalyzerUnavailableError as exc:
        raise HTTPException(status_code=503, detail="News analyzer unavailable") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="News analyzer initialization failed") from exc


app = FastAPI(title="News AI Analysis")


@app.post("/analyze/news", response_model=NewsAnalysisResponse)
def analyze_news(
    request: NewsAnalysisRequest,
    analyzer: NewsAnalyzer = Depends(get_analyzer),
) -> NewsAnalysisResponse:
    try:
        return NewsAnalysisResponse(articles=analyzer.analyze(request.articles))
    except AnalyzerError as exc:
        raise HTTPException(status_code=502, detail="News analysis failed") from exc
