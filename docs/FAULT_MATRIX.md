# 장애 경우의 수 닫힌 목록 (FAULT_MATRIX)

> 작성: 헤드 조사 담당(읽기 전용 조사). 초안 2026-10-28, **같은 날 구현·시험 반영 갱신**. 상태: 헤드 검토 전. 증명이 아니라 '닫힌 목록'이다: 찾은 간선 41개와 각 간선의 장애 방식 칸을 모두 나열하고 칸마다 기대 동작 정의 여부와 시험 여부를 적는다. 목록에 없는 간선이 있을 수 있다(2절의 검색 방법으로 누구나 다시 찾아 보태라).

**읽는 법 (두 글자 코드).** 앞 글자 = 기대 동작이 영역 문서에 정의되어 있는가. 뒤 글자 = 시험 근거.

| 코드 | 뜻 |
| --- | --- |
| D | 기대 동작이 영역 문서(boundary/design/runbook/HTTP.md, deploy의 E2E.md·Caddyfile 주석 포함)에 정의되어 있다 |
| P | 부분 정의: 코드나 단위 시험으로 동작은 보이나 영역 문서에는 없거나 일부만 있다 |
| ? | **기대 동작 미정의**: 문서에서 찾지 못했다(이 문서가 찾은 가장 중요한 빈칸) |
| E | deploy E2E(`scripts/e2e_steps.py`, `e2e.sh`)가 그 장애를 일으켜 확인한다 |
| U | 영역 단위 시험만 있다(영역 `tests/`, mock·가짜 서버 포함). 실제 컨테이너 조합에서는 안 해 봄 |
| N | 안 함: 시험 근거를 찾지 못했다 |
| -- | 해당 없음(이유는 3절 간선 설명) |
| `*` (E 뒤) | **두 환경 확인**: 오늘(2026-10-28) 이 PC(02:56, deploy f8c2649)와 gpu-dev(02:48, deploy 7355791)의 전체 모드 E2E가 모두 실패 0으로 끝났고(수치는 정본 `deploy/docs/E2E_RESULTS.md`), 해당 단계(5, 5p, 5q, 5w, 5f, 5r, 7, 9)가 두 로그에서 모두 REAL/PASS였다. 정본 `deploy/docs/E2E_RESULTS.md` |

**주의 1.** 시험 코드는 '그 시험이 저장소에 있는가'를 뜻한다. E 칸의 통과는 위 정본과 두 환경의 로그(둘 다 FAIL 0, POLICY-PENDING 0. 수치는 정본)로 확인했다. **U 칸의 통과는 이 조사에서 실행하지 않았다**(시험 파일과 영역 문서를 읽었을 뿐이다). **주의 2.** 'E'로 표시한 칸도 보는 범위가 좁을 수 있다. 예: 5p는 postgres를 stop하지 pause하지 않고, 환자 턴은 위험 신호가 없는 발화 하나다. 한계는 3절 설명에 적었다. **주의 3.** 두 환경 확인은 E 칸에 한정된다. U 칸 중 영역 문서가 '이 PC에서 측정'이라고만 적은 것(DB 대기 상한 4개 영역)은 한 환경 확인이다(아래 별도 표). **주의 4.** 두 환경의 E2E는 fake 모델 백엔드이고 두 로그의 deploy 커밋이 다르다(7355791, f8c2649: 뒤의 것은 E2E 기록 문서 커밋으로 읽었으나 diff를 열어 보지 않았다). **주의 5.** 조사 도중(03:10) 다른 세션이 `deploy/scripts/e2e_steps.py`를 수정 중이었다(미커밋, 단계 2를 import 모드로 바꾸는 변경으로 읽음, 실패 주입 단계 5q·5w·5p는 건드리지 않음). 그래서 이 파일은 `e2e_steps.py`를 줄 번호가 아니라 함수 이름으로 인용하고, E 칸의 근거는 위 두 환경의 실행 로그(그 변경 이전)다. 다른 파일의 줄 번호는 2026-10-28 03:14 작업 트리 기준이다.

장애 방식: F1 중지(연결 거부), F2 멈춤(연결은 되나 무응답), F3 느림, F4 재시작, F5 5xx 응답, F6 잘못된/깨진 응답 본문, F7 인증 실패(401/403), F8 네트워크 분리. 볼륨·정적 파일처럼 네트워크 호출이 아닌 간선은 해당 없는 칸에 이유를 적었다.

## 1. 요약 (분모 명시)

**이전(초안) 대비.** 이전 값은 초안 작성 시점(칸 267개)의 같은 파일에서 센 것이다.

| 항목 | 이전 초안 | 지금 | 변화 |
| --- | --- | --- | --- |
| 간선 | 40 | 41 | +1 |
| 칸(간선 x 8) | 320 | 328 | +8 |
| 해당 없음 | 53 | 60 | +7 |
| **해당 있는 칸(분모)** | 267 | 268 | +1 |
| 기대 D (정의됨) | 119 | 140 | +21 |
| 기대 P (부분) | 59 | 65 | +6 |
| 기대 ? (미정의) | 89 | 63 | -26 |
| 시험 E (E2E) | 26 | 31 | +5 |
| 시험 U (영역 단위만) | 85 | 107 | +22 |
| 시험 N (안 함) | 156 | 130 | -26 |

- 간선 41개 x 장애 방식 8 = **328칸**. 그중 해당 없음 60칸, **해당 있는 칸 268**(이하 비율의 분모). 분모가 267에서 268으로 1 늘었다(신규 간선 G8의 F1 한 칸).
- **재집계(헤드 문서 정리, 2026-10-28 3차 점검 뒤).** 3절 행렬의 실제 칸을 다시 세었다(41행 x 8 = 328칸; 해당 없음 `--` 60, 해당 있음 268). 결과는 위 표·아래 줄과 모두 같다(어긋남 없음). 한 칸 안의 상태를 세 가지로 묶어 적는다.
  - **확인(시험으로 통과를 본 칸, 코드 E)**: 268칸 중 **31칸**. 오늘 02:48~02:56 두 환경 전체 모드 E2E 기록을 읽은 것이다. 이 칸들은 2차·3차 수정 뒤의 E2E로 다시 확인하지 않았다(정본 [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md)의 최신 행이 이 칸의 단계를 지금도 포함하는지는 이 정리에서 대조하지 못했다).
  - **정책 정의(기대 동작이 영역 문서에 있음, 코드 D)**: 268칸 중 **140칸**. 그중 시험까지 본 것은 위 31칸이고, **107칸(U)은 시험 파일이 있다는 것만 읽었고 실행하지 않았다**(통과를 확인했다고 말하지 않는다), 6칸(DN)은 시험 없음, 부분 정의(P)는 별도 65칸.
  - **미정(기대 동작을 문서에서 찾지 못함, 코드 ?)**: 268칸 중 **63칸**(전부 시험도 없음, ?N). 35개 간선에 퍼져 있다(위 '미정 칸 목록' 합 63과 일치).
  - 시험 N(안 함) 130칸은 미정 63 + 부분 61 + 정의 6의 합이다.
  - 3차 점검의 알림 변경(전달 실패 알림은 재시도 때 다시 전달, 멱등 키에 종류 포함; `AUDIT_SUMMARY.md` 3차 절)과 L23(키오스크의 재알림 수단 없음)은 A9·A10 칸의 코드를 바꾸지 않았다. 이 행렬은 3차 수정 뒤 해당 영역 문서를 다시 읽지 않았으므로 A9·A10 칸이 낡았을 수 있다. 계약이 없어 정의할 수 없는 '재알림'은 칸이 아니라 [`change-requests/CR-H001-staff-call-redelivery.md`](change-requests/CR-H001-staff-call-redelivery.md) 초안으로 둔다.
- 기대 동작: 정의됨(D) 140/268, 부분(P) 65/268, **미정의(?) 63/268**. (초안: D 119 / P 59 / ? 89 of 267)
- 시험: E2E 시험함(E) 31/268, 영역 단위 시험만(U) 107/268, 안 함(N) 130/268. (초안: E 26 / U 85 / N 156 of 267) E 칸 31개는 전부 두 환경 확인(`*`)이다.
- 조합(기대+시험): DU 103, ?N 63, PN 61, DE 31, DN 6, PU 4 (합 268). 초안: ?N 89, DU 84, PN 58, DE 26, DN 9, PU 1 (합 267).
- 비기능 칸(4절) 22행(초안 20행에 N21·N22 추가): 기대 D 9, P 9, ? 4; 시험 E 5, U 9, N 8. 초안: 기대 D 6 / P 5 / ? 9; 시험 E 2 / U 5 / N 13. 타임아웃 일람은 5절.
- 바뀐 칸 34개('갱신 내역' 표). 시험 N -> U 22, N -> E 5, U -> E 0, 시험 그대로 7; 기대 ? -> D/P 27, P -> D 4.
- 한 줄 결론: 장애를 일부러 일으키는 E2E는 이제 **다섯 가지**다: model-serving 중지·기동(단계 5), **survey-service 중지·기동(5q)**, **survey-service 무응답 pause(5w)**, PostgreSQL 중지·기동(5p; 이제 **중지 중 환자 턴도 본다**), 백업·복구(단계 9). 환자 경로의 gateway-survey 구간(A2)과 서버 턴 총 마감·DB 대기 상한(A5·C4·D1·D4·E1)은 정의되고 시험되었다. 남은 큰 구멍은 직원 알림 경로(A9·A10, 입력원 비활성), 위험 신호가 있는 턴의 확정 실패(사용자 결정), DB pause의 E2E 부재, 깨진 응답 본문, 디스크 가득의 서비스 쪽 처리, 점검(check-health)을 주기로 부르는 주체 부재다.

### 기대 동작 미정의('?') 칸 목록 (간선: 장애 방식)

| 간선 | 미정의 칸 | 칸 수 | 초안 대비 |
| --- | --- | --- | --- |
| A1 키오스크 브라우저 -> gateway(Caddy) | F6 | 1 | 변화 없음 |
| A2 gateway -> survey-service(키오스크 API·직원 API 프록시) | F6 | 1 | 해소 F1, F2, F4, F5, F7, F8 |
| A3 gateway -> kiosk-frontend(정적 화면) | (없음) | 0 | 해소 F1, F2, F3, F4, F8 |
| A5 survey-service -> PostgreSQL(survey DB) | F6 | 1 | 해소 F2, F3, F5, F7 |
| A6 survey-service -> ops-feedback-ingest(I6 Trace, outbox 경유) | F2 | 1 | 변화 없음 |
| A8 survey-service -> survey-data 볼륨(releases/ 사본) | F1, F6 | 2 | 변화 없음 |
| A10 직원 브라우저 SSE -> gateway -> survey-service(알림 스트림) | F5, F8 | 2 | 해소 F4 |
| B1 model-serving -> release-gate(I4 번들 읽기, PUT 적재 때) | F8 | 1 | 변화 없음 |
| B3 model-serving -> HuggingFace(외부 인터넷, GPU/LLM 모드만) | F6, F7 | 2 | 변화 없음 |
| B4 (외부 추론 모드) survey-service -> 외부 추론 서버 / 외부 서버 -> release-gate | F8 | 1 | 변화 없음 |
| C1 release-gate 서버(Loop 60초) -> question-authoring(I1) | F8 | 1 | 변화 없음 |
| C2 release-gate 서버(Loop 60초) -> model-registry(I3) | F8 | 1 | 변화 없음 |
| C3 job-release-gate-collect -> question-authoring(I1)·model-registry(I3), gate DB에 접수 기록 | F8 | 1 | 변화 없음 |
| C4 release-gate(서버·수집 잡) -> PostgreSQL(gate DB) | F5, F6, F7 | 3 | 해소 F2, F3 |
| C5 release-gate·수집 잡 -> gate-data 볼륨(번들 파일 releases/) | F1 | 1 | 변화 없음 |
| C6 scheduler.py(호스트) -> docker compose run --rm <잡> | F4, F6, F8 | 3 | 해소 F2 |
| C7 admin-console 브라우저 -> gateway -> release-gate(승인 조회·결정) | F8 | 1 | 변화 없음 |
| C8 operator -> gateway -> release-gate(activate·rollback·active-pointer) | F8 | 1 | 변화 없음 |
| D1 job-ops-feedback -> PostgreSQL(ops_log, ops_failure) | F5, F6, F7 | 3 | 해소 F2, F3 |
| D2 job-ops-feedback -> release-gate(I4 읽기) | F8 | 1 | 변화 없음 |
| D3 job-ops-feedback -> release-gate(I5 롤백 요청) [운영 설정에 연결 없음] | F2, F8 | 2 | 변화 없음 |
| D4 ops-feedback-ingest(서버) -> PostgreSQL(ops_log, ops_failure) | F6, F7 | 2 | 해소 F2, F3 |
| D5 question-authoring -> ops-feedback-ingest(I7 개선 신호 읽기) | F8 | 1 | 변화 없음 |
| D6 reviewer 브라우저 -> gateway -> ops-feedback-ingest(검토 게시) | F8 | 1 | 변화 없음 |
| E1 question-authoring -> PostgreSQL(qa DB) | F6, F7 | 2 | 해소 F2, F3 |
| E2 저자 클라이언트 -> question-authoring(문항 등록·검수) | F1, F2, F3, F4, F5, F6, F7, F8 | 8 | 변화 없음 |
| F1 model-lab(GPU 서버, 컴포즈 밖) -> model-registry(I3 publish) | F8 | 1 | 변화 없음 |
| F3 synthetic-data(컴포즈 밖) -> question-authoring(I1)·ops-feedback(I7)·(I2는 HTTP 면 없음) | F8 | 1 | 변화 없음 |
| G1 PostgreSQL -> pg-data 볼륨(디스크) | F6 | 1 | 해소 F1 |
| G2 deploy up/rollback -> 로컬 레지스트리(compose.registry.yaml, 이미지 pull) | F6, F8 | 2 | 변화 없음 |
| G3 backup job -> postgres(pg_dump) / BACKUP_DIR 디스크 | F2, F3, F4, F6, F8 | 5 | 변화 없음 |
| G4 Docker 데몬/호스트 -> 컨테이너 재시작(restart: unless-stopped) | F4 | 1 | 변화 없음 |
| G5 외부 감시 -> gateway /healthz (서버 밖) | (없음) | 0 | 해소 F1 |
| G7 병원/의사 시스템 -> survey 결과 조회 API / 위험 신호 감지기 -> survey risk-signals API | F1, F2, F3, F4, F5, F6, F8 | 7 | 변화 없음 |
| G8 주기 호출자(cron/systemd timer, 서버 밖) -> check-health.sh (점검을 부르는 주체) | F1 | 1 | 신규 간선 |
| (합계) | | 63 | 초안 89 |

장애 방식별 미정의 칸 수(지금 / 초안): F1 5/8, F2 5/13, F3 3/9, F4 5/8, F5 5/7, F6 15/15, F7 6/8, F8 19/21. F8(분리) 칸의 다수는 F1·F2와 증상이 같아 보이나(연결 실패·타임아웃) 그렇다고 적은 영역 문서가 없어 미정의로 센다. FAULT_POLICY 11은 head 정책이지 영역 문서가 아니다.

비기능에서 미정의: N7 시계 어긋남, N9 비밀 파일 회전, N11 컨테이너 자원 제한, N18 TLS·인증서 만료. (초안은 N2 부하, N3 연결 풀, N4 동시 중복, N6 디스크 가득, N7 시계, N8 재시작 중 요청, N9 비밀 회전, N11 자원 제한, N18 TLS였고 N2·N3·N4·N6·N8이 정의되거나 부분 정의되었다)

### 갱신 내역: 바뀐 칸과 근거

이전에 N이던 칸이 U/E로 바뀐 근거를 칸마다 적었다. 근거는 문서·시험 파일을 직접 읽어 확인한 것이고(경로:줄), U 칸의 시험은 실행하지 않았다. 기대만 바뀌고 시험이 그대로인 칸도 포함한다.

