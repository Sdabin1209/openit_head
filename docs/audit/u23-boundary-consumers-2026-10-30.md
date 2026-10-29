# U23 감사: 승격 경계 스키마 49개의 소비자 쪽 확인 (2026-10-30)

OPEN_GAPS U23, D107·D108. 범위: `boundary-contracts/boundary_contracts/schemas`에 있는 승격 스키마 49개(`audit/boundary-schema-promotion-2026-10-29.md`의 이름 중 D108이 뺀 `TurnOutcome`과 승격하지 않은 것 제외).

## 방법과 한계

- **확인한 것**: 각 영역 main 작업 트리의 소스를 정적으로 읽고 grep했다(`.venv/`, `node_modules/`, `build/`, `docs/change-requests/` 아래 제외, 예외로 deploy `scripts/`·`config/`는 읽음). 낸 쪽과 읽는 쪽은 계약 `conformance/promoted/*.MANIFEST.json`의 producer/consumers 선언을 출발점으로 삼고 코드에서 실제로 있는지 확인했다.
- **확인하지 못한 것**: 시험·컨테이너를 돌리지 않았다. 영역 CI(`PublishRequest`의 내는 쪽)는 워크스페이스에 없다. 런타임에 값이 실제로 계약을 통과하는지는 보지 않았다(정적 읽기뿐). `ServingConfig`·`RuntimeProfile` 등 손코드가 계약 스키마와 정확히 같은 규칙인지 항목별로 대조하지는 않았다(모양이 겹치는 것만 확인).
- **판정 값 추가 1개**: 주어진 값에 없는 `계약 불일치`(내는 쪽 실제 출력이 계약 스키마를 어김)를 1건에 썼다.
- **손코드 중복의 두 종류**: (A) 계약 검증기를 쓰면서 같은 모양을 또 검사 (B) 읽는 쪽이 계약 검증기를 쓰지 않고 같은 규칙을 손으로만 구현(계약 검증으로 바꿀 후보). 줄에 A/B를 적었다.
- 읽는 쪽이 필드를 읽기만 하고 같은 모양을 또 검사하지 않으면 OK로 봤다(계약 검증기 없이 읽는 경우는 "근거"에 적음).

## 판정별 개수

| 판정 | 개수 |
|---|---|
| OK | 25 |
| 손코드 중복 | 7 (A 1, B 6) |
| 계약 밖 읽기 | 3 |
| 소비자 없음 | 12 |
| 확인 불가 | 1 |
| 계약 불일치(추가 값) | 1 |
| 합계 | 49 |

## 표

### admin-console

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| ActivateRequest | admin-console `api/releases.ts:61-63` (`assertRequest`로 보내기 전 검증) | release-gate `release_gate/app.py:415-429` | 아니오. 본문에서 `release_id`만 읽음(`app.py:429`), 스키마 검증 없음 | 모양 검사 없음(역할은 토큰, `app.py:416-419`) | OK (읽는 쪽 계약 미사용, 중복 검사도 없음) |
| ApprovalRequest | admin-console `api/client.ts:57-58` (`assertRequest`) | release-gate `release_gate/app.py:400-411`, `gate.py:290-322` | 아니오. `GateApproval`(결과 레코드)만 검증(`gate.py:322`), 요청 모양(`ApprovalRequest`)은 검증하지 않음 | `gate.py:293-304` dict 여부·`submission_id` 필수·`approver_role` 일치·서버 채움 키 거부를 손으로 함; `app.py:407` approver_id 대조 | 손코드 중복 (B) |
| CaseReviewRequest | admin-console `api/cases.ts:53` (`assertRequest`) | ops-feedback `src/ops_feedback/api.py:287-317` | 아니오 | `api.py:306-316` 키 집합(`set(body) - {...}`)·`review_status` 필수·`expected` 타입·`reviewed_input` 타입·`expected_kind` 조합을 손으로 검사 | 손코드 중복 (B) |
| ListEnvelope | release-gate `app.py:363,373,388`; ops-feedback `api.py:250` (자기 검사 없음) | admin-console `api/contract.ts:31-36` (`readEnvelope`가 `ListEnvelope` 검증기 사용; 호출 `client.ts:38`, `cases.ts:32`, `releases.ts:51`) | 예 | 없음 | OK |

