# 평가 지표 v2 변경 제안 (D-C)

상태: **제안**(2026-10-27, 헤드). `boundary-contracts/METRICS.md`는 헤드 소유지만 이 세션에서는 고치지 않았다. 학습 담당자가 검토해 다듬는 문서이므로, 아래 항목을 담당자와 확인한 뒤 `boundary-contracts` 쪽에서 반영한다. 지표 이름은 `EvaluationReport.metrics[].name` 자유 문자열이라 이름을 바꿔도 계약은 깨지지 않는다(METRICS.md 첫 문단, `V2_DRAFT.md` 0장).

근거로 읽은 것(확인): `boundary-contracts/METRICS.md` 전체, `boundary-contracts/V2_DRAFT.md`(2장 LoRA-A/B 입출력, 0장 METRICS 영향), `docs/DECISIONS.md` D53·D59·D74~D84, `docs/migration-2.0.0.md`, `turn-engine/docs/boundary.md`, `model-runtime/docs/boundary.md`, `survey-service/docs/boundary.md`, `model-lab/docs/boundary.md`. 읽지 못한 것: 평가 구현 코드(`model-lab` 소스)와 `EvaluationReport` 스키마 파일 자체(slice kind가 열거인지 자유 문자열인지 확인하지 못함). 그래서 "구현이 지금 무엇을 계산하는가"는 이 문서에 쓰지 않았다.

표기: **폐기** = v2 출력에 근거가 없어 지표 자체가 의미가 없다. **대체** = 같은 목적을 v2 필드로 다시 정의한다. **유지** = 이름과 뜻이 그대로 통한다. **신설** = v2에서 새로 필요하다. **[학습 담당 확인]** = 정의·분모·허용 오차를 학습 담당이 정해야 한다(헤드가 정할 수 없다).

## 1. v2 출력이 바꾼 것 (지표 정의의 근거)

- LoRA-A 출력은 `values[](key, value, precision, status, save)`, `action`(NEXT, REASK, CORRECT, CONFIRM, REDIRECT, HOLD, SKIP), `reason`, `targets`, `note`, `next_item`이다(`V2_DRAFT.md` 2.2). 정규화·절차·다음 문항을 모델이 한다(D74).
- 위험 신호와 의도 분류 필드가 없다. 직원 알림 입력원은 비어 있다(G01).
- LoRA-A 출력이 형식을 끝내 못 지키면 대체 출력이 아니라 503 `OUTPUT_INVALID`다(D75). 의미 규칙은 서비스가 `validate_extraction`(turn-engine)으로 사후 검증한다(D75).
- LoRA-B 출력은 JSON이 아니라 문자열(24~122자, 전수 확인)이고, 안내 문장(RISK_NOTICE 등 고정 문장)은 B가 쓰지 않는다. 고정 문장은 서비스가 쓴다(`survey-service/docs/boundary.md` G01·G12 절). B 입력은 `action`, `topic`, `known`, `ask`, `previous`, `current`, `hold`, `next`, `reason`, `note`, `user_utterance`다(`V2_DRAFT.md` 2.5).
- 제약 디코딩이 형식을 지키므로(D82, D83) 형식 통과율만으로는 변별력이 낮다. gpu-dev 실측에서 extract 48회가 모두 형식을 통과했다(OPEN_GAPS U04, 학습 안 된 모델). 의미 정확도를 따로 봐야 한다.

## 2. LORA_A 지표 (절 제목: `LORA_A 파서 (UtteranceParserOutput)` -> `LORA_A 추출·절차 (ActionExtraction)`)