| 간선 | 장애 | 이전 | 지금 | 근거 |
| --- | --- | --- | --- | --- |
| A1 | F4 | PN | DU | 키오스크가 502·503·504·429·네트워크 오류·무응답을 같은 turn_id로 지수 백오프 재시도하고 예산 20초 뒤 직원 호출(kiosk-frontend docs/design.md:32,35,47; test/retry.test.ts:28,36,44,117). 모의 서버 시험(실제 gateway 아님) |
| A1 | F5 | PU | DU | 500·그 밖의 4xx는 재시도 없이 오류, 502·503·504·429는 재시도(design.md:32,47; retry.test.ts:36,53). 초안의 '문서는 이를 말하지 않는다'가 해소됨 |
| A1 | F8 | PN | DU | 분리는 fetch 네트워크 오류·무응답으로 보여 재시도 규칙에 든다(design.md:47; retry.test.ts:36 TypeError fetch failed). 분리를 명시한 문장은 아님 |
| A2 | F1 | ?N | DE* | Caddyfile:196-202,239-253(연결 거부 -> 503 {"code":"UPSTREAM_UNAVAILABLE"}+Retry-After), deploy docs/E2E.md:35,43. E2E 5q(e2e_steps.py step5q()) docker stop 중 환자 턴 503(1.0s), gateway /readyz 503, /healthz 200, 복구 뒤 같은 turn_id 200 |
| A2 | F2 | ?N | DE* | Caddyfile:201-202(응답 헤더 8.5s)->504 JSON, E2E.md:44. E2E 5w(e2e_steps.py step5w()) docker pause 중 504, gateway 접근 로그 duration 8.5s(6.0<=d<10.0 단언), gateway /readyz 504 2.0s |
| A2 | F3 | PN | DE* | 느림이 응답 헤더 상한(8.5s)을 넘으면 F2와 같은 504 경로(5w). 상한 안의 느림은 정상 처리. 상한 직전의 느린 응답 자체는 시험하지 않음 |
| A2 | F4 | ?N | DE* | 5q의 stop->start 사이클이 재시작과 같은 증상(중지 중 503, 기동 뒤 gateway /readyz 200, 세션 값 보존). 처리 중 요청의 SIGTERM 정리는 survey 단위 시험 test_readyz_db_outage.py:173 |
| A2 | F5 | ?N | DE* | survey가 낸 5xx는 gateway가 가공하지 않고 통과: E2E 5p에서 DB 중지 중 환자 턴이 gateway 경유 503 UNAVAILABLE(retryable true) 본문 그대로(e2e_steps.py step5p()의 환자 턴 단언). 500 같은 다른 5xx는 시험하지 않음 |
| A2 | F7 | ?N | PU | survey가 401/403을 내면 gateway는 통과시키고 키오스크는 401/403을 직원 호출로 처리(design.md:32; test/client.test.ts:28). gateway 토큰이 어긋난 원인 자체의 정의·시험은 없음 |
| A2 | F8 | ?N | PN | 분리는 F1·F2와 같은 규칙(FAULT_POLICY 11)이고 dial 1s·응답 헤더 8.5s 상한이 Caddyfile:196-202에 있으나, 영역 문서의 분리 서술과 분리 시험은 없음 |
| A3 | F1 | ?N | PN | Caddyfile:218-233의 연결 2s+응답 헤더 10s, 사이트 수준 handle_errors(:239-253)가 정적 화면 상류에도 적용되어 gateway의 응답은 정해져 있다(E2E.md:35). 단 키오스크 화면 쪽 기대와 시험은 없다(5q·5w는 survey만 멈춘다) |
| A3 | F2 | ?N | PN | Caddyfile:218-233의 연결 2s+응답 헤더 10s, 사이트 수준 handle_errors(:239-253)가 정적 화면 상류에도 적용되어 gateway의 응답은 정해져 있다(E2E.md:35). 단 키오스크 화면 쪽 기대와 시험은 없다(5q·5w는 survey만 멈춘다) |
| A3 | F3 | ?N | PN | Caddyfile:218-233의 연결 2s+응답 헤더 10s, 사이트 수준 handle_errors(:239-253)가 정적 화면 상류에도 적용되어 gateway의 응답은 정해져 있다(E2E.md:35). 단 키오스크 화면 쪽 기대와 시험은 없다(5q·5w는 survey만 멈춘다) |
| A3 | F4 | ?N | PN | Caddyfile:218-233의 연결 2s+응답 헤더 10s, 사이트 수준 handle_errors(:239-253)가 정적 화면 상류에도 적용되어 gateway의 응답은 정해져 있다(E2E.md:35). 단 키오스크 화면 쪽 기대와 시험은 없다(5q·5w는 survey만 멈춘다) |
| A3 | F8 | ?N | PN | Caddyfile:218-233의 연결 2s+응답 헤더 10s, 사이트 수준 handle_errors(:239-253)가 정적 화면 상류에도 적용되어 gateway의 응답은 정해져 있다(E2E.md:35). 단 키오스크 화면 쪽 기대와 시험은 없다(5q·5w는 survey만 멈춘다) |
| A5 | F2 | ?N | DU | survey 영역: 문장 상한 SURVEY_DB_STATEMENT_TIMEOUT_SECONDS 기본 2s + 서버가 얼면 +1s 뒤 클라이언트 소켓 강제 종료, 턴 총 마감 6s(boundary.md:53,55; pg.py:100-119). 시험: tests/test_turn_db_outage_bounds.py:65, test_readyz_db_outage.py:139(둘 다 실제 PostgreSQL 컨테이너 docker pause). E2E는 pause를 하지 않음 |
| A5 | F3 | ?N | DU | F2와 같은 상한(문장 2s, 접속 2s, 재접속 유예 1s)이 느림도 덮는다(boundary.md:53,55). 서버 쪽 statement_timeout이 발동하는 느린 문장(pg_sleep) 직접 시험은 survey에서 찾지 못했고 pause(얼음)와 설정 시험으로 갈음(test_turn_db_outage_bounds.py:42) |
| A5 | F5 | ?N | DU | 정정(초안이 놓침): 쓰기 확정 실패는 NOT_COMMITTED 신호(boundary.md:82 Session Store 오류 행; test_orchestrator.py:334 FaultyStore). 실제 PostgreSQL이 내는 SQL 오류가 아니라 가짜 저장소 시험 |
| A5 | F7 | ?N | PU | 운영 중 접속 실패는 원인이 인증이든 거부든 한 경로(pg.py:93-96 except Exception -> OperationalError -> 503 UNAVAILABLE). 인증 실패를 직접 일으키는 시험은 없음(test_turn_db_outage_bounds.py:49는 연결 거부 주소) |
| A10 | F4 | ?N | PU | 정정+신규: SSE가 끊긴 뒤 Last-Event-ID(재시작 뒤 포함)로 이어 받는 단위 시험이 있다(survey tests/test_staff_alerts.py:472; alerts.py:203). survey SIGTERM 때 SSE 종료는 boundary.md:114에 있으나 그 시험은 찾지 못함. gateway 경유 실제 재시작 E2E 없음 |
| C4 | F2 | ?N | DU | release-gate boundary.md:40,43-53: 접속·문장 3s(+얼면 1s), /readyz 2s 안 503, 잡은 종료 코드 75. tests/test_pg_timeouts.py:193,216,231(docker pause) |
| C4 | F3 | ?N | DU | F2와 같은 상한. 서버 쪽 statement_timeout 설정 확인 test_pg_timeouts.py:172(느린 문장을 일부러 만드는 시험은 아님) |
| C6 | F1 | DN | DU | 스케줄러가 안 돌면 마지막 시작이 주기의 2배(+60초)를 넘어 CRIT(deploy docs/runbook.md:90-104; scripts/check_health.py 스케줄러 절). 자체 시험 scripts/test-check-health.sh:25. 점검을 주기로 부르는 주체(cron/timer)는 아직 없음(runbook 5-1 '아직 하지 않은 것') |
| C6 | F2 | ?N | DU | 시작했는데 1시간(--stuck-seconds) 넘게 안 끝나면 CRIT(check_health.py), scheduler.py:17,67-70의 잡당 3600s 종료 코드 124. 시험 test-check-health.sh:27. 같은 한계: 부르는 주체 미배치 |
| C6 | F3 | DN | DU | F2와 같은 규칙(느려서 1시간을 넘으면 CRIT). 시험 test-check-health.sh:27 |
| C6 | F5 | DN | DU | 잡의 마지막 종료 코드가 0이 아니면 CRIT(runbook.md:100, test-check-health.sh:23). E2E 단계 9는 정상 상태 파일만 읽음(e2e.sh:191 check-health 항목, OK 3 SKIP 2) |
| D1 | F2 | ?N | DU | ops-feedback boundary.md:60,64-70: 접속·문장 3s(+얼면 1s), 잡 종료 코드 2. tests/test_postgres_timeout.py:146(잡), :87,:125(docker pause) |
| D1 | F3 | ?N | DU | ops-feedback boundary.md:60,64-70: 접속·문장 3s(+얼면 1s), 잡 종료 코드 2. tests/test_postgres_timeout.py:146(잡), :87,:125(docker pause) ; 서버 쪽 statement_timeout 발동을 직접 만드는 느린 문장 시험은 qa만 있고 나머지는 얼음 시험으로 갈음 |
| D4 | F2 | ?N | DU | ops-feedback boundary.md:60,64-70: 요청 경로는 상한 안에 503 UNAVAILABLE, /readyz 2s. tests/test_postgres_timeout.py:87,107,125 |
| D4 | F3 | ?N | DU | ops-feedback boundary.md:60,64-70: 요청 경로는 상한 안에 503 UNAVAILABLE, /readyz 2s. tests/test_postgres_timeout.py:87,107,125 ; 서버 쪽 statement_timeout 발동을 직접 만드는 느린 문장 시험은 qa만 있고 나머지는 얼음 시험으로 갈음 |
| E1 | F2 | ?N | DU | question-authoring boundary.md:40,46-59: 접속·문장 3s(+얼면 1s), /readyz 2s. tests/test_postgres_specific.py:191(느린 문장을 서버 timeout이 끊음),:202,:267(docker pause) |
| E1 | F3 | ?N | DU | question-authoring boundary.md:40,46-59: 접속·문장 3s(+얼면 1s), /readyz 2s. tests/test_postgres_specific.py:191(느린 문장을 서버 timeout이 끊음),:202,:267(docker pause) |
| G1 | F1 | ?N | PU | 디스크 사용률 80%/90% 경보를 check-health가 읽는다(runbook.md:100-104; 자체 시험 test-check-health.sh:32). 단 state/·BACKUP_DIR만 기본이고 pg-data 볼륨 디스크는 --disk-path로 더해야 하며, 서비스의 쓰기 거부(503)는 미구현(runbook 5-1 '아직 하지 않은 것') |
| G5 | F1 | ?N | DU | check-health가 external-monitor 설정의 gateway /healthz를 직접 불러 닿지 못하면 CRIT(runbook.md:100-104; test-check-health.sh:45,47). E2E 단계 9가 실제 gateway /healthz를 읽어 OK. 외부 감시 서비스·공개 주소는 아직 없음(url null이면 SKIP) |

신규 간선 G8(점검 호출 주체)은 칸 1개(F1 `?N`)를 더한다. 코드가 그대로인 CH 항목: 없음. 같은 코드이지만 설명(근거)이 바뀐 간선: A6 F7, A4, C7·C8·D6(추가 발견), D3.

### 두 환경 확인 칸과 한 환경 확인 칸

**두 환경 확인(오늘 이 PC와 gpu-dev 전체 E2E 통과)** — E 칸 31개 전부. 칸과 확인한 단계:

| 간선 | 칸 | 확인한 E2E 단계 |
| --- | --- | --- |
| A2 | F1, F2, F3, F4, F5 | (이번에 새로 E가 된 칸 포함) 5q, 5w, 5p 확장 |
| A4 | F1, F4 | 5(model-serving stop/start) |
| A5 | F1, F4, F8 | 5p(+환자 턴) |
| A10 | F7 | 5f/5r(직원 경로 인증) |
| C4 | F1, F4, F8 | 5p |
| C7 | F7 | 5f |
| C8 | F7 | 5f |
| D1 | F1, F4, F8 | 5p |
| D4 | F1, F4, F8 | 5p |
| D6 | F7 | 7 |
| E1 | F1, F4, F8 | 5p |
| G1 | F4 | 5p(단계 9 복구) |
| G2 | F1, F4 | 9(레지스트리 기동·digest 잠금 롤백) |
| G3 | F1 | 9 |
| G7 | F7 | 5r |

확인 근거: 이 PC 로그 `e2e-full7.log`(02:57, FAIL 0, `POLICY-PENDING` 0건)과 gpu-dev 로그 `e2e-gpudev7.log`(02:48, 같은 결과)에서 5q·5w·5p 줄과 정책 단언 5건이 모두 REAL이었음을 읽었다(로그는 헤드 scratchpad에 있어 리포지토리에는 없다). 정본 기록은 `deploy/docs/E2E_RESULTS.md`의 두 줄(02:56 f8c2649 이 PC, 02:48 7355791 gpu-dev, 각 116/0/0). 두 환경의 5w 실측은 클라이언트 8.51s / 8.5s, gateway 접근 로그 8.5s로 같았고, 5p의 DB 중지 중 환자 턴은 4.0s / 3.7s였다. 단계 5·5f·5r·7·9의 각 줄이 두 로그에 있음은 단계 제목과 REAL/PASS 줄로 확인했고, 이 단계들의 내용(어떤 장애를 일으키는가)은 e2e_steps.py·e2e.sh를 읽은 것이다.

**한 환경만 확인(영역이 '이 PC에서 측정했다'고 적은 U 칸)** — 영역 시험이 실제 PostgreSQL 컨테이너를 `docker pause`해서 얻은 값으로, 시험 코드는 저장소에 있으나 이 조사도 두 번째 환경 실행 기록도 찾지 못했다:

| 간선·칸 | 영역 | 측정 기록 |
| --- | --- | --- |
| A5 F2·F3 | survey-service | boundary.md:55 '이 PC에서 postgres 중지 시 턴 2.0초, pause 시 5.0초' |
| C4 F2·F3 | release-gate | boundary.md:53 '이 PC, 로컬 PostgreSQL 컨테이너 docker pause' |
| D1·D4 F2·F3 | ops-feedback | boundary.md:80 '이 세션, 호스트의 Docker PostgreSQL 16 컨테이너' (/readyz 2.0s, 수집 POST 7.0s, 잡 3.3s) |
| E1 F2·F3 | question-authoring | boundary.md:58 '이 PC, 일회용 PostgreSQL 컨테이너 한 대' |

그 밖의 U 칸(107개)은 시험 파일이 있다는 것만 읽었고 어느 환경에서 통과하는지 확인하지 못했다.

### 우선순위 (환자 안전과 데이터 손실에 닿는 것 먼저)

상태: **해소**(정의+시험, 근거는 갱신 내역), **부분**(일부만), **남음**.

