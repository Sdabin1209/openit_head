# 2차 독립 점검: UI·모델·계약 수정분 (2026-10-28 03:50 이후 커밋)

읽기 전용 점검. 코드·설정·문서는 수정하지 않았다. 재현은 영역 .venv/node로 함수·서비스를 직접 불러 확인했고, 임시 파일은 스크래치패드에만 썼다.
"확정"은 실제로 돌려서 확인한 것, "읽어서 확인"은 코드를 읽고 판단한 것, "추정"은 확인하지 못한 것이다.

## 요약

| 리포 | H | M | L |
| --- | --- | --- | --- |
| kiosk-frontend | 1 | 1 | 5 |
| admin-console | 0 | 0 | 2 |
| model-runtime | 0 | 2 | 4 |
| model-lab | 0 | 2 | 2 |
| synthetic-data | 0 | 0 | 2 |
| boundary-contracts(문서) | 0 | 1 | 1 |
| turn-engine(ADR) | 0 | 0 | 0 (깊게 보지 않음) |

H
- K-1 [kiosk-frontend] 직원 호출 화면(CALL_STAFF)이 유휴 60초 뒤 처음 화면으로 돌아간다. 직원 알림 전달 실패(DELIVERY_FAILED)도 포함된다.

M
- K-2 [kiosk-frontend] 세션 시작이 실패하면 이미 소비된 subject_ref가 사라진다. 다음 시작은 접수 참조 없이 간다.
- MR-1 [model-runtime] run_session.sh가 쓰기 허용 폴더 검사보다 먼저 `--work` 경로를 만든다(~/dabin 밖에 디렉터리 생성).
- MR-2 [model-runtime] `--clean-cache`가 `$WORK/cache`를 통째로 지운다. 이 경로는 실행 사이에 공유되고, 미리 있던 같은 이름의 폴더도 지운다.
- ML-1 [model-lab] 인증 실패 제한이 출발지 주소 단위라서, 틀린 토큰 몇 번이면 같은 주소의 정상 호출자까지 잠긴다(확정).
- ML-2 [model-lab] SIGTERM 우아한 종료가 유휴 keep-alive 연결 하나만 있어도 약 30초 걸린다. Docker 기본 정지 시간(10초)보다 길다(확정).
- BC-1 [boundary-contracts 문서] "토큰이 없거나 틀리면 401"이라는 새 규약이 같은 문서의 고정 표(PERMISSION_DENIED=403)와 실제 서비스(403)와 어긋난다.

(M 개수: 표의 값은 영역별 소계. MR-1·MR-2는 model-runtime, ML-1·ML-2는 model-lab.)

---

## kiosk-frontend

### K-1 [H] 직원 호출 화면이 유휴 초기화로 사라진다 (확정)
- 근거: `apps/kiosk/flow.ts` armIdle()은 `LISTENING | REPEAT_PROMPT | CALL_STAFF`에 타이머를 건다. CALL_STAFF이면 `this.reset()`을 부르고, reset은 세션을 끝내지 않고 화면만 IDLE로 만든다. 커밋 a71d8ff.
- ADR 0008은 "위험 정지 대기에는 적용하지 않는다(세션을 끝내면 위험 환자의 대기가 사라진다)"고 쓰지만, 위험 신호로 멈췄는데 직원 알림 전달이 실패한 경우(DELIVERY_FAILED)가 바로 CALL_STAFF다. 이 화면이 가장 급한데 가장 먼저 사라진다.
- 재현: `/tmp/.../scratchpad/k2.mts`. 목 서버가 두 번째 응답에 DELIVERY_FAILED를 준다. idleMs=300으로 돌렸더니 `t0 CALL_STAFF DELIVERY_FAILED`, 500ms 뒤 `IDLE`, 종료 요청은 0번이었다. 서버 세션은 PAUSED_RISK로 남고 키오스크는 "문진을 시작합니다"로 돌아가 다음 사람이 시작할 수 있다.
- 부수: CALL_STAFF에서 reset하면 열린 서버 세션이 정리되지 않는다(고아 세션).
- 제안: CALL_STAFF는 사유가 DELIVERY_FAILED·AUTH·NO_DEVICE_TOKEN이면 유휴 초기화에서 제외하거나, LONG_WAIT처럼 안내만 덧붙이고 직원이 "처음으로"를 누를 때까지 유지한다. 시험 추가: 유휴 타이머가 CALL_STAFF/DELIVERY_FAILED를 건드리지 않음.
- 자율 수정: 가능(키오스크 영역 코드, 임상 값 변경 아님). 단, 어떤 사유에서 화면을 유지할지는 U10과 같은 임상 판단이라 헤드 확인을 권한다.

