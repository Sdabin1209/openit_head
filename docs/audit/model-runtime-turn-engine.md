# 전수 점검: model-runtime, turn-engine

> 읽기 전용 감사(2026-10-28). 기준: head/docs/AUDIT_CHECKLIST.md의 A~I 63개 항목, FAULT_POLICY.md. 코드·설정·문서는 수정하지 않았고 이 파일만 썼다. 비밀 위치는 열지 않았다.

## 0. 요약

- 판정 분모: 63개 항목 x 2개 영역 = 126개 판정. 건너뛴 항목 없음.
- 판정별 개수(항목 단위):

| 영역 | OK | 문제 | 해당 없음 | 확인 못 함 | 합계 |
|---|---|---|---|---|---|
| model-runtime | 19 | 29 (M 15, L 14) | 7 | 8 | 63 |
| turn-engine | 15 | 6 (M 1, L 5) | 40 | 2 | 63 |
| 합계 | 34 | 35 | 47 | 10 | 126 |

- 같은 원인을 묶은 서로 다른 문제: 20건(M 7, L 13), 2절. 항목 표의 "문제" 35건은 이 20건을 여러 항목이 가리킨 횟수다.
- H(높음) 문제: 확정 0건. 조건부 H 후보 1건: MR-3(긴 입력이 `/readyz`를 503으로 만들고, survey-service가 그것으로 턴을 막으면 교착)이며 조건은 읽지 못한 영역에 있다.
- M 문제 7건: MR-1 인증 기본 열림·역할 구분 없음, MR-2 특수 토큰 인젝션(+B 내용 검사 없음), MR-3 입력 길이 상한 없음, MR-4 연결·동시성 자원 한도 없음, MR-5 공급망 고정·스캔 부재, MR-6 시간 한도·처리량 미실측, TE-1 `validate_extraction`이 값 타당성·중복·타 문항 덮어쓰기를 안 봄.
- 시험 실행(영역 `.venv`, 읽기 전용): model-runtime 172 통과/1 건너뜀, turn-engine 39 통과/1 건너뜀. 한 환경 결과이며 두 번째 환경 확인이 아니다.
- 사용자·헤드 결정이 필요한 것: MR-1 기본값 변경 시 deploy 영향, MR-2(학습 글자 일치·G05), MR-3 계약 maxLength, MR-6(GPU 실측), MR-7, MR-13, MR-14, TE-1(I8 규칙 확장). 나머지는 영역에서 자율 수정 가능.

## 1. 항목별 판정

표기: `OK:` 문제 없음(근거), `문제[H/M/L] ID:` 문제(ID는 2절), `N/A:` 해당 없음(이유), `확인못함:` 확인 못 함(이유). model-runtime=MR, turn-engine=TE.

