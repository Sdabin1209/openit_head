# release-gate 전수 점검 (읽기 전용 감사, 2026-10-28)

기준: `head/docs/AUDIT_CHECKLIST.md` A~I 전 항목. 대상: `/home/user/sdabin/healthKiosk/release-gate` (HEAD d6205ed). 코드·설정·문서는 수정하지 않았고 이 파일만 썼다.

## 요약

- 항목 수 **63** (A9 + B12 + C10 + D7 + E8 + F6 + G3 + H5 + I3). 판정 분모는 63.
- 판정: **OK 21 / 문제 29 / 해당 없음 4 / 확인 못 함 9** (합 63).
- 문제 29건의 심각도: **H 0 / M 10 / L 19**.
- **H 문제 없음.** 단 B2·C6(승인자 식별 위조)은 게이트웨이가 클라이언트 `X-Openit-User`를 지우는지 읽지 못해(deploy 폴더 열람 금지) 조건부다. 지우지 않거나 승인자 토큰을 여러 사람이 공유하면 H로 올려야 한다.
- M 문제 10건(같은 원인 묶음 표기):
  1. A4 SIGTERM 처리 없음, python이 PID 1 (우아한 종료 안 됨)
  2. A6 접수·판정·릴리스·어댑터 사본이 무한 증가(보존·정리 정책 없음, 접수 남발 상한 없음)
  3. A7 승인 때 번들 복사 동안 저장소 전역 락을 쥐어 같은 프로세스의 읽기(활성 포인터)가 막힘
  4. A9 요청 스레드·소켓 timeout·본문 크기 상한 부재(ThreadingHTTPServer 무제한)
  5. B2 `release-approver` 요청에 `X-Openit-User`가 없으면 본문 자기 신고 `approver_id`를 그대로 기록(activate는 401인데 approvals는 허용)
  6. C3 보존 기간·삭제 경로 없음(사용자 결정 필요)
  7. C6 감사 기록 공백(실패한 시도·거부된 요청은 행위자 없이 접근 로그에만 남음, 위 B2와 같은 뿌리)
  8. F2/B9 이미지·의존 공급망: 기반 이미지 태그만, 잠금 파일에 해시 없음, SBOM·스캔 없음
  9. G2 `GET /v1/submissions` 목록이 전체 접수를 훑고 건마다 쿼리(N+1)
  10. G3 활성화·번들 GET마다 어댑터 전체를 복사·해시(수 GB면 CPU·디스크 폭주)

## 확인한 방법

- 읽음: AUDIT_CHECKLIST, FAULT_POLICY, FAULT_MATRIX(이 영역 행), CLAUDE.md, README, docs/brief·boundary·design·runbook·STATUS, `release_gate/*.py` 전부(app, main, gate, store, postgres_store, reader, registry, config, collector, views, review, util, 일부 checks·policy), Dockerfile, requirements*, scripts/smoke.sh, 시험 파일 목록과 주요 시험. 읽기 전용으로 `../boundary-contracts/HTTP.md`의 승인 절과 `GateApproval` 스키마.
- 실행: 영역 `.venv`의 `python -m pytest -q -p no:cacheprovider` → **320 passed, 195 skipped, 0 failed** (66초). 건너뜀은 `TEST_DATABASE_URL` 없음(PostgreSQL 시험)과 docker pause 시험으로 사유가 출력된다. README·STATUS가 적은 수치(PostgreSQL 없이 320/195)와 같다. PostgreSQL 포함 485 통과는 이번에 재현하지 못했다.
- grep 위험 패턴: `shell=True`, `eval(`, `exec(`, `pickle`, `yaml.load`, `verify=False`, `os.system`, `subprocess`, f-string SQL, `extractall`, `.format(` 모두 `release_gate/`·`scripts/`에서 **0건**. SQL은 전부 `?`/`%s` 파라미터화이고 동적 부분은 고정 컬럼명뿐(`store.py` find_decisions). 평문 비밀 없음(토큰은 `read_secret`). 경로 조합 `root/"releases"/release_id`는 `get_release(release_id)`가 DB 행을 먼저 요구해 임의 문자열이 파일 경로에 닿지 않는다(`store.py:~311, ~342`; 릴리스 ID는 서버가 `rel-`+해시로 생성, `gate.py:342`). tar는 만들기만 하고 풀지 않으며 심볼릭 링크 제외(`reader.py:98`).
- `pip-audit`는 설치되어 있지 않아 설치하지 않았다 → 의존성 취약점은 **확인 못 함**. 핀 상태는 B9에서 판정.

## 라우트 전수 표 (근거 `release_gate/app.py`)

