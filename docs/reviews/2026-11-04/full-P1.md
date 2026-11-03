대조한 칸 210 / 몫의 전체 칸 210 / 결함 칸 34 (낡음 23, 계약 빈칸 9, 모순 2; 맞음 176). 몫 P1 = CELLS 묶음 2(F08~F14) 전부, 완료.

기준: boundary-contracts wo-320 커밋 1bbf6dd(3.4.4). 읽은 것: RUNTIME.md 1~171줄 전부, RUNTIME-MATRIX.md A·B, RUNTIME-MATRIX-CELLS.md 1~45줄(머리·대응표)과 묶음 2 전체(261~475줄, 210칸), CONVENTIONS.md 6절·9절·13절·시간 상한 사슬, HTTP.md I9·401/403 문장, PUBLIC_API.md E·F·G절 발췌, `schemas/Exposure.schema.json`, `boundary_contracts/clients/_http.py`(오류 매핑·egress), survey-service `components/link_push.py`(읽기만). 읽지 않음: PUBLIC_API.md 의 나머지 절, INTERFACES.md 전문, 각 Env 스키마 전문.
판정 기준: 맞음 = 현행 조항이 출력을 정하고 칸이 같다(판정 열의 "열림 (On)" 표시는 대응표로 닫혔으므로 갱신만 필요한 것은 맞음으로 두고 고칠 것에 적었다). 낡음 = 칸의 출력·입력이 현행 조항·호출 목록과 다르다. 계약 빈칸 = 현행 계약에 출력이 없다. 모순 = 두 문장이 부딪친다. C24 는 칸마다 "영역 내부로 뺌" 표시만 확인했다(7칸 모두 표시 있음).

## 결함 요약
- 낡음 23칸: C13 F08~F11(4, "게이트웨이 기계 입구" 문구), C15 F11·F12(2, 이미 해소된 M2 를 모순으로 적음), C34 F08~F13(6, 칸이 HTTP 호출 모델인데 현행 C34 는 deploy 가 띄우는 잡), C01·C02·C09·C10·C16·C17·C19 F12(7, `WWW-Authenticate` 누락·C09 의 submit 오기·C16/C17 의 SSE 닫힘 문장이 R2.4 와 다름), C11 F12·C14 F12(2, 해소된 모순을 열림으로 적음), C16·C17 F14(2, 새 SSE 연결 503 문장).
- 계약 빈칸 9칸: C23 F08~F11(K1), C30 F08~F11(K2), C29 F12(K4).
- 모순 2칸: C13 F12·F13(K3).

## 표

