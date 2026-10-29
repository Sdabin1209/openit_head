# 전수 점검: survey-service (읽기 전용 감사)

> 점검일 2026-10-28. 기준: `head/docs/AUDIT_CHECKLIST.md` A~I 전 항목. 대상: `survey-service` (작업 트리 clean, 커밋 대상 아님). 코드·설정·문서는 수정하지 않았다. 이 파일만 썼다.
> 읽은 것: AUDIT_CHECKLIST, FAULT_POLICY 전문, FAULT_MATRIX의 survey 관련 행, 이 영역 CLAUDE.md·brief.md·README.md·docs/boundary.md(1~6-1절 대부분), runbook 제목·일부, `survey_service/` 중 api.py, service.py, settings.py, orchestrator.py, pg.py, db.py, retention.py, clients.py, alerts.py, remote.py, risk_rules.py, store/sqlite.py, trace/outbox.py, trace/exporter.py 일부, graph.py 일부(130~200, 360~500, 열거한 grep 지점), Dockerfile, requirements.*, scripts/smoke.sh 일부, tests/compose/compose.smoke.yaml. 읽지 못한 곳은 맨 끝.

## 요약

- 항목 수 **63** (A 9, B 12, C 10, D 7, E 8, F 6, G 3, H 5, I 3). 분모는 모두 63.
- 판정별: **OK 18 / 문제 34 / 해당 없음 3 / 확인 못 함 8** (합 63).
- 문제 34건의 심각도: **H 1 / M 14 / L 19**. 같은 원인은 아래 "묶음 문제"로 묶었다(묶으면 H 1, M 11묶음).
- 시험 실행(영역 `.venv`, `pytest -p no:cacheprovider`, 읽기 전용): 진행 표시 기준 **통과 979, 건너뜀 35, 실패 0**(요약 줄이 출력되지 않아 점 개수로 센 값이다. README의 "수집 415개"와 다르다). 건너뜀 35 = PostgreSQL 34(`TEST_DATABASE_URL` 없음) + docker 1(`test_turn_db_outage_bounds.py:68`). 즉 **운영 저장소(PostgreSQL) 경로는 이 실행에서 시험되지 않았다.** 한 번만 돌렸으므로 간헐 실패 여부는 모른다.
- 위험 패턴 grep(`shell=True|eval(|exec(|pickle|yaml.load|verify=False|os.system|subprocess|__import__|innerHTML`): `survey_service/`에서 **0건**(smoke.sh의 시험용 subprocess 1건만). f-string SQL은 있으나 모두 상수 표 이름 또는 `?` 나열(아래 B5).
- pip-audit: 설치되어 있지 않아 실행하지 않았다(설치 금지) → 취약점은 **확인 못 함**. `requirements.lock`은 57개 모두 `==` 정확 핀(읽어서 확인), 해시 없음.

### H 문제 (1건)
1. **(해결됨 2026-10-28 04:07, survey-service ab22579, D88 U1: 위험 선별을 모든 발화 턴에서 추출 전 `prescreen` 노드로 옮김. 아래 원문은 점검 당시 기록)** **위험 규칙 엔진이 모델 추출이 성공한 턴에서만 돈다**(I1). 모델 실패·시간 초과·검증 위반 턴에서는 환자 발화에 위험 문구가 있어도 감지·정지·알림이 없다. 현재 실제 모델은 U07로 모든 턴이 실패했으므로 규칙 파일을 켜도 그 경우 작동하지 않는다. 사용자(도메인) 결정 필요.

### M 묶음 문제 (11묶음, 14항목)
- M1 연결·스레드·요청 속도 제한이 없다(A9, B10, E1의 인증 실패 무기록)
- M2 보존 기간 기본 무기한 + 정리 대상 누락, 테이블 무한 증가(A6, C3)
- M3 접근 기록이 직원 개인을 남기지 않고 헤더 신뢰·변조 방지 없음(C6)
- M4 키오스크 토큰 하나를 전 키오스크가 공유, 세션 ID만 알면 접근(B2)
- M5 웹 푸시 endpoint SSRF(B6)
- M6 저장 시 암호화·파일 권한 없음(C5)
- M7 관측성: 메트릭 엔드포인트·경보 기준 없음, 요청 로그 없음(E1, E2)
- M8 공급망: 기반 이미지 digest 미고정, lock 해시 없음, SBOM·스캔 없음(F2)
- M9 운영 저장소(PostgreSQL) 시험이 기본 실행에서 건너뛰어짐(H3)
- M10 환자에게 가는 문구의 임상 검토 표시 없음(I2)
- M11 실패 시 환자 화면에 빈 응답이 갈 수 있음, 필수 고정 문구 존재를 시작 때 검사하지 않음(I3)

## 라우트 전수 표 (인증 데코레이터 대신 `api.py`의 역할 판정 근거)

기본 거부 구조: `PublicApi._handle`(api.py:103-148)이 경로 해석(`_route`, 161-189) 후 `want` 역할을 정하고(108), `_role`(150-158, `hmac.compare_digest`로 모든 토큰을 끝까지 비교)로 토큰 역할을 구해 불일치면 401/403. 경로 해석이 실패하면 인증 전에 404(106-107). HTTP 핸들러(service.py:389-405)는 `/v1/`로 시작하는 GET, 모든 POST/DELETE를 `_api`로 보낸다.