| v1 지표 | 처분 | v2 제안 | 비고 |
|---|---|---|---|
| `risk_signal_recall` (SAFETY) | **폐기** | 대체 없음. 위험 신호 입력원이 정해지면(G01) 그 입력원 기준으로 **신설** | v2 A 출력에 위험 신호 필드가 없다. SAFETY 맨 위 지표가 빠지므로 승인 보고서의 SAFETY 구성은 담당자가 다시 정한다 **[학습 담당 확인]** |
| `risk_signal_false_alarm` (SAFETY) | **폐기** | 위와 같음 | 같은 이유 |
| `item_precision`, `item_recall` | **대체** | `value_precision`, `value_recall`: `values[]`의 (`key`, `value`, `status`) 일치 기준 | 항목 단위를 key로 둘지 (key, value)로 둘지 **[학습 담당 확인]**. 괄호 없는 술 키(`Q7_1.amount`)는 정답에 있으므로 key 일치는 문자열 일치 |
| `target_accuracy` | **대체** | `targets_match`: `targets`가 정답과 같은 비율 (REASK·CONFIRM·HOLD·SKIP 행만) | `targets`는 없을 때 키 자체가 없다(빈 배열 아님). 분모는 해당 action 행 |
| `value_exact_match` | **유지(뜻 변경)** | 모델이 정규화까지 하므로 "단위 환산 후" 문구 삭제. `precision`(exact/approximate/unspecified) 일치를 값과 같이 볼지 따로 볼지 **[학습 담당 확인]** | 범위 답의 저장값은 IO_SPEC 7장이 미정(`V2_DRAFT.md` 4장) |
| `intent_accuracy` | **폐기** | 아래 4개로 **대체** | v2에는 의도 분류가 없다 |
| (신설) `action_accuracy` | **신설** | `action` 7종 일치율 | 분리 기준 `ACTION`(아래 4절) |
| (신설) `reason_accuracy` | **신설** | `reason` 일치율 (reason이 있는 action 행만) | 새 reason 4종 포함(`V2_DRAFT.md` 3장) |
| (신설) `status_accuracy` | **신설** | `values[].status` 7종 일치율 | |
| (신설) `next_item_accuracy` | **신설** | `next_item` 일치율 | CONFIRM은 현재 문항이 아니라 충돌 대상 문항인 경우가 많다(333건 중 278건). 분모를 action별로 나눠 보고하기를 제안 |
| (신설) `semantic_violation_rate` | **신설** | `validate_extraction`이 위반을 낸 출력의 비율 (정답과의 일치가 아니라 규칙 자체의 위반) | **U11**. 아래 3절 |
| `schema_valid_raw` | **유지(뜻 좁힘)** | 출력 보호 전 `ActionExtraction` 스키마 통과율. 제약 디코딩 하에서는 100% 근처가 되므로 변별력이 낮다 | 제약 디코딩을 끄고 잰 값과 켜고 잰 값을 구분할지 **[학습 담당 확인]** |
| `protection_intervened` | **폐기(A)** | A는 대체 출력을 쓰지 않는다 | B에는 유지. A에서는 아래 `output_invalid_rate`가 대신한다 |
| `fallback_rate` | **폐기(A)** | 위와 같음 | `is_fallback`은 B의 개념이다 |
| (신설) `output_invalid_rate` | **신설** | 재시도 후에도 형식을 못 지켜 `OUTPUT_INVALID`가 된 비율, 그리고 재시도 횟수(`X-Openit-Attempts`) 분포 | D75, `model-runtime/docs/boundary.md`. 서빙 쪽 지표라 평가 백엔드가 같은 경로를 쓰는지 **[학습 담당 확인]** |

## 3. U11: A 출력 의미 위반율

OPEN_GAPS U11("A 출력의 의미 위반율 지표를 평가에 넣지 않았다")의 처분 제안이다.

