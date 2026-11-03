P6 계약 문서 전체 재검토: 바뀐 문장 대조 완료 / 대상 문서 7개(전부 읽음, 문서별 범위는 맨 끝 "읽은 범위") / 결함 17건 (05:20 갱신: 최종본, 진행 수 변경 없음)

대상: boundary-contracts wo-320, 1bbf6dd. 변경 범위 60dc386..1bbf6dd. 앞 구간(60dc386..8021268)의 문장은 이미 같은 날 8021268 판 전체를 읽고 검토 B로 낸 결함(B-01~B-28)의 반영 여부를 대조했고, 8021268..1bbf6dd의 모든 바뀐 줄을 새로 읽었다. 확인한 것과 추정을 구분했다("추정"만 추정).

---

### R6-1 사람 요청의 승인자 식별: HTTP.md는 "release-approver 토큰", CONVENTIONS 6절은 "gateway 역할 토큰"
- 위치: HTTP.md 87행 "서버는 `release-approver` 토큰의 요청에서 이 헤더 값을 승인자로 쓴다" 및 I5 `decide` 행 "쓰기 역할 `release-approver`만" / CONVENTIONS.md 6절(1bbf6dd) "서비스는 `X-Openit-User`·`X-Openit-Roles`·`X-Openit-Device` 를 platform 공개 입구의 서비스 토큰(토큰 역할 `gateway`)이 붙은 요청에서만 쓰고, 그 밖의 토큰으로 온 요청의 같은 이름 헤더는 무시한다. 사람 요청의 권한은 `X-Openit-Roles` 가 정한다".
- 왜 결함: 사람이 승인할 때 상류 토큰은 `gateway` 역할이므로 `release-approver` 토큰은 사람 경로에 존재하지 않는다. HTTP.md 문장대로면 승인 요청에서 헤더를 아무도 쓰지 않고(`gateway` 토큰은 `release-approver`가 아니다), CONVENTIONS 문장대로면 `release-approver` 토큰 요청에서 온 헤더는 무시된다. 두 문장이 승인자를 정하는 방법을 반대로 말한다. 같은 문제가 INTERFACES.md 96행 "호출자가 말한 역할이 토큰의 역할과 다르면 PERMISSION_DENIED"(토큰 기준)와 CONVENTIONS 6절 "헤더 역할과 다르면 PERMISSION_DENIED"(헤더 기준)에도 있다.
- 고칠 문장: HTTP.md 87행 "서버는 `release-approver` 토큰의 요청에서" → "서버는 `gateway` 역할 토큰으로 온 사람 요청에서 `X-Openit-Roles` 에 `release-approver` 가 있을 때 이 헤더 값을 승인자로 쓴다(서비스 역할 토큰으로 오는 기계 호출은 해당 없음)". I5 `decide` 행 "쓰기 역할 `release-approver`만" → "사람 요청은 `X-Openit-Roles` 에 `release-approver` 가 있어야 한다". INTERFACES.md 96행 첫 두 문장 → "서비스 역할 토큰으로 오는 기계 호출의 역할은 토큰에 묶여 있고, 사람 요청의 역할은 `X-Openit-Roles` 가 정한다(CONVENTIONS 6절). `requested_by_role` 은 기록용이며 토큰(기계) 또는 `X-Openit-Roles` 의 역할 목록(사람)에 없으면 `PERMISSION_DENIED` 다."

