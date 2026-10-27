# 빈 곳과 미확인 대장 (OPEN_GAPS)

목적: 일부러 비워 두었거나 확인하지 못한 것을 한곳에 모아, **빈 채로 완성이라고 판단하지 않게 한다.** 헤드는 "완료"를 말하기 전에 이 파일에서 열린 항목이 해당 범위에 남아 있지 않은지 확인하고, 남아 있으면 완료가 아니라 "N건 열림"이라고 말한다. 새로 비워 두는 것이 생기면 같은 날 여기에 추가한다. 닫을 때는 지우지 않고 상태를 `닫힘`으로 바꾸고 근거(커밋·시험·결정 번호)를 적는다.

상태: `열림`(아직 안 함) / `부분`(일부만) / `닫힘` / `보류`(사용자가 미루기로 함).
종류: `빈 곳`(일부러 비움) / `미확인`(해 보지 않음) / `미정`(결정 필요).

## 1. 빈 곳 (일부러 비워 둠)

| ID | 내용 | 영역 | 상태 | 비고 |
|---|---|---|---|---|
| G01 | **직원 알림의 입력원이 없다.** v1은 파서의 위험 신호에서 StaffAlert를 만들었는데 v2 LoRA-A 출력에는 위험 신호 필드가 없다. 알림 경로는 코드를 유지하되 입력원이 없으면 **비활성**이며 `/readyz`와 문서에 명시한다(조용히 끄지 않는다) | survey-service | 부분 | **포트 문서화·시험됨, 입력원 미정.** `RiskSource` 포트(`SURVEY_RISK_SOURCE`)와 가짜 입력원 시험이 있다(survey-service 1cfc463, `survey-service/docs/boundary.md` 4절). 입력원은 없고 `/readyz`의 `staff_alert_source.active=false`다. 환자 안전과 닿는다. 입력원을 정하기 전에는 "직원 알림이 동작한다"고 말하지 않는다. 사용자 결정 대기. 사용자 지시(2026-10-27): 일단 빈 채로 만든다 |
| G02 | **2026-10-27 방향 결정: 데이터셋 담당의 최종 데이터를 가져와 검증·게시한다(재생성 안 함).** 게시기(import) 모드를 구현했다(synthetic-data 4dcb94a, e5ce2c9; 가짜 입력 시험만, 실제 데이터 게시 안 함, 행 형식은 추정, v2 의미 검사 없음, CR-006). E2E 단계 2는 아직 v1 생성기를 기준으로 BLOCKED다. 이전 서술: synthetic-data의 생성 파이프라인이 v1 내용을 만든다(15개 시험을 건너뜀). 지금 잡을 돌리면 합성 샘플이 전부 걸러지고 시드만 남은 데이터셋이 게시될 수 있다. 운영에서는 돌리지 않는다 | synthetic-data | 부분 | **2026-10-28 실제 C1 파일 6개(64,459행)로 게시기를 실행했다(synthetic-data 903434d): 행 형식 추정이 맞았고 스키마 검증 64,459/64,459 통과, human_review 모두 auto_only, 개인정보 의심 0행, 게시와 멱등 재실행 확인.** 평가 누수 판정 키를 '정규화 발화+입력 전부'로 정했다(발화·문항만 같고 state가 다른 8건은 입력도 정답도 달라 누수가 아님). 허용치 0의 근거는 C1에서 0이었다는 한 번의 측정. **미확인**: 의미 검사(targets, next_item 등)와 비식별 확인은 하지 않음(`semantic_checks.performed=false`, `deid_attested=false`), 문항 세트 출처는 자리 표시(CR-006), 운영 저장소 게시 안 함, C1 외 빌드, **데이터셋 담당의 사용 허락 확인 필요**. E2E 단계 2는 시험용 소형 데이터로 배선만 확인(deploy bec4271) | **E2E 사실(2026-10-27)**: 단계 2에서 합성 샘플 6,066건이 모두 v2 스키마 위반으로 제외되어 데이터셋이 게시되지 않는다(NOTHING_TO_DO).
| G03 | B 입력의 `topic`·`known`·`ask`·`previous`·`current`·`hold` 표는 데이터셋 담당의 `labels.py`(학습 서버 `~/WS/dataset/scripts/labels.py`, 2026-10-14)를 옮겨 쓴다. 학습 데이터 B 입력 5,077행에서 `next.text`를 뺀 필드가 글자 단위로 같다(survey-service 보고). **표 승인 기록은 찾지 못했다**(IO_SPEC 7장 2번은 아직 '미정') | survey-service | 부분 | 데이터셋 담당이 `labels.py` 규칙을 B 입력의 기준으로 확정하는지 확인 · **2026-10-28 C1 빌드 전체(B 32,289행)로 재대조: `next` 제외 B 입력이 글자 단위로 32,289/32,289(100%) 일치(survey-service b9ba3d8). `labels.py`는 10-14 그대로(sha256 64e8c959…)**. 승인 기록은 여전히 못 찾음 |
| G04 | respond 대체 문장: 재료가 하나도 없을 때의 문구("죄송합니다. 다시 한 번 말씀해 주세요.")는 잠정이다. 환자에게 가는 문구 | model-runtime | 열림 | 도메인 소유자 확인 |
| G05 | v1의 G1(응답 숫자가 입력 재료에 있는지 검사)에 해당하는 검사를 v2에서 둘지 정하지 않았다 | model-runtime | 열림 | |
| G06 | model-lab 학습기(`trainers/hf.py`)는 학습 서버의 코드와 달라 같은 어댑터를 만들 수 없다. 학습 정본은 서버 코드(D78). 비전문가도 쓸 수 있는 학습 실행(설정 + 한 명령 + doctor)으로 서버 코드를 감싸는 수정이 필요하다 | model-lab | 열림 | 사용자 지시(2026-10-27): 서버 코드를 정본으로 보고, 대상이 비전문가이므로 이후 수정 필요 · **2026-10-27 서버에서 읽음(읽기 전용)**: `train_lora_a.py`·`train_lora_b.py`의 인자는 `--data_dir --prefix --model --out_dir --max_len --epochs --lr --batch --accum --rank --alpha --dropout --eval_steps --seed --dry_run`이다. 각 run의 `run_config.json`이 값을 남긴다. `arg_map`에는 model-lab 6fa4e96에서 반영했다(`args_verified: true`는 서버 코드를 읽은 것이고 `--help` 실행은 하지 않았다). 설정 `configs/train.yaml`(A 8B), `configs/train-b.yaml`(B 8B). **남은 것**: `--help` 확인, 출력 폴더 위치 확인, 실제 실행(H3) |
| G07 | turn-engine의 `normalize`, `judge`, `write_record`, `plan`은 폐기 표시만 했고 제거하지 않았다(survey-service 이전 뒤 제거) | turn-engine | 닫힘 | 근거: turn-engine 23973fc / 태그 v0.4.0이 `normalize`, `judge`, `write_record`, `plan`, `OutputContractError`를 제거했다(`turn-engine/docs/boundary.md` 2절). survey-service는 v0.4.0 기준(6241d00) |
| G08 | release-gate의 기본 태그를 turn-engine v0.3.0, model-runtime v0.6.1로 올림 | release-gate | 닫힘 | 시험 209 통과, 스모크 통과, release-gate 7139123 |
| G10 | `prompt-3`(JCS)은 폐기 예정으로 남겼다. 제거 시점은 다음 MINOR로 제안 | model-runtime | 닫힘 | 근거: model-runtime 8279847 / 태그 v0.7.0이 `prompt-3`을 제거했다(`model-runtime/docs/boundary.md` 호출자 절, CHANGELOG 0.7.0). `prompt-3` `serving_config`는 `UnsupportedServingConfig`로 거부된다. 이전 계열로 만든 릴리스는 거부된다(깨지는 변경으로 기록됨) |
| G11 | 문진 스키마 정수 버전 1 안에서 비호환 변경이 있었다(`SessionStore`, `TurnTrace`, v1 모델 입출력 계약 12개 삭제). survey-service와 ops-feedback은 반드시 같은 잠금으로 함께 배포해야 한다 | survey-service, ops-feedback | 열림 | D79. 운영 데이터가 생기기 전에 TurnTrace 별도 버전 필드 검토 |
| G12 | v2에서는 A가 REASK/CONFIRM을 계속 내도 서비스가 끊지 않는다(v1의 반복 물음 상한·못 알아들음 상한은 사라짐). 환자가 같은 질문을 무한히 받을 수 있다 | survey-service | 부분 | **메커니즘 구현됨, 값·의미는 사용자 결정 대기.** `SURVEY_MAX_CONSECUTIVE_REASK`(기본 0=끔)를 켜면 상한을 넘는 REASK·CONFIRM 대신 기존 직원 호출 경로(정지 `PAUSED_RISK`, `CALL_STAFF` 알림)를 쓴다(survey-service 5705632, `survey-service/docs/boundary.md` 4절). 정할 것: 값 N, 의미(N번 되묻고 N+1번째에 직원을 부른다), 정지 이름 `PAUSED_RISK` 재사용 여부. 기본이 꺼짐이라 지금은 환자가 같은 질문을 무한히 받을 수 있다. CR-012 |
| G13 | 표는 `DATASET_RULES_UNCONFIRMED`(데이터셋 담당 규칙을 옮김, 승인 기록 미확인; G03). 57행 문제 처리용 새 `next.text`(남은 칸만 묻기)는 학습 분포에 없어 B 모델이 어떻게 다루는지 확인하지 못했다. A 입력 state의 묶음 순서는 서버 val 549행 중 536행(97.6%)이 서비스 규칙과 글자 단위로 같고 13행이 다르다. 원인(확인, `prev_state.py`): 학습 데이터는 원래 시나리오 state에 있던 값이 먼저, 그 뒤에 흐름 생성기가 더한 직전·참조 문항이 오는 구조라 "직전이 먼저"라는 단일 규칙이 아니다. 서비스는 이 시나리오 정보를 모르므로 완전히 재현할 수 없다. 영향은 드문 키 순서 차이이며 성능 영향은 미측정. B 입력은 `next.text`만 다르다(데이터는 같은 문항도 문장이 제각각, 서비스는 문항 은행 문장) | survey-service | 열림 | 서버 val 대조(in-sample) · **2026-10-28 C1 전체로 재측정(survey-service b9ba3d8): A 입력 state 일치 31,411/32,170(97.64%), 불일치 759행은 모두 칸 집합·값이 같고 순서만 다름(문항 묶음 순서 623, 칸 순서 136). 순서 차이가 모델 출력에 영향을 주는지는 GPU에서만 확인 가능. 값 검증이 정상 정답을 거부한 2행(OUT_OF_CURRENT_ITEM, 규칙이 과했음)은 규칙을 고쳐 0행. 칸 값 형식 규칙(선택지·단위·예/아니오)은 실제 문항 세트(칸 정의 포함)가 없어 시험용 세트로만 확인** |
| G14 | ops-feedback 탐지 규칙 `REASK_STREAK`(연속 REASK)은 임계값이 자리표시자(예시 설정 `enabled:false`, threshold 3)다. `EXTRACT_FAILED`가 값 없는 HOLD·SKIP을 실패로 볼지, `extract_protections` 건수를 비식별에서 남길지도 미정 | ops-feedback | 열림 | G12(반복 물음 상한)와 함께 사용자가 정한다 |
| G09 | `tests/golden/`(model-runtime, model-lab)은 v1 정적 예시라 시험이 쓰지 않는다. 삭제 여부 미정 | model-lab, model-runtime | 닫힘 | 근거: model-runtime 8279847(v0.7.0)이 `tests/golden/`(정적 예시 216개)와 `prompt-3` 골든 2개를 제거했고 어떤 시험·스크립트도 읽지 않는 것을 grep으로 확인했다(CHANGELOG 0.7.0). **model-lab 쪽 `tests/golden/`은 이번에 읽지 못해 제거 여부를 확인하지 못했다.** 남아 있으면 model-lab 세션이 처리한다 | **정정(헤드 확인 2026-10-27)**: model-lab `tests/golden/`은 git에 210개가 남아 있다. 사용처 확인 후 제거하는 일이 남았다. **닫힘 근거(2026-10-27)**: model-lab b1f57e3가 `tests/golden/` 210개를 제거(읽는 곳 없음 grep, pytest 150 통과, 스모크 통과).

