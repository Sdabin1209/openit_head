# 영역 횡단 점검 (cross-cutting)

> 2026-10-28. 읽기 전용 정적 점검(코드·설정·문서·계약을 읽고 grep으로 확인). **실행·시험은 하지 않았다.** 근거는 파일과 함수 이름(줄 번호는 확실한 것만). 범위는 `AUDIT_CHECKLIST.md`의 B·C·I 중 영역 사이를 가로지르는 부분과 `FAULT_POLICY.md`다. 영역 안쪽 점검은 다른 에이전트의 몫이라 여기서는 흐름만 본다.
> 표기: **확인** = 코드·설정을 읽어 확인, **추정** = 읽은 것에서 추론, **미확인** = 읽지 못했거나 실행해야 아는 것.

## 0. 요약

발견 29건: **H 6 / M 14 / L 9**.

### H 목록

| ID | 한 줄 | 항목 |
| --- | --- | --- |
| H-1 | 위험 신호 입력원이 배포 구성에 없다(G01). 게다가 문항 세트에 저작·임상 승인되는 `risk_phrases`·`risk_rule`·`ask_limit`·`confirm_limit`·`unrecognized_streak_limit`는 런타임이 읽지 않는다(저자·승인자는 작동한다고 믿기 쉽다). 반복 질문 상한도 기본 꺼짐. | I1·I3 |
| H-2 | 위험 정지가 성공(`DELIVERED`)하면 서버는 `turn_failure_signal=null`을 준다. 키오스크는 `DELIVERED`를 보고서야 대기 화면으로 가므로 **실제 서버에서는 "말씀해 주세요" 화면에 머물고**, 정지 중 발화는 무응답이며, "그만하기"를 누르면 열린 위험 알림이 직원 결정 없이 `RESOLVED`가 된다. | I3 |
| H-3 | 쓰기 확정이 실패하거나 턴 마감(6초)을 넘으면 위험 알림이 나가지 않는다(`staff_alert=NONE`). 사용자 결정 대기 항목이지만, 환자 쪽 안전망은 "다시 말씀해 주세요"와 20초 뒤 문구 화면뿐이다. | I3 |
| H-4 | 서비스 안 규칙 감지기(켜면)가 `n_plan_writes` 안에 있어 **LoRA-A 추출이 성공하고 검증을 통과한 뒤에만** 돈다. 모델 장애·출력 불량 때(가장 불안정한 때) 위험 문구를 놓친다. 입력원을 켜는 순간 발현하는 잠재 결함. | I3 |
| H-5 | 발화 원문과 세션 전체가 쌓이는 곳의 **보존 기본값이 전부 무기한**이다: survey 세션(purge 잡이 스케줄에 없고 환경값 없음), ops_log 원본(`raw_days: null`), outbox DEAD 행(삭제 코드 없음), 백업(보존일 미정). 삭제 경로는 일부만 있다. | C3 |
| H-6 | 키오스크·직원 브라우저 ↔ gateway가 **평문 HTTP**(`auto_https off`, TLS 미정)이고 내부 서비스 간(Trace 전량 포함)과 외부 추론 모드(`0.0.0.0` 바인드, 토큰만)도 평문이다. 기본 바인드가 `127.0.0.1`이라 현재는 노출되지 않지만, LAN에 열면 직원 암호·기기 토큰·환자 발화가 평문이다. | B8·C5 |

## 1. 임무 1 — 개인(건강)정보 흐름 (C1, C4)

### 1-1. 지점별 표

열: 발화 원문 / session_id / subject_ref / 직원 ID / 기기 ID / 시각 / 값(답변, 건강정보). `●` 있음, `○` 가명·마스킹, `-` 없음.

