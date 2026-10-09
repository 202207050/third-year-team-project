# Frontend 인수인계

- Status: READY_FOR_FRONTEND_INTEGRATION
- AI Implementation: COMPLETE
- Frontend Work: REQUIRED

## 표시 규칙

| API label | UI 배지 |
| --- | --- |
| `POSITIVE` | 호재 |
| `NEUTRAL` | 중립 |
| `NEGATIVE` | 악재 |

새 AI 분석 페이지보다 기존 종목 상세 화면의 뉴스 목록에 작은 배지로 표시하는 방식을 권장합니다.

예: `[호재] 실적 예상 상회...` · `[중립] 정기 주주총회...` · `[악재] 실적 전망 하향...`

화면에 필요한 값은 `article_id`와 `sentiment.label`입니다. `confidence`는 주가 확률이 아니라 모델의 분류 확신도이므로 기본 UI에서는 숨기는 것을 권장합니다.

## 호출 흐름

`Frontend → Backend → AI Server` 구조를 권장합니다. Frontend가 AI Server를 직접 호출하지 않도록 Backend 연결 일정을 맞춰 주세요.

상세 계약은 [공통 API 명세](news-sentiment-integration.md)를 참고하세요.

UI 상태와 배지 동작은 [뉴스 감성분석 UI 가이드](news-sentiment-ui-handoff.md)를 참고하세요.
