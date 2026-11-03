대조한 칸 수 162 / 몫의 전체 칸 수 162 / 결함 칸 수 121  (맞음 41, 낡음 116, 계약 빈칸 5, 모순 0)

검토 대상: boundary-contracts 1bbf6dd(3.4.4). 몫 P5 = RUNTIME-MATRIX-CELLS.md "묶음 5"(881~1042줄)의 C37~C42 × F01~F27 = 162칸. 읽은 현행 계약: RUNTIME.md(1bbf6dd 의 R1.5·R1.8·R2.4·R3.x·R4.1·R6.2·R10.x 전체와 이전 판 대비 diff), CONVENTIONS.md·HTTP.md·INTERFACES.md 의 1bbf6dd 변경분과 I1·I4·I7·I9 절, MATRIX A(C37~C42 정의), 스키마 x-consumers(RuntimeInfo·GateDecision·FailureCase·ReviewRecord).
용어: 맞음 = 입력·출력이 현행 조항과 같다. 낡음 = 출력의 뜻은 맞거나 거의 맞지만 칸의 문장(입력 열, 판정 라벨 "열림", 낡은 인용·"모순 M1" 문구)이 현행과 다르다. 계약 빈칸 = 계약 문장이 없어서 칸을 판정할 수 없다. 모순 = 0건.
이 몫의 모든 칸(162)을 한 줄씩 아래 표에 적었다(맞음 포함).

## 이 묶음 전체에 걸친 발견 (표의 "고칠 것"에서 반복되는 원인)

G1. 입력 열이 다른 호출의 문구다 (낡음의 가장 큰 원인). 묶음 5 의 칸은 "같은 인터페이스를 같은 종류의 호출자가 부르는 기존 호출에서 옮겼다" 고 머리에 적었으나(CELLS:877), 입력 열 문장이 원본 그대로다. 예: C37(model-lab → qa) F01 입력 "synthetic-data 잡 → question-authoring(I1 읽기)", C37~C40 의 F04·F05·F08~F11 입력 "model-lab 파이프라인 → dataset-store (I2 읽기)", C38 의 F01~F03·F06·F07 입력 "synthetic-data 잡 → ops-feedback", C39·C41 의 입력 "ops-feedback 잡 → release-gate", C40·C42 의 입력 "survey-service → 추론 서버". 판정 열의 "(= C04 F01)" 은 원본 표시라 의도된 것이지만 입력 열은 이 칸의 호출 설명이어야 한다. 입력 열의 호출 이름이 이 칸의 호출과 다른 칸: 84칸(입력 열에 "→" 가 있고 caller·callee 이름이 C37~C42 의 것과 다른 칸, 나머지 78칸의 입력 문장은 호출 이름이 없는 일반 설명이라 문제 없음).
  고칠 문장(일괄): 입력 열을 "<MATRIX A 의 호출 설명>: <실패 설명>" 형식으로 다시 쓴다. C37 "model-lab 파이프라인(학습 서버, compose 밖) → question-authoring(I1 읽기)", C38 "… → ops-feedback(I7 읽기)", C39 "… → release-gate(I4 읽기, 판정 조회)", C40 "… → 추론 서버(I9 정보·준비·평가 호출)", C41 "question-authoring → release-gate(I4 읽기, 판정 조회)", C42 "release-gate → 추론 서버(I9 정보·준비, 호환 검사)".

G2. 판정 "열림" 칸(O2·O4·O6·O8 제안)이 닫히지 않은 채 복사됐다. 묶음 5 에서 "열림" 으로 표시된 칸: C37~C42 의 F16·F24·F26(18칸)과 C40·C42 의 F12(2칸). 현행 계약이 모두 닫았다: F16=R3.17 오른쪽 열(UNAVAILABLE), F24=R3.25, F26=R3.26, F12(O8)=HTTP.md I9 의 401 행(121줄). CELLS:3 의 "열림은 모두 닫았다" 와 묶음 5 의 라벨이 모순이므로 라벨을 "닫힘(R…)" 으로 바꾼다.

G3. compose 밖 호출자 C37~C40 에 영역 게이트웨이 출구가 빠졌다. 현행 R1.5 는 compose 밖 호출자가 OUT-FILE·서비스 토큰과 "deploy 가 같은 서버에 둔 자기 영역 게이트웨이의 출구(IN-EGRESS, R1.8)" 로 부른다고 한다. F04·F05·F06·F13 의 칸에는 (a) 자기 게이트웨이에 닿지 못함(R3.21 → UNAVAILABLE), (b) 자기 게이트웨이가 상대를 허용하지 않음(R1.8 → CONNECT 403 → 클라이언트 PERMISSION_DENIED, details.reason=EGRESS_DENIED, 재시도 안 함)이 없다. 출력의 큰 줄기(UNAVAILABLE)는 바뀌지 않으므로 낡음으로 분류했다. F13 은 compose 안의 C41·C42 에도 (b)가 해당한다(영역 안 컴포넌트의 영역 밖 호출은 모두 자기 게이트웨이를 지난다, CONVENTIONS 13절).

