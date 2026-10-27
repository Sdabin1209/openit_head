# 프로젝트 구조

문진 시스템 워크스페이스의 구조를 한 장으로 정리한 문서다. 리포 13개, 각 리포 안에 무엇이 있는지, 서로 어떻게 연결되는지만 다룬다. 세부 설계와 근거는 `DECISIONS.md`(결정 D01~D84)와 각 리포의 `docs/`에 있다. 폴더 목록은 2026-10-26에 각 리포에서 직접 확인했다(이후 바뀐 폴더는 확인하지 않았다). 턴 처리와 계약·라이브러리 서술은 2026-10-27에 학습 데이터셋 v2(D74) 기준으로 고쳤다(계약 v2.0.2, turn-engine v0.4.0, model-runtime v0.7.0).

## 1. 전체 흐름 (큰 그림)

```mermaid
flowchart TB
  subgraph PIPE["모델·문항 파이프라인 (학습 서버 쪽)"]
    QA["question-authoring<br/>문항 저작·의료인 확인"]
    SD["synthetic-data<br/>합성 데이터"]
    ML["model-lab<br/>학습·평가·패키징"]
    REG["model-registry<br/>모델 패키지 보관"]
    RG["release-gate<br/>자동 검사·승인·릴리스·활성 포인터"]
  end
  subgraph RUN["운영 (서빙·백 서버 쪽)"]
    GW["게이트웨이 Caddy<br/>인증·토큰 주입·경로 분리"]
    SS["survey-service<br/>문진 서비스 (LangGraph)<br/>저장·표 조회·안전장치"]
    MS["model-serving<br/>추론 서버 (model-runtime)<br/>LoRA-A extract · LoRA-B respond"]
    OF["ops-feedback<br/>수집·비식별·실패 사례"]
  end
  subgraph UI["사람이 쓰는 화면 (정적)"]
    KF["kiosk-frontend<br/>환자 화면 · 직원 콘솔"]
    AC["admin-console<br/>출고 승인 · 실패 사례 검토"]
  end
  subgraph LIB["공유 계약·라이브러리"]
    BC["boundary-contracts<br/>계약 스키마·HTTP 규약·클라이언트"]
    TE["turn-engine<br/>A 출력 사후 검증 규칙"]
  end
  DP["deploy<br/>Compose·이미지 잠금·E2E"]
  HD["head<br/>결정 기록·브리프"]

  QA --> SD --> ML --> REG
  REG --> RG
  QA --> RG
  RG -->|"승인 요청"| AC
  AC -->|"승인·반려"| RG
  RG -->|"활성 릴리스·번들"| SS
  RG -->|"번들 읽기"| MS
  KF --> GW --> SS
  SS --> MS
  SS --> TE
  SS -.->|"Trace"| OF
  OF -->|"실패 사례"| AC
  AC -->|"검토 확정"| OF
  OF -.->|"문항 개선 신호"| QA
  OF -.->|"회귀 평가 사례"| ML
  OF -.->|"롤백 요청"| RG
  GW --> AC
  GW --> RG
  GW --> OF
  BC -. "모든 영역이 의존" .-> PIPE
  BC -. "" .-> RUN
  DP -. "빌드·기동·검증" .-> RUN
  DP -. "" .-> PIPE
  DP -. "" .-> UI
  HD -. "계약·결정" .-> BC
```

굵은 규칙은 네 가지다. 영역 하나가 리포 하나이고, 영역끼리는 `boundary-contracts`의 HTTP 계약으로만 만나며, 출고 승인과 실패 사례 검토는 사람이 하고, 모델 성능은 완성 기준에 넣지 않았다.

## 2. 리포별로 무엇이 들어 있나