### K-2 [M] subject_ref가 시작 실패 때 소비된다 (확정)
- 근거: `api/device.ts` createStartHolder.take()가 요청 전에 참조를 비운다. `flow.ts` start()는 take 뒤에 서버 호출을 한다. 시작이 실패하거나(503 소진, 400, 환자가 중간에 "직원 호출") 하면 같은 환자가 "처음으로"를 눌러 다시 시작해도 참조가 없다.
- 재현: `k1.mts`. 첫 시작이 400으로 CALL_STAFF/START_FAILED, 같은 홀더로 reset 후 다시 시작하면 본문에 subject_ref가 없고 `startNotice=NO_SUBJECT_REF`.
- 부수(읽어서 확인): `/config.json`에 subject_ref를 두는 기기는 새로고침하면 홀더가 새로 만들어져 같은 참조가 다시 한 번 나온다. "한 번 쓰면 비운다"는 보장이 새로고침에서 깨진다.
- 제안: 소비 시점을 "서버가 세션 시작을 수락한 뒤"로 옮긴다(실패하면 되돌려 놓기). 이웃의 접수 연동 방식은 사용자 확인 대기이므로 그 결정 전까지의 보수적 기본값으로만 둔다.
- 자율 수정: 가능.

### K-3 [L] 상태 확인 조회가 정상 턴을 최대 약 20초 붙잡는다 (읽어서 확인)
- 근거: flow.ts hear()는 위험 신호가 없는 모든 정상 응답 뒤에 `getSessionState`를 부른다. 이 호출은 일반 재시도 정책(예산 20초, 시도당 10초)을 쓰고 `onRetry`를 넘기지 않아 `retrying` 표시도 없다. 조회가 막히면 이미 받은 정상 응답을 화면에 못 보인다. 실패하면 "정지 아님"으로 진행하므로 틀린 결과는 아니고 지연만이다.
- 제안: 이 확인은 재시도 1회·짧은 timeout(예: 2초)으로 따로 건다.

### K-4 [L] 길이 자르기가 서로게이트 쌍을 가를 수 있다 (확정)
- 근거: hear()의 `.slice(0, MAX_INPUT_CHARS)`와 `input.maxLength`는 UTF-16 단위다. 499자 뒤에 이모지가 오면 `"\ud83d"` 단독 서로게이트가 JSON으로 나간다(재현: 직렬화 결과 끝이 `\ud83d`). 이런 문자열은 서버에서 UTF-8로 바꿀 때 오류가 날 수 있다(추정, 서버는 안 돌려 봤다). 같은 turn_id 재시도도 같은 문자열을 보낸다. STT가 500자를 넘기면 말한 뒤쪽이 조용히 잘리는 점도 같다.
- 제안: 코드 포인트 단위로 자르고(`Array.from`), 잘렸다면 안내한다.

### K-5 [L] 로컬 STT 초기화에 시간 상한이 없다 (읽어서 확인)
- 근거: stt.ts init()은 `available()`이 지원하지 않으면 건너뛰어 안전하다. 그러나 `install()`이 끝나지 않으면 `ready`가 영원히 false이고, 그동안 화면은 "이 기기에서는 음성 인식을 쓸 수 없어요"를 보인다(내려받는 중인데 불가로 안내). 지원 판정 API(`available`) 자체가 없는 브라우저는 예외 없이 음성이 꺼지고 글자 입력으로 간다(문제 없음).
- 제안: install에 상한(예: 30초)을 두고, 진행 중 문구를 따로 둔다.

