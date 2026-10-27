# 문진 시스템 개요 (팀 공유용 입구)

기준일 2026-10-27. 이 문서는 **새로 설명하지 않고 모으기만 한다.** 각 영역의 설명은 그 영역의 `README.md`가 정본이다. 숫자는 이 PC(WSL2 + Docker Desktop) 한 환경에서 확인한 값이고, 깨끗한 두 번째 환경에서는 확인하지 못했다(U12).

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
| model-runtime | 두 모델(LoRA-A 추출, LoRA-B 응답)을 불러 호출하는 라이브러리 겸 추론 서버 | [README](../../model-runtime/README.md) | v0.7.0 |
| survey-service | 환자 발화 한 턴을 받아 저장값으로 바꾸고 다음 말을 돌려주는 HTTP 서비스 | [README](../../survey-service/README.md) | main |
| release-gate | 문항 세트와 모델 조합을 검사하고 사람이 승인한 조합만 릴리스로 묶는 서비스 | [README](../../release-gate/README.md) | main |
| ops-feedback | 운영 중 trace를 받아 개인정보를 지우고 실패 사례를 가려내는 영역 | [README](../../ops-feedback/README.md) | main |
| question-authoring | 의료인이 올린 문항 자료를 검토·확인해 바꿀 수 없는 문항 버전으로 저장하는 서비스 | [README](../../question-authoring/README.md) | main |
| model-lab | 어댑터를 모델 패키지로 묶어 보관·제공(model-registry), 학습 서버 코드 감싸기 | [README](../../model-lab/README.md) | main |
| synthetic-data | 학습·검증 데이터를 만들어 게시하는 run-once 잡(역할은 결정 대기, G02) | [README](../../synthetic-data/README.md) | main |
| deploy | 여러 영역의 이미지를 한 서버에 묶어 띄우고 되돌리고 끝에서 끝까지 시험하는 영역 | [README](../../deploy/README.md) | main |
| kiosk-frontend | 환자용 키오스크 화면과 직원 콘솔 화면 | [README](../../kiosk-frontend/README.md) | 계약 정렬 진행 중 |
| admin-console | 출고 승인과 실패 사례 검토 화면 | [README](../../admin-console/README.md) | 계약 정렬 진행 중 |

서비스 영역의 기준 버전 `main`은 계약 v2.0.2, turn-engine v0.4.0, model-runtime v0.7.0에 맞춰져 있다(`deploy/scripts/check-versions.sh`가 8개 영역의 26개 표기가 표와 같은지 확인한다. 두 프런트엔드는 아직 이 점검 대상이 아니었고, 지금 맞추는 중이다).

## 4. 지금 확인된 것

| 무엇 | 결과 | 어디서 확인 |
|---|---|---|
| 끝에서 끝까지 한 바퀴(가짜 모델) | 92 PASS / 0 FAIL (전체 모드, BLOCKED/TEST-SUB 단계가 있어 시나리오 전체 합격은 아님) | deploy `scripts/e2e.sh`, 이 PC |
| 데모 띄우기(가짜 모델) | 성공, 비밀 노출 점검 통과 | `deploy/scripts/demo.sh up`, 이 PC |
| 비밀이 환경 변수로 읽히지 않음 | 통과(컨테이너 9개, 비밀 파일 42개) | `deploy/scripts/check-secrets-hidden.sh` |
| 실제 LLM(Qwen3-1.7B)이 12GB GPU에 올라감 | 확인, 약 10.1GB 사용, 기동 166초 | gpu-dev, model-runtime v0.6.5 |
| LoRA-A 출력이 제약 디코딩으로 형식을 지킴 | 48회 모두 통과(OUTPUT_INVALID 0) | gpu-dev, v0.6.5 |
| 키오스크 화면 브라우저 시험 | 9/9 통과, 호스트 설치 없이 컨테이너로 | kiosk-frontend `npm run test:e2e`, 이 PC |

## 5. 아직 안 되는 것