### deploy

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| BuildImageRequest | 내는 쪽 없음(deploy가 `build-images.sh`로 직접 빌드) | 받을 `scripts/build-image.sh`가 어느 영역에도 없음(`ls <영역>/scripts`) | 해당 없음 | deploy가 영역마다 다른 Dockerfile 인자를 직접 안다: `deploy/scripts/build-images.sh:96-98, 104-105, 111-113, 131-132, 146-147, 169-170, 179, 186` (`COMMIT`/`REVISION`/`BOUNDARY_TAG`/`BC_VERSION`/`BOUNDARY_CONTRACT`...) | 계약 밖 읽기 (구조 규칙 1: Dockerfile 인자에 기댐) |
| BuildImageResult | 내는 쪽 없음 | deploy `build-images.sh`가 영역 빌드 산출 파일을 직접 읽음: `:92` `survey-service/build/wheels/VERSIONS.env`, `:104-105` `question-authoring/build/contracts.tag`·`survey-schema.tag`, `:111-112` `ops-feedback/build/wheels/BOUNDARY_TAG` | 아니오 | 위와 같음 | 계약 밖 읽기 (이웃 파일 구조) |
| Exposure | 라벨 `io.openit.exposure`를 다는 영역 Dockerfile 없음(`grep io.openit.exposure` 결과 deploy 검사기뿐) | deploy `scripts/check_image_labels.py:47`이 라벨이 있을 때만 검증. 노출 규칙은 `config/Caddyfile`에 손으로 적음(생성하지 않음) | 해당 없음 | 없음 | 소비자 없음 (내는 쪽도 없음) |
| ImageLabels | 영역 Dockerfile `LABEL`(예 `kiosk-frontend/Dockerfile:19-23`, `model-lab/Dockerfile:37-42`, `model-runtime/Dockerfile:41-46`) | deploy `scripts/lib.sh:19-21` `validate_image_labels` → `check_image_labels.py`(설치된 계약 패키지 우선, 없으면 `docs/change-requests/contract-ready` 사본) ← `build-images.sh:84`, `publish-image.sh:57`, `publish-images.sh:24` | 예 | `publish-image.sh:52-55` 필수 4키·`revision` unknown을 손으로 먼저 검사한 뒤 바로 계약 검증(`:57`)을 또 함; `e2e.sh:275`(`labels6` 키 6개 존재), `e2e.sh:284`(`labels_kiosk`) | 손코드 중복 (A) |
| JobsDeclaration | 라벨 `io.openit.jobs`를 다는 영역 없음 | deploy `check_image_labels.py:47`이 있을 때만 검증; 잡 정의는 `config/systemd/*.service`·compose에 손으로 있음 | 해당 없음 | 없음 | 소비자 없음 (내는 쪽도 없음) |
| PublishRequest | 영역 CI(워크스페이스에 없음, `deploy/docs/ci-example/publish-image.yml`만) | deploy `scripts/publish-image.sh:28-38` | 아니오. argv를 손으로 파싱; 서비스 이름은 `lib.sh:49` `SERVICES` 목록과 대조(`publish-image.sh:37`) | 스키마의 `service` enum과 `lib.sh` `SERVICES`가 두 정본(동기화 확인 못 함) | 확인 불가 (내는 쪽 CI가 워크스페이스에 없음; 읽는 쪽은 CLI 인자라 스키마 검증기 없음) |
| PublishResult | deploy `publish-image.sh:100` (표준 출력 마지막 줄 `PUBLISHED/UNCHANGED ...`, JSON 아님) | 영역 CI 없음. `deploy/docs/ci-example/publish-image.yml:42,47`이 `tail -1`과 문자열 비교만 | 아니오 | 없음 | 소비자 없음 |
| SetupEnvReport | 영역 `scripts/setup-env.sh` 10개는 있으나 JSON 한 줄을 내지 않음(`grep status\|environment` 결과 없음) | deploy `prepare-areas.sh:52-55`은 종료 코드·시간만 씀; `doctor.sh:110` 이웃 `.venv/bin/python`과 `import pytest`, `:122` 이웃 `node_modules`를 직접 확인 | 아니오 | `doctor.sh:109-123`이 계약의 `environment` 선언 대신 경로를 추측 | 계약 밖 읽기 (구조 규칙 1: 이웃 `.venv`·`node_modules`) |