| 순위 | 칸 | 상태 | 지금 | 해야 할 일(제안, 미결정) |
| --- | --- | --- | --- | --- |
| P0-1 | A2 F1·F2·F4·F5 (gateway-survey 구간) | 해소 | gateway가 503/504 UPSTREAM_UNAVAILABLE JSON을 주고 키오스크는 같은 turn_id로 재시도(예산 20초). 5q·5w 두 환경 통과. 남은 것: 실제 gateway 뒤의 키오스크 시험, gateway 토큰 불일치(A2 F7) | 키오스크-gateway-survey를 잇는 브라우저 E2E는 선택 |
| P0-2 | A4 총 대기 / N4 같은 turn_id 동시 중복 | 부분 | 서버 턴 총 마감 6초와 409 TURN_IN_PROGRESS가 정의·단위 시험됨. 5w가 gateway 상한을 단언. 남은 것: 겹침을 실제로 만드는 E2E 없음, model-serving pause E2E 없음, 6초 마감이 발동하는 E2E 경로 없음, 504 뒤 늦은 확정(N22) | model-serving pause와 동시 같은 turn_id E2E |
| P0-3 | A5 F2·F3 / C4 F2·F3 / D4 F2·F3 / E1 F2·F3 (DB 무응답) | 부분 | 네 영역 모두 접속·문장 상한과 /readyz 2초가 구현·문서화·단위 시험(docker pause). 남은 것: E2E의 pause 없음(5p는 stop), 4개 영역 모두 한 환경 측정 | 5p에 postgres pause 변형(영역 4개 + 환자 턴) |
| P0-4 | A5 F1의 환자 턴 (5p의 한계) | 부분 | 5p가 중지 중 환자 턴(비위험 발화)을 보고 두 환경에서 통과. 남은 것: 위험 신호가 있는 턴의 확정 실패 시 알림(사용자 결정)과 그 변형 시험 | 사용자 결정 후 위험 발화 변형 추가 |
| P0-5 | A9·A10·G7 (직원 알림 경로) | 남음 | 입력원 비활성(G01) 그대로. SSE 재연결은 단위 시험(A10 F4 PU)이 생겼으나 푸시 장애·SSE 장애·gateway 경유 재시작은 정의·시험 없음 | G01 결정 후 알림 경로 장애 기대를 정한다 |
| P1-1 | A6 F7 (Trace 토큰 불일치) | 부분 | survey /readyz가 trace_outbox.dead_by_code로 DEAD 건수를 원인별로 드러냄(단위 시험). 남은 것: 이 신호를 읽는 경보가 없음(check-health는 survey /readyz를 읽지 않음), DEAD 건 자동 재전송 미구현, ops-ingest 쪽 /readyz에는 신호 없음 | check-health 대상에 survey /readyz dead 건수 추가 검토 |
| P1-2 | N6 디스크 가득 / G1 | 부분 | check-health가 디스크 80/90%를 읽음(자체 시험). 서비스의 쓰기 거부(503)와 pg-data 디스크 기본 포함은 미구현 | 경보 대상에 pg-data 포함, 쓰기 거부 정의 |
| P1-3 | D3 (자동 롤백 간선) | 남음(사용자 결정) | runbook 5-2가 의도된 비연결임을 문서화함. 기준은 사용자 결정 대기 | 사용자 결정(롤백 기준) 후 운영 설정 연결과 E2E |
| P1-4 | C6·G5·G8 (스케줄러·감시) | 부분 | check-health가 잡 실패·스케줄러 정지·디스크·gateway /healthz를 읽음(자체 시험, E2E는 정상 상태만). gateway /readyz는 이제 survey를 반영. 남은 것: 점검을 주기로 부르는 주체와 알림 수신자 없음(G8 신규) | 감시 호출자·수신자 결정(D10) |
| P2 | E2 / N9 / N11 / N7 / N18 외 나머지 ? | 남음 | 저작 입력 경로 운영 부재(사용자 결정), 비밀 회전, OOM, 시계, TLS. 위 항목 처리 뒤 |  |

### 남은 위험 칸 10개 (시험이 없거나 컨테이너 조합 시험이 없는 것 중 환자 안전·데이터 손실에 닿는 순서)

표의 코드는 지금의 칸 코드다. 이 10개 중 두 환경 확인(`*`) 칸은 2번의 A5 F1 하나뿐이고 그것도 위험 발화 변형이 빠져 있다. 나머지는 E 시험이 없다.

| 순위 | 칸 | 지금 코드 | 왜 위험한가 | 해야 할 일(제안) |
| --- | --- | --- | --- | --- |
| 1 | A9 F2·F3·F5·F6·F7·F8 / A10 F1·F5·F8 (직원 알림 전달·SSE 장애), 입력원 G01 | A9 F2 PN, F3 PN, F5 PN; A10 F1 PN, F5 ?N, F8 ?N | 위험 환자가 직원에게 닿는 마지막 구간. 입력원이 지금 비활성이고 푸시·SSE 장애·재시작 때 알림 유실 여부 정의와 E2E가 없다(푸시는 VAPID·HTTPS 필요로 E2E 불가) | G01 결정 뒤 전달 실패 기대 정의, SSE 장애는 gateway 경유 E2E 추가 |
| 2 | A5 F1·F2 중 위험 신호가 있는 턴의 확정 실패 (사용자 결정 대기) | A5 F1 DE* / F2 DU | 쓰기 확정이 실패하면 위험 알림이 나가지 않는다(survey boundary.md:87 주의(안전)). 5p의 환자 턴은 위험 신호 없는 발화라 이 경우를 보지 못한다 | 사용자 결정 후 위험 발화 변형을 5p에 추가 |
| 3 | A4 F2·F3 (model-serving 멈춤·느림 중 환자 턴) | A4 F2 DU / F3 DU | 실제 모델 서버가 멈추거나 느린 상황에서 6초 마감·키오스크 재시도·gateway 9.5초가 맞물리는지 컨테이너 조합에서 본 적이 없다(5는 stop/start만, 단위는 가짜 모델) | 5w와 같은 model-serving pause E2E 단계 |
| 4 | DB 오류 계열: A5 F6, C4 F5·F6·F7, D1 F5·F6·F7, D4 F6·F7, E1 F6·F7 | A5 F6 ?N; C4 F5 ?N F6 ?N F7 ?N; D1 F5 ?N F6 ?N F7 ?N; D4 F6 ?N F7 ?N; E1 F6 ?N F7 ?N | SQL 오류·변조된 결과·운영 중 암호 변경에서 어떤 응답을 주는지 문서·시험이 없다. 환자 세션과 활성 릴리스 포인터가 이 DB에 있다 | 공통 규칙(FAULT_POLICY 10)을 영역 문서로 옮기고 오류 주입 시험 |
| 5 | A1 F6 / A2 F6 (깨진 응답 본문) | A1 F6 ?N, A2 F6 ?N | 환자 화면이 JSON 파싱에 실패했을 때(client.ts:183) 무엇을 보이는지 정의·시험이 없다. 오동작하면 환자에게 잘못된 안내가 나갈 수 있다 | 깨진 본문을 500과 같이 처리한다는 규칙(FAULT_POLICY 10)을 design.md에 적고 시험 |
| 6 | G1 F6 / N6 / A8 F1·F6 / C5 F1 (디스크 가득·볼륨 쓰기 불가) | G1 F1 PU, F6 ?N; A8 F1 ?N, F6 ?N; C5 F1 ?N | 5개 DB가 한 볼륨이다. 검출(check-health)은 생겼으나 서비스의 쓰기 거부 503이 없어 가득 차면 환자 데이터 쓰기가 한꺼번에 실패한다. 경보는 호출 주체가 없다(G8) | pg-data를 점검 대상에 포함, 가득 찼을 때의 기대를 영역 문서에 정의 |
| 7 | G3 F2·F3·F4·F6·F8 (백업 중 DB 멈춤·느림·재시작·깨진 덤프·분리) | G3 F2 ?N F3 ?N F4 ?N F6 ?N F8 ?N | 백업이 조용히 불완전하면 복구 불능이 된다. 정상 백업·복구만 E2E(단계 9), 실패 중 동작은 미정의. 잡 실패 자체는 check-health가 읽는다(C6 F5) | 백업 중 DB 중지·가득 시 .partial 폐기와 잡 실패 종료 코드를 정의·시험 |
| 8 | G4 F4 / N12 (호스트·Docker 재부팅 뒤 기동 순서) | G4 F4 ?N | 서버 전체 재기동 뒤 키오스크가 복구되는지 시험하지 않았다. 서버 전체 중단은 '비보증'(D10)이고 gateway는 depends_on을 다시 평가하지 않는다 | 재부팅 후 기동 순서 점검(또는 비보증 유지 시 감시 알림 경로 확정) |
| 9 | A6 F1·F2 (Trace 수집 중지·무응답) | A6 F1 DU / F2 ?N | Trace가 수집기 장애 동안 outbox에 쌓이고 복구 뒤 재전송되는지 컨테이너 조합에서 본 적이 없다. 개선 데이터 손실 방향(환자 안전과는 간접) | ops-feedback-ingest stop/start 중 환자 턴과 outbox 재전송 E2E |
| 10 | A3 F1·F2·F3·F4·F8 (정적 화면 서버 장애) | A3 PN PN PN PN PN | 키오스크가 처음 열릴 때 정적 서버가 없으면 환자에게 JSON 오류가 보일 뿐 화면 기대가 정의되지 않았다. 이미 로드된 앱은 영향 없으리라는 것은 추정 | kiosk-frontend 정적 서버 stop 시 gateway 응답과 화면 기대 정의 |

사용자 결정 대기 항목(코드 칸 아님, 그대로 둔다): (1) 위험 신호가 있는 턴의 확정 실패 시 직원 알림, (2) 키오스크 재시도 예산 20초와 서버 턴 총 마감 6초의 현장 적합성(gateway 9.5초, 키오스크 대기 10초 포함), (3) 자동 롤백 기준(`rollback: null`), (4) 저자가 운영 구성에서 문항을 올리는 경로(E2). 이 중 (1)은 위 2번 칸, (3)은 D3, (4)는 E2의 `?N` 8칸에 걸린다.

### 조합 간극과 추가로 발견한 것

- **키오스크 x gateway x survey를 한 번에 잇는 시험이 없다.** 키오스크 재시도(예산 20초)는 모의 서버로, gateway 503/504는 python 클라이언트(E2E 5q·5w)로, 409 TURN_IN_PROGRESS는 survey 단위 시험과 키오스크 모의 서버로 따로 본다. 세 규칙의 맞물림(예: 503 Retry-After 2초 뒤 재시도가 예산 20초 안에서 복구를 보는지)은 어디서도 합쳐 보지 않았다. kiosk-frontend design.md:37의 '실제 survey-service가 이 응답을 내는지 확인하지 못했다'는 낡은 문장이다.
- **영역 문서 사이의 어긋남**: survey boundary.md:53은 '접속 대기가 10초에서 3초로 줄었다'고 하나 같은 문단과 settings.py:142의 기본은 2초다. boundary.md:114 N8 단락과 6-1절 부하 표는 총 마감을 8초로 적었고 기본은 6초다(표는 측정 당시 값이라고 적혀 있음). kiosk-frontend design.md:37(위). 이 문서는 어느 쪽도 고치지 않는다.
- **504 뒤 늦은 확정(N22).** 5w에서 gateway가 504로 끝낸 요청을 survey가 unpause 뒤 처리했다(처리 횟수 1, 두 환경). 멱등이라 값이 두 번 저장되지는 않지만, 키오스크가 504 후 예산을 소진해 직원 호출로 간 환자의 값이 저장되는 경우가 생긴다.
- **gateway의 게이트·ops·admin-console 프록시에는 상류 시간 상한이 Caddyfile에 없다**(C7·C8·D6 설명). 환자 API·직원·정적 화면·/readyz만 명시되어 있다.
- **점검 스크립트를 부르는 주체가 없다**(신규 간선 G8). C6·G1·G5의 새 DU 칸은 검출 능력이 생긴 것이지 사람에게 알리는 경로가 생긴 것이 아니다.
- **E2E의 `/readyz` 시간 단언이 약하다**: 5p는 '중지 뒤 처음 비정상 코드가 보인 경과(3~12초)'를 출력하지만 요청 하나의 응답 시간(정책 5: 2초)은 단언하지 않는다. 그 상한은 영역 단위 시험이 본다.

### 정책 단언 중 아직 확인되지 않은 것

`FAULT_POLICY.md`의 원칙과 이번에 만든 E2E 정책 단언(`policy()`, 5q·5w·5p) 중 컨테이너 조합에서 통과를 확인하지 못했거나 일부만 확인한 것이다. E2E의 `policy()` 단언 5개는 두 환경 모두 REAL로 통과했다: 5q 재시작 뒤 확정 turn_id 재전송 멱등, 5w 클라이언트가 본 504 시간 10초 미만, 5w 504 뒤 같은 turn_id 재전송 한 번 기록, 5p 중지 중 환자 턴 총 마감, 5p 재전송 한 번 기록. 아래는 그 밖의 것이다.

| 정책 | 단언 상태 | 읽은 사실 |
| --- | --- | --- |
| 원칙 2: 처리 중 같은 turn_id는 409 TURN_IN_PROGRESS(+Retry-After) | E2E 단언 없음(단위만) | survey 단위 시험 test_turn_idempotency_deadline.py:38,62,143과 키오스크 모의 서버 시험만. 겹침을 실제로 만드는 E2E, 키오스크-survey 연결 시험 없음 |
| 원칙 3: 서버 턴 총 마감 6초가 실제로 발동해 NOT_COMMITTED | E2E에서 발동 경로를 건드리지 않음 | 5p의 DB 중지 턴은 접속 실패 503이 4초에 끝나 마감(6초)에 닿지 않는다. 마감 발동은 단위 시험(test_turn_idempotency_deadline.py:89,113, test_readyz_db_outage.py:139)만. 정책 3의 근거인 'pause 최악 5.0초'는 survey 영역이 이 PC에서 1회 측정한 값(boundary.md:55)이고 E2E의 값이 아니다 |
| 원칙 3: 불변식 키오스크 10초 > gateway 9.5초 > 서버 6초 | 부분(gateway 쪽만 E2E) | 5w가 gateway duration 6.0~10.0초를 단언(실측 8.5초)하나 키오스크 쪽 10초는 retry.ts·테스트(모의)에, 서버 6초는 survey 설정에 있다. 세 값을 한 곳에서 맞춰 보는 시험 없음. 5w 클라이언트 관찰 8.51초로 10초와의 여유는 약 1.5초 |
| 원칙 4: 영역 DB connect/statement timeout 2~3초 | 단위 시험(한 환경) | survey 2/2, release-gate·question-authoring·ops-feedback 3/3. 모두 영역이 이 PC에서 docker pause로 측정. E2E는 stop뿐 |
| 원칙 5: 의존이 죽으면 /readyz가 2초 안에 503 | E2E 시간 단언 없음 | 단위 시험이 영역별로 본다(survey test_readyz_db_outage.py:55, gate test_pg_timeouts.py:193, ops test_postgres_timeout.py:87, qa test_postgres_specific.py:245). 5p는 첫 비정상 관찰 경과만 출력 |
| 원칙 5: gateway /readyz가 survey /readyz를 반영 | E2E 통과(두 환경) | 5q 503(1.0s), 5w 504(2.0s), 복구 뒤 200. 다만 survey가 활성 릴리스 없이 503 no_active_release일 때와 DB 장애일 때를 구분하는 시험은 없음 |
| 원칙 7: 키오스크 지수 백오프·지터·예산 20초 | 단위(모의 서버)만 | retry.test.ts. 실제 gateway 503/504를 받는 키오스크 시험 없음. 값의 현장 적합성은 사용자 결정 대기 |
| 원칙 9: 인증 실패를 조용히 버리지 않는다 | 부분 | survey /readyz의 dead_by_code는 단위 시험(test_trace_export.py:242)만, 토큰 불일치를 일으키는 E2E 없음. ops-ingest 쪽은 로그 경고뿐. 이를 읽는 경보 없음 |
| 원칙 10: 깨진 응답은 신뢰하지 않는다 | 단위(boundary-contracts 클라이언트)만 | 키오스크의 깨진 응답 처리(A1 F6)는 정의·시험 없음. E2E 없음 |
| 원칙 11: 분리(F8)는 F1·F2 규칙 | 시험 없음 | 네트워크를 끊는 시험은 없다. F8 칸 중 DE로 센 것(A5·C4·D1·D4·E1)은 db 네트워크 분리를 postgres 중지(5p)와 같은 증상으로 읽은 것이다 |
| 원칙 12: 복구 후 비동기 전송(outbox) 재전송 | 부분 | 5p는 중지 전에 Trace 전송 완료를 기다려 행 지문이 흔들리지 않게 했다. 수집기 장애 동안 쌓인 outbox의 복구 뒤 재전송은 단위 시험(test_trace_export.py)뿐 |
| 원칙 13: 디스크 가득 경보·쓰기 거부 503 | 경보만 단위, 쓰기 거부 미구현 | check-health 자체 시험(디스크 한계를 0%로 낮춤)만. 서비스 쓰기 거부는 runbook이 각 영역의 몫으로 남김 |
| 원칙 14: 서버 밖에서 gateway /readyz 감시, 스케줄러 실패 노출 | 부분 | check-health 시험·E2E는 gateway /healthz를 대상으로 하고(/readyz 아님), 실패 상태는 가짜 상태 파일 단위 시험만, E2E는 정상 상태 OK 3 SKIP 2. 호출 주체 없음(G8) |

