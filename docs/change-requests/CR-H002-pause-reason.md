# CR-H002 (초안): 정지 사유 필드 (위험 정지와 되묻기 한도 정지의 구분)

> **이 문서는 초안이다. 사용자 결정 전이며 확정된 것이 없다.** `boundary-contracts`는 수정하지 않았다(헤드가 소유하고, 사용자 결정 뒤에야 계약 변경으로 옮긴다). "제안"은 전부 제안이다. 열거 값 이름은 자리 표시다.
>
> 작성 2026-10-28, 헤드. 대장 항목: [`OPEN_GAPS.md`](../OPEN_GAPS.md) L28. 근거는 survey-service ADR-0020에 관한 에이전트 보고이며 **새 clone 재현 전**이다. 이 초안은 survey-service 코드·ADR 원문을 읽지 않았다("읽은 근거"는 PUBLIC_API.md를 읽고 확인한 것만 뜻한다).

## 1. 문제

위험 신호로 멈춘 경우와 되묻기 한도(G12, 기본 N=3 초과)로 멈춘 경우가 둘 다 세션 상태 `PAUSED_RISK`이고, `GET /v1/sessions/{id}/state`와 `turn_failure_signal`의 모양이 같다(보고). 둘을 가르는 것은 환자에게 가는 고정 문장(`RISK_NOTICE`/`CALL_STAFF`)뿐이다. 그래서 직원 콘솔은 "환자가 위험해서 멈췄다"와 "시스템이 못 알아들어서 멈췄다"를 구분해 보여 줄 수 없고, 운영 지표(ops-feedback)도 두 경우를 한 덩어리로 센다. 전자는 환자 안전 문제이고 후자는 모델·질문 품질 문제라 대응이 다르다.

## 2. 현재 계약 (읽은 근거, `boundary-contracts/PUBLIC_API.md`)

- 34행: "`turn_failure_signal`: null이 아니면 이번 턴 처리에 문제가 있었다는 뜻이다. `write_committed`(기록이 저장됐는지: COMMITTED/NOT_COMMITTED)와 `staff_alert`(직원 호출이 전달됐는지: NONE/DELIVERED/DELIVERY_FAILED)를 담는다." 정지 사유 필드는 없다.
- 77행: "`IN_PROGRESS`·`PAUSED_RISK` 아직 끝나지 않음." `SessionResult.status`는 정지 사유를 말하지 않는다.
- 87~88행: 위험 신호 경로는 알림(`kind` = severity 값 `RISK`|`CALL_STAFF`)을 만들고 "세션을 `PAUSED_RISK`로 멈춘다". `StaffAlert.kind`가 사유를 부분적으로 담을 수 있으나, 되묻기 한도가 `kind`를 무엇으로 쓰는지는 확인하지 못했다(보고에서는 기존 `CALL_STAFF` 경로 재사용).
- 확인하지 못한 것: `/state` 응답 스키마의 정확한 필드 목록.

## 3. 제안 (미결정)

1. 세션 상태 응답(`/state`), 직원용 세션 조회, `StaffAlert`에 **optional** `pause_reason` 열거를 더한다: `RISK`(위험 신호), `REASK_LIMIT`(되묻기 한도), `OTHER`(그 밖, 모르는 값). `PAUSED_RISK`가 아닌 상태에서는 null/생략.
2. `turn_failure_signal`에는 손대지 않는다(턴 처리 실패 신호이고 정지 사유와 의미가 다르다).
3. 모르는 값을 받는 쪽은 `OTHER`처럼 취급하도록 규약에 적는다(열거 확장 대비).
4. 상태 이름 `PAUSED_RISK`는 바꾸지 않는다(MAJOR 변경이 되고 결과 조회 소비자가 깨진다).

## 4. 대안과 버리는 이유

| 대안 | 버리는 이유 |
|---|---|
| 상태를 `PAUSED_REASK_LIMIT`로 새로 나눔 | 기존 소비자는 `PAUSED_RISK`만 아는데 새 값을 받으면 정지를 알아보지 못할 수 있다. 상태 열거 확장은 호환이 깨지기 쉽고 `SessionResult.status` 규약(77행)까지 바꾼다 |
| `StaffAlert.kind`만 구분 | 알림이 없는 경로(알림 저장 실패)나 세션 조회에서는 사유가 안 보이고, `kind`는 알림 종류이지 세션 정지 사유가 아니다 |
| 환자 문장(`RISK_NOTICE`/`CALL_STAFF`)으로 구분 유지 | 지금 상태다. 문장은 화면 표시용이라 파싱하면 문구 변경에 깨지고 지표 집계에 못 쓴다 |
| ops-feedback가 TurnTrace에서 추정 | 추정이 틀릴 수 있고 정지를 결정한 survey-service가 가장 정확히 안다. 직원 콘솔은 추정할 입력도 없다 |

## 5. 하위 호환

optional 필드와 열거를 추가하는 변경이다. 같은 MAJOR의 모르는 필드를 받아들이는 읽기 규칙(HTTP.md 공통 절, CR-H001 초안이 확인한 내용이며 이 초안은 다시 읽지 않았다)을 따르면 기존 클라이언트는 깨지지 않으므로 MINOR 후보다. 정확한 버전 번호와 `CONVENTIONS.md` 규칙 적용은 헤드가 확정한다(이 초안은 그 규칙을 읽지 않았다). 새 클라이언트 + 옛 서버: 필드가 없으므로 미상으로 폴백해야 한다.

## 6. 영향 영역

| 영역 | 일 |
|---|---|
| survey-service | 정지 시점에 사유를 기록하고 응답·알림에 내보낸다. 스키마, 적합성 시험, ADR(D89) |
| kiosk-frontend | 직원 콘솔 화면에서 사유 표시(직원 콘솔 위치는 CR-H001 초안의 읽은 문서 기준이며 다시 확인하지 않았다) |
| admin-console | 실패 사례 검토 화면에서 사유 표시 가능성. 코드를 읽지 않아 **추정** |
| ops-feedback | 정지 건수를 사유별로 집계(REASK_STREAK와 구분). 비식별 허용 목록에 열거 값 추가 |

## 7. CR-H001과 같은 계약 MINOR로 묶을지

제안(미결정): **묶는 편을 권한다.** 둘 다 `StaffAlert`와 직원 호출 경로에 optional 필드를 더하는 호환 변경이라 스키마, 적합성 시험, 태그를 한 번에 낼 수 있고, 소비자(kiosk-frontend, ops-feedback)도 한 번만 따라가면 된다. 묶지 않는 쪽의 이유: CR-H001은 새 엔드포인트와 임상 흐름 확인(재알림 간격·횟수)이 필요해 결정이 오래 걸릴 수 있고, CR-H002는 필드 하나라 빨리 낼 수 있다. **CR-H001의 결정이 늦어질 것 같으면 분리**한다. 두 CR이 같은 `StaffAlert` 스키마를 건드리므로 분리해도 필드 충돌이 없는지 확인한다.

## 8. 사용자 결정이 필요한 것

1. 이 방향(optional `pause_reason`, 상태 이름 유지)으로 진행할지.
2. 열거 값의 집합과 이름.
3. CR-H001과 묶을지.