- 정의(제안): `semantic_violation_rate = validate_extraction(input, output, flow)`가 위반을 하나 이상 낸 출력 수 / 전체 출력 수. 위반 코드별 비율도 `slice`로 낸다. 검사 내용은 `targets`가 `values` 키의 부분집합, `next_item` 규칙, 건너뛰기 순서, `save` 규칙(ANSWERED·CORRECTION일 때만 true), MISSING·UNCLEAR·UNKNOWN·REJECTED이면 value가 null이다(`migration-2.0.0.md` turn-engine 절, D75). `group`은 `SAFETY`가 아니라 `ACCURACY`(또는 새 그룹)를 제안한다. 정답과 비교하지 않으므로 정답이 틀린 데이터에도 영향을 받지 않는다.
- 왜 필요한가: 서비스는 위반을 한 번 재시도한 뒤 턴을 실패 신호로 처리한다(D75). 운영에서 실제로 턴이 실패하는 비율이 이 값에서 나온다.
- 기준 시험: 학습 데이터의 A 출력 전수(5,077행)가 위반 0이어야 한다(`migration-2.0.0.md`). 이 값이 0이 아니면 지표가 아니라 검증기나 데이터의 문제다.
- 막혀 있던 이유: OPEN_GAPS U11에는 "boundary 규칙과 충돌, 허락 필요"라고 적혀 있다. 어떤 규칙인지 이번에 다시 확인하지 못했다(`model-lab/docs/boundary.md`는 "평가에서 `validate_extraction`은 쓰지 않았다(제안만)"라고만 적는다). **[학습 담당 확인]**: 평가가 turn-engine을 의존해도 되는지(model-lab은 이미 turn-engine을 계보 기록용으로 의존), 평가 백엔드(transformers+peft)에서 위반 코드별 `slice`를 허용할지.
- 이 지표를 넣는 일은 `boundary-contracts`(METRICS.md)와 model-lab 평가 구현을 모두 건드린다. 헤드가 METRICS.md 쪽을 반영하고 model-lab에는 변경 요청을 낸다. 아직 요청을 내지 않았다.

## 4. 분리 기준(slice kind)

| v1 | 처분 | v2 제안 |
|---|---|---|
| `INTENT` | **폐기** | `ACTION`(NEXT, REASK, CORRECT, CONFIRM, REDIRECT, HOLD, SKIP, B는 START 포함)과 `REASON`으로 **대체** |
| `QUESTION_TYPE` | 유지 | 문항 유형 분류가 v2 문항 은행에도 있는지 확인하지 못했다 **[학습 담당 확인]** |
| `UNIT` | 유지 | 단위 코드가 `glass/bottle/can/cc`, `week/month/year` 등 영문 코드다(`V2_DRAFT.md` 2.4). 구현이 한글 단위를 가정했는지 확인하지 못함 |
| `RANGE` | 유지 | 범위 답의 저장값이 IO_SPEC 7장 미정이라 정답 정의가 바뀔 수 있다 |
| `NOISE`, `SCENARIO`, `QUESTION_SET`, `SEEN_UNSEEN`, `ALL` | 유지 | `SEEN_UNSEEN`은 D32대로. 학습 서버 데이터에 `noise_types`가 없다(`V2_DRAFT.md` 4장: v1 샘플 필드 중 뺐다) -> `NOISE`로 나누려면 데이터 쪽 필드가 필요하다 **[학습 담당 확인]** |

`EvaluationReport` 스키마에서 slice `kind`가 열거인지 자유 문자열인지는 읽지 못했다. 열거라면 `ACTION`·`REASON` 추가는 계약 MINOR가 된다.

## 5. LORA_B 지표 (절 제목: `LORA_B 생성기 (ResponseGeneratorOutput)` -> `LORA_B 응답 (ResponseText)`)