| 경로 | 메서드 | 필요한 토큰/역할 | 근거 |
|---|---|---|---|
| `/healthz` | GET | 없음(의도) | service.py:394 |
| `/readyz` | GET | 없음(의도). 내부 상태를 노출(B11) | service.py:396, 243-280 |
| `/v1/sessions` | POST | kiosk | api.py:181, 108 |
| `/v1/sessions/{id}/turns` | POST | kiosk | api.py:183-185 |
| `/v1/sessions/{id}/end` | POST | kiosk | api.py:183-185 |
| `/v1/sessions/{id}/state` | GET | kiosk | api.py:186-188 (세션별 0.5초 폴링 상한 352-361) |
| `/v1/sessions/{id}/intervention` | POST | staff + 헤더 `X-Openit-User` 필수 | api.py:49, 183, 318-325 |
| `/v1/staff/alerts` | GET | staff | api.py:49, 162 |
| `/v1/staff/alerts/stream` | GET(SSE) | staff | service.py:314 → api.py:589-598 |
| `/v1/staff/sessions/{id}` | GET | staff (접근 기록 fail-closed) | api.py:172-174, 443-472 |
| `/v1/staff/push-config` | GET | staff | api.py:175 |
| `/v1/staff/push-subscriptions` | POST, DELETE | staff | api.py:177-180 |
| `/v1/results/{id}`, `/v1/results` | GET | result-reader (토큰 미설정이면 404로 꺼짐) | api.py:50, 109, 164-168 |
| `/v1/sessions/{id}/risk-signals` | POST | risk-source (토큰 미설정이면 404) | api.py:50, 169-171 |
| 그 밖의 경로, PUT/PATCH | 모두 | 없음 → 404 | api.py:106, service.py:402-405 |
| HEAD, OPTIONS 등 | | 정의 없음 → 표준 라이브러리 기본 501 HTML 오류 | service.py (핸들러에 do_HEAD 없음) |

인증 없이 열린 경로는 `/healthz`, `/readyz`뿐이다(의도). 데코레이터 누락으로 보호되지 않은 비공개 경로는 찾지 못했다. 4개 토큰은 서로 달라야 하고(api.py:74-78, service.py:126-131) 비어 있으면 시작을 거부한다.

## 항목별 판정

### A. 신뢰성

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| A1 외부 호출 timeout | OK | DB: connect 2초(pg.py:89), statement_timeout 서버 쪽 + 클라이언트 강제 소켓 종료 상한+1초(pg.py:98-119, settings.py:58-59). 추론: `HttpModelRuntime(base_url, token, timeout=4.0)`(remote.py:132, settings.py:90), 적재 600초(settings.py:91, 별도 상한 있음). 릴리스·Trace HTTP 10초(clients.py:122). 푸시 3초(alerts.py:376,443). 단 연결과 읽기가 한 값이라면 따로 나뉘지 않는다: HTTP 클라이언트 구현은 `boundary_contracts`에 있어 읽지 못했다(끝 절). |
| A2 재시도 | 문제 L | 추론은 연결 실패만 1회, 고정 `0.2*attempt` 대기(remote.py:105-108), 지터 없음. Trace 전송은 지수 백오프 1~60초 상한이 있으나 지터 없음(exporter.py:121-127). 두 호출 모두 멱등(추출은 무상태, Trace는 (세션,턴) 유일). 제안: 지터 추가(자율 수정 가능, 영향 작음). |
| A3 부분 쓰기 | 문제 L | 세션 쓰기는 한 트랜잭션(sqlite.py:104-129, PG 같은 SQL). 확정 실패 시 NOT_COMMITTED. 남은 틈 둘: (1) 세션 DB와 알림 DB의 쓰기는 한 트랜잭션이 아니다(alerts.py:3-6, 문서화됨, DELIVERY_FAILED 복구 경로). (2) 마감 직전에 시작된 확정은 `cancelled` 확인(graph.py:525) 뒤에 반영될 수 있다(boundary.md가 한계로 인정). 제안: 현상 유지 또는 (2)를 시험으로 고정. 자율 수정 가능(시험 추가). |
| A4 우아한 종료 | OK | SIGTERM → `draining` 표시, /readyz 503, `httpd.shutdown()`, 요청 스레드는 비데몬이고 `block_on_close`(service.py:409-414, 443-453). SSE는 draining을 0.5초 안에 본다(360-362). 시험 test_readyz_db_outage.py:173(문서 인용, 이번 실행에서 통과). 단 느린 클라이언트가 있으면 종료가 늦어질 수 있다(A9). |
| A5 재시작 후 정상화 | OK | 시작 시 첫 폴링과 `ensure_loaded(open_release_ids)`(service.py:146-158), 세션은 DB 영속, DB 복구 후 /readyz 자동 200(pg.py 재접속 유예). DB가 시작 때 죽어 있으면 프로세스가 종료 코드 3으로 끝나 재시작 정책에 의존한다(service.py:436-439, E7). FAULT_MATRIX 5q·5p 통과 기록은 deploy 것이라 인용만 한다. |
| A6 무한 증가 | 문제 M | 상한이 있는 것: outbox PENDING 상한 20000(outbox.py:73-84), SENT 24시간 정리(service.py:160), 알림 이벤트 1만 건 정리(161), 푸시 구독 100(settings.py:82), 폴링 맵 정리(api.py:362-363). **없는 것**: 세션·턴 행(보존 기본 없음, C3), `outbox` DEAD 행은 영구(`purge_sent`는 SENT만, outbox.py:143), `staff_access_log` 무기한(retention.py:42는 일부러 지우지 않음), `alerts` 행, `session_meta` 외 정리 후 남는 알림. 묶음 M2. |
| A7 동시성 | OK | 세션별 락(orchestrator.py:45-64, 152), 같은 (세션,턴) 겹침은 409(117-121), 낙관적 revision 검사(sqlite.py:112), PG는 `FOR UPDATE`. 데드락 소지: 세션 락 하나 + 저장소 락(저장소별 RLock) 순서가 고정이다. 약점(L): 마감을 넘긴 작업 스레드는 `_inflight`와 슬롯 해제 뒤에도 최대 모델 timeout까지 살아 있다(orchestrator.py:136-149). 상한 32 곱하기 약 4~8초라 유한하다. PG 경로의 동시성 시험은 이번 실행에서 건너뜀(H3). |
| A8 /healthz·/readyz | OK | /healthz는 의존과 무관 200(service.py:394). /readyz는 3개 저장소를 동시 확인, 상한 DB timeout+1초(207-230), 활성 릴리스 없음·종료 중이면 503(243-253). FAULT_POLICY 원칙 5와 일치. |
| A9 자원 한도 | 문제 M | 접속 수·스레드 상한이 없다: `ThreadingHTTPServer`가 접속마다 스레드를 만들고(service.py:409-418), `api_max_inflight=32`는 본문을 다 읽고 JSON을 파싱한 뒤에야 걸린다(api.py:128). **소켓 읽기 timeout이 없다**(`StreamRequestHandler.timeout` 기본 None) → 느린 클라이언트(slowloris)가 스레드를 무한히 붙잡는다. 부하 측정에서 N=100일 때 스레드 약 309개(boundary.md:118). /readyz는 호출마다 스레드 4개를 만든다(인증 없음, 207-223). 컨테이너 메모리 한도는 deploy 몫. 제안: 핸들러 `timeout` 설정, 접속 상한, /readyz 결과 캐시(1~2초). 자율 수정 가능. 묶음 M1. |