| 항목 | model-runtime | turn-engine |
|---|---|---|
| A1 외부 호출 timeout | OK: release 번들 읽기 소켓 timeout 120초(server.py:435), `/readyz` 도달성 확인 2초(:159), 요청 총 상한 3.5초(:280-303), 시험 test_hung_engine_returns_503_engine_timeout... | N/A: 외부 호출 없음(boundary.md 1절, 코드에 I/O·네트워크 없음) |
| A2 재시도 | OK: 재시도는 모델 생성뿐이고 `max_attempts` 최대 5(serving_config.py:159), 추론은 부작용 없음(HTTP.md I9). 백엔드 기동 재시도는 고정 30초(:188-190, 단일 프로세스라 지터 불필요) | N/A: 호출·재시도 없음 |
| A3 부분 쓰기 없음 | OK: 번들은 stage 디렉터리에 풀고 검증한 뒤 최종 위치로 옮긴다(releases.py:49-74, `_place` 구현은 읽지 못함), 적재 실패는 해당 릴리스만 FAILED이고 서빙 중 릴리스는 유지(server.py:232-234) | N/A: 쓰기 없음 |
| A4 우아한 종료 | 문제[L] MR-8: SIGTERM에 `SystemExit`, daemon 스레드(server.py:459-466) | N/A: 프로세스 없음 |
| A5 복구 후 자동 정상화 | 문제[L] MR-7: 백엔드 기동 실패(:179-190)와 `engine_error`는 자동 해제되나, 엔진이 영영 멈추면 `/healthz`가 200이라 재시작이 일어나지 않는다 | N/A: 상태 없음 |
| A6 무한 증가 없음 | 문제[L] MR-9: 번들 디렉터리를 지우지 않음(server.py:229-230은 메모리만), FAILED 릴리스 항목 영구 보존(MR-4) | N/A: 상태 없음. `lru_cache`는 검증기 2개뿐(validation.py:25-27) |
| A7 동시성 | OK: 엔진 직렬화 `engine_lock`, 릴리스 표 `rlock`, 대기 거절(:270-303). 시간 초과 뒤 늦게 끝난 호출이 락을 풀 때까지 새 호출이 못 들어오므로 `overdue`·`session.last_call_info` 경합 없음(코드 읽기, 시험 test_rejects_when_queue_would_exceed_wait 등) | OK: 전역 가변 상태 없음, 입력을 바꾸지 않음(validation.py 전체 정독) |
| A8 healthz/readyz 의미 | OK: healthz 항상 200(:360), readyz는 백엔드·엔진 정지·엔진 예외·release 도달성을 반영(:144-167), 의미는 boundary.md에 문서화. 한계는 MR-7 | N/A: 서비스 아님 |
| A9 자원 한도 | 문제[M] MR-4(연결·스레드·동시 적재 무제한), MR-3(입력 길이). 엔진 메모리는 프로파일이 정함 | N/A: 프로세스 없음. 입력 크기는 호출자 몫(G3 참고) |
| B1 인증 기본 거부 | 문제[M] MR-1: 토큰이 없으면 모두 허용(server.py:353-354) | N/A: HTTP 경로 없음 |
| B2 인가 | 문제[M] MR-1: 모든 역할 토큰이 PUT/GET/POST 전부 허용(:356). 세션 개념이 없는 무상태 서버라 수평 권한 상승(다른 세션 데이터)은 해당 없음 | N/A: 접근 주체 없음 |
| B3 비밀 | OK: `_FILE` 우선(read_secret, server.py:404-408), 시작 로그는 출처만, 값 부재 시험 tests/test_secrets_hidden.py, 이미지 ENV에 비밀 없음(Dockerfile:12,21-23). 한계: 회전은 재시작 필요, runbook 예시 compose는 토큰을 환경 변수로 보임(MR-1) | N/A: 비밀 사용 없음(README 4절, 코드 grep) |
| B4 입력 검증 | 문제[M] MR-3, MR-4: 길이 상한 없음, 깊은 중첩 JSON·PUT 길이 처리 미흡. 양호: release_id 정규식(:53,373), JSON만 역직렬화, 본문 4 MiB 상한(:383) | 문제[L] MR-14: 스키마 `$` 때문에 키 `Q4.answer\n`이 통과(실행 확인) |
| B5 인젝션 | 문제[M] MR-2: 프롬프트 인젝션(특수 토큰 미이스케이프). SQL·명령·템플릿은 N/A(DB·셸 없음, grep). 로그 인젝션 OK(경로는 `ID_RE`로 제한 :333, 발화 로그 없음) | OK: 발화·출력 값을 해석하거나 메시지에 싣지 않음(Violation 메시지 고정 문구, validation.py:21,59-107). eval·exec 없음(grep) |
| B6 SSRF | OK: 호출자가 URL을 정할 수 없다. release URL은 환경 변수(:435), 모델은 프로파일(운영자 설정) | N/A: 네트워크 없음 |
| B7 웹 | N/A: 브라우저용 응답 없음(JSON·text/plain API) | N/A: 웹 없음 |
| B8 전송 | 확인못함: 서버는 평문 HTTP만 제공(:456), 발화가 내부망에서 평문으로 간다. TLS 종료·네트워크 분리는 deploy 소관이라 읽지 못함 | N/A: 전송 없음 |
| B9 의존성 | 문제[M] MR-5: digest·해시 고정 없음, 스캔 못 함 | 문제[L] TE-2: 잠금은 `==`로 고정이나 해시·커밋 SHA 없음, 스캔 못 함 |
| B10 속도 제한 | 문제[L] MR-4: 속도 제한은 없고 대기 상한 503(:276-282)만 있음. 인증이 없으면 남용 가능(MR-1) | N/A: 요청 처리 없음 |
| B11 오류 정보 노출 | 문제[L] MR-10: 비인증 `/readyz`에 host:port·예외 이름. 그 밖의 오류는 종류만(:58-68,313,322; 400은 경로:키워드만 errors.py:14) | OK: `ContractViolation.errors`는 `경로: 검사` 이름뿐(validation.py:50, _common.py:10) |
| B12 토큰 수명·범위 | 문제[M] MR-1: 역할 무시, 만료·회전 없음, 빈 토큰 허용 | N/A: 토큰 없음 |
| C1 개인정보 목록 | OK: 발화·B 입력은 요청 본문으로 받아 메모리에서만 쓰고 저장·로그하지 않는다(로그 호출 전수: session.py:170,184, server.py의 릴리스 ID·예외 이름·위반 경로). 디스크에는 어댑터·프롬프트·질문 은행(환자 정보 아님)만 | OK: 저장·전송·기록 없음(boundary.md 2절 약속, 코드에 로그 호출 없음) |
| C2 최소 수집 | OK: 서버가 수집·저장하는 환자 값 없음 | OK: 같음 |
| C3 보존·삭제 | N/A: 보존하는 환자 데이터 없음 | N/A: 같음 |
| C4 비식별 | 확인못함: 이 서버의 로그는 깨끗하나 vLLM 엔진 자체 로그가 프롬프트를 남기지 않는지는 GPU에서 확인하지 못했다(`disable_log_stats`는 설정만, vllm_backend.py:94 주석이 "GPU 시험에서 확인") | OK: 메시지·예외에 값 없음 |
| C5 저장·전송 암호화 | N/A: 저장 없음. 전송은 B8 | N/A: 저장·전송 없음 |
| C6 접근 기록 | 문제[L] MR-11: 누가 릴리스를 적재했는지(토큰 역할) 기록하지 않음(로그는 릴리스 ID만 :231) | N/A: 접근 주체 없음 |
| C7 백업·복원 | N/A: 상태 없음(번들·HF 캐시는 재생성 가능) | N/A: 상태 없음 |
| C8 DB 계정 최소 권한 | N/A: DB 없음 | N/A: DB 없음 |
| C9 마이그레이션 | N/A: 스키마 마이그레이션 없음(릴리스 되돌리기는 F4) | N/A: 같음 |
| C10 정합성·유니코드 | 확인못함: 발화에 NFC/NFD 정규화 코드가 없음(grep). 학습 데이터가 어느 형태인지 읽지 못해 판단 불가 | N/A: 문자열 값을 해석하지 않고 ASCII 패턴의 키·문항 ID만 비교 |
| D1 계약 일치 | OK: HTTP.md I9 표와 라우트·상태 코드·헤더·본문 형식 대조(위 3절), 계약 적합성 시험 test_contract_client_conformance 통과. 추가 필드 `system_prompt_sha256`은 boundary.md에 문서화 | OK: I8 시그니처와 위반 코드가 boundary.md 8-1과 validation.py가 일치, 시험 통과 |
| D2 불가능한 전이 방어 | OK: 릴리스 상태 LOADING/LOADED/FAILED 전이(server.py:193-209), 미적재는 404 | OK: 문항 순서·건너뛰기 어긋남을 `NEXT_ITEM_MISMATCH`/`SKIP_ORDER_MISMATCH`로 잡음(실행 확인). 한계는 TE-1 |
| D3 멱등·중복 | OK: PUT 멱등(:195-209), 추론은 부작용 없음 | N/A: 순수 함수 |
| D4 시간·시계 | OK: 마감은 `time.monotonic()`(:280). `avg_s`·probe가 `time.time()`을 쓰지만 판단 영향 미미 | N/A: 시간 사용 없음 |
| D5 인코딩·크기 | 문제[M] MR-3: 긴 한글·큰 본문(4 MiB)의 상한이 프롬프트 길이와 맞지 않음. NUL·이모지는 `json.dumps` 이스케이프라 안전 | 문제[L] MR-14: 끝 줄바꿈 키 통과. NUL 포함 입력은 오류 없이 처리(실행 확인) |
| D6 값 지어내기 금지 | 문제[M] MR-2: A는 OK(엄격 스키마, 실패 시 503 OUTPUT_INVALID, session.py:164-173, 대체 출력 없음). B는 비어 있지 않음만 검사하고 내용·숫자 검사 없음(G05 열림) | 문제[M] TE-1: 구조 검사는 견고하나 값 타당성·중복·타 문항 덮어쓰기는 통과(실행 확인) |
| D7 문서-코드 일치 | 문제[L] MR-15: README의 "154개 수집"은 현재 173(172 통과+1 건너뜀)과 다르다, boundary.md 머리의 "계약 2.0.0 기준"은 v2.0.2와 불일치 | 문제[L] TE-3: flow.py 주석 "25개 문항"과 실제 31개 |
| E1 구조화 로그 | 문제[L] MR-11: 상관 ID 없음, 지연 미기록. 발화·비밀은 안 남음(OK 부분) | N/A: 로그 없음 |
| E2 메트릭·경보 | 문제[L] MR-11: `/metrics` 없음. 경보는 `/readyz` 감시(FAULT_POLICY 14)에 의존 | N/A |
| E3 설정·시작 거부 | 문제[M] MR-1: 보안 기본값(토큰)이 열림. 양호: 백엔드·스키마·비밀 파일 오류는 시작 거부(server.py:398-420) | N/A: 설정 없음 |
| E4 런북 | OK: docs/runbook.md 증상별 확인 표(161행 근처)와 boundary.md 장애표 | N/A: 서비스 장애 없음(runbook은 개발·릴리스 절차) |
| E5 감시·알림 | 확인못함: 감시 대상과 알림 경로는 deploy 소관, 이 영역은 `/readyz`만 제공 | N/A |
| E6 용량 계획 | 문제[M] MR-6: 실제 모델 지연·처리량 측정 없음(boundary.md가 "초기값 경고"로 자인) | N/A: 용량 개념 없음 |
| E7 시작 순서 | OK: 백엔드 비동기 기동 + readyz 503(server.py:109,179-190), release 도달성 대기 | N/A |
| E8 시간 불변식 | OK: boundary.md의 불변식(10초>9.5>6>4>3.5)과 기본값 3.5/3.0/120이 코드와 같다(:444-448). 값의 실측 근거는 MR-6 | N/A |
| F1 이미지 권한·포트 | 문제[M] MR-1: 비root(Dockerfile:30,45)는 OK이나 runbook 예시가 8080 전체 게시. 읽기 전용 루트는 쓰기 경로를 /var/lib/model-runtime로 모았으나(Dockerfile:20-23) 그 모드의 시험은 없다. capabilities·docker.sock은 compose를 읽지 못함 | N/A: 이미지 없음 |
| F2 이미지 핀·스캔 | 문제[M] MR-5 | N/A: 이미지 없음 |
| F3 compose | 확인못함: compose는 deploy 소관. runbook의 예시 조각에는 자원 한도·restart가 없음 | N/A |
| F4 되돌리기·업그레이드 순서 | 문제[L] MR-9: `MAX_RELEASES`로 이전 릴리스 유지, MAJOR.MINOR 불일치 거부(:217)는 양호하나 퇴출이 적재 순서라 활성 릴리스가 밀려날 수 있음 | OK: `ENGINE_VERSION`=pyproject 버전을 시험이 확인(boundary.md 4절), SemVer 표 |
| F5 비밀 파일 권한 | 확인못함: 파일 권한·compose 환경은 읽지 못함(비밀 위치 열람 금지). 코드는 파일을 읽기만 함 | N/A |
| F6 레지스트리·CI 신뢰 | 확인못함: CI·레지스트리는 deploy 소관 | N/A |
| G1 측정된 처리량·지연 | 문제[M] MR-6: 측정은 1.5B·무작위 어댑터뿐(design.md:216-257) | 확인못함: 측정 문서 없음. 이 점검의 임시 측정: 작은 입력 1000회 0.26초 |
| G2 N+1·인덱스·풀 | N/A: DB 없음. 엔진은 직렬 | N/A |
| G3 큰 입력 폭주 | 문제[M] MR-3 | OK: 선형 알고리즘이고 values 20,000개 1.22초(실행 확인), 대부분 jsonschema 비용 |
| H1 핵심 경로 실구성 시험 | 문제[L] MR-6: I4 서버·계약 클라이언트는 실제 참조 구현으로 시험(test_server_e2e.py)하나 vLLM은 모킹(test_vllm_backend.py), GPU 경로 시험 없음(문서화됨) | OK: 실제 `boundary_contracts` 검증기와 공개 함수로 시험, 모킹 없음 |
| H2 간헐 실패 | 문제[L] MR-16: 실제 `sleep` 12곳(tests/test_server.py)이 마감 시간 시험에 쓰임, 포트는 대부분 0 배정 | OK: 시계·네트워크·무작위 없음 |
| H3 건너뜀 사유·대체 | OK: 1건(xgrammar 없음, `-rs`로 확인), 대체는 scripts/xgrammar_check.py | 문제[L] TE-4: 1건(학습 데이터 A 전수), 0.4.0 재실행 기록 없음 |
| H4 부정 시험 | 문제[L] MR-16: 인증 거부·입력 400·출력 불량·옛 경로는 있음. 본문 상한 초과, 잘못된 release_id, 역할 인가, 특수 토큰, 긴 입력 시험은 이름 기준으로 찾지 못함 | OK: 위반 코드별 부정 시험이 있다(39개 통과; 다만 값 타당성 부정 시험은 규칙이 없어 없음, TE-1) |
| H5 환경 의존 | 확인못함: 이 PC의 기존 `.venv` 한 환경에서만 통과. 형제 폴더 읽기 시험 2곳(runbook:6), 깨끗한 두 번째 환경은 안 돌림 | 확인못함: 같은 이유(STATUS 남은 일 4, OPEN_GAPS U12 열림) |
| I1 안전 결정 표시 | OK: 대체 문구 "잠정" 표시와 G04 열림(protection.py:87,96), 환자 재질문 상한·직원 호출은 이 영역에 없음 | OK: `DATASET_V2_FLOW`가 "임시"로 표시(flow.py:4,47-48), CR-010 열림. 위험 신호 로직 없음 |
| I2 문구 출처 | OK: 대체 문구에 도메인 소유자 확인 필요 표시(protection.py:87). 모델이 생성하는 문구의 임상 검토는 model-lab·게이트 소관이라 확인 못 함 | N/A: 환자 문구 없음 |
| I3 실패 시 환자에게 | 문제[L] MR-13: extract 실패는 503으로 정직하게 알림(OK), respond 실패는 대체 문장이며 재료가 없으면 "다시 한 번 말씀해 주세요"가 END 뒤에도 나갈 수 있다 | OK: 위반은 목록으로 반환되어 조용히 통과하지 않고, 입력 위반은 예외 |

