# 전수 점검: question-authoring (읽기 전용 감사, 2026-10-28)

기준: `head/docs/AUDIT_CHECKLIST.md` A~I. 대상 커밋: question-authoring HEAD `7bbed7e`, 작업트리 깨끗. 코드·설정·문서는 수정하지 않았다.

## 요약

- 항목 분모: 63개(A9, B12, C10, D7, E8, F6, G3, H5, I3). 모두 판정했다.
- 판정별: OK 22 / 문제 31(H 2, M 8, L 21) / 해당 없음 1 / 확인 못 함 9. (22+31+1+9=63)
- 같은 원인을 묶은 고유 문제: H 1건, M 6건(아래), L 다수.
- 시험 실행(영역 .venv, 읽기 전용): `206 passed, 77 skipped`(49.5초). 건너뜀 77건은 모두 `TEST_DATABASE_URL 없음`(tests/conftest.py:28)이라 PostgreSQL 경로는 이 점검에서 시험하지 못했다.
- 의존성 핀: requirements.lock이 `==`로 고정, 설치본과 일치(jsonschema 4.26.0, psycopg 3.3.6, boundary-contracts 2.0.2, openit-survey-schema 1.0.0). pip-audit는 설치 금지라 취약점 조회는 못 했다.

### H 문제
- **P1 (H) 텍스트 양식 추출기 정규식·목록 탐색이 제곱 시간, 요청 하나로 서비스 전체가 멈춘다** (B4, G3). 근거와 수치는 아래 B4.

### M 문제
- P2 clinical_basis_approved를 bool()로 강제 변환해 문자열 "false"가 승인(True)으로 저장된다 (D1, B4, H4).
- P3 저자/검수자 권한 분리 없음: 자기 초안을 자기가 확인하면 곧 임상 승인, 저자끼리 서로의 초안·검수에 제한 없음 (B2).
- P4 보존·삭제 없음: 원본 자료(blobs)·초안이 무기한 쌓이고, 환자 정보 경고를 수락한 자료도 영구 저장 (A6, C3, C2).
- P5 환자 정보 경고 탐지의 누락이 크다 (C4).
- P6 설정 누락 시 조용히 SQLite(tmpfs)로 떨어지고, 토큰 0개로도 시작 (E3).
- P7 자원 한도 부재: 스레드 수 무제한, 본문을 인증 전에 읽음, compose에 메모리·CPU 한도 없음 (A9, F3).

## 노출 범위 (운영 구성)

- `deploy/compose.yaml:224-241`: question-authoring에 `ports` 없음. 네트워크 `authoring`, `release`, `db-qa`(후자 둘은 internal 성격: release internal:true, db-qa internal:true). 호스트 포트를 연 것은 gateway뿐(:182, 기본 127.0.0.1).
- `deploy/config/Caddyfile`에 authoring 경로 없음(grep 0건). 즉 저자 클라이언트(FAULT_MATRIX E2)는 현재 운영 구성에서 이 서비스에 닿을 길이 없다. boundary.md:63도 같은 입장(사용자 결정 보류).
- 같은 네트워크의 호출자: `authoring`=ops-feedback-ingest, `release`=release-gate 외 몇 개(compose.yaml:276,307,327,345). 토큰 없이는 /healthz·/readyz만 응답.
- compose.test.yaml:14-16만 `127.0.0.1::8080`(임의 포트)을 연다.
- 이 파일들은 영역 밖이라 노출 범위 확인 목적으로 비밀 아닌 부분만 읽었다.

## 라우트 전수 표