### R6-2 `gateway` 역할 토큰을 서비스가 어떻게 받는지 어느 스키마에도 없다
- 위치: CONVENTIONS.md 6절 "platform 공개 입구의 서비스 토큰(토큰 역할 `gateway`)" / CONVENTIONS.md 13절 "영역 사이 설정 이름은 `*Env` 스키마에 있다"·RUNTIME R9.1 "IN-ENV 는 스키마에 있는 이름만" / GateEnv(`GATE_READ_TOKENS`, `GATE_WRITE_TOKENS`)·SurveyServiceEnv(`SURVEY_KIOSK_DEVICE_TOKENS` 등)·그 밖 Env 스키마에 `gateway` 역할 토큰 이름이 없다(`boundary_contracts/schemas/*Env*.json` 확인).
- 왜 결함: 이 토큰이 없으면 서비스는 모든 사람 경로의 `X-Openit-User/Roles/Device` 를 무시한다(위 6절 규칙). 영역 사이에 오가는 값(토큰 이름·역할 이름)이 계약 스키마에 없다(구조 규칙 6, 13절 "설정 이름은 스키마에").
- 고칠 문장: 서비스를 가진 영역의 Env 스키마(또는 `CommonEnv`가 아니라 영역별로)에 `<접두사>_GATEWAY_TOKENS_FILE`(비밀 파일 경로, D84)를 더하고, HTTP.md 공통 "토큰" 항목에 "역할 `gateway` 는 platform 공개 입구가 사람·기기 요청을 상류에 넘길 때 쓰는 토큰이다(Exposure `upstream_token`의 이름과 같다)"를 쓴다.

### R6-3 SSE 상태 확인 탐침은 서버에서 진짜 구독이 된다
- 위치: PUBLIC_API.md SSE 행 "연결이 닫혀 다시 열리지 않으면 같은 경로로 한 번 요청해 상태와 `Retry-After` 만 읽고 본문은 받지 않는다" / 같은 문서 "`TurnFailureSignal.staff_alert`: … 전달 경로가 하나 이상 살아 있을 때(SSE 연결 또는 푸시 서비스가 접수) `DELIVERED`" 및 "서버는 동시 SSE 연결 상한을 넘으면 429".
- 왜 결함: 탐침이 200을 받는 순간 서버에는 구독 하나가 생긴다. (1) 그 사이에 난 위험 알림은 아무도 읽지 않는 연결 때문에 `DELIVERED`가 된다(키오스크가 직원 호출 화면을 띄우지 않는다. 안전에 관한 오판). (2) 연결 상한(429)을 한 칸 더 쓴다. (3) 탐침이 헤더만 읽고 끊어도 `heartbeat`/`resync` 이벤트가 이미 나갈 수 있다. (확인: admin-console 구현이 정확히 이 방식이라 같은 위험이 있다.)
- 고칠 문장: PUBLIC_API.md SSE 행의 위 문장을 "상태 코드가 필요한 클라이언트는 `EventSource` 대신 `fetch()` 스트림 읽기로 연결해 응답 상태와 `Retry-After` 를 연결 한 번에서 얻는다(WHATWG: `EventSource` 는 상태 코드를 주지 않는다)."로 바꾸고, "서버는 응답 헤더를 보낸 직후 첫 이벤트 전에 닫힌 연결은 구독자(`DELIVERED` 판정)로 세지 않는다"를 더한다.

### R6-4 R3.26의 받는 스트림 여유 16MiB는 상한 안의 정상 tar를 거부할 수 있다
- 위치: RUNTIME.md R3.26 "tar 는 풀기 전 총 크기 8GiB(`max_tar_bytes`)·항목 200,000개, 받는 스트림은 tar 헤더 여유 16MiB 를 더한 8GiB+16MiB(여유는 근거 기록 없음·측정 안 함)" / `_http.py` `cap = self.max_tar_bytes + (16 << 20)`.
- 왜 결함: tar는 항목마다 512바이트 헤더와 512바이트 단위 패딩을 가진다(POSIX ustar). 항목 200,000개면 헤더만 약 98MiB(200,000×512B)이고 패딩을 더하면 최대 약 195MiB다. 16MiB 여유는 항목 상한 안의 정상 tar에서도 `INTEGRITY_ERROR("tar 응답이 크기 상한을 넘는다")`를 낼 수 있다(계산은 문서의 두 상한에서 나온 값, 실측 아님). "근거 기록 없음"을 문장이 스스로 적었다.
- 고칠 문장: R3.26을 "받는 스트림은 `max_tar_bytes` + 항목 상한×1024바이트(헤더 512 + 패딩 최대 512)+ 1MiB(끝 블록)"로 쓰고 `_http.py` cap 도 같은 식으로 맞춘다(근거: POSIX ustar 형식, 계산값).

