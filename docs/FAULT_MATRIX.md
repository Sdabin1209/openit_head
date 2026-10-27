# 장애 경우의 수 닫힌 목록 (FAULT_MATRIX)

> 작성: 헤드 조사 담당(읽기 전용 조사, 2026-10-28). 상태: **초안, 헤드 검토 전**. 증명이 아니라 '닫힌 목록'이다: 찾은 간선 40개와 각 간선의 장애 방식 칸을 모두 나열하고 칸마다 기대 동작 정의 여부와 시험 여부를 적는다. 목록에 없는 간선이 있을 수 있다(2절의 검색 방법으로 누구나 다시 찾아 보태라).

**읽는 법 (두 글자 코드).** 앞 글자 = 기대 동작이 영역 문서에 정의되어 있는가. 뒤 글자 = 시험 근거.

| 코드 | 뜻 |
| --- | --- |
| D | 기대 동작이 영역 문서(boundary/design/runbook/HTTP.md)에 정의되어 있다 |
| P | 부분 정의: 코드나 단위 시험으로 동작은 보이나 영역 문서에는 없거나 일부만 있다 |
| ? | **기대 동작 미정의**: 문서에서 찾지 못했다(이 문서가 찾은 가장 중요한 빈칸) |
| E | deploy E2E(`scripts/e2e_steps.py`, `e2e.sh`)가 그 장애를 일으켜 확인한다 |
| U | 영역 단위 시험만 있다(영역 `tests/`, mock·가짜 서버 포함). 실제 컨테이너 조합에서는 안 해 봄 |
| N | 안 함: 시험 근거를 찾지 못했다 |
| -- | 해당 없음(이유는 3절 간선 설명) |

**주의 1.** 시험 코드는 '그 시험이 저장소에 있는가'를 뜻하고 '지금 통과하는가'가 아니다. 통과 여부는 `deploy/docs/E2E_RESULTS.md`(정본)를 보며, 이 조사에서는 그 실행 기록을 읽지 않았다. **주의 2.** 'E'로 표시한 칸도 시험이 보는 범위가 좁을 수 있다(예: E2E 5p는 postgres 중지 중 `/readyz`만 보고 환자 턴은 보지 않는다). 해당 한계는 3절 설명에 적었다. **주의 3.** 다른 환경에서 한 번 더 확인한 칸은 없다(E2E 통과 기록은 한 환경 기준, `deploy/docs/STATUS.md:185`).

장애 방식: F1 중지(연결 거부), F2 멈춤(연결은 되나 무응답), F3 느림, F4 재시작, F5 5xx 응답, F6 잘못된/깨진 응답 본문, F7 인증 실패(401/403), F8 네트워크 분리. 볼륨·정적 파일처럼 네트워크 호출이 아닌 간선은 해당 없는 칸에 이유를 적었다.

## 1. 요약 (분모 명시)

- 간선 40개 x 장애 방식 8 = **320칸**. 그중 해당 없음 53칸, **해당 있는 칸 267**(이하 비율의 분모).
- 기대 동작: 정의됨(D) 119/267, 부분(P) 59/267, **미정의(?) 89/267**.
- 시험: E2E 시험함(E) 26/267, 영역 단위 시험만(U) 85/267, 안 함(N) 156/267.
- 조합(기대+시험): ?N 89, DU 84, PN 58, DE 26, DN 9, PU 1 (합 267).
- 비기능 칸(4절) 20행: 기대 D 6, P 5, ? 9; 시험 E 2, U 5, N 13. 타임아웃 일람은 5절.
- 한 줄 결론: 장애를 일부러 일으키는 E2E는 **세 가지뿐**이다: model-serving 중지·기동(단계 5), PostgreSQL 중지·기동(단계 5p, `/readyz`만 관찰), 백업·복구(단계 9). 나머지 칸은 영역 단위(mock) 시험이거나 시험이 없다. 환자 경로의 gateway-survey 구간(A2)은 정의도 시험도 없다.

### 기대 동작 미정의('?') 칸 목록 (간선: 장애 방식)

| 간선 | 미정의 칸 | 칸 수 |
| --- | --- | --- |
| A1 키오스크 브라우저 -> gateway(Caddy) | F6 | 1 |
| A2 gateway -> survey-service(키오스크 API·직원 API 프록시) | F1, F2, F4, F5, F6, F7, F8 | 7 |
| A3 gateway -> kiosk-frontend(정적 화면) | F1, F2, F3, F4, F8 | 5 |
| A5 survey-service -> PostgreSQL(survey DB) | F2, F3, F5, F6, F7 | 5 |
| A6 survey-service -> ops-feedback-ingest(I6 Trace, outbox 경유) | F2 | 1 |
| A8 survey-service -> survey-data 볼륨(releases/ 사본) | F1, F6 | 2 |
| A10 직원 브라우저 SSE -> gateway -> survey-service(알림 스트림) | F4, F5, F8 | 3 |
| B1 model-serving -> release-gate(I4 번들 읽기, PUT 적재 때) | F8 | 1 |
| B3 model-serving -> HuggingFace(외부 인터넷, GPU/LLM 모드만) | F6, F7 | 2 |
| B4 (외부 추론 모드) survey-service -> 외부 추론 서버 / 외부 서버 -> release-gate | F8 | 1 |
| C1 release-gate 서버(Loop 60초) -> question-authoring(I1) | F8 | 1 |
| C2 release-gate 서버(Loop 60초) -> model-registry(I3) | F8 | 1 |
| C3 job-release-gate-collect -> question-authoring(I1)·model-registry(I3), gate DB에 접수 기록 | F8 | 1 |
| C4 release-gate(서버·수집 잡) -> PostgreSQL(gate DB) | F2, F3, F5, F6, F7 | 5 |
| C5 release-gate·수집 잡 -> gate-data 볼륨(번들 파일 releases/) | F1 | 1 |
| C6 scheduler.py(호스트) -> docker compose run --rm <잡> | F2, F4, F6, F8 | 4 |
| C7 admin-console 브라우저 -> gateway -> release-gate(승인 조회·결정) | F8 | 1 |
| C8 operator -> gateway -> release-gate(activate·rollback·active-pointer) | F8 | 1 |
| D1 job-ops-feedback -> PostgreSQL(ops_log, ops_failure) | F2, F3, F5, F6, F7 | 5 |
| D2 job-ops-feedback -> release-gate(I4 읽기) | F8 | 1 |
| D3 job-ops-feedback -> release-gate(I5 롤백 요청) [운영 설정에 연결 없음] | F2, F8 | 2 |
| D4 ops-feedback-ingest(서버) -> PostgreSQL(ops_log, ops_failure) | F2, F3, F6, F7 | 4 |
| D5 question-authoring -> ops-feedback-ingest(I7 개선 신호 읽기) | F8 | 1 |
| D6 reviewer 브라우저 -> gateway -> ops-feedback-ingest(검토 게시) | F8 | 1 |
| E1 question-authoring -> PostgreSQL(qa DB) | F2, F3, F6, F7 | 4 |
| E2 저자 클라이언트 -> question-authoring(문항 등록·검수) | F1, F2, F3, F4, F5, F6, F7, F8 | 8 |
| F1 model-lab(GPU 서버, 컴포즈 밖) -> model-registry(I3 publish) | F8 | 1 |
| F3 synthetic-data(컴포즈 밖) -> question-authoring(I1)·ops-feedback(I7)·(I2는 HTTP 면 없음) | F8 | 1 |
| G1 PostgreSQL -> pg-data 볼륨(디스크) | F1, F6 | 2 |
| G2 deploy up/rollback -> 로컬 레지스트리(compose.registry.yaml, 이미지 pull) | F6, F8 | 2 |
| G3 backup job -> postgres(pg_dump) / BACKUP_DIR 디스크 | F2, F3, F4, F6, F8 | 5 |
| G4 Docker 데몬/호스트 -> 컨테이너 재시작(restart: unless-stopped) | F4 | 1 |
| G5 외부 감시 -> gateway /healthz (서버 밖) | F1 | 1 |
| G7 병원/의사 시스템 -> survey 결과 조회 API / 위험 신호 감지기 -> survey risk-signals API | F1, F2, F3, F4, F5, F6, F8 | 7 |
| (합계) | | 89 |

