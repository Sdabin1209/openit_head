# 전수 점검: ops-feedback (읽기 전용 감사)

> 점검일 2026-10-28. 대상 `/home/user/sdabin/healthKiosk/ops-feedback`(커밋 c9b50bd, 작업 트리 변경 없음 확인: `git status --short` 빈 출력). 기준 `head/docs/AUDIT_CHECKLIST.md` A~I. 코드·설정·문서는 수정하지 않았다. 이 영역 `.venv`로 시험을 읽기 전용으로 돌렸다(`-B -p no:cacheprovider`).
> 근거 표기: `파일:줄`은 `ops-feedback/` 기준 상대 경로. "시험"은 이 세션에서 돌린 것, "코드 읽음"은 읽기만 한 것, "실측"은 임시 스크립트(scratchpad)로 직접 돌려 본 것.

## 요약

**분모: 체크리스트 63항목(A9 B12 C10 D7 E8 F6 G3 H5 I3) 전부 판정. 영역 특유 점검 S1~S7은 별도(아래).**

| 판정 | 개수 (/63) |
| --- | --- |
| OK | 20 |
| 문제 H | 1 |
| 문제 M | 14 |
| 문제 L | 18 |
| 해당 없음 | 4 |
| 확인 못 함 | 6 |
| 합계 | 63 |

**H 문제 (1건)**
1. **C3 원본 보존 기본 무기한 + 삭제 경로 부재**: `retention.raw_days`가 `null`(= 삭제 안 함)이 예시 기본이고(`config/job.example.yaml:86-87`, `src/ops_feedback/job.py:150-153`), 처리가 끝난 뒤에도 TraceEnvelope 원본 전체(발화·답변·직원 ID 포함)가 평문으로 남는다. 실패 사례 저장소(cases, traces, aux)는 삭제 코드가 아예 없고, 세션·환자 단위 삭제 경로도 없다. 운영 잡 설정(deploy 소유)의 실제 값은 읽지 못해 확인 못 함. 값 결정은 사용자 몫(brief 5절 "보관 기간은 사용자가 정한다"), 삭제 기능 자체(실패 사례·비식별 trace 정리, 처리 완료 원본 정리 옵션)는 자율 수정 가능.

**M 문제 (14건, 원인 묶음)**
- 개인정보: C2 최소 수집 위반(전체 봉투 보관), C4 비식별 허용 목록이 모델 출력 문자열과 검토자 자유 입력을 값 검증 없이 통과(next_item 실측), C5 저장 시 암호화·파일 권한 없음, C6 검토자 행위 기록(reviewed_by)이 호출자 헤더 값이고 열람 기록 없음, C7 백업·복원 없음, C8 DB 계정 최소 권한(앱이 시작 때 DDL 실행, 한 프로세스가 두 DB 접속 정보 보유).
- 신뢰성·남용: A6 무한 증가(C3과 같은 원인), A9/G3 미처리 원본 전량 메모리 적재와 소켓 timeout·스레드 상한 없음, B10 속도 제한 없음과 인증 없는 `/readyz`가 요청마다 DB 새 연결, B12 토큰 수명·DB 권한.
- 운영·배포·시험: E2 지표·경보 없음, F2 이미지·의존 핀 불완전(베이스 이미지 태그만, 해시 없는 잠금), H3 운영 백엔드인 PostgreSQL 시험 110건이 기본 실행에서 건너뛰어짐.
- 영역 특유 S5(신규): 수집 토큰만 있으면 임의 `release_id`로 위조 Trace를 넣어 실패율을 올릴 수 있다. 운영 롤백이 꺼져 있는 동안은 잠복 위험.

**영역 특유 S1~S7**: 6개는 C항목과 같은 원인이고 신규는 S5 하나다(위 M에 포함). 라우트 전수 표는 S7.

---

## 항목별 판정