## 2. 간선을 찾은 방법 (재현 가능, 닫힌 목록의 한계)

간선 = 호출자 -> 대상 중 런타임에 일어나는 것(HTTP, DB 연결, 볼륨 공유, 스케줄러 실행, 외부 서비스 호출). 아래 순서로 찾았고, **여기서 놓친 간선은 이 문서에도 없다.** 다시 돌려서 새로 나오는 줄이 있으면 이 문서에 보탠다. 경로는 모두 `/home/user/sdabin/healthKiosk` 기준. 2026-10-28 갱신에서 간선 1개(G8)를 보탰다.

1. Compose 구조: `deploy/compose*.yaml`, `deploy/test/compose.fake-model.yaml`을 통째로 읽음(networks, volumes, secrets, depends_on, env_file, ports, profiles jobs).
2. 환경 변수 URL: `grep -nE '_URL|FACTORY|TIMEOUT|POLL' deploy/config/*.env`(비밀 파일 `secrets/`와 토큰 값은 열지 않았다. `cat config/*.env` 형태는 도구가 거부해 URL·타임아웃 줄만 grep).
3. 게이트웨이: `grep -nE 'reverse_proxy|handle|timeout' deploy/config/Caddyfile`.
4. 클라이언트 생성: `grep -rnE 'Http(QuestionReader|ModelRegistry|ReleaseReader|GateService|FailureStore|TraceIngest|DatasetStore|ModelRuntime)|boundary_contracts.clients' --include=*.py --include=*.yaml <각 영역>`.
5. 타임아웃·재시도: `grep -rnE 'timeout|TIMEOUT|retries|retry' <영역 소스>`; `grep -rnE 'ConnectionPool|psycopg_pool|max_connections|statement_timeout'`.
6. 서버 종류·본문 상한: `grep -rnE 'ThreadingHTTPServer|MAX_BODY|Content-Length'`.
7. 스케줄러·잡: `deploy/config/jobs.yaml`, `deploy/scripts/scheduler.py`, `run-job.sh`, `backup*.sh`, `check-health.sh`.
8. 계약: `boundary-contracts/HTTP.md` 전체, `boundary-contracts/boundary_contracts/clients/_http.py`(오류 분류).
9. 영역 문서: 각 영역 `docs/boundary.md`의 '장애 영향'(또는 '장애') 절, survey-service `docs/inference-server-spec.md` 5절, kiosk-frontend `docs/design.md`, deploy `docs/E2E.md`·`docs/runbook.md`.
10. 시험: `deploy/scripts/e2e_steps.py`(`grep -nE '"(stop|start|pause|kill)"'`로 장애 주입 지점 확인: step5()의 model-serving stop/start, step5q()의 survey stop/start, step5w()의 survey pause, step5p()의 postgres stop/start), `deploy/scripts/e2e.sh`(차단 단언 119-142, 스케줄러·check-health 181-186, 백업·복구 187-205), `deploy/scripts/test-check-health.sh`, 영역 `tests/`(`grep -rnE 'def test_\w*(unavail|down|refus|timeout|slow|retry|503|401|403|corrupt|tamper|reconnect|restart|concurren|frozen|pause)'`).

**읽지 못한/얕게 읽은 것**: `secrets/` 전체(의도적으로 열지 않음), `deploy/config/*.env`의 값(URL·타임아웃 줄만 grep), `synthetic-data/`(어댑터 소스만 grep, docs 미열람), `turn-engine/`(런타임 간선 없음으로 보고 열지 않음), `model-lab` 내부(경계 문서·팩토리만), `admin-console`/`kiosk-frontend` 테스트 본문(파일 이름·일부 줄만; 갱신에서 retry.test.ts 일부를 읽음), `deploy/scripts/test-*.sh`·`check-*.sh` 중 test-check-health.sh 외(내용 읽지 못함), `deploy/docs/E2E.md`의 측정표(5w 구간별 계측 절), `midterm presentation/`, 영역 단위 시험의 **통과 여부**(실행하지 않음), 갱신 커밋의 diff 전부(문서·시험 파일은 현재 상태만 읽음). Caddy의 기본 타임아웃은 deploy E2E.md:36가 '설정 없는 reverse_proxy' 관찰을 적고 있으나 이 조사는 그 값을 확인하지 못했다.

**이 조사가 정적 읽기만 했다는 점**: 아무 컨테이너도 띄우거나 멈추지 않았다. E 칸의 '시험함'은 시험 코드를 읽고 두 환경의 E2E 로그에서 해당 단계 줄과 PASS/FAIL 수를 확인한 것이고, U 칸은 시험 코드를 읽은 것이다.

## 3. 간선 x 장애 방식 행렬

`*`는 두 환경 확인(범례). 변경된 칸은 위 '갱신 내역'에 근거가 있다.

| ID | 구분 | 호출자 -> 대상 | F1 중지 | F2 멈춤 | F3 느림 | F4 재시작 | F5 5xx | F6 깨진 본문 | F7 인증 실패 | F8 분리 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 환자 | 키오스크 브라우저 -> gateway(Caddy) | DU | DU | DU | DU | DU | ?N | DU | DU |
| A2 | 환자 | gateway -> survey-service(키오스크 API·직원 API 프록시) | DE* | DE* | DE* | DE* | DE* | ?N | PU | PN |
| A3 | 환자 | gateway -> kiosk-frontend(정적 화면) | PN | PN | PN | PN | -- | -- | -- | PN |
| A4 | 환자 | survey-service -> model-serving(I9 extract/respond/PUT 적재) | DE* | DU | DU | DE* | DU | DU | DU | PN |
| A5 | 환자 | survey-service -> PostgreSQL(survey DB) | DE* | DU | DU | DE* | DU | ?N | PU | DE* |
| A6 | 환자 | survey-service -> ops-feedback-ingest(I6 Trace, outbox 경유) | DU | ?N | DU | DU | DU | DU | DU | PN |
| A7 | 환자 | survey-service -> release-gate(I4 활성 포인터 폴링 5초, load_bundle) | DU | DU | DU | DU | DU | DU | DU | PN |
| A8 | 환자 | survey-service -> survey-data 볼륨(releases/ 사본) | ?N | -- | -- | DN | -- | ?N | -- | -- |
| A9 | 환자·직원 | survey-service -> 웹 푸시 서비스(외부 인터넷, VAPID) | DU | PN | PN | -- | PN | PN | PN | PN |
| A10 | 직원 | 직원 브라우저 SSE -> gateway -> survey-service(알림 스트림) | PN | PN | -- | PU | ?N | -- | DE* | ?N |
| B1 | 환자(적재) | model-serving -> release-gate(I4 번들 읽기, PUT 적재 때) | DU | DU | DU | DU | DU | DU | DU | ?N |
| B2 | 환자(적재) | model-serving -> serving-data 볼륨(번들 캐시) | DU | -- | -- | DN | -- | DU | -- | -- |
| B3 | 환자(적재) | model-serving -> HuggingFace(외부 인터넷, GPU/LLM 모드만) | PN | PN | PN | -- | PN | ?N | ?N | PN |
| B4 | 환자 | (외부 추론 모드) survey-service -> 외부 추론 서버 / 외부 서버 -> release-gate | PN | PN | PN | PN | PN | PN | PN | ?N |
| C1 | 출고 | release-gate 서버(Loop 60초) -> question-authoring(I1) | DU | DU | DU | DU | DU | DU | DU | ?N |
| C2 | 출고 | release-gate 서버(Loop 60초) -> model-registry(I3) | DU | DU | DU | DU | DU | DU | DU | ?N |
| C3 | 출고 | job-release-gate-collect -> question-authoring(I1)·model-registry(I3), gate DB에 접수 기록 | DU | DU | DU | DU | DU | DU | DU | ?N |
| C4 | 출고·데이터 | release-gate(서버·수집 잡) -> PostgreSQL(gate DB) | DE* | DU | DU | DE* | ?N | ?N | ?N | DE* |
| C5 | 출고 | release-gate·수집 잡 -> gate-data 볼륨(번들 파일 releases/) | ?N | -- | -- | DN | -- | DU | -- | -- |
| C6 | 출고 | scheduler.py(호스트) -> docker compose run --rm <잡> | DU | DU | DU | ?N | DU | ?N | -- | ?N |
| C7 | 출고 | admin-console 브라우저 -> gateway -> release-gate(승인 조회·결정) | DU | DU | DU | DU | DU | DU | DE* | ?N |
| C8 | 출고 | operator -> gateway -> release-gate(activate·rollback·active-pointer) | PN | PN | PN | PN | PN | PN | DE* | ?N |
| D1 | 피드백 | job-ops-feedback -> PostgreSQL(ops_log, ops_failure) | DE* | DU | DU | DE* | ?N | ?N | ?N | DE* |
| D2 | 피드백 | job-ops-feedback -> release-gate(I4 읽기) | PN | PN | PN | PN | PN | PN | PN | ?N |
| D3 | 피드백 | job-ops-feedback -> release-gate(I5 롤백 요청) [운영 설정에 연결 없음] | DU | ?N | DU | DU | DU | DU | DU | ?N |
| D4 | 피드백 | ops-feedback-ingest(서버) -> PostgreSQL(ops_log, ops_failure) | DE* | DU | DU | DE* | DU | ?N | ?N | DE* |
| D5 | 피드백 | question-authoring -> ops-feedback-ingest(I7 개선 신호 읽기) | DU | DU | DU | DU | DU | DU | DU | ?N |
| D6 | 피드백 | reviewer 브라우저 -> gateway -> ops-feedback-ingest(검토 게시) | PN | PN | PN | PN | PN | PN | DE* | ?N |
| E1 | 저작 | question-authoring -> PostgreSQL(qa DB) | DE* | DU | DU | DE* | DU | ?N | ?N | DE* |
| E2 | 저작 | 저자 클라이언트 -> question-authoring(문항 등록·검수) | ?N | ?N | ?N | ?N | ?N | ?N | ?N | ?N |
| F1 | 모델 게시 | model-lab(GPU 서버, 컴포즈 밖) -> model-registry(I3 publish) | DU | DU | DU | DU | DU | DU | DU | ?N |
| F2 | 모델 게시 | model-registry -> models-data 볼륨 | DU | -- | -- | DN | -- | DU | -- | -- |
| F3 | 데이터 | synthetic-data(컴포즈 밖) -> question-authoring(I1)·ops-feedback(I7)·(I2는 HTTP 면 없음) | PN | PN | PN | PN | PN | PN | PN | ?N |
| G1 | 인프라 | PostgreSQL -> pg-data 볼륨(디스크) | PU | -- | -- | DE* | -- | ?N | -- | -- |
| G2 | 인프라 | deploy up/rollback -> 로컬 레지스트리(compose.registry.yaml, 이미지 pull) | DE* | -- | -- | DE* | -- | ?N | -- | ?N |
| G3 | 인프라 | backup job -> postgres(pg_dump) / BACKUP_DIR 디스크 | DE* | ?N | ?N | ?N | DN | ?N | -- | ?N |
| G4 | 인프라 | Docker 데몬/호스트 -> 컨테이너 재시작(restart: unless-stopped) | DN | -- | -- | ?N | -- | -- | -- | -- |
| G5 | 인프라 | 외부 감시 -> gateway /healthz (서버 밖) | DU | -- | -- | -- | -- | -- | -- | -- |
| G6 | 환자 | 키오스크 브라우저 -> 브라우저 음성 인식(Web Speech API, 외부 서비스) | PN | PN | PN | -- | PN | PN | -- | PN |
| G7 | 예정 | 병원/의사 시스템 -> survey 결과 조회 API / 위험 신호 감지기 -> survey risk-signals API | ?N | ?N | ?N | ?N | ?N | ?N | DE* | ?N |
| G8 | 인프라 | 주기 호출자(cron/systemd timer, 서버 밖) -> check-health.sh (점검을 부르는 주체) | ?N | -- | -- | -- | -- | -- | -- | -- |

### 간선별 근거와 설명

**A1. 키오스크 브라우저 -> gateway(Caddy)** (환자)
- 근거(간선): kiosk-frontend/api/client.ts:12,19,36,123-130; kiosk-frontend/apps/kiosk/flow.ts:146-157; Caddyfile:170-181; kiosk-frontend/docs/design.md:19-42
- 기대 동작·시험 근거: F1~F3: 시도당 10초 중단(AbortController), 같은 turn_id로 지수 백오프 재시도(0.5초 x2, 상한 5초, 지터 50~100%), 총 예산 20초를 넘으면 직원 호출 화면(kiosk-frontend 71f4ec5; design.md:32-35,45-47; api/retry.ts). [갱신] 초안의 '3회' 규칙은 폐기되었다. 재시도 대상은 429·502·503·504·네트워크 오류·무응답, 비대상은 500·그 밖의 4xx(404는 세션 만료 안내), 401/403은 직원 호출, 409는 details.reason=TURN_IN_PROGRESS만 같은 turn_id로 재시도하고 나머지 409는 WAITING_STAFF(design.md:47; e69d441). 예산은 시작한 시도를 끊지 않으므로 최악 약 예산+10초(design.md:35). F6: 응답 본문이 깨졌을 때(client.ts:183 JSON.parse 실패) 화면 동작 문서 없음. 시험은 모의 서버를 쓰는 영역 단위(test/retry.test.ts, client.test.ts, mock.test.ts, test-e2e/browser.e2e.test.ts는 모의 서버+헤드리스 브라우저)뿐이고, 실제 gateway·survey를 거치는 키오스크 시험은 없다. 한계: 예산·값이 임상 현장에 맞는지는 실측하지 못했고 사용자 결정 대기다. design.md:37의 '실제 survey-service가 이 응답을 내는지는 확인하지 못했다'는 survey 757351e 이후 낡은 문장이다(survey는 내고 단위 시험이 있다: test_turn_idempotency_deadline.py:38). 단 키오스크 모의 서버와 실제 survey를 이은 시험은 없다.