| 호출 | 실패 | 판정(맞음/낡음/계약 빈칸/모순) | 현행 조항 | 고칠 것(그대로 넣을 문장 또는 칸 갱신 문장) |
|---|---|---|---|---|
| C01 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C01 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C01 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C01 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C01 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). |
| C01 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C01 | F14 | 맞음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1 | — |
| C02 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C02 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C02 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C02 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C02 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). |
| C02 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C02 | F14 | 맞음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1 | — |
| C03 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C03 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C03 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C03 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C03 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C03 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C03 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C04 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C04 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C04 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C04 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C04 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C04 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C04 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C05 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C05 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C05 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C05 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C05 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — 쓰기는 일어나지 않는다. |
| C05 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — 아무것도 저장하지 않는다. |
| C05 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C06 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C06 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C06 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C06 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C06 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C06 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C06 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C07 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C07 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C07 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C07 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — compose 밖 호출자(C06·C07)도 같다(R1.5·R1.7). |
| C07 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — 쓰기는 일어나지 않는다. |
| C07 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — 아무것도 저장하지 않는다. |
| C07 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C08 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C08 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C08 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C08 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C08 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C08 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C08 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C09 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C09 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C09 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C09 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C09 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). (3) "activate·rollback·submit 에 `X-Openit-User` 가 없으면 401"에서 submit 을 뺀다: CONVENTIONS 9절이 `X-Openit-User` 를 요구하는 것은 approvals·activate·rollback·cases/{id}/review 뿐이고 `POST /v1/submissions` 는 역할(`requested_by_role`)로만 판정한다(INTERFACES I5, HTTP.md I5). 이 헤더가 없는 401 도 `Bearer realm="openit"`(R3.23). |
| C09 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C09 | F14 | 맞음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1 | — |
| C10 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C10 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C10 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C10 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C10 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). `POST /v1/approvals` 에 `X-Openit-User` 가 없는 401 도 `WWW-Authenticate: Bearer realm="openit"`(R3.23). |
| C10 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C10 | F14 | 맞음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1 | — |
| C11 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C11 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C11 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C11 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C11 | F12 | 낡음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401]; CONVENTIONS 9절 "서비스 역할 토큰(`GATE_SERVICE_ROLES`, 기본 `ops-feedback`)으로 오는 기계 호출의 activate·rollback 은 이 헤더 없이 받고 행위자를 `service:<역할>`로 기록"; R10.9 | 판정 열 "열림 (O7)"과 출력의 "모순(M1) → 붙일 행 O7"이 낡았다(CONVENTIONS 9절·R10.9 가 맞춰졌다). 갱신: "토큰 없음·틀림: 401 + `WWW-Authenticate: Bearer` → `PERMISSION_DENIED`(http_status=401), 재시도 안 함. 토큰이 서비스 역할(ops-feedback)이면 `X-Openit-User` 없이 받는다(행위자 `service:ops-feedback`)". |
| C11 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — 활성 포인터는 바뀌지 않는다. |
| C11 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C12 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C12 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C12 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C12 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C12 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C12 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C12 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C13 | F08 | 낡음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | 칸의 입력 "(게이트웨이 기계 입구 또는 직접)"과 출력 "게이트웨이 기계 입구를 거치면 게이트웨이↔release-gate 구간의 실패는 503 UU"는 낡았다(RUNTIME-MATRIX A 의 C13 은 "추론 서버 → release-gate", 호출 영역 게이트웨이 → 받는 영역 게이트웨이). 두 문장을 지우고 출력은 "계약 클라이언트의 결과 `UNAVAILABLE`(재시도 가능; TLS 검증 실패는 URLError/OSError → UNAVAILABLE, _http.py `_open`)"만 남긴다. |
| C13 | F09 | 낡음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | 칸의 입력 "(게이트웨이 기계 입구 또는 직접)"과 출력 "게이트웨이 기계 입구를 거치면 게이트웨이↔release-gate 구간의 실패는 503 UU"는 낡았다(RUNTIME-MATRIX A 의 C13 은 "추론 서버 → release-gate", 호출 영역 게이트웨이 → 받는 영역 게이트웨이). 두 문장을 지우고 출력은 "계약 클라이언트의 결과 `UNAVAILABLE`(재시도 가능; TLS 검증 실패는 URLError/OSError → UNAVAILABLE, _http.py `_open`)"만 남긴다. |
| C13 | F10 | 낡음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | 칸의 입력 "(게이트웨이 기계 입구 또는 직접)"과 출력 "게이트웨이 기계 입구를 거치면 게이트웨이↔release-gate 구간의 실패는 503 UU"는 낡았다(RUNTIME-MATRIX A 의 C13 은 "추론 서버 → release-gate", 호출 영역 게이트웨이 → 받는 영역 게이트웨이). 두 문장을 지우고 출력은 "계약 클라이언트의 결과 `UNAVAILABLE`(재시도 가능; TLS 검증 실패는 URLError/OSError → UNAVAILABLE, _http.py `_open`)"만 남긴다. |
| C13 | F11 | 낡음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | 칸의 입력 "(게이트웨이 기계 입구 또는 직접)"과 출력 "게이트웨이 기계 입구를 거치면 게이트웨이↔release-gate 구간의 실패는 503 UU"는 낡았다(RUNTIME-MATRIX A 의 C13 은 "추론 서버 → release-gate", 호출 영역 게이트웨이 → 받는 영역 게이트웨이). 두 문장을 지우고 출력은 "계약 클라이언트의 결과 `UNAVAILABLE`(재시도 가능; TLS 검증 실패는 URLError/OSError → UNAVAILABLE, _http.py `_open`)"만 남긴다. |
| C13 | F12 | 모순 | R3.23 "앱 앞에서 토큰을 대조하는 것은 `Exposure.auth.kind=machine-token` 경로뿐" 대 RUNTIME-MATRIX A C13 "추론 서버 → release-gate"(모든 서비스 호출은 호출 영역 게이트웨이 → 받는 영역 게이트웨이) | K3: R3.23 은 machine-token 경로의 게이트웨이를 말하지만 그 게이트웨이가 어느 쪽(platform 공개 입구인지 받는 영역 게이트웨이인지)이고 거절 본문이 무엇인지 정하지 않는다. 비 `BoundaryError` 401 이면 `_http.py` `_map_error` 가 `UNAVAILABLE` 로 읽어 재시도 루프가 된다. 칸의 "게이트웨이 기계 입구" 문구도 낡았다. K3 문장으로 고친다. |
| C13 | F13 | 모순 | R3.24 "서비스 토큰의 권한 밖은 받는 서비스가 403" 대 R3.23/Exposure `machine-token`(게이트웨이가 토큰 대조) 대 MATRIX A C13 | K3 와 같다(machine-token 경로의 거절 주체와 본문). 칸의 "게이트웨이 기계 입구" 문구는 낡았다. |
| C13 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — 괄호 "(게이트웨이 기계 입구도 토큰 대조만 한다)"는 낡았으니 지운다. |
| C14 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C14 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C14 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C14 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C14 | F12 | 낡음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401]; HTTP.md I9 "오류는 … 400 …, 401 토큰 없음·틀림 + `WWW-Authenticate: Bearer`, 403, 404, 412, 422, 503" | 출력은 현행과 같다. "HTTP.md I9 의 오류 목록에 401 이 없다 → 모순(M3), 붙일 행 O8"은 낡았다(I9 에 401 이 들어갔다). 그 문장을 지운다. |
| C14 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C14 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C15 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — |
| C15 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — |
| C15 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — |
| C15 | F11 | 낡음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; R3.13; R3.15 | 칸의 (c)·판정 열의 "R3.13 과 R3.15·R10.6 모순(M2)"은 낡았다. R3.13 이 기기 인증서 거절(OUT-NET)을 "R3.15 와 같이 같은 `turn_id` 로 재시도, 총 예산 120초 뒤 직원 호출 화면"으로 고쳤다. (c) 를 이렇게 갱신: "기기 시계 어긋남으로 기기 인증서가 아직 유효 전·만료로 판정됨: TLS 단계 거부 = OUT-NET → 키오스크는 같은 `turn_id` 로 재시도하고 총 예산 120초 뒤 직원 호출 화면(R3.13)". |
| C15 | F12 | 낡음 | R3.13 "기기 토큰: 401, 본문은 `BoundaryError` 전체 필드(R3.23) … 기기 인증서(검증을 켠 배포): TLS 핸드셰이크 거부 = OUT-NET … 키오스크는 R3.15 와 같이 같은 `turn_id` 로 재시도하고 총 예산 120초 뒤 직원 호출 화면"; PUBLIC_API "401(기기 인증 실패)은 재시도 없이 직원 호출 화면" | "R3.13 은 후자도 '재시도 없이'라 하나 … 모순(M2) → 붙일 행 O6"은 낡았다(R3.13 이 고쳐졌다). 갱신: "기기 토큰: 401 + BoundaryError 전체 필드(+`WWW-Authenticate: Bearer`), 재시도 없이 직원 호출 화면. 기기 인증서 거절: OUT-NET → 같은 `turn_id` 로 재시도, 총 예산 120초 뒤 직원 호출 화면". |
| C15 | F13 | 맞음 | PUBLIC_API G절 "다른 기기는 404, 직원 토큰은 403"; R3.24 우측 열; CONVENTIONS 9절 | — |
| C15 | F14 | 맞음 | R3.13; R3.12(사람 경로에만 적용) | 해당 없음 판정이 맞다(기기 인증은 platform 사람 인증 확인을 거치지 않는다). |
| C16 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C16 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C16 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C16 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C16 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). (3) "인증이 만료·철회되면 서버가 열린 SSE 를 닫고"는 R2.4 와 다르다: 스트림은 인증 만료 신호를 받지 않고 서버가 최대 수명(`SURVEY_SSE_MAX_SECONDS`, 기본 300초)에 정상 종료하며 platform 공개 입구도 세션이 끝나면 자기 쪽 연결을 닫을 수 있다. 다음 연결의 출력이 401(R3.23). |
| C16 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C16 | F14 | 낡음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1; R2.4 "스트림의 최대 수명 … 그 시각에 정상 종료" | 칸의 "새 SSE 연결은 503 UU"는 R3.12 의 "이미 맺은 로그인 세션은 쿠키 수명까지 유지"와 맞지 않는다. 갱신: "이미 맺은 세션의 요청(새 SSE 연결 포함)은 평소 출력을 받는다. 열린 스트림은 R2.4 의 최대 수명에 정상 종료한다. 유효한 세션이 없는 요청만 503 UU(+`Retry-After`)이고 클라이언트는 `Retry-After` 를 따라 지수 백오프로 다시 잇는다". (R3.12 요청 구분 보충은 X1) |
| C17 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C17 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C17 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C17 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C17 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). (3) "인증이 만료·철회되면 서버가 열린 SSE 를 닫고"는 R2.4 와 다르다: 스트림은 인증 만료 신호를 받지 않고 서버가 최대 수명(`SURVEY_SSE_MAX_SECONDS`, 기본 300초)에 정상 종료하며 platform 공개 입구도 세션이 끝나면 자기 쪽 연결을 닫을 수 있다. 다음 연결의 출력이 401(R3.23). |
| C17 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C17 | F14 | 낡음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1; R2.4 "스트림의 최대 수명 … 그 시각에 정상 종료" | 칸의 "새 SSE 연결은 503 UU"는 R3.12 의 "이미 맺은 로그인 세션은 쿠키 수명까지 유지"와 맞지 않는다. 갱신: "이미 맺은 세션의 요청(새 SSE 연결 포함)은 평소 출력을 받는다. 열린 스트림은 R2.4 의 최대 수명에 정상 종료한다. 유효한 세션이 없는 요청만 503 UU(+`Retry-After`)이고 클라이언트는 `Retry-After` 를 따라 지수 백오프로 다시 잇는다". (R3.12 요청 구분 보충은 X1) |
| C18 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C18 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C18 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C18 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C18 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — 쓰기는 일어나지 않는다. |
| C18 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — 아무것도 저장하지 않는다. |
| C18 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C19 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C19 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C19 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C19 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C19 | F12 | 낡음 | R3.23 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 답한다 … `/v1/` 경로: 401, 본문 `BoundaryError` 전체 필드 … 모든 401 은 `WWW-Authenticate` 를 갖는다(… 로그인 세션(쿠키) 경로는 `Bearer realm="openit"`) … 화면 경로 GET + `Accept: text/html` 이면 302 `Location`" | 출력이 R3.23 과 어긋난 곳을 갱신한다: (1) `/v1/` 401 에 `WWW-Authenticate: Bearer realm="openit"`(쿠키 세션 경로)를 더한다(칸에 없음). (2) 판정 열 "열림 (O1)·현재 계약에 없다"는 낡았다(R3.23 이 닫음). `cases/{id}/review` 에 `X-Openit-User` 가 없는 401 도 `Bearer realm="openit"`. |
| C19 | F13 | 맞음 | R3.24 "사람 요청은 platform 공개 입구가 앱에 넘기지 않고 403, 서비스 토큰의 권한 밖은 받는 서비스가 403 … 본문 `BoundaryError` 전체 필드 … 역할이 하나도 없으면 `details.reason=ACCOUNT_PENDING_APPROVAL` … 예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면"; CONVENTIONS 6절 | 출력은 현행과 같다. 판정 열 "열림 (O2)"·"모순(M4)"은 R3.24 와 CONVENTIONS 6절 정정으로 닫혔다(갱신: 닫힘). |
| C19 | F14 | 맞음 | R3.12 "사람 경로: 503 UU(401·로그인 화면 이동 아님, 계정 관리가 낸 오류 본문은 호출자에게 가지 않는다). 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"; R10.2; R4.1 | — |
| C20 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C20 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C20 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C20 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C20 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C20 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C20 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C21 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C21 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C21 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C21 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C21 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C21 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C21 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C22 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C22 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C22 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C22 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; _http.py `_open`(OSError→UNAVAILABLE) | — |
| C22 | F12 | 맞음 | R3.23 우측 열 "`PERMISSION_DENIED`(`details.http_status`=401), 재시도하지 않는다"; CONVENTIONS 9절 "토큰이 없거나 틀리면 401 … `WWW-Authenticate: Bearer`"; _http.py `_STATUS_CODE`[401] | — |
| C22 | F13 | 맞음 | R3.24 우측 열 "`PERMISSION_DENIED`(`details.http_status`=403), 재시도하지 않는다"; CONVENTIONS 9절; HTTP.md 공통 "읽기 토큰은 쓰기 경로를 호출할 수 없다"; _http.py `_STATUS_CODE`[403] | — |
| C22 | F14 | 맞음 | R3.12 우측 열 "기계 토큰 경로: 출력이 바뀌지 않는다" | — |
| C23 | F08 | 계약 빈칸 | R3.18 "(불통·느림·429·5xx·404·410·이름 해석·TLS 검증)"의 입력 목록에는 있으나 출력은 상태 코드별(404·410·429·5xx·401·403·그 밖의 4xx)만 있다 | K1: R3.18 은 TLS 검증 실패를 다시 보내는지 정하지 않는다. 칸의 "재시도 규칙(Retry-After 없으면 지수 백오프)으로 다시 보내고"는 R3.18 에 없다(TLS 실패에는 Retry-After 가 없다). 실제 구현 survey-service `link_push.py` 는 한 번 시도한다. K1 문장을 넣고 칸은 "다시 보내지 않고 `DELIVERY_FAILED` 로 기록"으로 갱신. |
| C23 | F09 | 계약 빈칸 | R3.18 "(불통·느림·429·5xx·404·410·이름 해석·TLS 검증)"의 입력 목록에는 있으나 출력은 상태 코드별(404·410·429·5xx·401·403·그 밖의 4xx)만 있다 | K1: R3.18 은 TLS 검증 실패를 다시 보내는지 정하지 않는다. 칸의 "재시도 규칙(Retry-After 없으면 지수 백오프)으로 다시 보내고"는 R3.18 에 없다(TLS 실패에는 Retry-After 가 없다). 실제 구현 survey-service `link_push.py` 는 한 번 시도한다. K1 문장을 넣고 칸은 "다시 보내지 않고 `DELIVERY_FAILED` 로 기록"으로 갱신. |
| C23 | F10 | 계약 빈칸 | R3.18 "(불통·느림·429·5xx·404·410·이름 해석·TLS 검증)"의 입력 목록에는 있으나 출력은 상태 코드별(404·410·429·5xx·401·403·그 밖의 4xx)만 있다 | K1: R3.18 은 TLS 검증 실패를 다시 보내는지 정하지 않는다. 칸의 "재시도 규칙(Retry-After 없으면 지수 백오프)으로 다시 보내고"는 R3.18 에 없다(TLS 실패에는 Retry-After 가 없다). 실제 구현 survey-service `link_push.py` 는 한 번 시도한다. K1 문장을 넣고 칸은 "다시 보내지 않고 `DELIVERY_FAILED` 로 기록"으로 갱신. |
| C23 | F11 | 계약 빈칸 | R3.18 "(불통·느림·429·5xx·404·410·이름 해석·TLS 검증)"의 입력 목록에는 있으나 출력은 상태 코드별(404·410·429·5xx·401·403·그 밖의 4xx)만 있다 | K1: R3.18 은 TLS 검증 실패를 다시 보내는지 정하지 않는다. 칸의 "재시도 규칙(Retry-After 없으면 지수 백오프)으로 다시 보내고"는 R3.18 에 없다(TLS 실패에는 Retry-After 가 없다). 실제 구현 survey-service `link_push.py` 는 한 번 시도한다. K1 문장을 넣고 칸은 "다시 보내지 않고 `DELIVERY_FAILED` 로 기록"으로 갱신. (F11 의 (b) VAPID 401·403 은 R3.18 이 정한 대로 맞음.) |
| C23 | F12 | 맞음 | R3.18 "401·403(VAPID 인증 거절 …)과 그 밖의 4xx → 다시 보내지 않고 구독은 지우지 않는다" | 칸 출력(재시도 안 함, 구독 유지, `DELIVERY_FAILED`)은 R3.18 과 같다. 판정 열 "열림 (O3)" 갱신: 닫힘. |
| C23 | F13 | 맞음 | R3.18 "401·403 … 다시 보내지 않고 구독은 지우지 않는다" | 칸 출력은 현행과 같다. 판정 열 "열림 (O3)" 갱신: 닫힘. |
| C23 | F14 | 맞음 | R3.12(사람 경로에만 적용) | 해당 없음 판정이 맞다. |
| C24 | F08 | 맞음 | 영역 내부 표시 확인(첫 열 "3.4.4 영역 내부로 뺌"); R3.10; R10.1 | 영역 내부 표시 있음. 칸 본문의 "R10.1 … R1.1~R1.3 대로 TLS·검증"은 낡았다(현행 R10.1 은 DB 를 영역 컴포넌트로 보고 이 계약은 R3.10 출력만 정한다). 출력(서비스 503 `UNAVAILABLE`·`/readyz` 503)은 R3.10 과 같다. |
| C24 | F09 | 맞음 | 영역 내부 표시 확인(첫 열 "3.4.4 영역 내부로 뺌"); R3.10; R10.1 | 영역 내부 표시 있음. 칸 본문의 "R10.1 … R1.1~R1.3 대로 TLS·검증"은 낡았다(현행 R10.1 은 DB 를 영역 컴포넌트로 보고 이 계약은 R3.10 출력만 정한다). 출력(서비스 503 `UNAVAILABLE`·`/readyz` 503)은 R3.10 과 같다. |
| C24 | F10 | 맞음 | 영역 내부 표시 확인(첫 열 "3.4.4 영역 내부로 뺌"); R3.10; R10.1 | 영역 내부 표시 있음. 칸 본문의 "R10.1 … R1.1~R1.3 대로 TLS·검증"은 낡았다(현행 R10.1 은 DB 를 영역 컴포넌트로 보고 이 계약은 R3.10 출력만 정한다). 출력(서비스 503 `UNAVAILABLE`·`/readyz` 503)은 R3.10 과 같다. |
| C24 | F11 | 맞음 | 영역 내부 표시 확인(첫 열 "3.4.4 영역 내부로 뺌"); R3.10; R10.1 | 영역 내부 표시 있음. 칸 본문의 "R10.1 … R1.1~R1.3 대로 TLS·검증"은 낡았다(현행 R10.1 은 DB 를 영역 컴포넌트로 보고 이 계약은 R3.10 출력만 정한다). 출력(서비스 503 `UNAVAILABLE`·`/readyz` 503)은 R3.10 과 같다. |
| C24 | F12 | 맞음 | 영역 내부 표시 확인; R3.10 "서비스의 접속을 거부함(계정 인증 실패·권한 없음) … 401·403 을 밖으로 내지 않는다" | 영역 내부 표시 있음. 출력(서비스 503 `UNAVAILABLE`, 401·403 을 내지 않음)은 R3.10 과 같다. |
| C24 | F13 | 맞음 | 영역 내부 표시 확인; R3.10 "401·403 을 밖으로 내지 않는다" | 영역 내부 표시 있음. 출력은 R3.10 과 같다. |
| C24 | F14 | 맞음 | 영역 내부 표시 확인 | 영역 내부 표시 있음. 해당 없음 판정이 맞다. |
| C27 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C27 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C27 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6 | — 출력은 현행과 같다(칸 안의 "게이트웨이"=platform 공개 입구). |
| C27 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6 | — 출력은 현행과 같다. 칸 안의 "게이트웨이"는 platform 공개 입구, 판정 열의 "열림(O1)" 참조는 R3.23 으로 닫혔다. |
| C27 | F12 | 맞음 | R3.23 "계정 관리 화면(로그인·가입)과 `Exposure.auth.kind=none` 경로는 세션 없이 연다" | 칸 출력(로그인·가입 화면 200, 비밀번호 틀림은 platform 소관)은 현행과 같다. 판정 열 "열림 (O1)" 갱신: 닫힘. |
| C27 | F13 | 맞음 | R3.24 "예외: `Exposure.auth.kind=authenticated` 경로와 계정 관리 화면은 역할이 없어도 연다" | 칸 출력과 같다. 판정 열 "열림 (O2)"·"모순(M4)" 갱신: 닫힘. |
| C27 | F14 | 맞음 | R3.12 "또는 계정 관리(로그인·가입·관리 화면)가 `BoundaryError` 가 아닌 5xx 를 냄 … 사람 경로: 503 UU" | — |
| C29 | F08 | 맞음 | R3.8 "서버 인증서의 이름 불일치·모르는 루트·만료·아직 유효 전·시계 어긋남 → 503 UU / UNAVAILABLE"; R1.3; R10.6; R10.6 첫 적재 | 칸 (c) 키오스크 첫 적재는 R10.6 이 닫는다("키오스크 앱을 적재하기 전(첫 적재)이면 … 브라우저 오류 화면만"). 판정 열 "열림 (O9)" 갱신: 닫힘. |
| C29 | F09 | 맞음 | R1.2 "SAN 은 그 서비스 이름과 별칭뿐"; R3.8; R1.3; R10.6; R10.6 첫 적재 | 칸 (c) 키오스크 첫 적재는 R10.6 이 닫는다("키오스크 앱을 적재하기 전(첫 적재)이면 … 브라우저 오류 화면만"). 판정 열 "열림 (O9)" 갱신: 닫힘. |
| C29 | F10 | 맞음 | R1.3 "IN-ROOT 로 검증, 검증 실패 → UNAVAILABLE"; R3.8; R1.7; R10.6; R10.6 첫 적재 | 칸 (c) 키오스크 첫 적재는 R10.6 이 닫는다("키오스크 앱을 적재하기 전(첫 적재)이면 … 브라우저 오류 화면만"). 판정 열 "열림 (O9)" 갱신: 닫힘. |
| C29 | F11 | 맞음 | R1.6 "어긋나 검증이 실패하면 출력은 R3.8(서비스 사이 인증서)·R3.23(토큰·쿠키)과 같다"; R3.8; R10.6; R10.6 첫 적재 | 칸 (c) 키오스크 첫 적재는 R10.6 이 닫는다("키오스크 앱을 적재하기 전(첫 적재)이면 … 브라우저 오류 화면만"). 판정 열 "열림 (O9)" 갱신: 닫힘. (F11: 기기 인증서 쪽의 첫 적재 거절은 K4) |
| C29 | F12 | 계약 빈칸 | R3.23 "`/v1/` 밖의 화면 경로 GET + `Accept: text/html` → 302 … text/html 없으면 401"; R3.13 "기기 인증서 거절 = OUT-NET → 재시도 … 직원 호출 화면"; R10.6 첫 적재는 공개 입구 인증서에 대해서만 | K4: 키오스크 화면을 처음 적재할 때 기기 인증서가 거절되면(R3.13 의 OUT-NET) 보일 앱이 없는데 R3.13 의 "재시도 뒤 직원 호출 화면"은 적용되지 않는다. 칸의 "(O9, O6)"이 가리키는 문장은 R10.6 에 공개 입구 인증서에 대해서만 있다. K4 문장을 R3.13 에 넣는다. |
| C29 | F13 | 맞음 | R3.24 예외 규정; `kind=account` 에 역할이 모자라면 403 | 칸 출력과 같다. 판정 열 갱신: 닫힘. |
| C29 | F14 | 맞음 | R3.12; R3.13 | — |
| C30 | F08 | 계약 빈칸 | R10.1 "감시 수집은 … 실패는 R10.11"; R10.11 에는 실패 출력이 없다 | K2: R10.1 이 가리키는 R10.11 에 수집 실패의 출력이 없다. K2 문장을 R10.11 에 넣는다. 칸 출력("연결 실패, 서비스 쪽 출력은 바뀌지 않는다")은 K2 와 같다. |
| C30 | F09 | 계약 빈칸 | R10.1 "감시 수집은 … 실패는 R10.11"; R10.11 에는 실패 출력이 없다 | K2: R10.1 이 가리키는 R10.11 에 수집 실패의 출력이 없다. K2 문장을 R10.11 에 넣는다. 칸 출력("연결 실패, 서비스 쪽 출력은 바뀌지 않는다")은 K2 와 같다. |
| C30 | F10 | 계약 빈칸 | R10.1 "감시 수집은 … 실패는 R10.11"; R10.11 에는 실패 출력이 없다 | K2: R10.1 이 가리키는 R10.11 에 수집 실패의 출력이 없다. K2 문장을 R10.11 에 넣는다. 칸 출력("연결 실패, 서비스 쪽 출력은 바뀌지 않는다")은 K2 와 같다. |
| C30 | F11 | 계약 빈칸 | R10.1 "감시 수집은 … 실패는 R10.11"; R10.11 에는 실패 출력이 없다 | K2: R10.1 이 가리키는 R10.11 에 수집 실패의 출력이 없다. K2 문장을 R10.11 에 넣는다. 칸 출력("연결 실패, 서비스 쪽 출력은 바뀌지 않는다")은 K2 와 같다. |
| C30 | F12 | 맞음 | R10.11 "인증을 요구하지 않는다(토큰이 있어도 무시, 401·403 없음; 접근 통제는 망)" | 칸 출력과 같다. 판정 열 "열림 (O5)" 갱신: 닫힘. |
| C30 | F13 | 맞음 | R10.11 | 칸 출력과 같다. 판정 열 갱신: 닫힘. |
| C30 | F14 | 맞음 | R3.12(사람 경로에만 적용) | 해당 없음 판정이 맞다. |
| C33 | F08 | 맞음 | IN-JOB(RUNTIME 0.1: deploy 의 배포 설정이 argv 를 띄움); R9.2; CONVENTIONS 13절 deploy 예외 | — 해당 없음 판정이 맞다. |
| C33 | F09 | 맞음 | IN-JOB(RUNTIME 0.1: deploy 의 배포 설정이 argv 를 띄움); R9.2; CONVENTIONS 13절 deploy 예외 | — 해당 없음 판정이 맞다. |
| C33 | F10 | 맞음 | IN-JOB(RUNTIME 0.1: deploy 의 배포 설정이 argv 를 띄움); R9.2; CONVENTIONS 13절 deploy 예외 | — 해당 없음 판정이 맞다. |
| C33 | F11 | 맞음 | IN-JOB(RUNTIME 0.1: deploy 의 배포 설정이 argv 를 띄움); R9.2; CONVENTIONS 13절 deploy 예외 | — 시계는 스케줄 판정에만 쓰이며 R10.12 가 출력을 정한다. |
| C33 | F12 | 맞음 | R9.2 "종료 코드 0 은 마지막 줄 JSON 을 내보냈다는 뜻 … 0 이 아닌 값"; CONVENTIONS 3절; R6.3; R10.12 | — |
| C33 | F13 | 맞음 | R9.2; CONVENTIONS 3절; R10.12 | — |
| C33 | F14 | 맞음 | R3.12(사람 경로에만 적용) | 해당 없음 판정이 맞다. |
| C34 | F08 | 낡음 | RUNTIME-MATRIX A 의 C34: "deploy 가 영역 이미지로 한 번 띄움 → 영역 잡, 출력 OUT-JOB"; R9.2; CONVENTIONS 13절 예외 | 칸은 계약 클라이언트의 `UNAVAILABLE`(HTTP 호출 모델)로 쓰여 있어 낡았다. 이 입력은 C34 에서 생기지 않는다: 잡을 띄우는 일은 TLS 연결이 아니다. C33 의 같은 F 칸과 같게 "해당 없음: 관리 명령은 deploy 가 띄우는 프로세스 실행이고 TLS 연결이 없다. 잡 안의 서비스 호출에서 생기면 그 호출의 행(C03~C22)이 정한다(R9.2)"로 갱신. |
| C34 | F09 | 낡음 | RUNTIME-MATRIX A 의 C34: "deploy 가 영역 이미지로 한 번 띄움 → 영역 잡, 출력 OUT-JOB"; R9.2; CONVENTIONS 13절 예외 | 칸은 계약 클라이언트의 `UNAVAILABLE`(HTTP 호출 모델)로 쓰여 있어 낡았다. 이 입력은 C34 에서 생기지 않는다: 잡을 띄우는 일은 TLS 연결이 아니다. C33 의 같은 F 칸과 같게 "해당 없음: 관리 명령은 deploy 가 띄우는 프로세스 실행이고 TLS 연결이 없다. 잡 안의 서비스 호출에서 생기면 그 호출의 행(C03~C22)이 정한다(R9.2)"로 갱신. |
| C34 | F10 | 낡음 | RUNTIME-MATRIX A 의 C34: "deploy 가 영역 이미지로 한 번 띄움 → 영역 잡, 출력 OUT-JOB"; R9.2; CONVENTIONS 13절 예외 | 칸은 계약 클라이언트의 `UNAVAILABLE`(HTTP 호출 모델)로 쓰여 있어 낡았다. 이 입력은 C34 에서 생기지 않는다: 잡을 띄우는 일은 TLS 연결이 아니다. C33 의 같은 F 칸과 같게 "해당 없음: 관리 명령은 deploy 가 띄우는 프로세스 실행이고 TLS 연결이 없다. 잡 안의 서비스 호출에서 생기면 그 호출의 행(C03~C22)이 정한다(R9.2)"로 갱신. |
| C34 | F11 | 낡음 | RUNTIME-MATRIX A 의 C34: "deploy 가 영역 이미지로 한 번 띄움 → 영역 잡, 출력 OUT-JOB"; R9.2; CONVENTIONS 13절 예외 | 칸은 계약 클라이언트의 `UNAVAILABLE`(HTTP 호출 모델)로 쓰여 있어 낡았다. 이 입력은 C34 에서 생기지 않는다: 잡을 띄우는 일은 TLS 연결이 아니다. C33 의 같은 F 칸과 같게 "해당 없음: 관리 명령은 deploy 가 띄우는 프로세스 실행이고 TLS 연결이 없다. 잡 안의 서비스 호출에서 생기면 그 호출의 행(C03~C22)이 정한다(R9.2)"로 갱신. |
| C34 | F12 | 낡음 | RUNTIME-MATRIX A C34 (deploy 가 영역 이미지로 띄우는 잡, OUT-JOB); R9.2 | C34 는 HTTP 호출이 아니라 잡 실행이다. C33 F12 칸과 같게 갱신: "OUT-JOB: 비밀 파일이 없거나 잡 안의 서비스 호출이 401 이면 계약 클라이언트가 `PERMISSION_DENIED` 를 받아 재시도하지 않고 0 이 아닌 종료 코드로 끝난다(비밀 값은 출력에 없다, R6.3)". |
| C34 | F13 | 낡음 | RUNTIME-MATRIX A C34; R9.2 | C33 F13 칸과 같게 갱신: "OUT-JOB: 잡 안의 서비스 호출이 403 이면 `PERMISSION_DENIED` 를 받아 재시도하지 않고 0 이 아닌 종료 코드(비밀 값 없음)". HTTP 서버 403 모델은 C34 에서 생기지 않는다. |
| C34 | F14 | 맞음 | R3.12; RUNTIME-MATRIX A C34 | 칸 결론("출력이 바뀌지 않는다")은 맞다. 사유 문구 "기계 토큰 경로"를 "잡 실행은 사람 인증을 거치지 않는다"로 바꾼다(칸은 낡은 HTTP 모델의 문장). |
| C36 | F08 | 맞음 | R1.7; R1.5 "이전 인증서·루트가 만료되면 R3.8" | — |
| C36 | F09 | 맞음 | R1.5; R3.14; R3.8 | — |
| C36 | F10 | 맞음 | R1.7 | — |
| C36 | F11 | 맞음 | R1.6 | — 판정 해당 없음이 맞다. |
| C36 | F12 | 맞음 | R1.5 | 해당 없음 판정이 맞다(OUT-FILE 에 인증이 없다). |
| C36 | F13 | 맞음 | R1.5 | 해당 없음 판정이 맞다. |
| C36 | F14 | 맞음 | R3.12(사람 경로에만 적용) | 해당 없음 판정이 맞다. |