| 경로 | 메서드 | 필요한 토큰/역할 | 근거 |
| --- | --- | --- | --- |
| `/healthz` | GET | 없음 | app.py:177 |
| `/readyz` | GET | 없음 (DB 종류, 정책·라이브러리 버전, 승인 대기 건수, 루프 상태 노출) | app.py:179-185, main.py:293-306 |
| `/v1/active-pointer` | GET | 읽기 토큰(역할 구분 없음) | app.py:186-188 |
| `/v1/releases`, `/v1/releases/{id}` | GET | 읽기 토큰 | app.py:189-196 |
| `/v1/releases/{id}/bundle` | GET | 읽기 토큰 (해시 검증 후 tar) | app.py:197, reader.py:80 |
| `/v1/decisions`, `/v1/decisions/{id}` | GET | 읽기 토큰 | app.py:211-219 |
| `/v1/submissions`, `/v1/submissions/{id}` | GET | 읽기 토큰 | app.py:199-204 |
| `/v1/submissions/{id}/review-report` | GET | 읽기 토큰 (부작용: 보고서를 만들어 저장함, gate.py:63-71) | app.py:205-210 |
| `/v1/submissions` | POST | 쓰기 토큰, 역할 ∈ {operator, release-gate-collector, question-authoring, model-lab}, 본문 역할이 있으면 토큰 역할과 같아야 함 | app.py:256-258, config.py:8, gate.py:81 |
| `/v1/approvals` | POST | 쓰기 토큰, 역할 `release-approver`만. I1·I3 연결 필수(없으면 503). 행위자는 `X-Openit-User`, 없으면 본문 `approver_id` | app.py:229-238, gate.py:273 |
| `/v1/activate` | POST | 쓰기 토큰, 역할 `operator`만(`GATE_ACTIVATE_ROLES`로 변경 가능). 사람 역할은 `X-Openit-User` 없으면 401, 서비스 역할(`ops-feedback`)은 `service:<역할>` | app.py:239-253 |
| `/v1/rollback` | POST | 쓰기 토큰, 역할 `ops-feedback` 또는 `operator`. 헤더 규칙은 activate와 같음. 본문 역할은 토큰 역할로 덮어씀 | app.py:239-255 |
| 그 밖의 GET | GET | 읽기 토큰 없으면 403, 있으면 404 | app.py:186, 220 |
| 그 밖의 POST | POST | 쓰기 토큰 없으면 403(본문 읽기 전), 있으면 404 | app.py:226, 259 |
| PUT/DELETE/HEAD 등 | - | 핸들러 없음(http.server 기본 501) | app.py (do_GET, do_POST만 정의) |

## 이 영역 특유 점검

| 점검 | 판정 | 근거 |
| --- | --- | --- |
| 승인 권한 분리 | OK(구조) | `approver_roles={"release-approver"}`만 결정(config.py:15, gate.py:273). activate는 operator만, 승인자 토큰으로 activate 시도는 403, operator 토큰으로 approvals는 403(test_gate_flow.py:123-124, test_http.py:65·187). 제출 역할 4종에 승인자 없음 → 제출자와 승인자 토큰이 분리됨. 한 사람이 두 토큰을 가진 경우의 직무 분리는 코드에 없음(토큰 발급은 deploy) |
| 승인 기록 위조 방지 | **문제 M (B2/C6)** | `app.py:234-237`, `gate.py:277-278`: 헤더가 있으면 그 값(ID 형식만 검사), **없으면 본문 `approver_id`를 그대로** 승인 기록·판정 `approver.id`에 씀. 시험이 이를 고정(`test_http.py:348-351`). HTTP.md:68은 "개발·시험용"이라 적었지만 코드에 운영/개발 구분이 없다. 이 서버는 `0.0.0.0:8080`(main.py:331)이라 헤더 신뢰 경계는 "gateway가 클라이언트 헤더를 지우고 승인자 토큰을 gateway만 가짐"에 전적으로 의존. 그 두 가지는 이 점검이 읽지 못했다 |
| 활성 릴리스 전환 원자성 | OK | 포인터 이력은 추가 전용, 기대 버전과 새 버전=현재+1 확인 후 삽입, 영수증과 한 트랜잭션(store.py switch_pointer, postgres_store.py:355-375; PG는 advisory lock + PK 위반 시 False). 활성화는 풀어서 모든 해시를 검증한 뒤에만 전환(gate.py:126-127). 시험: test_conformance.py:223, test_upstream_faults.py:357·406, test_postgres.py:105(PG는 이번에 건너뜀). 한계: 검증과 전환 사이에 번들 파일이 바뀌는 시간차(TOCTOU)는 있으나 읽는 쪽(survey)도 로드 때 다시 검증함(boundary.md) |
| 번들 해시·변조 검증 | OK | 읽을 때마다 매니페스트 content_hash, 판정 PASS 여부, 문항 세트 해시, 어댑터 directory_hash, 시스템 프롬프트 파일 sha256 검증(reader.py:14-41). 변조 시험 4종(test_v2_contract.py:80, test_http.py:152, test_http_clients.py:64, test_gate_flow.py:335). 한계: 해시 기준이 같은 DB·같은 볼륨에 함께 있어 두 곳을 모두 바꾸는 공격자는 못 막음(서명 없음) |
| 반려/승인 감사 기록 | 문제 M (C6) | 반려·승인 모두 `approvals`와 `decisions`에 남고 불변(PK/UNIQUE, `_same`). 활성화·롤백은 포인터 `ext`/영수증에 행위자 기록. 공백: 거부된 시도(401/403/422 INTEGRITY)는 접근 로그 한 줄뿐이며 행위자가 없다(app.py:73-74) |