장애 방식별 미정의 칸 수: F1 8, F2 13, F3 9, F4 8, F5 7, F6 15, F7 8, F8 21. F8(분리) 칸의 다수는 F1·F2와 증상이 같아 보이나(연결 실패·타임아웃) 그렇다고 적은 문서가 없어 미정의로 센다.

비기능에서 미정의: N2 부하, N3 연결 풀/연결 수 제한, N4 같은 turn_id의 동시 중복 전송, N6 디스크 가득, N7 시계 어긋남, N8 재시작 중 요청, N9 비밀 파일 회전, N11 컨테이너 자원 제한, N18 TLS·인증서 만료.

### 우선순위 (환자 안전과 데이터 손실에 닿는 것 먼저)

| 순위 | 칸 | 왜 | 해야 할 일(제안, 미결정) |
| --- | --- | --- | --- |
| P0-1 | A2 F1·F2·F4·F5 (gateway-survey 구간) | 환자 경로. survey가 죽거나 재시작하는 순간 gateway의 응답이 정의되어 있지 않고, 프런트는 502/504에서 재시도 없이 직원 호출 화면으로 간다(flow.ts:152). 재시작 한 번에 모든 키오스크가 동시에 직원 호출로 갈 수 있다. E2E 없음. | 기대 동작을 정하고(재시도할 상태 코드 포함) survey 중지·재시작 E2E 단계를 만든다 |
| P0-2 | A4 총 대기 / N4 같은 turn_id 동시 중복 | 서버 한 턴의 최악 시간에 총 상한이 없다. 읽기 4초는 소켓 단위이고, extract 재시도+respond를 합하면 계산상 10초를 넘을 수 있다(5절). 프런트는 10초에 중단하고 같은 turn_id를 다시 보내므로 처리 중인 턴과 겹친다. 겹침 동작이 문서에 없다. | 턴 총 마감 시간과 겹침 시의 기대(같은 결과/409/대기)를 정하고 단위·E2E로 확인 |
| P0-3 | A5 F2·F3 / C4 F2·F3 / D4 F2·F3 (DB 무응답) | PostgreSQL이 TCP는 받되 응답이 없는 경우 주 연결에 statement_timeout이 없다. 턴이 DB 락/쿼리에서 얼마나 멈추는지 정의가 없고, 시험은 '중지'(5p)뿐이다. | statement_timeout과 기대 동작을 정하고 pause/네트워크 지연 시험을 추가 |
| P0-4 | A5 F1의 환자 턴 (5p의 한계) | E2E 5p는 /readyz만 본다. DB 중지 중 환자 턴이 NOT_COMMITTED로 가고 화면이 '다시 말해 주세요'가 되는지, 위험 발화가 있을 때 알림이 나가지 않는 주의(survey boundary.md 6절)가 실제로 어떻게 보이는지 컨테이너 조합에서 본 적이 없다. | 5p에 중지 중 턴 1회 추가 |
| P0-5 | A9·A10·G7 (직원 알림 경로) | 위험 환자 경로의 끝. 알림 입력원이 지금 활성이 아니고(G01), 푸시·SSE 장애·재시작 중 알림 유실 여부가 문서에 없고, 실제 푸시는 E2E 불가. | G01 결정 후 알림 경로 장애 기대를 정한다 |
| P1-1 | A6 F7 (Trace 토큰 불일치) | PERMISSION_DENIED는 재시도 없이 DEAD로 옮겨진다(test_trace_export.py:93). 토큰 회전·오설정 시 Trace가 조용히 유실되는 방향이며 이를 알리는 신호가 /readyz에 있는지 읽지 못했다. | DEAD 건수의 감시 신호 확인 |
| P1-2 | N6 디스크 가득 / G1 | 5개 DB가 단일 PostgreSQL 컨테이너·단일 볼륨이고 백업 폴더·로그와 호스트 디스크를 공유한다. 가득 찼을 때 동작과 경보가 문서에 없다. | 경보·상한과 기대 동작 정의 |
| P1-3 | D3 (자동 롤백 간선) | 운영 잡 설정에 gate_service가 없고 rollback 기준이 null이다. 나쁜 릴리스 감지 후 롤백이 사람 손에만 달려 있다. E2E 8은 테스트 하니스가 직접 요청한 것. | 사용자 결정(롤백 기준) 후 운영 설정 연결과 E2E |
| P1-4 | C6·G5 (스케줄러·감시) | 스케줄러가 멈추거나 잡이 FAIL이어도 알리는 곳이 없고 외부 감시는 예시 파일뿐이다. gateway /healthz·/readyz는 정적 200. | 감시 대상을 정하고(D10 미정) gateway readyz 의미를 정의 |
| P2 | E2 / N9 / N11 / N7 / N3 / N2 외 나머지 ? | 저작 입력 경로 운영 부재, 비밀 회전, OOM, 시계, 연결 수, 부하. 위 항목 처리 뒤. |  |

### 가장 위험한 미시험/미정의 칸 10개

1. A2 F1/F2/F4: survey 중지·멈춤·재시작 때 gateway가 환자에게 무엇을 주는지 미정의, 시험 없음 (프런트는 502에서 즉시 직원 호출).
2. A4 총 대기 / N4: 서버 턴 총 시간 상한 없음, 10초 중단 뒤 같은 turn_id 동시 재전송의 동작 미정의.
3. A5 F2/F3: survey가 PostgreSQL 무응답일 때 주 연결 statement_timeout 없음, 정의·시험 없음.
4. A5 F1 중 환자 턴: E2E 5p가 /readyz만 봐서 중지 중 환자 턴(NOT_COMMITTED, 위험 알림 미발송 주의)은 컨테이너 조합에서 미시험.
5. A9/A10: 직원 알림 전달(푸시·SSE) 장애와 재시작 중 유실, 입력원 비활성(G01), E2E 불가.
6. A6 F7: Trace 인증 실패 -> DEAD 유실 방향, 알림 신호 미확인.
7. D3: 자동 롤백 간선이 운영 설정에 연결되어 있지 않음(rollback: null, gate_service 없음).
8. N6/G1: 디스크 가득 미정의 (단일 PostgreSQL 볼륨에 5개 DB).
9. C6/G5: 스케줄러·서버 중단을 알리는 감시 부재, gateway /readyz 정적.
10. E2: 운영 구성에서 저자가 문항을 올리는 경로 없음(포트·gateway 경로 없음) - 의도 여부 확인 필요.