## 2. 문제 목록 (같은 원인은 묶음. 항목 표의 ID가 여기를 가리킨다)

범례: 자율 = 영역 에이전트가 단독으로 고칠 수 있음. 결정 = 헤드/사용자 결정 또는 다른 영역 협의 필요.

| ID | 심각도 | 제목 | 근거(파일:줄) | 제안 수정 | 자율/결정 |
|---|---|---|---|---|---|
| MR-1 | M | 인증이 기본 열림이고 역할 구분이 없다 | server.py:353-356(`tokens`가 비면 모두 허용), :404(빈 토큰 `survey=` 허용), :455(기본 바인드 0.0.0.0), :356(`in values()` 일반 비교, 역할 무시), docs/runbook.md:37(기본 "인증 없음"), :94(예시 compose가 `8080:8080` 전체 게시), :100(예시가 토큰을 환경 변수로) | 토큰이 없으면 시작을 거부(개발용 명시 옵션으로만 허용), 빈 토큰 거부, `hmac.compare_digest`, 역할별 경로 제한(survey는 extract/respond/GET, 적재 PUT은 별도 역할), 예시를 `127.0.0.1:8080:8080`과 `_FILE`로 수정 | 코드·문서는 자율. 기본값을 거부로 바꾸면 deploy compose가 토큰을 주는지 확인해야 하므로(읽지 못함) 헤드와 협의 |
| MR-2 | M | 환자 발화 속 채팅 특수 토큰(`<\|im_end\|>` 등)을 막지 않는다 | prompts.py:32-42(발화가 `json.dumps`로만 들어가며 `<\|im_end\|>`는 이스케이프되지 않음), docs/design.md:18 ④(알고 있으나 "학습과 같은 동작이라 막지 않았다"), session.py:147-148·protection.py:98(respond 검증은 비어 있지 않음뿐) | 실제 토크나이저가 텍스트 안의 특수 토큰 문자열을 특수 토큰으로 해석하는지 GPU 환경에서 먼저 확인(이 점검은 못 함). 해석하면 발화·입력 문자열 값에서 `<\|...\|>` 형태를 무력화(학습 글자와 어긋나는 범위를 model-lab과 확인), 또는 토큰 ID로 조립. respond 출력의 내용 검사(G05)도 함께 | 결정(학습 글자 일치 U03, G05 미정, 도메인) |
| MR-3 | M | 입력 길이 상한이 없고, 너무 긴 입력이 `/readyz`를 503으로 만들 수 있다(추정) | schema에 `user_utterance` maxLength 없음(boundary-contracts 스키마 확인), server.py:50(본문 4 MiB), :319-322(엔진 예외는 모두 `engine_error`를 세워 `/readyz` 503, 다음 성공 때까지), profiles/gpu-12g.json(`max_model_len` 4096) | 호출 전에 프롬프트 길이를 `max_model_len`에서 도출한 상한과 비교해 400으로 거절하고 입력 기인 예외는 `engine_error`를 세우지 않는다. 계약에 maxLength를 요청(CR). 주의: vLLM이 초과 프롬프트에 예외를 던진다는 것은 이 점검이 실행으로 확인하지 못했다. survey-service가 `/readyz`로 턴을 막는다면 요청이 없어 해제되지 않는 교착이 가능(그쪽은 읽지 못함, 그 경우 H) | 코드는 자율, 계약 상한은 결정(헤드 CR) |
| MR-4 | M | 연결·동시성 자원 한도가 없다 | server.py:455-456(`ThreadingHTTPServer`, 스레드 수·소켓 timeout 없음), :376(PUT의 `int(Content-Length)` 미처리·음수면 EOF까지 읽음), :385-387(깊은 중첩 JSON의 RecursionError 미처리), :199-203(동시 적재 수 제한 없음, 실패 릴리스 항목이 영구 보존) | 핸들러 `timeout` 설정, 동시 연결·동시 적재 상한, PUT 본문 상한과 파싱 오류 처리, FAILED 항목 정리 | 자율 |
| MR-5 | M | 공급망 고정이 약하고 취약점 점검을 하지 못했다 | Dockerfile:10(`python:3.12-slim` 태그만, digest 없음), requirements-gpu.lock(199개 `==`, 해시 없음), Dockerfile:24(boundary-contracts를 빌드 컨텍스트로, 태그 v2.0.2는 가변), pip-audit 미설치 | 베이스 이미지 digest 고정, `pip --require-hashes`, 태그의 커밋 SHA 기록, 이미지 스캔을 CI에 | 자율(CI/스캔은 deploy와 협의) |
| MR-6 | M | 시간 한도(요청 3.5초, 대기 3.0초)와 처리량이 실제 모델로 측정되지 않았다 | docs/boundary.md "초기값 경고", design.md:216-257(1.5B·무작위 어댑터 측정뿐) | 24GB에서 extract/respond p50/p95/max 실측 후 값 확정(절차는 boundary.md에 있음) | 결정(GPU 필요, 헤드가 6초 불변식 재확인) |
| MR-7 | L | `/healthz`가 엔진 정지에도 200이라 컨테이너 재시작이 일어나지 않는다 | Dockerfile:50, boundary.md 장애표(문서화됨) | 밖의 감시가 `/readyz` 503 지속을 보고 재시작하는 경로를 deploy에서 확인 | 결정(deploy) |
| MR-8 | L | 종료 시 진행 중 요청을 마무리하지 않는다 | server.py:459-466(SIGTERM이 `SystemExit`, 핸들러 스레드는 daemon, 새 요청 거부 단계 없음) | 종료 시 `/readyz` 503 후 진행 중 요청 대기(상한) | 자율 |
| MR-9 | L | 번들 디렉터리를 지우지 않고, 퇴출이 사용 순서가 아닌 적재 순서다 | server.py:229-230(메모리 `del`만, 디스크 `dest/<release_id>` 유지), :228-230(오래 적재한 활성 릴리스가 먼저 퇴출 가능), 디스크 경보 없음 | 퇴출 시 디렉터리 삭제, 사용 시각 기준 퇴출, 디스크 여유 점검을 `/readyz`에 | 자율 |
| MR-10 | L | 인증 없는 `/readyz` 사유에 내부 정보가 있다 | server.py:152·163(release 서버 host:port, 엔진 예외 클래스 이름) | 사유를 분류 코드로, 상세는 로그로 | 자율(FAULT_POLICY 5항은 "접속 정보 없음"을 요구 → 현재 host:port가 이에 어긋남) |
| MR-11 | L | 요청 상관 ID·지연·메트릭이 없다 | server.py:332-333(로그에 메서드와 경로만), `/metrics` 없음 | 요청 ID와 지연(원문 제외)을 로그에, 호출 수·지연·OUTPUT_INVALID 수 노출 | 자율 |
| MR-12 | L | 운영에서 `MODEL_RUNTIME_BACKEND=fake`로 기동되는 것을 막지 않는다 | server.py:399·411-420(fake 코드와 "(가짜 응답)"가 같은 이미지에 있음), backends.py:111 | 가짜 백엔드는 시험 전용 환경 변수 확인 후에만 허용, `/v1/info`의 backend를 deploy가 감시 | 자율 |
| MR-13 | L | respond 대체 문장의 재료 없음 문구가 잠정이고 END 뒤에도 같은 문구가 나갈 수 있다 | protection.py:96(G04 열림) | 도메인 소유자가 문구 확정 | 결정(사용자, 도메인) |
| MR-14 | L | 스키마 정규식의 `$`가 끝 줄바꿈을 허용한다(`Q4.answer\n` 통과) | boundary-contracts 스키마의 `^...$` 패턴(model-runtime과 turn-engine 모두 영향). turn-engine에서 `Q4.answer\n` 키가 스키마를 통과하는 것을 실행으로 확인(우연히 건너뛰기 규칙에 걸려 위반이 났을 뿐) | 패턴을 `\z` 또는 `^(?!...)`식으로(계약 변경) | 결정(헤드 CR) |
| MR-15 | L | 문서 사실이 어긋난다 | README.md "154개 수집"(현재 173: 172 통과+1 건너뜀), docs/boundary.md 머리 "계약 2.0.0 기준"(실제 v2.0.2) | 시험 개수 복사 삭제(README 5절만 정본이라는 워크스페이스 규칙), 버전 정정 | 자율 |
| MR-16 | L | 시험이 실제 타이머에 기대고 부정 시험이 부족하다 | tests/test_server.py의 `sleep` 12곳, 이름 기준으로 본문 상한 초과·잘못된 release_id·역할 인가·특수 토큰·긴 입력 시험을 찾지 못함 | 마감 시험에 주입 가능한 시계, 부정 시험 추가 | 자율 |
| TE-1 | M | `validate_extraction`은 구조만 보고 값의 타당성·중복·타 문항 덮어쓰기를 보지 않는다 | validation.py:60-117. 실행 확인: `Q4.bogus=123456789` 통과, `Q4.answer="열대여섯"` 통과, `Q1.D01.*`를 Q4 질문 중에 저장해도 통과. 같은 키가 두 번 나와도 중복 자체는 위반이 아니다(`saved` 사전에서 마지막 값이 이김, validation.py:107) | 칸별 타입·열거·범위를 담는 표(CR-010과 같이)와 `DUPLICATE_KEY`·`UNKNOWN_SLOT` 위반 추가. 현재 문서(boundary.md 8-1)가 약속한 규칙과는 일치하므로 "버그"가 아니라 값 지어내기 방지의 범위 한계. survey-service가 별도로 값을 검증하는지는 읽지 못함 | 결정(I8 규칙 확장은 계약·MINOR 버전, 헤드) |
| TE-2 | L | 의존 고정이 약하다 | pyproject.toml(`jsonschema>=4.18`), requirements.lock 1행(git 태그만, 커밋은 주석), 취약점 스캔 못 함 | 해시 고정, 커밋 SHA | 자율 |
| TE-3 | L | 문서·주석 사실이 어긋난다 | flow.py:4("25개 문항") 대 flow.py:52-55와 README(31문항) | 주석 정정 | 자율 |
| TE-4 | L | 학습 데이터 전수 시험이 기본으로 건너뛰어지고 0.4.0에서 재실행 기록이 없다 | tests/test_validation.py:244, README 5절 | 0.4.0으로 재실행 후 CHANGELOG에 기록 | 자율(학습 서버 읽기는 허락된 경로로) |

