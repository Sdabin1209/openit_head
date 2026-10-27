# 2차 독립 점검: release-gate / ops-feedback / question-authoring (수정분)

점검일 2026-10-28. 대상: 각 리포의 2026-10-28 03:50 이후 커밋. 읽기 전용. 재현은 영역 `.venv`의 python으로 함수를 직접 호출했고 임시 파일은 스크래치패드에만 두었다. 영역 코드·설정·문서는 수정하지 않았다.
표기: **확정** = 재현했거나 코드로 직접 확인. **추정** = 코드를 읽고 한 판단, 재현 안 함.

## 요약

| 영역 | H | M | L |
|---|---|---|---|
| release-gate | 0 | 1 | 5 |
| ops-feedback | 0 | 2 | 5 |
| question-authoring | 0 | 0 | 6 |

H 없음. M 제목:
- [release-gate M1] prune이 계획과 삭제 사이에 활성화된 릴리스를 지운다(활성 포인터가 PRUNED 릴리스를 가리킴). 삭제 직전 보호 재확인 없음
- [ops-feedback M2] 검토 게시(expected/note/reviewed_input)의 이메일 PII 패턴이 제곱 시간이다: 인증된 검토자 하나가 큰 본문으로 서버 전체를 멈출 수 있다
- [ops-feedback M3] `retention.cases_purge_confirmed: "false"`(문자열)가 검증을 통과해 참으로 처리된다: 확정(CONFIRMED) 사례가 삭제된다. 잡 기본(삭제)과 admin purge 기본(보존)도 서로 다르다

---

## release-gate

### [release-gate, M, M1] prune이 활성화 경쟁에서 활성 릴리스를 지운다
- 근거: `release_gate/retention.py` `prune()` (plan_bundles로 보호 집합을 계산한 뒤 `apply`에서 `prune_release_files`를 보호 재확인 없이 호출), `store.py` `prune_release_files`. 활성화(`gate.py activate`)는 `verify_in_tempdir` 뒤 포인터를 바꾸므로 prune과 상호 배제가 없다.
- 재현(확정, 인터리빙을 순서대로 실행): 릴리스 5개, 활성=rels[4], keep=1. plan_bundles가 [rels[0..2]]를 돌려준 뒤 운영자가 그중 하나를 `activate`하고, 이어 계획 목록 전체에 `prune_release_files`를 실행. 결과: 활성 포인터의 release_id가 `is_pruned == True`. (스크래치패드 `/tmp/claude-1000/-home-user-sdabin-healthKiosk/239a6438-b51c-4422-840e-8503c4b1368d/scratchpad/rg/test_r2.py` `test_prune_race_activate_pruned`)
- 영향: 읽기 SDK가 활성 번들을 못 읽는다(FAILED_PRECONDITION PRUNED). 어댑터 사본은 복구 수단이 없다(원본은 훈련 서버 쪽에만).
- 같은 뿌리의 확정 사항: `GATE_RETAIN_KEEP_RELEASES=0`이 허용되어(retention.py `v < 0`만 거부) 방금 승인돼 아직 활성화 전인 최신 릴리스도 plan_bundles 대상이 된다(`test_keep0_new_release_pruned`로 확인). 승인→활성화 사이에 prune이 돌면 활성화가 PRUNED로 실패.
- 제안: (a) `prune_release_files` 직전에 `protected_ids`를 다시 계산해 보호 대상이면 건너뛴다. (b) 삭제를 "PRUNED 표시 먼저 쓰기 → 포인터가 그 릴리스를 가리키면 되돌림" 같은 순서로 하거나 `activate`/`switch_pointer`가 PRUNED 표시를 확인하게 한다(포인터 전환 트랜잭션과 같은 락). (c) keep_releases 최소를 1로 올리거나 "승인됐으나 한 번도 활성화되지 않은 릴리스"를 보호. 
- 자율 수정 가능: 예(영역 내부). 포인터 전환 쪽 변경은 ADR 0004와 0009 갱신 필요.