| 경로 | 메서드 | 필요한 것 | 근거 |
| --- | --- | --- | --- |
| /healthz | GET | 없음 | http_api.py:142 |
| /readyz | GET | 없음(응답: status, db 종류만) | http_api.py:144-149 |
| /v1/question-sets, /{id}/versions, /{id}/latest, /{id}/versions/{n}, .../reviews, .../change | GET | 읽기 토큰 또는 저작 토큰 | http_api.py:150-154, 182-218 |
| /v1/question-sets* | GET 외 | 위와 같은 인증 뒤 404 | http_api.py:152-153 |
| /v1/signals | GET | 저작 토큰(읽기 토큰은 403), 하위 I7 토큰은 서버가 보유 | http_api.py:230-248 |
| /v1/drafts | POST, GET | 저작 토큰 | :249-253 |
| /v1/materials | POST | 저작 토큰 | :254-257 |
| /v1/reviews | POST | 저작 토큰 | :258-262 |
| /v1/drafts/{id} | GET | 저작 토큰(역할 재확인 없음, 토큰 표에 있으면 통과) | :263-267 |
| /v1/drafts/{id}/preview | GET | 저작 토큰 | :268 |
| /v1/drafts/{id}/edits, /acknowledge, /confirm, /discard | POST | 저작 토큰 | :271-278 |
| 그 밖 | 모두 | 토큰 없으면 403, 있으면 404 | :155, 279 |

미인증은 401이 아니라 403(계약 HTTP.md:11이 403으로 정함, 문제 아님).

## 항목별 표

### A. 신뢰성
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| A1 timeout | OK | DB 접속 3s·문장 3s(+1s 소켓 종료)·readyz 2s·큰 쓰기 30s(__main__.py:12-18, postgres.py:105-126,198), I7 5s+총 마감 20s(signals.py:57-62), 서버 소켓 30s(http_api.py:284). 상한 0 초과 600 이하 검증(__main__.py:39). |
| A2 재시도 | OK | 재시도는 연결 끊김 때 한 번, 모든 쓰기가 멱등(postgres.py:180-216). 백오프·지터는 없고 즉시 1회(상한 있음)라 문제 삼지 않음. |
| A3 부분 쓰기 | OK | 버전+검수+변경 분류가 한 트랜잭션(postgres.py:255-277, sqlite.py:116-138). confirm은 `confirming`에 번호·시각을 예약해 중간 중단 후 재시도해도 같은 레코드(service.py:338-342). 근거는 코드 읽기와 sqlite 시험. PG 시험은 이 점검에서 못 돌림. |
| A4 우아한 종료 | 문제 L | SIGTERM 처리기 없음(grep으로 `signal` 0건), `serve_forever()`만(__main__.py:82), compose에 `init: true` 없음(grep 0건). PID 1인 Python은 SIGTERM을 기본 무시하므로 `docker stop`이 10초 뒤 SIGKILL로 끝날 가능성이 높다(실행해 확인하지는 않음). 쓰기는 트랜잭션·멱등이라 손상은 없고 진행 중 요청만 끊긴다. 제안: SIGTERM에서 `shutdown()`을 별도 스레드로 부르는 처리기. 자율 수정 가능(영역 내). |
| A5 자동 복구 | OK | 연결 끊김 시 재접속(postgres.py:207-210), 스키마 생성 멱등·advisory lock(:140-153), compose `restart: unless-stopped`(compose.yaml:7). 시험은 test_postgres_specific(이 점검에서 건너뜀). |
| A6 무한 증가 | 문제 M (P4) | `drafts`, `blobs`를 지우는 코드·설정·문서가 없다(store/base.py의 추상에 delete 없음). 업로드마다 초안이 새로 생기고(service.py:259, boundary.md:78이 인정) 원본 최대 8MiB가 blobs에 영구 보존(postgres.py:312-315). FALLBACK 초안도 쌓인다. 제안: 폐기·확정 초안과 연결 없는 blob의 보존 기간·정리 잡(run-once). 보존 기간은 사용자 결정, 구현은 자율. |
| A7 동시성 | 문제 L | (1) 초안 읽기-수정-쓰기가 잠금·버전 검사 없이 전체 덮어쓰기(service.py:202-215 → save_draft). 두 저자가 동시에 편집하면 한쪽이 사라진다. (2) confirm이 `confirming`에 버전 번호를 예약한 뒤 다른 초안이 먼저 커밋되면, 재시도는 stale 검사를 건너뛰고(service.py:336) 같은 번호로 계속 CONFLICT. 초안을 폐기하고 다시 시작해야 복구된다. 새 버전 번호 충돌 자체는 advisory lock으로 안전(postgres.py:229). 제안: 초안에 revision을 두고 비교 저장, `confirming` 충돌 시 예약 해제. 자율 수정 가능. |
| A8 healthz/readyz | OK | healthz는 정적, readyz는 주 연결·락을 쓰지 않는 별도 연결로 schema_version 확인(postgres.py:329-356). |
| A9 자원 한도 | 문제 M (P7) | `ThreadingHTTPServer`는 스레드 수 상한이 없다(http_api.py:324). 본문을 인증 전에 최대 8MiB 읽는다(http_api.py:286-310, 인증은 api.handle 안). 동시 연결 N개면 8MiB×N 메모리. DB는 연결 하나와 RLock 하나로 읽기·쓰기를 모두 직렬화(postgres.py:85,186). 파일 핸들·디스크 한도 없음. 제안: 인증 헤더를 본문보다 먼저 검사(Content-Length만 보고 거부), 동시 요청 상한(세마포어). 자율 수정 가능. compose 한도는 F3. |