## 2. 미확인 (해 보지 않음)

| ID | 내용 | 상태 | 비고 |
|---|---|---|---|
| U01 | gpu-dev(12GB)에서 Qwen3-1.7B(`gpu-12g`, D81) 적재와 중립 A·B 어댑터 동시 적재. **2026-10-27 확인(gpu-dev 1회)**: `/readyz` 200, 컨테이너 시작부터 적재 완료 약 2분 30초(모델 다운로드 60.8초 포함), `nvidia-smi` 약 10.1GB 사용(적재 직후 10,093MiB, 요청 중 최대 10,141MiB), KV 캐시 5.42GiB/50,720토큰. A·B 동시 적재는 B respond 200, A extract 생성까지 간 것으로 간접 확인(어댑터 로드 성공 로그 줄은 못 찾음). **남은 것**: 동시 요청 부하, 장시간 안정성 | 부분 | 프로파일 값은 아직 추정으로 두고 model-runtime이 측정값 반영 여부 판단 |
| U13 | 학습된 어댑터(Qwen3-4B/8B)의 실제 서빙·평가는 24GB급 GPU 서버가 필요하다. 아직 그런 서버에서 해 보지 않았다 | 열림 | D81. 사용자의 4090 서빙 서버 사용 시점 미정 |
| U14 | (보류, 요구 아님) 제약 디코딩이 `values[].key`를 현재 문항의 유효 칸 집합으로 제한하지 못한다. 모델 입력 형식은 학습 데이터로 고정(D74)이라 입력에 칸 목록을 넣을 수 없다. 하려면 프롬프트가 아니라 서빙 API의 별도 매개변수로 문법에만 쓰는 방식인데, 학습된 LoRA-A는 키를 학습했고 서비스가 사후 검증으로 막으므로 학습 안 된 모델로 데모를 통과시키려는 목적 외에는 필요 없다 | 보류 | 필요해지면 그때 | 
| U15 | model-runtime `pyproject`의 dev extra가 turn-engine v0.3.0(boundary v2.0.0 고정)을 가리킨다. `model-runtime[dev]`로 설치하면 boundary v2.0.1과 충돌. 서비스 이미지·lock 해결에는 영향 없음(model-lab에서 확인). 다음 model-runtime 릴리스(D80 연쇄 때문에 단독 릴리스 안 함)에서 v0.3.1로 고친다 | 닫힘 | 근거: model-runtime 8279847(v0.7.0)이 dev extra의 turn-engine 하드 핀을 없앴다. turn-engine이 필요한 시험은 `importorskip`으로 없으면 건너뛴다(CHANGELOG 0.7.0) |
| U16 | E2E의 가짜 모델은 A 출력을 `values` 빈 NEXT로만 내서, 환자 말에서 값을 뽑아 저장하는 경로(검증 → 저장 → 응답 재료 조립)가 E2E에서 한 번도 실행되지 않는다. 영역 단위 시험(survey-service 415)에는 있을 수 있으나 이 세션에서 E2E 수준으로는 확인하지 못했다. 가짜 A가 문항별로 값을 내도록 확장해 저장·정정·건너뛰기를 E2E에서 확인해야 한다 | 부분 | model-runtime 가짜 백엔드(`MODEL_RUNTIME_FAKE_FLOW_FILE` 확장) + deploy E2E 단계. 다음 model-runtime 릴리스에 묶는다 | **정정(2026-10-27)**: 영역 단위로는 survey-service `tests/test_orchestrator.py::test_full_conversation`이 값 저장·다음 문항·B 입력 조립을 지난다(확인). 빠진 것은 영역 사이(E2E)다. model-runtime v0.7.1에서 가짜 A가 값을 내도록 확장했고, deploy E2E 단계 추가가 남았다. **진행(2026-10-27 16:18)**: model-runtime v0.7.1 가짜 A가 `slots`/`skips`로 값을 내고, deploy E2E 단계 5g(직접 6건 + 서비스 경유 값 있는 3턴)와 5s(릴리스 교체 전후 컨테이너 불변)를 REAL로 추가, 전체 모드 통과(deploy 4720f02, 통과 수는 최신 결과: [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md)). **남은 것**: 저장된 값 자체를 읽는 공개 경로는 없다. **정정(2026-10-27 22:45)**: 직원 세션 조회(`GET /v1/staff/sessions/{id}`)가 turns[].action과 values[]를 읽기 전용으로 주므로 그것으로 값과 status를 직접 단언했다. 정정(CORRECT)은 model-runtime v0.7.2 가짜 A(`corrections`)와 deploy E2E 단계 5c에서 전체 모드 REAL로 확인했다. 못 보는 것: 이력의 이전 값, 정정 뒤 다음 문항, 모델이 실제 정정 표현을 알아듣는지.
| U02 | 24GB(RTX 4090)에서 Qwen3-8B 적재, 실측 | 열림 | |
| U03 | 서빙 프롬프트와 학습 데이터의 글자 일치. **2026-10-28 최종 학습 데이터 C1 전체(A 32,170행·B 32,289행; val/test/train)로 서빙 v0.7.3의 prompt-4 `render_prompt`를 대조했다: system+user가 글자 단위로 100% 재현(A 32,170/32,170, B 32,289/32,289).** 시스템 프롬프트는 역할마다 1종(A `sha256:53bc60fd…50bd`, B `sha256:9a9eee95…c804372b`). 정답(assistant)은 사후 검증기와 relax-3 제약 스키마를 100% 통과하고 A의 키 순서도 계약과 같다. user 최대 길이 A 643자·B 417자로 입력 상한 2500자를 넘는 행이 없다. **미확인**: 서빙 번들의 시스템 프롬프트와의 해시 일치(번들 파일 필요, GPU 세션 키트가 번들을 만들 때 확인), 실제 xgrammar 컴파일, 토큰 수 기준 길이, `apply_chat_template` 토큰 ID 대조, assistant 쪽 `<think>` 처리. 재현: `MODEL_RUNTIME_REFERENCE_DATA_DIR=<…/data/final> python scripts/check_reference_data.py`(model-runtime 12b0cb3) | 부분 | D77 |
| U04 | vLLM 제약 디코딩(xgrammar)이 `ActionExtraction`의 규칙을 어디까지 지키는지. **2026-10-27 gpu-dev, model-runtime v0.6.5(relax-3) + 계약 v2.0.1**: 변형 8개 `anyOf` 문법을 경고·에러 없이 받았고 extract 48회(키오스크 28 + 직접 20) 모두 형식 통과, OUTPUT_INVALID 0건. (이전 v0.6.3: 100%, v0.6.4: pattern 0건이나 의미 규칙 위반 31건.) **남은 것**: 문법 컴파일 비용은 분리해 재지 못함(첫 호출 비교가 오염됨), `minItems`·`maxItems` 강제 여부는 xgrammar 단독 시험 외 실측 없음 | 부분 | D82, D83 |
| U05 | 실제 브라우저 화면, 한국어 음성 인식(STT), 웹 푸시 수신 | 열림 | 키오스크 프런트 |
| U06 | 일반 Linux 서버에서의 설치(지금은 WSL2 + Docker Desktop 두 환경) | 열림 | |
| U07 | 새 구조(v2)의 **실제 LLM** 데모(Qwen3, GPU). 가짜 모델 E2E 통과 수는 정본을 따른다(최신 결과: [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md)). **gpu-dev 실제 LLM(2026-10-27, v0.6.5)**: 기동 166초(엔진 준비 약 80초), 시작 응답 정상, extract 형식 통과 100%. **그러나 키오스크 발화 14턴 모두 실패**: 학습 안 된 1.7B가 문항 세트에 없는 slot key(`Q1.D01.akan` 등)를 지어내서 survey-service `UNKNOWN_SLOT` 검증(D75)에서 걸리고 `turn_failure_signal`(NOT_COMMITTED)로 끝남. 의도대로의 동작(값을 지어내지 않음)이며 모델 내용 문제라 학습된 LoRA-A가 와야 한 턴이 통과할 것으로 추정(미확인). 건너뜀: 단계 2(G02), 직원 알림 화면(G01), 브라우저·STT·푸시(U05). **2026-10-27 19:50~20:06 gpu-dev 재검증(deploy 80b0d68, v0.7.1)**: `demo.sh up --llm --yes-large` 성공(약 12분, GPU 10,094/12,282MiB), 비밀 노출 점검 통과(비밀 값 62개), `probe-serving --demo --repeat 3`에서 30건 모두 형식 통과(OUTPUT_INVALID 0, 첫 호출 2.16초, 이후 중앙값 1.70초). 형식 통과일 뿐 값의 정확성은 보지 않았다(학습 안 된 1.7B). 학습된 어댑터로 한 턴은 여전히 미확인 | 부분 | 모델 정확성은 학습 쪽 몫(사용자 정리 대기). 학습 없이 한 턴을 통과시키려면 key를 현재 문항의 유효 slot enum으로 제약해야 하나 계약 변경이 필요(U14) |
| U08 | LoRA 교체 시험: 같은 기반 모델의 두 번째 어댑터로 model-serving만 바꿔 나머지가 그대로 동작하는지(D72) | 부분 | | **진행(2026-10-27)**: `deploy`에 `demo.sh swap-adapters`를 만들어 가짜 백엔드 데모에서 실제로 돌렸다(교체 후 model-serving을 포함한 7개 컨테이너의 StartedAt 불변, 새 release_id LOADED, 기반 모델 불일치 어댑터는 거부되고 활성 릴리스 그대로; deploy 3a4d688). **진행(2026-10-27 gpu-dev, `--llm`)**: `swap-adapters`로 새 릴리스가 9.9초에 LOADED, 컨테이너 11개 변화 0건, 교체 후 비밀 점검 통과. 승인자는 스크립트(TEST-SUB)이고 어댑터는 시험용(`~/swap-test`)이다. **남은 것**: 학습된 진짜 어댑터로의 교체(H2), 사람 승인 흐름.
| U09 | 정규화 쪽을 다른 담당자가 수정 중이다(`~/WS/AGENTS.md`). 확정 시점과 범위 모름 | 열림 | 학습 서버 쪽 |
| U10 | 평가가 가짜 모델로만 돌았다. 실제 모델 평가 값 없음 | 열림 | |
| U11 | A 출력의 의미 위반율 지표(`validate_extraction` 기반)를 평가에 넣지 않았다 | 열림 | boundary 규칙과 충돌, 허락 필요. 지표 정의와 처분 제안은 `metrics-v2-proposal.md` 3절(학습 담당 확인 필요) |
| U12 | 두 번째 독립 머신에서의 영역 시험 확인(영역별 "같은 PC의 새 venv"까지만) | 열림 | gpu-dev 정적 점검 SKIP 2건의 원인은 영역 `.venv`·`node_modules` 부재로 확인(deploy ea08203, SETUP F절). gpu-dev에서 SKIP 0이 되는지는 확인 안 함 |
| U17 | PostgreSQL 컨테이너 재시작 시 서비스 복구: 단계 5p(전체 모드 REAL, 이 PC)에서 4개 서비스가 `/readyz` 503 후 7초 안에 200, 행 지문 보존. survey-service는 처음 `/readyz`가 37초 뒤 연결 끊김이라 고쳤다(survey-service d8f4243·4d78b3e, CR-D23). **남은 것**: 주 연결이 응답 없는 DB에 걸리면 턴 처리가 최대 10초 기다림(결정 필요), 서비스 컨테이너 자체의 재시작 시험 없음, gpu-dev에서는 안 돌림 | 부분 | |

