# 영역 경계 스키마 계약 승격 지시 (2026-10-29, 구조 규칙 6, D104)

규칙 6: 영역 사이를 오가는 스키마는 헤드의 책임이다. 각 영역이 낸 초안(`docs/change-requests/schemas/`, 59개)을 헤드가 분류했다. **확인한 것**: 초안 파일 목록과 각 CR의 "만드는 쪽 → 읽는 쪽" 서술을 읽었다. **확인하지 못한 것**: 각 초안의 세부 내용 전부(헤드는 CR 서술만 읽었다).

## 분류 원칙

- 두 영역(deploy 포함)이 만들고 읽으면 영역 사이 스키마다 → 계약으로 올린다.
- 읽는 쪽이 만든 부분집합 스키마는 두지 않는다. 읽는 쪽은 내는 쪽의 스키마를 쓴다(내는 쪽이 정본).
- 영역 밖의 당사자(학습 서버, 외부 데이터셋)와의 형식은 소유 영역에 남긴다. 계약이 아니다.
- 한 영역 안의 컴포넌트 사이 형식은 영역 몫이다(규칙 5).

## 계약 이름 (Pascal, 계약 패키지에서 `<이름>.schema.json`)

| 영역 | 승격 (초안 → 계약 이름) | 승격하지 않음 |
|---|---|---|
| admin-console | ActivateRequest, ApprovalRequest, CaseReviewRequest, ListEnvelope (그대로) | DeidentifiedTraceView: ops-feedback이 내는 `OpsFeedbackDeidentifiedTrace`를 쓴다(읽는 쪽 부분집합 금지) |
| deploy | build-image-request→BuildImageRequest, build-image-result→BuildImageResult, exposure→Exposure, image-labels→ImageLabels, jobs-declaration→JobsDeclaration, publish-request→PublishRequest, publish-result→PublishResult, setup-env-report→SetupEnvReport | |
| kiosk-frontend | DeviceConfig, KioskStartFragment, StaffPushPayload, StaticImageInterface, TurnOutcome (그대로) | |
| model-lab | model-package-layout→ModelPackageLayout, regression-trace-input→RegressionTraceInput(ops-feedback이 내는 trace의 읽는 부분집합이라 `OpsFeedbackDeidentifiedTrace`로 대체 가능한지 먼저 판단하고 가능하면 승격하지 않는다) | server-dataset-row, server-train-invocation, train-wrap-record (학습 서버와의 형식. model-lab에 남긴다) |
| model-runtime | ServingConfig, RuntimeInfo, ReleaseLoadStatus, RuntimeProfile (그대로), RuntimeFlowFile | |
| ops-feedback | ops-feedback-deidentified-trace→OpsFeedbackDeidentifiedTrace, -failurecase-ext→OpsFeedbackFailureCaseExt, -job-config→OpsFeedbackJobConfig, -job-result→OpsFeedbackJobResult, -readyz→OpsFeedbackReadyz, -server-env→OpsFeedbackServerEnv | |
| question-authoring | authoring-requests→AuthoringRequests, authoring-responses→AuthoringResponses, signals-response→SignalsResponse, ext-question-authoring→QuestionAuthoringExt, deploy-interface→QuestionAuthoringDeployInterface | |
| release-gate | gate-job-config→GateJobConfig, gate-job-result→GateJobResult, gate-policy→GatePolicy, gate-readyz→GateReadyz, gate-ext→GateExt | gate-build-context (파일이 아니라 환경 변수·디렉터리 규약이다. deploy의 BuildImageRequest로 다룬다) |
| survey-service | purge-output→SurveyPurgeOutput, question-bank-read→SurveyQuestionBankRead, readyz-body→SurveyReadyz, service-env→SurveyServiceEnv | image-labels: deploy의 `ImageLabels`로 통합(다르면 차이를 보고), question-flow-table-args: 문진 서비스 안(LangGraph 노드와 turn-engine)이라 영역 몫 |
| synthetic-data | _defs→SyntheticDefs, job-config-run→SyntheticJobConfigRun, job-config-import→SyntheticJobConfigImport, job-result→SyntheticJobResult, job-error→SyntheticJobError, import-report→SyntheticImportReport, run-report→SyntheticRunReport | training-data-row (외부 데이터셋 담당과의 형식) |

## 영역이 준비할 것 (코드는 바꾸지 않는다)

각 영역은 작업 브랜치 `wo6`(영역 worktree에서 `main`으로부터)에 `docs/change-requests/contract-ready/`를 만든다.

1. `schemas/<계약 이름>.schema.json`: `$id`는 `<계약 이름>.schema.json`(상대), `$schema` 2020-12, `title`은 계약 이름. 다른 승격 스키마를 가리키는 `$ref`는 `<계약 이름>.schema.json`으로, 공통 정의는 `_common.schema.json#/$defs/...`로(이미 있는 것은 중복 정의하지 않는다. 있는지 계약 `boundary_contracts/schemas/_common.schema.json`을 읽어 확인한다).
2. `examples/valid/<계약 이름>[.변형].json`: 통과해야 하는 예시(실제 코드·설정이 낸 값). `examples/invalid/<계약 이름>[.변형].json`: 거부되어야 하는 예시, 형식마다 1개 이상.
3. `MANIFEST.json`: 항목마다 `{name, source_draft, producer, consumers, unknown_keys: "reject"|"ignore", note}`. `$defs` 묶음(AuthoringRequests 등)은 어떤 `$defs`로 예시를 검증하는지 `def` 필드에 적는다.
4. 위 파일을 자체 스크립트로 검증한 실제 출력(통과 N건, 거부 N건)을 보고에 붙인다.
5. 이웃에 의존하는 불변식(예: 상대 영역이 읽는 필드)은 읽지 못했다면 `note`에 "이웃 쪽 미확인"이라 쓴다.

헤드가 `boundary-contracts`로 옮기고(`conformance/examples/`) 계약 시험에 넣는다. 계약에 올라간 뒤 영역이 손코드 검증을 스키마 검증으로 바꾼다(다음 단계).
