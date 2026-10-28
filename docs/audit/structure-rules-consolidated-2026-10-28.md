# 구조 규칙 6개(+R7) 전수 점검 취합 (2026-10-28, D104)

기준서: `structure-rules-audit-spec.md`. 영역별 원본 보고서는 각 리포 `docs/audit/structure-rules-2026-10-28.md`(증거 `파일:줄`은 거기에 있다). 이 문서는 숫자와 공통 원인과 고칠 순서만 적는다. 영역 사실은 복사하지 않고 원본을 가리킨다.

## 1. 개수 (영역별 보고서에서 센 값)

| 영역 | P1 | P2 | P3 | 합 |
|---|---|---|---|---|
| deploy | 15 | 17 | 4 | 36 |
| survey-service | 6 | 11 | 3 | 20 |
| ops-feedback | 3 | 10 | 8 | 21 |
| model-lab | 3 | 9 | 5 | 17 |
| model-runtime | 3 | 9 | 7 | 19 |
| synthetic-data | 2 | 12 | 8 | 22 |
| release-gate | 2 | 13 | 4 | 19 |
| kiosk-frontend | 1 | 12 | 7 | 20 |
| question-authoring | 0 | 12 | 7 | 19 |
| admin-console | 0 | 7 | 7 | 14 |
| **합계** | **35** | **112** | **60** | **207** |

헤드 소유 `boundary-contracts`와 `head`는 에이전트 점검 대상이 아니었다. 헤드 몫은 3절에 따로 적는다.

## 2. 공통 원인 (영역마다 따로 고치면 안 되는 것)

- **C1. 영역 경계를 넘는 형식에 스키마가 없다 (R6).** 잡 설정(ops-feedback OF-01, synthetic-data SD-01, release-gate RG-09, deploy DP-06·07), 기기 설정 `/config.json`(kiosk KF-01), 이미지 빌드 인자·라벨·게시 인터페이스(deploy DP-01·12), 게이트웨이 경로·역할 표(DP-13), 서빙 설정(MR-09), 승인·활성화·사례 검토 요청 본문과 비식별 trace와 목록 봉투(admin AC-04·08), 학습 서버 JSONL(ML-08), 영역 환경 변수·`/readyz` 본문(여러 영역).
- **C2. 영역이 이웃의 구조를 안다 (R1).** deploy가 가장 많다(21곳). 그 밖에 model-lab이 synthetic-data 저장 배치를 직접 읽음(ML-02), synthetic-data·release-gate·question-authoring이 이웃 폴더 git·wheel에 의존(SD-02, RG-02, QA-08), survey-service가 deploy 스크립트·model-runtime 내부를 씀(SV-11·13), ops-feedback이 survey-service 재질문 상한을 복제(OF-02).
- **C3. 영역 안에 컴포넌트 경계가 없다 (R2·R3·R4).** model-runtime `_Session`(MR-01)과 `server.py`(MR-03), survey-service 노드와 `TurnState`(SV-01·05·06), model-lab `Run`(ML-03), synthetic-data `_run_job`·`_run_import`(SD-09), question-authoring `AuthoringService`(QA-01), ops-feedback 핸들러 한 클래스, release-gate `GateEngine`(RG-19).
- **C4. 컴포넌트 사이 스키마가 암묵 dict다 (R5).** 모든 영역에 있다. deploy는 스키마 파일 0개(DP-15).
- **C5. 보증된 값을 다시 검증한다 (R7).** survey-service의 LoRA-A 세 겹 재검증과 재시도(SV-02·03, 계약 I8·I9가 의무로 적음), ops-feedback, model-lab(ML-05), synthetic-data(SD-13·14), release-gate(RG-14), 릴리스 로더(SV-17).
- **C6. 실제 계약 위반 (F).** question-authoring이 경로의 퍼센트 인코딩을 디코딩하지 않음(QA-13, 재현됨), model-lab 평가 보고서가 지표 레지스트리에 없는 이름 18개를 필수로 냄(ML-01), release-gate 오류 본문이 BoundaryError 스키마 아님(RG-10)·재판정 경로 없음(RG-12)·필수 검사 미등록 시 조용히 건너뜀(RG-16), 입력 2500자 초과 거절(MR-11), admin-console 사례 목록이 `next_cursor`를 따라가지 않음(AC-01), 개발 승인자 경로(AC-02), ops-feedback `X-Openit-User` 필수(계약에 없음), model-runtime 특수 토큰 처리가 서버에만 있어 학습·평가와 프롬프트가 달라질 수 있음(MR-02).

## 3. 헤드 몫 (R6, 영역이 못 고치는 것)