### R6-5 `ResultReadyEvent`의 x-consumers에 kiosk-frontend가 있다
- 위치: boundary_contracts/schemas/ResultReadyEvent.schema.json `x-consumers: [admin-console, kiosk-frontend]`, description "clinician 역할에만 보낸다(B-06)" / PUBLIC_API.md SSE 행 "`staff`에는 `alert`·`resolved`, `clinician`에는 `result_ready`".
- 왜 결함: kiosk-frontend의 직원 콘솔은 `staff` 역할이라 이 이벤트를 받지 않는다. 받지 않는 소비자가 소비자로 적혀 있으면 스키마 변경 영향 범위가 틀리고(13절 "x-consumers = 그 값을 입력으로 받는 쪽") 소비자가 결과 알림을 받는 줄 오해한다.
- 고칠 문장: `x-consumers` → `["admin-console"]`. (kiosk-frontend 직원 콘솔이 `clinician` 계정으로도 쓰이는 설계라면 PUBLIC_API B절에 그렇다고 적고 그때는 현행 유지.)

### R6-6 EXTERNAL_SCHEMAS.json 목록에 영역 사이 본문 두 개가 빠졌다
- 위치: EXTERNAL_SCHEMAS.json `schemas`(QuestionBank, FrontendMessage, FrontendInput, SessionResult, StaffSessionView, TurnTrace 6개) / PUBLIC_API.md 호출표 "`turn_id` … 문진 스키마(`FrontendMessage`, `InterventionDecision`)" · 직원 콘솔 표 "개입 결정 … 본문 `{"session_id", "decision", "turn_id"}`" · D절 "위험 신호 … 본문 `RiskSignal`".
- 왜 결함: kiosk-frontend(직원 콘솔) → survey-service의 `InterventionDecision`과 외부 감지기 → survey-service의 `RiskSignal`은 영역 사이 입력인데 계약 schemas에도 EXTERNAL_SCHEMAS에도 이름·주인이 없다(`RiskSignal`은 `grep`으로 PUBLIC_API.md 서술 밖에 없음을 확인). `TurnFailureSignal`은 FrontendInput 안에 있고 "where"에 적혀 있으나 독립 항목이 아니다. 13절 "모든 스키마는 x-producers·x-consumers를 가진다"에 빠진다.
- 고칠 문장: EXTERNAL_SCHEMAS.json에 `{"name": "InterventionDecision", "x-producers": ["kiosk-frontend"], "x-consumers": ["survey-service"], "where": "PUBLIC_API 직원 콘솔 개입 결정"}`, `{"name": "RiskSignal", "x-producers": ["external:install-site"], "x-consumers": ["survey-service"], "where": "PUBLIC_API D절"}` 를 더한다(RiskSignal 정본이 문진 스키마에 없으면 이 리포 schemas로 신설).

### R6-7 `HumanUserInfo.groups`의 패턴이 읽는 쪽에서 userinfo 전체를 거부할 수 있다
- 위치: boundary_contracts/schemas/HumanUserInfo.schema.json `groups.items.pattern = ^/?[a-z][a-z-]*$` / CONVENTIONS.md 1절 3항 "읽는 쪽은 … 모르는 열거값은 오류로 죽지 않고 '알 수 없음'으로 처리한다" · HTTP.md 공통 "패턴 위반은 INTEGRITY_ERROR".
- 왜 결함: IdP 그룹은 역할 8개 말고도 있을 수 있다(대문자·숫자·중첩 경로 `/org/team`). 패턴을 읽기 쪽 검증에 쓰면 그 계정은 로그인했는데 userinfo가 `INTEGRITY_ERROR`가 된다. 화면은 "표시에만 쓰고 권한 판단은 게이트웨이가 한다"(같은 설명)이므로 엄격히 거부할 이유가 없다.
- 고칠 문장: `groups.items`를 `{"type": "string"}`으로 바꾸고 description에 "역할 목록(CONVENTIONS 6절)의 이름이 오며, 그 밖의 그룹 이름도 올 수 있어 화면은 무시한다"를 쓴다.