## 항목별 판정

범례: 자율 = 영역 에이전트가 단독 수정 가능, 결정 = 사용자(또는 헤드/계약 변경 요청) 결정 필요.

### A. 신뢰성

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| A1 외부 호출 timeout | OK | DB 접속·문장 3초(+얼면 1초 소켓 종료), /readyz 별도 연결 2초(postgres_store.py:41-60, 74-80, main.py:187-190). I1·I3 클라이언트 읽기 timeout 기본 10초(factories.py:25). 가짜 상류(멈춤·느림·5xx)로 시험(test_upstream_faults.py). 한계: 조금씩 보내는 응답의 전체 시간 상한 없음(boundary.md가 이미 기재) |
| A2 재시도 | OK | I1·I3 재시도 없음, 다음 주기(Loop 60초)로 미룸(gate.py:229-234). 포인터 비교 후 교체 재시도는 5회 상한(gate.py:128, 146), 이 쓰기들은 CAS/request_id로 멱등 |
| A3 부분 쓰기 | OK | 승인·판정·릴리스 행·포인터·영수증이 각각 한 트랜잭션. 번들은 `.tmp-<id>`에 쓰고 rename, 실패하면 정리(store.py:324-358). 커밋 실패로 남은 디렉터리는 읽기에 안 보이고 재생성 때 치움. 시험: test_upstream_faults.py:297 |
| A4 우아한 종료 | **문제 M** | `signal`·`shutdown` 처리 없음(grep 0건). `serve_forever()`만 있음(main.py:335)이고 Dockerfile `CMD ["python", ...]`(PID 1, 기본 SIGTERM 처분이라 컨테이너가 무시 → 10초 뒤 SIGKILL). 진행 중 승인(번들 복사)이 중간에 죽을 수 있다(트랜잭션이라 기록은 안 남지만 요청이 끊김). 제안: SIGTERM 핸들러로 `shutdown()`+루프 정지, 또는 compose `init: true`(deploy 확인 못 함). 자율 |
| A5 재시작 복구 | OK | PG 연결 끊김 시 `_conn()`이 재접속(postgres_store.py:117-124), Loop는 실패해도 다음 주기 계속(app.py:274-291), 복구 시험 test_pg_timeouts.py(이번엔 건너뜀). 단 시작 때 DB 불가는 E7 참조 |
| A6 무한 증가 | **문제 M** | 접수·판정·릴리스·포인터 이력은 불변이라 삭제 안 함(runbook.md:101), 릴리스마다 어댑터 사본을 통째로 복사(수 GB 가능, STATUS "정리 정책 미정"). `POST /v1/submissions`는 쓰기 토큰 4종이 무제한 호출 가능하고 수집기는 (문항×A×B) 곱을 매번 제출(collector.py:75-82). `releases/.tmp-*` 잔재는 수동 정리(runbook.md:100). 로그는 stdout. 제안: 릴리스 보존 개수·아카이브 정책과 접수 상한. 정책은 결정, 접수 상한·정리 도구는 자율 |
| A7 동시성 | **문제 M** | 정합성은 OK(승인 PK + IntegrityError→CONFLICT, gate.py:306-313; advisory lock, CAS). 문제: `commit_decision`의 트랜잭션이 저장소 전역 `RLock`을 쥔 채 `_stage_release`(어댑터 `copytree`)를 수행(store.py 433-453 부근 `with self._Txn`, postgres_store.py 273-295, `_Txn.__enter__`가 `s._lock` 획득). 읽기도 같은 락(`_q`)이라 큰 어댑터를 승인하는 동안 `/v1/active-pointer` 읽기까지 막힌다. survey는 5초 폴링·10초 timeout이므로 실패할 수 있다. PG는 단일 연결을 락으로 공유(postgres_store.py:173-186). 제안: 복사를 트랜잭션·락 밖에서 먼저 하고 rename만 안에서. 자율 |
| A8 healthz/readyz | OK | healthz 의존 무관 200(app.py:177), readyz는 DB 별도 연결 2초 안 503 + 접속정보 없음(app.py:179-185, boundary.md). I1·I3 문제는 503 대신 `judging_loop`에 노출(의도적, FAULT_POLICY 9와 일치) |
| A9 자원 한도 | **문제 M** | `ThreadingHTTPServer` 스레드 무제한(app.py:37), 요청 소켓 timeout 없음(느린 연결이 스레드를 영구 점유), `Content-Length: -1`이면 `rfile.read(-1)`이 EOF까지 읽음(app.py:111-114; 쓰기 토큰 보유자만 도달). 번들 GET은 임시 파일 2벌 생성(app.py:161, reader.py:87). Dockerfile/compose 자원 한도는 확인 못 함. 제안: 핸들러 `timeout` 설정, 음수 길이 거부, 동시 요청 상한. 자율 |