G4. [계약 빈칸] C40 "model-lab 파이프라인 → 추론 서버 I9 정보·준비·평가 호출" 의 면이 정해져 있지 않다.
  - HTTP.md:108 "## I9 ModelRuntime 추론 서버 — 소유: model-runtime (서버), 소비: survey-service (D62)" — 소비자가 survey-service 하나뿐이다. 그런데 INTERFACES.md:23 은 "I9 읽는 쪽: survey-service, model-lab, release-gate", 스키마 `RuntimeInfo` 의 x-consumers 는 `deploy, model-lab, survey-service, release-gate`, MATRIX A 는 C40·C42 를 둔다.
  - HTTP.md I9 의 extract/respond 는 `/v1/releases/{release_id}/…` 로 "적재된 릴리스" 에만 있고 PUT 은 "서버가 I4 에서 번들을 읽어 적재"(PASS 릴리스)다. model-lab 이 평가하는 후보 모델은 게이트 PASS 전이라 릴리스가 없으므로(평가 보고서가 PASS 의 입력이다) 이 경로로 평가할 수 없다. INTERFACES.md:204 는 model-lab 이 라이브러리 `*_raw` 로 평가한다고 적었다(프로세스 안, 영역 사이 호출이 아님).
  - 따라서 C40 의 "평가 호출" 이 HTTP 호출인지 라이브러리 호출인지 계약에 없다. HTTP 호출이면 후보를 적재하는 면(릴리스 없이)이 없고, 라이브러리면 C40 은 호출 표에서 빠져야 한다.
  - 넣을 위치와 문장(결정 필요, 둘 중 하나): (a) 호출 표에서 C40 을 정보·준비로 한정: RUNTIME-MATRIX.md C40 행을 "model-lab 파이프라인 → 추론 서버 | I9 정보·준비(`GET /v1/info`, `GET /v1/releases/{id}`) | 서비스 토큰" 으로 고치고 평가는 라이브러리 `*_raw` 라고 INTERFACES 에 이미 있음을 칸에 적는다. 그러면 C40 의 F03·F18·F19·F20·F23 칸은 C42 와 같은 GET 칸이 된다. (b) 평가를 HTTP 로 하려면 HTTP.md I9 에 "후보 평가 적재" 경로(예: `PUT /v1/candidates/{package_id}/{version}` + 같은 extract/respond)를 정의한다. 근거 표준: 없음(헤드 설계 결정).
  - 그리고 HTTP.md:108 의 "소비:" 를 "소비: survey-service(적재·extract·respond), release-gate·model-lab·deploy(`GET /v1/info`)" 로 고친다.
  - 영향받은 칸: C40 F03·F18·F19·F20·F23(계약 빈칸 5칸). C40 의 나머지 칸은 어느 쪽 결정에도 출력이 같아 맞음/낡음으로 판정했다.

G5. 칸이 다른 호출의 인터페이스 동작을 말한다.
  - C39·C41(판정 조회 `get_decision`·`find_decisions`)이 F18 에 `QUESTION_SET_REQUIRED`, F19 에 412·409, F26 에 번들·문항 세트 해시를 적었다 — 이는 `get_release_question_bank`·`load_bundle`·`submit_candidate` 의 동작이다. 판정 조회의 실패는 404(get_decision), 빈 목록 200(find_decisions), GateDecision 스키마·content_hash 검증 실패 INTEGRITY_ERROR 이다.
  - C38(model-lab → ops-feedback)의 F20 은 reviewer 전용 `get_review_trace` 의 "접근 기록" 을 적었으나 model-lab 은 그 경로를 부르지 않는다(스키마 `OpsFeedbackReviewTrace` 소비자는 admin-console, 읽기 토큰은 403).
  - C42(GET 만 부름)의 F03·F18·F19·F20·F23 은 extract/respond/PUT 의 동작을 적었다. 적재되지 않은 릴리스의 `GET /v1/releases/{id}` 는 404 가 아니라 200 `state=ABSENT`(HTTP.md I9).

G6. 판정 근거 확인(맞음 칸). 출력이 현행 조항과 같은 칸: F01·F02(R3.1·R3.2 오른쪽 열 UNAVAILABLE, R4.1)·F14(R3.12 기계 토큰 경로 불변)·F15(R3.5·R3.6 INVALID_RECORD)·F21(R3.10)·F22(R3.11)·F25(R6.4)·F27(R10.5·R3.10)·F18·F19(해당 호출) 등. 출력하는 쪽·받는 쪽은 모두 "계약 클라이언트(호출 영역) → 호출 컴포넌트" 이고 현행 CONVENTIONS 13절과 맞다. 데이터베이스는 영역 컴포넌트이고(R10.1 개정) F21 칸의 "받는 서비스의 DB" 는 영역 내부 표시만 확인했으며 다른 영역의 DB 를 가리키는 칸은 없다(C24 행은 이 몫에 없음).