| 리포 | 역할 | 들어 있는 것 |
|---|---|---|
| **head** | 결정 기록, 영역 브리프, 워크스페이스 구성 | `docs/`(DECISIONS, STRUCTURE, STATUS, E2E, HANDOFF, architecture, 이 문서), `briefs/`(영역별 브리프), `templates/`(브리프·CLAUDE.md 템플릿), `shared/`(루트 공통 규칙), `scripts/`(`new-area.sh`), `setup.sh`, `workspace.yaml`, `README.md` |
| **boundary-contracts** | 영역 사이 계약 (헤드 소유) | `schemas/`(레코드 스키마 28개 + 공통 타입 `_common.schema.json`, 확인: `ls schemas`가 29개를 냄(2026-10-27). v2 모델 입출력은 `ActionExtraction*`, `Response*`), `examples/`(스키마별 예시), `boundary_contracts/`(패키지: 검증기·해시 계산·HTTP 클라이언트), `conformance/`(참조 서버), `tests/`, `verify.py`, 문서 `INTERFACES.md` `HTTP.md` `PUBLIC_API.md` `CONVENTIONS.md` `METRICS.md` |
| **turn-engine** | LoRA-A 출력의 사후 검증(`validate_extraction`, `QuestionFlowTable`) 순수 라이브러리. v1의 정규화·판정·기록·Plan은 v0.4.0에서 제거했다(G07 닫힘) | `turn_engine/`(엔진), `tests/`, `examples/`, `scripts/`, `docs/` |
| **model-runtime** | 추론 런타임과 추론 서버 (vLLM, 제약 디코딩). `extract`(JSON)와 `respond`(텍스트) | `src/`(런타임·서버), `profiles/`(GPU 프로파일), `scripts/`(스모크·GPU 점검), `runs/`(실행 산출물), `Dockerfile`, `requirements-cpu.lock` `requirements-gpu.lock`, `tests/`, `docs/` (이 행의 폴더 목록은 2026-10-26 확인분이고 0.7.0에서 `tests/golden/`을 제거했다) |
| **survey-service** | 문진 서비스 + 문진 스키마 소유 | `survey_service/`(LangGraph 오케스트레이터·공개 API·세션 저장소·Trace·직원 알림·추론 호출·표 찾기 표). 정규화기·Plan 코드는 없다, `schema/`(문진 스키마), `scripts/`(스모크), `tests/`, `Dockerfile`, `requirements.lock`, `docs/` |
| **question-authoring** | 문항 저작·검수·문항 세트 보관 | `question_authoring/`, `examples/`, `scripts/`, `tests/`, `Dockerfile`, `requirements.lock`, `docs/` |
| **synthetic-data** | 합성 데이터 생성 | `synthetic_data/`, `configs/`, `work/`(작업 폴더), `tests/`, `requirements.lock`, `docs/` |
| **model-lab** | 학습·평가·패키징·모델 레지스트리 | `model_lab/`, `configs/`, `profiles/`, `fixtures/`, `vendor/`(휠), `scripts/`, `runs/`, `tests/`, `Dockerfile`, `requirements*.lock/txt`(서비스용·학습용 분리), `CHANGELOG.md`, `docs/` |
| **release-gate** | 자동 검사, 사람 승인, 릴리스, 활성 포인터, 롤백 | `release_gate/`(`app.py` HTTP, `gate.py` 판정, `checks.py` 검사, `collector.py` 후보 수집, `review.py` 승인, `views.py` 제출 조회, `store.py` 저장, `policy.py` 정책), `scripts/`, `tests/`, `Dockerfile`, `requirements.lock`, `docs/` |
| **ops-feedback** | 수집, 비식별, 실패 탐지, 검토 큐, 롤백 요청 | `src/ops_feedback/`(`deid.py` 비식별, `logstore.py` 원본 저장, `failurestore.py` 실패 사례, `detect.py` 탐지, `review.py` 검토, `job.py` 주기 잡, `api.py` HTTP, `rollback.py` 롤백 평가, `config.py`), `config/`, `examples/`, `scripts/`, `tests/`, `Dockerfile`, `docs/` |
| **deploy** | 배포 구성, 이미지 잠금, 전체 시험 | `compose.yaml`(+`compose.test.yaml` `compose.registry.yaml`), `config/`(`Caddyfile`, 서비스별 `*.env`, 주기 잡 설정), `locks/`(`images.lock`+이력), `scripts/`(`e2e.sh` `up.sh` `doctor.sh` `publish-image.sh` `backup.sh` `restore.sh` `rollback.sh` `scheduler.py` 등), `test/`(시험 자료), `docs/`(SETUP, runbook, ci), `CHANGELOG.md` |
| **kiosk-frontend** | 환자 키오스크 화면, 직원 콘솔 (정적 웹) | `apps/`(두 앱), `api/`(공개 API 클라이언트), `mock-server/`(공개 API 모의 서버), `server/`(정적 서버), `scripts/`, `test/`, `Dockerfile`, `docs/` |
| **admin-console** | 출고 승인, 실패 사례 검토 (정적 웹) | `app/`(화면), `api/`(게이트·실패 사례 클라이언트), `generated/`, `mock-server/`, `serve/`(정적 서버), `scripts/`, `tests/`, `Dockerfile`, `docs/` |