### kiosk-frontend

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| DeviceConfig | deploy `scripts/kiosk-add-device.sh:23` (`{"device_token","allow_remote_stt"}`, 스키마 검증 없이 생성) | kiosk-frontend `api/device.ts:56`, `api/contract.ts:7,16-24` | 예 | 없음(`device.ts:10`은 정규식을 되풀이하지 않고 검증기 호출) | OK |
| KioskStartFragment | 병원 접수/시연(영역 밖) | kiosk-frontend `api/device.ts:45` | 예 | 없음 | OK |
| StaffPushPayload | survey-service `survey_service/alerts.py:541` — 실제 키는 `type, alert_id, session_id, kind`(테스트가 이 4개를 단정: `tests/test_staff_alerts.py:116`) | kiosk-frontend `apps/staff/pushbody.ts:8` (`validateStaffPushPayload`) | 예 | 없음 | 계약 불일치. 스키마는 `session_id`(필수)·`kind`·`alert_id`만 허용하고 `additionalProperties:false`인데 내는 쪽이 `type`을 더 실어, 읽는 쪽이 항상 거부하고 일반 문구("새 알림이 있습니다")로 떨어진다. 어느 쪽을 고칠지는 헤드 결정 |
| StaticImageInterface | kiosk-frontend: 예시·시험(`test/image-contract.test.ts`)만 | deploy는 선언을 읽지 않고 `config/Caddyfile:343,357`에 `kiosk-frontend:8080`과 경로를 직접 적음 | 아니오 | 없음 | 소비자 없음 |

### model-lab, model-runtime

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| ModelPackageLayout | model-lab `model_lab/registry.py:60-72` (`layout_of`, 게시 때 자기 검사: `registry.py:118`, `packager.py:59`) | 선언된 읽는 쪽 release-gate·model-runtime은 이 문서를 읽지 않고 `canonical.directory_hash`와 시스템 프롬프트 해시를 직접 재계산(`release_gate/gate.py:377-382`, `reader.py:54-59`, `model_runtime/session.py:107-117`) | 아니오 | 없음(이웃은 `adapter_hash` 대조뿐이라 레이아웃 스키마 검사와 겹치지 않음) | 소비자 없음 |
| ServingConfig | model-lab(패키지에 담음, `model_lab/packager.py:57,69`) | model-runtime `serving_config.py:11-59`, release-gate(`ReleaseManifest` 검증 안에서) | 아니오(model-runtime·model-lab 모두 계약 `ServingConfig`가 아니라 model-runtime 사본을 씀: `serving_config.py:55,59`, model-lab `packager.py:57`, `pipeline.py:203`) | `SERVING_CONFIG_SCHEMA` 전체가 계약 스키마와 같은 모양을 영역 안에 다시 정의(두 정본) | 손코드 중복 (B, 스키마 사본) |
| RuntimeInfo | model-runtime `server.py:306-319` (자기 검사 없음) | deploy `scripts/probe-serving.py:192`(`loaded`), `e2e_steps.py:325,340`(`serving_config_expectation`, `runtime_version`) | 아니오(검증기 없이 필드만 읽음) | 중복 검사 없음 | OK (스키마가 정한 필드만 읽음) |
| ReleaseLoadStatus | model-runtime `server.py` (PUT/GET `/v1/releases/{id}`; 자기 검사 없음) | survey-service는 계약 클라이언트 `HttpModelRuntime`만 씀(`survey_service/remote.py:18`) | 클라이언트가 받음(스키마 대신 손 검사, 범위 밖 발견 참조) | survey-service 쪽 없음 | OK |
| RuntimeProfile | model-runtime `profiles/*.json` | model-runtime `vllm_backend.py:32-43` `load_profile` | 아니오 | `load_profile`이 형식·`engine` 모르는 키(`_ENGINE_KEYS`, `:27,40`)를 손으로 검사 | 손코드 중복 (B) |
| RuntimeFlowFile | deploy·survey-service 시험 설정 | model-runtime `backends.py:67-145` (`load_fake_flow`, `load_fake_flow_spec`, `load_fake_corrections`, `load_fake_reasks`) | 아니오 | 위 4개 함수가 `order/slots/skips/corrections/reasks` 모양을 손으로 검사 | 손코드 중복 (B) |