### B. 보안

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| B1 인증 | OK | 위 라우트 표. 기본 거부, 인증 없는 경로는 /healthz·/readyz뿐. 토큰 비교는 상수 시간(api.py:156). |
| B2 인가 | 문제 M | 역할 분리는 맞다(api.py:114). 그러나 (1) **kiosk 토큰은 모든 키오스크가 공유**하고 세션 ID가 클라이언트가 정하는 `[A-Za-z0-9_-]{1,64}`다(api.py:45). 토큰과 세션 ID를 아는 쪽은 그 세션의 `/state`를 읽고 `/turns`로 발화를 넣을 수 있다(세션 소유 확인 없음, api.py:279-295, 352-371). 세션 ID가 추측하기 어려워야 하는데 생성 규칙은 이 영역이 정하지 않는다. (2) 직원 신원은 gateway가 붙이는 `X-Openit-User` 헤더를 그대로 믿는다(service.py:302, api.py:319-325). staff 토큰을 가진 쪽이 gateway를 우회해 보내면 임의 계정으로 개입을 기록할 수 있다. 제안: 세션 생성 때 서버가 불투명 세션 비밀을 발급하는 방안, 또는 세션 ID 최소 엔트로피 규약을 PUBLIC_API에 명시. 계약 변경이므로 사용자·헤드 결정 필요(변경 요청 대상). 묶음 M4. |
| B3 비밀 | OK | 모든 비밀은 `read_secret`(NAME_FILE 우선)로 읽는다(service.py:60-65, 120-131; db.py:20-24; clients.py:116). /readyz에는 출처(file/env/unset)만(service.py:194-205). DB 오류는 클래스 이름만(pg.py:92-96). 로그에 토큰·DSN 없음(grep). Dockerfile에 비밀 없음. 이미지 ENV에 키 없음. 단 비밀은 시작 때 한 번 읽으므로 회전하려면 재시작이 필요하다(L, 문서화 없음). `tests/test_secrets.py`는 이번 실행에서 통과. |
| B4 입력 검증 | 문제 L | 좋은 점: 본문 64KB(api.py:47,116), ID 정규식 고정, 발화 1000자(220), FrontendMessage는 jsonschema로 모르는 필드 거부(214), limit 1~200, 역직렬화는 json만. 문제: (a) `int(self.headers.get("Content-Length") or 0)`의 ValueError가 처리되지 않아 연결이 끊긴다(service.py:299). 음수·1MB 초과 길이는 본문을 읽지 않고 빈 본문으로 처리해 400을 준다(300). (b) `SURVEY_RISK_RULES_FILE`의 `regex`는 환자 발화에 `re.search`로 적용되고 실행 시간 상한이 없다(risk_rules.py:127, 500자 길이 제한만, 83-90). 운영자 파일이라 신뢰하지만 파국적 역추적(ReDoS)은 막지 않는다. (c) 외로운 서로게이트 문자(JSON `"\ud800"`)가 발화 검증을 통과하면 `json.dumps(...,ensure_ascii=False).encode()`에서 UnicodeEncodeError가 난다(이 부분은 실행으로 확인했다. 전체 서비스 경로로는 실행하지 않았고 service.py:291,303, sqlite 저장 경로에서 같은 오류가 날 것으로 추정). 제안: Content-Length 파싱 보호, 서로게이트 거부, 규칙 파일에 정규식 길이·`regex` 사용 경고. 자율 수정 가능. |
| B5 인젝션 | 확인 못 함 | 확인한 것: SQL은 전부 `?` 파라미터(sqlite.py, alerts.py). f-string SQL 4곳은 상수(`PRAGMA table_info({table})` alerts.py:122, `ALTER TABLE {table}` 496, `DELETE FROM {t}` 282, `SELECT 1 FROM {table}` pg.py:194)이거나 `?` 나열(sqlite.py:205, alerts.py:259)이다. 명령 실행 없음(grep). 로그는 JSON 직렬화로 줄바꿈이 이스케이프되고(service.py:38-42) ID는 정규식으로 제한된다. 발화는 추출 모델의 데이터 필드 `user_utterance`로만 들어가고(extraction.py:87) 모델 출력은 turn-engine `validate_extraction`과 `check_slots`로 코드가 검증한다(graph.py:425-428). **확인 못 한 것**: LoRA-B(응답 문장 생성)가 발화를 입력으로 받는데(extraction.py:171) 발화가 응답 문구를 바꾸는지는 model-runtime의 출력 보호 규칙에 달려 있고 이 점검에서 읽지 못했다. |
| B6 SSRF | 문제 M | `POST /v1/staff/push-subscriptions`는 `https://`로 시작하기만 하면 임의 endpoint를 저장한다(api.py:562-577). 알림이 나면 서버가 그 URL로 POST한다(alerts.py:375). staff 토큰 보유자가 내부 https 서비스를 두드리게 할 수 있다. 제안: 알려진 푸시 서비스 호스트 허용 목록(설정), 사설 IP 차단, 리다이렉트 미추적 확인. 자율 수정 가능(허용 목록 값은 운영 설정). 그 밖의 외부 URL(릴리스 읽기, 수집, 추론)은 환경 변수로 운영자가 정한다. |
| B7 웹 | 해당 없음 | JSON 전용 API, 인증은 Authorization 헤더, 쿠키·HTML·서비스 워커 없음 → XSS/CSRF/쿠키 속성 해당 없음. CORS·보안 헤더(nosniff 등)는 이 서비스가 내지 않는다(gateway 몫이며 deploy에서 확인 필요). |
| B8 전송 | 확인 못 함 | 서비스는 평문 HTTP를 0.0.0.0:8080에서 받는다(service.py:419). TLS 종료는 gateway(deploy)이고 이 영역에서 읽지 못했다. 내부 구간에는 베어러 토큰과 환자 발화가 평문으로 간다. DB 접속의 `sslmode`는 운영자가 DSN에 넣어야 하며 이 영역 문서에 요구 사항이 없다. |
| B9 의존성 | 확인 못 함 | pip-audit 없음 → 취약점 스캔은 못 했다. 읽어서 확인한 것: requirements.lock 57개 전부 `==` 핀(해시 없음), 이웃 라이브러리는 Git 태그(requirements.txt:2-4, 태그는 변경 가능), dev 의존 pytest·pyyaml·setuptools는 미핀(requirements.txt:10-12, 개발용). 이미지 쪽 문제는 F2. 이 항목은 M8 묶음에 포함해 센다(F2에서 계수). |
| B10 속도 제한 | 문제 M | 전역 동시 처리 32(429)와 세션별 상태 폴링 상한뿐(api.py:128, 355). 클라이언트별 제한, 인증 실패 제한, 세션 시작 남발 제한이 없다(세션 시작은 DB 행을 만든다). 토큰 최소 길이 검사도 없다(api.py:72-78, 비어 있지 않고 서로 다르기만 하면 된다). 제안: 인증 실패 카운터·로그, 토큰 최소 길이(예: 32자) 시작 거부, 세션 시작 속도 상한. 최소 길이 검사는 자율 수정 가능, 상한 수치는 운영 결정. 묶음 M1. |
| B11 오류 노출 | 문제 L | API 오류는 고정 한국어 메시지와 코드뿐이고 트레이스백을 내지 않는다(api.py:59-64). 그러나 `/readyz`는 인증 없이 릴리스 ID, 적재 거부 내역(`rejections`), 모델 백엔드, 질문 흐름, 카운터, 비밀 출처를 낸다(service.py:254-279). gateway가 외부에 그대로 내보내는지는 읽지 못했다. 처리되지 않은 예외는 표준 라이브러리가 stderr에 트레이스백을 찍는다(B4 a). 제안: /readyz 상세는 내부 전용으로 문서화하거나 상세/요약 분리. |
| B12 토큰 수명·최소 권한 | 문제 L | 토큰은 역할 4개로 나뉘어 최소 권한은 좋다. 그러나 만료·회전 절차가 없고(재시작 필요), 앱 시작 때 DDL을 실행하므로(pg.py:176-186, alerts.py:493-496) 운영 DB 계정에 DDL 권한이 있어야 한다. 서비스별 DB 계정 분리는 deploy 문서(RUN.md 4-1-1)를 읽지 못했다. |