### [release-gate, L] 임시 디렉터리 정리의 mtime 휴리스틱
- 근거: `store.py purge_stale_tmp` — `.tmp-*`/`.bundle-*`를 최상위 디렉터리 mtime이 1시간을 넘으면 삭제. 디렉터리 mtime은 직계 항목을 만들 때만 바뀌므로 하위로 계속 쓰는 긴 복사·다운로드(1시간 이상)는 "오래됨"으로 보인다. 추정: 현실적으로 드문 크기에서만. 영향은 해당 승인 요청 실패(재시도 가능), 손상은 없음.
- 제안: 하위 최신 mtime을 보거나 상한을 설정으로. 자율 수정: 예.

### [release-gate, L] prune과 제자리 읽기(검증·번들 tar)의 경쟁
- 근거: `reader.py verify_release(dest=None)`/`write_bundle_tar`가 릴리스 디렉터리를 제자리에서 읽는다. 해시 계산 중 또는 tar 스트리밍 중 prune의 `rmtree(adapters)`가 겹치면 INTEGRITY_ERROR(오해를 부르는 코드) 또는 응답 도중 끊김. 추정(재현 안 함). 보호 대상(활성·직전)은 prune이 건드리지 않으므로 보호되지 않은 릴리스를 명시 활성화/롤백할 때만 해당. M1의 재확인으로 대부분 해소.
- 제안: read_release_parts에서 PRUNED 표시와 어댑터 부재를 구분해 FAILED_PRECONDITION(PRUNED)으로 돌려주기(rmtree와 PRUNED 쓰기 사이 틈: 어댑터 없음+PRUNED 없음 → 현재는 `adapters`에 역할이 빠져 INTEGRITY_ERROR). 자율: 예.

### [release-gate, L] 해시 검증 TOCTOU(제자리)
- 근거: 검증 후 포인터 전환 사이, 그리고 검증 후 tar 전송 사이에 파일이 바뀔 수 있다. 이전(복사본 검증)도 소비자가 나중에 읽는 원본과의 사이에는 같은 틈이 있었고 소비 쪽(클라이언트)이 해시를 다시 확인한다고 문서에 있다. 릴리스 디렉터리에 쓰기 권한이 있는 주체(같은 컨테이너/볼륨)만 악용 가능하므로 새 위험 증가는 작다. 확정: 새로 생긴 틈은 아니고 검증 강도는 같다(같은 해시 함수).
- 제안: 문서(ADR 0003)에 "검증은 시점 검사이고 소비자가 재검증"을 명시. 자율: 예.

### [release-gate, L] 깊게 중첩된 JSON 본문
- 근거: `app.py _body`가 `ValueError`만 잡는다. `json.loads`의 `RecursionError`(1MiB 한도 안에서 `[[[[…`)는 `_run`의 `except Exception`으로 가서 500(INTERNAL)+스택 로그. 서비스는 죽지 않음. ops-feedback은 같은 문제를 이번에 고쳤다(`RecursionError` 처리). 추정(재현 안 함).
- 제안: `(ValueError, RecursionError)`로 400. 자율: 예.

### [release-gate, L] 종료 순서
- 근거: `main.py run_until_signal` — 요청 대기 후 `loop.stop_event.set()`만 하고 Loop 스레드를 join하지 않은 채 `store.close()`. 주기 작업(process_pending)이 판정 커밋 중이면 닫힌 연결 예외가 로그에 남고, 프로세스 종료 시 daemon이라 중단됨. SQLite/PG 트랜잭션은 원자적이라 손상은 없다. 승인 요청 중 종료(grace 20초 초과)는 `.tmp-*`/행 없는 디렉터리 잔재가 남을 수 있으나 다음 생성/정리에서 치워진다(코드로 확인). 추정.
- 제안: Loop join(상한) 뒤 close. 자율: 예.