## 2. 간선을 찾은 방법 (재현 가능, 닫힌 목록의 한계)

간선 = 호출자 -> 대상 중 런타임에 일어나는 것(HTTP, DB 연결, 볼륨 공유, 스케줄러 실행, 외부 서비스 호출). 아래 순서로 찾았고, **여기서 놓친 간선은 이 문서에도 없다.** 다시 돌려서 새로 나오는 줄이 있으면 이 문서에 보탠다. 경로는 모두 `/home/user/sdabin/healthKiosk` 기준.

1. Compose 구조: `deploy/compose*.yaml`, `deploy/test/compose.fake-model.yaml`을 통째로 읽음(networks, volumes, secrets, depends_on, env_file, ports, profiles jobs).
2. 환경 변수 URL: `grep -nE '_URL|FACTORY|TIMEOUT|POLL' deploy/config/*.env`(비밀 파일 `secrets/`와 토큰 값은 열지 않았다. `cat config/*.env` 형태는 도구가 거부해 URL·타임아웃 줄만 grep).
3. 게이트웨이: `grep -nE 'reverse_proxy|handle|timeout' deploy/config/Caddyfile`.
4. 클라이언트 생성: `grep -rnE 'Http(QuestionReader|ModelRegistry|ReleaseReader|GateService|FailureStore|TraceIngest|DatasetStore|ModelRuntime)|boundary_contracts.clients' --include=*.py --include=*.yaml <각 영역>`.
5. 타임아웃·재시도: `grep -rnE 'timeout|TIMEOUT|retries|retry' <영역 소스>`; `grep -rnE 'ConnectionPool|psycopg_pool|max_connections|statement_timeout'`.
6. 서버 종류·본문 상한: `grep -rnE 'ThreadingHTTPServer|MAX_BODY|Content-Length'`.
7. 스케줄러·잡: `deploy/config/jobs.yaml`, `deploy/scripts/scheduler.py`, `run-job.sh`, `backup*.sh`.
8. 계약: `boundary-contracts/HTTP.md` 전체, `boundary-contracts/boundary_contracts/clients/_http.py`(오류 분류).
9. 영역 문서: 각 영역 `docs/boundary.md`의 '장애 영향'(또는 '장애') 절, survey-service `docs/inference-server-spec.md` 5절, kiosk-frontend `docs/design.md`.
10. 시험: `deploy/scripts/e2e_steps.py`(`grep -nE 'docker, "(stop|start)"|"stop"|kill|pause'`로 장애 주입 지점 확인: 5의 model-serving, 5p의 postgres 둘뿐), `deploy/scripts/e2e.sh`(차단 단언 119-142, 백업·복구 187-205, 스케줄러 181-183), 영역 `tests/`(`grep -rnE 'def test_\w*(unavail|down|refus|timeout|slow|retry|503|401|403|corrupt|tamper|reconnect|restart|concurren)'`).

**읽지 못한/얕게 읽은 것**: `secrets/` 전체(의도적으로 열지 않음), `deploy/config/*.env`의 값(URL·타임아웃 줄만 grep), `synthetic-data/`(어댑터 소스만 grep, docs 미열람), `turn-engine/`(런타임 간선 없음으로 보고 열지 않음), `model-lab` 내부(경계 문서·팩토리만), `admin-console`/`kiosk-frontend` 테스트 본문(파일 이름과 일부 줄만), `deploy/docs/E2E_RESULTS.md`의 실행 기록 표(현재 통과 여부 미확인), `deploy/scripts/test-*.sh`·`check-*.sh` 내용, `midterm presentation/`. Caddy의 기본 타임아웃과 502/504 동작은 문서·코드에서 확인하지 못했다(추정으로 표시).

**이 조사가 정적 읽기만 했다는 점**: 아무 컨테이너도 띄우거나 멈추지 않았다. 아래 '시험함'은 시험 코드를 읽어 얻은 사실이다.

## 3. 간선 x 장애 방식 행렬

