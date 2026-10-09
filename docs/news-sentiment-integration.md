# 뉴스 투자영향 감성분석 API

- Status: READY_FOR_INTEGRATION
- Owner: AI
- Implementation: COMPLETE
- Backend Integration: NOT STARTED
- Frontend Integration: NOT STARTED

## 목적

뉴스 문장의 감정이 아니라 해당 뉴스가 종목 또는 시장에 미치는 투자 관점의 영향 방향을 분류합니다.

## Endpoint

`POST /analyze/news`

기사 1~50개를 한 번에 전달합니다. `article_id`와 `title`은 필수이며 나머지 필드는 선택입니다.

```json
{
  "articles": [
    {
      "article_id": "news-001",
      "title": "기업, 시장 예상 상회 실적 발표",
      "content": "..."
    }
  ]
}
```

선택 필드: `content`, `url`, `source`, `published_at`, `symbol_code`

응답의 기사 ID는 입력 ID와 연결됩니다.

```json
{
  "articles": [
    {
      "article_id": "news-001",
      "sentiment": {
        "label": "POSITIVE",
        "confidence": 0.95
      }
    }
  ]
}
```

## Label 의미

- `POSITIVE`: 투자 관점에서 유의미한 긍정 영향
- `NEUTRAL`: 방향이 불분명하거나 영향이 제한적이거나, 긍정·부정 요소가 상쇄됨
- `NEGATIVE`: 투자 관점에서 유의미한 부정 영향

`confidence`는 주가 상승·하락 확률이 아니라 sentiment 분류에 대한 모델의 확신도입니다. 일반 사용자 UI에는 기본적으로 표시하지 않는 것을 권장합니다.

## 오류와 설정

- `422`: 요청 형식, 필수 값, 기사 수 또는 중복 ID validation 실패
- `503`: analyzer를 사용할 수 없음 (예: API key 미설정)
- `502`: analyzer 초기화, Gemini 요청 또는 분석 응답 처리 실패

설정은 `GEMINI_API_KEY`와 선택 항목인 `GEMINI_MODEL` 환경변수로 전달합니다. 실제 값은 저장소나 문서에 포함하지 않습니다.

## 검증 및 범위

- 자동 테스트: 30 passed, 0 failed
- Gemini structured batch 호출: HTTP 200 확인
- 실제 결과에서 `POSITIVE`, `NEUTRAL`, `NEGATIVE` 반환 확인

현재 미구현: 중요도(`importance`), 기사 유사도(`similarity`), 중복 그룹화(`duplicate`), Backend 연결, Frontend 연결