### C. 데이터·개인정보

C1 저장·전송·기록 목록(이 점검이 코드에서 직접 정리):

| 데이터 | 어디 | 근거 |
|---|---|---|
| 발화 원문, 응답 문장, 저장된 답 전부(세션 문서) | `sessions.doc` (SQLite 또는 PG, 평문 JSON) | sqlite.py:20-28, 89-96 |
| 턴 결과(응답·콘솔 입력) | `turns.result_json` | sqlite.py:30-37, 177-185 |
| Trace 봉투(발화 원문, 턴 전 세션 문서 전체 `session_before`, 모델 입출력) | `outbox.envelope` → ops-feedback로 전송 | graph.py:157-158, 362-363; outbox.py:15-30 |
| 환자 참조 `subject_ref` | `session_meta` (세션 문서·로그·알림 밖) | alerts.py:64-69, boundary.md:48 |
| 직원 ID | 대화 로그 개입 항목 `staff_id`, `alerts.resolved_by` | api.py:343, alerts.py:180 |
| 세션 ID | 알림, 접근 기록, 푸시 본문, 로그 | alerts.py:427, service.py (로그 문장) |
| 직원 브라우저 푸시 endpoint·키 | `push_subscriptions` | alerts.py:82-86 |
| 로그 | 표준 출력 JSON: 세션 ID·턴 ID·오류 클래스. 발화·값 없음(service.py:38-42, graph.py:436 주석, grep) | |

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| C1 목록 | 문제 L | 위 표는 이 점검이 코드를 읽어 만들었다. 영역 문서에는 이런 단일 목록이 없다(boundary.md가 곳곳에 흩어 설명). 제안: boundary.md에 "저장하는 개인정보" 표 추가. 자율 수정 가능. |
| C2 최소 수집 | OK | `subject_ref`는 선택이고 세션 문서 밖에 둠(api.py:257-259), 로그·알림에 발화 없음, 위험 규칙 증거에 발화 원문 없음(risk_rules.py:8-10). 참고: Trace가 매 턴 `session_before` 전체를 싣는 것은 ops-feedback 평가 요구에 따른 것으로 보이나 필요성은 그 영역이 판단한다(확인 못 함). |
| C3 보존·삭제 | 문제 M | `SURVEY_SESSION_RETENTION_DAYS` 기본 없음 = **무기한**(settings.py:55, boundary.md:48). 삭제 경로(`python -m survey_service purge`, retention.py)는 있고 멱등이나, 정리 대상에서 `staff_access_log`, `alerts` 행, DEAD outbox는 빠진다(retention.py:42). 정리를 언제 돌릴지(deploy 스케줄러)와 기간은 정해지지 않았다. 사용자 결정 필요(보존 기간). 기본값이 무기한인 것을 시작 시 경고로 드러내는 일은 자율 수정 가능. 묶음 M2. |
| C4 비식별 | OK | 이 영역의 로그·알림·푸시·접근 기록·위험 규칙 증거에는 발화 원문이 없다(위 표, grep으로 로그 호출 전수 확인). 다만 Trace는 발화 원문을 ops-feedback에 보낸다(설계상). 그곳의 비식별과 모델 학습 환류는 이 점검 범위 밖이다. |
| C5 저장·전송 암호화 | 문제 M | 세션 문서는 앱 수준 암호화 없는 평문 JSON이다(README가 "세션 문서 암호화 미확인"으로 인정). SQLite 파일 권한은 앱이 지정하지 않는다(`sqlite3.connect`, `mkdir` 기본 umask; Dockerfile:24는 `/data`만 chown). PG 디스크 암호화·볼륨 권한은 deploy. 전송 평문 구간은 B8. 사용자 결정 필요(디스크 암호화로 충분한지, 앱 암호화까지 할지). 묶음 M6. |
| C6 접근 기록 | 문제 M | `staff_access_log`는 (시각, **역할 이름**, 세션 ID, 결과, 조건 이름)만 남긴다(alerts.py:56-63, 233-243; api.py:431-438). 여러 직원이 staff 토큰 하나를 공유하므로 **누가 열람했는지 알 수 없다**. `X-Openit-User`는 `intervention`에서만 쓰고 세션 조회에는 넘기지 않는다(api.py:136-137). 알림 목록 조회·키오스크 `/state`·푸시 구독 변경은 기록이 없다. 기록 테이블은 같은 DB 계정으로 UPDATE/DELETE가 가능해 변조 방지가 없다. 행위자 헤더는 변조 가능(B2). 현재 PUBLIC_API.md:75가 "역할 이름"으로 정하고 있어 계약 변경이 필요하다. 제안: 헤더의 계정 ID를 접근 기록에 추가(변경 요청으로 헤드에게), DB 쪽 추가 전용 권한. 사용자·헤드 결정 필요. 묶음 M3. |
| C7 백업·복원 | 확인 못 함 | boundary.md:48이 "알림 DB는 백업 대상"이라고만 적고 주기·복원 시험·백업 암호화 기술이 이 영역에 없다. deploy 문서를 읽지 못했다. |
| C8 DB 계정 | 확인 못 함 | 세션·outbox·알림 세 저장소가 한 DSN 하나(`SURVEY_DATABASE_URL`)와 한 데이터베이스를 쓴다(db.py:17-35). 계정 권한은 deploy에서 정해져 읽지 못했다. 앱이 시작 때 DDL을 돌린다는 점은 B12. |
| C9 마이그레이션 | 문제 L | 스키마는 `CREATE IF NOT EXISTS`와 `ADD COLUMN`(PG는 `IF NOT EXISTS`)으로 덧붙이는 방식이며(sqlite.py:58-66, alerts.py:116-123, 491-496) PG는 advisory lock으로 동시 기동을 막는다(pg.py:176-186). 버전 표·되돌리기 절차가 없다. 덧붙이기만 하므로 이전 이미지로 돌려도 대체로 동작하겠지만 문서화되어 있지 않다. 제안: runbook에 스키마 변경 규칙 한 줄. 자율 수정 가능. |
| C10 정합성 | 문제 L | 기본키·UNIQUE·CHECK는 있다(sessions PK, turns PK, outbox UNIQUE·CHECK, alerts CHECK). 외래키 없음(알림 테이블은 세션 ID를 문자열로만 가짐), `sessions.status` CHECK 없음. 시각은 UTC 에폭 또는 `Z` 문자열(좋음). 한글 NFC 정규화는 위험 규칙 비교에서만 하고(risk_rules.py:30) 저장 발화·추출 입력에는 하지 않는다. 자율 수정 가능(NFC 적용 범위는 모델 입력 변경이라 영향 검토 필요). |