| ID | 구분 | 호출자 -> 대상 | F1 중지 | F2 멈춤 | F3 느림 | F4 재시작 | F5 5xx | F6 깨진 본문 | F7 인증 실패 | F8 분리 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 환자 | 키오스크 브라우저 -> gateway(Caddy) | DU | DU | DU | PN | PU | ?N | DU | PN |
| A2 | 환자 | gateway -> survey-service(키오스크 API·직원 API 프록시) | ?N | ?N | PN | ?N | ?N | ?N | ?N | ?N |
| A3 | 환자 | gateway -> kiosk-frontend(정적 화면) | ?N | ?N | ?N | ?N | -- | -- | -- | ?N |
| A4 | 환자 | survey-service -> model-serving(I9 extract/respond/PUT 적재) | DE | DU | DU | DE | DU | DU | DU | PN |
| A5 | 환자 | survey-service -> PostgreSQL(survey DB) | DE | ?N | ?N | DE | ?N | ?N | ?N | DE |
| A6 | 환자 | survey-service -> ops-feedback-ingest(I6 Trace, outbox 경유) | DU | ?N | DU | DU | DU | DU | DU | PN |
| A7 | 환자 | survey-service -> release-gate(I4 활성 포인터 폴링 5초, load_bundle) | DU | DU | DU | DU | DU | DU | DU | PN |
| A8 | 환자 | survey-service -> survey-data 볼륨(releases/ 사본) | ?N | -- | -- | DN | -- | ?N | -- | -- |
| A9 | 환자·직원 | survey-service -> 웹 푸시 서비스(외부 인터넷, VAPID) | DU | PN | PN | -- | PN | PN | PN | PN |
| A10 | 직원 | 직원 브라우저 SSE -> gateway -> survey-service(알림 스트림) | PN | PN | -- | ?N | ?N | -- | DE | ?N |
| B1 | 환자(적재) | model-serving -> release-gate(I4 번들 읽기, PUT 적재 때) | DU | DU | DU | DU | DU | DU | DU | ?N |
| B2 | 환자(적재) | model-serving -> serving-data 볼륨(번들 캐시) | DU | -- | -- | DN | -- | DU | -- | -- |
| B3 | 환자(적재) | model-serving -> HuggingFace(외부 인터넷, GPU/LLM 모드만) | PN | PN | PN | -- | PN | ?N | ?N | PN |
| B4 | 환자 | (외부 추론 모드) survey-service -> 외부 추론 서버 / 외부 서버 -> release-gate | PN | PN | PN | PN | PN | PN | PN | ?N |
| C1 | 출고 | release-gate 서버(Loop 60초) -> question-authoring(I1) | DU | DU | DU | DU | DU | DU | DU | ?N |
| C2 | 출고 | release-gate 서버(Loop 60초) -> model-registry(I3) | DU | DU | DU | DU | DU | DU | DU | ?N |
| C3 | 출고 | job-release-gate-collect -> question-authoring(I1)·model-registry(I3), gate DB에 접수 기록 | DU | DU | DU | DU | DU | DU | DU | ?N |
| C4 | 출고·데이터 | release-gate(서버·수집 잡) -> PostgreSQL(gate DB) | DE | ?N | ?N | DE | ?N | ?N | ?N | DE |
| C5 | 출고 | release-gate·수집 잡 -> gate-data 볼륨(번들 파일 releases/) | ?N | -- | -- | DN | -- | DU | -- | -- |
| C6 | 출고 | scheduler.py(호스트) -> docker compose run --rm <잡> | DN | ?N | DN | ?N | DN | ?N | -- | ?N |
| C7 | 출고 | admin-console 브라우저 -> gateway -> release-gate(승인 조회·결정) | DU | DU | DU | DU | DU | DU | DE | ?N |
| C8 | 출고 | operator -> gateway -> release-gate(activate·rollback·active-pointer) | PN | PN | PN | PN | PN | PN | DE | ?N |
| D1 | 피드백 | job-ops-feedback -> PostgreSQL(ops_log, ops_failure) | DE | ?N | ?N | DE | ?N | ?N | ?N | DE |
| D2 | 피드백 | job-ops-feedback -> release-gate(I4 읽기) | PN | PN | PN | PN | PN | PN | PN | ?N |
| D3 | 피드백 | job-ops-feedback -> release-gate(I5 롤백 요청) [운영 설정에 연결 없음] | DU | ?N | DU | DU | DU | DU | DU | ?N |
| D4 | 피드백 | ops-feedback-ingest(서버) -> PostgreSQL(ops_log, ops_failure) | DE | ?N | ?N | DE | DU | ?N | ?N | DE |
| D5 | 피드백 | question-authoring -> ops-feedback-ingest(I7 개선 신호 읽기) | DU | DU | DU | DU | DU | DU | DU | ?N |
| D6 | 피드백 | reviewer 브라우저 -> gateway -> ops-feedback-ingest(검토 게시) | PN | PN | PN | PN | PN | PN | DE | ?N |
| E1 | 저작 | question-authoring -> PostgreSQL(qa DB) | DE | ?N | ?N | DE | DU | ?N | ?N | DE |
| E2 | 저작 | 저자 클라이언트 -> question-authoring(문항 등록·검수) | ?N | ?N | ?N | ?N | ?N | ?N | ?N | ?N |
| F1 | 모델 게시 | model-lab(GPU 서버, 컴포즈 밖) -> model-registry(I3 publish) | DU | DU | DU | DU | DU | DU | DU | ?N |
| F2 | 모델 게시 | model-registry -> models-data 볼륨 | DU | -- | -- | DN | -- | DU | -- | -- |
| F3 | 데이터 | synthetic-data(컴포즈 밖) -> question-authoring(I1)·ops-feedback(I7)·(I2는 HTTP 면 없음) | PN | PN | PN | PN | PN | PN | PN | ?N |
| G1 | 인프라 | PostgreSQL -> pg-data 볼륨(디스크) | ?N | -- | -- | DE | -- | ?N | -- | -- |
| G2 | 인프라 | deploy up/rollback -> 로컬 레지스트리(compose.registry.yaml, 이미지 pull) | DE | -- | -- | DE | -- | ?N | -- | ?N |
| G3 | 인프라 | backup job -> postgres(pg_dump) / BACKUP_DIR 디스크 | DE | ?N | ?N | ?N | DN | ?N | -- | ?N |
| G4 | 인프라 | Docker 데몬/호스트 -> 컨테이너 재시작(restart: unless-stopped) | DN | -- | -- | ?N | -- | -- | -- | -- |
| G5 | 인프라 | 외부 감시 -> gateway /healthz (서버 밖) | ?N | -- | -- | -- | -- | -- | -- | -- |
| G6 | 환자 | 키오스크 브라우저 -> 브라우저 음성 인식(Web Speech API, 외부 서비스) | PN | PN | PN | -- | PN | PN | -- | PN |
| G7 | 예정 | 병원/의사 시스템 -> survey 결과 조회 API / 위험 신호 감지기 -> survey risk-signals API | ?N | ?N | ?N | ?N | ?N | ?N | DE | ?N |

### 간선별 근거와 설명

**A1. 키오스크 브라우저 -> gateway(Caddy)** (환자)
- 근거(간선): kiosk-frontend/api/client.ts:12,19,36,123-130; kiosk-frontend/apps/kiosk/flow.ts:146-157; Caddyfile:170-181; kiosk-frontend/docs/design.md:19-42
- 기대 동작·시험 근거: F1~F3: 10초 중단(AbortController), 같은 turn_id로 3회, 소진하면 직원 호출 화면(design.md:32,40; boundary.md:7). F4/F8: 재시도 구간(약 31초) 안에 돌아오면 성공, 아니면 직원 호출이 된다는 것은 코드로 알 수 있으나 재시작·분리를 명시한 문서가 없다. F5: 재시도는 429·503만(client.ts:19). 500/502/504는 재시도 없이 즉시 직원 호출(flow.ts:152, 코드 읽음)이고 문서는 이를 말하지 않는다. F6: 응답 본문이 깨졌을 때 화면 동작 문서 없음. F7: 401/403은 직원 호출(AUTH). 시험은 mock 서버를 쓰는 영역 단위(kiosk-frontend/test/client.test.ts, d85.test.ts)뿐. 실제 gateway·서비스를 멈추는 E2E는 없다(E2E 5f는 정상 경로와 401 단언).

**A2. gateway -> survey-service(키오스크 API·직원 API 프록시)** (환자)
- 근거(간선): Caddyfile:34,173; compose.yaml:175-181(depends_on healthy는 기동 순서일 뿐); Caddyfile:25-27(/readyz 정적 ok)
- 기대 동작·시험 근거: survey-service가 중지·멈춤·5xx일 때 gateway가 무엇을 돌려주는지(Caddy 기본 502/504로 추정, 미확인) 정의한 문서가 없다. Caddyfile에는 키오스크 경로의 타임아웃·health check가 없다(staff SSE의 read_timeout 1h만, :38-40). F3: 프런트의 10초 중단만 있다. gateway /readyz는 항상 200 'ok'(:25-27)라 상류 상태를 반영하지 않는다. survey 재시작 중 요청: survey 문서는 재적재 전까지 /readyz 503(boundary.md 6절)까지만 말하고, 그 사이 환자 요청에 대한 응답은 미정의. F7: gateway가 붙이는 survey 토큰이 어긋났을 때(회전 포함) 문서 없음. 모두 E2E 없음.

