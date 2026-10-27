# 문진 시스템 개요 (팀 공유용 입구)

기준일 2026-10-27. 이 문서는 **새로 설명하지 않고 모으기만 한다.** 각 영역의 설명은 그 영역의 `README.md`가 정본이다. 확인은 이 PC와 gpu-dev(둘 다 WSL2 + Docker Desktop) 두 환경에서 했다. 깨끗한 일반 리눅스 서버에서는 확인하지 못했다(U06, U12).

## 1. 한 문단 요약

환자가 키오스크에서 말하면, 문진 서비스가 한 턴씩 처리한다. 첫 질문은 응답 모델(LoRA-B)만 부른다. 환자 발화가 오면 추출 모델(LoRA-A)이 값 추출·정규화·절차(action)·다음 문항을 한 번에 내고, 서비스는 그것을 검증해 저장하고, 표를 찾아 응답 재료를 모아 LoRA-B에 넘겨 환자에게 할 문장을 얻는다(D74~D76). 서비스에는 정규화기나 Plan 코드가 없다. 모델(LoRA 어댑터)은 학습 쪽이 만들고, 우리는 그것을 **패키지 → 릴리스 → 서빙**으로 얹는 환경과 서비스 계층을 맡는다.

## 2. 영역은 서로 독립이다 (마이크로서비스)

영역 사이는 HTTP로만 연결한다(D49). 한 서버에 모두 둘 수도, 서버를 나눌 수도, 일부만 묶을 수도 있다. 영역 사이의 연결에 필요한 것은 **상대 주소(URL)와 토큰 파일**뿐이고, 비밀은 환경 변수가 아니라 파일(`NAME_FILE`)로 받는다(D84).

| 배치 | 확인 여부 |
|---|---|
| 한 서버에 전부(Docker Compose) | 확인함(E2E, 이 PC) |
| 모델 서빙(model-serving)만 다른 서버 | 확인함(`test-inference-location.sh`, fake 추론 서버로, 이 PC) |
| 그 밖의 분리 조합(예: 게이트만 따로) | **확인하지 못함** |

## 3. 영역 지도

| 영역 | 한 줄 설명 | 입구 | 기준 버전 |
|---|---|---|---|
| boundary-contracts | 영역 사이 데이터 형식(계약)과 그것을 지키는지 확인하는 공유 패키지. 소유자는 헤드 | [README](../../boundary-contracts/README.md) | v2.0.2 |
| turn-engine | AI가 낸 "환자 답변 해석"이 말이 되는지 규칙으로 다시 검사하는 작은 라이브러리 | [README](../../turn-engine/README.md) | v0.4.0 |
| model-runtime | 두 모델(LoRA-A 추출, LoRA-B 응답)을 불러 호출하는 라이브러리 겸 추론 서버 | [README](../../model-runtime/README.md) | v0.7.2 |
| survey-service | 환자 발화 한 턴을 받아 저장값으로 바꾸고 다음 말을 돌려주는 HTTP 서비스 | [README](../../survey-service/README.md) | main |
| release-gate | 문항 세트와 모델 조합을 검사하고 사람이 승인한 조합만 릴리스로 묶는 서비스 | [README](../../release-gate/README.md) | main |
| ops-feedback | 운영 중 trace를 받아 개인정보를 지우고 실패 사례를 가려내는 영역 | [README](../../ops-feedback/README.md) | main |
| question-authoring | 의료인이 올린 문항 자료를 검토·확인해 바꿀 수 없는 문항 버전으로 저장하는 서비스 | [README](../../question-authoring/README.md) | main |
| model-lab | 어댑터를 모델 패키지로 묶어 보관·제공(model-registry), 학습 서버 코드 감싸기 | [README](../../model-lab/README.md) | main |
| synthetic-data | 학습·검증 데이터를 만들어 게시하는 run-once 잡(역할은 결정 대기, G02) | [README](../../synthetic-data/README.md) | main |
| deploy | 여러 영역의 이미지를 한 서버에 묶어 띄우고 되돌리고 끝에서 끝까지 시험하는 영역 | [README](../../deploy/README.md) | main |
| kiosk-frontend | 환자용 키오스크 화면과 직원 콘솔 화면 | [README](../../kiosk-frontend/README.md) | 계약 v2.0.2 |
| admin-console | 출고 승인과 실패 사례 검토 화면 | [README](../../admin-console/README.md) | 계약 v2.0.2 |

서비스 영역의 기준 버전 `main`은 계약 v2.0.2, turn-engine v0.4.0, model-runtime v0.7.2에 맞춰져 있다. `deploy/scripts/check-versions.sh`가 **10개 영역의 28개 표기**가 표와 같은지 확인한다(두 프런트엔드는 오늘 뒤늦게 정렬하고 점검 대상에 넣었다: admin-console은 계약 v1.3.3 기준이라 단위 시험 2건이 실패하고 있었고 고쳐서 42건 모두 통과, kiosk-frontend는 모의 서버의 `pipeline_schema_version`이 "1.0"으로 하드코딩된 것을 고침).

## 4. 지금 확인된 것 (숫자는 주인 문서에서 본다)

