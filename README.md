# 뉴스 AI 분석 서버

뉴스 기사에 대한 투자영향 감성분석을 제공하는 독립 FastAPI 서비스입니다. 현재 구현 범위는 기사별 뉴스 투자영향
감성 분석(POSITIVE, NEUTRAL, NEGATIVE)입니다. 문장 감정이 아니라 해당 종목/시장에
미치는 투자 관점의 방향과 confidence를 분석합니다.

## API

`POST /analyze/news`는 `{"articles": [...]}`를 받고 같은 순서로
`{"articles": [...]}` 분석 결과를 반환합니다. 요청당 1~50개 기사입니다.
기사는 article_id, title이 필수이며 content, url, source, published_at,
symbol_code는 선택입니다. 응답은 기사별 article_id와 sentiment
{label, confidence}만 포함합니다. 요청당 모든 기사를 Gemini structured output
한 번으로 처리하며 응답 ID와 confidence를 검증합니다.

FakeAnalyzer는 deterministic 테스트 전용 fixture입니다. 기본 서버는
GeminiNewsAnalyzer를 사용하며 GEMINI_API_KEY가 없으면 HTTP 503, 분석 실패나
잘못된 응답은 HTTP 502로 반환합니다. 중요도, 유사도, 중복 그룹화는 이 기능 범위에
포함하지 않습니다.

## 실행 및 테스트

Python 3.12, 아래 명령은 저장소 루트에서 실행합니다.

`GEMINI_API_KEY`와 선택적인 `GEMINI_MODEL`은 환경변수 또는 로컬 `.env`에서
설정합니다. 기본 모델은 `gemini-3.6-flash`입니다. `.env`는 Git에서 제외됩니다.

```sh
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
python -m pytest tests
```

테스트는 SDK 호출 경계 mock/stub를 사용하며 네트워크나 API 키를 사용하지 않습니다.
입력 검증 실패는 422이며 분석 실패를 정상 결과로 대체하지 않습니다.

## Integration Docs

- [공통 API 명세](docs/news-sentiment-integration.md) — 요청·응답 계약과 현재 지원 범위
- [Frontend 인수인계](docs/frontend-handoff.md) — UI 표시와 호출 흐름
- [Backend 인수인계](docs/backend-handoff.md) — AI Server 연결 작업