### 관점별 확인(발견 없음 또는 문제 없음)
- 승인 X-Openit-User 필수(401), 본문 approver_id 불일치 400: 코드 읽기로 확인(`app.py` 333~346). 헤더는 `_ID` 형식 검사 뒤 `decide(approver_id=user)`로 본문을 덮는다. 인증 실패/401이 반려 판정으로 기록되지 않음: `process_pending`이 PERMISSION_DENIED를 즉시 올리고 `_reject`를 거치지 않는다(코드 확인). 시도 기록은 유효한 쓰기 토큰만.
- 락 밖 번들 복사: `_stage_release`는 고유 이름(.tmp-rid-uuid)으로 만들고, 락 안에서 행 삽입→rename→커밋 순서. 동시 같은 릴리스 승인은 UNIQUE 위반(CONFLICT)로 한쪽만 이긴다(코드 확인, 동시 실행 재현은 안 함). 행 없는 디렉터리 찌꺼기는 다음 생성에서 `rmtree(final)` 뒤 rename. 원자적 교체 불변식(읽기는 행 기준)은 유지된다.
- 계약: HTTP.md 68행이 CR-0008 내용을 이미 반영. 단 `boundary_contracts.clients.HttpGateService`가 X-Openit-User를 못 보내 SDK 승인 호출은 401이 된다(CR-0008에 기록됨, 미해결).

---

## ops-feedback

### [ops-feedback, M, M2] 검토 PII 패턴(이메일)이 제곱 시간
- 근거: `review.py DEFAULT_REVIEW_PATTERNS["email"] = [A-Za-z0-9._%+-]+@…`를 `rx.search`로 문자열 전체에 적용. '@'가 없는 긴 영숫자 열에서 시작 위치마다 끝까지 훑는다. `api.py MAX_BODY = 8 MiB`.
- 재현(확정): `re.search(email, "a"*N)` N=20k 0.18s, 40k 0.70s, 80k 2.81s(제곱). 8 MiB 한 문자열이면 수 시간 단위로 외삽(추정). Python `re`는 GIL을 놓지 않으므로 서버 전체(수집 POST 포함)가 멈춘다. 요청 소켓 timeout(30초)은 CPU 시간을 끊지 못한다.
- 전제: 검토 토큰 보유자(인증됨). 위협은 오조작/내부자 또는 토큰 탈취.
- 같은 패턴은 `config/job.example.yaml`의 `residual_patterns.email`에도 있다. 잡의 잔존 검사는 마스킹 뒤 결과에 적용되고 keep 값은 64자 이하로 제한되어 현재는 큰 문자열이 남기 어렵다(추정). 설정으로 다른 키를 keep에 넣으면 같은 문제.
- 제안: 길이 한도(검토 필드당 예: 4096자, 초과면 400)를 패턴 검사 앞에 두고, 패턴을 길이 제한 형태로(`[A-Za-z0-9._%+-]{1,64}@…`, question-authoring이 쓴 방식). 자율: 예.

### [ops-feedback, M, M3] `cases_purge_confirmed` 문자열이 참으로 해석되고 기본이 서로 다르다
- 근거: `config.py`가 불리언 검사를 `purge_unprocessed`에만 한다(`for flag in ("purge_unprocessed",)`). `job.py:205`는 `include_confirmed=ret.get("cases_purge_confirmed", True)`.
- 재현(확정): 예시 설정에 `cases_purge_confirmed: "false"`를 넣어 `load_config` → 통과, 값 `'false'`, `bool()`은 True → 잡이 CONFIRMED 사례(학습 정답)를 180일 뒤 삭제. 이번 수정이 `auto_submit` 문자열을 막은 것과 같은 부류의 누락.
- 부가: 잡 기본은 확정 사례도 삭제(True), `admin purge`는 기본 보존(`--include-confirmed` 필요). 문서(STATUS 77행, ADR 0007)는 위험을 명시했으나 두 경로의 기본이 다르다.
- 제안: `("purge_unprocessed", "cases_purge_confirmed")` 모두 불리언 강제. 확정 사례 삭제 기본을 False로 바꾸거나(학습 소비 전 삭제 위험) 최소한 경고 목록(`retention_warnings`)에 "확정 사례도 삭제됨"을 넣기. 기본값 변경은 사용자 결정(D88 U4)이므로 값 변경은 헤드/사용자 몫, 불리언 검증은 자율 가능.