## 3. 누가 누구를 부르나

| 호출하는 쪽 | 받는 쪽 | 무엇을 |
|---|---|---|
| 키오스크 앱 | survey-service (게이트웨이 경유) | 세션 시작·발화·종료·상태 조회 (공개 API) |
| 직원 콘솔 | survey-service (게이트웨이 경유) | 알림 목록·SSE·푸시 구독·멈춘 세션 재개/종료 (알림의 입력원은 아직 없다, G01) |
| survey-service | model-serving | `extract`(LoRA-A)·`respond`(LoRA-B) 호출, 릴리스 적재 신호 |
| survey-service | release-gate | 활성 포인터·릴리스 번들 읽기 |
| survey-service | ops-feedback | Trace 전송(비동기) |
| model-serving | release-gate | 릴리스 번들 직접 읽기 |
| release-gate | model-registry(model-lab) | 모델 패키지·평가 보고서 읽기 |
| release-gate | question-authoring | 문항 세트·검수 기록 읽기 |
| admin-console | release-gate | 제출 목록·승인 보고서·승인/반려 |
| admin-console | ops-feedback | 실패 사례 목록·검토 확정 |
| ops-feedback | release-gate | 롤백 요청 |
| model-lab | ops-feedback·synthetic-data·question-authoring | 실패 사례·데이터셋·문항 읽기 (I7, I2, I1) |
| synthetic-data | ops-feedback·question-authoring | 실패 사례 시드·문항 읽기 |
| question-authoring | ops-feedback | 문항 개선 신호 읽기 |

survey-service는 문항 세트를 question-authoring에서 직접 읽지 않고 릴리스 번들(I4)로 받는다(근거: `survey-service/survey_service/clients.py`는 `HttpReleaseReader`·`HttpTraceIngest`만 만들고, `boundary-contracts/INTERFACES.md`의 I1 소비자는 synthetic-data·model-lab·release-gate).

호출 규약은 `boundary-contracts/HTTP.md`(서비스 사이)와 `PUBLIC_API.md`(화면 ↔ 서비스)에 있다.

### 3-1. 한 턴의 흐름 (v2)

```mermaid
flowchart TB
  K["키오스크 앱"] -->|"세션 시작"| S0["survey-service"]
  S0 -->|"START: A를 부르지 않는다<br/>B 입력(topic, next)을 표에서 조립"| B0["LoRA-B respond"]
  K -->|"발화(STT 텍스트)"| S1["survey-service"]
  S1 -->|"A 입력(question_id, current_question,<br/>user_utterance, state)"| A["LoRA-A extract<br/>정규화·절차(action)·next_item"]
  A -->|"제약 디코딩(anyOf)이<br/>형식·변형 규칙을 지킨다"| V["사후 검증<br/>validate_extraction (turn-engine)"]
  V -->|"위반/OUTPUT_INVALID:<br/>1회 재시도, 그래도 안 되면<br/>turn_failure_signal, 세션 불변"| F["턴 실패"]
  V -->|"통과"| W["저장 (save=true인 값만)<br/>세션 저장소 한 트랜잭션"]
  W --> T["표 조회: 문항 번호로 질문 문장,<br/>ask 틀, 칸 설명 (survey-service 소유)"]
  T -->|"B 입력(action, known, ask, next ...)"| B["LoRA-B respond<br/>(텍스트, 실패하면 대체 문장)"]
  B --> R["응답 문장 -> 키오스크"]
```