## 3. 미정 (결정 필요)

| ID | 내용 | 결정자 | 상태 |
|---|---|---|---|
| D-A | 운영 도메인·HTTPS, 직원 콘솔 로그인, CI가 서버 레지스트리에 닿는 방법, 토큰 발급·회전, 원본 보관 기간 | 사용자 | 열림 |
| D-B | 원문 정규화 담당자의 변경이 계약에 미치는 영향 | 사용자 확인 후 헤드 | 열림 |
| D-C | `METRICS.md`의 v1 지표(`risk_signal_*`, `intent_accuracy`)를 v2 용어로 바꾸는 일 | 헤드 + 학습 담당 | 부분 (근거: `metrics-v2-proposal.md`가 폐기·대체·신설 목록을 정리했다. `METRICS.md` 본문은 아직 v1이고 학습 담당 확인 뒤 반영) |
| D-D | 데이터셋 담당에게 보내는 정리 요청(`dataset-requests.md`) | 사용자 전달 | 보류(구조 완성 뒤) |
| D-E | 회귀 평가가 읽는 v2 TurnTrace 입력 키 이름(`extract_input` 등은 추정) | survey-service 확정 후 | 열림 |
| D-F | turn-engine CR-010: QuestionBank에서 `QuestionFlowTable`을 만드는 변환 함수를 더할지, `docs/rules/` 삭제 여부 | 헤드 | 열림 |
| D-G | I2(DatasetStore)를 HTTP로 정할지(경로, 클라이언트, 참조 서버). 지금은 SDK 프로토콜과 INTERFACES.md뿐 | 헤드 | 열림 |
| D-H | admin-console CR-003: 생성된 검증기(`generated/contract-validators.cjs`)를 커밋 대상으로 둘지 | 헤드 | 열림 |
| D-I | **문진 결과(저장된 답)가 병원으로 나가는 경로**가 정의되어 있지 않은 것으로 보인다. `boundary-contracts/PUBLIC_API.md`와 `INTERFACES.md`, `survey-service/docs/boundary.md`에서 저장 값을 내보내거나 조회하는 인터페이스를 찾지 못했다(이 세 문서만 grep, 다른 문서·코드는 읽지 않음). 의도적으로 범위 밖이면 그렇다고 결정에 적고, 아니면 인터페이스가 필요하다 | 사용자(제품 범위) | 열림 |