### [ops-feedback, L] `purge_received_before(processed_only=True)`가 재처리 대기 원본을 지운다
- 근거: `logstore.py` — `processed_only`는 `status IS NOT NULL`. `DEID_FAILED`/`PUBLISH_FAILED`도 상태가 있어 "처리됨"으로 센다(`MINIMIZABLE` 주석에서 이 둘이 재처리 대상임을 스스로 밝힘). raw_days(기본 30) 뒤 재시도 가능한 원본이 조용히 삭제된다. 개인정보 최소화 관점에서는 의도일 수 있으나 "처리 안 된 원본을 지우지 않는다"는 설명(admin docstring, job 주석)과 다르고 경고도 없다. 확정(코드).
- 제안: 문서에 명시하거나 `status IN ('DONE_CASE','NO_FAILURE')`로 한정하고 실패 상태는 별도 기한/경고. 자율: 예(동작 선택은 사용자).

### [ops-feedback, L] 고아 trace 삭제와 잡의 경쟁
- 근거: `failurestore.py purge_cases_created_before` — 사례가 참조하지 않는 모든 trace를 지운다(나이 무관). 잡은 `put_trace` 뒤 사례를 쓰므로(job.py 145~154) 다른 프로세스의 admin purge가 그 사이에 돌면 방금 쓴 trace를 지워 사례가 dangling이 될 수 있다. 같은 잡 프로세스 안에서는 순차이므로 영향 없음. 추정.
- 제안: 고아 삭제에 최소 나이 조건(예: 1시간)을 둔다. 자율: 예.

### [ops-feedback, L] `delete-session` 한계
- 근거: `admin.py delete_session` — 비식별 trace 조회가 `session_id`가 `pseudonymize_keys`에 있다는 전제(`session_pseudonym`)다. 예시 설정은 그렇지만 정책이 다르면 실패 저장소는 아무것도 못 지우고도 오류 없이 `cases:0,traces:0`을 낸다. dry-run은 `raw_rows`를 0으로 낸다(세지 않음). 범위 자체(다른 세션 삭제 여부)는 문제 없음: 원본은 `session_id=?` 정확 일치, trace는 의사 식별자 정확 일치. 지운 원본의 중복 키가 사라져 같은 턴이 재수집되면 다시 들어온다(docstring에 명시됨).
- 제안: 정책에 session_id 의사화가 없으면 오류로 종료, dry-run에서 raw 건수 세기. 자율: 예.

### [ops-feedback, L] 우회 스위치와 허용 목록의 한계
- `OPS_REVIEW_REQUIRE_USER=0`으로 검토자 신원 필수를 끌 수 있다(api.py main). CR-0008이 "끄는 스위치가 운영에 남으면 위조 위험이 되살아난다"며 release-gate에 두지 않은 판단과 반대다. 확정(코드). 제안: 시험 전용 표시로만 허용하거나 /readyz 경고.
- 비식별 허용 목록 합성 시험(확정): 전체 일치(`fullmatch`)이고 ASCII 문자 집합이라 부분 일치 통과, 전각 문자(`Ｑ1`), 개행 변형(`q1\n`, `q1\nHong`), 한글 이름, 공백 포함 값은 모두 차단. 식별자 모양의 영문 이름(`JohnSmith`, `Hong.Gildong`, 대문자 `KIM`을 code로)은 통과한다(docstring에 한계로 명시). `repeat_key`는 빈 문자열 허용. 문서와 일치.
- 위조 Trace→롤백: CR-006에 한계가 정직하게 기록됨(출처 인증 불가). 현재 보호는 `auto_submit` 기본 false+불리언 강제+`evidence_refs`. 변경 없음, 헤드 결정 대기.
- SIGTERM: `api.py`는 `srv.shutdown()`만 호출하고 처리 중 요청을 기다리지 않는다(`daemon_threads=True`). 쓰기가 단일 문장 자동 커밋이라 손상은 없다(주석과 일치).

### 관점별 확인
- 보존 기본값 시작 거부: `raw_days/cases_days/metrics_days` null, 0, 음수, 불리언, 문자열(forever 외) 거부 확인(코드). 기존 `raw_days: null` 설정은 이제 시작 거부(의도된 비호환, 문서화됨).
- 검토 게시 X-Openit-User: `_ID.fullmatch`(개행 우회 없음), 없으면 PERMISSION_DENIED. 정상.
- 로그 위조: `JsonFormatter`로 이스케이프. `/readyz`는 코드와 건수만, 비밀 없음.