### B. 보안

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| B1 인증 | OK | healthz·readyz 외 모든 GET은 `_read_role()` 이후에만 라우팅(app.py:186), POST는 본문 읽기 전 토큰 확인(app.py:226). 등록되지 않은 경로도 토큰 없으면 403. 시험: test_http.py:55·87, smoke.sh의 토큰 없는 403 단언 |
| B2 인가 | **문제 M** | (1) 승인자 식별 위조 위험: 위 "이 영역 특유 점검" 참조. 제안: `X-Openit-User`가 없으면 approvals도 activate처럼 401(서비스 역할 제외), 또는 환경변수로 "헤더 필수"를 켜고 운영 기본값을 켬. HTTP.md:68이 "헤더가 없으면 본문 사용"이라 계약 변경 요청 필요 → 결정(헤드). (2) 읽기 토큰은 역할 구분 없이 전부 읽는다(README 4절·STATUS 기재). 읽는 내용에 환자정보가 없어 L. (3) 수평 권한 상승: 환자 세션 개념 없음, 해당 없음 |
| B3 비밀 | OK | `read_secret(NAME)` 파일 우선(main.py:118, 285, 325-332), 설정 파일 인라인 비밀 거부(main.py:164-201), 오류에 값 없음, smoke.sh가 inspect·env·로그에 평문 없음 확인, tests/test_secrets.py. 회전은 파일 교체 후 재시작(재적재 기능 없음, B12). 파일 권한은 F5 |
| B4 입력 검증 | 문제 L | 본문 1MiB 상한과 JSON 객체 검사(app.py:112-117), `limit` 1~500, ID 정규식 단순(ReDoS 없음, app.py:31), 열거값은 스키마가 검증, 경로 조작은 위 확인대로 차단. 남은 것: 음수 `Content-Length`(A9), 승인 본문의 `ext`가 크기·구조 제한 없이 저장됨(`GateApproval` 스키마가 임의 객체 허용, 1MiB 한도 안). 제안: 음수 거부, 승인 본문에서 `ext` 제거. 자율 |
| B5 인젝션 | 문제 L | SQL 파라미터화(OK), 명령 실행 없음, 모델/프롬프트 없음. 로그 인젝션: `log_message`를 재정의해 기본 구현의 제어문자 이스케이프를 우회(app.py:73-74; 요청 줄의 `\x1b` 등이 그대로 로그로). 제안: `%r` 또는 제어문자 치환. 자율 |
| B6 SSRF | 해당 없음 | 사용자 입력으로 정해지는 URL을 호출하는 경로가 없다. I1·I3 주소는 설정(`GATE_I1_URL` 등, factories.py)뿐 |
| B7 웹 | 해당 없음 | JSON API 전용, 쿠키·세션·CORS 헤더·HTML·서비스 워커 없음. 브라우저는 gateway를 거침(gateway 헤더는 deploy 몫, 확인 못 함) |
| B8 전송 | 확인 못 함 | 서버는 평문 HTTP 8080(main.py:331), 토큰이 Bearer로 내부망에서 평문 전송. TLS 종료 지점·네트워크 분리는 compose/gateway 소관이라 읽지 않음 |
| B9 의존성 | 문제 L | 핀: `requirements.lock`에 8개 패키지 `==` 고정(psycopg 3.3.6, jsonschema 4.26.0 등)이나 **해시 없음**(`--require-hashes` 미사용), boundary-contracts는 git 태그(변경 가능), 기반 이미지 `python:3.12-slim` 태그만(Dockerfile:5). 취약점: pip-audit 미설치 → **확인 못 함**. 컨테이너 이미지 스캔도 못 함. 제안: 해시 잠금, digest 고정(F2와 같은 뿌리). 결정(기반 이미지 정책은 헤드) |
| B10 속도 제한 | 문제 L | 인증 실패·접수 남발 제한 없음(app.py 전체). 토큰 무차별 대입 내성은 토큰 길이에 달림(발급은 deploy). 인증 실패 횟수 로그/경보 없음. 제안: 실패 로그 + gateway 제한 확인. 자율/결정 혼합 |
| B11 오류 노출 | 문제 L | 일반 예외는 `{"code":"INTERNAL"}`만 반환(app.py:133-135)이고 PG 오류는 종류+SQLSTATE만(postgres_store.py `_safe`). 단, 비ASCII 문자가 든 `Authorization` 헤더는 `hmac.compare_digest`가 TypeError를 내 500(+스택 로그)로 끝난다(app.py:90; 같은 입력으로 확인한 것은 `compare_digest("é","a")`의 TypeError뿐, 서버 호출은 하지 않음). 제안: bytes로 비교. 자율 |
| B12 토큰 수명·권한 | 문제 L | 토큰은 정적 문자열, 만료·폐기 없음(재시작으로만 교체), 역할별 최소 권한은 쓰기에서 적용(OK), 읽기는 구분 없음. DB 계정 권한은 C8 |