### D. 정확성·계약

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| D1 계약 일치 | OK | `PUBLIC_API.md`(읽기 전용으로 대조): 상태 코드·코드 표(400 INVALID_RECORD, 401/403 PERMISSION_DENIED, 409 CONFLICT, 429/503 UNAVAILABLE+Retry-After)가 api.py:48, 59-64, 99-100과 일치. 엔드포인트 12종이 라우트 표와 일치. `turn_id` 처리 중 409 `details.reason=TURN_IN_PROGRESS` 일치(api.py:240-244). 시험 test_public_api*.py 통과. 응답 본문 필드 전체 대조는 하지 않았다. |
| D2 상태 기계 | OK | 끝난 세션에 발화 409(api.py:293-294), 멈추지 않은 세션에 개입 409(340-341), 없는 세션 404, 유휴 만료는 IN_PROGRESS만(sqlite.py:187-192), 위험 신호는 끝난 세션 409(orchestrator.py:186-187). 시험 통과. |
| D3 멱등 | OK | (세션,턴) 기본키와 입력 해시 비교(sqlite.py:30-37, orchestrator.py:214-222), 겹치면 409(117-121), start/end/idle 고정 turn_id(api.py:54), risk signal_id, outbox UNIQUE. 참고(L, D7과 함께): 모델 실패로 끝난 NOT_COMMITTED 턴은 `cacheable=True`라 같은 turn_id 재전송은 같은 실패를 되돌려준다(graph.py:741, orchestrator.py:158). 마감 초과 턴만 고정하지 않는다. FAULT_POLICY 원칙 1의 "재전송이 안전하다"는 성립하나 "재전송하면 성공할 수 있다"는 아니다. |
| D4 시간·시계 | 문제 L | 마감은 `time.monotonic()`(좋음, orchestrator.py:128). 그러나 유휴 만료와 목록 정렬은 `time.time()` 벽시계(sqlite.py:190, service.py:177, store 갱신 시각)라 시계가 크게 뒤로 가거나 앞서면 대량 만료 또는 미만료가 생길 수 있다. 시각 표기는 UTC. |
| D5 인코딩·크기 | 문제 L | 발화 1000자·본문 64KB 제한은 좋고 이모지·긴 한글은 문자 수로 센다(api.py:220). 문제: 서로게이트 문자(B4 c), Content-Length 비정상(B4 a). JSON에서 NULL 문자는 이스케이프되어 저장된다. 8MiB 규약(CONVENTIONS)은 응답 쪽에서 확인하지 않았다. |
| D6 값 지어내기 금지 | OK | 추출 결과를 `validate_extraction`과 `check_slots`로 검증하고 위반이면 같은 요청을 1회만 재시도, 그래도 틀리면 NOT_COMMITTED(graph.py:416-440, README의 D75). 모델이 없는 slot key를 만들면 턴이 실패로 끝난다(U07로 관찰: 14턴 모두 실패, 안전한 방향). 값을 지어내 저장하는 경로는 찾지 못했다. |
| D7 문서·코드 일치 | 문제 L | 어긋남 모음: (1) boundary.md:53 "접속 대기 3초" vs settings.py:58 기본 2초(FAULT_MATRIX:209가 지적). (2) boundary.md:114·116과 pg.py:33 주석에 총 마감 8초가 남아 있고 기본은 6초(settings.py:57). (3) service.py:1 모듈 설명 "공개 API(I10)는 O06 대기라 만들지 않는다"는 낡음. (4) brief.md §2·§7의 "O06 미확인"은 README·boundary와 다르게 낡음. (5) README "CR-001~012", 실제 CR-016까지. (6) README "수집 415개" vs 이번 관측 약 1014개. (7) runbook §6은 `git -C ../<이름> archive`라고 쓰나 build_wheels.sh는 `git clone`(scripts/build_wheels.sh:14). (8) settings.py에 `outbox_max_pending` 필드가 두 번 선언됨(97, 99). (9) 이미지 태그가 requirements.txt·build_wheels.sh 기본값·Dockerfile ARG에 중복(기준표는 deploy/scripts/lib.sh). 자율 수정 가능. |

