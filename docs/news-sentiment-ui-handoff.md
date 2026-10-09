# 뉴스 감성분석 UI 인수인계

- Status: READY_FOR_UI_IMPLEMENTATION
- AI Implementation: COMPLETE
- Frontend Integration: NOT STARTED

## 표시 위치와 배지

별도의 AI 분석 페이지를 추가하기보다 기존 종목 상세 화면의 뉴스 목록에 감성 배지를 작게 표시하는 방식을 권장합니다.

```text
[호재] 기업, 예상 상회 실적 발표
       경제신문 · 14:21

[중립] 정기 주주총회 개최 공시
       뉴스통신 · 11:03

[악재] 실적 전망 하향 발표
       경제신문 · 어제
```

| API label | 화면 배지 |
| --- | --- |
| `POSITIVE` | 호재 |
| `NEUTRAL` | 중립 |
| `NEGATIVE` | 악재 |

사용자 화면에는 enum 원문 대신 한국어 텍스트를 표시합니다. 기존 디자인 시스템을 우선하고, 색상만으로 의미를 전달하지 말고 배지에 텍스트를 함께 둡니다.

## 상태별 동작

- **분석 성공:** 결과가 있으면 호재·중립·악재 배지를 표시합니다.
- **결과 없음:** 뉴스는 그대로 보여 주고 배지는 생략합니다. `중립`으로 임의 대체하지 않습니다.
- **분석 중:** 뉴스 목록은 계속 사용할 수 있게 둡니다. 배지는 생략하거나 작은 로딩 표시만 사용합니다.
- **분석 실패:** 뉴스는 계속 보여 주고 배지는 숨깁니다. `NEGATIVE`나 `NEUTRAL`로 대체하지 않으며 뉴스 조회·클릭을 막지 않습니다.

## 매칭과 데이터

뉴스와 분석 결과는 배열 순서가 아니라 `article_id`로 연결합니다. UI에 필요한 기본 값은 `article_id`와 `sentiment.label`이며 `sentiment.confidence`는 개발·디버깅에만 선택적으로 활용할 수 있습니다.

`confidence`는 주가 상승·하락 확률이나 통계적으로 보정된 투자 확률이 아니라 모델의 분류 확신도이므로 일반 사용자 화면에서는 기본적으로 숨깁니다.

배지는 뉴스 제목보다 눈에 띄지 않게 두고 클릭을 방해하지 않도록 합니다. 별도 팝업을 강제하지 말고 기존 종목 탐색 흐름과 뉴스 사용을 유지합니다.

개발용 응답 예시는 [`docs/examples/news-sentiment-response.sample.json`](examples/news-sentiment-response.sample.json)에서 확인할 수 있습니다. 이 파일은 UI mock data이며 실제 API 호출 결과가 아닙니다.

공통 API 계약은 [뉴스 투자영향 감성분석 명세](news-sentiment-integration.md)를 참고하세요.
