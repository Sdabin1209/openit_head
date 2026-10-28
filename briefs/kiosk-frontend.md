# 영역 브리프: 키오스크 프런트엔드 (kiosk-frontend)

> 이 브리프는 헤드가 전달한 것이다. 상세한 현재 상태는 이 리포의 `README.md`, `docs/brief.md`, `docs/boundary.md`.

## 0. 따라야 할 계약과 정본 위치 (모든 영역 공통, 2.1.0 기준)
- 규칙의 정본: 워크스페이스 루트 `CLAUDE.md`(자기 리포 안에서만 수정, 이웃 사실을 복사하지 않고 링크, 구조 선택마다 ADR의 '왜', 비밀은 `NAME_FILE`, 커밋 단위, 변경 요청 절차).
- 버전 열차(계약, turn-engine, model-runtime)의 값은 **`deploy/scripts/lib.sh`의 표**가 정본이다. 이 문서에 숫자를 적지 않는다.
- 계약 정본(`boundary-contracts`, 읽기 전용): `INTERFACES.md`(I1~I10 무엇을 내놓고 받는가), `HTTP.md`(HTTP 면), `PUBLIC_API.md`(I10, 직원 호출 G절, 정지 사유 H절), `CONVENTIONS.md`(오류·멱등·버전·인증·`/readyz` 총 2초·환자 턴 시간 상한 사슬), `METRICS.md`와 `boundary_contracts/metrics.json`(평가 지표 이름), `boundary_contracts/schemas`(JSON 스키마), 문진 스키마 `survey-service/schema`.
- 표준 결정: `head/docs/DECISIONS.md`(D88 표준 기본값, D89 '왜', D92 작성자≠검수자, D93~D103), 장애 정책 `head/docs/FAULT_POLICY.md`.
- 계약이 모자라거나 틀리면 직접 고치지 말고 `docs/change-requests/`에 변경 요청을 써서 헤드에게 넘긴다.
- 영역 목록의 정본: `head/shared/areas.json`.

### 이 영역이 따르는 계약
- **소비 I10 공개 API**(`PUBLIC_API.md`): 환자 화면(세션 시작·발화·종료·상태 폴링)과 직원 콘솔(알림 목록·SSE·푸시·개입 결정). **G절** 직원 호출 재알림과 실패 기록, **H절** `pause_reason`(RISK / REASK_LIMIT / OTHER, 모르는 값은 OTHER).
- 지킬 규칙(환자 안전): 직원 호출 화면은 전달 실패·`NOT_NOTIFIED`·재알림 상한 어느 경우에도 끝내지 않고 '접수처로 직접 알려 달라'를 유지, 환자가 세션을 임의로 끝낼 수 없음(직원 개입으로만 해제), 응답을 못 받은 재전송만 같은 `turn_id`(5xx·시간 초과 포함), 직원 콘솔은 같은 `alert_id`의 `delivery_attempts`가 커질 때만 '다시 알림'으로 처리, 새 문구는 임상 검토 전 임시 표시(`provisional`), 시간 제한 없는 안내와 키보드 조작, 음성 인식 정책 D88.
- 이웃: 서버는 survey-service뿐(HTTP, 기기별 토큰), gateway는 deploy.