### R6-8 CONVENTIONS 13절의 나가는 쪽 허용 상대 목록이 R6.2·Exposure `egress`와 다르다
- 위치: CONVENTIONS.md 13절 "자기 게이트웨이는 계약이 정한 호출 관계(HTTP.md I1~I10, 웹 푸시)에 있는 상대에게만 터널을 열고" / RUNTIME R6.2 "허용되는 호출 관계는 INTERFACES.md "한눈에" 표(I1~I10, 정본), … 웹 푸시(R3.18), 백업 저장소(R10.1), 배포의 OUT-FILE(R1.5)뿐" / Exposure.schema.json `egress` 항목 `external:web-push`·`external:backup`.
- 왜 결함: 13절은 백업 저장소 출구를 빼고(R10.1은 백업을 자기 게이트웨이 출구로 보낸다고 함) "HTTP.md I1~I10"을 정본으로 삼는데 R6.2는 정본이 INTERFACES.md 표라고 한다(두 문서가 어긋날 때 어느 쪽이 맞는지 정해 있지 않다). R6.4는 여전히 "바깥 인터넷으로 나가는 호출은 웹 푸시 발송뿐"이라 `external:backup` 선언을 설명하지 못한다(백업 저장소가 platform이므로 "바깥 인터넷"이 아니라는 구분이 문장에 없다).
- 고칠 문장: CONVENTIONS 13절 해당 괄호를 "(INTERFACES.md 한눈에 표의 I1~I10, 웹 푸시, platform 백업 저장소 — RUNTIME R6.2; 영역은 Exposure `egress` 로 이 중 자기 몫을 선언한다)"로, R6.4를 "영역 서비스가 platform 밖(바깥 인터넷)으로 나가는 호출은 …뿐이다"로 고친다.

### R6-9 HTTP.md I9의 소비자는 survey-service 하나인데 INTERFACES·호출 표·스키마는 model-lab·release-gate를 소비자로 둔다
- 위치: HTTP.md "## I9 ModelRuntime 추론 서버 — 소유: model-runtime (서버), 소비: survey-service (D62)" / INTERFACES.md 한눈에 표 "I9 model-runtime … 읽는 쪽 survey-service, model-lab, release-gate" · RUNTIME-MATRIX.md C40(model-lab → 추론 서버)·C42(release-gate → 추론 서버)· RuntimeInfo `x-consumers [deploy, model-lab, survey-service]`.
- 왜 결함: 같은 호출 관계(허용 목록의 정본, R6.2)를 두 문서가 다르게 말한다. HTTP.md만 읽는 게이트웨이 설정은 model-lab·release-gate의 터널을 막는다. 또 RuntimeInfo의 소비자에 release-gate가 없는데 C42(release-gate가 `GET /v1/info` 호출)가 있다.
- 고칠 문장: HTTP.md I9 머리를 "소비: survey-service(적재·extract·respond), model-lab(`/v1/info`·평가 호출), release-gate(`/v1/info`·`/readyz` 호환 검사)"로, RuntimeInfo `x-consumers`에 `release-gate`를 더한다.