- **실제 모델로 대화 한 턴이 끝까지 통과하는 것.** 학습 안 된 모델은 문항 세트에 없는 slot key를 지어내서 서비스가 막는다(`UNKNOWN_SLOT`). 이것은 설계대로 동작한 것(값을 지어내지 않음)이다. 학습된 LoRA-A를 얹어 봐야 한다(구멍 H2).
- **GPU가 필요한 일(구멍)**: 24GB급에서 Qwen3-8B 적재(H1), 학습된 어댑터 얹기와 교체 시험(H2), 학습 파이프라인 실제 실행(H3), 문법 컴파일 비용과 동시 부하(H4). 순서와 명령은 [`deploy/docs/GPU_HOLE.md`](../../deploy/docs/GPU_HOLE.md)에 있다.
- **학습 서버 접속**이 지금 거부된다(포트 41822 `Connection refused`). 학습 서버 스크립트의 인자 이름을 읽어야 학습 감싸기(G06)의 인자 매핑을 채울 수 있다.
- 실제 기기에서의 마이크·한국어 음성 인식·웹 푸시 구독, 일반 리눅스 서버 설치, 두 번째 독립 환경(U05, U06, U12).

## 6. 열린 항목 수

[`OPEN_GAPS.md`](OPEN_GAPS.md) 기준. 닫힌 것: 이 문서를 쓰는 시점에 열림 25, 부분 7, 닫힘 4(갱신하면 달라진다). **"완료"가 아니라 "N건 열림"이다.**

## 7. 역할 분배 제안

누구에게 줄지는 사용자가 정한다. 아래는 일의 묶음이다. 모두 지금 바로 시작할 수 있고 헤드의 결과를 기다릴 필요가 없다.

| 역할 | 맡길 일 | 받는 것 | 내놓는 것 | 완료 기준 |
|---|---|---|---|---|
| LoRA 학습 담당 | 학습 서버 스크립트의 인자 이름, 어댑터 출력 위치, run 기록의 키를 알려 주기(G06) | 서버의 `train_lora_a.py`, `train_lora_b.py` | model-lab `configs/train.yaml`의 `arg_map`을 채울 정보 | `train --dry-run`이 실제 명령을 출력 |
| 〃 | 학습된 어댑터 쌍(A와 B가 같은 기반 모델) + 학습에 쓴 시스템 프롬프트 + run 기록을 한 폴더로 모으기(H2) | 학습 결과 | 어댑터 2개, 프롬프트 2개, 데이터셋 해시, 기반 모델 revision | `package-adapters`가 거부 없이 패키지를 만듦 |
| 데이터셋 담당 | 질문 표 확정(G03, G13, G04): `ask` 문장 틀, 칸 설명, 술 이름. 지금 `DRAFT_UNCONFIRMED` | `survey-service/schema/data/response_tables.json` | 확정된 표 | 표 상태가 확정으로 바뀜 |
| 〃 | IO_SPEC 최신화, [`dataset-requests.md`](dataset-requests.md)의 요청 처리 | dataset-requests.md | 갱신된 IO_SPEC | 서비스 쪽 표와 일치 |
| 정규화 담당 | 변경 범위와 확정 시점 알려 주기(U09, D-B) | — | 한 줄 공지 | 계약 영향 여부를 헤드가 판단 가능 |
| 도메인·임상 책임자 | 환자 안전 값 정하기: 직원 알림을 언제 낼지(G01), 재질문 몇 번까지(G12), 대체 문구(G04), 금지 표현 | OPEN_GAPS의 해당 행 | 결정 | 코드에는 설정 자리가 이미 있어 값만 넣으면 됨 |
| 프론트·현장 담당 | 실제 기기에서 사람이 확인(U05): 마이크 권한, 한국어 음성 인식, TTS, 글꼴, 푸시 | `kiosk-frontend/docs/runbook.md`의 체크리스트, `demo.sh up` | 체크 결과 | 전 항목 합격/불합격 |
| 인프라 담당 | 깨끗한 리눅스 서버에 문서만 보고 설치해 막힌 곳 보고(U06, U12) | `deploy/docs/SETUP.md`, `RUN.md` | 막힌 곳 목록 | `demo.sh up`이 처음부터 끝까지 성공 |
| 〃 | 학습 서버 접속 복구, 24GB급 GPU 서버 제공(H1~H3) | — | 접속 정보 | 읽기 전용 접속 성공 |
| 운영·보안 담당 | 운영 정책(D-A): 도메인·HTTPS, 직원 콘솔 로그인, 토큰 발급·회전, 원본 보관 기간 | — | 정책 문서 | 정책 확정 |