---

## question-authoring

### [question-authoring, L] gateway 사용자 ID 형식 불일치
- 근거: `http_api.py _principal`은 사용자 ID에 `@`를 허용(`[A-Za-z0-9._:@-]`)하지만 `service.py _ID`(`_auth`)는 `@`를 거부한다.
- 재현(확정): `user_roles={"bob@hosp.kr":"clinical-reviewer"}`, gateway 토큰으로 `GET /v1/drafts` → 400 `actor.id 형식이 아니다`. `bob`은 200.
- 영향: 이메일형 ID를 쓰는 gateway에서는 모든 쓰기·검수가 막힌다(안전하게 실패, 기능 문제). 어떤 ID를 쓰는지는 이 영역이 확인하지 못함(추정).
- 제안: 두 정규식을 한 상수로 통일(이메일형을 허용할지 결정). 자율: 예.

### [question-authoring, L] 보존 정리 경쟁
- 근거: `store/base.py purge` — 보존 대상(`keep`) 집합을 계산한 뒤 나중에 삭제하고, 원본 `put_source`는 `INSERT OR IGNORE`라 이미 있는 같은 해시의 `created_at`을 갱신하지 않는다. 오래된 미참조 자료와 같은 파일을 다시 올리면 `put_source`(created_at 그대로) → 초안 저장 사이, 또는 keep 계산 후 새 초안이 생긴 사이에 purge가 겹치면 새 초안이 가리키는 자료가 삭제된다. 확정(코드 순서), 시간창은 좁다.
- 버전·검수·변경 분류는 지우지 않음(확인: `_version_source_hashes`가 보호, 버전/검수 테이블은 purge 대상 아님). OPEN/DISCARDED 초안만 삭제, CONFIRMED는 보존.
- 제안: 재업로드 시 created_at 갱신 또는 삭제를 조건부(DELETE … WHERE NOT EXISTS 참조)로. 자율: 예.

### [question-authoring, L] SIGTERM 설명과 동작이 다르다
- 근거: `__main__.py` 주석 "진행 중 요청을 마치고 멈춘다". 실제로는 `srv.shutdown()`뒤 `server_close()`이고 `ThreadingHTTPServer.daemon_threads=True`라 처리 중 스레드를 기다리지 않는다. 확정(코드). confirm 도중이면 `confirming` 예약만 남고(다음 호출이 복구 경로로 푼다) 손상은 없다.
- 제안: 주석 수정 또는 in-flight 카운트 대기. 자율: 예.

### [question-authoring, L] 보존 CLI가 운영 구성 검사를 거치지 않는다
- 근거: `main(["purge"])`는 `build()`가 아닌 `open_store()`를 바로 호출한다. QA_DATABASE_URL이 빠지면 조용히 빈 SQLite(`/data/…`)를 열어 `0 removed`를 내고 성공 종료한다. 정리가 안 도는 것을 못 알아챈다. 확정(코드).
- 제안: 운영 모드(QA_DEV_MODE 아님)에서는 DB URL 없으면 purge도 거부. 자율: 예.

### [question-authoring, L] 환자 정보 탐지의 거짓 경고
- 재현(확정, 경고 전용): `2024-01-02 1234567`(날짜 뒤 7자리)과 `Q-02 1234 5678`, `031 123 4567`이 "유선전화 형태"로 경고. 설계 의도(D88 U5 "놓치는 것보다 거짓 경고")와 일치하므로 결함 아님, 저자 피로도 관찰 사항. ReDoS 없음: 2MB 입력 9종(0 반복, 공백/하이픈 반복, '@' 반복, 점 반복, +82 반복 등) 모두 0.5초 미만.
- 비UTF-8은 NON_UTF8_WARNING으로 알림. NFKC로 전각 변형을 흡수.