### R6-10 시간 상한 사슬 표 아래 새 행이 빈 줄 뒤에 있어 표에서 떨어진다
- 위치: CONVENTIONS.md 시간 상한 사슬 둘째 표 마지막에 빈 줄 하나를 두고 "| 표에 없는 서비스 사이 호출(이웃 호출, 계약 클라이언트) | — | — | — | 계약 클라이언트 `timeout` 10초 …|" (1bbf6dd 약 148~150행).
- 왜 결함: Markdown(GFM)에서 빈 줄 뒤의 `|` 행은 앞 표에 속하지 않고 문단이 된다. R10.3이 "CONVENTIONS 시간 상한 사슬의 '표에 없는 서비스 사이 호출' 행"을 근거로 가리키는데 그 행이 표의 행이 아니다. 도구가 표를 파싱하면 이 행이 사라진다.
- 고칠 문장: 빈 줄을 지워 앞 표의 마지막 행으로 붙인다(열 수 5개 유지).

### R6-11 SSE 최대 수명의 값 출처가 두 곳이다
- 위치: PUBLIC_API.md SSE 행 "스트림의 최대 수명은 platform 의 세션 갱신 주기 이하이고(값은 survey-service ADR, 측정 안 함)" / RUNTIME R2.4 "값은 `SurveyServiceEnv.SURVEY_SSE_MAX_SECONDS`, 기본 300초·측정 안 함, deploy 가 세션 갱신 주기 이하로 준다" / SurveyServiceEnv.SURVEY_SSE_MAX_SECONDS(기본 "300").
- 왜 결함: 값의 정본이 "survey-service ADR"(영역 내부 문서)과 Env 스키마(영역 사이) 둘이다. 영역 사이 값은 스키마에만 있어야 한다(13절). 또 기본 300초가 platform의 세션 갱신 주기보다 길 수 있는데, 그 주기 값은 "platform ADR"(R3.12)에만 있어 이 계약에서 "이하" 조건을 검사할 수가 없다.
- 고칠 문장: PUBLIC_API.md의 괄호를 "(값은 `SurveyServiceEnv.SURVEY_SSE_MAX_SECONDS`)"로 바꾼다. R3.12에 "세션 갱신 주기는 `HumanAuthEndpoints`(또는 별도 platform 설정 스키마)의 `session_refresh_seconds`로 선언한다(값은 platform ADR, 측정 안 함)"를 더해 deploy가 두 값을 대조하게 한다.

### R6-12 쿠키 세션의 401에 `WWW-Authenticate: Bearer realm="openit"`
- 위치: RUNTIME.md R3.23 "로그인 세션(쿠키) 경로는 `Bearer realm="openit"`(쿠키 세션에 맞는 표준 체계가 없어 챌린지 이름만 정한다), `X-Openit-User` 가 없는 401 도 `Bearer realm="openit"`" / RFC 6750 §3(Bearer는 Authorization 헤더로 보내는 토큰의 체계).
- 왜 결함: 표준 체계가 없는데 Bearer를 빌려 쓰면 일반 클라이언트가 Authorization 헤더로 토큰을 보내려 시도한다(오작동 위험). RFC 9110 11.6.1은 401에 "대상에 적용되는 챌린지"를 요구하나 쿠키 로그인에는 해당 체계가 없다는 점을 문장이 스스로 인정한다. 측정이 아니라 표준 해석의 문제다.
- 고칠 문장: "쿠키 세션 경로의 401은 `WWW-Authenticate` 를 갖지 않는다(RFC 9110 11.6.1이 요구하는 챌린지에 해당하는 표준 체계가 없다. 계약 클라이언트·키오스크·화면은 이 헤더에 의존하지 않고 상태 코드로 분기한다)"로 바꾸거나, 이름을 `openit-session`처럼 표준에 없는 체계 이름으로 쓴다.