### C. 데이터·개인정보

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| C1 개인정보 목록 | OK | 환자 정보 없음(환자 대화는 다루지 않음, README). 저장: 직원 ID(`approver_id`, `requested_by`, `service:<역할>`), 승인·반려 사유 자유 텍스트, 문항 세트·어댑터·평가 보고서, 접근 로그의 클라이언트 IP. design.md 10절도 "입력 원문·개인정보 없음" |
| C2 최소 수집 | OK | 승인 기록은 필요한 필드만. 예외: `ext` 임의 객체(B4) |
| C3 보존·삭제 | **문제 M** | 삭제 경로 없음, 기본이 무기한(runbook.md:101 "삭제하지 않는다"). 감사 기록의 불변은 의도지만 보존 기간(직원 ID·사유 텍스트)과 어댑터 사본의 정리 기준이 정해져 있지 않다. 사용자 결정 필요(보존 기간, 아카이브) |
| C4 비식별 | OK | 로그에 본문·사유 없음(`log.*` 전수 확인: 요청 줄, 코드·메시지 200자, ID). 승인 사유는 DB에만. 학습 환류 없음 |
| C5 저장·전송 암호화 | 확인 못 함 | 볼륨·DB 암호화와 디렉터리 권한은 deploy/compose 소관. 코드는 `/data`를 gate 사용자(uid 10001) 소유로 만듦(Dockerfile:25)까지 확인 |
| C6 접근 기록 | **문제 M** | 성공한 승인·반려·활성화·롤백은 행위자와 함께 불변 기록(gate.py:105-106, 325-343). 공백: (1) 위 B2의 자기 신고 `approver_id`, (2) 거부·실패한 시도의 행위자 미기록(접근 로그에 `X-Openit-User` 없음), (3) 이미 활성인 릴리스 재활성화는 기록 없이 성공(gate.py:130-131), (4) 번들·판정 열람 기록 없음. 제안: 접근 로그에 토큰 역할과 `X-Openit-User` 추가, 거부 시도 로그. 자율(1은 결정) |
| C7 백업·복원 | 확인 못 함 | runbook.md:96-101에 "DB 덤프 + releases/ 디렉터리를 한 쌍으로" 절차는 있으나 둘의 일관된 시점 보장·주기·복원 시험·백업 권한은 이 영역 밖/미확인. DB와 파일이 한 쌍이라 시점 불일치 위험은 문서가 언급하지 않음 |
| C8 DB 계정 | 확인 못 함 | 계정 분리는 compose 소관. 코드는 시작 때 `CREATE TABLE IF NOT EXISTS`(postgres_store.py:125-135)를 하므로 런타임 계정에 DDL 권한이 필요하다(최소 권한과 충돌). 마이그레이션 전용 계정 분리 여부 미확인 |
| C9 마이그레이션 | 문제 L | 스키마 버전 표·마이그레이션 단계 없음, `IF NOT EXISTS`만(postgres_store.py:30-40, store.py `_SCHEMA`). 컬럼 추가 시 구버전과 신버전 공존·되돌리기 방법이 없다. 아직 스키마 변경이 없어 실해는 없음. 자율 |
| C10 정합성 | 문제 L | 유일성은 UNIQUE/PK로 있으나 외래키·CHECK 없음(`decisions.submission_id` 등), 레코드는 TEXT JSON(검사는 애플리케이션 스키마). 시간은 UTC `Z`(util.py:30), ID 정규식이 ASCII라 한글 정규화 문제는 해당 없음, 자유 텍스트 `reason`은 정규화 안 함. 자율 |