## 계약 문장을 고칠 것 (계약 빈칸·모순)
### K1 (계약 빈칸) C23 F08·F09·F10·F11
- 넣을 위치: RUNTIME.md R3.18 의 출력 칸, "401·403 … 다시 보내지 않고 구독은 지우지 않는다." 문장 뒤
- 그대로 넣을 문장: 불통·시간 초과·이름 해석 실패·TLS 검증 실패처럼 푸시 서비스의 HTTP 응답이 없는 실패는 다시 보내지 않고 그 푸시를 `DELIVERY_FAILED` 로 기록한다(같은 알림의 재전달은 PUBLIC_API G절의 직원 호출 재알림이 맡는다).
- 근거: 확인한 것: R3.18 은 입력에 이 실패들을 나열하지만 재시도는 429·5xx 에만 적는다. TLS 검증 실패는 다시 보내도 같은 결과이고(CONVENTIONS 3절: 재시도는 `UNAVAILABLE` 일시 장애에만) RFC 8030 5 의 재시도 지침은 푸시 서비스가 낸 응답 상태에만 있다. survey-service `link_push.py` 는 실제로 한 번만 시도한다(읽음). 이 문장은 P4 몫의 C23 F04·F05(불통·이름 해석)와 P3 몫의 F25 와 겹친다.