### K-6 [L] 유휴 초기화 경로의 부수 문제 (읽어서 확인)
- 유휴 만료는 `end().then(reset)`이라 ENDED 화면이 바로 IDLE로 덮이고, 종료 요청 실패(`endFailed`) 안내가 보이지 않는다.
- reset 때 마이크 인식(`stt.cancel`)을 부르지 않아, 말하기 중에 초기화되면 인식이 끝날 때까지 마이크가 켜져 있다. 결과는 IDLE에서 버려진다.

### K-7 [L] /config.json 노출 범위 (읽어서 확인)
- 근거: `server/static.mjs`가 CONFIG_FILE을 `/config.json`으로 아무 헤더 검사 없이 낸다. 같은 서버가 `/staff/`도 내므로 직원 브라우저와 같은 출처에서 읽힌다. 기기 토큰과 subject_ref가 들어 있을 수 있다. 코드 주석은 "gateway 몫"이라 적었다(문서화됨). 서버 로그에는 내용이 안 남는다(확인).
- 기기 토큰이 URL/저장소로 새는지: 조각은 읽은 뒤 `replaceState`로 지우고 메모리에만 둔다. 요청 헤더는 `/sessions*` 경로에만 붙는다(client.ts). localStorage/sessionStorage 사용은 보지 못했다.
- 제안: deploy 쪽에서 `/config.json`을 기기(키오스크 IP)만 읽게 하고, 그 요구를 deploy에 변경 요청으로 남긴다.

### 문제 없음으로 본 것
- api/validate.ts: 문진 스키마 FrontendInput/TurnFailureSignal(`response_text` 빈 문자열 금지, `additionalProperties:false`는 검사하지 않음)과 SessionState(`state`, `resume_text` 필수)와 일치. 정상 응답을 거부하는 경로는 못 찾았다. 응답에 모르는 필드가 있어도 통과한다(읽기 모드와 일치).
- 재시도·turn_id: 같은 발화 텍스트만 같은 turn_id를 재사용. `end()`가 진행 중 요청을 abort해도 서버는 같은 turn_id로 멱등이라 이중 전송 경로는 찾지 못했다.
- 위험 정지 대기(WAITING_STAFF)는 유휴 초기화 대상이 아니다(확인). 입력 중에는 `input` 이벤트가 타이머를 다시 센다(확인).

### 얕게 본 곳
- SSE 재연결·heartbeat 감시(api/staff.ts, apps/staff/sync.ts)는 03:50 이전 커밋이라 diff에 없어 이번에는 읽지 않았다. 타이머 누수·이중 연결은 판단하지 못했다.
- 브라우저에서 실제 실행(Playwright/E2E)은 하지 않았다.

---

## admin-console

### A-1 [L] 응답 대조가 정상 재생 응답을 "서버 응답 이상"으로 보일 수 있다 (추정)
- 근거: `api/client.ts` 승인 응답에서 `a.report_hash`가 있으면 요청의 `report_hash`와 같아야 한다. HTTP.md는 같은 제출·같은 결정의 재전송에 200으로 기존 결과를 돌려준다고 하는데, 보고서가 바뀐 뒤 재전송할 때 서버가 STALE_REPORT(409)를 줄지 기존 승인(옛 report_hash)을 줄지는 계약에 순서가 없다. 후자라면 정상 재생이 BAD_RESPONSE 알림으로 보인다. 서버는 읽지 않았다.
- 제안: 재생(200)일 때는 report_hash 대조를 생략하거나, 계약에 판정 순서를 적도록 변경 요청.

### A-2 [L] requested_by_role="operator" 고정 (추정)
- 근거: INTERFACES.md는 롤백 허용 역할을 `ops-feedback`·`operator`, 역할은 토큰에 묶인다고 한다. 게이트웨이가 롤백을 `ops-feedback` 토큰으로 중계하면 본문 `operator`와 달라 PERMISSION_DENIED가 된다. CR-004가 operator 계정만 통과시킨다고 했으므로 지금 설계에서는 맞다. 게이트웨이 토큰 매핑은 deploy 쪽이라 확인하지 못했다.
- 확인한 것: 본문 모양은 RollbackRequest 스키마(requested_by_role 필수)와 HTTP.md I5 활성화 본문과 맞는다.