### D. 정확성·계약

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| D1 계약 일치 | 확인 못 함 | 실제 `boundary_contracts.clients`(`HttpReleaseReader`, `HttpGateService`)로 서버를 시험(test_http_clients.py)하고 통과했으나 `conformance/` 모음은 실행하지 않았다. 확인 필요 1건: 토큰 없음/틀림에 서버는 403(app.py:34 `PERMISSION_DENIED:403`), `PUBLIC_API.md:14`는 401이라고 적음. 후자가 gateway 공개 API 대상인지 I4·I5 대상인지 읽지 못함 |
| D2 상태 기계 | OK | 승인은 `AWAITING_APPROVAL`에서만(gate.py:296), 이미 결정됨→동일 결정 200/다른 결정 409, 활성화는 PASS만(reader.py:25), `assert_decision_rule`(승인 없는 PASS 금지, gate.py:25-34), 승인 직전 자동 검사 재실행(gate.py:335-340). 롤백은 from=현재·to≠from·to 검증(gate.py:176-190) |
| D3 멱등 | OK | 접수 ID = 조합 해시(gate.py:84-85), 승인 `ap-<sid>`, 릴리스 `rel-<sid>`, 롤백 `request_id`+요청 해시(다른 내용이면 CONFLICT, gate.py:147-151), 활성화 재호출은 현재 포인터 반환 |
| D4 시간 | OK | 시계 주입 가능(util.Clock), 모든 시각 UTC `Z`. 만료 개념 없음. 보고서 오래됨은 해시(STALE_REPORT)로 판단하므로 시계에 의존하지 않음 |
| D5 인코딩·크기 | OK | 본문 1MiB 상한(app.py:112), `ensure_ascii=False`로 UTF-8 저장·응답, 8MiB 규칙은 이 영역에 해당 없음. 음수 길이는 B4/A9 |
| D6 값 지어내기 | 해당 없음 | 모델 출력을 받지 않는다. 비슷한 요구인 "깨진 이웃 응답을 성공으로 취급하지 않음"은 INTEGRITY_ERROR 반려/건너뜀으로 구현되어 시험됨(boundary.md, test_upstream_faults.py) |
| D7 문서-코드 일치 | 문제 L | 어긋난 곳: README.md 3절 "이미지 안에서는 serve가 기본 진입점인지 미확인"(Dockerfile:42 `CMD ... serve`로 확인됨), README "239개 수집" 등 과거 수치와 4절 수치 혼재, design.md 8절 끝 "사람이 승인하는 단계는 브리프에 없다"(D53 이후 사실과 반대), runbook의 쓰기 토큰 예시(runbook.md 환경 변수 표)에 `release-approver` 항목 없음, brief.md는 D53 대체 주석이 달려 있으나 헤드 소유. 자율 |

### E. 운영성

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| E1 구조화 로그 | 문제 L | 평문 한 줄 로그(main.py:263), 상관 ID 없음, 접근 로그에 행위자·역할 없음(C6). 비밀·PHI는 제외됨. 자율 |
| E2 메트릭·경보 | 문제 L | 메트릭 엔드포인트 없음. `/readyz`에 `awaiting_approval` 건수와 루프 상태는 있으나 "승인 대기 N시간 초과"나 INTEGRITY_ERROR 경보 기준은 없다. 감시 연결은 deploy. 자율(기준값은 결정) |
| E3 설정 | 문제 L | 대기 상한 값은 양수 검사로 시작 거부(main.py:266-277), 필수 토큰·스키마 경로 없으면 거부. 그러나 `GATE_POLL_SECONDS`는 `float()`만(main.py:320; 0 이하면 바쁜 루프 또는 `wait` 오류), `PORT`도 `int()` 직접. 자율 |
| E4 런북 | OK | runbook.md에 승인 정체, 자동 검사 정체(RECEIVED), INTEGRITY_ERROR 대응, 백업·정리, 비밀 파일화 절차. boundary.md 장애 영향 표가 장애별 동작을 적음 |
| E5 감시·알림 경로 | 확인 못 함 | 감시 대상·알림은 deploy 소관. 이 영역은 `/readyz`를 제공 |
| E6 용량 계획 | 문제 L | 근거 측정 없음. STATUS가 대용량 어댑터 복사 시간·디스크를 "확인하지 못함/미정"으로 인정. 측정은 자율 |
| E7 시작 순서 | 문제 L | DB가 안 열리면 `PostgresStore.__init__`이 UNAVAILABLE을 올려 프로세스가 곧바로 종료(main.py:285 → postgres_store.py:125-137). 의존 대기 루프 없음 → compose `restart`/healthcheck 조건에 의존(확인 못 함). `serve`에 시작 재시도(상한 포함)가 있으면 더 안전. 자율 |
| E8 시간 불변식 | OK | 영역 값(DB 3/3/2, +1초 소켓 종료, I1·I3 10초, 폴링 60초)이 boundary.md 표와 코드 기본값이 일치(postgres_store.py:50-52, main.py:187-190, factories.py:25). gateway 쪽 게이트 프록시 상한 부재는 FAULT_MATRIX C7·C8에 이미 기록됨(deploy 몫). 이 영역의 승인·활성화 요청 자체의 총 마감 시간은 없음(번들 복사는 상한 밖, boundary.md가 명시) |