### E. 운영성

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| E1 구조화 로그 | 문제 M | 로그는 JSON 한 줄(시각, 수준, 로거, msg)이고 비밀·발화는 없다(service.py:38-42). 그러나 (1) 상관 ID가 별도 필드가 아니라 msg 문자열 안에 `session=… turn=…`으로 섞여 있다. (2) **접근 로그가 꺼져 있다**(`log_message`가 아무것도 안 함, service.py:287). 401/403/429의 건수·출처가 어디에도 남지 않아 토큰 추측·남용을 알 수 없다. (3) 트레이스백은 형식기에서 버려진다(PHI 보호엔 좋지만 원인 분석이 어렵다). 제안: 인증 실패·429를 카운터와 경고 로그(경로·역할·상태만)로 남긴다. 자율 수정 가능. 묶음 M7(와 M1). |
| E2 메트릭·경보 | 문제 M | `/readyz`에 카운터가 있으나(trace_outbox, staff_alerts, validation_violations 등) `/metrics` 형식이 없고 경보 기준이 이 영역 문서에 없다. FAULT_MATRIX:181·228이 지적하듯 `trace_outbox.dead_by_code`, `staff_alerts.delivery_failed`를 읽는 경보가 없다. 알림이 직원에게 닿지 못하는 것은 환자 안전과 닿는다. 제안: 경보 기준 표(어떤 필드가 0이 아니면 알린다)를 boundary.md에 쓰고 deploy가 읽게 한다. 자율 수정 가능(문서), 경보 연결은 deploy. 묶음 M7. |
| E3 설정 | 문제 L | 환경 변수 설정, 필수 3개 없으면 종료 코드 2(service.py:430-433)는 좋다. 문제: `float()` 직접 호출 두 곳이 ConfigError가 아니라 ValueError(settings.py:129,150), 실수 필드 중 일부가 상한·하한 검증이 없다, `SURVEY_MODEL_BACKEND=fake`가 운영에서도 받아들여지고 /readyz에 `production_safe=false`로만 드러난다(service.py:273), 안전하지 않은 기본값들(보존 무기한, 위험 입력원 없음, 재질문 상한 끔)은 이미 알려진 사용자 결정 항목이다(I1). 제안: fake 백엔드를 운영 표시 환경에서 거부하는 옵션. 자율 수정 가능. |
| E4 런북 | 문제 L | runbook에 띄우기·상태 보기·Trace 전송·턴 실패·이미지·스모크는 있고 boundary.md §6 장애 표에 복구 열이 있다. 없는 것: 토큰 회전, DEAD Trace 수동 재처리("미구현"이라 적힘), 보존 정리 실행법, 알림 미도달 대처, 스키마 되돌리기. |
| E5 감시 대상·알림 경로 | 확인 못 함 | 감시는 deploy의 check-health 소관. FAULT_MATRIX:181이 "check-health는 survey /readyz를 읽지 않음"이라 적었다. 이 점검에서 deploy를 읽지 못했다. |
| E6 용량 근거 | 문제 L | 부하 측정은 있고 조건이 명시되어 있다(boundary.md:96-121). 한계: 가짜 모델, 이 PC 한 곳, 마감 8초 시절 값이며 6초로 낮춘 뒤 다시 재지 않았다. 실제 모델 지연 포함 측정 없음. |
| E7 시작 순서 | OK | 첫 릴리스 적재를 `startup_wait_seconds`(5초)까지만 기다리고 서비스를 연다. 활성 릴리스가 없으면 /readyz 503(service.py:170, 250-253). 의존 DB가 죽어 있으면 시작 실패 후 재시작(A5). |
| E8 timeout 체인 | 문제 L | 기본값은 문서·코드가 같다: 서버 마감 6초(settings.py:57,143), 키오스크 10초 > gateway 9.5초 > 6초. 약점: 추론 timeout 4초 ×(extract + respond) + 재시도 + 백오프가 6초 마감과 맞는지 시작 때 검증하지 않는다(마감은 새 모델 호출만 막고 진행 중 호출은 끊지 못함, graph.py:386, 601). 옛 8초 문구(D7). |