| v1 지표 | 처분 | v2 제안 | 비고 |
|---|---|---|---|
| `forbidden_expression_rate` (SAFETY) | **유지** | 그대로. 단 금지 표현 목록이 없다(D59, `architecture.md` 11절 12번에 "금지 표현률 지표는 만들지 않음"으로 남아 있음) -> 목록이 생기기 전에는 계산 불가(`n=0`) | 목록 소유자 **[학습 담당 확인]**, 환자 안전과 닿는 도메인 결정 |
| `risk_notice_verbatim_rate` (SAFETY) | **폐기** | 대체 없음 | B가 안내 문장을 쓰지 않는다. 고정 문장은 서비스가 쓴다. 서비스 쪽 고정 문장 사용 여부는 survey-service의 시험 몫 |
| `ungrounded_number_rate` (SAFETY) | **대체** | 재료(`known`, `ask`, `previous`, `current`, `hold`, `next.text`, `user_utterance`)에 없는 숫자를 말한 비율. 재료 목록을 v2 입력 키로 다시 정의 | G05(응답 숫자 검사를 v2에서 둘지)와 같은 결정이 필요하다 **[학습 담당 확인]**. `CONFLICT_WITH_PREVIOUS`의 `ask`에는 영문 괄호 문구가 그대로 들어 있다(`V2_DRAFT.md` 2.5) -> 숫자 추출 규칙 영향 |
| `slot_coverage` (ACCURACY) | **대체** | `material_coverage`: action별로 말해야 할 재료(NEXT면 `known`과 `next.text`, REASK면 `ask` 등)를 빠짐없이 말한 비율 | action별 필수 재료 표는 학습 데이터 규칙(IO_SPEC)이다 **[학습 담당 확인]**. 헤드는 그 표를 읽지 못했다 |
| `schema_valid_raw` | **유지(뜻 변경)** | B 출력은 JSON이 아니므로 "문자열이고 길이·형식 조건을 통과"로 정의 | 길이 범위는 데이터 24~122자(확인)이나 서빙 기준값은 아니다 **[학습 담당 확인]** |
| `protection_intervened`, `fallback_rate` | **유지** | `X-Openit-Outcome=fallback` 비율. action별 `slice`(ACTION)를 제안 | 대체 문장 문구(G04)는 잠정 |
| `length_p95_ms` | **유지** | 그대로(`unit=ms`) | 이름의 `length`가 길이로 읽히는 문제는 v1에도 있었다. 이름을 `latency_p95_ms`로 바꿀지는 담당자 몫 |
| (신설) `response_length_chars` | **신설(선택)** | 응답 글자 수의 분포(p50/p95) | 키오스크 음성 출력에 영향. 필요 여부 **[학습 담당 확인]** |
| (신설) START 응답 품질 | **신설(선택)** | `action=START` slice로 `forbidden_expression_rate` 등을 따로 | START는 B만 부르므로(D74) 별도 분리가 의미 있다. 데이터 110행 |

## 6. 공통 보조 지표

| 지표 | 처분 | 비고 |
|---|---|---|
| `coverage_seen_unseen_gap` | 유지 | |
| `regression_fixed`, `regression_broken` | 유지(입력 형식 변경) | `FailureCase.expected_kind`가 `LORA_A`/`LORA_B`이고 `reviewed_input`이 `ActionExtractionInput` 또는 `ResponseRequest`로 검증된다(`migration-2.0.0.md` ops-feedback 절). 회귀 평가가 읽는 TurnTrace 키 이름은 OPEN_GAPS D-E에서 미정 |
| (신설) `turn_failure_rate` | 신설(선택, 운영 지표) | 재시도 뒤에도 `turn_failure_signal`로 끝난 턴 비율. 평가보다 ops-feedback 탐지 규칙에 가깝다 |

## 7. 반영 순서 제안

1. 담당자와 [학습 담당 확인] 항목을 한 번에 확인한다(각 표의 비고 열에 표시했다).
2. 헤드가 `boundary-contracts`에서 METRICS.md를 고친다(절 제목, 폐기 지표 제거 또는 "v1 전용" 표시, 신설 지표 추가, 분리 기준). 계약 스키마는 바뀌지 않으므로 PATCH 또는 문서 변경이다. `verify.py` 통과를 확인한다.
3. model-lab에 평가 구현 변경 요청을 낸다(헤드는 model-lab 코드를 고치지 않는다). U11 지표와 `OUTPUT_INVALID` 지표가 가장 우선이다.
4. 그 전까지 `OPEN_GAPS.md` D-C는 `부분`(이 제안서까지만 끝)으로 둔다.