### 문제 없음으로 본 것
- 확인창: 취소가 첫 포커스, Esc는 전송 중에만 막힘. 승인 흐름 회귀는 못 찾았다. 확인 입력은 `setField`가 다시 그리지 않아 타이핑 중 포커스 이동이 없다(확인).
- 본문 읽기 중 timeout, 영수증 대조(`request_id`, 대상 릴리스)는 정상 응답을 거부하지 않는다(스키마 읽음).

### 얕게 본 곳
- 테스트와 mock-server 변경, ADR 본문은 읽지 않았다. main.ts의 `needFocus`(h2 포커스)와 ops-view의 포커스 이동이 한 번 겹치는지는 실행하지 않았다.

---

## model-runtime

### MR-1 [M] `--work`를 만든 뒤에 쓰기 허용 폴더를 검사한다 (확정)
- 근거: `scripts/gpu_session/run_session.sh` `mkdir -p "$WORK"`가 `case "$WORK_REAL/" in "$ROOT_REAL"/*)` 검사보다 앞에 있다.
- 재현: `GPU_SESSION_WRITE_ROOT=<스크래치>/t1/root`, `--work <스크래치>/t1/outside/deep`. 스크립트는 "밖이다"로 거부하지만 `outside/deep`이 만들어졌다. 서버의 "~/dabin 밖에는 쓰지 않는다" 규칙에 어긋난다(빈 폴더지만 경로를 잘못 주면 홈 밖에 생긴다).
- 제안: `mkdir` 전에 `realpath -m "$WORK"`로 접두를 검사한다. 자율 수정 가능.

### MR-2 [M] `--clean-cache`가 공유 캐시 폴더를 지운다 (읽어서 확인)
- 근거: `C="$WORK_REAL/cache"`는 실행마다가 아니라 작업 폴더에 하나다. `rm -rf -- "${C:?}"`는 변수가 비었을 때는 막지만, (a) 다른 실행이 같은 `--work`로 동시에 돌고 있으면 그 캐시를 지우고, (b) 사용자가 `--work`로 미리 쓰던 폴더를 주고 그 안에 `cache`가 있으면 그것도 지운다. WRITE_ROOT 안이라 홈 밖은 아니다. `RUN`·`C`는 `:?` 가드가 있고 `rm`은 모두 `--`와 따옴표를 쓴다(확인).
- 제안: 캐시를 `$RUN/cache`로 두거나(대신 재사용 못 함), 이 스크립트가 만든 것만 지우도록 표식 파일을 둔다.

### MR-3 [L] 옵션 값 없이 끝나는 인자에서 무한 루프 (확정)
- 근거: preflight.sh와 run_session.sh의 `--until`/`--work` 같은 옵션이 마지막 인자이면 `shift 2`가 실패하고 인자가 줄지 않아 while이 영원히 돈다. `timeout 3 bash preflight.sh --until` → 종료 코드 124. 해는 없지만 사람이 서버에서 붙잡혀 있게 된다.
- 제안: 옵션마다 `[ $# -ge 2 ] || die`.

### MR-4 [L] 토큰이 curl 인자에 보인다 (읽어서 확인)
- 근거: 준비 대기에서 `curl -H "Authorization: Bearer $(cat "$RUN/token")"`. 공유 서버에서 다른 사용자가 `ps`로 볼 수 있다. 서버는 루프백 전용이라 영향은 작다. 측정 스크립트는 파일로 읽는다.
- 제안: `curl -H @파일`이나 python 한 줄로 바꾼다.

### MR-5 [L] prepare_bundle.py `--release-id ..`와 `--overwrite` (확정)
- 근거: `out = Path(a.out)/a.release_id`를 검증 없이 쓰고 `--overwrite`면 `shutil.rmtree(out)`. 재현: `--out X/inner --release-id .. --overwrite` → `X` 전체(형제 폴더 포함)가 지워졌다. run_session.sh는 이 옵션을 쓰지 않아 자동 경로는 안전하다.
- 제안: release_id를 서버와 같은 `ID_RE`로 검증한다.