**A2. gateway -> survey-service(키오스크 API·직원 API 프록시)** (환자)
- 근거(간선): Caddyfile:25-34,193-202,239-253; compose.yaml:175-181; deploy docs/E2E.md:35,43-44; e2e_steps.py step5q()·step5w()
- 기대 동작·시험 근거: [갱신] gateway 구간은 이제 정의되고 시험된다. 설정: 환자 API는 연결 1s + 응답 헤더 8.5s(합 9.5s 상한, 재시도 없음 lb_try_duration 0), 연결 거부·이름 해석 실패는 1초대에 502->503, 시간 초과는 504, 둘 다 본문 {"code":"UPSTREAM_UNAVAILABLE"}, Content-Type JSON, Retry-After 2, Cache-Control no-store, 본문에 내부 주소 없음(Caddyfile:193-202,239-253; E2E.md:35). gateway /healthz는 상류와 무관한 정적 200, /readyz는 survey /readyz를 연결 1s+응답 헤더 2s로 프록시해 2xx면 ok 200, 아니면 상류 상태 코드와 {"ready":false}(Caddyfile:25-43; 정적 200이던 초안 서술은 폐기). 시험: E2E 5q(survey docker stop: 환자 턴 503 1.0s, gateway /readyz 503, /healthz 200, 기동 뒤 gateway /readyz 200, 세션 값 보존, 상류에 닿지 못한 턴은 기록 없음, 같은 turn_id 재전송 200, 정책 단언: 확정된 turn_id 재전송은 저장된 응답과 같고 한 번만 기록), E2E 5w(survey docker pause: 504, gateway 접근 로그 duration 6.0s 이상 10.0s 미만 단언 실측 8.5s, gateway /readyz 504 2.0s, 정책 단언: 호스트 클라이언트가 본 시간 10s 미만 실측 8.5s, 504로 끝난 턴을 같은 turn_id로 재전송해도 발화 한 번), E2E 5p 확장(DB 중지 중 환자 턴이 gateway를 통과한 survey의 503 UNAVAILABLE retryable, 이 PC 4.0s·gpu-dev 3.7s). 한계: (1) F7은 gateway가 survey에 붙이는 토큰이 어긋난 경우를 시험하지 않음. (2) F5·F6은 survey가 내는 응답을 가공 없이 통과시킨다는 것을 5p의 503 한 가지로만 봤다. (3) 5w에서 서비스는 unpause 뒤 gateway가 포기한 요청을 처리한다(관찰 횟수 1, 두 환경): 504를 본 키오스크 입장에서는 실패인데 서버에서는 뒤늦게 확정될 수 있고, 같은 turn_id 재전송은 한 번만 기록된다는 단언만 통과했다(N22). (4) 환자 API 외 gateway 프록시(C7·C8·D6·admin-console)에는 응답 헤더 상한이 Caddyfile에 없다(Caddyfile:81-173).

**A3. gateway -> kiosk-frontend(정적 화면)** (환자)
- 근거(간선): Caddyfile:190,197; compose.yaml:187-190
- 기대 동작·시험 근거: 정적 화면 상류(kiosk-frontend)가 응답하지 못할 때 gateway는 연결 2s+응답 헤더 10s(Caddyfile:218-233) 뒤 사이트 수준 handle_errors로 503/504 JSON을 준다(:239-253, 설계상 모든 상류에 적용). 그러나 정적 화면 대신 JSON을 받은 브라우저가 무엇을 보이는지, 이미 로드된 앱이 정적 서버 장애와 무관하리라는 것은 문서·시험 없음(추정, 미확인). E2E 5a는 정상 응답과 CSP만 본다. 5q·5w는 survey만 멈춘다.
- 해당 없음: F5/F6/F7: 정적 파일 서버, 본문 검증 없음, 인증 없는 경로

**A4. survey-service -> model-serving(I9 extract/respond/PUT 적재)** (환자)
- 근거(간선): survey.env:9; survey_service/remote.py:129-163; settings.py:132-133; boundary-contracts/HTTP.md I9절; survey-service/docs/inference-server-spec.md 4~5절
- 기대 동작·시험 근거: F1: 연결 실패는 0.2초 간격 1회 재시도, 계속되면 해당 단계 실패. extract 실패는 NOT_COMMITTED(쓰기 없음), respond 실패는 COMMITTED(쓰기 유지, 문장 없음). /healthz는 산다(spec 5절). E2E 5: model-serving docker stop -> 그 턴 실패 신호 -> start -> 다음 턴 성공(e2e_steps.py step5() 추론 서버 stop/start 절). F2: 읽기 타임아웃 4초, 재시도 없음(test_slow_extract_beyond_timeout_fails_the_step_without_retry). F3: 4초 안이면 정상, 서버는 대기가 길어지면 큐에 쌓지 않고 503(HTTP.md I9; model-runtime test_rejects_when_queue_would_exceed_wait). F4: 404 -> PUT 재적재(200이면 재호출, 202면 이번 턴 실패)(spec 5절, test_forgotten_release_*); E2E 5의 stop/start가 같은 경로. F5: 502/503/504는 1회 재시도, extract의 503 OUTPUT_INVALID는 그래프가 1회 더 재시도 후 턴 실패·상태 불변(D75, test_output_invalid_*). F6: 200인데 JSON 아님·계약 위반 -> 재시도 없이 단계 실패(test_malformed_*). F7: 401/403 재시도 없이 단계 실패(test_auth_failure_on_calls_fails_the_step). E2E 5는 토큰 없는 직접 호출을 서버가 거부하는지만 본다. F8: 연결 시도도 같은 4초 타임아웃(urlopen timeout)으로 끝난다고 읽히나 분리를 명시한 문서·시험이 없다. 주의: inference-server-spec.md는 parse/generate 이름을 쓰고 HTTP.md는 extract/respond(HTTP.md가 기준, D62). 4초는 소켓 단위 타임아웃이지 총 시간 상한이 아니다(urllib 의미: 코드로 확인하지 못한 추정). [갱신] 서버 턴 총 마감(SURVEY_TURN_DEADLINE_SECONDS 기본 6초, survey boundary.md:50-52)이 이제 호출별 소켓 timeout 합 위에 걸려, 느리거나 멈춘 모델·재시도 합이 6초를 넘으면 NOT_COMMITTED로 끝나고 늦은 작업은 확정하지 않는다(test_turn_idempotency_deadline.py:89,113). 따라서 초안의 '총 시간 상한 없음'(P0-2)은 해소된 상태다. 시험은 가짜 모델·Rig 단위뿐이고 model-serving을 pause하는 E2E는 없다(A4 F2·F3의 E 부재가 남음).

**A5. survey-service -> PostgreSQL(survey DB)** (환자)
- 근거(간선): compose.yaml:211,214; survey_service/pg.py:46-53,126-131; survey-service/docs/boundary.md 5~6절
- 기대 동작·시험 근거: F1: /readyz가 중지 뒤 503(problems: session_db/outbox_db/alert_db), /healthz 200, 복구 시 자동 200 = E2E 5p(postgres stop/start, 행 지문 보존). [갱신] 5p가 이제 DB 중지 중 환자 턴을 gateway 경유로 한 번 보낸다: 503 UNAVAILABLE retryable true(이 PC 4.0s, gpu-dev 3.7s), 확정된 이전 값 Q1.D01 유지, 중지 중 턴의 값 저장 없음(부분 저장 없음), 중지 중 발화 기록 0건, 복구 뒤 같은 turn_id 재전송이 200으로 확정되고 값이 한 번 저장됨(e2e_steps.py step5p()의 환자 턴 절). 정책 단언 2건(총 마감 6s+0.5s 이내, 재전송 뒤 한 번 기록) 통과. 단 이 환자 발화는 위험 신호가 없는 발화다: 위험 신호가 있는 턴이 확정에 실패했을 때 직원 알림을 보낼지는 사용자 결정 대기이고(survey boundary.md:87 주의(안전)), 그 변형은 시험하지 않았다. F2/F3: 주 연결에 접속·문장 상한(기본 각 2s)과 서버가 얼면 상한+1s 뒤 소켓 강제 종료, 접속 실패 뒤 1s 재접속 유예가 생겼다(boundary.md:53,55; pg.py:100-119). 이 PC에서 측정: postgres 중지 시 턴 2.0s, pause 시 5.0s(boundary.md:55). 시험: tests/test_turn_db_outage_bounds.py:49,65와 test_readyz_db_outage.py:55,139(실제 PostgreSQL 컨테이너 pause). 한계: pause의 E2E는 없고(5p는 stop), 이 PC에서만 측정했다고 survey 문서가 적었다. F5: 쓰기 확정 실패는 NOT_COMMITTED(boundary.md:82, test_orchestrator.py:334, 가짜 저장소). F6: 운영 중 변조된 응답 동작은 StoreError/DB_ERROR로 바꾼다는 코드(pg.py:56)뿐 문서 없음. F7: 접속 실패는 원인과 무관하게 한 경로(pg.py:93-96)이나 인증 실패 직접 시험 없음. F8: db-survey 네트워크 분리 = F1과 같은 증상.

**A6. survey-service -> ops-feedback-ingest(I6 Trace, outbox 경유)** (환자)
- 근거(간선): survey.env:6; survey_service/trace/exporter.py:66-120; survey-service/docs/boundary.md 4·6절
- 기대 동작·시험 근거: 턴 응답과 분리(턴은 영향 없음), UNAVAILABLE일 때만 지수 백오프 1~60초로 재시도, 최소 1회 전달, 같은 (세션,턴)은 한 번만(boundary.md 4절; test_trace_export.py). F2(연결은 되나 무응답): 클라이언트 10초 타임아웃 후 UNAVAILABLE로 보이나 이 경우를 명시한 문서는 없다. F6: 깨진 본문은 클라이언트가 UNAVAILABLE로 분류(boundary-contracts _http.py _map_error)해 재시도. F7: PERMISSION_DENIED는 재시도하지 않고 DEAD로 옮긴다(test_non_retryable_errors_are_not_retried:93) = 토큰이 틀리면 Trace가 DEAD 처리되어 유실되는 방향이고, [갱신] 이를 알리는 신호가 이제 survey /readyz의 trace_outbox.dead와 원인 코드별 dead_by_code(예: PERMISSION_DENIED)로 나온다(survey eeaf04f, boundary.md:54,81; tests/test_trace_export.py:242). 이 신호를 경보로 읽는 곳은 아직 없다(check-health는 survey /readyz를 읽지 않음). 수신 쪽 ops-feedback은 403 PERMISSION_DENIED를 서버 로그에 경고로 남길 뿐 /readyz에 인증 실패 신호가 없다(ops boundary.md:61). DEAD 건의 자동 재전송은 미구현. E2E 5/6은 정상 전송과 재전송 중복 없음만 본다(수집기 중지 E2E 없음).

**A7. survey-service -> release-gate(I4 활성 포인터 폴링 5초, load_bundle)** (환자)
- 근거(간선): survey.env:3,11; survey_service/clients.py:30; survey-service/docs/boundary.md 4·6·7절
- 기대 동작·시험 근거: 턴 처리 중에는 부르지 않는다(test_registry_never_calls_the_reader_during_a_turn). 장애 시 새 릴리스 반영만 늦고 진행 중 세션은 영향 없음, 다음 주기에 자동 재시도(boundary.md 6절; test_loader_retry.py). 잘못된 토큰·해시 불일치 등 결정적 오류는 이전 릴리스 유지 + rejections 기록(test_wrong_token_is_a_rejection_not_a_crash, test_release_loader.py). 포인터 교체(정상 경로)와 롤백은 E2E 4/5/5s/8. 이 간선의 장애 주입 E2E는 없다. F8: 분리는 F1과 같은 증상으로 읽히나 명시 없음.

**A8. survey-service -> survey-data 볼륨(releases/ 사본)** (환자)
- 근거(간선): compose.yaml:213
- 기대 동작·시험 근거: F1(볼륨 쓰기 불가·가득): 문서 없음. F4: 재시작 시 게이트 묶음에서 다시 적재되므로 백업 대상 아님(compose.yaml:213 주석, boundary.md 6절 '컨테이너 재시작' 행). 사본 손상(F6)은 해시 재검증이 있을 뿐(boundary.md 7절) 손상 시나리오 시험은 찾지 못했다.
- 해당 없음: F2/F3/F5/F7/F8: 로컬 볼륨, 네트워크·인증 없음

**A9. survey-service -> 웹 푸시 서비스(외부 인터넷, VAPID)** (환자·직원)
- 근거(간선): survey_service/alerts.py:354-372,439; settings.py:74(3초); survey-service/docs/boundary.md 3·6절
- 기대 동작·시험 근거: 직원 알림 전달 3초 상한(push_timeout). VAPID 키가 없으면 SSE만(boundary.md 3절). 전달 경로가 없거나 실패하면 DELIVERY_FAILED 신호로 환자 화면이 직원 호출이 된다(kiosk design.md:29; 단위 test_no_delivery_path_is_delivery_failed_but_alert_is_stored). 푸시 서비스의 느림·5xx·거부 개별 시험은 찾지 못했다. 실제 푸시는 E2E 불가(E2E 5x BLOCKED: VAPID·HTTPS 필요). 현재 직원 알림 입력원이 활성이 아니다(boundary.md 5절, G01).
- 해당 없음: F4: 외부 서비스, 우리가 재시작하지 않음

**A10. 직원 브라우저 SSE -> gateway -> survey-service(알림 스트림)** (직원)
- 근거(간선): Caddyfile:30-41; survey_service/service.py:338(heartbeat)
- 기대 동작·시험 근거: SSE는 gateway가 버퍼링을 끄고 read_timeout 1h(Caddyfile:38-40). 브라우저 EventSource 자동 재연결과 Last-Event-ID 이어받기(kiosk design.md:49). 서비스·게이트웨이 재시작 중 알림 유실 여부, 하트비트 끊김 감지 기준은 문서 없음. F7: 인증 없는 직원 경로 401/403은 E2E 5f/5r이 gateway 쪽에서 단언. [갱신] survey SIGTERM 때 /readyz는 503 shutting_down, SSE는 0.5초 안에 끝낸다고 boundary.md:114가 적었고 처리 중 턴을 끝까지 처리한다는 단위 시험이 있다(test_readyz_db_outage.py:173; SSE 종료 자체의 단언은 읽지 못함). SSE 재연결은 Last-Event-ID로 이어 받는 단위 시험이 있다(test_staff_alerts.py:472).
- 해당 없음: F3/F6: 스트림이라 느림·본문 검증 개념이 약함

**B1. model-serving -> release-gate(I4 번들 읽기, PUT 적재 때)** (환자(적재))
- 근거(간선): model-serving.env:5; model-runtime/src/model_runtime/server.py:149,399(timeout=120); compose.yaml:290
- 기대 동작·시험 근거: 적재 요청(PUT)에서 게이트 장애면 503 UNAVAILABLE(HTTP.md I9). 서버 /readyz는 release URL 도달 불가 시 503 후 복구(model-runtime test_unreachable_release_url_healthz_ok_readyz_503_then_recovers). 서버는 번들을 120초 타임아웃으로 읽는다. 호출한 survey 쪽은 적재 신호 실패 시 이전 릴리스 유지(spec 5절). F8 분리는 F1과 같은 증상이나 명시 없음. E2E 5/5s는 정상 적재만.

**B2. model-serving -> serving-data 볼륨(번들 캐시)** (환자(적재))
- 근거(간선): compose.yaml:293; model-runtime/tests/test_server.py:197,246
- 기대 동작·시험 근거: 쓰기 불가면 /readyz 503 + 이유(test_unwritable_bundle_dir_makes_readyz_503_with_reason). 캐시 손상은 해시 재검증으로 INTEGRITY_ERROR(test_tampered_or_missing_system_prompt_fails_the_load_with_integrity_error). 디스크 가득은 비기능 표. F4: 재시작해도 번들은 다시 받을 수 있다(compose.yaml:42).
- 해당 없음: F2/F3/F5/F7/F8: 로컬 볼륨

**B3. model-serving -> HuggingFace(외부 인터넷, GPU/LLM 모드만)** (환자(적재))
- 근거(간선): compose.llm.yaml(첫 기동 모델 내려받기, HF_HUB_OFFLINE); deploy/docs/GPU_HOLE.md
- 기대 동작·시험 근거: 첫 기동에 약 4GB를 내려받는다(compose.llm.yaml 주석). 오프라인이면 볼륨을 미리 채우고 HF_HUB_OFFLINE=1이라는 우회만 문서에 있다. 내려받기 실패 시 서비스 동작은 미정의. 이 모드(GPU)는 E2E 불가(GPU 구멍). OPEN_GAPS U01은 gpu-dev 1회 확인.
- 해당 없음: F4: 외부 서비스