### R6-13 HTTP.md I5가 중복 제출의 200을 말하지 않는다
- 위치: HTTP.md I5 `submit_candidate` 행 응답 "`GateSubmission` (202). …(문장 끝) 세트 하나라도 어긋나면 제출 전체가 `REJECTED_AUTO` 다" / INTERFACES.md I5 "같은 subject의 중복 요청은 기존 접수를 200 으로 돌려준다(RUNTIME R10.8)" · RUNTIME R10.8 "기존 접수를 200 으로 돌려준다(새 접수는 202)".
- 왜 결함: 와이어 정본인 HTTP.md 응답 칸에는 202뿐이라 클라이언트·서버 구현자가 중복에 202를 내도 HTTP.md와 모순되지 않는다. 같은 요청 → 같은 출력 규칙이 두 문서에만 있다.
- 고칠 문장: HTTP.md I5 `submit_candidate` 응답 칸 맨 앞을 "`GateSubmission` — 새 접수 202, 같은 대상(문진표들·LoRA-A·LoRA-B)의 중복 요청은 기존 접수를 200 으로"로 쓴다.

### R6-14 `lineage.question_sets`가 선택 필드인데 없으면 FAIL, 이미 게시된 패키지는 고칠 수 없다
- 위치: ModelPackageManifest.schema.json `lineage.question_sets` description(1bbf6dd) "model-lab 은 게시할 때 반드시 채운다(1개 이상) … 이 필드가 없거나 비면 대조할 수 없으므로 FAIL 이다. 스키마에서 필수로 바꾸지 않은 이유: 필수 추가는 MAJOR … 출력 규칙으로 같은 효과" / CONVENTIONS 1절 5항 "모든 레코드는 불변이다" · R7 "만드는 쪽은 스키마로 검증한 뒤 내보낸다".
- 왜 결함: (1) 스키마가 통과시키는 레코드(필드 없음)를 게시한 쪽이 계약 위반인지 알 수 없다. 생산자 출력 검증(R7)은 스키마 기준인데 규칙이 스키마 밖에 있다. (2) 이미 게시된 패키지(불변, 해시 포함)는 이 필드를 나중에 채울 수 없으니 전부 영구 FAIL이다(새 버전으로 다시 게시해야 함). 문장이 이 영향을 적지 않았다. (3) 3.3.0에서 이미 MAJOR 예외를 썼고 "다음부터 이 예외를 쓰지 않는다"고 했으므로 필수화는 4.0.0이 맞다.
- 고칠 문장: description 끝에 "이전 버전으로 게시한 패키지(이 필드 없음)는 불변이라 고칠 수 없으므로 이 검사에서 FAIL이다. 다시 게시(새 버전)해야 한다. 필수 승격은 4.0.0에서 한다(CHANGELOG에 예고)."를 더한다.

### R6-15 `PushSubscriptionRequest.endpoint` 패턴이 IP 리터럴·`localhost`를 통과시킨다
- 위치: PushSubscriptionRequest.schema.json `endpoint.pattern = ^https://[^/:@?#]+(:443)?/` / RUNTIME R3.18 "loopback·사설·링크로컬·특수 주소면 등록은 400 `INVALID_RECORD`(SSRF 방지, OWASP A10:2021)" / PUBLIC_API 푸시 구독 행 "https·포트 443·공인 주소만".
- 왜 결함: 스키마가 `https://127.0.0.1/`·`https://localhost/`·`https://169.254.169.254/`를 통과시킨다. 서버가 DNS 해석 뒤 검사하는 것은 맞지만(R3.18), 해석이 필요 없는 IP 리터럴까지 스키마 검증을 통과해 검사가 서버 구현에만 남는다. 또 "특수 주소"가 정의되어 있지 않다(RFC 6890 특수 목적 주소 등).
- 고칠 문장: 패턴 앞에 부정 선행 `(?![0-9.]+/|\[|localhost[/:])`를 두어 IP 리터럴·localhost를 스키마에서 거부하고, R3.18에 "특수 주소 = RFC 6890의 특수 목적 주소(loopback, 사설, 링크로컬, 공유 주소 100.64.0.0/10, 멀티캐스트 등)"를 정의한다. 해석된 주소 검사는 게이트웨이가 CONNECT 시점에도 한다는 R3.18의 문장은 맞다(DNS 재바인딩 방지).