- 서비스에는 정규화기·판정기·기록기·Plan 코드가 없다. 정규화, 절차(NEXT, REASK, CORRECT, CONFIRM, REDIRECT, HOLD, SKIP), 다음 문항을 LoRA-A가 정한다(D74). 서비스는 표 찾기, 저장, 전달, 안전장치를 한다.
- LoRA-A 출력은 두 번 걸러진다. 먼저 model-runtime이 제약 디코딩으로 형식을 지키게 한다: `pattern`·`minItems`를 그대로 넘기고(D82) `if/then` 의미 규칙을 같은 뜻의 `anyOf` 변형으로 펼쳐 넘긴다(D83). 계약 스키마 원본은 바꾸지 않는다. 그런 다음 survey-service가 turn-engine의 `validate_extraction`으로 의미 규칙(`targets`는 `values` 키의 부분집합, `next_item` 규칙, 건너뛰기 순서, `save` 규칙)을 검사한다(D75). 문항 순서·건너뛰기 표(`QuestionFlowTable`)는 survey-service가 소유하고 문진 스키마에서 만든다(D76).
- A가 끝내 형식을 못 지키면 서버는 값을 지어내지 않고 503 `UNAVAILABLE`(`details.reason=OUTPUT_INVALID`)을 낸다. 서비스는 한 번 재시도하고, 그래도 안 되면 그 턴을 실패 신호로 끝내며 세션 상태를 바꾸지 않는다(D75). 모르는 slot key는 `UNKNOWN_SLOT` 검증에서 걸린다(D75, 실측은 OPEN_GAPS U07).
- B는 JSON이 아니라 문장 하나를 낸다. 출력이 깨지면 재료를 이은 대체 문장이 나가고 턴은 실패하지 않는다.
- 서빙이 모델에 넣는 입력 글자는 학습 데이터와 한 글자도 다르면 안 된다(`prompt-4`, D77). 시스템 프롬프트는 모델 패키지의 일부다(D75).
- 직원 알림: v2 A 출력에 위험 신호 필드가 없어 입력원이 비어 있다(G01). 포트(`RiskSource`)와 알림 API·SSE·푸시는 있고 `/readyz`가 `staff_alert_source.active=false`로 드러낸다. 재질문 상한(G12)은 기본 꺼짐이다. 사용자 결정 대기.

### 3-2. 소유와 의존 방향

| 소유 | 내용 | 소유자 |
|---|---|---|
| 계약 스키마(영역 사이) | `boundary-contracts`(v2.0.2). 태그로 설치, 복사본 금지 | head |
| 문진 스키마(정수 버전 1), 문항 순서·건너뛰기 표(`QuestionFlowTable`), 표 찾기 표(`ask` 틀·칸 설명, 초안) | `survey-service/schema/` | survey-service |
| A 출력의 의미 검증 함수 | turn-engine | turn-engine |
| 제약 디코딩, 프롬프트 직렬화, 추론 서버 | model-runtime | model-runtime |
| 학습 | 학습 서버의 코드가 정본(D78). model-lab은 변환·평가·회귀·패키징·게시 | 학습 서버 / model-lab |

의존은 한 방향이다: 문진 스키마·boundary-contracts <- turn-engine·model-runtime <- 영역 리포. 영역 리포끼리 코드를 가져오지 않고, 이웃과는 `boundary-contracts/HTTP.md`의 HTTP API로만 만난다(D49). 태그는 완전 일치로 맞춘다(D80): 같은 열차(현재 bc v2.0.2, turn-engine v0.4.0, model-runtime v0.7.0)를 모든 영역이 쓴다.

## 4. 배포에서의 모양