### [question-authoring, L] 선형 파서 회귀(임의 입력 비교)
- 방법: 옛 정규식과 새 코드를 같은 입력에 비교. `_KV`(키:값 분할) 30만 임의 문자열에서 차이 0. 전제 조건(`<문항>.<슬롯> = <값>`)은 30만 중 24건 차이: 슬롯 이름이 `=`를 포함하고 뒤에 비ASCII 공백이 오는 등 비현실적 입력(예 `..===　\xa0qq`)이며 옛 정규식의 역추적으로만 맞던 경우다. 일반 양식(`q1.slot = 5`, `a==5`, 슬롯에 점 포함)은 동일.
- 위험 기준(`risk_rule`)은 공백 덩어리를 한 칸으로 줄인 뒤 매칭하므로 값 안의 연속 공백이 단일 공백으로 바뀐다(예 `>= 38  이상 즉시`). 값에 공백이 의미 있는 경우는 보기 어렵다. 확정(코드), 영향 작음.
- 예시 양식 `examples/question_form.txt` 결과 동일성은 직접 비교하지 않았다(아래 못 본 곳).

### 관점별 확인(4-eyes 등)
- 역할 이름: 정확 일치(`clinical-reviewer`). 대소문자 변형은 거부되는 쪽으로 실패(안전). 토큰 파싱에서 역할이 ROLES에 없으면 시작 거부.
- 같은 주체: `add_review`가 이 버전의 AUTHOR_CONFIRMATION `reviewer_id`와 `actor.id`가 같으면 거부. 다른 ID를 가진 같은 사람은 코드로 막을 수 없다(구성 책임). 저자 확인은 `clinical_basis_approved = not require_two_person`이라 4-eyes 모드에서 False.
- 정적 토큰 요청의 X-Openit-User: 재현(확정) — `Bearer st` + `X-Openit-User: bob`이 `alice`(question-author)로 처리, 헤더 무시. gateway 토큰만 헤더를 신뢰하고, 사용자 표에 없으면 None.
- 초안 소유(`_own`): created_by와 다르면 거부(4-eyes 모드). `require_two_person=False`에서는 해제되며 /readyz에 `two_person_disabled` 경고가 뜬다.
- 운영 구성 거부: DB URL·토큰이 있고 gateway 토큰이면 `QA_USER_ROLES` 필요. 정상 구성(Postgres+저자 토큰)을 막지 않는다(코드). smoke는 QA_DEV_MODE=1을 준다. Dockerfile의 `QA_DB_PATH` 기본값은 운영 모드에서 쓰이지 않는다.
- 사소: `_dlock`의 `_draft_locks` 딕셔너리가 인증된 호출의 서로 다른 draft_id마다 늘어나고 줄지 않는다(추정, 인증 후만).

---

## 읽지 못했거나 얕게 본 곳
- 동시성은 코드 읽기 위주다. release-gate의 동시 승인·활성화·롤백을 스레드로 실제 겹쳐 돌리지 않았다(M1은 순서를 직접 실행해 확인한 시뮬레이션). PostgreSQL 경로(`postgres_store.py`, `PostgresFailureBackend`, question-authoring postgres)는 SQLite와 같은 형태임을 diff로만 확인했고 실행하지 않았다.
- release-gate: ADR 10편, `docs/*`와 코드의 일치는 일부만 대조(승인 헤더, 보존 항목). 활성화·롤백의 `X-Openit-User` 서비스 역할 예외는 변경분 밖이라 깊이 보지 않았다.
- ops-feedback: `deid.py`의 residual 검사 구현과 `detect.py`, `rollback.py` 전체 흐름은 diff 범위만 읽었다. 비식별 우회는 정규식 단위 합성 시험이며 `Deidentifier.deidentify` 전체를 합성 TurnTrace로 돌리지는 않았다. 위조 Trace→롤백은 CR-006과 코드의 `auto_submit` 검사만 확인.
- question-authoring: 예시 양식 전체를 옛 코드와 새 코드로 돌려 결과(번들)를 비교하지 않았다(옛 파일은 스크래치패드에 저장해 두었으나 전체 추출 비교는 하지 않음). `store/postgres.py`와 `memory.py`의 purge 구현, `tests/*`는 읽지 않았다.
- deploy/gateway가 클라이언트가 보낸 X-Openit-User를 지우는지(세 영역 모두의 신뢰 전제)는 이 점검 범위 밖이라 확인하지 않았다.
- boundary-contracts는 HTTP.md의 승인 절만 확인했다. PUBLIC_API.md는 읽지 않았다.