### F. 배포·이미지

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| F1 권한·포트 | OK | 비root uid 10001(Dockerfile:23-24), 이미지에 docker.sock·권한 없음, 스모크는 호스트 포트를 `127.0.0.1::8080`로 배정(smoke.sh:35). 읽기 전용 루트 FS로 실제 기동해 보는 시험은 없다(쓰는 곳은 `/data`뿐으로 보이나 확인 못 함). capabilities·privileged는 compose(deploy) 몫. |
| F2 이미지 핀·재현·스캔 | 문제 M | 기반 이미지 `python:3.12-slim`이 digest 없이 태그만(Dockerfile:3,7→`FROM`). lock에 해시가 없고 `--require-hashes` 아님(Dockerfile:6). 이웃 라이브러리는 변경 가능한 Git 태그에서 wheel을 만든다(build_wheels.sh:6-14). SBOM·취약점 스캔 절차가 이 리포에 없다. LangSmith 추적은 환경 변수로 꺼져 있어 발화 외부 전송 위험은 낮춰 둠(Dockerfile ENV; 이 환경 변수만으로 충분한지는 라이브러리 동작을 읽지 못했다). 제안: digest 고정, 해시 포함 lock, 스캔을 CI에. 자율 수정 가능(디지스트 값은 빌드 시점 결정). 묶음 M8. |
| F3 compose | 해당 없음 | 운영 compose는 deploy 소유. 이 리포의 `tests/compose/compose.smoke.yaml`은 시험용이며 비밀을 파일로 준다. |
| F4 되돌리기·업그레이드 순서 | 확인 못 함 | runbook §6-1(이미지 조합 정책)의 제목은 확인했으나 내용을 끝까지 읽지 못했다. 스키마는 덧붙이기 방식(C9). |
| F5 비밀 파일 권한·compose 환경 | 해당 없음 | 이 리포에는 운영 compose가 없다. 스모크 compose는 `NAME_FILE`만 사용(compose.smoke.yaml:35-52). 운영 쪽 권한은 deploy. |
| F6 레지스트리·CI 신뢰 경계 | 확인 못 함 | 이 리포에 CI 설정이 없다. 이미지는 CI에서 빌드·digest 게시(D24)해야 하는데 이 영역에서는 확인할 수 없다. |

### G. 성능·용량

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| G1 측정·한계 문서화 | OK | boundary.md:96-121에 환경(CPU·메모리·가짜 모델·루프백), N별 p50/p95/max, 연결 3개, 스레드·메모리, 측정으로 고친 것까지 있다. 한계(가짜 모델, 옛 마감값)도 적혀 있다(E6의 약점은 별도 판정). |
| G2 쿼리·인덱스·풀 | 문제 L | 풀이 없고 저장소당 연결 1개를 락으로 직렬화(pg.py:76, 문서화됨: 병목이 연결이 아님). 턴당 DB 문장 약 29개(boundary.md:118). 결과 목록은 N+1 형태(세션마다 load + subject_of + timeline, api.py:529-532, 최대 200). `staff_access_log`에 session_id 인덱스 없음(alerts.py:56-63, `access_log(session_id)` 조회). 정렬은 `updated_at` 복합 인덱스가 status 필터에 의존. |
| G3 큰 입력 | 문제 L | 입력은 상한이 있다(B4). 그러나 세션 문서는 대화 로그가 누적되고 매 턴 전체를 다시 쓰며(`_dump(new_doc)`) Trace가 매 턴 `session_before` 전체를 싣는다. 재질문 상한이 꺼져 있으면(G12 열림) 한 세션이 무한히 커질 수 있다(유휴 만료는 무활동만 센다). 정규식은 B4 b. |

### H. 시험 품질

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| H1 핵심 경로 실제 구성요소 | OK | 시험이 실제 Orchestrator·그래프·저장소(SQLite)·HTTP 서버(`serve(app, 0)`)와 참조 서버(ref_servers.py)로 돈다. 모델은 가짜 백엔드이고 실제 모델로 한 턴을 통과한 시험은 없다(U07 열림, README). PG 경로는 이번 실행에서 안 돌았다(H3). |
| H2 간헐 실패 | 문제 L | 실제 `time.sleep`에 의존하는 시험이 있다(test_fault_a6_a8_a10.py:36,169-230; test_staff_alerts.py:462-481; test_inference_client.py:224 `sleep(1.3)`). 포트는 0(자동)이라 고정 포트 충돌은 없다(tests/test_service.py의 9000은 설정 파싱값). 이번에 1회 실행해 통과했고 반복 실행으로 간헐 실패를 재 보지는 않았다. |
| H3 건너뛰는 시험 | 문제 M | 35개 건너뜀. 사유는 출력에 명시된다(TEST_DATABASE_URL 없음 34, docker 불가 1). 문제는 **PG가 운영 저장소(D85)인데 기본 실행에서 시험되지 않는다**는 것. 대체 수단은 `smoke.sh`의 PG 단계(smoke.sh:166)와 "이 PC에서 로컬 PG 컨테이너로 돌렸다"는 문서 기록뿐이고 이번 점검에서는 재현하지 못했다. 제안: CI에서 `TEST_DATABASE_URL`을 주어 항상 실행. 자율 수정 가능(CI 환경 필요, 영역 밖 설정 포함). |
| H4 부정 시험 | OK | 역할 불일치 401/403, 잘못된 ID(65자), 모르는 필드, 끝난 세션, 멈추지 않은 세션 개입, 처리 중 같은 turn_id, 접근 기록 실패 시 거부 등의 시험이 있다(test_public_api.py, test_public_api_v132.py:72, test_staff_alerts.py:395, test_results_signals_retention.py). 빠진 것(L): 비정상 Content-Length, 서로게이트, 느린 클라이언트, 정규식 폭주. |
| H5 환경 의존 | 문제 L | 시험이 wheel을 `--no-build-isolation`으로 빌드하고 setuptools·wheel을 요구한다(requirements.txt:12-13). docker·PostgreSQL 유무에 따라 결과가 달라진다. 깨끗한 두 번째 환경에서의 재현은 문서 자체가 "미확인"이라 적었다. 이번 실행도 같은 PC·같은 venv다. |

