# 프로젝트 구조

문진 시스템 워크스페이스의 구조를 한 장으로 정리한 문서다. 리포 13개, 각 리포 안에 무엇이 있는지, 서로 어떻게 연결되는지만 다룬다. 세부 설계와 근거는 `DECISIONS.md`(결정 D01~D74)와 각 리포의 `docs/`에 있다. 폴더 목록은 2026-10-26에 각 리포에서 직접 확인했다.

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
    SS["survey-service<br/>문진 서비스 (LangGraph)"]
    MS["model-serving<br/>추론 서버 (model-runtime)"]
    OF["ops-feedback<br/>수집·비식별·실패 사례"]
  end
  subgraph UI["사람이 쓰는 화면 (정적)"]
    KF["kiosk-frontend<br/>환자 화면 · 직원 콘솔"]
    AC["admin-console<br/>출고 승인 · 실패 사례 검토"]
  end
  subgraph LIB["공유 계약·라이브러리"]
    BC["boundary-contracts<br/>계약 스키마·HTTP 규약·클라이언트"]
    TE["turn-engine<br/>턴 결정 규칙"]
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
| **boundary-contracts** | 영역 사이 계약 (헤드 소유) | `schemas/`(레코드 스키마 24개 + 공통 타입 `_common.schema.json`, 확인: `ls schemas`), `examples/`(스키마별 예시), `boundary_contracts/`(패키지: 검증기·해시 계산·HTTP 클라이언트), `conformance/`(참조 서버), `tests/`, `verify.py`, 문서 `INTERFACES.md` `HTTP.md` `PUBLIC_API.md` `CONVENTIONS.md` `METRICS.md` |
| **turn-engine** | 턴 결정 규칙 (순수 라이브러리) | `turn_engine/`(엔진), `tests/`, `examples/`, `scripts/`, `docs/` |
| **model-runtime** | 추론 런타임과 추론 서버 (vLLM) | `src/`(런타임·서버), `profiles/`(GPU 프로파일), `scripts/`(스모크·GPU 점검), `runs/`(실행 산출물), `Dockerfile`, `requirements-cpu.lock` `requirements-gpu.lock`, `tests/`, `docs/` |
| **survey-service** | 문진 서비스 + 문진 스키마 소유 | `survey_service/`(LangGraph 오케스트레이터·공개 API·세션 저장소·Trace·직원 알림·추론 호출), `schema/`(문진 스키마), `scripts/`(스모크), `tests/`, `Dockerfile`, `requirements.lock`, `docs/` |
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
| 직원 콘솔 | survey-service (게이트웨이 경유) | 알림 목록·SSE·푸시 구독·위험 정지 재개/종료 |
| survey-service | model-serving | 파서·생성기 호출, 릴리스 적재 신호 |
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

## 4. 배포에서의 모양

- `deploy/compose.yaml`이 서비스를 한꺼번에 띄운다: `gateway`, `kiosk-frontend`, `admin-console`, `survey-service`, `question-authoring`, `ops-feedback-ingest`, `release-gate`, `model-serving`, `model-registry`. 이 밖에 일회성 `model-serving-schema`(문진 스키마를 꺼냄)와, 프로파일 `jobs`로 한 번 실행하는 `job-ops-feedback`, `job-release-gate-collect`가 있다(확인: `deploy/compose.yaml`).
- 브라우저는 게이트웨이만 부른다. 게이트웨이(Caddy, `deploy/config/Caddyfile`)가 경로와 사람 계정 역할(`release-approver`, `reviewer`)에 맞춰 서버 토큰을 붙이고 `X-Openit-User`로 사용자를 기록한다.
- 이미지는 digest로 고정(`deploy/locks/images.lock`)하고 레지스트리에 올린다.
- 전체 시험은 `deploy/scripts/e2e.sh`(단계 1~9, 옵션 `--fast` `--reuse-build` `--keep`), 설치는 `deploy/docs/SETUP.md`.

## 5. 확인 수준 (2026-10-26 기준)

- 서비스끼리 실제 HTTP로 도는 전체 시험은 개발 PC에서 87건 통과했다(`deploy/docs/STATUS.md` 여덟째 구간, 전체 모드 87 PASS / 0 FAIL). 모델은 고정 출력 가짜 백엔드이고, 승인자 등 일부는 시험용 대체다.
- 서버(`gpu-dev`, RTX 4070 SUPER 12GB, WSL2의 Docker Desktop 연동)에서 `doctor.sh` 통과와 전체 시험 88 PASS를 사용자가 보고했다(2026-10-26). 리포의 기록 파일에서는 확인하지 못했고, 개발 PC의 87과 1건 차이가 나는 이유도 확인하지 못했다. D47("Docker 없음", 2026-10-15)은 그 시점의 사실이고 이후 바뀌었다.
- 실제 LLM 데모(D72): gpu-dev에서 vLLM(Qwen2.5-1.5B + 중립 LoRA)으로 문진 응답이 나오는 것을 확인했다(2026-10-26). survey-service의 릴리스 적재 재시도 수정(8e0ba7e)과 deploy `llm-demo`가 main에 병합됐다. 응답 품질은 학습 전이라 판단하지 않는다.
- 구조 방향(D74, 2026-10-27): 학습 데이터셋 v2에 맞춰 정규화·절차·다음 문항을 LoRA-A가 하고 서비스는 표 찾기만 한다. 이 문서의 위 그림과 표는 아직 v1(파서·정규화기·판정기·Plan 코드) 기준이다. 구현이 끝나면 고친다. 영향 목록은 `impact-d74.md`.
- 계약 패키지 현재 태그는 `v1.3.3`(`git -C boundary-contracts tag`).
- 실제 브라우저 화면, 한국어 음성 인식, 웹 푸시 수신, RTX 4090 실측은 확인하지 못했다.
- 미정: 운영 도메인·HTTPS, 직원 콘솔 로그인, CI가 서버 레지스트리에 닿는 방법, 토큰 발급·회전, 원본 보관 기간.