### B. 보안
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| B1 인증 | OK | /healthz·/readyz 외 모두 Bearer 필요, 토큰 표가 비면 전부 403(기본 거부, runbook.md:32,35). 위 라우트 표. 시험: tests/test_http_read.py, test_secrets.py 등에 403 단언. |
| B2 인가 | 문제 M (P3, 사용자 결정 필요) | (a) 토큰 표의 어떤 역할 이름이든 저자로 취급(`author_roles={a.role for ...}`, __main__.py:67). 저자와 검수자의 구분이 코드에 없다(design.md:69가 "미구현"이라 인정). (b) `confirm`이 확인자에게 `decision=APPROVED, clinical_basis_approved=True`를 자동 부여(service.py:366). 저자 한 사람이 올리고 확인하면 검수 완료(`reviewed_only`)가 된다. (c) 초안의 소유 검사가 없다: 다른 저자의 초안을 편집·폐기·확정 가능(service.py:202-238, `created_by`는 기록만). (d) `add_review`로 누구든 어느 버전이든 승인·철회(service.py:382-404). 읽기 토큰은 GET만(OK, 시험 있음). 이 구조는 D30의 "저자는 신뢰한다" 결정과 맞지만 "승인한 사람이 만든 사람과 달라야 하는가"는 결정된 적이 없다. 제안: 사용자가 2인 승인 여부를 결정하면 그에 맞춰 역할 열거와 규칙을 둔다. |
| B3 비밀 | OK | 모든 비밀을 `read_secret`(NAME_FILE 우선)로 읽음(__main__.py:45,58,64,71). DSN은 로그·오류에 쓰지 않는다(postgres.py:60-62,106-111). /readyz는 db 종류만. 로그는 내부 오류의 예외 종류만(http_api.py:160). 토큰은 시작 때 한 번 읽어 회전하려면 재시작 필요(경미). |
| B4 입력 검증 | **문제 H (P1)** + L | **ReDoS/제곱 시간(실측)**: `_KV = ^([^:：]+?)\s*[:：]\s*(.*)$`(textform.py:17)가 콜론 없는 긴 공백 줄에서 제곱 시간. 문항 줄 다음에 `x`+공백 N개+`y` 한 줄을 넣어 측정: 10,000자 0.24초, 40,000자 3.7초, 160,000자 62.9초. 8MiB(허용 상한)이면 수십 시간. `re`는 GIL을 잡으므로 이 요청 동안 프로세스 전체(healthz 포함)가 멈추고, compose는 unhealthy를 재시작하지 않는다(restart: unless-stopped). 같은 계열: `_missing`이 `any(f.path==path for f in self.flags)`로 플래그 전체를 매번 훑음(textform.py:73) → 슬롯 줄 16,000개 26초, 짧은 문항 줄 10,000개 44초(100KB). 8MiB 규모 정상 자료도 사실상 멈춘다. 인증된 저자만 보낼 수 있고 현재 외부에 노출되지 않는다는 점이 완화 요인. boundary.md:80은 "그 밖의 추출기·검증의 시간은 8MiB 규모로 측정하지 않았다"고 스스로 한계를 적었다. 제안: `_KV`를 `^([^:：]*?)` 대신 `str.partition`/첫 콜론 위치로 대체, 줄 길이 상한(예 4KB)과 줄 수·문항 수 상한, `_missing`을 집합으로, 추출 총 시간 예산. 자율 수정 가능. **환자 정보 정규식 자체는 폭주하지 않음**(8MB 입력 1.1~1.6초, 이메일 패턴은 길이를 묶음, service.py:28-30). 그 밖: `edits`가 목록이 아니면 500(`AttributeError/TypeError`, 실측; http_api.py:272, service.py:207) L, `discard`의 reason 형식 무검사 L, 파일 이름 길이·NUL 무검사(service.py:241, 파일명은 경로로 쓰지 않고 임시 파일은 고정명 `material`이라 경로 조작은 불가, service.py:254) L. 압축 풀기·아카이브 처리 없음(추출기는 .txt/.md만)이라 압축 폭탄은 해당 없음. 인코딩: 추출기는 UTF-8(BOM 허용)이 아니면 FALLBACK(textform.py:43-45). |
| B5 인젝션 | OK(프롬프트 부분 해당 없음) | SQL은 모두 파라미터화. f-string은 `int()`로 만든 timeout, 정규식으로 검증한 schema 이름뿐(postgres.py:83,123,144,231). 명령·템플릿 없음. 모델 호출이 없어 프롬프트 인젝션은 해당 없음. 로그 인젝션: 접속 로그가 요청 줄을 출력하나 원시 CR/LF는 요청 줄에 들어올 수 없다(http_api.py:321-322). |
| B6 SSRF | OK | 호출하는 외부 URL은 운영자가 정한 `QA_FAILURES_URL` 하나(__main__.py:69-72). 요청자가 URL을 줄 수 없다. |
| B7 웹 | 해당 없음 | JSON API만. HTML·쿠키·CORS·콘솔 UI가 이 영역에 없다(콘솔은 미구현). |
| B8 전송 | 문제 L (사용자 결정) | 서비스 내부는 평문 HTTP, Bearer 토큰이 authoring/release 네트워크에서 평문으로 흐른다. 호스트로는 열리지 않음(노출 범위 절). 콘솔을 열 때 gateway TLS 종료와 함께 다시 정해야 한다. |
| B9 의존성 | 문제 L | PyPI 의존은 `==` 고정(requirements.lock)이나 해시 고정(`--require-hashes`) 없음. 기반 이미지 `python:3.12-slim`이 태그만(Dockerfile:1, digest 아님). boundary-contracts·survey-schema는 태그의 소스로 wheel을 만들며 커밋은 build/*.rev에 기록되나 이미지 라벨은 태그만 보유. CVE는 pip-audit를 못 써서 확인 못 함. 제안: 기반 이미지 digest 고정, 잠금에 해시 추가. 자율 수정 가능. |
| B10 속도 제한 | 문제 L | 인증 실패 제한·요청 속도 제한 없음. 토큰 비교는 dict 조회(상수 시간 비교 아님). 외부에 노출되지 않아 낮음. |
| B11 오류 노출 | OK | 예상 밖 오류는 고정 문구 500(http_api.py:159-161, 실측 확인). DB 오류는 종류+SQLSTATE만. 일부 NOT_FOUND가 사용자 입력을 되돌려 줄 뿐. |
| B12 토큰 수명·권한 | 문제 L | 정적 토큰, 만료 없음, 저자 토큰은 모든 쓰기 권한(B2). 읽기 토큰의 역할 이름은 쓰이지 않는다(토큰→역할 표만 있고 구분 없음). DB 계정은 시작 때 `DROP TRIGGER/CREATE TRIGGER`를 실행하므로(postgres.py:148-150) 표 소유자여야 하고, 그러면 서비스 계정이 불변 트리거를 끌 수 있다. deploy의 역할 스크립트(10-roles.sh)는 영역 밖이라 읽지 않음. |

### C. 데이터·개인정보
C1 저장·전송·기록 목록:
- 저장(DB): 문항 세트 버전 본문(QuestionBank), 검수 기록(reviewer_id=토큰 표의 actor id, 시각), 변경 분류, 초안(본문+`flags[].raw`=자료의 원문 줄), `blobs`=업로드 원문 전체와 파일 이름, 폐기 사유.
- 전송: I1 읽기(문항 본문, 검수 기록), I7 읽기(실패 사례 건수·유형·ID만. signals.py:5-7이 발화 문장 제외를 명시, 코드도 trace에서 question_id만 읽음).
- 로그(stdout): 접속 로그에 클라이언트 주소, 메서드, 경로+쿼리(question_set_id, 파일 이름 포함)와 상태 코드, 오류 종류. 환자 발화는 이 서비스에 들어오지 않는다.
- 비밀: 토큰 3종·DSN은 파일.

| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| C1 목록 | OK | 위 목록(코드 읽기로 작성). design.md:168이 "자료에 환자 정보는 없다고 가정"이라 명시. |
| C2 최소 수집 | 문제 L (P4, 사용자 결정) | 파싱 결과만 필요한데 원문 전체를 영구 저장(service.py:257). 출처 해시를 위해서라면 해시만 남기는 선택지가 있다. |
| C3 보존·삭제 | 문제 M (P4, 사용자 결정) | 보존 기간·삭제 경로가 어디에도 없다(기본 무기한). 환자 정보 경고를 `accept_phi_warning=true`로 넘긴 자료는 blobs와 초안 `raw`에 영구 저장되고 지울 방법이 API·코드에 없다. 제안: 보존 기간 정책(사용자 결정) + 만료·삭제 run-once 잡, 경고를 수락한 자료는 원문을 저장하지 않는 옵션. |
| C4 비식별 | 문제 M (P5) | 탐지 정규식(service.py:28-30)의 누락을 실측했다. 누락: 한글에 붙은 주민번호 `홍길동900101-1234567`(\b 때문에 놓침), 하이픈 없는 13자리, 공백으로 나눈 전화 `010 1234 5678`, `+82-10-…`, 유선 `02-123-4567`, 전각 하이픈, UTF-16 등 UTF-8이 아닌 파일(`errors="ignore"`로 디코드, service.py:291). 이름·주소·병록번호는 패턴 자체가 없다. 잡힌 것: `901010-1234567`(앞뒤 비한글), `010-1234-5678`, 이메일. 경고 전용이라는 설계(design.md:110)는 맞지만, 누락 시 경고 없이 원문이 영구 저장된다(C3). 제안: 한글 인접을 허용하도록 `(?<!\d)…(?!\d)`로 바꾸고 숫자 사이 공백·`+82` 허용, 디코딩 실패 시 경고. 거짓 경고(6-7자리 숫자 열)는 저자가 수락하는 흐름이라 허용 가능. 자율 수정 가능. 접속 로그의 파일 이름·문항 세트 ID가 식별정보가 될 수 있음(L). |
| C5 암호화 | 확인 못 함 | 저장 암호화·볼륨 권한은 deploy(pg-data)의 몫이고 읽지 않았다. 전송은 B8. |
| C6 접근 기록 | 문제 L | 검수 기록의 행위자는 서버 쪽 토큰 표에서 오고 불변이라 위조 불가(OK). 그러나 초안 편집·폐기·확정 전 상태의 행위자는 `created_by`뿐이고 폐기에는 행위자가 없다(service.py:232-238). 읽기(누가 열람했나)는 기록하지 않는다. |
| C7 백업·복원 | 확인 못 함 | pg_dump 백업은 deploy 소관(compose.yaml:44 주석). 이 영역에서 확인한 것 없음. |
| C8 DB 계정 | 확인 못 함 | deploy 역할 스크립트는 영역 밖. B12의 소유자 필요성만 코드로 확인. |
| C9 마이그레이션 | 문제 L | `schema_version` 표지만 있고(postgres.py:46,94-97) 마이그레이션·되돌리기 수단이 없다. 형식이 다르면 시작 거부(안전). 스키마 변경이 생길 때 필요. |
| C10 정합성 | 문제 L | PK·UNIQUE(review_id)·불변 트리거 있음. `reviews/changes`에서 `versions`로의 FK·CHECK 없음(같은 트랜잭션과 코드로만 보장). 트리거는 행 단위라 TRUNCATE는 못 막음. 시각은 UTC 초 단위. 한글 유니코드 정규화(NFC) 없음(grep 0건)이라 NFD로 입력된 같은 문장은 다른 내용으로 보고 새 버전이 된다. |

### D. 정확성·계약
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| D1 계약 일치 | 문제 M (P2) | 읽기 면은 HTTP.md 표와 일치하고 적합성 시험이 통과(tests/test_http_client_conformance.py, test_reader_conformance.py 포함 206건). 그러나 `add_review`가 `clinical_basis_approved`를 `bool(...)`로 바꿔(service.py:389) 스키마 검사를 통과시킨다. 실측: `"false"`→True, `"no"`→True 저장, `0`/`false`는 False. 계약은 불리언이므로 400이어야 한다. 임상 승인 필드라 `reviewed_only` 결과를 바꿀 수 있다. 제안: `isinstance(x, bool)` 검사 후 거부. 자율 수정 가능. 같은 종류로 잘못된 형식 입력이 500(UNAVAILABLE, retryable)으로 나가 클라이언트가 재시도한다(`edits` 형식 오류, 실측). |
| D2 상태 기계 | OK | OPEN만 편집·폐기, CONFIRMED 재확인은 같은 해시면 멱등·다르면 CONFLICT, DISCARDED는 확정 불가(service.py:143-147,319-329). 시험: test_service_acceptance.py. 복구 불가 상태 1건은 A7. |
| D3 멱등 | OK | commit_version·add_review는 멱등(시험 있음). 자료 업로드·초안 생성이 멱등이 아니라는 한계는 boundary.md:78이 문서화. |
| D4 시간 | 문제 L | 시각은 서버 UTC 초 단위 문자열. 승인 철회 순서를 `(reviewed_at, 삽입 순번)`으로 정함(base.py:127). 시계가 뒤로 가면 늦게 한 철회가 먼저 한 승인보다 이르게 보일 수 있다(드묾). 만료 개념은 없음. |
| D5 인코딩·크기 | 문제 L | 본문 8MiB 상한과 413, 잘못된 Content-Length 400, 중단된 업로드 무저장(http_api.py:288-309). 잘못된 UTF-8 JSON은 400. 파일 이름의 NUL이 PostgreSQL TEXT에서 거부되면 입력 오류가 503으로 나갈 수 있다(PG 시험 못 해 추정, 확인 못 함). 긴 한글·이모지는 JSON/UTF-8 경로로 통과. 청크 전송은 Content-Length 없음으로 0바이트 취급(빈 자료 400). |
| D6 값 지어내기 | OK | 추출기는 확신 없는 값을 비우고 플래그, 열린 플래그가 있으면 확정 불가(service.py:330-333, textform.py 전반, design.md 원칙 4·5). 위험 기준 형식이 정확히 맞아야 값으로 읽음(textform.py:327-354). 모델 출력이 없는 서비스. |
| D7 문서-코드 | OK | boundary.md/design.md의 타임아웃, 라우트, 한계(멱등·미측정)가 코드와 일치함을 항목별로 대조했다(README의 시험 개수 등 모든 문장을 대조한 것은 아님). |

### E. 운영성
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| E1 로그 | 문제 L | `print` 기반 평문, 수준·상관 ID 없음(http_api.py:160,321). 접속 로그에 쿼리(파일 이름 포함). 비밀 없음. |
| E2 지표 | 문제 L | 메트릭 노출 없음, 경보 기준 문서 없음. |
| E3 설정 | 문제 M (P6) | `QA_DATABASE_URL`(_FILE)이 없으면 오류 없이 SQLite `/data`로 간다(__main__.py:44-52). compose의 `/data`는 tmpfs(compose.yaml:235)라 비밀 마운트 실수 시 서비스가 빈 문항 은행으로 정상 기동(/readyz 200, db:"sqlite")하고 재시작마다 사라진다. 토큰이 0개여도 시작(전부 403). `_FILE`이 있는데 읽지 못하면 SecretError로 거부(양호). 제안: 운영 표지(예 `QA_REQUIRE_POSTGRES=1`)로 DB URL·저자 토큰 필수화. 자율 수정 가능. |
| E4 런북 | OK | docs/runbook.md(64줄) 존재, 환경 변수·장애 표가 있다. 절차의 정확성은 얕게만 봤다. |
| E5 감시·알림 | 확인 못 함 | deploy/운영 소관, 이 영역에서 찾은 것 없음. |
| E6 용량 | 문제 L | DB 큰 쓰기 0.09초 측정(boundary.md:80)만 있고 추출기·미리보기·분류는 8MiB 규모 미측정. 이 점검의 실측이 제곱 시간을 보였다(P1). |
| E7 시작 순서 | OK | compose `depends_on: postgres service_healthy`(:237-238). DB가 안 열리면 시작 때 예외로 종료 후 재시작. |
| E8 시간 불변식 | OK | boundary.md:40,46-59의 체인(3s+1s, 2s, 30s)이 코드의 기본값과 같다(__main__.py:12-18, postgres.py:48-52). 호출자 쪽 대기와의 맞물림은 문서도 미시험이라 밝힘. |

### F. 배포·이미지
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| F1 이미지 권한 | OK | uid 10001 비root(Dockerfile:19-20), compose `cap_drop ALL`, `read_only`, `no-new-privileges`(compose.yaml:6-12), 이 서비스에 호스트 포트 없음, Caddyfile에 경로 없음. docker.sock·privileged 없음. |
| F2 이미지 핀·스캔 | 문제 L | 기반 이미지 digest 없음, SBOM·취약점 스캔 흔적 없음. 결과 이미지는 deploy가 digest로 고정(compose.yaml:226). wheel은 sibling 리포지토리 태그에서 만든다(scripts/build_wheels.sh). |
| F3 compose | 문제 M (P7) | restart·네트워크 분리·tmpfs는 있으나(compose.yaml:224-241) 이 서비스에도 앵커에도 메모리·CPU·pids 한도가 없다(앵커 6-12줄과 서비스 블록 확인). A9와 함께 8MiB×동시 연결 메모리가 무제한. deploy 소유라 헤드에 제안. |
| F4 롤백·업그레이드 | 확인 못 함 | deploy 소관. 이 영역은 schema_version 불일치 시 시작 거부(C9). |
| F5 비밀 파일 | 확인 못 함 | 파일 권한은 비밀 영역이라 읽지 않았다. compose에서 이 서비스는 비밀을 환경 변수로 받지 않고 `_FILE`만 받는다(OK 부분). |
| F6 레지스트리·CI | 확인 못 함 | 영역 밖. |

### G. 성능·용량
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| G1 측정·한계 | 문제 L | 처리량·지연 문서 없음. 부분 측정(DB 큰 쓰기, 이메일 정규식)만. P1 수치는 이 감사가 처음 측정. |
| G2 쿼리·풀 | 문제 L | 연결 풀 없음, 연결 하나 + 전역 RLock으로 I1 읽기(게이트 60초 주기)가 30초짜리 큰 쓰기 뒤에 줄을 선다(postgres.py:186). `latest(reviewed_only=True)`가 버전마다 검수 조회(N+1, base.py:131-133). `list_ids`가 전체 ID를 읽고 파이썬에서 거름(base.py:144). `_base`가 `list_versions(limit=1000)`이라 1000번째 넘는 버전은 `base_version` 지정 불가(service.py:170, MAX_LIMIT=1000). |
| G3 큰 입력 | 문제 H (P1) | B4와 같은 원인. 100KB 자료가 수십 초 CPU. 미리보기·분류·해시도 큰 bank로는 측정하지 않았다(확인 못 함). |

### H. 시험 품질
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| H1 핵심 경로 | 확인 못 함 | memory·SQLite는 실제 구성요소로 확인·승인 경로 시험(206 통과). PostgreSQL 시험 77건은 이 점검에서 건너뜀(TEST_DATABASE_URL 없음). 운영 DB 경로의 통과는 확인하지 못했다. |
| H2 간헐 실패 | 확인 못 함 | 1회 실행만 했다. 타이머 시험(docker pause)은 PG 쪽이라 건너뜀. |
| H3 건너뛰기 | 문제 L | 건너뛴 사유는 명시(conftest.py:28). 대체 수단 scripts/smoke.sh의 `SMOKE_DB=postgres`는 docker 필요, 이 점검에서 실행 안 함. 기본 실행에서 77건이 조용히 건너뛰어진다는 점이 위험. |
| H4 부정 시험 | 문제 L | 403·형식 오류 시험은 있으나 잘못된 필드 형식(bool 대신 문자열, 목록 아닌 edits), 큰 입력의 시간 예산, 권한 분리 시나리오 시험이 없다(이 감사의 실측이 시험 없이 재현됨). 제안: P1·P2에 회귀 시험 추가. |
| H5 환경 독립 | 문제 L | 이미지 빌드는 sibling 리포지토리(`../boundary-contracts`, `../survey-service`)의 git 태그에 의존(build_wheels.sh)하고, 개발 설치는 `../survey-service/schema` 편집 설치(.venv 확인). 영역 리포지토리 혼자 빌드되지 않는다. 두 번째 깨끗한 환경 검증은 하지 않았다. |

### I. 도메인·안전
| 항목 | 판정 | 근거·제안 |
| --- | --- | --- |
| I1 안전 결정 | OK | 정책 수치(질문 한도, 위험 기준, 위험 문구, 확인 한도)는 모두 자료나 저자 값이고 코드 기본값이 없다(design.md 원칙 5, textform.py가 누락 시 MISSING 플래그). 임상 승인의 자동 부여(`confirm`)는 D30 결정이며 B2에서 별도 지적. |
| I2 문구 출처 | OK | 환자에게 가는 문장은 저자 자료에서만 오고, 변경 분류에 임상 검토 표시/CLINICAL_REVIEW가 있다(design.md:75-92, 코드 읽기와 grep 수준). |
| I3 실패 시 환자 | OK | 이 서비스는 환자에게 직접 닿지 않는다. 장애 시 I1이 UNAVAILABLE(재시도 가능)로 게이트가 읽지 못할 뿐 잘못된 문항이 나가지 않는다. 읽지 못한 자료는 PARSED가 아닌 FALLBACK으로 명시(service.py:266-275). |

## 이 점검이 읽지 못한/얕게 본 곳

- PostgreSQL 경로의 시험 77건(TEST_DATABASE_URL 없음)과 컨테이너 스모크(docker 필요)는 실행하지 않았다. PG 쪽 판정(A3, A5, D5의 NUL 파일 이름)은 코드 읽기에 근거한다.
- pip-audit/이미지 스캔은 설치 금지로 못 돌렸다(B9의 CVE).
- deploy의 DB 역할 스크립트, 백업 스크립트, 비밀 파일 권한, Caddyfile 전체, CI/레지스트리는 영역 밖이거나 비밀이라 읽지 않았다. compose.yaml과 Caddyfile은 노출 범위 확인을 위해 해당 서비스 줄·grep으로만 봤다.
- docs/design.md, runbook.md, README.md는 전문을 읽지 않고 grep과 발췌로 대조했다(D7, E4, I2는 얕다).
- `preview.py`, `classify.py`는 정규식 grep과 시험 통과로만 봤고, 큰 bank에서의 시간은 측정하지 않았다.
- SIGTERM 동작(A4)은 코드·compose 근거로 추정했으며 컨테이너를 띄워 확인하지 않았다.
- 제곱 시간 측정은 이 PC 한 대, Python 3.12, 1회 측정이다.
