# 영역 경계 스키마 사용표(생성 파일)

`head/scripts/schema-usage.py`가 영역 리포지토리의 추적 파일에서 스키마 이름이 검증 호출에 나타나는 곳을 센 결과다. 손으로 고치지 않는다.
승격 기록(`boundary-contracts/conformance/promoted/*.MANIFEST.json`)의 producer/consumers는 승격 시점의 기록이고, 현재 사용은 이 표가 정본이다(U46).
칸의 값은 `코드 파일 수/시험 파일 수`. 문자열 이름으로 부르는 호출만 센다(변수로 이름을 넘기는 곳은 세지 않는다).

| 스키마 | model-runtime | model-lab | synthetic-data | survey-service | release-gate | ops-feedback | question-authoring | kiosk-frontend | admin-console | deploy | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ActionExtraction | 2/2 | 0/2 | 0/1 |  |  |  |  |  |  | 2/1 |  |
| ActionExtractionInput |  | 0/1 |  | 0/1 |  |  |  |  |  | 1/1 |  |
| ActivePointer |  |  |  |  | 0/2 |  |  |  |  | 1/0 |  |
| ApprovalRequest |  |  |  |  | 0/1 |  |  |  |  | 1/2 |  |
| BoundaryError |  |  |  |  | 0/2 |  |  |  |  | 1/0 | 0/1 |
| BuildImageRequest | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 |  |  | 1/0 |  |
| BuildImageResult | 1/1 | 1/1 | 1/1 | 0/2 | 1/1 | 1/1 | 1/1 |  |  | 1/0 |  |
| ChangeClassification |  |  |  |  |  |  | 0/1 |  |  | 1/0 |  |
| DatasetManifest |  | 1/1 |  |  |  |  |  |  |  | 1/0 |  |
| EvaluationReport |  | 1/4 |  |  |  |  |  |  |  | 1/0 |  |
| Exposure |  | 1/2 | 0/1 | 0/1 | 1/2 | 1/2 | 0/1 |  |  | 1/1 |  |
| ExtractRequest |  |  |  | 0/2 |  |  |  |  |  | 1/0 |  |
| FailureCase |  |  | 1/0 |  |  |  |  |  |  | 1/0 |  |
| GateApproval |  |  |  |  | 0/2 |  |  |  |  | 1/0 |  |
| GateDecision |  |  |  |  | 0/1 |  |  |  |  | 1/0 |  |
| GateExt |  |  |  |  | 0/1 |  |  |  |  |  |  |
| GateJobConfig |  |  |  |  | 1/0 |  |  |  |  |  |  |
| GateJobResult |  |  |  |  | 1/0 |  |  |  |  |  |  |
| GatePolicy |  |  |  |  | 1/0 |  |  |  |  |  |  |
| GateSubmission |  |  |  |  | 0/1 |  |  |  |  | 1/0 |  |
| ImageLabels | 0/1 | 0/1 | 0/2 | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |  |  |  |
| IngestResult |  |  |  |  |  |  |  |  |  | 1/0 |  |
| JobsDeclaration |  |  | 0/1 |  |  |  |  |  |  | 1/0 |  |
| ModelPackageLayout |  | 1/1 |  |  |  |  |  |  |  |  |  |
| ModelPackageManifest | 0/1 | 2/3 |  |  |  |  |  |  |  | 2/0 |  |
| OpsFeedbackDeidentifiedTrace |  | 1/1 |  |  |  | 0/1 |  |  |  |  |  |
| OpsFeedbackFailureCaseExt |  |  |  |  |  | 0/1 |  |  |  |  |  |
| OpsFeedbackJobConfig |  |  |  |  |  | 1/1 |  |  |  |  |  |
| OpsFeedbackJobResult |  |  |  |  |  | 1/1 |  |  |  |  |  |
| OpsFeedbackReadyz |  |  |  |  |  | 1/1 |  |  |  |  |  |
| OpsFeedbackServerEnv |  |  |  |  |  | 1/1 |  |  |  |  |  |
| PublishRequest |  |  |  |  |  |  |  |  |  | 0/1 |  |
| PublishResult |  |  |  |  |  |  |  |  |  | 0/1 |  |
| QuestionFieldSpec |  |  |  | 1/1 |  |  | 0/1 |  |  | 1/0 |  |
| QuestionFlowTable |  | 1/0 |  | 0/1 |  |  |  |  |  |  |  |
| ReleaseLoadStatus | 0/1 |  |  |  |  |  |  |  |  |  |  |
| ReleaseManifest | 1/1 |  |  | 1/0 | 0/2 |  |  |  |  | 1/0 |  |
| ResponseRequest | 0/1 |  |  | 0/1 |  |  |  |  |  | 1/1 |  |
| ResponseText | 0/1 |  |  |  |  |  |  |  |  | 0/1 |  |
| ReviewRecord |  |  |  |  |  |  | 0/1 |  |  | 1/0 |  |
| ReviewReport |  |  |  |  | 0/2 |  |  |  |  | 1/0 |  |
| RollbackReceipt |  |  |  |  | 0/2 |  |  |  |  | 1/0 |  |
| RollbackRequest |  |  |  |  |  |  |  |  |  | 1/0 |  |
| RuntimeFlowFile | 1/0 |  |  |  |  |  |  |  |  |  |  |
| RuntimeInfo | 0/1 |  |  |  |  |  |  |  |  |  |  |
| RuntimeProfile | 1/0 |  |  |  |  |  |  |  |  |  |  |
| ServingConfig | 1/0 |  |  |  |  |  |  |  |  |  |  |
| SessionState |  |  |  |  |  |  |  |  |  | 1/0 |  |
| SetupEnvReport | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |  |  | 1/0 |  |
| StaffAlert |  |  |  |  |  |  |  |  |  | 1/0 |  |
| StaffAlertPage |  |  |  |  |  |  |  |  |  | 1/0 |  |
| StaffCallRetryResult |  |  |  |  |  |  |  |  |  | 1/0 |  |
| StaffPushPayload |  |  |  | 0/1 |  |  |  |  |  |  |  |
| SubmissionView |  |  |  |  | 0/1 |  |  |  |  |  |  |
| SurveyQuestionBankRead |  |  |  |  | 0/1 |  |  |  |  |  |  |
| SurveyReadyz |  |  |  | 0/1 |  |  |  |  |  | 0/1 |  |
| SurveyRiskRulesFile |  |  |  | 1/1 |  |  |  |  |  | 1/1 |  |
| SurveyServiceEnv |  |  |  | 1/0 |  |  |  |  |  |  |  |
| SyntheticImportReport |  |  | 0/1 |  |  |  |  |  |  |  |  |
| SyntheticJobConfigImport |  |  |  |  |  |  |  |  |  | 0/1 |  |
| SyntheticJobError |  |  | 0/1 |  |  |  |  |  |  | 1/0 |  |
| SyntheticJobResult |  |  | 0/1 |  |  |  |  |  |  |  |  |
| SyntheticRunReport |  |  | 0/1 |  |  |  |  |  |  |  |  |
| TraceEnvelope |  |  |  | 1/1 |  |  |  |  |  | 1/0 |  |

## 이 방식으로 찾지 못한 스키마 21개

공통 정의·하위 정의($ref로만 쓰임)이거나, 변수로 이름을 넘겨 쓰이거나, 실제로 읽는 쪽이 없는 것이다. 하나씩 따진 결과는 OPEN_GAPS U47.

- ActionExtractionRules
- ActionExtractionSample
- ActivateRequest
- AuthoringRequests
- AuthoringResponses
- CaseReviewRequest
- DeviceConfig
- GateReadyz
- GateSubmissionRequest
- KioskStartFragment
- ListEnvelope
- PushConfig
- QuestionAuthoringDeployInterface
- QuestionAuthoringExt
- ResponseSample
- SignalsResponse
- StaffCallReport
- StaffCallRetryRequest
- SurveyPurgeOutput
- SyntheticDefs
- SyntheticJobConfigRun