1. **영역 경계를 넘는 문진 스키마 8개를 헤드로 올린다**: `FrontendMessage`, `FrontendInput`(`TurnFailureSignal` 포함), `InterventionDecision`, `StaffSessionView`, `SessionResult`, `RiskSignal`, `TurnTrace`, `QuestionBank` (SV-14). `QuestionFlow`도 model-runtime이 읽게 되므로 같은 대상(ADR 0010).
2. **계약에 없는 형식의 스키마를 정한다**: C1의 전부. 소비하는 쪽이 초안을 쓰고 헤드가 승인해 `boundary-contracts`에 둔다(영역→변경 요청→헤드).
3. **계약 문서와 클라이언트의 결함**: I3 "게이트는 평가 보고서를 해석하지 않는다"(RG-05), I5 역할 문구와 `release-approver`(RG-11, AC-08), I4 읽는 쪽 열에 admin-console 누락, `LibraryVersion` 형식과 MAJOR.MINOR 비교(RG-01), `HttpGateService`의 `X-Openit-User`·`X-Openit-Report-Hash`(RG-13), 알림 `kind`의 정본 `RISK_STOP` vs `RISK`(KF-13), `ServingConfig` 스키마 부재, 브리프의 "I8 규칙 미리보기" 서술(QA-17).
4. **I8·I9의 재시도 의무를 바꾼다** (SV-02, ADR 0010): LoRA-A 컴포넌트가 보증하고 survey-service는 믿는다. 규칙 명세는 정형화된 데이터.
5. **버전 정확 일치 규칙(D80)이 만드는 결합을 풀거나 근거를 다시 쓴다** (RG-01, DP 5가지). 스키마가 호환되는 한 PATCH·MINOR는 이웃에 영향이 없어야 한다.

## 4. 고칠 순서 (제안, 헤드가 정한다)

- **단계 1 (헤드, 영역 코드 변경 없음)**: 3절 문서·스키마 결함 수정, C1 스키마 초안 접수 체계. 영역은 자기 경계 형식 스키마 초안을 변경 요청으로 낸다(소비하는 쪽이 초안, 만드는 쪽은 자기 출력 초안).
- **단계 2 (영역별, 병렬)**: C6 실제 계약 위반부터(환자 안전과 데이터 손실에 가까운 것 우선: RG-16, AC-01, QA-13, ML-01, MR-02). 이어서 C3 컴포넌트 분리와 C4 컴포넌트 사이 스키마.
- **단계 3**: C2·C1 소비 전환. 이웃 구조 의존을 새 스키마로 교체. deploy가 이웃을 직접 빌드하지 않고 영역이 제공하는 빌드 진입점(스키마로 정한 인터페이스)을 호출하게 한다.
- **단계 4**: C5 R7 제거(LoRA-A 컴포넌트가 보증하게 된 뒤). turn-engine 리포 폐지.
- **단계 5**: 규칙 점검을 기계 검사로 올린다(영역 간 코드 import, 이웃 경로, 계약에 없는 형식). 전체 E2E 최종 1회, 새 clone 시험, push.

## 5. 사용자가 정해야 하는 것 (헤드가 임의로 정하지 않는다)

- **KF-11**: 직원 호출 전달 실패 화면의 "직접 알렸어요, 처음으로"가 세션을 정지 상태로 두고 처음 화면으로 간다. PUBLIC_API.md G절은 "환자가 세션을 임의로 끝낼 수 없다"고 권고하고 `design.md`는 반대다. 환자 안전과 닿는다.
- **QA-15**: CR-0006(4-eyes) 확인 대기인데 기본값이 이미 바뀌었다. 검수자가 구성되지 않으면 `reviewed_only`가 영원히 비어 이웃이 문항 세트를 못 받는다.

## 6. 점검의 한계 (보고서마다 있는 "점검하지 못한 것"의 공통분)

이웃 코드는 규칙상 못 읽었고(교차 확인 필요), 이미지 빌드·Docker 스모크·PostgreSQL·실제 브라우저·GPU는 돌리지 않았다. ADR·runbook 본문은 일부만 읽었다. 에이전트 보고는 증거가 아니다: 단계 2 이전에 P1 전부를 헤드가 코드에서 직접 재현·확인한다.

## 7. 헤드가 한 계약 수정과 영역이 받을 후속 요청 (2026-10-28 밤)

헤드가 고친 것(`boundary-contracts`): I3 평가 보고서 서술, I4·I5·I7 읽는/쓰는 쪽 표와 `release-approver`(`c31ff0a`), I7 검토의 `X-Openit-User` 규칙과 `StaffAlert.kind` 정본 값(다음 커밋).

영역에 전할 후속 요청(지금 일하는 에이전트에 끼우지 않고 병합 뒤 다음 지시로):
- survey-service: 세션 보기(`StaffSessionView.alerts[].kind`)가 `KIND_MAP`을 역변환해 `RISK`를 낸다. 계약은 목록과 같은 이름(`RISK_STOP` 등)을 쓴다 → 역변환 제거 (KF-13의 서버 쪽 원인).
- ops-feedback: I7 검토가 `X-Openit-User`를 필수로 요구하는 것은 이제 계약과 맞다(OF 보고의 계약 밖 헤더 항목 해소).