## 3-0. 알려진 한계와 사람 몫 (2026-10-28 전수 점검 후, 이유 포함)

전수 점검(`AUDIT_SUMMARY.md`)과 D88의 표준 적용 뒤 남긴 것이다. 코드로 닫지 않은 이유를 함께 적는다. 값은 모두 잠정이고 설정으로 바꾼다.

| ID | 내용 | 이유 / 담당 |
|---|---|---|
| L01 | secrets/ 백업과 복호 키 보관(분실 시 가명화 salt·계정 복구 불가) | 키 관리는 서버 밖 사람 일. 구조는 `backup-secrets.sh`(갈래 B) |
| L02 | 컨테이너가 읽는 비밀 파일이 644(폴더 700 안). Compose 파일 secrets의 uid/mode가 이 Docker/Compose 버전에서 적용되지 않음 | 그룹 읽기(640)+`group_add` 대안 검토 중(갈래 B) |
| L03 | gateway 로그인 시도 속도 제한 없음 | Caddy 플러그인이 필요해 커스텀 이미지 빌드라는 새 위험. 대안(네트워크 제한, 강한 암호, 실패 로그 감시)을 runbook에 |
| L04 | 취약점 스캔·SBOM 없음 | 외부 도구 설치·전송 금지 제약. '확인 못 함' |
| L05 | 서비스 간 내부 TLS 없음 | 컴포즈 내부 네트워크 한정. ADR에 범위와 위험 |
| L06 | 저장 시 DB 암호화 없음 | 볼륨 암호화는 호스트 계층. 요구·권고만 문서화 |
| L07 | 위조 Trace가 롤백 요청을 만들 수 있음(S5) | 방어는 호출자별 토큰·서명이 필요(ops-feedback CR-006). `auto_submit` 기본 false로 사람이 마지막 관문 |
| L08 | OPS_DB_SCHEMA=verify + migrate 분리, DB 계정 분리 | 계정 설계와 E2E 영향이 커서 이번 라운드에서 제외 |
| L09 | 모든 timeout·상한·한도·자원 값이 측정 없는 잠정값(6초 턴 마감, 3.5초 모델 상한, 소켓 15/30초, 연결 상한 등) | H1(24GB 실측) 뒤 재정. GPU 세션 키트 준비됨 |
| L10 | STT를 기기 안 처리로 둠. 실기기에서 온디바이스 한국어 인식이 되는지 미확인 | 실기기 필요. 안 되면 글자 입력으로 대체됨 |
| L11 | 위험 문구 기본 목록은 임상 검토 전 임시(`provisional=true`) | 임상 담당 검토 필요 |
| L12 | 확정 사례(CONFIRMED)도 180일 뒤 삭제됨(`retention.cases_purge_confirmed`) | 병원 규정에 따라 사용자 결정 |
| L13 | D30(저자 확인=임상 승인)을 D92(4-eyes)로 대체. 의료인이 한 명뿐이면 막힘 | `QA_REQUIRE_TWO_PERSON=false`로 되돌림 가능. **사용자 확인 필요** |
| L14 | 알림 DB 장애 때 로컬 재시도 큐 없음(DELIVERY_FAILED 신호로만 대응), 정지 중 반복 발화 알림 중복 제거 없음 | survey-service 후속 |
| L15 | 학습 서버 스크립트 해시(`configs/train.yaml server.script_sha256`) 값 비어 있음 | 서버에서 `train-doctor` 실행 필요 |
| L16 | devDependency 취약점 3건(kiosk-frontend: playwright, ajv, fast-uri), admin-console 온라인 감사 미실시 | 런타임 영향 없음(`--omit=dev` 0건). 고치려면 고정 버전 밖 업그레이드 + 시험 이미지 재검증 |
| L17 | synthetic-data v1 생성 경로 폐기 표시만(D91), 보류 시험 15건 | 시드 경로 분리 뒤 삭제 |
| L18 | 서비스 값 형식 검증(선택지·단위·예/아니오)을 **실제 문항 세트(칸 정의 포함)** 로 학습 정답에 돌려 본 적이 없다. 서버 `question_bank.json`은 문장만 있고 칸 정의가 없다 | 칸 정의가 있는 실제 문항 세트는 의료인이 question-authoring으로 올리는 내용(사람 입력). 올라오면 `scripts/reference_agreement.py`로 재실행 |