### A. 신뢰성

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| A1 외부 호출 timeout | OK | 나가는 호출만 해당. PostgreSQL 접속·문장·probe·DDL 상한이 기본 3/3/2/30초이고 잘못된 값은 시작 거부(`src/ops_feedback/pgbase.py:20-36,39-45`), 서버가 얼어도 +1초에 소켓을 닫는다(`pgbase.py:48-57,102-129`). 이웃 I4/I5는 `boundary_contracts.clients`의 읽기 timeout(10초)에 롤백 평가 전체 상한 60초(`job.py:160-192`). 시험: `tests/test_postgres_timeout.py`(docker pause, 이번 실행에서는 PG 없어 건너뜀), `tests/test_upstream_faults.py`(통과). 들어오는 소켓에 timeout이 없는 것은 A9/B10. |
| A2 재시도 | OK | 재시도는 연결 끊김 때 같은 멱등 문장 1회뿐(`pgbase.py:102-129`, INSERT는 ON CONFLICT, `logstore.py` 쓰기). 롤백 전달은 같은 `request_id`로 다음 잡 실행에서 재전송(`rollback.py:447,465`). 백오프·지터는 없다(재시도 주기는 deploy 스케줄러가 정함). 게이트가 request_id를 멱등으로 받는지는 확인 못 함(boundary.md 스스로 인정). |
| A3 부분 쓰기 | OK | 쓰기는 자동 커밋 단일 문장(`pgbase.py:66`). 잡은 trace 저장, 게시, 처리 표시 순서이고 재실행이 이어서 처리(`job.py:108-148`). 시험은 예외로 중단 모사(`tests/test_job.py`). SIGKILL 시험은 없음(boundary.md가 인정). |
| A4 우아한 종료 | 문제 L | `api.py:271-276`에 SIGTERM 처리가 없고 `serve_forever`를 멈추는 경로가 없다. 이미지 CMD가 `python`을 PID 1로 직접 실행(`Dockerfile:29`)해 SIGTERM이 무시되어 `docker stop`이 10초 뒤 SIGKILL로 끝난다. 쓰기가 단일 문장이라 데이터 손상은 없고 호출자(survey)가 재시도. 제안: SIGTERM 핸들러로 `shutdown()`, 또는 `--init`. 자율 수정 가능. |
| A5 재시작 복구 | OK | 스키마 `CREATE IF NOT EXISTS` 멱등(`pgbase.py:83-94`), 끊긴 연결 자동 재접속(`pgbase.py:118-123`, `tests/test_postgres_reconnect.py`는 PG 없어 건너뜀). DB가 시작 때 죽어 있으면 종료 코드 2(`api.py:266-268`)이므로 재시작은 restart 정책(deploy)에 의존. |
| A6 무한 증가 | 문제 M | `raw_traces`는 기본 삭제 없음(C3). `failures.db`의 cases, traces, aux에는 정리 코드가 없다(`failurestore.py` 전체에 DELETE 없음). 같은 원인은 C3. 제안: C3과 함께 처리. 값은 사용자 결정, 기능은 자율. |
| A7 동시성 | OK | `UNIQUE(session_id,turn_id)`+`ON CONFLICT DO NOTHING`(`logstore.py` PG DDL, insert_if_absent), 같은 키 8개 동시 전송 시험(통과: `tests/test_conformance_ingest.py`), 게시 경합은 CONFLICT(boundary.md D6 행). 단점: PG 연결 1개를 `RLock`으로 직렬화(`pgbase.py:78,118`)해 처리량 한계(G1). |
| A8 healthz/readyz | OK | `/healthz` 의존 무관 200(`api.py:148-149`), `/readyz`는 새 연결로 두 저장소를 동시에 확인해 상한 2초(`api.py:150-172`, `pgbase.py:134-158`). 단 `/readyz`가 인증 없이 저장소 종류·지원 버전을 노출(L, 정보 노출 경미). |
| A9 자원 한도 | 문제 M | `ThreadingHTTPServer`(`api.py:244`)는 스레드 상한이 없고 핸들러 `timeout`이 없어(`BaseHTTPRequestHandler.timeout=None`) 본문을 덜 보내는 연결이 스레드를 영구 점유한다(`api.py:233` `rfile.read(n)`). 요청당 최대 8 MiB(`api.py:45`)를 메모리에 읽는다. 컨테이너 자원 한도는 이 리포지토리에 없음(deploy). 제안: 핸들러 `timeout`, 동시 연결 상한. 자율 수정 가능. 큰 입력은 G3. |