### K2 (계약 빈칸) C30 F08·F09·F10·F11
- 넣을 위치: RUNTIME.md R10.11 의 출력 칸 끝
- 그대로 넣을 문장: 감시가 TLS 검증에 실패하거나 연결하지 못하거나 10초 안에 응답을 받지 못하면 그 수집은 이뤄지지 않은 것이다. 영역 서비스의 출력은 바뀌지 않고(서비스는 계속 응답한다), 수집 실패의 처리는 platform 이 정한다.
- 근거: 확인한 것: R10.1 은 "감시 수집은 … 실패는 R10.11"이라 하나 R10.11 에는 수집 실패의 출력이 없다(끊어진 참조). 이 문장은 영역 사이에서 관찰되는 것(서비스 쪽 출력 불변)만 정하고 platform 내부는 정하지 않는다(구조 규칙 6). 표준: Prometheus scrape 실패는 대상 쪽 출력을 바꾸지 않는다.

### K3 (모순) C13 F12·F13
- 넣을 위치: RUNTIME.md R3.23 의 괄호 "(앱 앞에서 토큰을 대조하는 것은 `Exposure.auth.kind=machine-token` 경로뿐, 검토 B-07)" 교체, 그리고 RUNTIME-MATRIX.md A 의 C13 행
- 그대로 넣을 문장: R3.23 괄호를 이렇게 바꾼다: "(앱 앞에서 토큰을 대조하는 것은 받는 영역 게이트웨이가 `Exposure.auth.kind=machine-token` 경로에서 하는 경우뿐이고, 그 거절의 모양은 서비스의 것과 같다: 토큰이 없거나 틀리면 401 + `WWW-Authenticate: Bearer`, 역할 밖이면 403, 본문은 `BoundaryError` 전체 필드다)". MATRIX A 의 C13 은 "추론 서버 → release-gate"로 이미 맞다(두 번째 경로는 없다).
- 근거: 두 문장: R3.23 "앱 앞에서 토큰을 대조하는 것은 `Exposure.auth.kind=machine-token` 경로뿐"(게이트웨이가 platform 공개 입구인지 받는 영역 게이트웨이인지 안 적음, `Exposure` 설명은 "다른 호스트의 추론 서버가 release-gate 읽기 면을 읽는 경로")과 MATRIX A "모든 행의 호출은 호출 영역 게이트웨이 → 받는 영역 게이트웨이를 지난다". 확인한 것: `_http.py` `_map_error` 는 본문이 `BoundaryError` 가 아닌 4xx 를 `UNAVAILABLE`(재시도)로 읽으므로 거절 본문을 정하지 않으면 토큰 오류가 재시도 루프가 된다. 표준: RFC 9110 11.6.1·15.5.2, RFC 6750 3.