## 3-1. GPU 구멍 (H, 2026-10-27 신설)

GPU 서버가 열릴 때 할 일이다. 줄기와 계획은 [`COMPLETION_PLAN.md`](COMPLETION_PLAN.md)가 갖는다. GPU 없이 닫을 수 없으므로 열림으로 둔다. 닫을 때 지우지 않는다.

| ID | 내용 | 관련 | 상태 |
|---|---|---|---|
| H1 | 24GB급 GPU에서 Qwen3-8B 적재·실측 | U02, U13 | 열림 |
| H2 | 학습된 LoRA-A/B를 얹어 한 턴이 통과하는지, 어댑터 교체 시험 | U07, U08, U10 | 열림 |
| H3 | 학습 파이프라인 실제 실행 | G06 | 열림 |
| H4 | 문법 컴파일 비용, 동시 요청 부하 | U01, U04 | 열림 |

## 4. 닫힘

| ID | 내용 | 근거 |
|---|---|---|
| C01 | 서버 실제 LLM 데모(학습 전 모델) | 2026-10-26, survey-service 8e0ba7e, deploy f76a94b |
| C02 | 계약 v2.0.0 | 태그 `v2.0.0`, D74, D75 |
| C03 | 서빙 프롬프트 직렬화를 학습 글자에 맞춤(model-runtime v0.6.1) | 시험 123 통과, 스모크 통과, D77 |
| G07 | turn-engine 폐기 함수 제거(1절 행도 `닫힘`) | turn-engine 23973fc, v0.4.0 |
| G09 | 정적 golden 제거(model-lab 쪽은 미확인, 1절 행 참고) | model-runtime 8279847, v0.7.0 |
| G10 | `prompt-3` 제거 | model-runtime 8279847, v0.7.0 |
| U15 | model-runtime dev 하드 핀 제거 | model-runtime 8279847, v0.7.0 |