### B. 보안

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| B1 인증(기본 거부) | OK | 아래 S7 라우트 표. `/v1/*` GET은 읽기 토큰 필수(`api.py:93-95,146-147`), POST는 경로별 토큰 필수(`api.py:178-180,224-225`), 세 토큰 종류가 서로 달라야 시작(`api.py:68-69`). 인증 없는 것은 `/healthz`, `/readyz`뿐. 시험·스모크: 수집 토큰으로 읽기 403, 읽기 토큰으로 수집·검토 403(`scripts/smoke.sh:229-236,250`, 이번 세션에서는 Docker 스모크 미실행, 단위 시험 `tests/test_api*.py` 통과). |
| B2 인가 | 문제 L | 읽기 토큰은 `역할=토큰` 형식이나 역할이 어디에도 쓰이지 않는다(`api.py:50-58`은 역할을 저장만 하고 `api.py:93`에서 버림). 모든 읽기 토큰이 모든 사례·비식별 trace를 읽는다. 데이터가 사용자별이 아니어서 수평 상승 개념은 없다. 제안: 역할별 범위가 필요 없으면 형식을 단순화, 필요하면 적용. 자율 수정은 가능하나 소비자 영역 의사 확인 필요. |
| B3 비밀 | 문제 L | 토큰·salt는 `read_secret(NAME_FILE)`(`api.py:250-252`, `job.py:233`), 잡 설정의 직접 비밀은 시작 거부(`config.py:114-128`), DB URL은 출력하지 않음(`pgbase.py:67-68,150`), 스모크가 `docker inspect/exec env`에 값이 없음을 확인(`smoke.sh:207-208`). 문제: (1) 운영에서도 환경 변수 폴백이 허용됨(D84 문서상 개발용), (2) 토큰은 시작 때 한 번 읽어 회전하려면 재시작(`api.py:250`), (3) 토큰 길이·엔트로피 검사가 없음, (4) salt 회전 불가(바꾸면 case_id·trace ref 전부 변경, runbook.md:59). 제안: 회전 절차 문서화, salt 회전 정책(사용자 결정). |
| B4 입력 검증 | 문제 L | 본문 8 MiB 상한, `Content-Length` 검사, id 정규식, `limit` 1~500, 열거값 검사는 있음(`api.py:45,118,188,205`). 문제: (1) `json.loads`가 `RecursionError`(깊게 중첩된 JSON, 실측 확인)를 던지면 수집 경로에서 잡히지 않아(`api.py:233-235`는 ValueError만) 응답 없이 연결이 끊김, (2) `Authorization`에 ASCII가 아닌 문자가 있으면 `hmac.compare_digest`가 TypeError(실측 확인) → 수집은 미처리 예외로 연결 끊김(`api.py:224`), 읽기·검토는 403이 아니라 503 "내부 오류"(`api.py:140-142,213-215`)로 보여 호출자가 재시도할 수 있음. 두 경우 모두 유효한 토큰이 필요하거나 단순 거절이라 영향 작음. 제안: 예외 처리 추가, 비교는 bytes로. 자율 수정 가능. ReDoS: 잔존 패턴은 설정 소유이고 선형(`config/job.example.yaml:64-66`). |
| B5 인젝션 | 문제 L | SQL은 모두 파라미터화(`logstore.py`, `failurestore.py`, f-string은 정수 `SET statement_timeout`만: `pgbase.py:84,92`). 프롬프트 인젝션은 모델을 호출하지 않아 해당 없음. 문제: 로그 형식이 `'{"msg":"%(message)s"}'`로 이스케이프가 없고(`api.py:248`) 요청 경로를 그대로 싣는다(`api.py:76`) → 인증 전 요청의 경로에 `"`를 넣어 로그 줄을 위조 가능. 제안: JSON 포매터 사용. 자율 수정 가능. |
| B6 SSRF | 해당 없음 | 요청 입력으로 URL을 만들어 호출하는 코드가 없다. 나가는 URL(`release_reader.args.base_url`)과 `factory: 모듈:함수`는 설정 파일에서만 오고 임의 모듈을 import한다(`job.py:225-227,244-246`). 설정은 deploy 소유 신뢰 입력이라는 전제(메모). |
| B7 웹 | 해당 없음 | JSON API만 제공, 쿠키·세션·HTML 없음. CORS 헤더를 내지 않음(기본 차단). 브라우저(reviewer)는 gateway 경유이고 보안 헤더는 gateway 소관(`FAULT_MATRIX` D6, Caddyfile은 읽지 못함). |
| B8 전송 | 확인 못 함 | 서비스는 평문 HTTP만 말한다(TLS 코드 없음). TLS 종료 지점, PostgreSQL `sslmode`(URL 안), 내부 평문 구간의 노출 범위는 deploy 소관이고 이 영역 문서에도 적혀 있지 않다(grep "TLS|https" 결과 없음). 원본 PHI가 이 평문 구간을 지난다. 제안: boundary.md에 전송 가정 명시. |
| B9 의존성 | 문제 L | `requirements.lock`에 서드파티 정확 버전 고정(PyYAML 6.0.3, jsonschema 4.26.0, psycopg 3.3.6 등), `pip check` 이상 없음. 문제: 해시 고정 없음(`Dockerfile:7`에 `--require-hashes` 없음), `pip-audit`는 설치돼 있지 않아 취약점 조회를 못 했다(설치 금지 제약). boundary-contracts는 태그 v2.0.2의 `git archive` wheel(`scripts/build_wheels.sh`). 취약점 점검은 확인 못 함. |
| B10 속도 제한 | 문제 M | 속도 제한, 연결 상한, 실패 잠금 없음. 특히 `/readyz`는 인증 없이 호출 때마다 PG 새 연결 2개(두 저장소)를 연다(`api.py:153,159-164`, `pgbase.py:143`) → 인증 없는 반복 호출로 DB 연결 소진 가능(gateway가 막는지는 확인 못 함). 토큰 추측 시도에 대한 지연도 없음. 제안: `/readyz` 결과 짧은 캐시(1~2초), 동시 연결 상한. 자율 수정 가능. |
| B11 오류 노출 | OK | 오류 본문은 코드+고정 문구 또는 스키마 규칙 이름·경로만(`schemas.py:43-48`, "값 조각 제외" 주석), 예기치 못한 예외는 "내부 오류"(`api.py:140-142,241-242`), DB 예외는 클래스 이름만(`pgbase.py:68,129,150`). 단 미지원 메서드는 표준 라이브러리 HTML 501. |
| B12 토큰·최소 권한 | 문제 M | 정적 장기 토큰, 만료·회전 없음(B3). 서버가 시작 때 `CREATE TABLE`을 실행(`pgbase.py:83-94`)하므로 앱 DB 계정에 DDL 권한이 필요하다(C8). 읽기 토큰 하나로 모든 사례 열람. 제안: DDL을 마이그레이션 단계로 분리, 계정 분리(사용자/헤드 결정 일부). |