| # | 지점 | 원문 | sid | subj | 직원 | 기기 | 시각 | 값 | 저장·전송·로그 상태 (근거) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 환자 음성 → 브라우저 STT(Web Speech API ko-KR) | ● 음성 | - | - | - | - | - | - | 브라우저 구현에 따라 **벤더 서버로 음성이 나갈 수 있다**. 문서에 이 사실도 동의 절차도 없다(`kiosk-frontend/docs/brief.md:52`는 제공 방식 "미정"만). 실제 전송 여부는 미확인(브라우저 의존). → M-12 |
| 2 | 키오스크 브라우저 메모리 | ● | ● (`s-`+랜덤 96비트, `api/ids.ts`) | ● (URL 조각 또는 `/config.json`) | - | 기기 토큰(메모리) | - | - | 메모리에만 둔다. `localStorage·sessionStorage·cookie·console` 사용 없음(grep 확인). URL 조각은 읽자마자 `replaceState`로 지움 |
| 3 | 키오스크 → gateway | ● 본문 | ● 경로 | ● 세션 시작 본문 | - | ● `Authorization` 기기 토큰 | - | - | **평문 HTTP** (`Caddyfile` `auto_https off`, `:8080`). → H-6 |
| 4 | gateway(Caddy) 접근 로그(stdout JSON) | - 본문 안 남김 | ● URI | - | ● 직원 계정 ID(`user_id`) | - 공유 서비스 토큰으로 교체되어 기기 ID 안 남음 | ● | - | `Authorization`은 REDACTED. 컨테이너 로그 json-file 10MB×5 회전(`compose.yaml` x-hardening)이라 영속 감사 기록이 못 된다. → M-1 |
| 5 | gateway → survey-service | ● | ● | ● | `X-Openit-User`는 직원 경로에서만(§2-3) | - | - | - | 내부망 평문 HTTP, 서비스 kiosk/staff 토큰으로 교체 |
| 6 | survey PostgreSQL `survey` DB | ● `dialogue_log[].input.utterance`, 응답 문장 | ● | ● `session_meta.subject_ref` | ● 개입 항목 `staff_id`, 알림 `resolved_by` | - | ● `session_timeline`, 알림 `created_at` | ● `answer_records` | **원문·값 영속**. 접근 기록 `staff_access_log`(role·session_id·시각, 개인 직원 ID 없음). 보존: §1-3 |
| 7 | survey → model-serving (I9) | ● `user_utterance` | - | - | - | - | - | ● `known`·`ask`·상태(답변 문장) | Bearer, 평문 HTTP. 모델 서버 코드는 원문을 로그에 안 남긴다(`session.py` 주석, 로그 호출 grep 확인). vLLM 엔진 로그가 프롬프트를 내는지는 "GPU 시험에서 확인"이라고만 적혀 있다(`vllm_backend.py:94`) → **미확인** |
| 8 | survey → ops-feedback-ingest (I6) | ● TraceEnvelope 전량(`session_before`·`session_after` 문서 통째, 누적 대화) | ● | - (Trace에 안 들어감, 확인) | ● `log_entry.staff_id` | - | - | ● | 평문 HTTP. 턴마다 **세션 누적 전체**가 다시 실려 원본이 증폭된다 |
| 9 | survey outbox(PG) | ● 위와 동일 | ● | - | ● | - | ● | ● | SENT는 24h 뒤 삭제(`purge_sent`), **DEAD는 삭제 코드 없음**(`outbox.py`) |
| 10 | ops-feedback `ops_log`(원본) | ● | ● | - | ● | - | ● `received_at` | ● | `raw_traces.envelope` 평문 TEXT. 보존 `retention.raw_days: null`(`deploy/config/ops-feedback-job.yaml`) = 무기한 |
| 11 | **비식별(job-ops-feedback)** | ○ 허용목록 외 문자열 `[MASKED]` | ○ `p-`+해시(salt) | - | ○ 마스킹(허용키 아님) | - | ○ 입력 시각 대신 `received_at` | ○ `Value` 정의·`value` 키 통째 마스킹 | **비식별이 일어나는 유일한 곳**. 허용목록 방식 + 잔존 패턴 검사(이메일·전화·주민번호) 실패 시 닫힘. 한계는 M-3 |
| 12 | ops-feedback `ops_failure` | ○ | ○ | - | ○ (`reviewed_by`는 직원 ID ●) | - | `created_at` | ○ | FailureCase 불변. 삭제 API 없음 |
| 13 | reviewer 화면 → 검토 게시 | ● **검토자가 직접 쓴 `reviewed_input`·`expected`·`note`** | - | - | ● `reviewed_by` | - | ● | ● 가능 | 스키마 검증만, **PII 스캔 없음** → M-4 |
| 14 | question-authoring 개선 신호(I7 읽기) | - 건수·ID만 | - | - | - | - | - | - | 담는 것은 건수·유형 분포·ID(`signals.py`). 그러나 v2 Trace에 없는 `planner_output`를 읽어 문항 단위는 공백 → M-6 |
| 15 | synthetic-data 시드 → 데이터셋 → model-lab 학습 | ○ 비식별 trace는 쓰지 않고 `reviewed_input`만 (`seeds.py`) | - | - | - | - | - | ● 검토자 입력 | 한번 데이터셋에 들어가면 철회 경로 없음 → M-5 |
| 16 | 직원 알림(SSE·웹 푸시·`StaffAlert`) | - | ● | - | ● `resolved_by` | - | ● | - | 스키마상 발화·개인정보 없음(`StaffAlert.schema.json`). 푸시 본문 `alert_id·session_id·kind`, 푸시 서비스(외부)는 경유하나 페이로드는 암호화 |
| 17 | 결과 조회 API(result-reader, 내부) | - 발화 없음 | ● | ● | - | - | ● | ● | 게이트웨이에 열려 있지 않음(확인). 호출마다 접근 기록, 기록 실패 시 거부(fail-closed) |
| 18 | 백업(`pg-backup.sh`) | ● | ● | ● | ● | - | ● | ● | `pg_dump -Fc` 5개 DB 전량, 폴더 700·파일 600, **암호화 없음**, `BACKUP_RETENTION_DAYS`는 필수지만 값 미정(O16) → M-13 |

### 1-2. 로그에 원문이 나가는가 (grep 전수)

대상: survey-service, ops-feedback, model-runtime, release-gate, question-authoring, kiosk-frontend 정적 서버, synthetic-data, model-lab, turn-engine, boundary-contracts 클라이언트. 모든 `log.*`·`print` 호출을 훑고 본문 변수가 들어가는지 봤다.

| 판정 | 위치 | 내용 |
| --- | --- | --- |
| 원문 직접 출력 **없음**(확인) | survey `graph.py` 로그 12곳 | `session=… turn=… step=… error=<클래스명>`과 위반 코드·경로만(주석 "발화·값·메시지는 싣지 않는다"). `graph._fail`의 `detail`은 위반 코드@경로 요약 |
| 없음(확인) | survey `api.py`·`orchestrator.py`·`alerts.py`·`trace/exporter.py` | session/turn ID와 예외 클래스명만. `service.py`는 `log_message`를 비워 접근 로그도 없음 |
| 없음(확인) | model-runtime `session.py`·`server.py` | 시도 횟수·위반 이름(`violation_names`: 경로·키워드만)만. 입력 위반 응답 `ContractViolation`은 경로 목록(`violations_of`)만 |
| 없음(확인) | ops-feedback `api.py` | `log_message`는 경로(쿼리 제거)만. 검증 오류는 `_brief`(경로·규칙 종류만, 주석 "값 조각이 섞일 수 있으므로"). PG 오류는 클래스 이름만(`pgbase.py`, `from None`) |
| 조건부 주의 | ops-feedback `api.py` `log.exception("수집 중 예외")`·`("읽기 중 예외")`·`("검토 중 예외")` | 예상 밖 예외의 **스택 트레이스 전체**가 stdout로 나간다. 현재 경로에서 본문이 예외 메시지에 들어가는 곳은 못 찾았으나 보장이 없다(L-9) |
| 없음(확인) | gateway Caddy | 본문 미기록. URI의 session_id와 직원 계정 ID는 남는다(원문 아님) |
| 없음(확인) | boundary-contracts HTTP 클라이언트 | 서버 메시지를 `_scrub`한 뒤 오류에 담는다(`clients/_http.py:245`) |
| 개발 전용 | survey `cli.py` | 콘솔 입력을 stderr에 출력(알림 본문, 발화 없음). 서비스 진입점 아님 |
| **미확인** | vLLM 엔진 자체 로그 | `disable_log_stats`만 설정. 프롬프트 출력 방지는 GPU 시험 미확인 |
| 해당 없음 | release-gate, synthetic-data, model-lab | 환자 데이터를 거치지 않는 경로(합성·평가 데이터). 로그 호출 grep에 본문 변수 없음 |

### 1-3. 보존 기간과 삭제 경로