**B4. (외부 추론 모드) survey-service -> 외부 추론 서버 / 외부 서버 -> release-gate** (환자)
- 근거(간선): compose.external-inference.yaml; compose.inference.yaml; deploy/docs/RUN.md 7-1
- 기대 동작·시험 근거: A4/B1과 같은 의미를 다른 호스트로 옮긴 것. 호스트 사이 양방향 도달성(compose.external-inference.yaml:5)이 깨졌을 때(방화벽·NAT 변경 등)는 문서 없음. 시험은 구성 병합 검사(scripts/test-inference-location.sh)뿐으로 읽었으나 그 스크립트의 내용은 열지 못했다.

**C1. release-gate 서버(Loop 60초) -> question-authoring(I1)** (출고)
- 근거(간선): release-gate.env:4-5,8; release_gate/main.py:180-191; factories.py:24(기본 30초)
- 기대 동작·시험 근거: I1/I3 중단 시 새 판정이 다음 주기로 미뤄진다(접수 유지, 기존 릴리스 영향 없음)(release-gate boundary.md 장애 영향; test_neighbor_down_defers, test_gate_flow.py:314,324). F7: PERMISSION_DENIED는 연기가 아니라 오류(test_wrong_token_is_permission_denied_not_deferred). E2E 4는 정상 판정만.

**C2. release-gate 서버(Loop 60초) -> model-registry(I3)** (출고)
- 근거(간선): release-gate.env:6-7; factories.py:31-32
- 기대 동작·시험 근거: C1과 같다. 승인 시점에 I3가 내려가 있으면 제출이 대기 상태로 남는다(test_approve_with_i3_down_leaves_submission_waiting). 어댑터 변조는 PASS를 막되 승인 기록을 남기지 않는다(test_adapter_tamper_blocks_pass_without_recording_approval).

**C3. job-release-gate-collect -> question-authoring(I1)·model-registry(I3), gate DB에 접수 기록** (출고)
- 근거(간선): compose.yaml:333-349; config/jobs.yaml(600초); release_gate/main.py:204-215; collector.py
- 기대 동작·시험 근거: 수집기는 이웃 장애 시 tempfail(종료 코드)로 연기하고 상태를 바꾸지 않는다(test_collect_defers_with_tempfail_when_neighbor_down, test_collector_defers_on_unavailable). 멱등(같은 조합은 기존 접수 반환). 스케줄러가 다음 주기에 다시 부른다. E2E 4가 수집기 실제 실행을 포함하나 장애 주입 E2E는 없다.

**C4. release-gate(서버·수집 잡) -> PostgreSQL(gate DB)** (출고·데이터)
- 근거(간선): compose.yaml:273,342; release_gate/postgres_store.py:74(connect_timeout=10)
- 기대 동작·시험 근거: F1/F4: /readyz 503 후 복구, 행 지문 보존 = E2E 5p(release-gate 포함). 연결 끊김 재접속 단위(release-gate test_postgres.py:97), /readyz 503이 접속 정보를 노출하지 않음(test_postgres.py:75). [갱신] F2/F3: 접속·문장 상한 기본 3s(이전 접속 10s·문장 없음), 서버가 얼면 +1s 뒤 클라이언트가 소켓을 닫음, /readyz는 별도 연결로 2s 안 503, 수집·판정 잡은 상한 안에 종료 코드 75(release-gate 6e45a12; boundary.md:40,43-53). 시험 tests/test_pg_timeouts.py:117,126,193,216,231(docker pause 포함). 한계: 이 PC의 측정이고 E2E는 pause를 하지 않는다. 상한은 문장 단위이므로 요청 하나가 여러 문장이면 합까지 걸릴 수 있다(boundary.md:51). F5/F6/F7: SQL 오류·DB 변조·인증 실패 시 동작은 문서에 없다.

**C5. release-gate·수집 잡 -> gate-data 볼륨(번들 파일 releases/)** (출고)
- 근거(간선): compose.yaml:275,344
- 기대 동작·시험 근거: 레지스트리 파일 손상 시 load_bundle/활성화가 INTEGRITY_ERROR, 롤백은 손상 대상을 REJECTED(release-gate boundary.md 장애 영향; test_rollback_to_corrupt_release_is_rejected). 쓰기 불가·가득은 문서 없음. 서버와 수집 잡이 같은 볼륨을 동시에 쓸 때의 경합도 문서 없음.
- 해당 없음: F2/F3/F5/F7/F8: 로컬 볼륨

**C6. scheduler.py(호스트) -> docker compose run --rm <잡>** (출고)
- 근거(간선): config/jobs.yaml; scripts/scheduler.py:47-78; scripts/run-job.sh; docs/runbook.md:81-85(cron)
- 기대 동작·시험 근거: [갱신] 스케줄러/잡 실패는 이제 읽을 수 있다: scripts/check-health.sh(deploy ebf13a3)가 state/scheduler.json과 config/jobs.yaml을 읽어 마지막 종료 코드가 0이 아니거나(CRIT), 마지막 시작이 주기의 2배+60초를 넘었거나(스케줄러 정지, CRIT), 시작했는데 1시간 넘게 끝나지 않으면(CRIT) 종료 코드 2를 낸다. 실행 기록이 없으면 WARN(1), 주기 미정·서버 밖(gpu-external) 잡은 SKIP으로 따로 센다(runbook.md 5-1절). 자체 시험: scripts/test-check-health.sh 11건(가짜 상태 파일, Docker 불필요), E2E 단계 9는 실제 스케줄러가 쓴 정상 상태 파일과 gateway /healthz를 읽어 OK 3 SKIP 2를 확인한다(정상 상태만, 실패 주입 없음). 한계: 이 점검을 주기로 부르는 cron/systemd timer와 알림 수신자는 아직 배치되지 않았다(runbook.md 5-1 '아직 하지 않은 것'). `docker compose run` 컨테이너가 시간 초과 뒤에 남는지 확인하지 못함. 이중 실행은 flock으로 BUSY(scheduler.py:60-63). F4(스케줄러 재시작)는 문서·시험 없음. F6(상태 파일 깨짐)은 check-health가 CRIT로 읽는 코드가 있으나(check_health.py) 시험 근거 없음.
- 해당 없음: F7: 인증 없음(로컬 프로세스)

**C7. admin-console 브라우저 -> gateway -> release-gate(승인 조회·결정)** (출고)
- 근거(간선): Caddyfile:50-82; admin-console/api/http.ts:54(15초); HTTP.md I5·D69
- 기대 동작·시험 근거: STALE_REPORT/ALREADY_DECIDED는 409로 구분(HTTP.md D69). 결정 POST는 같은 결정이면 같은 결과(멱등)라 무응답 뒤 재전송이 안전하다. 승인자가 결정하지 않으면 AWAITING_APPROVAL에서 대기(release-gate boundary.md). 화면의 오류 문구는 admin-console tests/ui.test.ts 단위(내용은 열지 않음). 실제 게이트 중지 E2E는 없다. E2E 4가 승인 경로를 gateway 경유로 정상 통과하고 E2E 5가 역할별 401/403을 단언. [추가 발견] gateway의 admin-console·release-gate 프록시(Caddyfile:81-173)에는 dial/응답 헤더 상한이 없다(환자 API·직원·정적 화면·/readyz만 명시, E2E.md:35). 게이트가 멈추면 gateway가 504를 주기까지 걸리는 시간은 Caddy 기본에 달려 있고(E2E.md:36의 '설정 없는 reverse_proxy' 관찰 참조, 값은 확인하지 못함) 화면의 15초 타임아웃이 먼저 끝날 수 있다.

**C8. operator -> gateway -> release-gate(activate·rollback·active-pointer)** (출고)
- 근거(간선): Caddyfile:129-162; e2e_steps.py step5() 역할별 권한 절
- 기대 동작·시험 근거: E2E 5가 권한 분리(401/403)와 operator 호출이 게이트까지 가는 것을 단언. 활성화·롤백은 멱등(같은 request_id 같은 결과, E2E 8). gateway 또는 게이트가 응답 없을 때 운영자 도구가 무엇을 보이는지는 문서 없음(호출자가 임의 HTTP 클라이언트). [추가 발견] C7과 같다: operator 경로(Caddyfile:160-173)에도 상류 상한이 없다.

**D1. job-ops-feedback -> PostgreSQL(ops_log, ops_failure)** (피드백)
- 근거(간선): compose.yaml:322-323; ops-feedback/src/ops_feedback/pgbase.py:21
- 기대 동작·시험 근거: 잡 중단·지연: 실패 사례 게시와 롤백 평가가 늦어지고 원본은 안전, 다음 실행이 이어서 처리(ops-feedback boundary.md 장애 영향). 연결 끊김 재접속·URL 비노출 단위(test_postgres_reconnect.py:55). E2E 5p는 ops_log/ops_failure 행 지문을 비교하나 잡 실행 중 DB 중지는 시험하지 않는다. [갱신] F2/F3: 접속·문장 상한 기본 3s(이전 10s), 얼면 +1s 뒤 소켓 종료, 잡은 상한 안에 종료 코드 2(처리 오류 1과 구분)(ops-feedback 616b2b1; boundary.md:60,64-70; tests/test_postgres_timeout.py:146). 한계: 이 세션(이 PC) 측정, E2E의 pause 없음, 느린 문장 직접 시험은 얼음 시험으로 갈음.

**D2. job-ops-feedback -> release-gate(I4 읽기)** (피드백)
- 근거(간선): config/ops-feedback-job.yaml:41-42; compose.yaml:314-331(networks logs, release, db-ops)
- 기대 동작·시험 근거: 롤백 평가에 필요한 릴리스 정보를 읽는다. 게이트 장애 시 잡의 종료 코드·재시도는 I4 읽기에 대해서는 정의를 찾지 못했다('게이트 UNAVAILABLE이면 롤백 요청이 전달되지 않고 다음 실행에서 재시도'는 D3 줄). 운영 설정의 rollback 항목이 null이라(ops-feedback-job.yaml:39) 현재 롤백 평가는 꺼져 있다고 읽힌다(미확인).

**D3. job-ops-feedback -> release-gate(I5 롤백 요청) [운영 설정에 연결 없음]** (피드백)
- 근거(간선): ops-feedback/src/ops_feedback/job.py:201(cfg['gate_service']); deploy/config/ops-feedback-job.yaml에 gate_service 항목 없음(grep), rollback: null(:39); e2e_steps.py step8()
- 기대 동작·시험 근거: 코드는 있고 단위 시험이 있다(test_unavailable_gate_retries_same_request: 요청 저장·같은 id 재전송). E2E 8은 ops-feedback 토큰으로 테스트 하니스가 직접 HttpGateService를 부른 것이며(e2e_steps.py step8()) 운영 잡 설정을 거치지 않는다. 운영 job 설정에는 gate_service 항목과 롤백 기준이 없어 자동 롤백 간선이 현재 켜져 있지 않다(grep 결과; 롤백 기준은 사용자 결정 대기). '나쁜 릴리스를 자동으로 되돌린다'는 사실로 쓰면 안 된다. [갱신] deploy docs/runbook.md의 5-2절이 운영 잡 설정에 rollback·gate_service가 없는 것이 '의도'임을 근거와 함께 적고, 기준이 정해지면 켜는 설정 예시와 확인 방법을 두었다(확인 단계는 아직 실행하지 않았다고 적혀 있다). 간선이 꺼져 있다는 사실은 그대로다.

**D4. ops-feedback-ingest(서버) -> PostgreSQL(ops_log, ops_failure)** (피드백)
- 근거(간선): compose.yaml:252-253; pgbase.py:21
- 기대 동작·시험 근거: log 쓰기 불가면 send가 UNAVAILABLE이고 survey가 재시도(boundary.md 장애 영향). E2E 5p가 /readyz 503->200과 행 지문 보존을 확인. 디스크 가득은 비기능 표. [갱신] F2/F3: 요청은 상한(문장 3s+1s, 연결 끊김 재접속 포함 최악 약 7s) 안에 503 UNAVAILABLE로 끝나고(호출자 survey가 재시도), /readyz는 별도 연결로 2s 안에 503(ops-feedback boundary.md:60,64-70; tests/test_postgres_timeout.py:87,107,125; 측정은 이 PC: /readyz 2.0s, 수집 POST 503 7.0s). 한계: E2E pause 없음. F7 수집 토큰 불일치(survey 설정·회전 오류)는 403 PERMISSION_DENIED와 서버 로그 경고뿐이고 /readyz에는 신호가 없다(boundary.md:61).

**D5. question-authoring -> ops-feedback-ingest(I7 개선 신호 읽기)** (피드백)
- 근거(간선): question-authoring.env:2; question_authoring/__main__.py:45-47; http_api.py:142; question-authoring boundary.md 장애 영향
- 기대 동작·시험 근거: ops-feedback 중단 시 GET /v1/signals만 UNAVAILABLE, 나머지는 영향 없음(boundary.md 장애 영향; test_signals.py, 403 매핑 포함). 클라이언트 타임아웃은 기본 10초(__main__.py:47에서 지정하지 않음). I7 읽기 면이 DB URL만으로 켜지는지는 ops-feedback 이미지로 확인해야 한다고 deploy가 '미검증'으로 적어 둠(ops-feedback-ingest.env:2). E2E 7이 I7 정상 경로를 사용.

**D6. reviewer 브라우저 -> gateway -> ops-feedback-ingest(검토 게시)** (피드백)
- 근거(간선): Caddyfile:86-119; HTTP.md I7 검토 게시
- 기대 동작·시험 근거: reviewer 역할만 쓰기(읽기 토큰 403), 같은 검토 재전송은 같은 결과(멱등). 중지·무응답 시 검토 화면 동작은 admin-console 문서에서 찾지 못했다. reviewer 계정 권한 분리와 검토 게시는 E2E 7이 단언(e2e_steps.py step7() 게이트웨이 경유 검토 절). [추가 발견] C7과 같다: ops-feedback-ingest 프록시(Caddyfile:117-130)에도 상류 상한이 없다.

**E1. question-authoring -> PostgreSQL(qa DB)** (저작)
- 근거(간선): compose.yaml:233,236; question_authoring/store/postgres.py:87(connect_timeout=5)
- 기대 동작·시험 근거: I1 호출이 UNAVAILABLE(재시도 가능), /readyz 503(question-authoring boundary.md 장애 영향). E2E 5p가 qa DB 행 지문과 복구 후 새 쓰기(버전 2)까지 확인. 연결 끊김 재접속·쓰기 응답 유실 멱등은 test_postgres_specific.py:80,94,107. [갱신] F2/F3: 접속 3s(이전 5s), 문장 3s(이전 없음, 쓰기 직렬화 advisory lock 대기 포함), 얼면 +1s 뒤 소켓 종료, /readyz 2s(question-authoring c585b9b; boundary.md:40,46-59). 시험 test_postgres_specific.py:184,191(느린 문장을 서버가 끊음),202(락 대기),220,245,259,267(pause). 한계: 이 PC의 측정, 컨테이너 조합 재측정은 E2E 5p의 stop만, 호출자가 이 영역 응답을 기다리는 시간과의 맞물림은 시험하지 않음.

**E2. 저자 클라이언트 -> question-authoring(문항 등록·검수)** (저작)
- 근거(간선): compose.yaml:182(호스트 포트는 gateway만); Caddyfile에 authoring 경로 없음(reverse_proxy 목록 grep); compose.test.yaml:17-19(시험용 포트)
- 기대 동작·시험 근거: 운영 구성에서 저자가 문항을 올리는 길이 없다(구성을 읽은 사실). E2E는 compose.test.yaml의 시험 포트로 직접 올린다(e2e_steps.py upload()). 이 간선의 운영 형태가 정해지지 않아 장애 기대도 정의할 수 없다. 의도된 구성인지는 확인하지 못했다.