### C. 데이터·개인정보

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| C1 저장·전송·기록 목록 | 문제 L | 영역 문서에 PHI 위치를 한곳에 모은 목록이 없다(design.md:39 등에 분산). 이 감사가 아래 "S1/S3" 표로 만들었다: 원본 `raw_traces.envelope`(평문 TEXT), `session_id`, `turn_id`, `release_id`, `received_at`(`logstore.py` DDL); 사례 `cases.record`(비식별 뒤); `traces`(비식별 trace); `aux`(지표 스냅샷, 롤백 요청·영수증); 로그(요청 줄 경로만). 제안: boundary.md에 목록 추가. 자율 수정 가능. |
| C2 최소 수집 | 문제 M | 탐지에 필요한 건 일부 필드인데 봉투 전체(`session_before` 대화 로그, `log_entry.staff_id`, 발화 원문 등)를 평문으로 저장(`logstore.py` `insert_if_absent`, `send`). 처리(`DONE_CASE`/`NO_FAILURE`) 뒤에도 원본이 남는다(`job.py:97-148`은 표시만 바꿈). 제안: 처리 완료 뒤 원본 삭제 또는 단축 보존(사용자 결정). |
| C3 보존·삭제 | **문제 H** | (1) `raw_days: null` = 무기한이 예시 기본(`config/job.example.yaml:86-87`), 로더도 null을 허용(`config.py:146-147`). (2) 삭제는 `purge_received_before`(`logstore.py` 두 백엔드) 하나뿐이고 `received_at` 기준이라 처리 여부와 무관(미처리 원본도 지울 수 있음: 정체가 보존 기간보다 길면 처리 전에 유실) — 잡이 돌 때만 실행(`job.py:150-153`). (3) `failures.db`(cases, traces, aux)는 삭제 경로 없음. (4) 세션·환자 단위 삭제(요청 시 삭제) 경로 없음. (5) 운영 잡 설정의 실제 `raw_days`는 읽지 못함(deploy 소유; FAULT_MATRIX에도 없음). 제안: 처리 완료 원본은 짧게(또는 즉시) 삭제하는 옵션, 사례·trace 보존 기간 설정과 정리 잡, 세션 단위 삭제 CLI. 값은 사용자 결정, 코드는 자율 수정 가능. |
| C4 비식별 | 문제 M | 상세는 S1. 요약: 허용 목록 방식이고 `Value` 정의·자유 문자열·미지정 키는 지움(실측: 발화, 답변 값, 추출 이유·메모, 응답 문장, `staff_id`, 위반 `message` 모두 `[MASKED]`). 그러나 `keep_string_keys`에 든 키(`question_id, slot_id, repeat_key, code, path, action, next_item`)는 값을 **검증 없이 그대로** 통과시키고 잔존 검사는 이메일·전화·주민번호 정규식뿐(`deid.py:224-225,271-276`, `config/job.example.yaml:55,64-66`). 실측: `extract_output.next_item="홍길동 환자"`가 비식별 결과에 그대로 남음. 한국어 이름·주소는 잔존 검사로 못 잡음. 또 검토자가 쓰는 `expected`, `reviewed_input`은 비식별/패턴 검사를 거치지 않음(`review.py:331-336`, 코드 주석도 "건드리지 않는다"). 모델 환류(I7 소비자)로 나가는 경로. 제안: 유지 키에 형식 검증(예: `question_id`·`slot_id` 패턴, `action` 열거), 검토자 입력에도 잔존 패턴 검사. 자율 수정 가능(허용 형식 정의는 헤드/사용자 확인). 모델 출력이 열거로 제한된다면 위험은 낮아진다(그 전제는 이 영역에서 확인 못 함). |
| C5 저장·전송 암호화 | 문제 M | 원본이 평문 TEXT(`logstore.py` DDL), SQLite 파일은 기본 권한(프로세스 umask), 앱 수준 암호화 없음. 볼륨·디스크 암호화, PG TLS, 볼륨 권한은 deploy 소관이라 확인 못 함. 제안: 위험을 문서화하고 deploy에서 디스크 암호화/권한 확인. |
| C6 접근 기록·위조 | 문제 M | 상세는 S4. 검토자 기록 `ext["ops-feedback"].reviewed_by`는 호출자가 보낸 `X-Openit-User` 헤더 값(Id 형식만 검사) 또는 역할 이름(`api.py:204-208`, `review.py:66`). 검토 토큰은 역할 단위(사람별 아님)라 토큰을 가진 누구나 임의 사용자명으로 기록할 수 있다. gateway가 헤더를 덮어쓰는지는 Caddyfile을 읽지 못해 확인 못 함. 열람 기록(누가 어떤 사례·trace를 읽었나)은 없고 접근 로그에 사용자 정보가 없음(`api.py:75-76`). 원본 DB 직접 열람은 "기록한다"는 문장뿐 수단 없음(runbook.md:122). 긍정: 사례는 version 불변이고 같은 version 다른 내용은 CONFLICT(`failurestore.py:302-324`)라 API로는 이력을 고칠 수 없다. 제안: 검토 서비스 계정을 사람별 토큰으로 하거나 gateway 서명 헤더, 열람 감사 로그. 헤드/사용자 결정 일부. |
| C7 백업·복원 | 문제 M | 이 영역에 백업·복원이 없고 문서도 "정책 밖, 원본 손실은 복구할 수 없다"(runbook.md:121). deploy가 백업 스크립트를 가진다는 기록은 있으나(FAULT_MATRIX:457) ops_log/ops_failure를 포함하는지, 복원 시험, 백업 파일 권한·암호화·보존은 확인 못 함. 제안: O16(허용 중단·복구 시점) 결정 후 deploy와 정렬. 사용자 결정 필요. |
| C8 DB 최소 권한 | 문제 M | 한 프로세스(ingest-api)가 원본 로그 DB와 실패 사례 DB 접속 정보를 모두 갖는다(`api.py:260-263`, `storage.py`), 잡도 같다(`job.py:236-237`). 원본 읽기를 비식별기에만 주는 것은 코드 관례(`DeidentifierView`, `tests/test_raw_access.py`)이고 DB 권한으로 강제되지 않는다. 앱이 시작 때 DDL 실행(B12). 서비스별 DB 분리는 deploy가 함(FAULT_MATRIX D1·D4). 제안: ingest는 raw INSERT 전용 계정, 잡은 raw SELECT/UPDATE/DELETE, 읽기 서비스는 failures SELECT 전용 계정. 헤드/deploy 결정 필요. |
| C9 마이그레이션 | 문제 L | `CREATE TABLE IF NOT EXISTS`만 있고 스키마 버전 표·마이그레이션·되돌리기 절차가 없다(`logstore.py`, `failurestore.py` DDL, `pgbase.py:83-94`). 컬럼이 바뀌면 기존 DB에 조용히 적용되지 않음. 제안: 스키마 버전 행과 단계별 마이그레이션. 자율 수정 가능. |
| C10 정합성 | 문제 L | UNIQUE(`raw_traces(session_id,turn_id)`, `cases(case_id,version)`)와 NOT NULL은 있음. 시각은 UTC `Z` 초 단위 TEXT(`clock.py:11-18`), 문자열 비교에 의존. 외래키 없음(`deidentified_trace_ref` 존재는 코드 검사 `failurestore.py`, DB 제약 아님). 한글 유니코드 정규화(NFC) 없음: 클라이언트가 보낸 id를 그대로 사용. 제안: 경미. 자율 수정 가능. |