### F. 배포·이미지

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| F1 권한·노출 | 확인 못 함 | Dockerfile: 비root(uid 10001 `gate`, 쉘 nologin, Dockerfile:25·41), 추가 capability·docker.sock 요구 없음, HEALTHCHECK 있음. 읽기 전용 루트 가능성: 쓰기는 `/data`와 `tempfile`(`/tmp`)뿐이라 tmpfs `/tmp`가 있으면 가능하다고 읽히나 시험하지 않음. 호스트 포트 바인딩·privileged 여부는 compose라 못 읽음 |
| F2 이미지 핀·SBOM | **문제 M** | `FROM python:3.12-slim`(digest 없음, Dockerfile:5), 잠금 파일 해시 없음(B9), boundary-contracts·turn-engine·model-runtime은 태그를 `git archive`해 wheel로 만듦(scripts/stage_context.sh:11, build_image.sh:19; 태그는 이동 가능), SBOM·취약점 스캔 없음. 결정(헤드의 이미지 정책) |
| F3 compose | 확인 못 함 | 이 영역에는 compose가 없다(`compose.dev.yaml` 삭제됨, D85). 자원 한도·restart·볼륨 권한은 deploy |
| F4 되돌리기·업그레이드 순서 | 문제 L | 릴리스 되돌리기(포인터 롤백)는 구현·시험됨. 업그레이드는 버전 정렬 검사(CONTRACT_COMPAT가 turn-engine·model-runtime 버전 불일치를 반려, runbook "이미지")가 있으나 wheel이 없으면 `unset`으로 모든 후보를 반려(runbook 이미지 절). 게이트 이미지 자체의 되돌리기와 DB 스키마 호환(C9) 절차는 문서에 없음. 자율 |
| F5 비밀 파일 권한 | 문제 L | runbook은 비밀 파일 모드를 "0644 이상 또는 해당 uid 소유"로 안내하고 smoke.sh도 0644를 쓴다(체크리스트는 0600/0400). 제안: uid 10001 소유 0400을 표준으로 문서화. 비밀이 compose 환경에 없는지는 compose를 못 읽어 확인 못 함. 자율(문서) |
| F6 레지스트리·CI | 확인 못 함 | 이 영역에는 CI 정의가 없고 이미지 게시는 deploy(D24). 참고: `scripts/build_image.sh`가 `../turn-engine`, `../model-runtime`을 `git archive`로 읽고 `dev-postgres.sh`가 `../deploy`를 호출한다(CLAUDE.md 공통 규칙은 읽기 허용 폴더를 두 곳으로 한정) → 규칙과 스크립트의 차이를 헤드가 정리할 것 |

### G. 성능·용량

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| G1 처리량·지연 문서화 | 문제 L | DB 상한의 근거는 "설계 판단, 측정 아님"(boundary.md). 처리량·승인 소요 시간·번들 크기별 측정 없음. 자율 |
| G2 쿼리·락 | **문제 M** | `list_submission_views`가 `submission_seqs()`로 전체 접수를 읽고 건마다 `get_work`+`latest_decision` 2쿼리(views.py:48-58) → 접수가 늘수록 승인 대기 목록(`?status=AWAITING_APPROVAL`)이 선형으로 느려지고 단일 연결 락을 오래 쥔다. `process_pending`도 상태별 조회는 전체 `SELECT submission_id, state`(store.py:`submission_ids`). `decisions`·`submissions`에 `state`/`submission_id` 인덱스 없음(UNIQUE 외). 풀 없이 단일 연결+락(A7). 제안: 상태 컬럼으로 필터·인덱스. 자율 |
| G3 큰 입력 | **문제 M** | 활성화 때마다(gate.py:127), 롤백 대상 검증(gate.py:185), 번들 GET마다(app.py:162) 어댑터 전체를 임시 디렉터리로 복사하고 `directory_hash`를 계산하며, 번들 GET은 거기에 tar 임시 파일을 한 벌 더 만든다. 승인 시에도 복사 두 번(I3→임시, 임시→릴리스). 수 GB면 디스크·CPU·시간 폭주. 제안: 해시 검증을 제자리에서 스트리밍, 번들 tar는 검증 후 직접 스트리밍. 자율 |

### H. 시험 품질

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| H1 핵심 경로 실제 구성요소 | OK | 승인/활성화/롤백이 실제 `GateEngine`·`Store`(memory·sqlite, 있으면 PG)·실제 `GateHTTPServer`·실제 `boundary_contracts.clients`로 시험(test_gate_flow, test_http, test_http_clients, test_http_integration). I1·I3는 대역 서버(tests/http_neighbors.py)로 실제 서비스가 아니다(문서에 명시). 환자 턴·알림은 이 영역에 없음 |
| H2 간헐 실패 | 문제 L | 포트는 모두 0번(자동 배정, 예: test_http.py:17)이라 고정 포트 문제 없음. 실제 시간 비교(`< TIMEOUT*3`, `< 4`초, test_upstream_faults.py:214·249, test_pg_timeouts.py:121)는 느린 머신에서 흔들릴 수 있다. 이번 1회 실행은 통과, 반복 실행은 하지 않음. 자율 |
| H3 건너뜀 사유 | OK | 195건 건너뜀 모두 사유 출력(`TEST_DATABASE_URL이 없어 ... PASS로 세지 않는다`, docker 부재), 대체로 같은 적합성 시험이 memory·sqlite에서 돈다. 단 PG 전용 경로(advisory lock, 별도 연결 /readyz, 소켓 종료)는 이번 점검에서 **실행해 보지 못했다** |
| H4 부정 시험 | OK | 잘못된 역할 403(test_gate_flow.py:123-124), 읽기 토큰으로 쓰기 403, 잘못된 헤더 형식 400(test_http.py:338-339), STALE/ALREADY_DECIDED, 변조 번들 422, 쓰기 불가 503. 없는 것: 비ASCII Authorization, 음수 Content-Length, 승인 본문 `ext` |
| H5 환경 의존 | 문제 L | 시험이 같은 워크스페이스의 `../boundary-contracts`(편집 설치)와 `../survey-schema` 경로, `.venv` 설치 방식에 의존(README 3절, conftest). 시계는 주입, 디스크는 tmp_path. PG 시험은 docker와 `../deploy/scripts/dev-postgres.sh`에 의존. 자율(문서화) |