### R6-16 FLOW.md 7행이 `ModelPackageManifest.question_sets`라고 쓰지만 정본 위치는 `lineage.question_sets`다
- 위치: head/docs/FLOW.md 7행 "`DatasetManifest.question_sets`, `ModelPackageManifest.question_sets`" / ModelPackageManifest.schema.json `properties.lineage.properties.question_sets`.
- 왜 결함: 필드 위치가 다르다. 이 리포 안의 문서(CHANGELOG·RUNTIME·PUBLIC_API·HTTP.md·INTERFACES)에는 옛 위치 표기가 없음을 grep으로 확인했다. 결함은 이 리포 밖(FLOW.md)에 있고 이 검토는 읽기 전용이라 고치지 않았다.
- 고칠 문장: FLOW.md 7행의 `ModelPackageManifest.question_sets`를 `ModelPackageManifest.lineage.question_sets`로 바꾼다(헤드).

### R6-17 R3 머리말의 `Retry-After: 5` 설명이 "구분할 입력이 없다"고 하면서 값을 정당화한다
- 위치: RUNTIME.md R3 머리말 "게이트웨이의 503 은 앱이 죽었거나 재시작 중일 때라 1초 안에 돌아올 가능성이 낮고, 포화(R3.16)와 재시작(R3.2)을 나누지 않는 것은 게이트웨이가 둘을 구분할 입력이 없어서다" / R3.16 포화 행 출력 "503 UU"(같은 5초).
- 왜 결함: 포화(R3.16)는 순간 상태라 1초 안에 풀릴 수 있다는 이유가 위 문장 안에서 "앱이 죽었거나 재시작"에만 적용되어, 같은 5초를 포화에 쓰는 근거가 되지 않는다. 구분 불가 때문에 한 값을 쓴다는 설명은 맞으나 "가능성이 낮다"는 추측(측정 안 함)이 근거처럼 읽힌다. 값 자체는 "시작값, 측정 안 함"이라고 밝혔으므로 결함이 작다.
- 고칠 문장: "…5초다(시작값, 측정 안 함. 앱이 내는 1초보다 길게 둔 이유는 추정이며, 재시작·포화를 구분할 입력이 없어 한 값이다)"로 "가능성이 낮다"를 "추정"으로 표시한다.

---

## 이번 판에서 이전 검토(B-01~B-28) 반영을 확인한 항목 (결함 없음으로 판정, 근거)
- B-01(활성 릴리스 없음): PUBLIC_API 호출표 `GET /v1/question-sets` 행에 503 `NO_ACTIVE_RELEASE`+`Retry-After`가 있고 CONVENTIONS 10절 reason 목록에 있다. 일치함.
- B-02(배치 ID가 목록에 없음): PUBLIC_API I절 둘째 항목에 규칙이 있다. 일치함.
- B-03: HTTP.md I5 응답 칸에 422/`REJECTED_AUTO` 규칙이 있다(중복 200만 R6-13).
- B-07·B-23·B-24: R3.23·R3.24·R1.8·R3.18 문장이 서비스 토큰 판정 주체, CONNECT 403 → `PERMISSION_DENIED/EGRESS_DENIED`, endpoint SSRF 규칙을 담고 `_http.py` `_egress_denied`가 같은 코드를 낸다(코드 읽음). 일치함.
- B-12: CELLS의 "R10.3 의 30초" 인용이 0건(`grep -c`)이고 R10.3은 10초다. 일치함.
- B-13: CONVENTIONS 1절 4항에 3.3.0 예외 기록. 일치함(다음 MAJOR 예고는 R6-14에서 요청).
- B-25: CONVENTIONS 13절·R10.1·MATRIX A표 머리말이 DB를 영역 컴포넌트로 통일. 일치함.
- B-08: R2.4가 최대 수명 방식으로 바뀜. 값 출처가 둘인 점만 R6-11.
- 새 스키마 `GatewayError`·`HeartbeatEvent`·`ResyncEvent`·`CommonEnv`·`HumanAuthEndpoints`: x-producers/x-consumers가 설명과 맞는지 확인했다(`ResultReadyEvent`만 R6-5). `CommonEnv.OPENIT_EGRESS_PROXY` 패턴(loopback http)이 `require_egress_proxy`의 규칙(http, loopback 호스트, 포트 필수)과 같다.

