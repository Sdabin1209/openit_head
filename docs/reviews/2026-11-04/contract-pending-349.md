# 계약 3.4.9 로 모아 낼 변경 (08:30 한 번에 — 고정 올림을 영역마다 반복하지 않으려고)

| # | 변경 | 찾은 곳 | 근거 |
|---|---|---|---|
| 1 | SurveyServiceEnv 에서 SURVEY_PUSH_ALLOW_PRIVATE_HOSTS 삭제 | survey-service 07:50 | 제품 설정의 시험용 문 금지(사설 주소 푸시 허용 = R3.18 SSRF 방지 우회). survey-service 코드는 이미 읽지 않음 |
| 2 | Exposure.schema.json auth `none` 설명: 영역의 /healthz·/readyz·/metrics 는 영역 게이트웨이 용이고 platform 공개 입구는 내보내지 않는다(CONVENTIONS 78행을 스키마 설명에 명시). 같은 (경로, 메서드)를 두 영역이 공개로 열면 공개 입구가 시작을 거부(종료 65)한다는 규칙도 PUBLIC_API/CONVENTIONS 13절에 | platform 07:58 | 규칙은 이미 CONVENTIONS 78·HTTP I1 에 있음 — 문구 보강(호환) |
