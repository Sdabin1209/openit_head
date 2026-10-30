# 영역 설계 규칙 (D117, 2026-10-30)

이 문서가 영역 내부 구조의 정본이다. `STRUCTURE.md`, `architecture.md`, `PROJECT_STRUCTURE.md`, `OVERVIEW.md`의 영역 내부 서술(특히 turn-engine 의존)은 이 문서로 대체한다. 구조 규칙 6개(D104)를 코드 배치와 검사로 옮긴 것이다.

## 1. 구조 규칙 6개 (D104, 사용자 확정)

1. 영역은 서로의 구조를 모른다.
2. 영역은 작업의 단위인 컴포넌트를 가진다.
3. 컴포넌트는 다른 컴포넌트와 독립적이며 서로의 구조를 모른다.
4. 컴포넌트는 자신에게 할당된 입력·출력 스키마와 자신이 할 업무밖에 모른다.
5. 영역은 자기 컴포넌트 사이의 스키마를 알고, 컴포넌트가 교류할 수 있게 그 스키마를 책임진다.
6. 영역 간 스키마는 헤드가 책임진다(boundary-contracts).

## 2. 컴포넌트는 함수다

- 컴포넌트 하나는 "입력 스키마 하나 → 출력 스키마 하나"인 업무 하나다. 같은 입력이면 같은 출력을 낸다.
- 상태나 바깥 자원(DB, 네트워크, 적재된 모델)이 필요하면 그것을 다루는 컴포넌트(저장소, 통신)로 따로 두고, 바깥에는 "작업 하나 = 입력 스키마 → 출력 스키마"인 함수 모양으로만 드러낸다. 업무 컴포넌트에는 wiring이 주입한다.
- 근거: functional core, imperative shell(Gary Bernhardt), 포트·어댑터(Alistair Cockburn).

## 3. 영역의 표준 배치

영역 리포(survey-service, release-gate, ops-feedback, model-runtime, synthetic-data, question-authoring, model-lab, admin-console, kiosk-frontend, deploy)는 패키지 안에 다음을 반드시 가진다.

| 위치 | 담는 것 |
|---|---|
| `schemas/` (리포 루트) | 영역 내부 타입의 JSON Schema(draft 2020-12). 타입 하나에 파일 하나, 파일 이름 = 타입 이름. `schemas/examples/<타입>.valid*.json`, `<타입>.invalid*.json` |
| `<패키지>/types/` | `schemas/`에서 생성한 코드 타입. 손으로 고치지 않는다(생성 명령을 README 4절에 적는다). Python: datamodel-code-generator, TypeScript: json-schema-to-typescript |
| `<패키지>/components/` | 컴포넌트마다 파일 하나. 통신 컴포넌트도 여기 둔다 |
| `<패키지>/wiring/` | 어느 컴포넌트의 출력을 어느 컴포넌트의 입력에 넘길지, 저장소·통신을 어디에 주입할지. 컴포넌트가 아니라 영역의 몫(규칙 5) |
| 그 밖 | 진입점(`__main__`, 서버 기동), 설정 읽기, DB 마이그레이션. 컴포넌트가 아니며 업무 규칙을 두지 않는다 |

- 의미가 같은 타입은 하나로 정의한다. 컴포넌트 사이 타입은 `schemas/`에 한 번, 영역 사이 타입은 boundary-contracts에 한 번.
- 영역 사이 타입은 `schemas/`에 복사하지 않는다. 필요하면 `$ref`로 계약을 가리키거나, 통신 컴포넌트가 계약 타입을 직접 쓴다.
- TypeScript 화면 리포는 화면 부품을 `ui/`(패키지 안, `components/`·`wiring/`과 같은 높이)에 두고 `components/`는 이 문서의 뜻으로만 쓴다. 구조 검사는 `ui/`를 허용 위치로 본다.

## 4. 통신 컴포넌트

- 이웃 영역과 주고받는 일은 통신 컴포넌트만 한다. 보내는 쪽(계약 클라이언트 사용)과 받는 쪽(HTTP 서버 면)을 각각 컴포넌트로 둔다.
- 통신 컴포넌트는 계약 타입 ↔ 영역 내부 타입 변환을 맡는다. 업무 컴포넌트는 계약 타입이나 HTTP를 모른다.
- 받는 쪽은 요청을 계약 스키마로 검증하고(그 밖의 손 검사 금지), 인증 실패 401·권한 403(CONVENTIONS 6절, D106), 오류는 `BoundaryError` 본문.

## 5. 스키마가 진실의 전부다

- 받아들이는 조건(필수, 형식, 열거, 범위, 조건부 필수 `if/then`·`dependentRequired`)은 전부 스키마에 적는다.
- 컴포넌트의 입력 검사는 스키마 검증 하나다. 코드 안에 따로 거부 조건을 두지 않는다. 스키마로 표현할 수 없는 조건이 있으면 그 이유를 `schemas/README.md`의 "스키마 밖 조건" 표에 적는다(목표 0건).
- 내는 쪽이 내기 전에 검증하고 받는 쪽은 다시 검증하지 않는다(R7). 단, 영역 경계(통신 컴포넌트의 받는 쪽)는 계약으로 검증한다.

## 6. 구조 검사 (영역마다 `tests/test_structure.*`, 헤드는 `head/scripts/structure-check.py`로 모든 영역을 같은 기준으로 본다)

1. `schemas/`, `types/`, `components/`, `wiring/`이 있다.
2. `components/`의 파일은 다른 `components/` 파일을 import하지 않는다.
3. HTTP 클라이언트(`boundary_contracts.clients`, `urllib.request`, `http.client`, `requests`, `fetch`)와 HTTP 서버는 통신 컴포넌트 파일(이름이 `link_` 로 시작) 밖에 없다.
4. 모든 스키마에 통과·거부 예시가 있고 결과가 맞다.
5. `types/`가 `schemas/`에서 다시 생성한 결과와 같다.
6. 시험을 뺀 모든 코드 파일이 `components/`, `wiring/`, `types/` 또는 진입점·설정·마이그레이션 중 하나에 속한다.

## 7. 순서

설계(이 문서) → 영역마다 위에서부터 컴포넌트 분해(입력 = 계약과 브리프, 기존 코드는 빠진 규칙을 찾는 대조 자료로만) → `schemas/` → `types/` 생성 → `components/`·`wiring/`로 이동 → 구조 검사·영역 시험 → 헤드 검증 → E2E 한 번.