### MR-6 [L] 요청 상한 3.5초와 호출자 마감의 체인 (읽어서 확인)
- 호출 하나: 서버 3.5초 < survey 읽기 timeout 4초 로 정합. 한 턴이 extract와 respond 두 번이면 서버 상한의 합(최대 7초)이 턴 마감 6초를 넘지만, 호출자가 먼저 끊는다. 이때 서버는 호출자가 끊은 줄 모르고 엔진을 최대 3.5초 더 잡아 다음 환자의 요청이 큐(3.0초)에서 밀릴 수 있다(추정, 측정 안 함). 수치는 모두 초기값이라고 문서에 적혀 있다.

### 문제 없음으로 본 것
- 인증 기본 닫힘: 토큰 하나(역할 이름 임의)로 PUT·GET·extract·respond가 모두 되며(put_roles 기본 None), `loader`만 추론 거부. survey-service가 404에서 PUT으로 다시 적재하는 흐름을 막지 않는다. Dockerfile이 HOST=0.0.0.0을 주고 HEALTHCHECK는 무인증 /healthz를 쓴다.
- 입력 상한: `len(json.dumps(body, ensure_ascii=False))`는 코드 포인트 수라 한글·이모지를 1로 센다. 학습 데이터 최대(A 643, B 417)의 약 3.9배이고 키오스크 발화 상한(500자)과도 맞는다. 경계 입력을 직접 만들어 2528자를 확인.
- 특수 토큰 이스케이프: `a<b`→`a< b`, `<br>`→`< br>`, `|>`→`| >`로 바뀌고, 숫자 앞 `<`(예: `BP <120`)·한글 앞 `<`는 그대로다. 환자 발화가 실제로 바뀌는 건 `<`+영문자·`|>`인 경우뿐. 모델이 그 문장을 답으로 되돌려 주면 저장되는 값도 바뀌어 있다(영향 작음, 추정).
- SIGTERM: 서버 쪽은 `shutdown()`을 별도 스레드에서 부르고 진행 요청을 5초까지 기다린 뒤 닫는다. 코드 읽기만 했다(실행 안 함).
- GPU 키트가 남의 프로세스를 건드리는 경로: preflight는 읽기만 한다. 종료 대상은 `setsid`로 띄운 서버의 프로세스 그룹(`-$SERVER_PID`)과 자기 하위 프로세스뿐이고 `pkill`/이름 기반 종료가 없다. 단 `kill -KILL -- -$SERVER_PID`는 서버 종료 뒤 PID 재사용을 확인하지 않는다(실제 위험은 매우 낮다고 보지만 추정). 센서 서브셸이 SIGKILL 때 남을 수 있다(L).
- 쓰기 경로: 변수가 비어 `rm -rf`가 위험해지는 경로는 못 찾았다(`${RUN:?}`, `${C:?}`, `set -u`). ~/dabin 밖 쓰기는 MR-1 한 건과, HOME을 바꾸지 않아 환경 변수로 지정하지 못한 라이브러리 캐시가 `~/.cache` 대신 `XDG_*`가 아닌 곳(`XDG_CONFIG_HOME`/`XDG_DATA_HOME`)에 쓸 가능성(추정, 실행 안 함).

### 얕게 본 곳
- measure.py(303줄)는 쓰기 경로만 grep했고 본문은 읽지 않았다. 실제 vLLM 기동은 불가능하다. run_session.sh 전체 실행 시험은 하지 않았다.

---

## model-lab

### ML-1 [M] 인증 실패 제한이 정상 호출자를 잠근다 (확정)
- 근거: `model_lab/service/app.py` `auth_blocked(addr)`이 모든 요청의 인증 앞에서 검사되고 키가 `client_address[0]`이다. 역방향 프록시·Docker 포트 매핑 뒤에서는 모든 호출자가 같은 주소로 보인다.
- 재현: 서비스를 띄우고 틀린 토큰 12번 보냈더니 9번째 이후가 503, 이어서 정상 토큰도 503이었다(60초).
- 영향: 아무나 닿는 곳에서 잘못된 토큰 10번이면 release-gate/게시자도 1분 동안 막힌다. 게시 재시도는 되지만 가용성 공격이 된다. `publisher.remote`에 기록되는 주소도 프록시 주소가 된다(게시자 기록의 값이 줄어듦, L).
- 제안: 제한은 "틀린 토큰을 보낸 요청"만 막고 정상 토큰은 통과시키거나(검사 순서 변경), `X-Forwarded-For`를 신뢰 프록시에서만 쓴다.