**A3. gateway -> kiosk-frontend(정적 화면)** (환자)
- 근거(간선): Caddyfile:190,197; compose.yaml:187-190
- 기대 동작·시험 근거: 정적 화면을 못 받을 때(최초 로드 실패) 키오스크가 무엇을 보이는지 문서 없음. 이미 로드된 앱은 JS가 메모리에 있어 정적 서버 장애와 무관하리라는 것은 추정(미확인). E2E 5f는 정상 응답과 CSP만 본다.
- 해당 없음: F5/F6/F7: 정적 파일 서버, 본문 검증 없음, 인증 없는 경로

**A4. survey-service -> model-serving(I9 extract/respond/PUT 적재)** (환자)
- 근거(간선): survey.env:9; survey_service/remote.py:129-163; settings.py:132-133; boundary-contracts/HTTP.md I9절; survey-service/docs/inference-server-spec.md 4~5절
- 기대 동작·시험 근거: F1: 연결 실패는 0.2초 간격 1회 재시도, 계속되면 해당 단계 실패. extract 실패는 NOT_COMMITTED(쓰기 없음), respond 실패는 COMMITTED(쓰기 유지, 문장 없음). /healthz는 산다(spec 5절). E2E 5: model-serving docker stop -> 그 턴 실패 신호 -> start -> 다음 턴 성공(e2e_steps.py:565-579). F2: 읽기 타임아웃 4초, 재시도 없음(test_slow_extract_beyond_timeout_fails_the_step_without_retry). F3: 4초 안이면 정상, 서버는 대기가 길어지면 큐에 쌓지 않고 503(HTTP.md I9; model-runtime test_rejects_when_queue_would_exceed_wait). F4: 404 -> PUT 재적재(200이면 재호출, 202면 이번 턴 실패)(spec 5절, test_forgotten_release_*); E2E 5의 stop/start가 같은 경로. F5: 502/503/504는 1회 재시도, extract의 503 OUTPUT_INVALID는 그래프가 1회 더 재시도 후 턴 실패·상태 불변(D75, test_output_invalid_*). F6: 200인데 JSON 아님·계약 위반 -> 재시도 없이 단계 실패(test_malformed_*). F7: 401/403 재시도 없이 단계 실패(test_auth_failure_on_calls_fails_the_step). E2E 5는 토큰 없는 직접 호출을 서버가 거부하는지만 본다. F8: 연결 시도도 같은 4초 타임아웃(urlopen timeout)으로 끝난다고 읽히나 분리를 명시한 문서·시험이 없다. 주의: inference-server-spec.md는 parse/generate 이름을 쓰고 HTTP.md는 extract/respond(HTTP.md가 기준, D62). 4초는 소켓 단위 타임아웃이지 총 시간 상한이 아니다(urllib 의미: 코드로 확인하지 못한 추정).

**A5. survey-service -> PostgreSQL(survey DB)** (환자)
- 근거(간선): compose.yaml:211,214; survey_service/pg.py:46-53,126-131; survey-service/docs/boundary.md 5~6절
- 기대 동작·시험 근거: F1: /readyz가 약 4초 안에 503(problems: session_db/outbox_db/alert_db), /healthz 200, 복구 시 자동 200 = E2E 5p(postgres stop/start, 행 지문 보존). 쓰기 확정 실패 턴은 NOT_COMMITTED 신호(boundary.md 6절 'Session Store 오류', 단위 test_orchestrator.py:334). 단 E2E 5p는 /readyz만 보고 중지 중 환자 턴은 시험하지 않는다. 연결 끊김 뒤 재접속은 단위(test_pg_conformance.py:105). F2/F3: 주 연결에는 statement_timeout이 없고 connect_timeout=10만 있다(pg.py:53; statement_timeout은 /readyz 전용 pg.py:130뿐). DB가 TCP는 받되 응답이 없을 때 턴이 얼마나 막히는지 문서 없음. F5/F6: 운영 중 SQL 오류·변조 시 동작은 StoreError/DB_ERROR로 바꾼다는 코드(pg.py:56)뿐 문서 없음. F7: 접속 실패는 시작 실패(pg.py:55)이나 운영 중 암호 변경 시 동작 문서 없음. F8: db-survey 네트워크 분리 = F1과 같은 증상.

**A6. survey-service -> ops-feedback-ingest(I6 Trace, outbox 경유)** (환자)
- 근거(간선): survey.env:6; survey_service/trace/exporter.py:66-120; survey-service/docs/boundary.md 4·6절
- 기대 동작·시험 근거: 턴 응답과 분리(턴은 영향 없음), UNAVAILABLE일 때만 지수 백오프 1~60초로 재시도, 최소 1회 전달, 같은 (세션,턴)은 한 번만(boundary.md 4절; test_trace_export.py). F2(연결은 되나 무응답): 클라이언트 10초 타임아웃 후 UNAVAILABLE로 보이나 이 경우를 명시한 문서는 없다. F6: 깨진 본문은 클라이언트가 UNAVAILABLE로 분류(boundary-contracts _http.py _map_error)해 재시도. F7: PERMISSION_DENIED는 재시도하지 않고 DEAD로 옮긴다(test_non_retryable_errors_are_not_retried:93) = 토큰이 틀리면 Trace가 DEAD 처리되어 유실되는 방향이고, 이를 알리는 신호가 /readyz에 있는지는 읽지 못했다. E2E 5/6은 정상 전송과 재전송 중복 없음만 본다(수집기 중지 E2E 없음).

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
- 기대 동작·시험 근거: SSE는 gateway가 버퍼링을 끄고 read_timeout 1h(Caddyfile:38-40). 브라우저 EventSource 자동 재연결과 Last-Event-ID 이어받기(kiosk design.md:49). 서비스·게이트웨이 재시작 중 알림 유실 여부, 하트비트 끊김 감지 기준은 문서 없음. F7: 인증 없는 직원 경로 401/403은 E2E 5f/5r이 gateway 쪽에서 단언.
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
- 기대 동작·시험 근거: F1/F4: /readyz 503 후 복구, 행 지문 보존 = E2E 5p(release-gate 포함). 연결 끊김 재접속 단위(release-gate test_postgres.py:97), /readyz 503이 접속 정보를 노출하지 않음(test_postgres.py:75). F5/F6: SQL 오류·DB 변조 시 동작은 문서에 없다(F5 칸의 단위 시험은 재접속 시험을 가리킨 것). F2/F3: statement_timeout 없음(검색 0건) -> 무응답 DB에서 승인·활성화 요청이 얼마나 막히는지 미정의.

**C5. release-gate·수집 잡 -> gate-data 볼륨(번들 파일 releases/)** (출고)
- 근거(간선): compose.yaml:275,344
- 기대 동작·시험 근거: 레지스트리 파일 손상 시 load_bundle/활성화가 INTEGRITY_ERROR, 롤백은 손상 대상을 REJECTED(release-gate boundary.md 장애 영향; test_rollback_to_corrupt_release_is_rejected). 쓰기 불가·가득은 문서 없음. 서버와 수집 잡이 같은 볼륨을 동시에 쓸 때의 경합도 문서 없음.
- 해당 없음: F2/F3/F5/F7/F8: 로컬 볼륨