| 데이터 | 기본 보존 | 삭제 경로 | 판정 |
| --- | --- | --- | --- |
| survey 세션 문서·턴·`session_meta`·`session_timeline`·`risk_signals` | **무기한**. `SURVEY_SESSION_RETENTION_DAYS` 미설정이면 아무것도 안 지움(`retention.py`) | `python -m survey_service purge`(수동 run-once). **`deploy/config/jobs.yaml`에 잡 없음**, `survey.env`에 값 없음 → 운영에서 호출하는 주체 없음. 끝난(ENDED_*) 세션만 대상: 위험 정지(PAUSED_RISK)로 방치된 세션은 영구 | **문제 H-5** |
| `staff_access_log`·알림 행 | 무기한(접근 기록은 의도적으로 안 지움) | 없음 | 접근 기록은 정상. 알림 행은 sid만 담아 L |
| survey Trace outbox | SENT 24h, PENDING 무기한(상한 20000건 넘으면 새 Trace 버림), **DEAD 무기한** | DEAD 삭제 코드 없음, 자동 재전송 없음 | **문제** (H-5 일부, L-8) |
| ops `ops_log` 원본 | **무기한**(`raw_days: null`, 사용자 결정 전) | `purge_received_before`는 `raw_days`가 있을 때만 | **문제 H-5**. 비식별 실패(`DEID_FAILED`) 원본도 남음 |
| ops `ops_failure`(비식별 FailureCase·trace) | 무기한 | **삭제 API 없음**(불변 레코드) | 비식별이 맞다면 허용 범위이나 M-3·M-5 |
| 검토자 입력(`reviewed_input`·`expected`) → 데이터셋·학습 | 무기한 | 없음 | M-5 |
| 백업 | `BACKUP_RETENTION_DAYS` 필수·값 미정 | `pg-backup.sh`가 보존일 지난 것 삭제(최근 1건 유지) | 값 정해질 때까지 미정. 암호화 없음 |
| gateway 로그 | json-file 10MB×5 | 회전 | 의도 없는 단기 보존 |
| 푸시 구독(직원 브라우저 endpoint) | 무기한 | `DELETE /v1/staff/push-subscriptions`, 410 GONE 시 자동 삭제 | 정상 |

### 1-4. 비식별 판정

- **일어나는 곳**: ops-feedback `deid.py` 한 곳. 방식(허용목록, 스키마 걷기, 잔존 패턴 실패 시 닫힘, 정책이 지목한 정의가 스키마에서 사라지면 닫힘)은 견고하다. session_id·turn_id는 salt 기반 결정적 가명(`p-…`), `case_id`도 가명 파생.
- **일어나지 않는 곳**: 키오스크→gateway→survey→모델→PG→outbox→ops_log 전 구간은 원문. 백업도 원문. 직원 콘솔 `GET /v1/staff/sessions/{id}`는 원문 대화를 낸다(의도).
- **한계**: (a) 허용 키 중 `repeat_key`는 `SlotRef.repeat_key`가 자유 문자열(`TurnTrace.json`)인데 평문으로 남는다. 서비스가 이 값을 문항 세트의 `repeat_keys` 목록과 대조하는지는 읽은 코드에서 확인하지 못했다(미확인) → 환자 답변이 키로 새면 마스킹되지 않는다. (b) 잔존 패턴은 이메일·전화·주민번호 3종뿐(이름·주소·병원 번호 없음). (c) 가명이 결정적이라 salt가 새면 session_id 역추적 가능(salt는 파일 비밀, OK). (d) `created_at`에 수집 시각이 남는다.
- **비식별을 안 거치는 환류 입력**: 검토자가 쓴 `reviewed_input`·`expected`·`note`는 "개인정보 없이 직접 고쳐 쓴 입력"이라는 신뢰에 맡긴다(`review.py` 주석, 스키마 검증만).

## 2. 임무 2 — 신뢰 경계와 인증 체계 (B 횡단)

### 2-1. 토큰·역할 한 장

발급은 모두 `deploy/scripts/gen-secrets.sh`(서비스 토큰·DB 암호·salt)와 `gateway-lib.sh`·`kiosk-add-device.sh`(직원 계정·기기 토큰). 값은 읽지 않았다(비밀 파일 미열람). 비밀은 파일로 마운트(D84, `docker inspect` 환경에 값 없음 설계).

| 토큰·계정 | 역할 | 발급 | 검증하는 곳 | 가진 곳 |
| --- | --- | --- | --- | --- |
| 키오스크 기기 토큰(기기마다 파일) | 환자 키오스크 | `kiosk-add-device.sh` | **gateway** `@device_ok`(`devices.caddy`) | 기기(메모리), gateway 설정 |
| 직원 기본 인증 계정(`staff`·`operator`·`release-approver`·`reviewer`, `gateway-accounts.conf`는 계정당 역할 1개) | 사람 | `gateway-lib.sh` | **gateway** `(authenticate)`+`@role_*` | 사람, gateway |
| `survey-api-kiosk` | kiosk | gen-secrets | survey `PublicApi._role` | gateway, survey |
| `survey-api-staff` | staff | 〃 | survey | gateway, survey |
| `survey-result-reader` | result-reader | 〃 | survey | survey만(소비자 없음) |
| `survey-risk-source` | risk-source | 〃 | survey | survey만(호출자 없음) |
| `gate-{read,write}-release-approver`, `gate-{read,write}-operator` | 승인자·운영자 | 〃 | release-gate `GATE_{READ,WRITE}_TOKENS` | gateway |
| `ops-read-reviewer`, `ops-review-reviewer` | 검토자 | 〃 | ops-ingest `OPS_READ_TOKENS`·`OPS_REVIEW_TOKENS` | gateway |
| `gate-read-survey-service`, `gate-read-model-serving`, `gate-{read,write}-ops-feedback` | 서비스 간 | 〃 | release-gate | survey / model-serving / job-ops-feedback |
| `ops-ingest-survey-service` | Trace 쓰기 | 〃 | ops-ingest `OPS_INGEST_TOKEN` | survey, ops-ingest |
| `ops-read-question-authoring` | I7 읽기 | 〃 | ops-ingest | question-authoring |
| `inference-survey-service` | 추론 호출 | 〃 | model-serving `MODEL_RUNTIME_TOKENS` | survey |
| `qa-read-release-gate`, `model-registry-read-release-gate` | I1·I3 읽기 | 〃 | question-authoring / model-registry | release-gate |
| `qa-author-tokens`(`토큰:actor-id:역할`), `qa-read-tokens` | 저자·읽기 | 〃 | question-authoring | **누구도 닿지 못함**(§2-4 E2) |
| `model-registry-{read,write}-tokens` | 읽기·게시 | 〃 | model-registry | release-gate(읽기), model-lab(쓰기, 컴포즈 밖) |
| DB 계정 5개(서비스마다 별도, 슈퍼유저 아님, `10-roles.sh`)·`deid-salt` | 데이터 | 〃 | PostgreSQL scram | 각 서비스 |