### ops-feedback

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| OpsFeedbackDeidentifiedTrace | ops-feedback `deid.py:349,419` (자기 검사, fail-closed) | admin-console `api/cases.ts:48`(`assertResponse`); model-lab `model_lab/regression.py:73`(`validator(...).is_valid`); question-authoring `signals.py:30-40`은 클라이언트로 받아 `extract_input.question_id`만 읽음(검증 없음); synthetic-data는 trace를 읽지 않음(`seeds.py:70-74`가 `reviewed_input`만 씀) | admin-console·model-lab 예 / question-authoring 아니오 | 없음 | OK |
| OpsFeedbackFailureCaseExt | ops-feedback `job.py:162-171`, `review.py:126-131` (검증 없음) | 선언된 admin-console·model-lab·synthetic-data 코드에 `ext["ops-feedback"]`를 읽는 곳 없음; 읽는 곳은 ops-feedback 자신뿐(`rollback.py:52`) | 해당 없음 | 없음 | 소비자 없음 |
| OpsFeedbackJobConfig | deploy `config/ops-feedback-job.yaml`(검증 없이 둠) | ops-feedback `config.py:46-50` | 예 | 조합 불변식만 따로(`config.py:51-55`, 스키마로 못 쓰는 것이라 중복 아님) | OK |
| OpsFeedbackJobResult | ops-feedback `job.py:351-357` (자기 검사) | deploy: 운영은 종료 코드만(`config/systemd/openit-ops-feedback-job.service`, `scripts/job-metrics.sh`), E2E는 stdout JSON의 `cases_published`를 읽음(`e2e_steps.py:1372,1382`) | 아니오(스키마 필드만 읽음) | 없음 | OK |
| OpsFeedbackReadyz | ops-feedback `api.py:280-283` (자기 검사, 어긋나면 로그만) | deploy 상태 확인(상태 코드; `scripts/status.sh`), gateway | 아니오(본문은 진단용, 상태 코드로 판단) | 없음 | OK |
| OpsFeedbackServerEnv | deploy `config/ops-feedback-ingest.env`·compose | ops-feedback `config.py:63-72`, `api.py:377` | 예 | 값 범위는 코드가 따로 검사(`api.py:404-408`; 스키마가 모양만 봄이라 중복 아님) | OK |