H 문제: 확정된 것 0건. 조건부 H 후보 1건: MR-3의 교착(survey-service가 model-runtime의 `/readyz`로 환자 턴 수용을 막는 경우). 그 조건은 이 점검이 읽지 못한 영역(survey-service, deploy)에 있다.

## 3. model-runtime 서버 라우트 전수 표 (server.py:358-389 `_route`, 근거는 코드를 읽은 것)

| 경로 | 메서드 | 인증 | 근거와 비고 |
|---|---|---|---|
| `/healthz` | GET | 없음 | :360. 항상 200 |
| `/readyz` | GET | 없음 | :362-364. 503 사유에 host:port·예외 이름(MR-10) |
| `/v1/info` | GET | Bearer(토큰 설정 시) | :365-368. 해시·백엔드·`test_hooks`. 토큰 미설정이면 공개 |
| `/v1/releases/{id}` | GET | Bearer(토큰 설정 시) | :378. id는 `ID_RE`(:53)로 제한, 경로 조작 불가 |
| `/v1/releases/{id}` | PUT | Bearer(토큰 설정 시) | :375. 본문을 읽고 버림, 상한·오류 처리 없음(MR-4). I4(설정된 release URL)에서만 읽음, 호출자가 URL을 정할 수 없음 |
| `/v1/releases/{id}/extract` | POST | Bearer(토큰 설정 시) | :380-388. 본문 1 B~4 MiB, JSON 계약 검증 |
| `/v1/releases/{id}/respond` | POST | Bearer(토큰 설정 시) | 같음 |
| 그 밖의 경로·메서드 | 임의 | 인증 먼저(없으면 403) 뒤 404 | :365-372, :389. HEAD·DELETE·OPTIONS는 `do_*`가 없어 라이브러리 기본 501 |
| 역할 구분 | - | 어떤 역할의 토큰이든 모든 `/v1/*` 허용 | :356(MR-1) |