### D. 정확성·계약

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| D1 계약 일치 | OK | 응답은 모두 계약 스키마로 검증 후 반환(`api.py:109,133,209`, `logstore.py` `IngestResult`), 오류 코드→HTTP 매핑(`api.py:43-44`), 적합성 시험 통과(`tests/test_conformance_*.py`, 이번 실행 295 통과). 단 `boundary-contracts/HTTP.md` 본문과의 줄 단위 대조는 하지 않았다(읽기 범위 밖으로 둠). |
| D2 상태 기계 | OK | version은 1부터 연속(건너뛰면 FAILED_PRECONDITION), 같은 version 다른 내용 CONFLICT(boundary.md I7 상세, `failurestore.py:302-324`). 잡은 검토된 사례를 덮어쓰지 않음(`job.py:136-141`). 검토는 `CONFIRMED→PENDING` 되돌림도 허용(`review.py:307`, 설계상 허용으로 보임, 확인한 의도는 아님). |
| D3 멱등·중복 | 문제 L | 수집은 (session_id, turn_id)로 중복 제거해 DUPLICATE 반환(OK). 같은 키에 **다른 내용**이 오면 먼저 받은 것을 유지하고 알려 주지 않음(boundary.md D3·A6 행, `logstore.py` `send`가 `envelope_hash`를 저장만 하고 비교 안 함). 검토 재전송 멱등은 OK(`review.py:343-349`). 제안: 해시 불일치를 INTEGRITY_ERROR/로그로 표면화. 계약(CONVENTIONS) 영향이 있어 헤드 확인 필요. |
| D4 시간 | OK | 모든 시각 UTC, 서버 수신 시각(`logstore.py` `received_at = self._clock()`)을 사례 `created_at`·롤백 창에 사용, 클라이언트 `sent_at`은 쓰지 않아 시계 어긋남 영향 없음. 시험은 주입 시계(`conftest.py`). |
| D5 인코딩·크기 | 문제 L | 8 MiB 상한 OK(`api.py:45,230`), 한글은 `ensure_ascii=False`로 저장, null 문자는 JSON 이스케이프로 저장되어 PG TEXT 문제 없음(코드 읽음). 문제: 중첩 JSON `RecursionError` 미처리(B4), NFC 없음(C10). |
| D6 값 지어내기 | OK | 이 영역은 값을 생성하지 않는다. 검토자 정답은 계약 스키마로 검증(`review.py:353-368`), 깨진 상류 응답은 지어내지 않고 실패 처리(`job.py:68-69,186`, `rollback.py:469-470`). |
| D7 문서-코드 일치 | 문제 L | 대체로 일치(auto_submit 필수 `config.py:150`, DB 상한 `pgbase.py:20-23`와 boundary.md 표 일치). 불일치: README가 STATUS의 "133 통과"와 195건 수집을 언급하나 현재 405건(PG 없이 295 통과 110 건너뜀: 이번 실행)이고 STATUS.md는 갱신 전 수치(README 4절 스스로 어긋남을 적음). runbook.md:122 "개인정보 접근으로 기록한다"는 기록 수단이 없음. 제안: STATUS 갱신. 자율 수정 가능. |

### E. 운영성

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| E1 구조화 로그 | 문제 L | JSON 모양이지만 메시지 이스케이프가 없어 깨질 수 있고(B5), 요청 ID·상관 ID·사용자 정보 없음(`api.py:75-76,248`). PHI/비밀은 로그에 안 남도록 되어 있음(요청 경로와 코드만, `api.py:87-88`; 단 `log.exception`의 스택은 확인하지 못함). 제안: 요청 ID 추가. |
| E2 지표·경보 | 문제 M | 지표 엔드포인트·카운터 없음(대시보드 미구현: README). 인증 실패는 로그 경고뿐이고 `/readyz`에 건수 없음(boundary.md 장애 표, FAULT_POLICY 원칙 9 요구와 차이), 잡 오류는 종료 코드·표준 출력 JSON뿐. 경보 기준 문서 없음. 제안: 최소 카운터(인증 실패, 수집 건수, 미처리 원본 수)와 `/readyz` 또는 상태 API 노출. 자율 수정 가능, 경보 기준은 deploy. |
| E3 설정 | OK | 필수 설정 없으면 시작 거부: 비식별 정책 키(`deid.py:49-51`), 분류 기본값(`detect.py:191-193`), `REASK_STREAK` 임계값(`detect.py:101-103`), 롤백 항목 전부(`config.py:149-152`), 잘못된 DB 상한(`pgbase.py:34-36`), 인라인 비밀(`config.py:114`). 약점: `auto_submit`을 문자열 `"false"`로 쓰면 참으로 평가됨(S5), 알 수 없는 최상위 키는 무시. |
| E4 런북 | OK | `docs/runbook.md:100-123` 증상별 표(비식별 실패, skipped_diff, submit_error), 장애별 절차는 `docs/boundary.md` 장애 표. 얕음: PG 장애·토큰 회전·salt 분실 절차는 부족. |
| E5 감시·알림 | 확인 못 함 | 감시 대상·알림 경로는 deploy 소관, 이 영역에는 없음. |
| E6 용량 근거 | 문제 L | 측정된 용량 근거 없음. DB 기본값 근거도 "측정한 값이 아니라 추정"(boundary.md DB 대기 상한 절). |
| E7 시작 순서 | OK | DB 접속 실패 시 종료 코드 2로 끝나 재시작 정책에 맡김(`api.py:259-268`), 스키마 생성은 advisory lock으로 서버·잡 동시 시작에도 안전(`pgbase.py:83-94`). |
| E8 시간 불변식 | OK | 수집 최악 약 7초(문장 3+1, 재접속 3), `/readyz` 2초, 잡 3.3초가 boundary.md:64-70에 있고 코드 기본값과 같다(`pgbase.py:20-23`). 키오스크/gateway 체인과의 정렬은 FAULT_POLICY 쪽(수집은 outbox 경유라 턴 비차단). |