사실은 그것을 아는 영역이 한 곳에서만 쓴다. 이 문서는 복사하지 않고 가리킨다.

| 무엇 | 주인 문서 |
|---|---|
| 서비스 사이 연결(가짜 모델 E2E). **배선만 증명한다**: 모델은 가짜, 승인은 스크립트, 합성 데이터 단계는 BLOCKED. 가짜 A가 값을 내는 경로와 릴리스 교체 때 다른 서비스가 재시작되지 않는 것도 이 시험이 본다 | [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md) |
| 영역마다 자기 시험이 통과하는지 | 각 영역 README의 "현재 상태" 절 ([영역 지도](#3-영역-지도)의 링크) |
| 계약·turn-engine·model-runtime 버전이 영역 사이 일치하는지 | `deploy/scripts/check-versions.sh`, 기준표는 `deploy/scripts/lib.sh` |
| 영역 사이 정적 일관성(10규칙) | `deploy/scripts/check-all.sh` (실행하면 규칙별 검증됨/대상 아님/검증 안 함 분모가 나온다) |
| 비밀이 컨테이너 환경 변수로 읽히지 않는지 | `deploy/scripts/check-secrets-hidden.sh` (E2E 단계에도 있음) |
| 실제 LLM이 12GB GPU에 올라가는지, 출력 형식 | [`OPEN_GAPS.md`](OPEN_GAPS.md) U01, U04, U07 (gpu-dev 측정 기록) |
| 키오스크 화면 브라우저 시험(컨테이너) | [`kiosk-frontend/README.md`](../../kiosk-frontend/README.md) |

## 5. 아직 안 되는 것

- **실제 모델로 값 추출·저장이 도는 대화 한 턴.** 가짜 모델 E2E는 이제 이 경로를 지나간다(위 4절, 간접 단언). 실제 모델로는 아직 한 턴이 끝까지 통과한 적이 없다.
- (이어서) **실제 모델로 대화 한 턴이 끝까지 통과하는 것.** 학습 안 된 모델은 문항 세트에 없는 slot key를 지어내서 서비스가 막는다(`UNKNOWN_SLOT`). 이것은 설계대로 동작한 것(값을 지어내지 않음)이다. 학습된 LoRA-A를 얹어 봐야 한다(구멍 H2).
- **GPU가 필요한 일(구멍)**: 24GB급에서 Qwen3-8B 적재(H1), 학습된 어댑터 얹기와 교체 시험(H2), 학습 파이프라인 실제 실행(H3), 문법 컴파일 비용과 동시 부하(H4). 순서와 명령은 [`deploy/docs/GPU_HOLE.md`](../../deploy/docs/GPU_HOLE.md)에 있다.
- **학습 감싸기(G06)**: 학습 서버 스크립트의 인자 이름은 서버에서 읽어 `arg_map`을 채웠다(코드를 읽은 것이고 `--help`는 실행하지 않음). 학습 실제 실행은 H3로 남아 있다.
- **B 입력 표(G03)**: 데이터셋 담당의 `labels.py` 규칙을 옮겼다. 담당이 그 규칙을 기준으로 확정했다는 기록은 못 찾았다.
- **gpu-dev 실제 LLM**: 학습 안 된 Qwen3-1.7B로 기동·형식 통과·어댑터 교체까지 확인했다(U07, U08). 정확성은 확인하지 못했다.
- 실제 기기에서의 마이크·한국어 음성 인식·웹 푸시 구독, 일반 리눅스 서버 설치, 두 번째 독립 환경(U05, U06, U12).

## 6. 열린 항목 수

[`OPEN_GAPS.md`](OPEN_GAPS.md) 기준. 상태별 개수는 이 문서에 적지 않는다(표마다 열 구성이 달라 세면 틀린다). 대장의 각 행이 상태를 갖는다. **"완료"가 아니라 "N건 열림"이다.**

## 7. 역할 분배 제안

코드는 헤드(에이전트)가 짠다. 팀원은 **입력을 주고, 결정하고, 서버·접근을 열고, 내용을 확정하는 일**을 맡는다. 프레임워크는 사용자 포함 3명이고, 학습(LoRA-A, LoRA-B)과 데이터셋 증강 담당 3명은 이미 자기 일이 있어 부탁만 한다. 누구에게 줄지는 사용자가 정한다.

| 담당 | 사람이 할 일 (코드가 끝나길 기다리지 않고 지금 시작) | 코드 완성 뒤에 할 일 |
|---|---|---|
| **A: 서빙·인프라** | 이 PC에서 학습 서버(`openit`)가 왜 거부되는지 확인(주소·키 설정은 있음, 지금 포트 41822 거부), 24GB급 GPU 서버 확보 | 깨끗한 리눅스 서버에서 문서대로 설치 확인(U06, U12) |
| **B: 서비스·화면** | 질문 표 확정(데이터셋 담당과, G03·G13·G04), 직원 알림·재질문 규칙의 도메인 근거 모으기 | 실제 기기에서 마이크·음성 인식·푸시 확인(U05), 승인·검토 화면을 승인자 입장에서 써 보기 |
| **사용자: 결정과 창구** | 결정: 직원 알림 입력원(G01), 재질문 상한 값(G12), synthetic-data 역할(G02), 운영 정책(D-A), 문진 결과가 병원으로 나가는 경로 확인(공개 API 문서와 `INTERFACES.md`에서 찾지 못함) | — |

학습·데이터셋 담당에게 하는 부탁은 2건이다: 이번에 쓸 학습된 어댑터 A·B 쌍(어댑터는 서버에 이미 있음)과 그 시스템 프롬프트·run 기록 위치를 정해 알려 주기, 데이터셋 증강 담당의 질문 표 확정과 합성 데이터 영역의 v2 대응 의견. 학습 스크립트의 인자 이름은 접속이 되면 헤드가 서버에서 읽는다.

**헤드가 짠 코드(만들어서 확인함)**: `demo.sh swap-adapters`(가짜 백엔드와 gpu-dev 실제 LLM 데모에서 실행, U08), `probe-serving`, PostgreSQL 전환, 결과 조회·위험 신호 API, 기기·행위자 인증. **남은 것**: 정정(CORRECT) 흐름 시험, 직원 알림 규칙(사용자 결정), model-lab 24GB용 프로파일, 승인 화면의 v2 지표 표시, 병원·외부 감지기가 들어올 내부 입구(미정).

제품이 완성된 뒤의 일: 실제 GPU에서 학습된 어댑터로 한 턴 통과(H1~H3, [`deploy/docs/GPU_HOLE.md`](../../deploy/docs/GPU_HOLE.md)).

## 8. 문서 지도 (head/docs)

| 문서 | 무엇인가 | 누가 읽나 |
|---|---|---|
| 이 문서 `OVERVIEW.md` | 입구. 영역 지도, 상태, 역할 분배 | 모두 |
| 영역별 `README.md` | 그 영역의 정본 설명 | 모두 |
| [`OPEN_GAPS.md`](OPEN_GAPS.md) | 비워 두었거나 확인하지 못한 것의 대장 | 모두 |
| [`DECISIONS.md`](DECISIONS.md) | 확정한 결정(D01~D85) | 결정 근거가 필요할 때 |
| [`STATUS.md`](STATUS.md) | 진행 기록 | 헤드 |
| [`COMPLETION_PLAN.md`](COMPLETION_PLAN.md) | 완성까지의 작업줄기와 GPU 구멍 | 헤드, 계획 확인 |
| [`STRUCTURE.md`](STRUCTURE.md) | 에이전트용 구조 요약이자 영역 작업의 기준 | 에이전트 |
| [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) | 사람용 구조 설명(턴 도식, 소유와 의존 방향) | 사람 |
| [`architecture.md`](architecture.md) | 흐름·시퀀스·상태·배포 도식(790줄) | 상세가 필요할 때 |
| `E2E.md`, `HANDOFF.md`, `impact-d74.md`, `migration-2.0.0.md`, `metrics-v2-proposal.md`, `dataset-requests.md` | 시험 시나리오, 인수인계, 변경 지시서·제안 | 해당 작업자 |

`STRUCTURE.md`, `PROJECT_STRUCTURE.md`, `architecture.md`는 내용이 겹친다. 하나로 합칠지는 정하지 않았고, 우선은 위 표처럼 역할만 구분해 둔다.

## 9. 문서 정리 결과와 남은 것

영역들이 README를 쓰며 찾은 낡은 문서(STATUS의 시험 개수·태그 상태, `brief.md`의 v1 서술, 계약 버전 표기, 비밀을 환경 변수로 주는 예시, `V2_DRAFT.md`의 검토 대기 문구 등)는 10개 영역에서 문서만 고쳐 push했다(코드 변경 없음). 남은 것은 코드나 헤드의 판단이 필요한 것이다.

| 남은 것 | 이유 | 누가 |
|---|---|---|
| model-runtime `make_neutral_package.py` 도움말 "gpu-12g는 Qwen3-4B" (실제 1.7B), `profiles/gpu-12g.json`의 `loadable: unverified`에 측정값 반영 | 코드 영역 | 다음 model-runtime 릴리스에 묶음 |
| model-lab `configs/gpu-dev-fixture-*.yaml` 주석 "golden에서 만든", `pyproject` 0.1.0 vs CHANGELOG 0.2.3 | 코드 영역 | model-lab |
| turn-engine CR-010(QuestionBank에서 표를 만드는 변환 함수), `docs/rules/` 삭제 여부 | 헤드 결정 | 헤드 |
| I2(DatasetStore)를 HTTP로 정할지 | 계약 설계 결정 | 헤드 |
| admin-console CR-003(생성물 커밋 정책) | 헤드 결정 | 헤드 |
| `METRICS.md` v1 지표 | [`metrics-v2-proposal.md`](metrics-v2-proposal.md) 참고 | 헤드 + 학습 담당 |
| `STRUCTURE.md`, `PROJECT_STRUCTURE.md`, `architecture.md` 겹침 | 합칠지 결정 안 함 | 헤드 |