**F1. model-lab(GPU 서버, 컴포즈 밖) -> model-registry(I3 publish)** (모델 게시)
- 근거(간선): boundary-contracts/HTTP.md I3; model-lab/model_lab/config.py:130; model-lab/docs/boundary.md 장애 영향
- 기대 동작·시험 근거: 게시는 매니페스트를 마지막에 써 중단되어도 반쯤 게시된 패키지가 보이지 않고 재실행하면 이어서 끝낸다(model-lab boundary.md). 레지스트리 장애 시 학습 결과는 유지되고 게시만 재시도(test_registry_outage_keeps_training_result_and_retries_only_publish). 같은 ID·버전·다른 내용이면 409. E2E 3은 정상 게시만(E2E_GPU=1 경로는 GPU 호스트 필요).

**F2. model-registry -> models-data 볼륨** (모델 게시)
- 근거(간선): compose.yaml:306; model-lab/tests/test_registry.py:140,147
- 기대 동작·시험 근거: 파일 손상은 읽기에서 INTEGRITY_ERROR(변조를 조용히 통과시키지 않음). 가득·쓰기 불가는 비기능 표.
- 해당 없음: F2/F3/F5/F7/F8: 로컬 볼륨

**F3. synthetic-data(컴포즈 밖) -> question-authoring(I1)·ops-feedback(I7)·(I2는 HTTP 면 없음)** (데이터)
- 근거(간선): synthetic-data/synthetic_data/adapters.py:25-30(타임아웃 10초); boundary-contracts/HTTP.md I2 절
- 기대 동작·시험 근거: 읽기 클라이언트가 같은 UNAVAILABLE 분류를 쓴다(boundary-contracts test_clients_common.py). synthetic-data 자체의 실패 처리 문서는 읽지 못했다(이 조사는 synthetic-data/docs를 열지 않았다). I2 DatasetStore는 HTTP 경로가 정해지지 않았다(HTTP.md '실제 서버 구현 여부 미확인')라 이 간선은 일부 미정.

**G1. PostgreSQL -> pg-data 볼륨(디스크)** (인프라)
- 근거(간선): compose.yaml:44,142-160
- 기대 동작·시험 근거: 디스크 가득·볼륨 손상 시 5개 DB가 동시에 영향을 받는다(단일 postgres 컨테이너가 단일 장애점인 구성). 백업·복구(pg_dump)는 E2E 단계 9에서 시험(e2e.sh:198-205, 복구 후 e2e_verify_restore.py). [갱신] F1: 디스크 사용률은 check-health가 80% WARN·90% CRIT로 읽는다(기본 경로는 state/와 BACKUP_DIR이고 pg-data가 다른 디스크면 --disk-path로 더해야 함, runbook.md 5-1절; 자체 시험 test-check-health.sh:32). 가득 찼을 때 서비스가 쓰기를 거부(503)하고 기존 데이터를 깨뜨리지 않는다는 정책(FAULT_POLICY 13)은 아직 구현·시험되지 않았다(runbook 5-1: 각 영역의 몫). 컨테이너 로그·Docker 볼륨 사용량·postgres 자체의 디스크 경보는 하지 않았다고 적혀 있다.
- 해당 없음: F2/F3/F5/F7/F8: 로컬 볼륨

**G2. deploy up/rollback -> 로컬 레지스트리(compose.registry.yaml, 이미지 pull)** (인프라)
- 근거(간선): compose.registry.yaml; deploy/docs/boundary.md 6절; locks/images.lock
- 기대 동작·시험 근거: 레지스트리 중단: 새 이미지 적용·롤백이 막히고 이미 떠 있는 컨테이너는 영향 없음(deploy boundary.md 6절). 컨테이너가 재시작할 때 이미지가 로컬에 없으면(prune 등) 동작은 문서 없음(미확인). 시험: scripts/test-publish.sh, E2E 단계 9 코드 축 롤백(이 칸들의 시험 표시는 'N'으로 보수적으로 둠: 장애 주입 근거를 찾지 못함).
- 해당 없음: F2/F3/F5/F7: 레지스트리는 운영 중 요청 경로가 아님(배포 시점에만)

**G3. backup job -> postgres(pg_dump) / BACKUP_DIR 디스크** (인프라)
- 근거(간선): config/jobs.yaml(86400초); scripts/backup-all.sh, pg-backup.sh:13-30; e2e.sh:187-205
- 기대 동작·시험 근거: 설정(BACKUP_DIR·보관 기간)이 없으면 거부 코드 2, 보관은 방금 만든 것과 최근 하나를 남긴다(e2e.sh:187-200 시험). 백업 도중 DB 중지·디스크 가득은 문서 없음(.partial 디렉터리에 쓰고 완료 시 mv: pg-backup.sh:23-29는 읽음). 백업 주기·복구 시점(O16)은 미정.
- 해당 없음: F7: 로컬 docker exec

**G4. Docker 데몬/호스트 -> 컨테이너 재시작(restart: unless-stopped)** (인프라)
- 근거(간선): compose.yaml:7(x-hardening); deploy/docs/boundary.md 6절 '서버 전체 중단: 비보증(D10)'
- 기대 동작·시험 근거: 서버 전체 중단은 보증하지 않으며 외부 감시가 담당에게 알린다(미정, D10). 호스트 재부팅 뒤 기동 순서(postgres -> 서비스 -> gateway)가 depends_on healthy로 맞는지는 시험하지 않았다. 서비스 하나가 재시작할 때 이미 떠 있는 gateway는 depends_on을 다시 평가하지 않는다.
- 해당 없음: F2/F3: 간선이 아니라 인프라 계층 자체, F5~F8 해당 없음

**G5. 외부 감시 -> gateway /healthz (서버 밖)** (인프라)
- 근거(간선): config/external-monitor.example.yaml(url: null; 이제 scripts/check_health.py가 읽는다); Caddyfile:22-43
- 기대 동작·시험 근거: [갱신] 외부 감시 구성은 아직 없다(config/external-monitor.example.yaml의 url: null). 대신 서버 안에서 같은 설정을 읽는 check-health가 gateway /healthz를 직접 불러 기대 코드와 다르거나 닿지 못하면 CRIT(종료 코드 2)를 낸다(runbook.md 5-1절; 시험 test-check-health.sh:43,45,47, E2E 단계 9가 실제 gateway /healthz로 OK 확인). 서버가 통째로 죽으면 이 서버 안의 점검도 같이 멈추므로 서버 밖 호출자·알림 수신자는 여전히 필요하다(미정, D10). gateway /healthz는 정적 200이고 /readyz는 이제 survey /readyz를 반영한다(A2). F2~F8은 아직 존재하지 않는 간선.
- 해당 없음: F2~F8: 아직 존재하지 않는 간선

**G6. 키오스크 브라우저 -> 브라우저 음성 인식(Web Speech API, 외부 서비스)** (환자)
- 근거(간선): kiosk-frontend/docs/runbook.md:38; E2E 5x(BLOCKED, e2e_steps.py)
- 기대 동작·시험 근거: Chrome에서 인터넷과 구글 음성 서비스에 의존(runbook.md:38). 인식 실패·무신뢰는 REPEAT_PROMPT(design.md:20). 인터넷이 끊겼을 때 키오스크가 텍스트 입력 등으로 대체되는지는 문서 없음(미정). 실제 브라우저·STT는 E2E에서 볼 수 없다(BLOCKED).
- 해당 없음: F4: 외부 서비스, F7: 인증 없음

**G7. 병원/의사 시스템 -> survey 결과 조회 API / 위험 신호 감지기 -> survey risk-signals API** (예정)
- 근거(간선): Caddyfile:166-169(게이트웨이에 열지 않음); compose.yaml:204-205; e2e_steps.py step5r()(5r); survey boundary.md 5절
- 기대 동작·시험 근거: 호출자가 아직 없는 간선(결과 전달 대상 없음이 지금의 정상 구성, survey boundary.md 5절). 토큰 분리는 E2E 5r이 단언(다른 역할 403, 게이트웨이 404). 호출자가 생기면 장애 기대를 정해야 한다. 현재 직원 알림 입력원도 없다(G01).

**G8. 주기 호출자(cron/systemd timer, 서버 밖) -> check-health.sh (점검을 부르는 주체)** (인프라)
- 근거(간선): deploy docs/runbook.md 5-1절, scripts/check-health.sh, scripts/e2e.sh:90,191(check-health 항목); 호출하는 cron/timer 설정은 리포지토리에서 찾지 못함
- 기대 동작·시험 근거: [신규 간선, 2026-10-28] check-health.sh는 읽기 전용 일회 실행이고 스스로 도는 구성요소가 아니다. runbook 5-1은 'cron/systemd timer가 부르고 종료 코드로 알린다'고 하지만 실제 timer 설정과 알림 수신자는 '운영 서버가 정해지면'으로 미룬다. 따라서 스케줄러 정지·잡 실패·디스크·gateway 장애(C6, G1, G5의 새 DU 칸)가 사람에게 닿는 경로는 지금 구성에 없다. F1(호출자가 안 돔)은 정의도 시험도 없다. 나머지는 일회 실행 스크립트라 해당 없음.
- 해당 없음: F2~F8: 일회 읽기 실행(외부 호출은 5초 timeout으로 끝남, check_health.py)

## 4. 비기능 칸

| ID | 항목 | 현황(읽은 사실) | 기대 | 시험 | 근거 |
| --- | --- | --- | --- | --- | --- |
| N1 | 동시 요청(여러 키오스크의 동시 턴) | 서버는 모두 ThreadingHTTPServer. survey-service PostgreSQL 접근은 연결 하나 + RLock(pg.py:46-48)이라 DB 접근이 직렬화될 수 있다. [갱신] survey가 부하 측정을 했다(scripts/load_test.py, boundary.md 6-1절): 가짜 모델에서 동시 50 세션까지 모든 요청이 마감 안에 200, 100 세션은 NOT_COMMITTED 7건, 처리 한도 SURVEY_API_MAX_INFLIGHT=32 초과는 429. 이 PC 한 번의 측정(측정 당시 마감 8초). 추론 서버는 대기가 호출 타임아웃을 넘을 것 같으면 503(HTTP.md I9). | P | U | survey service.py:375; pg.py:46-48; survey docs/boundary.md:89-113(6-1절); model-runtime test_rejects_when_queue_would_exceed_wait; survey test_other_sessions_are_not_blocked_by_slow_inference. E2E에 동시 세션 시험 없음 |
| N2 | 부하(처리량·지연 분포, 목표 수치) | 목표 수치는 여전히 어느 문서에도 없다(임상 현장 동시 키오스크 대수를 알 수 없다고 survey가 적음). [갱신] survey가 측정 사실은 기록했다: 한 프로세스가 CPU(GIL) 한계에서 약 12~14 턴/초로 포화, 요청 스레드는 N에 비례(boundary.md 6-1절). 측정은 가짜 모델·루프백·이 PC 한 번이고 마감을 8초로 두었을 때의 값이며 6초로 낮춘 뒤 다시 재지 않았다. | P | U | survey scripts/load_test.py(pytest 수집 대상 아님); docs/boundary.md:89-113; head/docs/OPEN_GAPS.md:72 |
| N3 | 연결 풀/연결 수 제한 | 연결 풀은 만들지 않았다: survey가 N과 무관하게 PostgreSQL 연결 3개로 일정함을 측정했고 병목이 연결이 아니라 CPU라고 적었다(boundary.md:111). 접속 대기열은 128로 올렸다(survey 372e4a0). 그러나 PostgreSQL max_connections 대비 서비스별 연결 수 합의 산정은 여전히 없다(compose.yaml, 10-roles.sh에 설정 없음). 주 연결 문장 상한은 이제 있다(A5). | P | U | survey docs/boundary.md:89-113, scripts/load_test.py; max_connections 설정 없음(grep) |
| N4 | 같은 turn_id의 동시 중복 전송(프런트 10초 중단 뒤 재전송이 서버 처리와 겹침) | [갱신] 겹친 같은 turn_id는 두 번째가 새로 시작하지 않고 409 CONFLICT + details.reason=TURN_IN_PROGRESS + Retry-After(survey 8006a39/757351e, boundary.md:51,79). 확정된 턴은 저장된 결과 그대로. 키오스크는 이 409만 같은 turn_id로 재시도한다(kiosk-frontend design.md:47, e69d441). 순차 재전송은 같은 응답·한 번만 처리(E2E 5, E2E 5q·5w·5p의 정책 단언). 동시 겹침은 survey 단위 시험만(실제 겹침을 만드는 E2E 없음), 키오스크 모의 서버와 실제 survey를 이은 시험도 없다. | D | U | survey tests/test_turn_idempotency_deadline.py:38,62,143; kiosk-frontend test/retry.test.ts:61,212; e2e_steps.py step5(), step5q()의 idem, step5w(); survey docs/boundary.md:51,79 |
| N5 | 큰 입력 | survey API 본문 상한 64KiB이며 본문을 다 읽은 뒤 길이를 비교(api.py:47,112). 공통 클라이언트 응답 상한: JSON 256MiB, tar 8GiB(_http.py). 다른 서버(QA·ops·gate·model-runtime)의 요청 본문 상한은 grep으로 찾지 못함. | P | N | survey api.py:47,112; boundary-contracts _http.py:~180. 상한 시험은 찾지 못함 |
| N6 | 디스크 가득 | [갱신] 일부 정의: deploy check-health가 state/·BACKUP_DIR 디스크를 80% WARN·90% CRIT로 읽는다(runbook.md 5-1절, 자체 시험 있음). 서비스가 가득 찼을 때 쓰기를 거부(503)한다는 FAULT_POLICY 13은 구현되지 않았고, 영역 문서는 여전히 말이 없다. survey outbox 디스크 오류만 정의(boundary.md:77: Trace 유실, /readyz 503). pg-data, gate-data, serving-data, models-data, 백업 폴더, 컨테이너 로그(json-file 10MB x 5)가 호스트 디스크를 공유. | P | U | deploy docs/runbook.md 5-1절; scripts/test-check-health.sh:32; compose.yaml:12,40-44 |
| N7 | 시계 어긋남(호스트 시계 점프, 컨테이너 간 시각 차) | 문서 grep 0건. 시각을 쓰는 곳: 수집기의 created_at 최신 판정(collector.py), 승인 decided_at, Trace 시각, 스케줄러 last_start(scheduler.py:57-58). | ? | N | grep '시계|clock skew|ntp' 0건 |
| N8 | 재시작 중 요청(단일 컨테이너 재시작 순간) | [갱신] survey가 SIGTERM에 draining을 표시해 /readyz를 503 shutting_down으로 만들고(/healthz는 200), 새 접속을 받지 않고, 처리 중 요청이 끝나기를 기다린 뒤 저장소를 닫는다(survey 372e4a0; boundary.md:114; 단위 시험 test_readyz_db_outage.py:173). gateway는 중지 중 503 UPSTREAM_UNAVAILABLE(Caddyfile:239-253)이고 키오스크는 503을 같은 turn_id로 재시도한다. 중지 구간의 요청은 E2E 5q가 확인했다. 한계: 처리 중이던 요청이 끊기는 순간(진행 중 요청 + 재시작)은 E2E에 없고 survey 단위 시험뿐이며, 접속 대기열에 있던 미수락 연결은 버려진다(boundary.md:114). | D | E | Caddyfile:239-253; e2e_steps.py step5q(); survey docs/boundary.md:114, tests/test_readyz_db_outage.py:173 |
| N9 | 비밀 파일 회전(토큰·DSN·salt 교체) | 회전 절차·재시작 필요 여부가 문서에 없다('토큰 회전: 배포 담당, 문서에도 미정' CR-009, inference-server-spec 6절). read_secret은 호출 시 파일을 읽지만 각 서비스가 시작 때 한 번만 읽는지 요청마다 읽는지는 확인하지 못함. | ? | N | survey-service/docs/change-requests/CR-009-public-api-gaps.md:25; boundary-contracts secrets.py:17-34 |
| N10 | 비밀 파일 누락·빈 파일 | NAME_FILE을 못 읽거나 비어 있으면 SecretError로 시작 실패(secrets.py:17-28). 값 비노출은 영역별 test_secrets.py와 deploy check-secrets-hidden.sh. | D | U | boundary-contracts secrets.py; 각 영역 tests/test_secrets.py; deploy/scripts/test-check-secrets-hidden.sh(내용 읽지 못함) |
| N11 | 컨테이너 자원 제한(메모리·CPU·PID), OOM | compose.yaml에 mem_limit/cpus/ulimits/pids_limit 없음(grep). OOM으로 죽으면 restart: unless-stopped로 재시작될 뿐. | ? | N | grep 'mem|cpus|ulimit|pids' compose.yaml 0건 |
| N12 | 호스트·Docker 데몬 재부팅 뒤 기동 순서 | 서버 전체 중단은 '비보증'(D10). depends_on healthy는 최초 기동 순서를 정할 뿐 재시작 순서를 보장하지 않는다. | P | N | deploy boundary.md 6절; compose.yaml:175-181 |
| N13 | 모델 적재 중(콜드 스타트) 환자 요청 | 적재 한도 600초, 초과하면 새 릴리스를 거부하고 이전 릴리스 유지, 적재 중에도 /healthz 유지. 실제 GPU 적재 시간은 gpu-dev 1회 약 2분 30초(OPEN_GAPS U01). | D | U | survey test_loader_retry.py:235,301; inference-server-spec 5절 |
| N14 | 추론 서버 대기열 상한 3초, 적재 PUT 대기 3초 | 대기가 길면 큐에 쌓지 않고 503(재시도 가능). | D | U | model-runtime server.py:16,260-264; test_rejects_when_queue_would_exceed_wait |
| N15 | 로그 회전·폭주 | json-file 10MB x 5개로 회전(compose.yaml:12). 로그 폭주 시 동작은 시험하지 않음. | P | N | compose.yaml:12; deploy/docs/design.md:135 |
| N16 | 주기 잡 겹침·중복 실행 | flock 잠금으로 이미 실행 중이면 BUSY(scheduler.py:60-63). 잡은 멱등(같은 입력 같은 결과)으로 설계(D39). BUSY 경로 시험은 읽지 못함. | D | N | scheduler.py:60-63; e2e.sh:181-183은 기한 주기만 확인 |
| N17 | 쓰기 도중 강제 종료(kill -9, 전원 차단) | 응답 유실·커밋 불확실 재시도는 멱등으로 설계(survey write_outcome UNKNOWN, QA test_write_retry_after_lost_commit_ack_is_idempotent, test_confirm_retry_after_crash). deploy E2E는 docker stop(SIGTERM)만 쓰고 kill은 쓰지 않는다. | D | U | survey boundary.md 5절; question-authoring tests/test_postgres_specific.py:94, test_service_acceptance.py:98 |
| N18 | TLS·인증서 만료 | TLS 종단 미구성(운영 도메인 미정, Caddyfile 주석). 지금은 평문 HTTP. | ? | N | Caddyfile:186 주석; STATUS BLOCKED 항목 |
| N19 | 백업→복구 뒤 정합 | 파일 저장소와 PostgreSQL 5개 DB를 백업하고 복구한 뒤 해시·행 지문과 Trace 재전송 DUPLICATE까지 확인. | D | E | e2e.sh:187-205; scripts/e2e_verify_restore.py |
| N20 | 서비스 이름 DNS 해석(재시작 뒤 IP 변경) | 서비스는 Compose 서비스 이름으로 서로 부른다(*.env). model-serving 재시작 뒤 같은 이름으로 복구되는 것이 E2E 5에서 간접 확인된다. 다른 서비스 재시작에서의 이름 재해석은 시험하지 않음. | P | E | survey.env; e2e_steps.py step5() 추론 서버 stop/start 절 |
| N21 | 타임아웃 불변식(키오스크 대기 10초 > gateway 환자 API 9.5초 > 서버 턴 총 마감 6초) | survey boundary.md:50-55가 시간 불변식을 적고 Caddyfile:193-202에 gateway 상한 1s+8.5s가 있다. E2E 5w가 gateway 접근 로그 duration이 6.0 이상 10.0 미만임을 단언(두 환경 실측 8.5s), 5p가 DB 중지 중 턴 6.5s 이내를 단언(실측 4.0s·3.7s). 서버 6초 마감이 실제로 발동하는 경로는 E2E에서 건드리지 않았다(DB 중지는 접속 실패로 4초에 503). 설정값 3개가 서로 다른 리포지토리(kiosk-frontend retry.ts, deploy Caddyfile, survey settings.py)에 있어 한쪽 변경이 불변식을 깰 수 있다. | D | E | survey docs/boundary.md:50-55; deploy config/Caddyfile:193-202; e2e_steps.py step5w(), step5p()의 pol_deadline |
| N22 | 클라이언트·gateway가 포기한 뒤 서버가 늦게 확정하는 턴 | E2E 5w에서 survey를 pause한 채 보낸 요청은 gateway가 504로 끝냈지만 unpause 뒤 서비스가 그 요청을 처리했다(관찰 처리 횟수 1, 두 환경). 같은 turn_id 재전송 뒤 발화 기록은 한 번이라는 단언은 통과. survey boundary.md:52는 '마감 직전 시작된 확정은 뒤늦게 반영될 수 있다'는 한계만 적고 pause 뒤 처리는 적지 않았다. 키오스크 입장에서는 실패(직원 호출 또는 재시도)인데 서버는 값을 확정한 상태가 될 수 있어, 재시도하지 않고 직원 호출로 간 환자의 값이 저장되는 경우가 생긴다. | P | E | e2e_steps.py step5w()(관찰 출력 '처리된 횟수'); survey docs/boundary.md:52 |