**C6. scheduler.py(호스트) -> docker compose run --rm <잡>** (출고)
- 근거(간선): config/jobs.yaml; scripts/scheduler.py:47-78; scripts/run-job.sh; docs/runbook.md:81-85(cron)
- 기대 동작·시험 근거: F1(스케줄러 프로세스가 안 돌 때): 주기 잡이 서지 않고 상태 파일로 재개(deploy boundary.md 6절). 알리는 곳은 없다(external-monitor.example.yaml은 어떤 스크립트도 읽지 않음). F2/F3: 잡이 제한 시간 3600초(scheduler.py:17,67)를 넘으면 종료 코드 124로 기록하나 `docker compose run` 컨테이너가 남는지는 확인하지 못함. 이중 실행은 flock으로 BUSY(scheduler.py:60-63). E2E는 스케줄러 3틱 주기 동작을 확인(e2e.sh:181-183)하나 잡 실패·타임아웃 주입은 없다. F5: 잡이 0 아닌 종료 코드면 FAIL 기록만(scheduler.py:78).
- 해당 없음: F7: 인증 없음(로컬 프로세스)

**C7. admin-console 브라우저 -> gateway -> release-gate(승인 조회·결정)** (출고)
- 근거(간선): Caddyfile:50-82; admin-console/api/http.ts:54(15초); HTTP.md I5·D69
- 기대 동작·시험 근거: STALE_REPORT/ALREADY_DECIDED는 409로 구분(HTTP.md D69). 결정 POST는 같은 결정이면 같은 결과(멱등)라 무응답 뒤 재전송이 안전하다. 승인자가 결정하지 않으면 AWAITING_APPROVAL에서 대기(release-gate boundary.md). 화면의 오류 문구는 admin-console tests/ui.test.ts 단위(내용은 열지 않음). 실제 게이트 중지 E2E는 없다. E2E 4가 승인 경로를 gateway 경유로 정상 통과하고 E2E 5가 역할별 401/403을 단언.

**C8. operator -> gateway -> release-gate(activate·rollback·active-pointer)** (출고)
- 근거(간선): Caddyfile:129-162; e2e_steps.py:586-601
- 기대 동작·시험 근거: E2E 5가 권한 분리(401/403)와 operator 호출이 게이트까지 가는 것을 단언. 활성화·롤백은 멱등(같은 request_id 같은 결과, E2E 8). gateway 또는 게이트가 응답 없을 때 운영자 도구가 무엇을 보이는지는 문서 없음(호출자가 임의 HTTP 클라이언트).

**D1. job-ops-feedback -> PostgreSQL(ops_log, ops_failure)** (피드백)
- 근거(간선): compose.yaml:322-323; ops-feedback/src/ops_feedback/pgbase.py:21
- 기대 동작·시험 근거: 잡 중단·지연: 실패 사례 게시와 롤백 평가가 늦어지고 원본은 안전, 다음 실행이 이어서 처리(ops-feedback boundary.md 장애 영향). 연결 끊김 재접속·URL 비노출 단위(test_postgres_reconnect.py:55). E2E 5p는 ops_log/ops_failure 행 지문을 비교하나 잡 실행 중 DB 중지는 시험하지 않는다.

**D2. job-ops-feedback -> release-gate(I4 읽기)** (피드백)
- 근거(간선): config/ops-feedback-job.yaml:41-42; compose.yaml:314-331(networks logs, release, db-ops)
- 기대 동작·시험 근거: 롤백 평가에 필요한 릴리스 정보를 읽는다. 게이트 장애 시 잡의 종료 코드·재시도는 I4 읽기에 대해서는 정의를 찾지 못했다('게이트 UNAVAILABLE이면 롤백 요청이 전달되지 않고 다음 실행에서 재시도'는 D3 줄). 운영 설정의 rollback 항목이 null이라(ops-feedback-job.yaml:39) 현재 롤백 평가는 꺼져 있다고 읽힌다(미확인).

**D3. job-ops-feedback -> release-gate(I5 롤백 요청) [운영 설정에 연결 없음]** (피드백)
- 근거(간선): ops-feedback/src/ops_feedback/job.py:201(cfg['gate_service']); deploy/config/ops-feedback-job.yaml에 gate_service 항목 없음(grep), rollback: null(:39); e2e_steps.py:867-894
- 기대 동작·시험 근거: 코드는 있고 단위 시험이 있다(test_unavailable_gate_retries_same_request: 요청 저장·같은 id 재전송). E2E 8은 ops-feedback 토큰으로 테스트 하니스가 직접 HttpGateService를 부른 것이며(e2e_steps.py:868) 운영 잡 설정을 거치지 않는다. 운영 job 설정에는 gate_service 항목과 롤백 기준이 없어 자동 롤백 간선이 현재 켜져 있지 않다(grep 결과; 롤백 기준은 사용자 결정 대기). '나쁜 릴리스를 자동으로 되돌린다'는 사실로 쓰면 안 된다.

**D4. ops-feedback-ingest(서버) -> PostgreSQL(ops_log, ops_failure)** (피드백)
- 근거(간선): compose.yaml:252-253; pgbase.py:21
- 기대 동작·시험 근거: log 쓰기 불가면 send가 UNAVAILABLE이고 survey가 재시도(boundary.md 장애 영향). E2E 5p가 /readyz 503->200과 행 지문 보존을 확인. F2/F3: 무응답 DB에서의 동작·타임아웃은 미정의(statement_timeout 없음). 디스크 가득은 비기능 표.

**D5. question-authoring -> ops-feedback-ingest(I7 개선 신호 읽기)** (피드백)
- 근거(간선): question-authoring.env:2; question_authoring/__main__.py:45-47; http_api.py:142; question-authoring boundary.md 장애 영향
- 기대 동작·시험 근거: ops-feedback 중단 시 GET /v1/signals만 UNAVAILABLE, 나머지는 영향 없음(boundary.md 장애 영향; test_signals.py, 403 매핑 포함). 클라이언트 타임아웃은 기본 10초(__main__.py:47에서 지정하지 않음). I7 읽기 면이 DB URL만으로 켜지는지는 ops-feedback 이미지로 확인해야 한다고 deploy가 '미검증'으로 적어 둠(ops-feedback-ingest.env:2). E2E 7이 I7 정상 경로를 사용.

**D6. reviewer 브라우저 -> gateway -> ops-feedback-ingest(검토 게시)** (피드백)
- 근거(간선): Caddyfile:86-119; HTTP.md I7 검토 게시
- 기대 동작·시험 근거: reviewer 역할만 쓰기(읽기 토큰 403), 같은 검토 재전송은 같은 결과(멱등). 중지·무응답 시 검토 화면 동작은 admin-console 문서에서 찾지 못했다. reviewer 계정 권한 분리와 검토 게시는 E2E 7이 단언(e2e_steps.py:834-850).

**E1. question-authoring -> PostgreSQL(qa DB)** (저작)
- 근거(간선): compose.yaml:233,236; question_authoring/store/postgres.py:87(connect_timeout=5)
- 기대 동작·시험 근거: I1 호출이 UNAVAILABLE(재시도 가능), /readyz 503(question-authoring boundary.md 장애 영향). E2E 5p가 qa DB 행 지문과 복구 후 새 쓰기(버전 2)까지 확인. 연결 끊김 재접속·쓰기 응답 유실 멱등은 test_postgres_specific.py:50,94,107. 무응답 DB(F2/F3)는 connect_timeout 5초만 있고 statement_timeout은 없다.

