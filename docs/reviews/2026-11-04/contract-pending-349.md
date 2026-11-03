# 계약 3.4.9 로 모아 낼 변경 (08:30 한 번에 — 고정 올림을 영역마다 반복하지 않으려고)

| # | 변경 | 찾은 곳 | 근거 |
|---|---|---|---|
| 1 | SurveyServiceEnv 에서 SURVEY_PUSH_ALLOW_PRIVATE_HOSTS 삭제 | survey-service 07:50 | 제품 설정의 시험용 문 금지(사설 주소 푸시 허용 = R3.18 SSRF 방지 우회). survey-service 코드는 이미 읽지 않음 |