## 칸별 표
| 호출 | 실패 | 판정(맞음/낡음/계약 빈칸/모순) | 현행 조항 | 고칠 것(그대로 넣을 문장 또는 칸 갱신 문장) |
|---|---|---|---|---|
| C37 | F01 | 낡음 | R3.1(오른쪽 열 UNAVAILABLE), R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F01 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F02 | 낡음 | R3.2, R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F02 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F03 | 낡음 | R3.3·R10.3(10초) | 출력 문장 끝의 "(3.4.4 정정 전 초안은 30초). 단 _http.py 기본 timeout 은 10초, 영역 설정(…)도 10초라 R10.3 과 어긋난다(M1)" 를 지운다: 현행 R10.3 이 10초라 어긋남이 없다. 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F03 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F04 | 낡음 | R3.14·R1.5·R1.8 (compose 밖) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F04 설명>" 으로 바꾼다(지금은 다른 호출의 문구). compose 밖 호출자는 자기 영역 게이트웨이(IN-EGRESS)에도 연결해야 하므로 출력에 "자기 게이트웨이에 닿지 못하면 R3.21, UNAVAILABLE" 를 더한다. |
| C37 | F05 | 낡음 | R3.14·R1.5(hosts 표) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F05 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F06 | 낡음 | R3.4(오른쪽 열)·R4.1·R3.21(자기 영역 게이트웨이) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F06 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 "자기 영역 게이트웨이(IN-EGRESS)가 멈춘 경우는 R3.21: UNAVAILABLE" 를 더한다(R1.8). |
| C37 | F07 | 낡음 | R3.16(오른쪽 열) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F07 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F08 | 낡음 | R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F08 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F09 | 낡음 | R1.2·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F09 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F10 | 낡음 | R1.3·R3.8·R1.7 | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F10 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F11 | 낡음 | R1.6·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F11 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F12 | 낡음 | R3.23(서비스 토큰: 받는 서비스가 401)·CONVENTIONS 9절(WWW-Authenticate: Bearer) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F12 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F13 | 낡음 | R3.24(서비스 토큰의 권한 밖은 받는 서비스가 403)·R1.8·R6.2(EGRESS_DENIED) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F13 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 R1.8 의 경우를 더한다: "자기 영역 게이트웨이가 이 호출 관계를 허용하지 않으면 CONNECT 403 → 클라이언트 PERMISSION_DENIED(details.reason=EGRESS_DENIED), 재시도 안 함". |
| C37 | F14 | 낡음 | R3.12(오른쪽 열: 기계 토큰 경로 출력 불변) | 입력 열을 "model-lab 파이프라인(compose 밖) → question-authoring(I1 읽기): <F14 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C37 | F15 | 맞음 | R3.5·R3.6(오른쪽 열 INVALID_RECORD) | —(출력이 현행 조항과 같다) |
| C37 | F16 | 낡음 | R3.17(오른쪽 열) | 판정 "열림 … R3.17 의 서비스 사이 열이 —" 를 닫는다. 현행 R3.17 오른쪽 열: "계약 클라이언트는 UNAVAILABLE(연결 끊김·비 BoundaryError 408). 쓰기는 R10.8 로 같은 요청을 다시 보내도 안전". 칸 출력: "연결이 닫히거나 408 → OUT-CLIENT UNAVAILABLE. 이 호출은 읽기라 그대로 다시 보내면 된다".  |
| C37 | F17 | 낡음 | R10.4(영역 서비스는 429 대신 503)·CONVENTIONS 9절(클라이언트 Retry-After 전달) | 출력의 "CONVENTIONS 9절 마지막 문단은 '읽지 않는다'고 해 코드와 어긋난다 → 모순 M1" 을 지운다: 현행 CONVENTIONS 9절은 BoundaryError 본문 409·429·503 의 Retry-After 를 details.retry_after_s 로 넘긴다고 적었다(해소).  |
| C37 | F18 | 맞음 | CONVENTIONS 9절 표(400·422)·HTTP.md 공통(읽기 모드) | —(출력이 현행 조항과 같다) |
| C37 | F19 | 맞음 | HTTP.md I1 latest(404) | —(출력이 현행 조항과 같다) |
| C37 | F20 | 맞음 | RFC 9110 9.2.1·9.2.2(GET) | —(출력이 현행 조항과 같다) |
| C37 | F21 | 맞음 | R3.10·R4.1 | —(출력이 현행 조항과 같다) |
| C37 | F22 | 맞음 | R3.11·R3.8 | —(출력이 현행 조항과 같다) |
| C37 | F23 | 맞음 | R4.6·R3.2·R3.15·R3.21 | —(출력은 맞다. 문장 끝의 "게시(C05·C07)는 …" 는 읽기 호출인 이 칸과 무관하므로 지워도 된다) |
| C37 | F24 | 낡음 | R3.25 | 판정 "열림"과 "RUNTIME 에는 본문 도중 끊김 행이 없다" 를 닫는다. 현행 R3.25: "UNAVAILABLE(details.reason=예외 종류). 읽은 부분을 값으로 쓰지 않고 tar 의 목적지를 남기지 않는다(RFC 9112 8). 같은 요청을 다시 보내면 된다". 출력은 그대로 맞다. |
| C37 | F25 | 맞음 | R6.4(웹 푸시뿐) | —(출력이 현행 조항과 같다) |
| C37 | F26 | 낡음 | R3.26 | 판정 "열림"과 "상한의 값과 초과 출력은 조항이 없다" 를 닫는다. 현행 R3.26: JSON·바이트 256MiB, tar 풀기 전 8GiB·항목 200,000개, 받는 스트림 8GiB+16MiB(여유는 근거 기록 없음), INTEGRITY_ERROR 재시도 안 함. |
| C37 | F27 | 맞음 | R10.5·R3.10 | —(출력이 현행 조항과 같다) |
| C38 | F01 | 낡음 | R3.1(오른쪽 열 UNAVAILABLE), R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F01 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F02 | 낡음 | R3.2, R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F02 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F03 | 낡음 | R3.3·R10.3(10초) | 출력 문장 끝의 "(3.4.4 정정 전 초안은 30초). 단 _http.py 기본 timeout 은 10초, 영역 설정(…)도 10초라 R10.3 과 어긋난다(M1)" 를 지운다: 현행 R10.3 이 10초라 어긋남이 없다. 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F03 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F04 | 낡음 | R3.14·R1.5·R1.8 (compose 밖) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F04 설명>" 으로 바꾼다(지금은 다른 호출의 문구). compose 밖 호출자는 자기 영역 게이트웨이(IN-EGRESS)에도 연결해야 하므로 출력에 "자기 게이트웨이에 닿지 못하면 R3.21, UNAVAILABLE" 를 더한다. |
| C38 | F05 | 낡음 | R3.14·R1.5(hosts 표) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F05 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F06 | 낡음 | R3.4(오른쪽 열)·R4.1·R3.21(자기 영역 게이트웨이) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F06 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 "자기 영역 게이트웨이(IN-EGRESS)가 멈춘 경우는 R3.21: UNAVAILABLE" 를 더한다(R1.8). |
| C38 | F07 | 낡음 | R3.16(오른쪽 열) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F07 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F08 | 낡음 | R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F08 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F09 | 낡음 | R1.2·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F09 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F10 | 낡음 | R1.3·R3.8·R1.7 | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F10 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F11 | 낡음 | R1.6·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F11 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F12 | 낡음 | R3.23(서비스 토큰: 받는 서비스가 401)·CONVENTIONS 9절(WWW-Authenticate: Bearer) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F12 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F13 | 낡음 | R3.24(서비스 토큰의 권한 밖은 받는 서비스가 403)·R1.8·R6.2(EGRESS_DENIED) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F13 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 R1.8 의 경우를 더한다: "자기 영역 게이트웨이가 이 호출 관계를 허용하지 않으면 CONNECT 403 → 클라이언트 PERMISSION_DENIED(details.reason=EGRESS_DENIED), 재시도 안 함". |
| C38 | F14 | 낡음 | R3.12(오른쪽 열: 기계 토큰 경로 출력 불변) | 입력 열을 "model-lab 파이프라인(compose 밖) → ops-feedback(I7 읽기): <F14 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C38 | F15 | 맞음 | R3.5·R3.6(오른쪽 열 INVALID_RECORD) | —(출력이 현행 조항과 같다) |
| C38 | F16 | 낡음 | R3.17(오른쪽 열) | 판정 "열림 … R3.17 의 서비스 사이 열이 —" 를 닫는다. 현행 R3.17 오른쪽 열: "계약 클라이언트는 UNAVAILABLE(연결 끊김·비 BoundaryError 408). 쓰기는 R10.8 로 같은 요청을 다시 보내도 안전". 칸 출력: "연결이 닫히거나 408 → OUT-CLIENT UNAVAILABLE. 이 호출은 읽기라 그대로 다시 보내면 된다".  |
| C38 | F17 | 낡음 | R10.4(영역 서비스는 429 대신 503)·CONVENTIONS 9절(클라이언트 Retry-After 전달) | 출력의 "CONVENTIONS 9절 마지막 문단은 '읽지 않는다'고 해 코드와 어긋난다 → 모순 M1" 을 지운다: 현행 CONVENTIONS 9절은 BoundaryError 본문 409·429·503 의 Retry-After 를 details.retry_after_s 로 넘긴다고 적었다(해소).  |
| C38 | F18 | 맞음 | CONVENTIONS 9절 표(400·422)·HTTP.md 공통(읽기 모드) | —(출력이 현행 조항과 같다) |
| C38 | F19 | 맞음 | HTTP.md I7(404) | —(출력이 현행 조항과 같다) |
| C38 | F20 | 낡음 | HTTP.md I7(get_review_trace 는 reviewer 전용) | model-lab 은 reviewer 전용 get_review_trace 를 부르지 않는다(OpsFeedbackReviewTrace 의 소비자는 admin-console, 읽기 토큰은 403). 이 칸을 "해당 없음: 읽기(get_case·list_cases·get_trace)는 서버 상태를 바꾸지 않아 재전송이 출력을 바꾸지 않는다(GET 안전·멱등, RFC 9110 9.2.2)" 로 바꾼다. |
| C38 | F21 | 맞음 | R3.10·R4.1 | —(출력이 현행 조항과 같다) |
| C38 | F22 | 맞음 | R3.11·R3.8 | —(출력이 현행 조항과 같다) |
| C38 | F23 | 맞음 | R4.6·R3.2·R3.15·R3.21 | —(출력은 맞다. 문장 끝의 "게시(C05·C07)는 …" 는 읽기 호출인 이 칸과 무관하므로 지워도 된다) |
| C38 | F24 | 낡음 | R3.25 | 판정 "열림"과 "RUNTIME 에는 본문 도중 끊김 행이 없다" 를 닫는다. 현행 R3.25: "UNAVAILABLE(details.reason=예외 종류). 읽은 부분을 값으로 쓰지 않고 tar 의 목적지를 남기지 않는다(RFC 9112 8). 같은 요청을 다시 보내면 된다". 출력은 그대로 맞다. |
| C38 | F25 | 맞음 | R6.4(웹 푸시뿐) | —(출력이 현행 조항과 같다) |
| C38 | F26 | 낡음 | R3.26 | 판정 "열림"과 "상한의 값과 초과 출력은 조항이 없다" 를 닫는다. 현행 R3.26: JSON·바이트 256MiB, tar 풀기 전 8GiB·항목 200,000개, 받는 스트림 8GiB+16MiB(여유는 근거 기록 없음), INTEGRITY_ERROR 재시도 안 함. |
| C38 | F27 | 맞음 | R10.5·R3.10 | —(출력이 현행 조항과 같다) |
| C39 | F01 | 낡음 | R3.1(오른쪽 열 UNAVAILABLE), R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F01 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F02 | 낡음 | R3.2, R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F02 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F03 | 낡음 | R3.3·R10.3(10초) | 출력 문장 끝의 "(3.4.4 정정 전 초안은 30초). 단 _http.py 기본 timeout 은 10초, 영역 설정(…)도 10초라 R10.3 과 어긋난다(M1)" 를 지운다: 현행 R10.3 이 10초라 어긋남이 없다. 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F03 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F04 | 낡음 | R3.14·R1.5·R1.8 (compose 밖) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F04 설명>" 으로 바꾼다(지금은 다른 호출의 문구). compose 밖 호출자는 자기 영역 게이트웨이(IN-EGRESS)에도 연결해야 하므로 출력에 "자기 게이트웨이에 닿지 못하면 R3.21, UNAVAILABLE" 를 더한다. |
| C39 | F05 | 낡음 | R3.14·R1.5(hosts 표) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F05 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F06 | 낡음 | R3.4(오른쪽 열)·R4.1·R3.21(자기 영역 게이트웨이) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F06 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 "자기 영역 게이트웨이(IN-EGRESS)가 멈춘 경우는 R3.21: UNAVAILABLE" 를 더한다(R1.8). |
| C39 | F07 | 낡음 | R3.16(오른쪽 열) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F07 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F08 | 낡음 | R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F08 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F09 | 낡음 | R1.2·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F09 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F10 | 낡음 | R1.3·R3.8·R1.7 | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F10 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F11 | 낡음 | R1.6·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F11 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F12 | 낡음 | R3.23(서비스 토큰: 받는 서비스가 401)·CONVENTIONS 9절(WWW-Authenticate: Bearer) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F12 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F13 | 낡음 | R3.24(서비스 토큰의 권한 밖은 받는 서비스가 403)·R1.8·R6.2(EGRESS_DENIED) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F13 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 R1.8 의 경우를 더한다: "자기 영역 게이트웨이가 이 호출 관계를 허용하지 않으면 CONNECT 403 → 클라이언트 PERMISSION_DENIED(details.reason=EGRESS_DENIED), 재시도 안 함". |
| C39 | F14 | 낡음 | R3.12(오른쪽 열: 기계 토큰 경로 출력 불변) | 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F14 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F15 | 맞음 | R3.5·R3.6(오른쪽 열 INVALID_RECORD) | —(출력이 현행 조항과 같다) |
| C39 | F16 | 낡음 | R3.17(오른쪽 열) | 판정 "열림 … R3.17 의 서비스 사이 열이 —" 를 닫는다. 현행 R3.17 오른쪽 열: "계약 클라이언트는 UNAVAILABLE(연결 끊김·비 BoundaryError 408). 쓰기는 R10.8 로 같은 요청을 다시 보내도 안전". 칸 출력: "연결이 닫히거나 408 → OUT-CLIENT UNAVAILABLE. 이 호출은 읽기라 그대로 다시 보내면 된다".  |
| C39 | F17 | 낡음 | R10.4(영역 서비스는 429 대신 503)·CONVENTIONS 9절(클라이언트 Retry-After 전달) | 출력의 "CONVENTIONS 9절 마지막 문단은 '읽지 않는다'고 해 코드와 어긋난다 → 모순 M1" 을 지운다: 현행 CONVENTIONS 9절은 BoundaryError 본문 409·429·503 의 Retry-After 를 details.retry_after_s 로 넘긴다고 적었다(해소).  |
| C39 | F18 | 낡음 | CONVENTIONS 9절 표(400·422)·HTTP.md 공통(읽기 모드) | 출력 끝의 "문항 세트 지정 누락은 400 QUESTION_SET_REQUIRED" 는 get_release_question_bank 에만 해당한다. 판정 조회(get_decision·find_decisions)에는 해당 없으므로 지운다. |
| C39 | F19 | 낡음 | HTTP.md I4(get_decision 404) | 출력에서 412(PASS 아닌 릴리스)·409 를 뺀다: 판정 조회는 get_decision(없으면 404 NOT_FOUND)과 find_decisions(없으면 빈 목록 200)뿐이다. 412 는 load_bundle·get_release_question_bank 에만 있다. 입력 열을 "model-lab 파이프라인(compose 밖) → release-gate(I4 읽기(판정 조회)): <F19 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C39 | F20 | 맞음 | RFC 9110 9.2.1·9.2.2(GET) | —(출력이 현행 조항과 같다) |
| C39 | F21 | 맞음 | R3.10·R4.1 | —(출력이 현행 조항과 같다) |
| C39 | F22 | 맞음 | R3.11·R3.8 | —(출력이 현행 조항과 같다) |
| C39 | F23 | 맞음 | R4.6·R3.2·R3.15·R3.21 | —(출력은 맞다. 문장 끝의 "게시(C05·C07)는 …" 는 읽기 호출인 이 칸과 무관하므로 지워도 된다) |
| C39 | F24 | 낡음 | R3.25 | 판정 "열림"과 "RUNTIME 에는 본문 도중 끊김 행이 없다" 를 닫는다. 현행 R3.25: "UNAVAILABLE(details.reason=예외 종류). 읽은 부분을 값으로 쓰지 않고 tar 의 목적지를 남기지 않는다(RFC 9112 8). 같은 요청을 다시 보내면 된다". 출력은 그대로 맞다. |
| C39 | F25 | 맞음 | R6.4(웹 푸시뿐) | —(출력이 현행 조항과 같다) |
| C39 | F26 | 낡음 | R3.26 | 판정 "열림"과 "상한의 값과 초과 출력은 조항이 없다" 를 닫는다. 현행 R3.26: JSON·바이트 256MiB, tar 풀기 전 8GiB·항목 200,000개, 받는 스트림 8GiB+16MiB(여유는 근거 기록 없음), INTEGRITY_ERROR 재시도 안 함. 손상 쪽 문장을 이 호출에 맞춘다: 판정 조회는 GateDecision 스키마·content_hash 검증(번들·문항 세트 해시가 아님). |
| C39 | F27 | 맞음 | R10.5·R3.10 | —(출력이 현행 조항과 같다) |
| C40 | F01 | 낡음 | R3.1(오른쪽 열 UNAVAILABLE), R4.1 | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F01 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F02 | 낡음 | R3.2, R4.1; R4.6(추론 서버 적재는 재시작을 넘지 않음) | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F02 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F03 | 계약 빈칸 | R10.3(10초), CONVENTIONS 사슬 표(survey-service → model-runtime 21/26초 행) | model-lab 의 추론 호출(extract/respond 평가)은 사슬 표에 없어 R10.3 의 10초가 적용되는데 서버 상한은 extract 20초·respond 25초라 정상 응답이 10초에 끊긴다. CONVENTIONS 시간 상한 사슬 표의 해당 행을 "추론 서버 호출자(survey-service·model-lab) → model-runtime 클라이언트 읽기 상한 | extract 21초, respond 26초 | 서버 상한보다 1초 길다" 로 호출자를 넓힌다(근거: 서버가 먼저 503 을 내게). 칸 출력은 "model-lab 은 21/26초, 정보·준비 호출은 R10.3 의 10초" 로. 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F03 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F04 | 낡음 | R3.14·R1.5·R1.8 (compose 밖) | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F04 설명>" 으로 바꾼다(지금은 다른 호출의 문구). compose 밖 호출자는 자기 영역 게이트웨이(IN-EGRESS)에도 연결해야 하므로 출력에 "자기 게이트웨이에 닿지 못하면 R3.21, UNAVAILABLE" 를 더한다. |
| C40 | F05 | 낡음 | R3.14·R1.5(hosts 표) | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F05 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F06 | 낡음 | R3.4(오른쪽 열)·R4.1·R3.21(자기 영역 게이트웨이) | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F06 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 "자기 영역 게이트웨이(IN-EGRESS)가 멈춘 경우는 R3.21: UNAVAILABLE" 를 더한다(R1.8). |
| C40 | F07 | 낡음 | R3.16(오른쪽 열)·HTTP.md I9 큐 거절 | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F07 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F08 | 낡음 | R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F08 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F09 | 낡음 | R1.2·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F09 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F10 | 낡음 | R1.3·R3.8·R1.7 | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F10 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F11 | 낡음 | R1.6·R1.3·R3.8 | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F11 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F12 | 낡음 | R3.23(서비스 토큰: 받는 서비스가 401)·CONVENTIONS 9절(WWW-Authenticate: Bearer) | 판정 "열림 (O8)" 과 "HTTP.md I9 의 오류 목록에 401 이 없다 → 모순(M3)" 문장을 지운다: 현행 HTTP.md I9 는 "401 토큰 없음·틀림 + WWW-Authenticate: Bearer" 를 적었다(닫힘). 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F12 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F13 | 낡음 | R3.24(서비스 토큰의 권한 밖은 받는 서비스가 403)·R1.8·R6.2(EGRESS_DENIED) | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F13 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 R1.8 의 경우를 더한다: "자기 영역 게이트웨이가 이 호출 관계를 허용하지 않으면 CONNECT 403 → 클라이언트 PERMISSION_DENIED(details.reason=EGRESS_DENIED), 재시도 안 함". |
| C40 | F14 | 낡음 | R3.12(오른쪽 열: 기계 토큰 경로 출력 불변) | 입력 열을 "model-lab 파이프라인(compose 밖) → 추론 서버(model-runtime)(I9 정보·준비·평가 호출): <F14 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C40 | F15 | 맞음 | R3.5·R3.6(오른쪽 열 INVALID_RECORD) | —(출력이 현행 조항과 같다) |
| C40 | F16 | 낡음 | R3.17(오른쪽 열) | 판정 "열림 … R3.17 의 서비스 사이 열이 —" 를 닫는다. 현행 R3.17 오른쪽 열: "계약 클라이언트는 UNAVAILABLE(연결 끊김·비 BoundaryError 408). 쓰기는 R10.8 로 같은 요청을 다시 보내도 안전". 칸 출력: "연결이 닫히거나 408 → OUT-CLIENT UNAVAILABLE. 이 호출은 읽기(추론 호출은 부작용 없음)라 그대로 다시 보내면 된다".  |
| C40 | F17 | 낡음 | R10.4(영역 서비스는 429 대신 503)·CONVENTIONS 9절(클라이언트 Retry-After 전달) | 출력의 "CONVENTIONS 9절 마지막 문단은 '읽지 않는다'고 해 코드와 어긋난다 → 모순 M1" 을 지운다: 현행 CONVENTIONS 9절은 BoundaryError 본문 409·429·503 의 Retry-After 를 details.retry_after_s 로 넘긴다고 적었다(해소).  |
| C40 | F18 | 계약 빈칸 | CONVENTIONS 9절 표(400·422)·HTTP.md 공통(읽기 모드) | C40 의 평가 호출이 HTTP.md I9 의 어느 경로인지 정해져 있지 않다(위 G4). 면이 정해지면 이 칸은 extract/respond 문장 그대로 맞다. |
| C40 | F19 | 계약 빈칸 | HTTP.md I9, R4.6 | C40 의 평가 호출 면이 정의되지 않았다(위 G4). 면이 정해지기 전에는 이 칸의 PUT/extract 출력이 model-lab 에 적용되는지 알 수 없다. |
| C40 | F20 | 계약 빈칸 | HTTP.md I9 | C40 의 호출 면이 정해져야 이 칸을 판정할 수 있다(위 G4). 정해지면 PUT 은 멱등, extract·respond 는 부작용 없음이 맞다(HTTP.md I9 129줄). |
| C40 | F21 | 맞음 | R3.10(추론 서버는 DB 없음) | —(출력이 현행 조항과 같다) |
| C40 | F22 | 맞음 | R3.11·R3.8 | —(출력이 현행 조항과 같다) |
| C40 | F23 | 계약 빈칸 | R4.6·R3.2·R3.15·R3.21 | 호출자(survey-service)로 쓴 문장을 model-lab 에 맞추려면 평가 호출 면(위 G4)이 먼저 정해져야 한다. R4.6 은 "호출자가 PUT 으로 다시 적재한다" 라고만 적었다. |
| C40 | F24 | 낡음 | R3.25 | 판정 "열림"과 "RUNTIME 에는 본문 도중 끊김 행이 없다" 를 닫는다. 현행 R3.25: "UNAVAILABLE(details.reason=예외 종류). 읽은 부분을 값으로 쓰지 않고 tar 의 목적지를 남기지 않는다(RFC 9112 8). 같은 요청을 다시 보내면 된다". 출력은 그대로 맞다. |
| C40 | F25 | 맞음 | R6.4(웹 푸시뿐) | —(출력이 현행 조항과 같다) |
| C40 | F26 | 낡음 | R3.26 | 판정 "열림"과 "상한의 값과 초과 출력은 조항이 없다" 를 닫는다. 현행 R3.26: JSON·바이트 256MiB, tar 풀기 전 8GiB·항목 200,000개, 받는 스트림 8GiB+16MiB(여유는 근거 기록 없음), INTEGRITY_ERROR 재시도 안 함. |
| C40 | F27 | 맞음 | R10.5·R3.10 | —(출력이 현행 조항과 같다) |
| C41 | F01 | 낡음 | R3.1(오른쪽 열 UNAVAILABLE), R4.1 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F01 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F02 | 낡음 | R3.2, R4.1 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F02 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F03 | 낡음 | R3.3·R10.3(10초) | 출력 문장 끝의 "(3.4.4 정정 전 초안은 30초). 단 _http.py 기본 timeout 은 10초, 영역 설정(…)도 10초라 R10.3 과 어긋난다(M1)" 를 지운다: 현행 R10.3 이 10초라 어긋남이 없다. 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F03 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F04 | 낡음 | R3.14 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F04 설명>" 으로 바꾼다(지금은 다른 호출의 문구).  |
| C41 | F05 | 낡음 | R3.14·R1.4 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F05 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F06 | 낡음 | R3.4(오른쪽 열)·R4.1 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F06 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F07 | 낡음 | R3.16(오른쪽 열) | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F07 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F08 | 낡음 | R1.3·R3.8 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F08 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F09 | 낡음 | R1.2·R1.3·R3.8 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F09 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F10 | 낡음 | R1.3·R3.8·R1.7 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F10 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F11 | 낡음 | R1.6·R1.3·R3.8 | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F11 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F12 | 낡음 | R3.23(서비스 토큰: 받는 서비스가 401)·CONVENTIONS 9절(WWW-Authenticate: Bearer) | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F12 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F13 | 낡음 | R3.24(서비스 토큰의 권한 밖은 받는 서비스가 403)·R1.8·R6.2(EGRESS_DENIED) | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F13 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 R1.8 의 경우를 더한다: "자기 영역 게이트웨이가 이 호출 관계를 허용하지 않으면 CONNECT 403 → 클라이언트 PERMISSION_DENIED(details.reason=EGRESS_DENIED), 재시도 안 함". |
| C41 | F14 | 낡음 | R3.12(오른쪽 열: 기계 토큰 경로 출력 불변) | 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F14 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F15 | 맞음 | R3.5·R3.6(오른쪽 열 INVALID_RECORD) | —(출력이 현행 조항과 같다) |
| C41 | F16 | 낡음 | R3.17(오른쪽 열) | 판정 "열림 … R3.17 의 서비스 사이 열이 —" 를 닫는다. 현행 R3.17 오른쪽 열: "계약 클라이언트는 UNAVAILABLE(연결 끊김·비 BoundaryError 408). 쓰기는 R10.8 로 같은 요청을 다시 보내도 안전". 칸 출력: "연결이 닫히거나 408 → OUT-CLIENT UNAVAILABLE. 이 호출은 읽기라 그대로 다시 보내면 된다".  |
| C41 | F17 | 낡음 | R10.4(영역 서비스는 429 대신 503)·CONVENTIONS 9절(클라이언트 Retry-After 전달) | 출력의 "CONVENTIONS 9절 마지막 문단은 '읽지 않는다'고 해 코드와 어긋난다 → 모순 M1" 을 지운다: 현행 CONVENTIONS 9절은 BoundaryError 본문 409·429·503 의 Retry-After 를 details.retry_after_s 로 넘긴다고 적었다(해소).  |
| C41 | F18 | 낡음 | CONVENTIONS 9절 표(400·422)·HTTP.md 공통(읽기 모드) | 출력 끝의 "문항 세트 지정 누락은 400 QUESTION_SET_REQUIRED" 는 get_release_question_bank 에만 해당한다. 판정 조회(get_decision·find_decisions)에는 해당 없으므로 지운다. |
| C41 | F19 | 낡음 | HTTP.md I4(get_decision 404) | 출력에서 412(PASS 아닌 릴리스)·409 를 뺀다: 판정 조회는 get_decision(없으면 404 NOT_FOUND)과 find_decisions(없으면 빈 목록 200)뿐이다. 412 는 load_bundle·get_release_question_bank 에만 있다. 입력 열을 "question-authoring → release-gate(I4 읽기(판정 조회)): <F19 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C41 | F20 | 맞음 | RFC 9110 9.2.1·9.2.2(GET) | —(출력이 현행 조항과 같다) |
| C41 | F21 | 맞음 | R3.10·R4.1 | —(출력이 현행 조항과 같다) |
| C41 | F22 | 맞음 | R3.11·R3.8 | —(출력이 현행 조항과 같다) |
| C41 | F23 | 맞음 | R4.6·R3.2·R3.15·R3.21 | —(출력은 맞다. 문장 끝의 "게시(C05·C07)는 …" 는 읽기 호출인 이 칸과 무관하므로 지워도 된다) |
| C41 | F24 | 낡음 | R3.25 | 판정 "열림"과 "RUNTIME 에는 본문 도중 끊김 행이 없다" 를 닫는다. 현행 R3.25: "UNAVAILABLE(details.reason=예외 종류). 읽은 부분을 값으로 쓰지 않고 tar 의 목적지를 남기지 않는다(RFC 9112 8). 같은 요청을 다시 보내면 된다". 출력은 그대로 맞다. |
| C41 | F25 | 맞음 | R6.4(웹 푸시뿐) | —(출력이 현행 조항과 같다) |
| C41 | F26 | 낡음 | R3.26 | 판정 "열림"과 "상한의 값과 초과 출력은 조항이 없다" 를 닫는다. 현행 R3.26: JSON·바이트 256MiB, tar 풀기 전 8GiB·항목 200,000개, 받는 스트림 8GiB+16MiB(여유는 근거 기록 없음), INTEGRITY_ERROR 재시도 안 함. 손상 쪽 문장을 이 호출에 맞춘다: 판정 조회는 GateDecision 스키마·content_hash 검증(번들·문항 세트 해시가 아님). |
| C41 | F27 | 맞음 | R10.5·R3.10 | —(출력이 현행 조항과 같다) |
| C42 | F01 | 낡음 | R3.1(오른쪽 열 UNAVAILABLE), R4.1 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F01 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F02 | 낡음 | R3.2, R4.1; R4.6(추론 서버 적재는 재시작을 넘지 않음) | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F02 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F03 | 낡음 | R3.3·R10.3(10초) | C42 는 정보·준비(GET)만 부르므로 extract/respond 상한(20/25, 21/26초)을 칸에서 뺀다. 출력: "OUT-CLIENT UNAVAILABLE(소켓 단위 timeout 초과, 호출자 설정이 없으면 R10.3 의 10초)". 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F03 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F04 | 낡음 | R3.14 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F04 설명>" 으로 바꾼다(지금은 다른 호출의 문구).  |
| C42 | F05 | 낡음 | R3.14·R1.4 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F05 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F06 | 낡음 | R3.4(오른쪽 열)·R4.1 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F06 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F07 | 낡음 | R3.16(오른쪽 열)·HTTP.md I9 큐 거절 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F07 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F08 | 낡음 | R1.3·R3.8 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F08 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F09 | 낡음 | R1.2·R1.3·R3.8 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F09 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F10 | 낡음 | R1.3·R3.8·R1.7 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F10 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F11 | 낡음 | R1.6·R1.3·R3.8 | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F11 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F12 | 낡음 | R3.23(서비스 토큰: 받는 서비스가 401)·CONVENTIONS 9절(WWW-Authenticate: Bearer) | 판정 "열림 (O8)" 과 "HTTP.md I9 의 오류 목록에 401 이 없다 → 모순(M3)" 문장을 지운다: 현행 HTTP.md I9 는 "401 토큰 없음·틀림 + WWW-Authenticate: Bearer" 를 적었다(닫힘). 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F12 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F13 | 낡음 | R3.24(서비스 토큰의 권한 밖은 받는 서비스가 403)·R1.8·R6.2(EGRESS_DENIED) | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F13 설명>" 으로 바꾼다(지금은 다른 호출의 문구). 출력에 R1.8 의 경우를 더한다: "자기 영역 게이트웨이가 이 호출 관계를 허용하지 않으면 CONNECT 403 → 클라이언트 PERMISSION_DENIED(details.reason=EGRESS_DENIED), 재시도 안 함". |
| C42 | F14 | 낡음 | R3.12(오른쪽 열: 기계 토큰 경로 출력 불변) | 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F14 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F15 | 맞음 | R3.5·R3.6(오른쪽 열 INVALID_RECORD) | —(출력이 현행 조항과 같다) |
| C42 | F16 | 낡음 | R3.17(오른쪽 열) | 판정 "열림 … R3.17 의 서비스 사이 열이 —" 를 닫는다. 현행 R3.17 오른쪽 열: "계약 클라이언트는 UNAVAILABLE(연결 끊김·비 BoundaryError 408). 쓰기는 R10.8 로 같은 요청을 다시 보내도 안전". 칸 출력: "연결이 닫히거나 408 → OUT-CLIENT UNAVAILABLE. 이 호출은 읽기라 그대로 다시 보내면 된다".  |
| C42 | F17 | 낡음 | R10.4(영역 서비스는 429 대신 503)·CONVENTIONS 9절(클라이언트 Retry-After 전달) | 출력의 "CONVENTIONS 9절 마지막 문단은 '읽지 않는다'고 해 코드와 어긋난다 → 모순 M1" 을 지운다: 현행 CONVENTIONS 9절은 BoundaryError 본문 409·429·503 의 Retry-After 를 details.retry_after_s 로 넘긴다고 적었다(해소).  |
| C42 | F18 | 낡음 | CONVENTIONS 9절 표(400·422)·HTTP.md 공통(읽기 모드) | C42 는 GET info/readyz 만 부르므로 ExtractRequest·ResponseRequest 위반·OUTPUT_INVALID 문장을 뺀다. 출력: "응답 RuntimeInfo/ReleaseLoadStatus 가 스키마를 어기면 INTEGRITY_ERROR(재시도 안 함)". 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F18 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F19 | 낡음 | HTTP.md I9(적재 상태 GET) | C42 는 GET /v1/releases/{id}·GET /v1/info 만 부른다. 적재되지 않은 릴리스의 상태 조회는 404 가 아니라 200 {"state":"ABSENT"} 이다(HTTP.md I9). 출력: "200 ABSENT, 호환 검사 대상 아님". PUT 의 412·422 와 extract 404 문장은 뺀다. 입력 열을 "release-gate → 추론 서버(model-runtime)(I9 정보·준비(호환 검사)): <F19 설명>" 으로 바꾼다(지금은 다른 호출의 문구). |
| C42 | F20 | 낡음 | RFC 9110 9.2.1(안전한 GET) | C42 는 GET 뿐이므로 "해당 없음: GET 은 안전·멱등" 으로 바꾼다(PUT·extract·respond 문장 삭제). |
| C42 | F21 | 맞음 | R3.10(추론 서버는 DB 없음) | —(출력이 현행 조항과 같다) |
| C42 | F22 | 맞음 | R3.11·R3.8 | —(출력이 현행 조항과 같다) |
| C42 | F23 | 낡음 | R4.6·R3.2·R3.15·R3.21 | C42 의 호출자는 release-gate 이고 적재 `PUT` 을 하지 않는다. 출력: "재시작 동안 UNAVAILABLE. 복귀 뒤 GET /v1/releases/{id} 는 200 state=ABSENT(적재 상태는 재시작을 넘지 않음, R4.6); 호환 검사는 GET /v1/info 로 계속". survey-service 가 PUT 으로 다시 적재한다는 문장은 이 호출의 것이 아니다. |
| C42 | F24 | 낡음 | R3.25 | 판정 "열림"과 "RUNTIME 에는 본문 도중 끊김 행이 없다" 를 닫는다. 현행 R3.25: "UNAVAILABLE(details.reason=예외 종류). 읽은 부분을 값으로 쓰지 않고 tar 의 목적지를 남기지 않는다(RFC 9112 8). 같은 요청을 다시 보내면 된다". 출력은 그대로 맞다. |
| C42 | F25 | 맞음 | R6.4(웹 푸시뿐) | —(출력이 현행 조항과 같다) |
| C42 | F26 | 낡음 | R3.26 | 판정 "열림"과 "상한의 값과 초과 출력은 조항이 없다" 를 닫는다. 현행 R3.26: JSON·바이트 256MiB, tar 풀기 전 8GiB·항목 200,000개, 받는 스트림 8GiB+16MiB(여유는 근거 기록 없음), INTEGRITY_ERROR 재시도 안 함. |
| C42 | F27 | 맞음 | R10.5·R3.10 | —(출력이 현행 조항과 같다) |