### F. 배포·이미지

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| F1 비root·권한 | OK | `USER app`(uid 10001, `Dockerfile:23-24`), 쓰기 경로는 `/data`뿐으로 읽기 전용 루트 가능성 높음(실제 시험은 안 함), capabilities·privileged·docker.sock 설정 없음(Dockerfile 기준). 서버는 기본 `0.0.0.0` 바인딩(`api.py:61`)이라 호스트 포트 노출 최소화는 deploy 소관(확인 못 함). 스모크는 `127.0.0.1::8080`(`smoke.sh:204`). |
| F2 이미지 핀 | 문제 M | 베이스 이미지가 태그만(`python:3.12-slim`, `Dockerfile:2,10`, digest 없음), 잠금에 해시 없음, boundary-contracts는 변경 가능한 git 태그를 `git archive`한 wheel, SBOM·취약점 스캔 없음. CI 게시·digest 제출(D24)은 미구현(README 4절). 제안: digest 고정, `--require-hashes`, 스캔. 자율 수정 일부(CI는 헤드). |
| F3 compose | 확인 못 함 | compose는 deploy 소유라 읽지 않았다. |
| F4 릴리스 되돌리기·순서 | 확인 못 함 | deploy 소관. 이 영역 측: 스키마 변경 절차 없음(C9)이라 이전 이미지로 되돌려도 DB 호환 문제는 현재 없음(코드 읽음). 문진 스키마 정수 버전 결합은 README G11. |
| F5 비밀 파일 권한 | 확인 못 함 | 비밀 파일 생성·권한은 deploy 소관, 읽지 않음. 이 영역 쪽에는 파일 권한 검사가 없다. |
| F6 레지스트리·CI | 확인 못 함 | CI 없음(README 4절), 레지스트리는 deploy. 빌드는 이웃 폴더의 `boundary-contracts`를 `git archive`로 가져오는 로컬 절차(`scripts/build_wheels.sh`). |

### G. 성능·용량

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| G1 처리량·지연 문서화 | 문제 L | 처리량·지연 측정 없음. DB 정지 시 한도만 측정(boundary.md). 연결 1개 직렬화(A7)로 한계가 낮을 수 있음. |
| G2 쿼리·인덱스 | 문제 L | 인덱스 있음(`raw_status`, `raw_release`, `cases_filter`, `cases_release`). `_failure_counts`가 릴리스의 전체 사례를 페이지로 훑고 `since`는 파이썬에서 거름(`rollback.py:409-419`), 풀 없음. 사례 수가 늘면 비례해 느려짐. |
| G3 큰 입력 | 문제 M | 잡이 `limit` 없으면 미처리 원본 **전부**를 한 번에 메모리에 적재(`job.py:90`, `logstore.py` `unprocessed(limit=None)` → `fetchall`). 잡 중단이 길어지면 원본 최대 8 MiB × 건수가 메모리에 올라간다. 제안: 배치 크기 기본값. 자율 수정 가능. |

### H. 시험 품질

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| H1 핵심 경로 | 문제 L | 이번 실행: **295 통과, 110 건너뜀**(PG 없음, 64초). 실제 HTTP 서버와 실제 `boundary_contracts.clients`를 쓴 가짜 상류로 롤백·읽기 장애 시험(`tests/test_upstream_faults.py`, `test_http_clients.py`), 비식별은 실제 스키마 걷기 시험. 실제 release-gate·survey-service와는 연결 안 함(E2E는 deploy). |
| H2 간헐 실패 | OK | 서버는 포트 0(임시 포트)(`tests/test_api_read.py:23` 등), 시계는 주입, 실제 sleep은 상류 무응답 모사(`test_upstream_faults.py:58`). 이번 실행 한 번 통과(반복 실행은 안 함). |
| H3 건너뛰는 시험 | 문제 M | 110건이 `TEST_DATABASE_URL` 없으면 건너뜀(`tests/conftest.py:100`, `test_postgres_timeout.py:33-37`). 건너뛰는 사유는 출력되고 대체는 SQLite 적합성 시험이지만, **운영 백엔드가 PostgreSQL**이라 기본 실행으로는 운영 경로가 시험되지 않는다. README의 PG 통과(405)는 한 환경에서 한 번의 기록. 제안: CI에서 PG를 필수로. |
| H4 부정 시험 | OK | 토큰 없음/다른 종류 토큰 403, 잘못된 본문 400, 비밀 인라인 거부, 원본 접근 차단 시험 존재(`tests/test_api.py`, `test_api_read.py`, `test_api_review.py`, `test_secrets.py`, `test_raw_access.py`; `pytest.raises`/403 단언 수는 파일별 grep으로 확인). 위 B4의 두 입력(중첩 JSON, 비ASCII 헤더)은 시험에 없다. |
| H5 환경 의존 | 문제 L | 이웃 폴더 `../survey-service/schema`가 없으면 스키마 동기 시험 건너뜀(`tests/test_schema_sync.py:12`), docker/PG 의존 시험, 시험은 이 PC 한 환경만(두 번째 환경 검증 없음: README 4절). `tests/tests_plugin.py`는 이름이 pytest 규칙(`test_*.py`)에 안 맞아 수집되지 않는 것으로 보이고(수집 여부 확인 못 함), 오래된 `test_pgdefaults_tmp` .pyc가 남아 있다. |

### I. 도메인·안전

| 항목 | 판정 | 근거 / 제안 |
| --- | --- | --- |
| I1 환자 안전 결정 | OK | 이 영역에 환자 호출·위험 신호·재질문 상한을 정하는 코드는 없다. 사용자 결정 값(롤백 기준, 비식별 기준, 분류체계, REASK 임계값)은 코드 기본값 없이 설정 필수 또는 자리표시자로 표시(`config.py:150`, `detect.py:101`, `config/job.example.yaml:81-82`, README 5절 G14). 유일한 박힌 값 `DEFAULT_EMPTY_VALUES_OK_ACTIONS=["REDIRECT"]`(`detect.py:70`)는 survey-service 설계에서 도출한 값이고 G14로 열린 항목으로 표시. |
| I2 환자 문구 출처 | 해당 없음 | 환자에게 가는 문구를 만들지 않는다. |
| I3 실패 시 환자 화면 | 해당 없음 | 환자 경로 밖. 수집 장애는 턴을 멈추지 않는 설계(survey outbox)이나 그 쪽 동작은 이 감사에서 확인 못 함(FAULT_MATRIX A6). |