### ML-2 [M] SIGTERM 종료가 30초 걸린다 (확정)
- 근거: `_Server`가 `daemon_threads=False`, `block_on_close=True`라 `server_close()`가 모든 연결 스레드를 기다리는데, 유휴 keep-alive 연결은 소켓 timeout(30초)까지 읽기에서 대기한다.
- 재현: 서비스를 띄우고 keep-alive로 `/healthz`를 한 번 받은 뒤 연결을 열어 둔 채 SIGTERM → 30.1초 뒤 종료(코드 0).
- 영향: Docker/compose 기본 정지 시간 10초(deploy 설정은 읽지 못해 추정)이면 SIGKILL로 끝나 게시 중단 잔해가 남는다. 다음 시작의 `recover()`가 지우므로 데이터 손상은 아니다.
- 제안: 종료 신호 뒤에는 새 요청을 받지 않고 유휴 연결은 닫는다(`Connection: close`), 또는 진행 중 게시만 기다리는 상한을 둔다.

### ML-3 [L] 거절 응답도 요청 본문을 끝까지 읽는다 (읽어서 확인)
- 근거: `_fail`이 POST/PUT 실패 때 `_drain`으로 최대 `max_body`(4GiB)를 읽고 답한다. 디스크 부족·동시 게시 초과·인증 잠금(503)도 이 경로라, "받기 전에 거절"이 문서 문구와 달리 대역폭은 다 쓴다. 읽기 timeout이 읽기 한 번당이라 천천히 보내면 오래 붙잡힌다.

### ML-4 [L] 복구가 잠금 밖이다 (읽어서 확인)
- `recover()`가 `.tmp-*`를 지우는데, 같은 저장소 루트를 쓰는 다른 프로세스(CLI 게시)가 쓰는 임시 파일(`_atomic_write`의 `.tmp-` 접두)도 같은 패턴이다. 서비스 시작과 CLI 게시가 겹치면 CLI가 실패한다. 한 저장소를 한 프로세스만 쓰는 전제면 문제 없다.

### 문제 없음으로 본 것
- 게시 원자성: 매니페스트가 마지막 쓰기, `order` 중복 방지, `_s_versions` 중복 제거는 읽어서 맞다. 하드 링크 복사는 같은 루트 아래라 같은 파일 시스템이고 실패하면 복사로 돌아간다.
- 학습 계보 대조(`read_train_record`): 역할·데이터셋·기반 모델·어댑터 파일 해시를 대조한다. 기록이 없으면 경고만이고 막지 않는다(의도됨). 기록이 학습 실행기의 자기 보고라는 한계는 코드에 적혀 있다.
- 서버 코드 해시 비교: UNSET이면 `check_ready`가 통과시킨다(MISMATCH만 거부). 현재 설정에 값이 없으면 비교는 작동하지 않는다.

### 얕게 본 곳
- 디스크 가드(`check_free_space`)는 주입된 free 값으로 읽기만 했고 실제 가득 찬 디스크는 만들지 않았다. train_wrap의 doctor/disk_policy는 읽기만.

---

## synthetic-data

### SD-1 [L] 누수 판정이 엄격한 키라서 같은 발화·다른 state는 잡지 않는다 (읽어서 확인)
- 근거: 허용치 판정은 `input_key`(정규화 발화 + 입력 나머지 전부)다. `utterance_key`(발화+문항/액션)로 센 값은 보고만 한다. ADR 0004는 실제 데이터 8건이 모두 state가 달라 입력·정답이 달랐다고 근거를 댔다. 그러나 평가에서 훈련과 같은 발화를 본 것 자체가 암기 위험이라, 이 기준이 느슨하다는 판단은 데이터셋 담당과 정할 일이다. 구현이 문서와 어긋나는 것은 아니다.

### SD-2 [L] 개인정보 의심 패턴 한계 (확정)
- 행당 20000자까지만 검사한다(그 뒤의 이메일은 놓침, 재현). 구분자 없는 유선 전화(`0212345678`)는 패턴에 없다. 경고 전용이라고 문서에 적혀 있고(`deid_attested=false`), ReDoS 시간은 1000배 입력에서도 0.002초였다.

