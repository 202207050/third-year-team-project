# Backend 인수인계

- Status: READY_FOR_BACKEND_INTEGRATION
- AI Implementation: COMPLETE
- Backend Work: REQUIRED

## 연결 제안

```text
Frontend → Backend /api/ai/news-analysis → AI_SERVER_URL/analyze/news
```

Backend endpoint 이름은 팀 규칙에 맞게 조정할 수 있습니다.

## 필요한 작업

- Frontend 요청을 AI Server의 request 형식으로 전달
- AI Server response를 Frontend에 전달
- timeout 및 AI Server `502` / `503`을 기존 Backend 인증·오류 정책에 맞춰 처리

현재 sentiment 기능 연결에 DB 저장은 필수가 아닙니다. 기존 `/recommend`, `/pattern` 구현과 직접 연결할 필요도 없습니다.

Request/response 형식과 오류 세부사항은 [공통 API 명세](news-sentiment-integration.md)를 참고하세요.