## 8. 문서 지도 (head/docs)

| 문서 | 무엇인가 | 누가 읽나 |
|---|---|---|
| 이 문서 `OVERVIEW.md` | 입구. 영역 지도, 상태, 역할 분배 | 모두 |
| 영역별 `README.md` | 그 영역의 정본 설명 | 모두 |
| [`OPEN_GAPS.md`](OPEN_GAPS.md) | 비워 두었거나 확인하지 못한 것의 대장 | 모두 |
| [`DECISIONS.md`](DECISIONS.md) | 확정한 결정(D01~D84) | 결정 근거가 필요할 때 |
| [`STATUS.md`](STATUS.md) | 진행 기록 | 헤드 |
| [`COMPLETION_PLAN.md`](COMPLETION_PLAN.md) | 완성까지의 작업줄기와 GPU 구멍 | 헤드, 계획 확인 |
| [`STRUCTURE.md`](STRUCTURE.md) | 에이전트용 구조 요약이자 영역 작업의 기준 | 에이전트 |
| [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) | 사람용 구조 설명(턴 도식, 소유와 의존 방향) | 사람 |
| [`architecture.md`](architecture.md) | 흐름·시퀀스·상태·배포 도식(790줄) | 상세가 필요할 때 |
| `E2E.md`, `HANDOFF.md`, `impact-d74.md`, `migration-2.0.0.md`, `metrics-v2-proposal.md`, `dataset-requests.md` | 시험 시나리오, 인수인계, 변경 지시서·제안 | 해당 작업자 |

`STRUCTURE.md`, `PROJECT_STRUCTURE.md`, `architecture.md`는 내용이 겹친다. 하나로 합칠지는 정하지 않았고, 우선은 위 표처럼 역할만 구분해 둔다.

## 9. 문서 정리 목록 (README를 쓰면서 영역들이 찾은 어긋남)

코드 문제가 아니라 낡은 문서다. 영역이 각자 고친다.

- **여러 영역**: STATUS에 적힌 시험 개수가 실제 수집 개수와 다르다(ops-feedback, survey-service, synthetic-data, model-lab, kiosk-frontend). 과거 시점 문구가 남은 `brief.md`(model-runtime, turn-engine, release-gate, question-authoring).
- **boundary-contracts**: `V2_DRAFT.md`가 "브랜치, 검토 대기"로 낡았다. `HTTP.md`에는 I2(DatasetStore) 절이 없다. `METRICS.md`는 v1 지표(D-C, 제안: `metrics-v2-proposal.md`).
- **model-runtime**: `profiles/gpu-12g.json`의 `loadable`이 `unverified`인데 gpu-dev에서 적재를 확인했다. runbook이 `gpu-dev-12g.json`이라 적은 곳이 있다.
- **turn-engine**: `STATUS.md`가 브랜치·태그 없음으로 적혀 있으나 실제로는 main에 `v0.4.0`이 있다. 계약 문서(`INTERFACES.md`)에 제거된 `SUPPORTED_RUNTIME_CONTRACT_VERSION`이 남아 있다.
- **survey-service**: `design.md` 1~15절이 v1 내용이다(머리말에 폐기 표시). `boundary.md`가 계약 v2.0.1이라 적었다.
- **deploy**: `boundary.md`가 계약 v1.1.0, 서비스 6개로 적었으나 실제는 서비스 9개와 잡 2개이고 계약 v2.0.2다. STATUS는 v0.6.2에서 멈춰 있다.
- **ops-feedback**: README 한 곳이 비밀을 환경 변수로 주는 예시를 보여 준다(`OPS_INGEST_TOKEN=...`). `NAME_FILE` 예시로 바꿔야 한다.
- **OPEN_GAPS**: G09(model-lab 쪽 제거 완료)를 닫힘으로 바꿔야 한다. CR-010, O11, O16처럼 영역 문서에 있지만 대장에 ID가 없는 항목이 있다.
