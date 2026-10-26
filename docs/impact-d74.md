# D74 영향 목록: 서비스 구조를 학습 데이터셋 v2에 맞춘다

상태: 초안(2026-10-27). 구현 지시가 아니다. 각 항목은 헤드가 변경 지시를 낼 때 확정한다.
표기: **확인**은 리포나 서버에서 읽은 것, **제안**은 헤드 제안, **미정**은 근거가 없는 것.

## 1. 기준

- 기준 데이터: 학습 서버 `~/taehyeon/data/dataset_10_14`(LoRA-A 3,982/549/546건, LoRA-B 4,069/560/558건), 형식 문서 `~/WS/dataset/docs/IO_SPEC.md`(v2, 2026-10-13 확정). 서버는 탐색만 했다(읽기 전용).
- LoRA-A 입력(확인): `question_id`, `current_question`, `user_utterance`, `state`. 출력(확인): `values[{key,value,precision,status,save}]`, `action`, `reason`, `targets`, `note`, `next_item`. 시스템 프롬프트는 데이터 안에 있다.
- LoRA-B 입력(확인): `action`, `reason`, `user_utterance`, `known`, `ask`, `previous`, `topic`, `current`, `hold`, `next{type,text,question_id}`. 출력은 응답 문장 텍스트 그대로(JSON 아님).
- 이 두 형식은 고정이다. 서비스가 맞춘다(D74).
- 학습 설정(확인): Qwen3-4B/8B/14B, rank 16, alpha 16, 모든 선형층, `enable_thinking=False`.

## 2. 구조 변화

v1: 파서 → 정규화기 → 판정기 → 기록기 → Plan(코드) → 생성기
v2: 시작: 서비스 → B(START). 발화: A(추출·정규화·절차·다음 문항) → 서비스(표 찾기, 저장) → B

서비스에 남는 일(제안): 세션 상태 저장, 문항 은행 조회(질문 문장, 칸 설명, 문장 틀), A 출력 검증과 저장 규칙 적용, B 입력 조립, 직원 알림, Trace, 릴리스 적재. 판단(정규화·절차·다음 문항)은 하지 않는다.

## 3. 영역별 영향

| 영역 | 영향 | 근거 | 수준 |
|---|---|---|---|
| boundary-contracts | 파서 출력·생성기 입력 스키마(`ParserSample`, `GeneratorSample`)와 I9 입출력, golden, Trace 키(`normalizer_*`, `judge_*`, `planner_*`)를 v2 형식으로 바꾸는 MAJOR 후보. 상세 스키마는 데이터셋의 형식을 그대로 옮긴다 | 현재 스키마 24개 중 위 둘이 v1 형식(확인: `schemas/`) | 제안 |
| turn-engine | `normalizer.py`, `judge.py`, `writer.py`, `planner.py`가 서비스에서 쓰이지 않게 된다. 남는 것은 A 출력 검증·저장 규칙(`save`, `precision`, 건너뛰기 검산)일 수 있다 | `survey-service/ports.py:43`가 네 함수를 직접 연결(확인) | 제안 |
| survey-service | LangGraph 노드 재구성(`graph.py`: parser/normalizer/judge/record/plan 노드 제거 또는 통합), `assembly.py`(B 입력 조립: `known`, `ask`, `previous`, `next.text`), 시작 경로(A를 부르지 않고 B만), 문항 은행 조회, 문진 스키마(`schema/`)에 칸 설명표와 `ask` 문장 틀 표 추가 | `graph.py:28-31` Trace 키(확인) | 제안 |
| model-runtime | 프롬프트(`prompts.py`)를 데이터에 박힌 시스템 프롬프트로 대체, `enable_thinking=False` 전달, A는 JSON 출력·B는 텍스트 출력, 프로파일을 Qwen3 기준으로 추가 | 학습 설정(확인) | 제안 |
| synthetic-data / model-lab | 데이터셋과 학습 산출물이 이미 v2다. 이 두 리포가 학습 서버 코드와 어떻게 이어지는지는 확인하지 못했다 | 두 리포 마지막 커밋 10-15(확인) | 미정 |
| release-gate / ops-feedback | 모델 패키지 매니페스트(기반 모델, A·B 어댑터 두 개)와 평가 보고서 항목, 실패 사례의 단계 정보가 v2 용어로 바뀔 수 있다 | 미확인 | 미정 |
| deploy | 프로파일별 GPU 이미지·캐시, 두 어댑터 동시 적재 설정, 데모 패키지 생성(`make-llm-package.sh`)을 Qwen3 어댑터 기준으로 | D72 | 제안 |
| kiosk-frontend / admin-console | 공개 API(PUBLIC_API.md)가 유지되면 영향 없음 | 미확인 | 제안 |

## 4. 모델 호환(제안)

- 기반 모델은 프로파일로 선택한다. 어댑터가 학습된 기반 모델과 프로파일의 기반 모델이 같아야 한다(패키지 매니페스트에 기반 모델을 기록하고 적재 시 검사하는 것을 제안).
- `gpu-12g`: Qwen3-4B(A·B 모두 4B 어댑터가 서버에 있음, 확인). 12GB 적재 가능 여부는 **미확인**(4B bf16 가중치 약 8GB 추정).
- 24GB급: Qwen3-8B(A 정확도가 가장 높고 B 8B 체크포인트가 있음, 확인). 적재 가능 여부는 미확인.
- 14B: A만 학습됨(확인). 단독 서빙 요건은 미확인.
- 한 기반 모델에 A·B 어댑터를 동시에 올려야 한다(멀티 LoRA). A와 B의 기반이 같은 쌍(4B+4B, 8B+8B)만 쓴다.

## 5. 순서(제안)

1. 형식 확정: 데이터셋 v2의 A·B 입출력을 `boundary-contracts`의 새 스키마와 예시로 옮긴다(헤드). 학습 서버 데이터의 실제 샘플로 검증한다.
2. 문진 스키마에 칸 설명표·`ask` 문장 틀 표 추가(survey-service, 데이터셋 쪽 담당과 맞춤. IO_SPEC 7장에서 미정).
3. model-runtime: 새 형식의 파서·생성 호출, Qwen3 프로파일.
4. survey-service: 그래프 재구성.
5. turn-engine 축소 또는 제거.
6. deploy: 새 구성으로 E2E와 실제 LLM 데모, Qwen3 어댑터로 LoRA 교체 시험.

## 6. 먼저 풀어야 할 미정

- 정규화 쪽 학습 코드를 다른 담당자가 수정 중이다(`~/WS/AGENTS.md`). 확정 시점을 모른다.
- `ask` 문장 틀 표, 범위 답 저장값(IO_SPEC 7장).
- 일부 칸이 정해진 다음 문항에서 `next.text`가 이미 받은 내용을 다시 묻는 문제(데이터셋 작업 기록, 57건 중 20건 이상). 계약 수정이 필요하다고 적혀 있다.
- LoRA-B 시험에서 START 12건이 모두 문장 수 위반으로 집계됨(`~/myungchan/eval_b_8b.log`, 확인). 원인은 미확인.
- 어댑터와 기반 모델의 12GB 적재, 두 어댑터 동시 적재.