## 4. 영역 특유 점검 결과

1. 프롬프트 인젝션: 시스템 프롬프트는 어댑터 번들 파일(해시 검증)에서만 오고 환자 발화로 바꿀 수 없다(session.py:200-213, prompts.py:66). 발화는 user 메시지 JSON의 문자열 값으로만 들어간다. 그러나 특수 토큰 문자열은 이스케이프되지 않는다(MR-2). 출력 형식은 A가 스키마(제약 디코딩 + 생성 후 엄격 검증 session.py:148, `parse_constant` 거부 :142)와 turn-engine으로 막히지만 B(환자에게 가는 문장)는 비어 있지 않음만 검사한다.
2. 출력 검증과 값 지어내기: model-runtime은 A 출력을 엄격 스키마로 검증하고 실패하면 값을 만들지 않고 503 OUTPUT_INVALID(session.py:164-173)다. 대체 문장은 서비스가 준 재료(known/ask/hold/next.text)만 쓰고 발화를 쓰지 않는다(fallback.py:7-14). 우회 가능성: turn-engine이 값 타당성·중복·타 문항을 보지 않는다(TE-1). 실행으로 재현했다.
3. 번들·어댑터 적재: tar 풀기는 경로 검사·상한(8 GiB)·`xb` 열기, 매니페스트 해시·어댑터 디렉터리 해시·프롬프트 해시를 검증한다(boundary_contracts clients/_http.py:118-152, releases.py:44-74, 읽기 전용으로 읽음). `read_system_prompt`는 `resolve()` 뒤 `is_relative_to`로 심볼릭 링크 탈출을 막는다(session.py:203-213). 어댑터 경로는 이 번들 안으로만 간다. 신뢰의 뿌리는 release 서버(매니페스트 해시가 자체 포함이라 서버가 위조하면 통과). 어댑터 가중치 형식(safetensors/pickle)에 따른 vLLM 적재 위험은 확인 못 함.
4. 서빙 서버 인증과 노출: MR-1.
5. 추론 엔진 자원 한도: 엔진 호출은 직렬이고 요청 상한과 대기 상한이 있다(server.py:270-303). GPU 메모리는 프로파일(`gpu_memory_utilization`, `max_num_seqs`)이 정한다. 입력 길이 상한이 없다(MR-3), HTTP 연결 수 상한이 없다(MR-4). OOM 시 동작은 실행하지 못해 확인 못 함.
6. 학습·평가 코드가 운영 이미지에 있는가: 없다. Dockerfile:25-28은 `src`, `profiles`, `pyproject.toml`만 복사하고 scripts·tests·docs는 들어가지 않는다(.dockerignore도 tests·docs 제외). GPU 잠금 파일에 peft·trl·datasets 등은 없다(grep). vLLM의 전이 의존(fastapi, openai, uvicorn)은 있으나 이 서버는 쓰지 않는다. 가짜 백엔드는 이미지에 있다(MR-12).