**E2. 저자 클라이언트 -> question-authoring(문항 등록·검수)** (저작)
- 근거(간선): compose.yaml:182(호스트 포트는 gateway만); Caddyfile에 authoring 경로 없음(reverse_proxy 목록 grep); compose.test.yaml:17-19(시험용 포트)
- 기대 동작·시험 근거: 운영 구성에서 저자가 문항을 올리는 길이 없다(구성을 읽은 사실). E2E는 compose.test.yaml의 시험 포트로 직접 올린다(e2e_steps.py:142 upload). 이 간선의 운영 형태가 정해지지 않아 장애 기대도 정의할 수 없다. 의도된 구성인지는 확인하지 못했다.

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
- 기대 동작·시험 근거: 디스크 가득·볼륨 손상 시 5개 DB가 동시에 영향을 받는다(단일 postgres 컨테이너가 단일 장애점인 구성). 백업·복구(pg_dump)는 E2E 단계 9에서 시험(e2e.sh:198-205, 복구 후 e2e_verify_restore.py). 디스크 가득 시 동작은 문서 없음.
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
- 근거(간선): config/external-monitor.example.yaml(어떤 스크립트도 읽지 않음); Caddyfile:22-27
- 기대 동작·시험 근거: 외부 감시 구성이 없다(예시 파일 url: null). 서버가 통째로 죽었을 때 사람이 알게 되는 경로가 없다. gateway /healthz·/readyz는 정적 응답이라 DB나 survey가 죽어도 200이다.
- 해당 없음: F2~F8: 아직 존재하지 않는 간선

**G6. 키오스크 브라우저 -> 브라우저 음성 인식(Web Speech API, 외부 서비스)** (환자)
- 근거(간선): kiosk-frontend/docs/runbook.md:38; E2E 5x(BLOCKED, e2e_steps.py)
- 기대 동작·시험 근거: Chrome에서 인터넷과 구글 음성 서비스에 의존(runbook.md:38). 인식 실패·무신뢰는 REPEAT_PROMPT(design.md:20). 인터넷이 끊겼을 때 키오스크가 텍스트 입력 등으로 대체되는지는 문서 없음(미정). 실제 브라우저·STT는 E2E에서 볼 수 없다(BLOCKED).
- 해당 없음: F4: 외부 서비스, F7: 인증 없음

**G7. 병원/의사 시스템 -> survey 결과 조회 API / 위험 신호 감지기 -> survey risk-signals API** (예정)
- 근거(간선): Caddyfile:166-169(게이트웨이에 열지 않음); compose.yaml:204-205; e2e_steps.py:661-707(5r); survey boundary.md 5절
- 기대 동작·시험 근거: 호출자가 아직 없는 간선(결과 전달 대상 없음이 지금의 정상 구성, survey boundary.md 5절). 토큰 분리는 E2E 5r이 단언(다른 역할 403, 게이트웨이 404). 호출자가 생기면 장애 기대를 정해야 한다. 현재 직원 알림 입력원도 없다(G01).

## 4. 비기능 칸

| ID | 항목 | 현황(읽은 사실) | 기대 | 시험 | 근거 |
| --- | --- | --- | --- | --- | --- |
| N1 | 동시 요청(여러 키오스크의 동시 턴) | 서버는 모두 ThreadingHTTPServer. survey-service PostgreSQL 접근은 연결 하나 + RLock(pg.py:46-48)이라 DB 접근이 직렬화될 수 있다(락을 잡는 구간 길이는 읽지 못함). 추론 서버는 대기가 호출 타임아웃을 넘을 것 같으면 503(HTTP.md I9). | P | U | survey service.py:375; pg.py:46-48; model-runtime test_rejects_when_queue_would_exceed_wait; survey test_other_sessions_are_not_blocked_by_slow_inference. E2E에 동시 세션 시험 없음 |
| N2 | 부하(처리량·지연 분포, 목표 수치) | 목표 수치가 어느 문서에도 없다. OPEN_GAPS H4(문법 컴파일 비용, 동시 요청 부하)가 '열림'. | ? | N | head/docs/OPEN_GAPS.md:72 |
| N3 | 연결 풀/연결 수 제한 | 연결 풀 없음(grep 0건). PostgreSQL max_connections·서비스별 연결 수 합 산정 없음(compose.yaml, 10-roles.sh에 설정 없음). 주 연결에 statement_timeout 없음. | ? | N | grep 'ConnectionPool|psycopg_pool|max_connections|statement_timeout' 결과(survey pg.py:130 /readyz 전용 1건뿐) |
| N4 | 같은 turn_id의 동시 중복 전송(프런트 10초 중단 뒤 재전송이 서버 처리와 겹침) | 순차 재전송은 같은 응답·한 번만 처리(E2E 5, test_same_turn_id_returns_same_response_and_processes_once). 겹치는 동시 전송의 동작은 문서에 없다. 서버 한 턴의 최악 시간이 10초를 넘을 수 있다(타임아웃 표 참조, 계산). | ? | N | e2e_steps.py:541; survey tests/test_public_api.py:61; 동시 겹침 시험은 찾지 못함 |
| N5 | 큰 입력 | survey API 본문 상한 64KiB이며 본문을 다 읽은 뒤 길이를 비교(api.py:47,112). 공통 클라이언트 응답 상한: JSON 256MiB, tar 8GiB(_http.py). 다른 서버(QA·ops·gate·model-runtime)의 요청 본문 상한은 grep으로 찾지 못함. | P | N | survey api.py:47,112; boundary-contracts _http.py:~180. 상한 시험은 찾지 못함 |
| N6 | 디스크 가득 | 어느 영역 문서에도 없음(grep ENOSPC/디스크 가득/No space 0건). survey outbox 디스크 오류만 정의(boundary.md 6절: Trace 유실, /readyz 503). pg-data, gate-data, serving-data, models-data, 백업 폴더, 컨테이너 로그(json-file 10MB x 5)가 모두 호스트 디스크를 공유. | ? | N | compose.yaml:12,40-44 |
| N7 | 시계 어긋남(호스트 시계 점프, 컨테이너 간 시각 차) | 문서 grep 0건. 시각을 쓰는 곳: 수집기의 created_at 최신 판정(collector.py), 승인 decided_at, Trace 시각, 스케줄러 last_start(scheduler.py:57-58). | ? | N | grep '시계|clock skew|ntp' 0건 |
| N8 | 재시작 중 요청(단일 컨테이너 재시작 순간) | survey: 재적재 전까지 /readyz 503(boundary.md 6절). gateway는 /readyz를 보지 않고 프런트는 502에서 재시도 없이 직원 호출. 서비스별 재시작 순간 요청의 응답은 정의 없음. E2E 5s는 포인터 교체 때 컨테이너가 재시작하지 않음을 확인할 뿐. | ? | N | Caddyfile:25-27; flow.ts:152; e2e_steps.py:708-717 |
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
| N20 | 서비스 이름 DNS 해석(재시작 뒤 IP 변경) | 서비스는 Compose 서비스 이름으로 서로 부른다(*.env). model-serving 재시작 뒤 같은 이름으로 복구되는 것이 E2E 5에서 간접 확인된다. 다른 서비스 재시작에서의 이름 재해석은 시험하지 않음. | P | E | survey.env; e2e_steps.py:565-579 |