### question-authoring, release-gate

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| AuthoringRequests | 선언은 "콘솔/gateway"인데 이를 보내는 코드가 워크스페이스에 없음(admin-console은 문항 작성 API를 부르지 않음) | question-authoring `http_api.py:46-48`, `contract.py:34-37`, `http_api.py:236,257` | 예 | 없음 | OK (읽는 쪽만 있음) |
| AuthoringResponses | question-authoring `http_api.py:229-230` (자기 검사) | 읽는 콘솔 코드 없음(admin-console `grep authoring` 결과 없음) | 해당 없음 | 없음 | 소비자 없음 |
| SignalsResponse | question-authoring `http_api.py:234,249` (자기 검사) | 읽는 콘솔 코드 없음 | 해당 없음 | 없음 | 소비자 없음 |
| QuestionAuthoringExt | question-authoring `service.py:423,439,479` (`contract.check_ext`) | 선언된 release-gate·synthetic-data·admin-console에 `ext["question-authoring"]`를 읽는 곳 없음 | 해당 없음 | 없음 | 소비자 없음 |
| QuestionAuthoringDeployInterface | question-authoring `http_api.py:109`(ReadyzResponse 자기 검사), `__main__.py:46-53`(Environment 검사); `PurgeResult`는 `__main__.py:157`에서 검사 없이 출력 | deploy: 상태 코드(`e2e.sh:208`), purge는 한 줄 존재만(`e2e.sh:271`) | Environment는 qa가 계약으로 받음; deploy는 아니오 | 없음 | OK |
| GateJobConfig | deploy(운영 설정) | release-gate `main.py:135-141` | 예 | 없음 | OK |
| GateJobResult | release-gate `main.py:274-278` (`emit` 자기 검사) | deploy: 종료 코드와 마지막 줄 표시만(`e2e_steps.py:476,487`) | 아니오 | 없음 | OK |
| GatePolicy | deploy(정책 파일, 선택) | release-gate `policy.py:23-27` | 예 | 없음 | OK |
| GateReadyz | release-gate `app.py:348-358` (자기 검사 없음) | deploy `config/prometheus/json-exporter.yml:8-14`가 `judging_loop.*` 필드를 읽음(스키마에 있는 필드) | 아니오(경로 읽기) | 없음 | OK |
| GateExt | release-gate `gate.py:114-116` (자기 검사) | 선언된 admin-console·ops-feedback에 `ext["release-gate"]`를 읽는 곳 없음(`admin-console/api/types.ts`는 `ext`를 불투명 객체로만 둠) | 해당 없음 | 없음 | 소비자 없음 |

### survey-service, synthetic-data

| 스키마 | 내는 영역(위치) | 읽는 영역(위치) | 읽는 쪽이 계약으로 받는가 | 손코드로 다시 검사하는 곳 | 판정 |
|---|---|---|---|---|---|
| SurveyServiceEnv | deploy `config/survey.env`·compose | survey-service `survey_service/settings.py:137-177` (`Settings.from_env`) | 아니오(`validator`·`load_schema` 사용 없음) | `settings.py:137-177`과 `_int`·`_retention`·`_float` 보조 함수가 `SURVEY_*` 이름·형식·범위를 손으로 읽음; 모르는 `SURVEY_*` 이름 거부(계약 `unknown_keys: reject`)는 코드에 없음 | 손코드 중복 (B) |
| SurveyPurgeOutput | survey-service `retention.py:28-48` (자기 검사 없음) | deploy `e2e.sh:270`은 JSON 파싱 가능 여부만 | 아니오 | 없음 | OK |
| SurveyReadyz | survey-service `service.py:303-314` (자기 검사 없음) | deploy `e2e_steps.py:1805-1812`(`trace_outbox.pending/sent`), `scripts/status.sh` | 아니오(스키마 필드 읽기) | 없음 | OK |
| SurveyQuestionBankRead | 선언은 release-gate 서버인데 해당 엔드포인트 없음(`release-gate/release_gate/app.py` 라우트에 `question-bank` 없음) | survey-service는 `load_bundle`로 문항 세트를 받음(`release/loader.py:188`) | 해당 없음 | 없음 | 소비자 없음 (내는 쪽도 없음: 제안 단계) |
| SyntheticDefs | synthetic-data(`$defs`) | synthetic-data `store/spec.py:17`·`contract_check.py`가 `SyntheticJobConfigRun/Import` 안에서 참조 | 예 | 없음(`spec.py:17` 주석대로 형식 재검사 안 함) | OK |
| SyntheticJobConfigRun | deploy `e2e_steps.py:245-257`(E2E 설정 생성), 개발자 | synthetic-data `config.py:66` (`check_config`) | 예 | 스키마로 못 쓰는 불변식만 따로(`config.py:69-93`) | OK |
| SyntheticJobConfigImport | deploy `e2e_steps.py:imp_config`(~270-279), 개발자 | synthetic-data `importer.py:104` | 예 | 없음 | OK |
| SyntheticJobResult | synthetic-data `__main__.py:24` (`check_output`) | deploy E2E `e2e_steps.py:261-264,283-312`(`status`, `counts`, `version`을 필드로 읽음; 검증 없음); 운영 스케줄러는 종료 코드만 | 아니오 | 없음 | OK |
| SyntheticJobError | synthetic-data `__main__.py:46` | deploy가 stderr 한 줄을 파싱하는 곳 없음(종료 코드·원문 표시만) | 해당 없음 | 없음 | 소비자 없음 |
| SyntheticImportReport | synthetic-data `importer.py:411` | deploy `e2e_steps.py:286,297-304`(`invalid_reasons_by_file`, `inputs`) | 아니오(필드 읽기) | 없음 | OK |
| SyntheticRunReport | synthetic-data `job.py:217` | deploy `e2e_steps.py:1442`이 `report.json` 파일을 읽음(문자열 포함 여부만) | 아니오 | 없음 | OK |