### 2-2. 판정

- **기본 거부(B1)**: gateway는 `/v1/*` 끝에서 404, 키오스크 API는 기기 토큰 없으면 401, `/v1/staff/*`·`/intervention`·`/admin`·운영·검토 경로는 인증+역할 뒤. 서비스 쪽도 경로마다 역할을 묶는다(survey `_handle`: 역할 불일치 403, 설정 안 된 역할 경로는 404). 기본 경로(`handle {}`)는 정적 키오스크 화면으로 **무인증**(설계).
- **내부 면 비공개**: `risk-signals`·`results`는 gateway에서 404(`@internalsurvey`), E2E 5r이 단언(`e2e_steps.py:873`). 우회해도 survey가 kiosk 토큰은 403으로 막는다(2중).
- **권한 상승 경로**(확인한 범위): (a) 기기 토큰 → survey kiosk 토큰으로 교체되므로 직원 경로 불가(survey가 role 불일치 403, `e2e_steps.py:625`). (b) 직원 계정 하나는 한 역할(설정 형식)이라 승인자·운영자 겸임 없음. (c) gateway가 모든 읽기·쓰기 토큰을 한곳에 쥔다: gateway 침해 = 전 역할 침해(설계 한계, 승인자 쓰기 토큰 포함). (d) `staff` 계정은 **모든 환자의 발화 전문·subject_ref**를 읽을 수 있고 담당 범위·사유 제한이 없다(M-2). (e) 모든 키오스크가 같은 서비스 토큰을 쓰고 session_id만 알면 어느 세션이든 `turns/end/state` 접근이 가능하다(ID가 96비트 무작위라 실질 위험은 낮음, L-6). (f) 검토자 한 명이 `CONFIRMED`+`expected`를 게시하면 시드로 흘러 학습 입력이 된다(두 사람 확인 없음, 시드 이후 게이트·승인자가 최종 방어선).

### 2-3. `X-Openit-User` 처리 (gateway가 지우거나 덮어쓰는가)

| gateway 경로 | 처리 (`Caddyfile`) | 서비스 쪽 | 시험 |
| --- | --- | --- | --- |
| 키오스크 `/v1/sessions*` | `header_up -X-Openit-User`(**삭제**) | 개입이 아니면 무시 | 시험 직접 단언 못 찾음 |
| 직원 `/v1/staff/*`, `/intervention` | `header_up X-Openit-User {http.auth.user.id}`(**덮어씀**) | 개입은 헤더 없으면 401, 형식 검사 | E2E 5r: 위조 헤더 실어도 인증 계정 기록(`e2e_steps.py:889`) |
| 승인 읽기·쓰기 | 덮어씀 | release-gate가 `approver_id`로 사용, **헤더 없으면 본문 `approver_id` 폴백**(L-2) | E2E 4g 위조 단언(`:381`) |
| 운영자 읽기·쓰기 | 덮어씀 | 헤더 없으면 401 | 위조 단언 못 찾음(L-10) |
| 검토 읽기·쓰기 | 덮어씀 | `reviewed_by`, 헤더 없으면 토큰 역할명 | 위조 단언 못 찾음(L-10) |
| `/admin/*`, `/staff/*` 정적, 기본 경로 | 지우지 않음 | 정적 서버가 무시 | 해당 없음 |

판정: Caddyfile 코드로는 **전 경로에서 클라이언트 값을 지우거나 덮어쓴다**(확인). E2E 단언은 승인·개입 두 경로뿐.

### 2-4. gateway 우회·직접 호출 경로

- 호스트 포트는 gateway만 연다(`compose.yaml`, 기본 `127.0.0.1:8080`). 다른 서비스는 `ports` 없음(확인). `compose.test.yaml`은 서비스를 `127.0.0.1` 임의 포트로 연다(시험 전용, 운영에 섞이면 직접 호출 가능). `compose.registry.yaml`은 `127.0.0.1:5000`, `registry:2`라 **인증·TLS 없음**(주석). `compose.inference.yaml`은 추론 서버를 **기본 `0.0.0.0`** 으로 연다(L-1과 H-6).
- 컨테이너 네트워크: survey-service는 `edge`·`serving`·`db-survey`, kiosk-frontend·admin-console은 `edge`. 정적 컨테이너가 survey-service에 닿을 수 있으나 토큰이 없고 `/healthz`·`/readyz`만 무인증이다. **survey `/readyz`는 무인증으로 릴리스 ID·위반 통계·규칙 적중 수·outbox DEAD 원인을 낸다**(내부망 한정, L-1).
- `edge`·`serving`은 `internal: true`가 아니라 survey-service·model-serving에서 **외부로 나가는 길(egress) 제한이 없다**(원본 발화를 가진 서비스, L-1).
- 도달성 구멍(인증이 아니라 길 자체): model-registry(`release` 내부 네트워크만), question-authoring(`authoring` 등 컨테이너 네트워크만, gateway 경로 없음)에는 GPU 서버(F1)·저자(E2)·synthetic-data(F3)가 닿을 길이 정의되어 있지 않다(FAULT_MATRIX E2·F1·F3 F8 `?N`과 일치).

### 2-5. FAULT_MATRIX 간선 대조 (인증 수단)

범례: ◎ 토큰/암호 인증 있음, △ 의도적 무인증·한정, ✕ 인증 빠짐 또는 연결 없음, `-` 네트워크 호출 아님.

