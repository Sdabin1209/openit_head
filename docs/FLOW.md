# 제품 흐름 명세 (2026-11-03 신설)

왜 이 문서가 있는가: 규칙(D-번호)·계약 스키마·영역 시험은 모두 통과했는데 "어떤 문진표로 문진하는가", "결과가 어디로 가는가", "순서는 어디서 오는가"가 비어 있었다(U83~U90). 단계 사이를 잇는 값은 영역 하나의 시험으로는 보이지 않는다. 이 표는 제품을 처음부터 끝까지 한 줄로 따라가며 **각 단계의 입력을 누가 정하고, 어느 계약 필드에 실리고, 누가 저장하고 누가 읽는지**를 적는다. 빈칸이 결함이다. 새 기능·계약 변경은 이 표를 먼저 고친다.

| 단계 | 행위자 | 정하는 값 | 계약 필드(정본) | 저장 | 읽음 | 수용 시험(E2E 단계) |
|---|---|---|---|---|---|---|
| 1 저작 | 저자 | 문진표 ID·제목·문항(순서 `order`·선행 조건 `prerequisite`·칸·문장) | 문진 스키마 `QuestionBank`(4.0.0) ← question-authoring 텍스트 양식 | question-authoring DB(버전) | release-gate(I1) | 양식 둘 등록·확정 |
| 2 승인 | 승인자 | 함께 운영할 문진표 목록 + 모델 패키지 | `GateSubmissionRequest.subject.question_sets[]` → `GateDecision`·`ReviewReport`·`GateSubmission.subject.question_sets[]` → `ReleaseManifest.question_sets[]`(QuestionSetRef) | release-gate DB | survey-service(I4), admin-console | 세트 둘 제출·승인·활성, 구조 다른 세트 거절(U81) |
| 3 배치 | 운영자 | 기기마다 기본 문진표 | `DeviceConfig.question_set_id`(deploy 기기 설정), `KioskStartFragment.question_set_id`(시작 URL 조각, 조각이 먼저) | deploy 설정 | kiosk-frontend | 기기 A 배치, 기기 B 배치 없음 |
| 4 접수·시작 | 접수/환자 | (배치 없고 둘 이상이면) 선택 | I10 `GET /v1/question-sets` → `SESSION_START.question_set_id`(하나면 생략 가능) | survey-service 세션(세트 ID·제목) | survey-service | A 자동 시작·첫 문항 Q1.D01, B 목록 둘→선택→첫 문항 Q3, 모르는 ID 400 |
| 5 문진 | 환자·모델 | 다음 문항·끝 | 문진표 `order`·`prerequisite` → `QuestionFlowTable`(I9 extract `flow`, 연산자 6종) → 서버가 `next_item` 채움(ADR 0014) | 세션 상태 | model-runtime | 두 세션 끝까지, 건너뛰기 동작 |
| 6 결과 | 서비스 | 어느 문진표의 결과인지 | `SessionResult.question_set_id/title/question_bank_version`(PUBLIC_API B절), `result_ready` SSE | survey-service DB | admin-console(clinician) | 결과에 세트 ID·제목이 각각 맞음, clinician 조회·ack |
| 7 검토·학습 | 검토자·모델 실험 | 실패 사례의 문진표 | `FailureCase.question_set`(ArtifactRef, 세션의 세트), `DatasetManifest.question_sets`, `ModelPackageManifest.question_sets` | ops-feedback, dataset-store, model-registry | model-lab, release-gate(U81 대조) | (영역 시험) |

## 경계 밖(의식적으로 둔 것)
- 문항·칸 **구조**가 다른 문진표를 모델이 다루는 것: 학습 형식 변경(U77) 필요. 게이트가 구조 다른 세트를 거절한다(U81).
- 접수 시스템(HIS) 연동으로 환자별 문진표를 받는 것: 지금은 기기 배치와 화면 선택. 연동이 생기면 4단계의 입력원이 바뀌고 계약 필드는 그대로다.
- 운영 문진표의 임상 값(거절 설명·되묻기 문장·정책 한도·세션 설정·위험 기준): 사람 몫(U89).

## 점검
`scripts/rules-coverage.py`와 같은 방식의 자동 점검은 다음 라운드(흐름 단계 ↔ 계약 필드 ↔ E2E 단계 대응). 그 전까지는 계약 변경 때 이 표를 함께 고치는 것을 변경 기록(CHANGELOG)에서 확인한다.