## 5. 이 점검이 읽지 못한/얕게 본 곳

- 읽지 못함: `secrets/`, `.env`, 토큰 값, `~/.docker/config.json`(지시대로 열지 않음). survey-service·deploy·release-gate·boundary-contracts HTTP.md I9 외 문서(영역 경계 규칙). 그래서 호출 측 timeout·재시도·`/readyz` 사용, compose의 자원 한도·restart·포트 바인딩·read-only 루트·capabilities, 비밀 파일 권한(F3, F5 일부)은 확인 못 함.
- 실행하지 않음: Docker 이미지 빌드·스모크, GPU/vLLM 전부(OOM, 특수 토큰 해석, 긴 프롬프트 예외, LoRA 가중치 적재), `pip-audit`·이미지 스캔(설치 금지와 외부 전송 금지 때문), 부하·메모리 측정, 학습 데이터 전수 검증.
- 얕게 본 곳: model-runtime의 `schema_guard.py`의 relax 변환 352줄(전체 정독 안 함, 첫 140줄만), `backends.py`의 fake 응답 생성 후반, `scripts/` 전부(이미지에 안 들어가는 것만 확인), `tests/`는 이름·일부 grep만(시험의 부정 케이스 충분성은 목록으로만 판단), docs/design.md·STATUS.md는 grep 위주, turn-engine의 `docs/rules/`와 `scripts/validate_dataset_a.py`.
- 시험 실행 결과(영역 `.venv`, 캐시·바이트코드 쓰기 끔): model-runtime 172 통과, 1 건너뜀(xgrammar 없음), 경고 506(상류 `RefResolver` 폐기 경고). turn-engine 39 통과, 1 건너뜀(`TURN_ENGINE_DATASET_A` 없음). 이는 한 환경(이 PC의 기존 `.venv`) 결과이며 깨끗한 두 번째 환경 확인이 아니다.
- 이 점검에서 한 재현: turn-engine `validate_extraction`에 손으로 만든 출력 몇 개를 넣은 것(읽기 전용, 파일 쓰기 없음).