| 간선 | 인증 | 비고 |
| --- | --- | --- |
| A1 키오스크→gateway | ◎ 기기 토큰 | 평문 HTTP |
| A2 gateway→survey | ◎ 서비스 토큰 교체 | A2 F7(토큰 불일치) 정의 PU뿐 |
| A3 gateway→kiosk-frontend | △ 무인증 정적 | 설계. `/config.json`로 기기 토큰을 두면 누구나 읽음(compose는 마운트 안 함, L-7) |
| A4 survey→model-serving | ◎ Bearer | 평문 |
| A5 survey→PG | ◎ scram, 서비스별 계정 | 평문(TLS 안 켬, `RUN.md`) |
| A6 survey→ops-ingest | ◎ | DEAD는 `/readyz`로 노출, 경보 소비자 없음 |
| A7 survey→release-gate | ◎ | |
| A8·B2·C5·F2·G1 볼륨 | - | |
| A9 survey→웹 푸시 | △ VAPID 서명 | **VAPID 파일이 compose에 없음 → 푸시 꺼짐**. 구독 endpoint가 임의 https URL이면 서버가 POST(L-4) |
| A10 직원 SSE | ◎ 기본 인증+staff 토큰 | |
| B1 model-serving→release-gate | ◎ | |
| B3 model-serving→HuggingFace | △ 공개 다운로드 | 무결성 검증 방식은 미확인 |
| B4 외부 추론 | ◎ Bearer만 | **TLS 없음, 기본 0.0.0.0**(H-6) |
| C1·C2·C3 | ◎ | |
| C4·D1·D4·E1 PG | ◎ | |
| C6 스케줄러→docker | △ 호스트 docker.sock | 호스트 권한 |
| C7 승인 화면 | ◎ 기본 인증+역할+토큰 | |
| C8 운영자 | ◎ | |
| D2 job→release-gate 읽기 | ◎ | |
| **D3 job→release-gate 롤백** | ✕ **연결 없음, 그런데 쓰기 토큰(`gate-write-ops-feedback`)은 job에 마운트됨** | 쓰지 않는 쓰기 권한 보유(L-3) |
| D5 QA→ops-ingest | ◎ | |
| D6 검토자 | ◎ | |
| **E2 저자→question-authoring** | ✕ 도달 경로 없음 | 토큰은 정의됨, 길이 없음 |
| **F1 model-lab→model-registry** | ✕ 도달 경로 없음 | 〃 |
| **F3 synthetic-data→QA·ops** | ✕ 도달 경로 없음 | 〃 |
| G2 로컬 레지스트리 | ✕ 인증·TLS 없음 | 127.0.0.1 한정, 이미지 공급망(B9) |
| G3 백업 | - | 암호화 없음 |
| G5 외부 감시→/healthz | △ 무인증 의도 | |
| **G7 병원·감지기→survey 내부 면** | ◎ 토큰 있음, **호출자 없음** | `risk-source` 호출자 없음이 H-1의 원인 |
| 모든 서비스 `/healthz`·`/readyz` | △ 무인증 | survey `/readyz` 정보량 큼(L-1) |

인증이 **빠진** 간선: G2(레지스트리), 그리고 인증 수단은 있으나 소비 길이 없는 E2·F1·F3·G7. 인증된 간선 중 TLS가 있는 것은 하나도 없다.

## 3. 임무 3 — 환자 안전 (I 횡단)

### 3-1. 환자에게 가는 문구의 출처

| # | 출처 | 만드는 곳 | 검토 | 임시 표시 | 비고 |
| --- | --- | --- | --- | --- | --- |
| 1 | 모델 응답(LoRA-B `respond`) | model-serving | 런타임 검증은 **비어 있지 않음**뿐(`protection.py` J1). 금지 표현 필터 없음. 사전: 평가 보고서(`forbidden_expression_rate` 등)를 승인자가 본다. 문장 단위 검토 없음. E2E의 지표는 가짜 값(`e2e_steps.py:301-303`) | 없음 | M-7 |
| 2 | 모델 대체 문장 | model-runtime `fallback.py`(재료 `known·ask·hold·next.text` 이어 붙임) | 없음 | `empty_fallback_text` "죄송합니다. 다시 한 번 말씀해 주세요."는 **"잠정"** 주석(`protection.py:25`) | 재료가 없는 END 등에서도 같은 문장 |
| 3 | 재료 문장(`known/ask/hold`) | survey `response_tables.py` + `schema/data/response_tables.json` | "**데이터셋 담당 확인 대기**(표 승인 기록 미확인)", 서비스 쪽 판단 `remaining_text` | 문서에 확인 대기 표시 | 환자 답변을 되짚는 문장이라 오류 시 잘못된 확인 문구 |
| 4 | 문항 세트 문장(질문·안내·거절 설명·`reask_sentence`) | question-authoring → 게이트 | `ClinicalSafety` 검사: 그 버전에 `clinical_basis_approved=true`인 APPROVED 검수 기록 필요(`checks.py`) | - | |
| 5 | 문항 세트 **고정 문장**(`RISK_NOTICE`·`CALL_STAFF`·`RESUME`·`SURVEY_STOPPED`) | 〃 | 위 검수에 포함되나, 분류표가 `fixed_sentences`를 `(TEXT, False)`로 둬 **변경해도 CLINICAL_REVIEW 후속 작업이 안 생긴다**(`classify.py:39`; `risk_phrases`는 True). 키가 없으면 문장 없음 → 단계 실패(`n_respond`) | - | M-8 |
| 6 | 키오스크 고정 문구(`main.ts`: 시작·말씀해 주세요·다시 말씀해 주세요·직원이 곧 도와드립니다·직원을 불러 주세요 4종·연결 느림·저장하지 못했어요 등) | kiosk-frontend | 없음 | **연결 느림 문구만** 코드·문서에 "임상 문구가 아닌 임시 UI 문구"(`main.ts:31`, `design.md:36,48`). 나머지는 표시 없음 | M-8 |
| 7 | 재개 문장(`resume_text`) | survey(RESUME 고정 문장) → 상태 API | 4와 같음 | - | 키오스크가 상태를 폴링해야만 받는다. H-2에서는 폴링을 시작하지 않음 |
| 8 | 오류 응답(`UPSTREAM_UNAVAILABLE` JSON, `BoundaryError`) | gateway·survey | 환자 화면에 **보이지 않는다**(키오스크는 상태 코드로 분기해 고정 문구로 대체, `flow.ts fail`) | - | 깨진 본문(A1·A2 F6) 처리는 `?N`(FAULT_MATRIX) |
| 9 | 음성 합성(speechSynthesis) | kiosk | 읽어 주는 것은 `LISTENING`·`REPEAT_PROMPT` 문구뿐. **`CALL_STAFF`·`WAITING_STAFF` 문구는 음성 안내 없음**(`main.ts`) | - | M-10 |

### 3-2. 위험 신호 경로가 끊기는 지점

