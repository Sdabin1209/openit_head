# 영역별 변경 지시: boundary-contracts 2.0.0 (D74, D75)

상태: 지시 초안(2026-10-27). 기준 계약은 태그 `v2.0.0`(`boundary-contracts`의 `CHANGELOG.md`와 `V2_DRAFT.md`). 각 영역 세션이 자기 리포의 `docs/change-requests/` 또는 브리프로 받아 일한다. 헤드가 영역 코드를 고치지 않는다. 확인/제안/미정을 구분했다.

## 공통

- 의존 계약을 `v2.0.0` 태그로 올리고 잠금 파일·이미지 라벨(`io.openit.contracts.boundary`)을 갱신한다. v1 레코드는 `UNSUPPORTED_VERSION`이다.
- LoRA-A/B 입출력은 고정이다. 기준 데이터는 학습 서버 `~/taehyeon/data/dataset_10_14`(탐색만 가능), 형식은 계약의 `ActionExtraction*`, `ResponseRequest`, `ResponseText`.
- 시험을 통과하기 전에 완료라고 하지 않는다. 푸시는 헤드에게 알린 뒤.

## 순서

1. 동시에 가능(서로 계약만 본다): **turn-engine**, **model-runtime**, **model-lab**, **release-gate**, **synthetic-data**, **ops-feedback**
2. 위가 태그를 낸 뒤: **survey-service**(turn-engine·model-runtime 새 태그를 쓴다)
3. 마지막: **deploy**(모든 새 태그로 `BOUNDARY_TAG`, `DEPLOY_MR_TAG` 등을 올려 E2E, 실제 LLM 데모)

## turn-engine (v0.3.0 제안)
- 정규화기·판정기·기록기·Plan(`normalizer.py`, `judge.py`, `writer.py`, `planner.py`)을 쓰지 않는다. 폐기 표시하고 제거 시점은 survey-service 이전이 끝난 뒤.
- 새로 만든다: `validate_extraction(input, output, flow) -> list[Violation]` (INTERFACES I8 시그니처 초안). 검사: `targets ⊂ values`의 키, `next_item` 규칙(REASK·CONFIRM·REDIRECT·그 밖), 건너뛰기 순서, `save` 규칙(ANSWERED·CORRECTION일 때만 true), MISSING·UNCLEAR·UNKNOWN·REJECTED이면 value null. `QuestionFlowTable`(문항 순서·건너뛰기)은 문진 스키마에서 만든다.
- 기준 시험: 학습 데이터 A 출력 전수(5,077행)가 위반 0이어야 한다(계약의 `tools/validate_dataset_v2.py`의 의미 검사와 같은 기준).

## model-runtime (v0.6.0 제안)
- 서버: `POST /v1/releases/{id}/extract`(JSON), `…/respond`(`text/plain`). 헤더 `X-Openit-Outcome`(extract는 ok, respond는 ok|fallback), `X-Openit-Attempts`, `X-Openit-Protections`.
- A 출력이 `ActionExtraction`을 못 지키면 재시도 후 503 `UNAVAILABLE`, `details.reason=OUTPUT_INVALID`. 값을 지어내지 않는다(D75). B의 대체 문장 규칙은 이 영역이 정한다.
- 시스템 프롬프트는 패키지의 `system_prompt`(경로·sha256)만 쓴다. 코드에 두지 않는다. 학습과 같은 채팅 템플릿(`enable_thinking=False`).
- 프로파일: 기반 모델을 프로파일로 고른다. 추가: `gpu-12g`를 Qwen3-4B로(적재 가능 여부와 A·B 어댑터 동시 적재는 **미확인**, 측정 후 확정), 24GB급은 Qwen3-8B. 어댑터의 기반 모델과 프로파일이 다르면 적재를 거부한다.
- `ParserOutput`/`GeneratorOutput` 참조(`schema_guard`, `prompts`)를 제거한다. 적합성은 계약의 `RuntimeReferenceServer`·`HttpModelRuntime`으로 확인.
- 이미지: Dockerfile, `/healthz`, `/readyz`, 라벨은 기존 규칙(D22, D50) 유지.