## 읽은 범위 (줄 범위, 1bbf6dd 기준. 줄 번호는 현재 파일의 줄)
전부 읽음(문서 전체를 한 번 이상):
- RUNTIME.md 1~170: 8021268 판 1~168 전체를 읽었고(04:31~04:34), 1bbf6dd에서 바뀐 모든 행(R1.5, R1.8, R2.4, R3 머리말, R3.3, R3.13, R3.18, R3.23, R3.24, R3.26, R4.1, R6.1, R6.2, R10.1, R10.3, R10.4, R10.8)을 diff로 읽었다.
- CONVENTIONS.md 1~162: 8021268 판 1~157 전체와 1bbf6dd 변경 전부(1절 4항, 3절 표, 4절 추가 두 항목, 6절, 9절 헬스·401/403·과다 요청·reason·`/readyz`, 시간 상한 사슬, 13절).
- HTTP.md 1~153: 전체와 변경 전부(공통 12행, I1 `list_ids`, 저작 API 문단, I5 `submit_candidate`·승인자 식별, I9 보증·호출자 실패 처리).
- PUBLIC_API.md 1~156: 전체와 변경 전부(원칙 7·8행, 오류표 401, 호출표 문진표 목록, 직원 콘솔 SSE·푸시 구독, 재시도 규칙, "정한 값" 절, B절 result-reader, C절, E절, F절, H절, I절).
- INTERFACES.md 1~228: 전체와 변경 전부(한눈에 표 I4·I10, I4 `load_bundle`·`find_decisions`, I5 `submit_candidate`, I9 `OUTPUT_INVALID` 처리, 책임 요약 표).
- RUNTIME-MATRIX.md 1~85: 전체(A표 호출 목록과 B 실패 종류, 변경된 머리말·C24·C30·C34·C37~C42·F20·C 절).
- 스키마: 새로 생긴 것 `GatewayError`·`HumanAuthEndpoints`·`HumanUserInfo`·`ResultReadyEvent`·`CommonEnv`·`PushSubscriptionRequest` 본문, 변경된 `Exposure`(description·`egress`)·`SubmissionView`·`ModelPackageManifest`(lineage)·`ActionExtraction`(next_item)·`SurveyServiceEnv`(`SURVEY_SSE_MAX_SECONDS`) diff. 나머지 약 90개 스키마는 8021268 판의 x-producers/x-consumers 표만 봤다.
- `boundary_contracts/clients/_http.py`(270~445행과 8021268..1bbf6dd diff), `EXTERNAL_SCHEMAS.json` 전체, CHANGELOG.md 이번 구간 추가 줄.

못 읽음 / 얕게만 읽음:
- RUNTIME-MATRIX-CELLS.md: 이 몫의 대상이 아니다(P1~P5). R10.3 인용 "30초" 0건만 grep으로 확인했다.
- `HeartbeatEvent`·`ResyncEvent`·`HealthStatus`·`Exposure.examples`·`examples/*.json` 본문, `tests/*_344.py`(owners 테스트의 새 검사 줄만 읽음), `publicapi.py` 본문, METRICS.md, docs/adr 본문.
- 60dc386..8021268 구간의 diff 자체는 줄 단위로 다시 읽지 않았다(8021268 판 문서 전체를 읽은 것으로 대신함).