### K4 (계약 빈칸) C29 F12 (F11 의 기기 인증서 쪽도 같다)
- 넣을 위치: RUNTIME.md R3.13 의 출력 칸 끝
- 그대로 넣을 문장: 키오스크 앱을 적재하기 전(첫 적재)에 기기 인증서가 거절되면(위 OUT-NET) 보일 앱이 없으므로 재시도 규칙과 직원 호출 화면은 적용되지 않고 브라우저의 오류 화면만 보인다(R10.6 의 첫 적재와 같다).
- 근거: 확인한 것: R10.6 의 첫 적재 구분은 키오스크가 공개 입구 인증서를 검증할 때만 적혀 있고, R3.13 의 mTLS 거절은 "키오스크는 … 재시도 … 직원 호출 화면"만 적어 앱이 없는 첫 적재를 말하지 않는다. 표준: WHATWG Fetch(네트워크 오류는 원인을 노출하지 않는다), RFC 8446 4.4.2·6.2(클라이언트 인증서 거절은 핸드셰이크 경고).

## 그 밖의 발견 (칸 판정에는 넣지 않았다)
- X1 (R3.12 모호): "사람 경로: 503 UU … 이미 맺은 로그인 세션은 쿠키 수명까지 유지된다"가 어느 요청이 503 을 받는지 나누지 않는다. 칸 C01·C02·C09·C10·C19·C16·C17·C27·C29 의 F14 가 같은 문장을 되풀이한다. 넣을 문장(R3.12 출력 칸 끝): "쿠키 세션이 유효한 요청은 인증 확인을 기다리지 않고 평소 출력을 받는다(새 SSE 연결 포함). 유효한 세션이 없거나 갱신이 필요한 요청만 503 UU 를 받는다." 근거: R3.12 자신의 "세션은 쿠키 수명까지 유지", OWASP Session Management.
- X2 (표기): CELLS 묶음 2 의 입력 칸과 MATRIX A 의 사람·기기 행은 "게이트웨이"로 쓰고 있다. 현행 R3 는 사람·기기 경로의 주체를 "platform 공개 입구", 영역 사이는 "받는 영역 게이트웨이"로 나눈다. 출력은 같아 칸을 맞음으로 판정했으나 표기를 갱신해야 한다.
- X3 (판정 열 낡음): 묶음 2 의 "열림 (On)" 35칸은 대응표(CELLS 머리)로 닫혔다고 적혀 있으나 칸의 판정 열·출력 문장이 그대로다. 위 표의 "고칠 것"에 갱신 문장을 적은 칸만 고치면 된다. C13 의 두 칸은 닫히지 않고 모순(K3)이다.
- X4 (겹침): K1 은 몫 P4(C23 F04·F05)와 P3(F25)에, K2 는 F04~F07 의 C30 칸에, X1 은 F12 의 R3.23 에 걸린다. 헤드가 합칠 때 같은 조항에 한 번만 넣는다.
- X5 (C24 칸 본문): 영역 내부 표시는 7칸 모두 있다. 칸 본문 일부가 "R10.1 … TLS·검증"을 인용하는데 현행 R10.1 은 DB 를 영역 컴포넌트로 두고 이 계약은 R3.10 출력만 정한다. 표시 확인만 하는 규칙에 따라 판정은 맞음으로 두었다.