### I. 도메인·안전

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| I1 환자 안전 결정 | OK | 합격 임계치·자동 PASS를 코드에 두지 않는다(D53; policy.py가 이전 형식 파일을 거부, `required_checks` 고정 4종). 임상 승인 필수 규칙(`clinical_basis_approved`, 승인 뒤 더 늦은 비승인 검수가 있으면 FAIL)은 D30에서 온 규칙이며 checks.py:223-245에 근거 번호와 함께 있다. 사용자 결정으로 남은 O11은 문서에 열린 항목으로 표시됨 |
| I2 환자 문구 출처 | 해당 없음 | 환자에게 가는 문구를 만들지 않는다. 시스템 프롬프트는 모델 패키지에서 바이트 그대로 복사하고 sha256을 검증함(gate.py:353-356). 임상 검토 표시는 문항 세트의 검수 기록으로 확인 |
| I3 실패 시 환자 노출 | OK | 게이트 중단·승인 지연·번들 쓰기 실패 어느 경우도 이전 활성 포인터가 유지되어 환자 경로는 마지막 릴리스를 계속 쓴다(boundary.md 장애 영향, test_upstream_faults.py:357). 잘못된 릴리스가 환자에게 가려면 사람의 APPROVE와 operator의 activate가 모두 필요. 단 survey가 게이트가 죽은 채로 새로 기동하는 경우는 survey 영역 소관(FAULT_MATRIX A7) |

## 같은 원인 묶음 (수정 시 함께 보기)

- **승인자 신원**: B2 + C6(1). 헤더 필수화 + 접근 로그에 행위자 기록. 필수화는 `HTTP.md` 변경 요청이 필요할 수 있음 → 헤드/사용자 결정.
- **큰 어댑터**: A6 + A7 + G3 + E6. 한 번의 복사 방식 개선(락 밖 복사, 제자리 해시)과 보존 정책(C3, 결정)으로 같이 풀린다.
- **서버 방어선**: A4 + A9 + B4 + B10 + B11. 핸들러 timeout, 음수 길이, 비ASCII 헤더, SIGTERM 처리는 모두 `app.py`/`main.py` 안의 자율 수정.
- **공급망**: B9 + F2 + F6. 기반 이미지 digest, 해시 잠금, 태그 이동 가능성은 헤드 정책 필요.
- **문서 어긋남**: D7 + F5(문서 부분) + C7(절차 부분). 자율.

## 이 점검이 읽지 못한/얕게 본 곳

- **deploy 전부**: compose(자원 한도, restart, 포트 바인딩, 네트워크 분리, init), Caddyfile(gateway가 클라이언트 `X-Openit-User`를 지우는지, 승인자·operator 토큰이 누구에게 있는지, 게이트 프록시 timeout), 토큰 발급·회전, DB 계정 권한, 백업 주기, CI·레지스트리. 따라서 B2/C6(조건부 H), B8, C5, C7, C8, E5, F1, F3, F6은 확인 못 함 또는 부분 판정이다.
- **PostgreSQL 경로를 실행하지 못함**: pytest에서 PG 시험과 docker pause 시험이 건너뛰어졌다. advisory lock, `_Armed` 소켓 종료, 별도 연결 `/readyz`는 코드만 읽었다(README의 "PG 포함 485 통과"는 영역 문서 주장이며 재현하지 않았다).
- **의존성 취약점**: pip-audit 미설치로 못 함. 핀 상태만 판정.
- **이미지 빌드·smoke.sh 미실행**: Docker 빌드, 컨테이너 안 비root·읽기 전용 파일시스템 동작을 직접 확인하지 않았다(스크립트와 Dockerfile을 읽음).
- **`checks.py`, `schemas.py`, `factories.py`, `postgres_store.py`의 앞뒤 일부**는 훑기만 했다(CLINICAL_SAFETY와 정책 일부만 정독). `boundary-contracts/conformance/` 모음과 HTTP.md 전체, CONVENTIONS 9절은 읽거나 실행하지 않았다.
- **실제 서버를 띄운 동적 시험은 하지 않았다**: 비ASCII Authorization의 500, 음수 Content-Length의 블로킹, SIGTERM 무시는 코드·표준 라이브러리 동작에서 추론한 것이다(비ASCII의 `compare_digest` TypeError만 단독 확인).
- **A7의 읽기 차단**은 락 구조를 읽고 추론했다. 실제 큰 어댑터로 승인 중 `/v1/active-pointer` 응답 지연을 측정하지 않았다.
- **README 5절의 열린 항목**(G08 등)과 `head/docs/OPEN_GAPS.md`는 읽지 않았다.