## 손코드 중복·계약 밖 읽기·계약 불일치 요약

- 손코드 중복 (A): `ImageLabels` — `deploy/scripts/publish-image.sh:52-55`가 계약 검증(`:57`) 앞에서 같은 필수 키·`unknown`을 다시 검사. E2E의 `e2e.sh:275,284`도 키 존재를 따로 확인.
- 손코드 중복 (B, 걷어낼 후보): `ApprovalRequest`(release-gate `gate.py:293-304`), `CaseReviewRequest`(ops-feedback `api.py:306-316`), `ServingConfig`(model-runtime `serving_config.py:11-59`, 스키마 사본), `RuntimeProfile`(model-runtime `vllm_backend.py:32-43`), `RuntimeFlowFile`(model-runtime `backends.py:67-145`), `SurveyServiceEnv`(survey-service `settings.py:137-177`).
- 계약 밖 읽기: `BuildImageRequest`·`BuildImageResult`(deploy `build-images.sh`가 영역마다 Dockerfile 인자와 이웃 빌드 산출 파일을 직접 앎), `SetupEnvReport`(deploy `doctor.sh:109-123`이 이웃 `.venv`·`node_modules` 경로를 추측).
- 계약 불일치: `StaffPushPayload` — survey-service `alerts.py:541`이 스키마에 없는 `type` 키를 실어 kiosk-frontend 검증이 항상 실패한다.

## 범위 밖 발견 (고치지 않음)

1. 계약 클라이언트가 스키마 대신 손 검사를 한다(boundary-contracts 소유): `clients/runtime.py:44-51` `ReleaseLoadStatus` 상태값 검사, `clients/_http.py:336-344` `ListEnvelope` 검사, `clients/ops.py:38-42` `get_trace`가 `OpsFeedbackDeidentifiedTrace`를 검증하지 않음.
2. `deploy/docs/boundary.md` 1절 "이 영역은 계약을 소비하거나 생산하지 않는다"와 2절 "E2E의 검증기로만"이 현재 코드와 어긋난다(deploy는 `ImageLabels`로 게시 전 검증, `check_image_labels.py`, 라벨·잡 스키마 8개를 소비).
3. deploy E2E가 synthetic-data를 이웃의 `.venv`와 `cwd`로 직접 실행한다(`e2e_steps.py:159, 261-263, 283`): 이웃 파일 구조에 기댐(구조 규칙 1).
4. question-authoring `__main__.py:157`은 purge 출력을 "계약 PurgeResult"라고 주석하지만 검증하지 않는다(`http_api.py:109`의 readyz와 달리).
5. 승격 대상 중 낸 쪽 또는 읽는 쪽이 아직 없는 것이 많아(소비자 없음 12건 중 `Exposure`·`JobsDeclaration`·`BuildImage*`·`SurveyQuestionBankRead`·`SetupEnvReport`는 내는 쪽도 없음) MANIFEST의 producer/consumers 선언이 현재 코드와 어긋난다. 선언을 현재 사실로 고칠지, 영역이 구현할지 정해야 한다.
6. `PublishRequest.service` enum과 `deploy/scripts/lib.sh:49` `SERVICES` 목록이 두 정본이다(동기화 점검 없음).