### I. 도메인·안전

| 항목 | 판정 | 근거 / 내용 |
|---|---|---|
| I1 환자 안전 결정 | 문제 H(그중 (1)은 해결됨: ab22579) | (1) **위험 감지가 모델 성공에 종속**: 위험 입력원 `src.check(...)`는 `n_plan_writes`에서만 호출되고(graph.py:449-453), 이 노드는 추출이 검증을 통과한 뒤에만 실행된다(graph.py:416-440의 분기). 추출 실패·timeout·위반(NOT_COMMITTED)이면 규칙 엔진(발화에 대한 결정적 문자열 규칙, 모델이 필요 없음)조차 돌지 않아 환자 발화에 위험 문구가 있어도 정지·직원 알림이 없다. (2) 입력원이 기본으로 없다(`staff_alert_source.active=false`, G01, 사용자 결정 대기). (3) 재질문 상한 기본 끔 = 무한 되묻기(G12, `SURVEY_MAX_CONSECUTIVE_REASK=0`). (4) 쓰기 확정 실패 턴의 위험 알림 미발송(boundary.md "주의(안전)", FAULT_POLICY 사용자 결정 목록에 있음). (5) 추출 재시도 횟수 `MAX_EXTRACT_CALLS`가 코드 상수(D75). (1)만 영역 문서에 안전 문제로 적혀 있지 않은 새 지적이다. 제안: 규칙 평가를 추출 앞이나 추출 실패 경로에도 두는 방안을 도메인 소유자에게 묻는다. 사용자 결정 필요(환자 안전). 자율 수정 불가. |
| I2 문구 출처 | 문제 M | 환자에게 가는 문장은 (a) LoRA-B 생성 문장(표 찾기 입력 `DATASET_RULES_UNCONFIRMED`, 표 승인 기록 없음, 57행 문제의 서비스 쪽 문장은 학습 분포 밖, boundary.md·README G03·G13), (b) 릴리스 묶음의 고정 문장(RISK_NOTICE, CALL_STAFF, RESUME, SURVEY_STOPPED; graph.py:494-496). 코드에는 임상 검토 완료 표시가 없고 /readyz `response_tables.status`로 상태만 드러난다. 다른 영역(데이터셋 담당)·사용자 확인 필요. |
| I3 실패 시 환자 화면 | 문제 M | 모델 실패나 마감 초과 시 `response_text: null`과 `turn_failure_signal`을 200으로 돌려준다(api.py:238, orchestrator.py:248-254). 이후 화면은 키오스크 구현에 달려 있어(다른 영역) 이 영역만으로는 "조용히 빈 화면"이 아님을 보장하지 못한다. 또 `fixed_sentence(key)`가 없으면 `None`을 돌려주는데(assembly.py:27-30) 릴리스 적재 시 필수 고정 문장(RISK_NOTICE 등)의 존재를 검사하는 코드를 찾지 못했다(grep `fixed_sentence`는 graph.py:495 한 곳). 위험 정지 세션에서 안내 문구가 비면 환자는 아무것도 못 본다. 제안: 릴리스 적재 때 필수 키 존재 검사(자율 수정 가능), 키오스크 쪽 처리 확인은 다른 영역. |

## 이 점검이 읽지 못한/얕게 본 곳

- `boundary_contracts` 패키지(HTTP 클라이언트의 연결/읽기 timeout 분리, `read_secret` 구현, 재시도), `turn_engine`(`validate_extraction`), `model_runtime`(출력 보호 규칙, LoRA-B 프롬프트 처리). 이 영역에서 부르는 지점까지만 보았다. B5(응답 문구 주입), A1 일부가 여기에 걸린다.
- `survey_service/graph.py`는 약 40%만 읽었다(응답 생성 노드, 직원 콘솔 전달, 대화 로그 쓰기, 시각 기록 노드 본문 등). `trace/exporter.py`, `release/loader.py`(다운로드 경로·해시 검증 상세), `store/postgres.py`·`pg_outbox.py`·`effects.py`·`memory.py`, `extraction.py` 본문, `response_tables.py`, `flow.py`, `cli.py`, `inference.py`는 grep과 일부 줄만 확인했다. 릴리스 ID로 만든 파일 경로의 경로 조작(B4)은 읽지 못했다.
- `schema/`(문진 스키마 데이터)와 `docs/rules/`, `docs/design.md`, `docs/inference-server-spec.md`, `docs/STATUS.md`, `docs/change-requests/` 본문은 읽지 않았다. FAULT_MATRIX는 survey 관련 행만 보았고 전문을 읽지 않았다.
- deploy 영역(compose, TLS 종료, 비밀 파일 권한, 백업, DB 계정, check-health, CI/레지스트리)은 규칙상 읽지 않았다. 따라서 B8, C7, C8, E5, F4, F6은 '확인 못 함'이다.
- 실행한 것: pytest 1회(PostgreSQL·docker 시험은 건너뜀), `json.dumps` 서로게이트 한 줄. 실행하지 않은 것: 서비스 기동, `/readyz` 실측, 이미지 빌드·스모크(Docker 접근 필요), pip-audit(미설치), 부하, 슬로로리스 재현. B4(a)(c)와 A9의 느린 접속 문제, B6 SSRF의 실제 발현은 코드 읽기로 추정한 것이지 재현이 아니다.
- 의존성 취약점은 전혀 확인하지 못했다. lock의 핀 상태만 읽었고 일부 버전(예: `certifi==2026.7.22`, `httpx2`)의 실제 존재·안전성은 오프라인이라 대조하지 못했다.