| ID | 끊기는 곳 | 원인·조건 | 환자 화면 | 직원 | 근거 |
| --- | --- | --- | --- | --- | --- |
| R1 | **입력원 없음(G01)** | `SURVEY_RISK_RULES_FILE`·`SURVEY_RISK_SOURCE` 미설정, v2 `ActionExtraction`에 위험 필드 없음 | 정상 진행 | 알림 없음 | E2E 5d: "숨이 안 쉬어져요"·"가슴이 너무 아파요"에도 세션 ACTIVE·알림 없음(`e2e_steps.py:950-957`). `/readyz staff_alert_source.active=false`. check-health는 이 값을 읽지 않음(`check_health.py` grep 0건) |
| R2 | **저작된 위험·한도 필드 미소비** | `risk_phrases`·`risk_rule`·`ask_limit`·`confirm_limit`·`unrecognized_streak_limit`를 survey 코드가 참조하지 않음(grep 0건; turn-engine CR-003 "risk-phrases-unused"). 반복 질문 상한 `SURVEY_MAX_CONSECUTIVE_REASK` 기본 0(꺼짐), `survey.env`에 없음 | 같은 질문 무한 반복 가능 | 호출 없음 | H-1 |
| R3 | 외부 감지기 호출자 없음 | `POST …/risk-signals`는 gateway 404, 내부에서 `survey-risk-source` 토큰으로만. 호출자 미배포(G7) | - | - | 〃 |
| R4 | **규칙 감지가 추출 성공 뒤에만** | `risk_source.check`가 `n_plan_writes`(검증 통과 후)에서만 호출. `extract` 2회 실패·`OUTPUT_INVALID`·검증 위반이면 건너뜀 | "다시 말씀해 주세요" 류 | 없음 | H-4 |
| R5 | **쓰기 확정 실패** | DB 중지·응답 없음·`commit` 실패 | `NOT_COMMITTED` → "저장하지 못했어요. 다시 말씀해 주세요" | **없음** (`staff_alert: NONE`, 알림은 확정 뒤에만) | `survey/docs/boundary.md` "위험 알림도 나가지 않는다"; 사용자 결정 대기 |
| R6 | **턴 총 마감 6초 초과** | 느린 모델·DB | `NOT_COMMITTED` | 없음(`_deadline_outcome`: `staff_alert NONE`) | `orchestrator.py` |
| R7 | **정지 성공 후 키오스크 상태 어긋남** | 서버: 알림 전달 성공 시 `turn_failure_signal=null`(`graph._signal`, 시험 `test_staff_alerts.py:464`). 키오스크: `DELIVERED` 신호에서만 `WAITING_STAFF`(`flow.ts handle`). 모의 서버 시나리오만 `DELIVERED`를 준다(`design.md:78`) | `RISK_NOTICE` 문장 + **"말씀해 주세요"·"말하기"·"그만하기"** 유지. 정지 중 발화는 응답·신호 모두 null(`n_ignore`) → 무응답 | 알림은 감 | H-2. 실서버 조합 시험 없음 |
| R8 | 정지 상태에서 환자가 "그만하기" | `_end`는 `PAUSED_RISK`도 받고 `_resolve_ended`가 열린 알림을 **결정 없이 RESOLVED** | 종료 화면 | 열린 알림 목록에서 사라짐(SSE `resolved` 이벤트) | `api.py _end/_resolve_ended`. 설계 가정("이탈하면 직원이 할 일 없음")이 위험 환자에는 맞지 않을 수 있음(H-2) |
| R9 | **푸시 미구성** | VAPID 비밀이 compose에 없고(`secrets` 목록 확인), 웹 푸시·서비스 워커는 보안 출처(HTTPS) 필요 → 평문 gateway에서는 사실상 불가(`Caddyfile` 주석 "STT·웹 푸시는 보안 출처 필요, 미정") | - | 전달 경로가 SSE 하나 | M-9 |
| R10 | **SSE 구독자 0** | 직원 콘솔(`/staff/`)이 아무 브라우저에서도 안 열려 있음, 탭 절전, 로그아웃, gateway `read_timeout 1h`로 끊긴 사이 | `DELIVERY_FAILED` → `CALL_STAFF` 화면("가까이 있는 직원에게 알려 주세요") | 알림은 DB에 `OPEN`으로 저장(목록에서만 조회) | `AlertService.raise_alert` |
| R11 | **SSE 반개방 연결** | 서버는 쓰기 실패 전까지 구독자로 셈 → `DELIVERED` 오판(`survey/docs/STATUS.md:85` 알려진 한계) | 대기 화면 | 못 받음 | M-9 |
| R12 | **직원 콘솔에 소리·진동 경보 없음** | `apps/staff` grep에 audio/vibrate 없음. 푸시 꺼져 있으면 화면을 보고 있어야 인지 | - | 화면 주시 필요 | M-9 (추정: 콘솔 UI 전체를 읽지는 않음) |
| R13 | **알림 DB 장애** | 알림·세션이 같은 PostgreSQL. 알림 저장 실패 = 전달 실패 | `DELIVERY_FAILED` 또는 R5 | 없음 | `alerts.raise_alert` |
| R14 | `CALL_STAFF` 화면 자체 | "처음으로" 버튼이 있고 음성 안내가 없음. 누르면 `IDLE`로 돌아가 다음 환자 화면 | 사라짐 | 알림 `OPEN`만 남음 | M-10 |
| R15 | **gateway 504 뒤 늦은 확정(N22)** | gateway가 504로 끝낸 요청을 survey가 뒤늦게 처리, 키오스크는 예산 소진으로 직원 호출 화면 | 직원 호출 화면 | 위험 알림이 뒤늦게 갈 수는 있으나 환자 화면과 불일치 | FAULT_MATRIX N22 |

### 3-3. 위험 환자가 아무에게도 알려지지 않는 조합 (시나리오)

모든 시나리오는 **현재 배포 구성**(R1)을 전제로 하면 첫 번째가 이미 성립한다. 아래는 R1을 해소(규칙 파일 또는 감지기 연결)했다고 가정한 뒤에도 남는 것까지 나열한다.