합계 22행: 기대 D 9 / P 9 / ? 4; 시험 E 5 / U 9 / N 8. (초안 20행: D 6 / P 5 / ? 9; E 2 / U 5 / N 13)

## 5. 타임아웃·재시도 일람과 환자 경로 최대 대기

| 호출자 -> 대상 | 타임아웃 | 재시도 규칙 | 근거 |
| --- | --- | --- | --- |
| 키오스크 브라우저 -> gateway | 시도당 AbortController 10초 | 429·502·503·504·네트워크 오류·무응답을 같은 turn_id로 지수 백오프(0.5초 x2, 상한 5초, 지터 50~100%, Retry-After 이상) 재시도, 총 예산 20초(시작한 시도는 끊지 않아 최악 약 30초). 409는 details.reason=TURN_IN_PROGRESS만 재시도. 500·그 밖의 4xx 재시도 없음 | client.ts; api/retry.ts; kiosk-frontend docs/design.md:32-35,47 |
| gateway -> survey/ops/gate 등 | 환자 API: 연결 1s + 응답 헤더 8.5s(합 9.5s). 직원 API: 2s + 10s(SSE read_timeout 1h). /readyz: 1s + 2s. 정적 화면: 2s + 10s. 게이트·ops·admin-console 프록시(C7·C8·D6): 명시 없음(Caddy 기본, 미확인) | gateway 재시도 없음(lb_try_duration 0). 연결 거부 -> 503, 시간 초과 -> 504, 본문 {"code":"UPSTREAM_UNAVAILABLE"} + Retry-After 2 | Caddyfile:25-43,51-58,81-173,193-202,218-233,239-253 |
| survey -> model-serving | 읽기 4초(SURVEY_INFERENCE_TIMEOUT_SECONDS). urlopen timeout이라 소켓 단위(총 시간 아님, 추정) | 연결 실패·502/503/504는 1회(0.2초), 읽기 타임아웃은 재시도 없음, extract OUTPUT_INVALID는 그래프가 1회 더. 적재 신호: 최대 600초 확인 | settings.py:132-133; inference-server-spec 5절 |
| survey -> PostgreSQL(주 연결) | 접속 2초(SURVEY_DB_CONNECT_TIMEOUT_SECONDS), 문장 2초(SURVEY_DB_STATEMENT_TIMEOUT_SECONDS)+서버가 얼면 1초 뒤 소켓 강제 종료. 접속 실패 뒤 1초 재접속 유예. 서버 턴 총 마감 6초(SURVEY_TURN_DEADLINE_SECONDS)가 락 대기·멱등 확인·모델 호출·DB를 모두 덮음 | 트랜잭션 밖 멱등 한 문장만 새 연결로 1회 재시도, 트랜잭션 도중 끊김은 재시도 없음. 마감 초과는 NOT_COMMITTED(늦은 작업은 확정하지 않음) | survey settings.py:141-145; pg.py:34-119; docs/boundary.md:50-55 |
| survey -> PostgreSQL(/readyz 확인) | 2초(+1초 여유), 주 연결·락을 쓰지 않는 별도 연결, 세 저장소 동시 확인 | - | settings.py:145; pg.py; boundary.md:48 |
| survey -> release-gate(I4) | 10초(SURVEY_HTTP_TIMEOUT_SECONDS), 폴링 5초 | 적재 실패는 백오프 후 재시도, 결정적 오류는 영구 거부 | settings.py:135; clients.py:30; survey.env:11; test_loader_retry.py |
| survey -> ops-feedback-ingest(I6) | 10초 | UNAVAILABLE만 지수 백오프 1~60초, 예기치 않은 예외는 20회 뒤 DEAD | exporter.py:66-70,118-139 |
| survey -> 웹 푸시 | 3초 | 없음(경로 없으면 DELIVERY_FAILED) | settings.py:74 |
| model-serving -> release-gate(I4) | 120초(번들 읽기), /healthz 확인 2초 | 적재 요청(PUT)을 survey가 멱등 재호출 | server.py:149,399 |
| release-gate -> question-authoring/model-registry | 30초(GATE_I1_TIMEOUT, GATE_I3_TIMEOUT 환경 변수 없으면) | 다음 주기(Loop 60초)에 재시도 | factories.py:24; main.py:191 |
| release-gate -> PostgreSQL | 접속 3초, 문장 3초(+얼면 1초), /readyz 2초(GATE_DB_*) | 재접속 재시도 없음(호출자가 다시 요청). 수집·판정 잡은 상한 안에 종료 코드 75 | release-gate docs/boundary.md:43-53; postgres_store.py:41; main.py:188-190 |
| question-authoring -> ops-feedback(I7) | 10초(기본값, 호출 지점에서 지정 안 함) | 없음(요청 단위) | boundary-contracts _http.py:182; __main__.py:47 |
| question-authoring -> PostgreSQL | 접속 3초, 문장 3초(+얼면 1초, 호출 하나 최악 4초), /readyz 2초(QA_*) | 연결 끊김 재접속 | question-authoring docs/boundary.md:46-59; __main__.py:44-46 |
| ops-feedback(서버·잡) -> PostgreSQL | 접속 3초, 문장 3초(+얼면 1초), /readyz 2초, 시작 때 스키마 30초(OPS_DB_*) | 연결이 끊긴 것으로 보이면 재접속 1회(최악 약 7초). 잡은 종료 코드 2(처리 오류는 1) | ops-feedback pgbase.py:20-23; docs/boundary.md:64-70 |
| ops-feedback 잡 -> release-gate(I4/I5) | 10초(HttpReleaseReader 기본값) | 롤백 요청은 저장 후 같은 id 재전송(다음 실행) | ops-feedback-job.yaml:41-42; test_rollback.py:45 |
| job-release-gate-collect -> QA/registry | 30초 | 스케줄러 다음 주기(600초) | factories.py:24; jobs.yaml |
| scheduler -> 잡 컨테이너 | 잡당 3600초(--timeout), 초과하면 종료 코드 124 | 다음 주기 | scheduler.py:17,67-70 |
| admin-console -> gateway | 15초 | (재시도 규칙 http.ts에서 찾지 못함) | admin-console/api/http.ts:54 |
| synthetic-data -> QA/ops | 10초 | 읽지 못함 | synthetic_data/adapters.py:25-30 |
| model-runtime 추론 큐 | 대기 3초 초과 시 503 | - | server.py:16 |
| 스케줄러·점검 -> check-health | 외부 감시 대상 호출 5초(urlopen), 잡 정지 판정: 주기의 2배+60초, 미종료 1시간 | 읽기 전용 일회 실행(호출 주체 미배치) | scripts/check_health.py; runbook.md 5-1절 |

**환자 경로 최대 대기 (설정값에서 읽은 값과 계산. 실측으로 적은 것만 실측).**

- 불변식: 키오스크 한 시도 10초 > gateway 9.5초(연결 1 + 응답 헤더 8.5) > 서버 턴 총 마감 6초(survey `SURVEY_TURN_DEADLINE_SECONDS`, 요청 수신부터). 6초는 survey가 DB 장애 최악 경로 측정값 5.0초(pause, 이 PC 1회)에서 정했다(boundary.md:55).
- 서버 쪽 한 턴: 이제 상한이 있다(6초). 호출별 timeout 합(extract 4초 + 재시도 + respond 4초 + DB)이 아니라 총 마감이 락 대기·멱등 확인·모델 호출(재시도 포함)·DB 대기·쓰기 확정을 덮는다. 넘으면 NOT_COMMITTED 응답, 마감 뒤에는 모델을 부르지 않고 쓰기 확정을 시작하지 않는다. 한계: 마감 직전에 시작한 확정은 뒤늦게 반영될 수 있다(boundary.md:52).
- gateway 쪽: 연결 거부 1초대 503, 응답 없음 8.5초 뒤 504(5w 실측 8.5초, 두 환경). 재시도 없음.
- 키오스크 쪽: 시도당 10초, 총 재시도 예산 20초(지수 백오프 0.5초 x2 상한 5초, 지터), 시작한 시도는 끊지 않으므로 최악 약 30초 뒤 직원 호출(design.md:35). Retry-After가 남은 예산보다 길면 기다리지 않고 직원 호출. 이 값들이 현장 흐름에 맞는지는 사용자 결정 대기이고 실측하지 못했다.
- DB 중지 중 한 턴: 이 PC 4.0초, gpu-dev 3.7초(5p, gateway 경유 503 UNAVAILABLE retryable). DB pause 중 한 턴: survey 단위 측정 5.0초(이 PC, E2E 아님).
- 위 중 서버 6초 마감이 실제로 발동하는 경로, 키오스크 예산 소진 경로는 컨테이너 조합에서 확인하지 않았다.

## 6. 이 문서로 닫히지 않는 것

- 간선 추가 누락(2절 한계). 특히 `synthetic-data`, `model-lab` 내부와 GPU 서버 쪽 호출은 얕게만 봤다.
- 칸 안의 '장애 방식'이 서로 겹치는 경우(예: F4 재시작은 F1 중지와 F2 복구의 합)를 모두 분해하지 않았다. 동시에 둘 이상 일어나는 장애(DB 중지 중 model-serving 재시작 등) 조합은 칸으로 두지 않았다.
- 이 파일의 숫자는 이 파일 안의 표를 센 값이다(`E2E` 통과 수 같은 다른 영역 사실은 정본 `deploy/docs/E2E_RESULTS.md`가 갖는다. 이 파일은 통과 수를 적지 않고 그 정본의 두 줄을 읽은 것이고 숫자의 정본이 아니다).
- 기대 동작 열의 'D'는 영역 문서가 정의했다는 뜻이지 그 정의가 옳다는 판단이 아니다. 예: 위험 신호가 있어도 쓰기 확정이 실패한 턴은 직원 알림을 보내지 않는다는 survey 문서의 '주의(안전)'는 도메인 소유자 확인 대기다(survey boundary.md:87).
- U 칸의 통과 여부는 확인하지 않았다. 영역 시험이 DB 컨테이너를 pause하는 것들은 Docker 접근이 없으면 skip된다(예: test_turn_db_outage_bounds.py:68).
- `FAULT_POLICY.md`는 head의 정책이다. 이 문서는 영역 문서(와 deploy의 E2E.md·Caddyfile 주석)에 정의된 것만 D로 세었고 정책에만 있는 것은 P 또는 ?로 두었다.