---

## 영역 특유 점검 (S1~S7)

### S1. 비식별이 실제로 지우는 것과 지우지 않는 것
정책은 설정이 정하며(`DeidPolicy.from_config`, `deid.py:47-69`) 아래는 `config/job.example.yaml`의 정책 + `ops_feedback.deid`를 실제로 돌린 결과다. 합성 데이터(홍길동 등)로 `Deidentifier.deidentify`를 실행했다(scratchpad 스크립트, 저장 없음). 운영 정책 파일(deploy)은 읽지 못했다.

| 필드 | 처리 | 근거 |
| --- | --- | --- |
| 발화 원문 `frontend_message.utterance`, `extract_input.user_utterance`, `log_entry.input.utterance` | 지워짐(`[MASKED]`) | 실측; 미지정 문자열 마스킹 `deid.py:226-228` |
| 환자 답변 값 `Value` 계열, `extract_output.values[].value` | 지워짐 | `mask_defs:[Value]`, `mask_value_keys:[value]`, 실측 |
| 추출 `reason`, `note`, 문항 문장 `current_question`, 응답 `response_output`, `response_text` | 지워짐 | 실측 |
| 위반 `message` | 지워짐 | 실측 |
| `log_entry.staff_id`(직원 계정 ID) | 지워짐(`[MASKED]`) | 실측: 키가 허용 목록에 없음. 정책에서 `staff_id`를 허용하면 노출됨 |
| `session_id`, `turn_id` | **지워지지 않고 의사 식별자로 치환**(`p-`+SHA-256 salt 해시 32자) | `pseudonymize_keys`, `deid.py:216-218`. 같은 세션의 턴이 서로 연결되고, salt를 가진 쪽이 추측 가능한 id를 대조할 수 있음. salt가 바뀌면 전부 바뀜 |
| `extract_input.state` 같은 구조 없는 자유 객체 | 지워짐(`{}`) | `deid.py:193-198`, 실측 `dropped_paths` |
| 스키마에 없는 키 | 제거 | `deid.py:200-203` |
| **`next_item`, `action`, `code`, `path`, `question_id`, `slot_id`, `repeat_key`** | **그대로 남음, 값 검증 없음** | `keep_string_keys`, 실측: `next_item="홍길동 환자"`가 결과에 남음. 위반 `path`도 `values[0].홍길동`이 남음(실측) |
| 열거값·상수 문자열(`kind`, `response_outcome`, `extract_status` 등), 정수·불리언(`turn_index`, `extract_attempts`, `question_bank_version`), `mask_number_keys` 밖의 숫자 | 그대로 남음 | `deid.py:164-165,175-182`, 예시 정책 `mask_number_keys: []` |
| `source_release_id`, `created_at`(= 서버 수신 시각, 초 단위) | 사례에 남음 | `job.py:114-116`; 시각+릴리스는 준식별자가 될 수 있음 |
| 검토자가 쓰는 `expected`, `reviewed_input`, `ext.ops-feedback.reviewed_by`(직원 ID) | **비식별 검사를 거치지 않음** | `review.py:331-336,340`; 이중 읽기 토큰으로 공개 |
| 잔존 패턴 검사 | 이메일, 전화, 주민번호 정규식만, 걸리면 실패로 닫음(`DEID_FAILED`) | `deid.py:271-276`, 예시 정책 |

### S2. 보존·삭제 기본값과 삭제 경로
C3 참조. 요약: 기본 무기한, 삭제 경로는 원본 시간 기준 하나뿐, 사례·trace·aux 삭제 없음, 세션 단위 삭제 없음.

### S3. 실패 사례·Trace에 남는 식별 정보
사례 레코드: `case_id`(salt 해시), `source_release_id`, `created_at`, 비식별 trace 참조, `ext.ops-feedback.{detections(규칙 ID와 열거 값), deid_stats(처리 경로 이름), reviewed_by(직원 ID)}`. 비식별 trace는 S1 표와 같다. `deid_stats`의 경로 이름은 스키마 경로라 개인정보 아님. 오류 보고(`job.py:99,143`)는 의사 식별자와 코드만. **판정: 위 S1의 "남음" 행과 검토자 입력이 주 위험.**

### S4. 검토자 행위 기록의 위조 가능성
C6 참조. 요약: `reviewed_by`는 호출자 제공 헤더이고 토큰은 역할 단위. 위조는 gateway가 헤더를 덮어쓰지 않거나 서비스에 직접 도달할 수 있으면 가능(확인 못 함). 레코드 자체는 API로 불변.