1. **현 구성 그대로**: 환자가 "가슴이 아파서 숨을 못 쉬겠어요"라고 말한다. 입력원이 없어(R1·R2·R3) 세션은 정상 진행, 모델이 되묻는 질문을 한다. 직원도 환자 화면도 변화 없음. E2E 5d가 같은 문장 계열로 확인.
2. **규칙은 켰지만 모델이 흔들릴 때**(R4): 위험 문구가 들어간 발화에서 LoRA-A가 두 번 형식을 어긴다. 규칙 검사는 추출 성공 뒤라 실행되지 않는다. 환자는 "다시 말씀해 주세요"를 듣는다. 같은 발화를 반복해도 같은 결과가 나올 수 있다.
3. **DB 지연·장애 중**(R5·R6·R13): 위험 발화가 들어오고 쓰기 확정이 실패한다. 알림은 확정 뒤에만 만들어지므로 없다. 키오스크는 같은 turn_id를 최대 20초 재시도하다 "가까이 있는 직원에게 알려 주세요"로 간다(음성 없음, R14). 환자가 화면을 못 보거나 "처음으로"를 누르면 아무도 모른다.
4. **직원 콘솔을 아무도 안 열었을 때**(R10·R9·R12): 알림은 저장되고 환자는 `CALL_STAFF` 화면을 본다. 직원이 콘솔을 열지 않았고 푸시가 꺼져 있으면 알림은 `OPEN`인 채 방치된다. 환자가 화면을 닫으면 끝.
5. **정지는 됐는데 환자가 이탈**(R7·R8): 알림이 SSE 하나에 닿고 세션은 `PAUSED_RISK`. 키오스크는 "말씀해 주세요" 화면에 머물고(R7) 환자는 말해도 응답이 없어 "그만하기"를 누르거나 자리를 떠난다. "그만하기"는 알림을 `RESOLVED`로 닫는다(R8). 직원이 그 순간 화면을 보지 않았다면 열린 알림 목록에서도 사라진다.
6. **반개방 SSE + 푸시 없음**(R11): 서버는 `DELIVERED`로 기록하고 키오스크는 대기 화면 또는 H-2의 화면에 머문다. 직원 브라우저는 이미 끊겨 있다.
7. **gateway 504 후 키오스크가 직원 호출 화면으로 이탈**(R15): 환자는 안내를 받고 떠나지만 알림은 뒤늦게(또는 중복 없이) 저장된다. 직원 쪽 인지가 늦다.

환자 쪽에서 위험이 **드러나는** 조합은 전달 실패(R10)가 `DELIVERY_FAILED`로 키오스크에 신호될 때뿐이다. 그 외는 모두 침묵이다.

## 4. 발견 목록 (심각도순)

판정 표기는 `AUDIT_CHECKLIST.md`를 따른다. "자율"은 헤드·영역이 사용자 결정 없이 고칠 수 있다는 뜻.

### H

| ID | 항목 | 문제 | 근거 | 제안 | 결정 |
| --- | --- | --- | --- | --- | --- |
| H-1 | I1·I3 | 입력원 없음 + 저작 필드 미소비 + 반복 상한 꺼짐 | §3-2 R1·R2·R3 | 입력원 결정(CR-012); 소비되지 않는 필드(`risk_phrases` 등)는 저작 화면과 승인 화면에 "런타임 미사용"을 드러내거나 제거; check-health가 `/readyz staff_alert_source.active`를 읽게 한다 | 사용자 결정(입력원·상한 값). 표시 추가는 자율 |
| H-2 | I3 | 정지 성공 신호 null ↔ 키오스크 `DELIVERED` 가정; 정지 중 무응답; 그만하기가 알림을 자동 해결 | R7·R8; `graph._signal`, `flow.ts handle`, `api._end` | 서버가 정지 성공도 신호/상태로 알리거나 키오스크가 응답 후 `/state`를 확인; 정지 중에는 그만하기를 숨기거나, 위험 정지 세션의 이탈은 알림을 해결하지 않음; 실서버 조합 시험 추가 | 알림 해결 정책은 사용자 결정, 계약 정렬은 헤드(survey·kiosk 양쪽 변경 요청) |
| H-3 | I3 | 확정 실패·마감 초과에 위험 알림 없음 | R5·R6 | `FAULT_POLICY`의 사용자 결정 항목. 위험 판정은 확정과 분리해 먼저 알림을 보내는 안을 결정 | 사용자 결정 |
| H-4 | I3 | 규칙 감지가 모델 성공에 종속 | R4; `graph.n_plan_writes` | 규칙 검사를 추출 전(발화 수신 직후)으로 옮기거나 추출 실패 경로에서도 실행 | 입력원 결정 뒤 survey가 자율 수정 가능 |
| H-5 | C3 | 원본 보존 무기한, 삭제 경로 불완전 | §1-3 | `jobs.yaml`에 survey purge 잡, `raw_days`·세션 보존일·DEAD 보존 값을 사용자가 정함; PAUSED_RISK 방치 세션 처리; outbox DEAD 정리 | 값은 사용자 결정(O16). 잡 배선은 자율 |
| H-6 | B8·C5 | 평문 HTTP | §2-4, §2-5 | 운영 TLS 종단(도메인·인증서) 결정 전까지 `GATEWAY_BIND`를 열지 말 것; 외부 추론 모드는 TLS 또는 터널 필수; 서비스 간 TLS 필요성 판단 | 사용자 결정(도메인·인증서) |

### M

| ID | 항목 | 문제 | 근거 |
| --- | --- | --- | --- |
| M-1 | C6 | 직원 열람 접근 기록에 개인 ID 없음: `staff_access_log`는 역할 이름만(`api._audit(role,…)`, `X-Openit-User` 미전달). 개인 ID는 gateway 컨테이너 로그(회전)에만. 열람은 원문 대화 전체 | `api._staff_session` |
| M-2 | B2 | `staff` 계정이 모든 환자 세션·subject_ref를 열람(담당·사유 제한 없음) | `api._staff_session`, Caddyfile 직원 블록 |
| M-3 | C4 | 비식별 허용키 `repeat_key`가 자유 문자열로 평문; 잔존 패턴 3종뿐; `repeat_key`가 문항 세트 목록과 대조되는지 미확인 | `deid.py`, `deploy/config/ops-feedback-job.yaml`, `TurnTrace.json SlotRef` |
| M-4 | C4 | 검토자 자유 입력(`reviewed_input`·`expected`·`note`)에 PII 검사 없음, 그대로 학습 시드 | `review.py`, `seeds.py` |
| M-5 | C3 | FailureCase 불변·삭제 API 없음, 시드·데이터셋 환류 후 철회 경로 없음 | `failurestore`, `seeds.py` |
| M-6 | 환류 | `signals.py`가 v2 TurnTrace에 없는 `planner_output.directive`를 읽어 문항 단위 개선 신호가 항상 건너뛰기(`NO_QUESTION_ID`). 검색: `TurnTrace.json`에 `planner_output` 0건. 실행은 안 해 봄 | `question_authoring/signals.py:35` |
| M-7 | I2 | LoRA-B 출력은 비어 있지 않음만 검사, 금지 표현 필터·문장 검토 없음; 게이트 지표 값은 E2E에서 가짜 | `protection.py J1`, `e2e_steps.py:301-303` |
| M-8 | I2 | 고정 문장 변경이 임상 검토 후속을 안 만듦; 대체 문구 잠정; 키오스크 고정 문구 대부분 임시 표시 없음 | `classify.py:39`, `protection.py:25`, `main.ts` |
| M-9 | I3 | 전달 경로 SSE 하나(푸시 꺼짐·HTTPS 없음), 반개방 연결 오판, 콘솔에 소리 경보 없음(추정) | R9·R11·R12 |
| M-10 | I3 | `CALL_STAFF` 화면 음성 없음, "처음으로"로 해제 가능; 알림 `OPEN` 방치 | `main.ts` |
| M-11 | B10 | gateway Basic 인증·기기 토큰에 속도 제한·잠금 없음(Caddyfile에 없음) | `Caddyfile` |
| M-12 | C1 | 브라우저 STT가 음성을 벤더 서버로 보낼 수 있음; 동의·문서 없음 | `stt.ts`, `brief.md:52` |
| M-13 | C7 | 백업에 원본 포함, 암호화 없음, 보존일 미정(필수 입력이지만 값 없음) | `pg-backup.sh:5`, `backup.env.example` |
| M-14 | C8 | 원본(`ops_log`)을 비식별 처리기만 읽는다는 규칙(D15)이 코드 수준뿐; ingest 서버와 job이 같은 DB 계정·DSN | `compose.yaml`(두 서비스 모두 `db-ops-log-dsn`), `logstore.py` |