합계 20행: 기대 D 6 / P 5 / ? 9; 시험 E 2 / U 5 / N 13.

## 5. 타임아웃·재시도 일람과 환자 경로 최대 대기

| 호출자 -> 대상 | 타임아웃 | 재시도 규칙 | 근거 |
| --- | --- | --- | --- |
| 키오스크 브라우저 -> gateway | AbortController 10초(요청 전체) | 429·503·무응답·네트워크 오류만 재시도, 총 3회, 대기 0.5초(무응답) 또는 Retry-After/1초 | client.ts:12,19,36,127 |
| gateway -> survey/ops/gate 등 | Caddyfile에 지정 없음(staff SSE만 read_timeout 1h). Caddy 기본값은 확인하지 못함 | 없음 | Caddyfile:38-40 |
| survey -> model-serving | 읽기 4초(SURVEY_INFERENCE_TIMEOUT_SECONDS). urlopen timeout이라 소켓 단위(총 시간 아님, 추정) | 연결 실패·502/503/504는 1회(0.2초), 읽기 타임아웃은 재시도 없음, extract OUTPUT_INVALID는 그래프가 1회 더. 적재 신호: 최대 600초 확인 | settings.py:132-133; inference-server-spec 5절 |
| survey -> PostgreSQL(주 연결) | connect_timeout 10초, statement_timeout 없음 | 끊김 시 재접속(단위 시험), 그 밖에는 NOT_COMMITTED | pg.py:53; test_pg_conformance.py:105 |
| survey -> PostgreSQL(/readyz 확인) | 2초(+1초 여유) | - | settings.py:137; pg.py:126-131 |
| survey -> release-gate(I4) | 10초(SURVEY_HTTP_TIMEOUT_SECONDS), 폴링 5초 | 적재 실패는 백오프 후 재시도, 결정적 오류는 영구 거부 | settings.py:135; clients.py:30; survey.env:11; test_loader_retry.py |
| survey -> ops-feedback-ingest(I6) | 10초 | UNAVAILABLE만 지수 백오프 1~60초, 예기치 않은 예외는 20회 뒤 DEAD | exporter.py:66-70,118-139 |
| survey -> 웹 푸시 | 3초 | 없음(경로 없으면 DELIVERY_FAILED) | settings.py:74 |
| model-serving -> release-gate(I4) | 120초(번들 읽기), /healthz 확인 2초 | 적재 요청(PUT)을 survey가 멱등 재호출 | server.py:149,399 |
| release-gate -> question-authoring/model-registry | 30초(GATE_I1_TIMEOUT, GATE_I3_TIMEOUT 환경 변수 없으면) | 다음 주기(Loop 60초)에 재시도 | factories.py:24; main.py:191 |
| release-gate -> PostgreSQL | connect_timeout 10초, statement_timeout 없음 | 연결 끊김 재접속 | postgres_store.py:74 |
| question-authoring -> ops-feedback(I7) | 10초(기본값, 호출 지점에서 지정 안 함) | 없음(요청 단위) | boundary-contracts _http.py:182; __main__.py:47 |
| question-authoring -> PostgreSQL | connect_timeout 5초 | 연결 끊김 재접속 | store/postgres.py:87 |
| ops-feedback(서버·잡) -> PostgreSQL | connect_timeout 10초 | 연결 끊김 재접속 | pgbase.py:21 |
| ops-feedback 잡 -> release-gate(I4/I5) | 10초(HttpReleaseReader 기본값) | 롤백 요청은 저장 후 같은 id 재전송(다음 실행) | ops-feedback-job.yaml:41-42; test_rollback.py:45 |
| job-release-gate-collect -> QA/registry | 30초 | 스케줄러 다음 주기(600초) | factories.py:24; jobs.yaml |
| scheduler -> 잡 컨테이너 | 잡당 3600초(--timeout), 초과하면 종료 코드 124 | 다음 주기 | scheduler.py:17,67-70 |
| admin-console -> gateway | 15초 | (재시도 규칙 http.ts에서 찾지 못함) | admin-console/api/http.ts:54 |
| synthetic-data -> QA/ops | 10초 | 읽지 못함 | synthetic_data/adapters.py:25-30 |
| model-runtime 추론 큐 | 대기 3초 초과 시 503 | - | server.py:16 |

**환자 경로 총 최대 대기 (계산, 측정 아님).**

- 브라우저 쪽: 시도당 10초 x 3회 + 대기 2번(무응답은 0.5초, 429/503은 Retry-After 또는 1초) = 약 31~32초 뒤 직원 호출 화면. 서버가 Retry-After에 큰 값을 주면 더 길다. 500/502/504는 재시도 없이 즉시 직원 호출.
- 서버 쪽 한 턴: 상한 없음(총 마감 시간이 코드에 없음). 구성 요소: extract(읽기 4초, 연결 실패·5xx는 0.2초 뒤 1회 재시도, OUTPUT_INVALID는 그래프가 1회 더) + respond(같은 규칙) + PostgreSQL 쓰기(statement_timeout 없음). inference-server-spec 4절은 '4+4초'로 설계했다고 적었으나 재시도를 포함하지 않는다. 예: extract가 3.9초에 503 -> 0.2초 -> 3.9초에 성공(8.0초) + respond 3.9초 = 약 11.9초로 프런트의 10초를 넘는다. 이 경우 프런트는 중단하고 같은 turn_id를 다시 보내며, 서버는 앞 요청을 계속 처리 중일 수 있다(N4 미정의).
- 따라서 '환자가 최악에 기다리는 시간'은 문서에 없고, 위 계산이 유일한 추정이다.

## 6. 이 문서로 닫히지 않는 것

- 간선 추가 누락(2절 한계). 특히 `synthetic-data`, `model-lab` 내부와 GPU 서버 쪽 호출은 얕게만 봤다.
- 칸 안의 '장애 방식'이 서로 겹치는 경우(예: F4 재시작은 F1 중지와 F2 복구의 합)를 모두 분해하지 않았다. 동시에 둘 이상 일어나는 장애(DB 중지 중 model-serving 재시작 등) 조합은 칸으로 두지 않았다.
- 이 파일의 숫자는 이 파일 안의 표를 센 값이다(`E2E` 통과 수 같은 다른 영역 사실은 옮기지 않았다. 정본: `deploy/docs/E2E_RESULTS.md`).
- 기대 동작 열의 'D'는 영역 문서가 정의했다는 뜻이지 그 정의가 옳다는 판단이 아니다. 예: 위험 신호가 있어도 쓰기 확정이 실패한 턴은 직원 알림을 보내지 않는다는 survey 문서의 '주의(안전)'는 도메인 소유자 확인 대기다(survey boundary.md 6절).