## survey-service
- LangGraph 노드를 재구성한다: 파서·정규화·판정·기록·Plan 노드를 `extract` 한 번과 `validate_extraction`으로 합친다. 시작(SESSION_START)은 A를 부르지 않고 B만 `action=START`로 부른다.
- B 입력은 표 찾기로 조립한다: `known`, `ask`, `previous`, `current`, `hold`, `topic`, `next{type,question_id,text}`. 이를 위해 문진 스키마(`schema/`)에 칸 설명표와 `ask` 문장 틀 표가 필요하다. 데이터셋 쪽 표가 미정(IO_SPEC 7장)이므로 먼저 데이터 형식에서 역으로 만든 초안으로 시작하고 사용자 확인을 받는다.
- 오류 처리(D75): 503 OUTPUT_INVALID와 `validate_extraction` 위반은 같은 요청을 1회 재시도, 그래도 안 되면 `turn_failure_signal`, 세션 상태 불변.
- Trace 키(`parser_*`, `normalizer_*`, `judge_*`, `planner_*`)는 이 영역이 소유하므로 `extract_*`, `validation_*`, `response_*` 등으로 바꾼다. 위험 신호·직원 호출이 v1 의도에서 왔다면 v2에서 어떻게 표현되는지(A의 `reason`·`note`) 먼저 정리해 헤드에게 보고한다(**미정**).
- `runtime_contract_version`은 이 영역이 소유한다(D75). 값이 다른 패키지는 적재를 거부한다.
- 기존 로더 재시도(8e0ba7e)는 그대로 둔다.

## model-lab
- `datasets.py`의 `PARSER`/`GENERATOR` 매핑을 `LORA_A → ActionExtractionSample`, `LORA_B → ResponseSample`로. 학습 서버의 `messages` 형식과 `*Sample` 사이 변환기가 필요하다.
- 패키징: 어댑터 디렉터리에 시스템 프롬프트 파일을 넣고 `ModelPackageManifest.system_prompt{path,sha256}`를 채워 게시한다.
- 평가·회귀의 v1 용어(`risk_signal_*`, `intent_accuracy` 등)를 정리한다(`METRICS.md` 영향, 지표 이름은 자유 문자열).
- 학습 서버 코드와의 관계(학습은 서버의 별도 코드로 이미 이뤄지고 있음)를 먼저 확인해 보고한다(**미정**).

## release-gate
- 릴리스 생성 때 `ReleaseManifest.adapters[LORA_A|LORA_B].system_prompt`를 패키지에서 복사한다.
- 계약 검사와 골든 케이스의 입출력을 v2 형식으로. `runtime_contract_version` 호환 기준은 D75(문진 스키마 정수 버전, 값이 다르면 거부).
- 클라이언트가 MAJOR 2를 읽도록 올린다.

## synthetic-data / ops-feedback
- synthetic-data: `store/base.py`, `quality.py`의 v1 샘플 검증을 v2 샘플로. 이 영역의 역할(데이터 생성은 학습 서버 파이프라인이 이미 함)은 사용자가 정해야 한다(**미정**).
- ops-feedback: `FailureCase.expected_kind`를 `LORA_A`/`LORA_B`로. `expected`는 객체 또는 문자열. `reviewed_input`은 `ActionExtractionInput` 또는 `ResponseRequest`로 검증. 비식별 trace 키·실패 유형 분류가 정규화·판정 단계에 묶였는지 확인해 보고한다.

## deploy
- `scripts/e2e_steps.py`: PUT 적재 → `extract` → `respond`(텍스트). 시험용 가짜 모델의 고정 출력을 v2 형식으로.
- 새 태그가 나온 뒤 `BOUNDARY_TAG=v2.0.0`, 영역 이미지 태그를 올리고, 잠금 파일을 갱신하고 E2E.
- 실제 LLM 데모: Qwen3 프로파일, 패키지에 프롬프트 포함. LoRA 교체 시험(D72)은 같은 기반 모델의 두 번째 어댑터로.

## 아직 정해지지 않은 것
- 정규화 쪽 수정 시점(다른 담당자), `ask` 문장 틀 표·칸 설명표, 12GB에서 Qwen3-4B와 두 어댑터 동시 적재, v1 의도(위험 신호 등)의 v2 대응, synthetic-data의 역할. 데이터셋 담당 요청: `dataset-requests.md`.