### L

| ID | 항목 | 문제 |
| --- | --- | --- |
| L-1 | B11·F1 | survey `/readyz` 무인증 상세 정보; `edge`·`serving` 네트워크 egress 제한 없음; 추론 서버 compose 기본 `0.0.0.0` |
| L-2 | B1 | release-gate `decide`는 헤더가 없으면 본문 `approver_id` 사용(survey 개입·운영자는 401). 직접 호출 시 승인자 위조 가능 |
| L-3 | B12 | job-ops-feedback에 쓰기 토큰 `gate-write-ops-feedback` 마운트(롤백 연결 없음) |
| L-4 | B6 | 웹 푸시 구독 endpoint가 임의 https URL이면 서버가 POST(허용 도메인 제한 없음). 접근은 staff 역할 |
| L-5 | B3·F5 | 토큰 파일 644(폴더 700); 직원 계정 암호가 `tokens/account-*-password`에 평문 |
| L-6 | B2 | 모든 키오스크가 같은 서비스 토큰, 기기 ID 어디에도 기록 안 됨(추적 불가), 기기 폐기에 gateway 재시작 필요 |
| L-7 | B1 | 기본 정적 경로가 무인증이라 `/config.json`에 기기 토큰·subject_ref를 두면 노출(현 compose는 마운트 없음 → 현재 영향 없음) |
| L-8 | A6 | outbox 상한 초과 시 새 Trace 유실, DEAD 자동 재전송 없음, 경보 소비자 없음(알려진 한계) |
| L-9 | E1 | ops-ingest `log.exception` 스택 트레이스 전체 출력(본문 포함 경로는 못 찾음) |
| L-10 | H4 | gateway의 `X-Openit-User` 덮어쓰기 E2E 단언이 승인·개입 두 경로뿐(운영자·검토 경로 없음) |

## 5. 확인한 좋은 점 (근거 있는 OK)

- 환자 발화·값이 survey·model-runtime·ops-feedback 로그에 직접 나가지 않는다(전수 grep).
- 알림·푸시 본문에 발화·개인정보가 없다(`StaffAlert` 스키마, `_push` 페이로드).
- 접근 기록 fail-closed(결과 조회·직원 세션 조회: 기록 못 남기면 데이터 안 줌).
- 개입의 행위자는 헤더가 정본이고 헤더가 없으면 401, 본문 `staff_id`는 버린다.
- DB 계정은 서비스별 분리·슈퍼유저 아님, 네트워크도 서비스별 내부망(`db-*`).
- 컨테이너 비root·`cap_drop ALL`·읽기 전용 루트·`no-new-privileges`(gateway만 `NET_BIND_SERVICE`).
- 비식별은 허용목록+실패 시 닫힘+정책/스키마 불일치 시 닫힘.

## 6. 읽지 못한 곳·확인 못 한 것

- **비밀**: `deploy/secrets/` 전체(`tokens/`, `gateway-accounts.caddy`, `gateway-devices.caddy`), `.env`, `~/.docker/config.json`, SSH 키는 열지 않았다. 따라서 토큰 값·해시 알고리즘·`@device_ok`의 비교 방식(상수 시간 여부)은 확인 못 함. `config/gateway-accounts.conf`는 계정명·역할만 있어 읽었다.
- **실행하지 않음**: 어떤 시험도 돌리지 않았다. E2E 결과(`E2E_RESULTS.md`)는 읽지 않았고, FAULT_MATRIX의 E/U 주장은 그 문서에 적힌 것을 인용했을 뿐 재확인하지 않았다.
- **Caddy 동작**: `handle` 블록의 매칭 순서(`/v1/sessions/*/intervention` 대 `/v1/sessions/*`), 경로 정규화 우회 가능성은 Caddyfile을 읽은 추론이며 실행 확인이 아니다(E2E가 일부 단언).
- **admin-console**, **model-lab**, **synthetic-data**, **release-gate** 내부는 환자 데이터 로그 grep, 인증 코드 일부, 승인 경로만 봤다. 영역 안쪽 점검은 다른 에이전트 몫.
- **vLLM 엔진 로그**의 프롬프트 출력 여부(GPU 필요, 소스에도 "GPU 시험에서 확인"으로만 적힘).
- **브라우저 STT 전송 실태**(브라우저·OS 의존).
- **`repeat_key`가 문항 세트 목록으로 검증되는지**(turn-engine·survey 검증 코드를 끝까지 읽지 못함).
- **직원 콘솔 UI 전체**(알림 시 소리·강조 표시)는 파일 목록과 grep만 봤다.
- **`INTERFACES.md`·`CONVENTIONS.md`·`METRICS.md` 전문**, `deploy/docs` 대부분, `scripts/check_health.py` 본문은 필요한 부분만 grep으로 봤다.
- **TLS 종단·운영 도메인·병원 IdP(OIDC)**: 문서가 "미정"이라 현황 자체가 없음.