### 문제 없음으로 본 것
- 사유에 값이 섞이는지: `check_boundary_codes`가 `경로#스키마키워드`만 낸다. 배열 번호는 `*`로 바뀌고 메시지·값은 없다. JSON 오류 문구는 `e.msg`(위치 설명)뿐이다. 중복 scenario_id 사유에서도 예시 값을 뺐다.
- human_review는 스키마 enum이라 `Counter` 키가 해시 불가한 값이 될 수 없다(크래시 경로 없음). 멱등: `version`을 줘도 digest가 같으면 ALREADY_PUBLISHED. `pending_policy`가 digest에 들어가 정책을 바꾸면 다른 버전이 된다.
- 추정(확인 못 함): `pending_policy=exclude`일 때 `counts`와 매니페스트의 `rows_valid`가 제외 전 값일 가능성. 실행해서 보지 않았다.

---

## boundary-contracts 문서

### BC-1 [M] 401/403·429 규약이 실제 서비스와 어긋난다 (확정)
- 근거: `CONVENTIONS.md` 9절(4f62770)이 "토큰이 없거나 틀리면 401, 권한이 없으면 403"이라고 쓰는데, 같은 절의 고정 표는 `PERMISSION_DENIED | 403`이고 "상태 코드는 다음으로 고정한다"이다. 실제 서비스는 토큰이 없을 때도 모두 403이다: model-runtime(`_err("PERMISSION_DENIED")`→403), model-lab 서비스(`STATUS`에 401 없음, 앞의 잠금 재현에서도 403). 승인(D88)만 `X-Openit-User` 없을 때 401이다.
- 같은 곳의 "과다 요청은 429와 `UNAVAILABLE`, `Retry-After`"도 실제와 다르다: model-lab의 인증 실패 제한과 동시 게시 초과는 503(Retry-After 없음), model-runtime의 큐 초과도 503이고 `Retry-After`는 연결 초과 응답에만 있다. 키오스크 클라이언트는 429를 재시도하지만 실제로 429를 내는 서비스는 보지 못했다(읽은 범위).
- 영향: 클라이언트가 401과 403을 구분해 처리하면(예: 키오스크의 AUTH 화면은 둘 다 같게 처리하므로 해 없음) 서비스마다 다르게 동작한다. 문서만 읽는 새 영역이 잘못 구현한다.
- 제안(헤드 몫, boundary-contracts는 헤드 소유): 표에 401을 추가하고 "서비스 영역은 토큰 부재·불일치를 401로 낸다"를 요구하거나, 문서를 현실에 맞춰 "서비스 간 호출은 403, 401은 승인(사람 식별 헤더 없음)뿐"으로 고친다. 429도 같다.
- 자율 수정: 불가(boundary-contracts는 헤드 소유, 변경 요청 대상).

### BC-2 [L] 서비스는 502·504를 내지 않는다는 문장 (읽어서 확인)
- model-runtime·model-lab 코드에서 502/504를 직접 내는 곳은 못 찾았다(문장과 일치). `_guarded`의 예외 응답은 503이다. 다만 gateway가 아닌 서비스가 내는 5xx 중 500이 있는지는 전 영역을 보지 않았다.

---

## turn-engine (ADR만)
- 7편 ADR과 README만 변경. 코드와의 대조는 하지 않았다. 읽지 않음.

## 전체에서 읽지 못했거나 얕게 본 곳
- 학습 서버, 실제 GPU, 실제 브라우저, 컨테이너 빌드·E2E는 실행하지 않았다(제약).
- kiosk-frontend SSE/heartbeat 코드, admin-console 테스트·mock, model-runtime measure.py 본문, synthetic-data 테스트, turn-engine ADR은 읽지 않았거나 일부만 읽었다.
- survey-service 쪽 동작(PUT 재적재, 상태 응답의 실제 모양, 서버 turn_id 멱등 구현)은 경계상 읽지 않아 모두 계약 문서 기준이다.
- 스크래치패드 재현 파일: `/tmp/claude-1000/-home-user-sdabin-healthKiosk/239a6438-b51c-4422-840e-8503c4b1368d/scratchpad/` 의 `k1.mts`, `k2.mts`, `t1`~`t4`.