- `deploy/compose.yaml`이 서비스를 한꺼번에 띄운다: `gateway`, `kiosk-frontend`, `admin-console`, `survey-service`, `question-authoring`, `ops-feedback-ingest`, `release-gate`, `model-serving`, `model-registry`. 이 밖에 일회성 `model-serving-schema`(문진 스키마를 꺼냄)와, 프로파일 `jobs`로 한 번 실행하는 `job-ops-feedback`, `job-release-gate-collect`가 있다(확인: `deploy/compose.yaml`).
- 브라우저는 게이트웨이만 부른다. 게이트웨이(Caddy, `deploy/config/Caddyfile`)가 경로와 사람 계정 역할(`release-approver`, `reviewer`)에 맞춰 서버 토큰을 붙이고 `X-Openit-User`로 사용자를 기록한다.
- 이미지는 digest로 고정(`deploy/locks/images.lock`)하고 레지스트리에 올린다.
- 비밀(서비스 토큰, salt, VAPID 키)은 환경 변수가 아니라 **파일**로 받는다(D84): 서비스는 `<이름>_FILE`이 가리키는 파일을 읽고, 환경 변수는 개발·시험용 호환이다. deploy가 compose `secrets:`로 `/run/secrets/…`에 마운트한다(`deploy/docs/boundary.md`). 값은 로그·`/readyz`·오류 응답에 내지 않는다. 발급·회전·보관 정책은 미정이다(D-A).
- 전체 시험은 `deploy/scripts/e2e.sh`(단계 1~9, 옵션 `--fast` `--reuse-build` `--keep`), 설치는 `deploy/docs/SETUP.md`.

## 5. 확인 수준 (2026-10-26 기준, 마지막 두 항목은 10-27)

- 서비스끼리 실제 HTTP로 도는 전체 시험은 개발 PC에서 통과했다(`deploy/docs/STATUS.md` 여덟째 구간, 전체 모드. 최신 결과: [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md)). 모델은 고정 출력 가짜 백엔드이고, 승인자 등 일부는 시험용 대체다.
- 서버(`gpu-dev`, RTX 4070 SUPER 12GB, WSL2의 Docker Desktop 연동)에서 `doctor.sh` 통과와 전체 시험 통과를 사용자가 보고했다(2026-10-26, 당시 사용자 보고이며 수치는 [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md)의 과거 기록 표를 따른다). 리포의 기록 파일에서는 확인하지 못했고, 개발 PC 결과와 차이가 있었다면 그 이유도 확인하지 못했다. D47("Docker 없음", 2026-10-15)은 그 시점의 사실이고 이후 바뀌었다.
- 실제 LLM 데모(D72): gpu-dev에서 vLLM(Qwen2.5-1.5B + 중립 LoRA)으로 문진 응답이 나오는 것을 확인했다(2026-10-26). survey-service의 릴리스 적재 재시도 수정(8e0ba7e)과 deploy `llm-demo`가 main에 병합됐다. 응답 품질은 학습 전이라 판단하지 않는다.
- 구조(D74, 2026-10-27): 학습 데이터셋 v2에 맞춰 정규화·절차·다음 문항을 LoRA-A가 하고 서비스는 표 찾기·저장·안전장치만 한다. 이 문서의 그림과 표는 2026-10-27에 v2 기준으로 고쳤다. 영향 목록은 `impact-d74.md`.
- 계약 패키지 현재 태그는 `v2.0.2`, turn-engine `v0.4.0`, model-runtime `v0.7.0`(`git tag`로 확인, 2026-10-27). 이 절 앞쪽의 E2E 결과와 LLM 데모 값은 2026-10-26(v1 구조) 기록이다. v2 가짜 모델 E2E 기록은 [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md)에 있고, 현재 열차로 다시 돌린 결과는 이 문서 갱신에서 확인하지 못했다. 현재 값은 `STATUS.md`를 따른다.
- 실제 브라우저 화면, 한국어 음성 인식, 웹 푸시 수신, RTX 4090 실측은 확인하지 못했다.
- 미정: 운영 도메인·HTTPS, 직원 콘솔 로그인, CI가 서버 레지스트리에 닿는 방법, 토큰 발급·회전, 원본 보관 기간.
