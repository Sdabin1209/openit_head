# 영역 브리프: 운영 콘솔 (admin-console)

> 이 브리프는 헤드가 전달한 것이다. 상세한 현재 상태는 이 리포의 `README.md`, `docs/brief.md`, `docs/boundary.md`.

## 0. 따라야 할 계약과 정본 위치 (모든 영역 공통, 2.1.0 기준)
- 규칙의 정본: 워크스페이스 루트 `CLAUDE.md`(자기 리포 안에서만 수정, 이웃 사실을 복사하지 않고 링크, 구조 선택마다 ADR의 '왜', 비밀은 `NAME_FILE`, 커밋 단위, 변경 요청 절차).
- 버전 열차(계약, turn-engine, model-runtime)의 값은 **`deploy/scripts/lib.sh`의 표**가 정본이다. 이 문서에 숫자를 적지 않는다.
- 계약 정본(`boundary-contracts`, 읽기 전용): `INTERFACES.md`(I1~I10 무엇을 내놓고 받는가), `HTTP.md`(HTTP 면), `PUBLIC_API.md`(I10, 직원 호출 G절, 정지 사유 H절), `CONVENTIONS.md`(오류·멱등·버전·인증·`/readyz` 총 2초·환자 턴 시간 상한 사슬), `METRICS.md`와 `boundary_contracts/metrics.json`(평가 지표 이름), `boundary_contracts/schemas`(JSON 스키마), 문진 스키마 `survey-service/schema`.
- 표준 결정: `head/docs/DECISIONS.md`(D88 표준 기본값, D89 '왜', D92 작성자≠검수자, D93~D103), 장애 정책 `head/docs/FAULT_POLICY.md`.
- 계약이 모자라거나 틀리면 직접 고치지 말고 `docs/change-requests/`에 변경 요청을 써서 헤드에게 넘긴다.
- 영역 목록의 정본: `head/shared/areas.json`.

### 이 영역이 따르는 계약
- **소비 I5 GateService / I4 ReleaseReader**(출고 승인·활성화·롤백)와 **I7 FailureStore**(실패 사례 검토), 모두 게이트웨이를 거쳐 운영자 계정(역할: 승인자, 검토자, 읽기)으로 호출한다(`INTERFACES.md`, `HTTP.md`).
- **직원 알림 화면은 이 영역에 없다**(직원 콘솔은 kiosk-frontend 소유).
- 지킬 규칙: 역할별 허용 경로만 호출, 평가 보고서의 지표 이름은 `metrics.json`의 현행(ACTIVE) 이름, 생성된 계약 검증기(`generated/`)는 `gen-schemas`로만 만든다, 사람 승인은 필수 관문.