### S5. 롤백 자동 요청의 안전장치 (신규 M)
- `auto_submit`: 코드에 기본값 없음, `rollback` 항목이 있으면 반드시 적어야 시작(`config.py:150-152`), 예시는 `false`(주석 처리)(`config/job.example.yaml:96`). `false`이면 게이트를 부르지 않고 요청만 저장(`rollback.py:465`). 시험: `tests/test_rollback.py`(통과). 운영 잡 설정은 `rollback: null`이라는 deploy 기록이 있어 현재 자동 롤백 간선은 꺼져 있음(FAULT_MATRIX D3, 직접 확인은 못 함).
- 문제 1: `if self._p["auto_submit"]`(`rollback.py:465`)은 진릿값 검사라 YAML에서 문자열 `"false"`나 `"no"`를 쓰면 참 → 실수로 자동 전송. 제안: 불리언 형식 검사. 자율 수정 가능(L).
- 문제 2(M, 잠복): 실패율의 분자는 수집한 Trace에서 만든 사례, 분모는 수집 건수이고 `release_id`는 봉투의 클라이언트 값이다(`logstore.py` `send`는 활성 릴리스와 대조하지 않음). 수집 토큰 하나(survey-service 또는 탈취자)로 활성 릴리스 ID를 단 실패 Trace를 대량 주입하면 `max_failure_rate`를 넘겨 롤백 요청이 생성되고 `auto_submit`이 켜져 있으면 게이트로 전달된다. 게이트의 자체 승인 규칙은 확인 못 함. 제안: auto_submit 활성화 전에 `release_id`가 알려진 릴리스인지 확인, 표본 하한·전달 전 사람 승인 단계(사용자 결정).
- 참고: "되돌릴 릴리스"는 릴리스 목록에서 현재의 바로 다음 항목이라 직전 정상 릴리스를 뜻한다는 보장이 없다(`rollback.py:396-407`). `PENDING` 사례도 실패로 센다(예시 `counted_review_statuses`). 롤백 후 쿨다운은 `pointer_version` 변화에만 의존.

### S6. 검토 게시 권한 분리
OK. 수집/읽기/검토 토큰은 서로 달라야 시작(`api.py:68-69`), 검토 경로는 검토 토큰만(`api.py:176-180`), 읽기 토큰으로 검토 403(스모크·`tests/test_api_review.py`), `publish_case`는 HTTP로 열지 않고 잡만 호출(주석 `api.py:14`). 검토 API는 `failure_type`을 못 바꾸고 허용 키가 제한됨(`api.py:194`). 남는 위험은 토큰이 역할 단위라 검토자 개인 구분이 없는 점(S4)과, CONFIRMED + `expected` 입력이 모델 학습 정답으로 소비되므로 검토 토큰 유출이 학습 데이터 오염 경로가 된다는 점(코드가 아닌 운영 위험).

### S7. 라우트 전수 표 (`api.py` 기준, 이 서비스는 ThreadingHTTPServer 하나)

| 메서드 | 경로 | 필요한 인증 | 비고 |
| --- | --- | --- | --- |
| GET | `/healthz` | 없음 | `api.py:148` |
| GET | `/readyz` | 없음 | 호출마다 DB 새 연결(B10), 저장소 종류·지원 버전 노출 `api.py:150-172` |
| GET | `/v1/cases/{case_id}?version=` | 읽기 토큰(아무 역할) | I7 get_case, `api.py:102-110` |
| GET | `/v1/cases?review_status&failure_type&source_release_id&updated_since&latest_only&cursor&limit` | 읽기 토큰 | limit 1~500 `api.py:111-134` |
| GET | `/v1/deidentified-traces/{ref}` | 읽기 토큰 | `api.py:135-136` |
| GET | 그 밖의 `/v1/*` | 읽기 토큰 후 404 | |
| GET | 그 밖의 경로 | 없음 | 404 JSON |
| POST | `/v1/traces` | 수집 토큰 | 본문 ≤ 8 MiB `api.py:223-242` |
| POST | `/v1/cases/{case_id}/review` | 검토 토큰(역할 → `reviewed_by` 기본값), `X-Openit-User` 선택 | `api.py:175-215` |
| POST | 그 밖의 경로 | 없음 | 404 JSON |
| PUT/DELETE/PATCH/HEAD 등 | 모든 경로 | 없음 | 표준 라이브러리 501 HTML |

읽기 면(`failures`)이 꺼져 있으면(`OPS_READ_TOKENS` 또는 저장소 없음) 읽기 토큰이 비어 모든 `/v1` GET이 403(`api.py:262-265`).

---

## 이 점검이 읽지 못한/얕게 본 곳

- **deploy 소유물을 읽지 않았다**(운영 잡 설정 `ops-feedback-job.yaml`의 실제 `retention.raw_days`·`deid` 정책·`rollback` 값, compose의 포트·자원 한도·restart·네트워크, Caddyfile의 X-Openit-User 처리와 상류 상한, 비밀 파일 권한, 백업 스크립트의 범위). C3의 운영 값, C5, C6의 위조 가능성 최종 판정, C7, F3~F6, B8, E5는 그래서 "확인 못 함" 또는 영역 쪽 사실만.
- **PostgreSQL 시험 110건은 실행하지 못했다**(`TEST_DATABASE_URL` 없음, docker 사용 안 함). README의 PG 포함 405 통과는 읽은 기록이다. 스모크(`scripts/smoke.sh`)·이미지 빌드·실제 기동도 하지 않았다(Docker 사용 제약 판단).
- **취약점 조회 안 함**: `pip-audit` 미설치, 설치·외부 전송 금지. 의존성 CVE는 B9 "확인 못 함".
- **비식별 실측은 예시 정책과 합성 trace 두 건**으로만 했다. 운영 정책, v2 TurnTrace(README: 스키마 v1 스냅샷 기준 구현), `session_before.dialogue_log` 같은 중첩 구조 전체, 모델이 실제로 `next_item`에 무엇을 쓰는지는 보지 못했다.
- `failurestore.py` 중 `put_trace`·`list_cases`·`scan` 구현 상세, `tests/` 개별 시험 본문은 줄 단위로 읽지 않았다(시험 이름·건수·통과로만 판단). `boundary-contracts`의 `HTTP.md`·`CONVENTIONS.md`는 읽지 않았다(D1은 시험과 코드로만).
- 게이트의 `request_id` 멱등, survey-service outbox의 재전송 동작은 이웃 영역이라 확인하지 않았다.
- `build/src`(이웃 `boundary-contracts` 소스 복사본, `.gitignore`에 있음)와 `.venv`는 점검 대상에서 제외했다.
