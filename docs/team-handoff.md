# AI 서버 팀 인수인계

## 현재 구현 상태

- 뉴스 투자영향 방향(sentiment)과 기사별 중요도(importance)를 반환합니다.
- 기본 provider는 GPT-6 Luna이며 reasoning effort는 `none`입니다.
- Gemini는 대체 provider로 선택할 수 있습니다. 한 provider가 실패해도 다른 provider를 자동 호출하지 않습니다.
- Endpoint는 `POST /analyze/news`입니다.

## Request

```json
{
  "articles": [
    {
      "article_id": "news-001",
      "title": "회사 실적 발표",
      "content": "기사 본문"
    }
  ]
}
```

`article_id`와 `title`은 필수입니다. `content`, `url`, `source`, `published_at`(datetime), `symbol_code`는 선택입니다. 요청당 1~50건이며 `article_id`는 중복될 수 없습니다.

## Response

각 결과는 요청 순서에 맞춰 반환됩니다.

```json
{
  "articles": [
    {
      "article_id": "news-001",
      "sentiment": {"label": "POSITIVE", "confidence": 0.91},
      "importance": {"score": 0.82, "label": "HIGH"}
    }
  ]
}
```

sentiment label은 `POSITIVE`, `NEUTRAL`, `NEGATIVE`이며 투자 영향 방향을 뜻합니다. importance score는 0~1이고 `LOW`, `MEDIUM`, `HIGH` label은 서버 기준으로 계산합니다.

## UI 권장 표현

| API label | 화면 표시 |
| --- | --- |
| POSITIVE | 호재 |
| NEUTRAL | 중립 |
| NEGATIVE | 악재 |
| LOW | 낮음 |
| MEDIUM | 보통 |
| HIGH | 높음 |

뉴스 목록에 방향과 중요도를 badge로 표시하는 구성이 적절합니다. confidence는 일반 사용자 화면에 필수로 노출하지 않는 것을 권장합니다.

## Failure behavior

입력 검증 실패는 422, analyzer 설정이 없으면 503, 분석 또는 provider 초기화 실패는 502를 반환합니다. AI 분석 실패가 원본 뉴스의 표시를 막지 않도록 Backend와 Frontend에서 뉴스 표시와 분석 결과 표시를 분리해 주세요. 자동 provider 전환은 없습니다.

## Environment

변수명은 [.env.example](../.env.example)에 정리되어 있습니다.

- `AI_PROVIDER`: `openai` 또는 `gemini`, 기본값 `openai`
- `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_REASONING_EFFORT`
- `GEMINI_API_KEY`, `GEMINI_MODEL`

키 값은 이 문서에 포함하지 않습니다. 기본 OpenAI 모델은 `gpt-6-luna`, reasoning effort는 `none`, Gemini 모델은 `gemini-3.6-flash`입니다.

## Backend integration

Backend 코드는 이번 인수인계에서 수정하지 않았습니다. 현재 Backend 설정의 `AI_SERVER_URL` 기본값은 `http://localhost:8001`이고, AI router에는 `/recommend`, `/pattern` 등의 proxy 호출 경로와 공통 호출 함수가 있습니다. 뉴스 감성 분석을 연결하려면 Backend에 인증 및 요청 검증 정책에 맞는 proxy 경로를 추가해 이 서버의 `POST /analyze/news`를 호출해야 합니다. 해당 Backend 변경은 팀 작업입니다.

## Frontend integration

기존 뉴스 목록에서 감성 방향과 중요도를 badge로 보여주는 방식을 권장합니다. 별도 AI 페이지는 필수가 아닙니다. 분석 결과가 없거나 실패해도 뉴스 제목과 본문 등 원본 뉴스는 정상 표시해야 합니다.

## Validation evidence

아래는 초기 검증 결과이며 최종 정확도나 운영 성능을 의미하지 않습니다.

- Unit/regression tests: 55 passed
- GPT-6 Luna endpoint smoke test에서 POSITIVE/HIGH, NEUTRAL/LOW, NEGATIVE/HIGH 예시 응답 확인
- 초기 synthetic benchmark 12건: sentiment 12/12, importance 10/12, joint 10/12
- 초기 12건 처리 시간 약 4.83초, 추정 비용 약 `$0.0002903`
- Gemini 3.8 Flash low는 HTTP 503이 반복되어 같은 조건의 품질 비교를 완료하지 못함

## Known limitations

- Benchmark 표본은 12건으로 작습니다.
- 실제 운영 뉴스의 대규모 평가는 수행하지 않았습니다.
- Gemini 3.8의 품질 비교는 완료되지 않았습니다.
- provider 자동 fallback은 없습니다.

## Ownership / next team work

AI 모듈은 구현, 테스트, GPT-6 Luna endpoint smoke 검증을 마쳤습니다.

**TEAM_REQUEST**

- Backend: 인증된 뉴스 분석 proxy를 연결하고 `AI_SERVER_URL` 배포 설정을 확인해 주세요.
- Frontend: 기존 뉴스 목록에 방향/중요도 badge를 연결하고 분석 실패 시에도 뉴스 표시를 유지해 주세요.
- Deployment: 실행 환경에 `AI_PROVIDER`와 선택 provider의 키/모델 변수를 설정해 주세요. secret은 배포 secret 설정으로 관리해야 합니다.
