# 문진 시스템 개요 (팀 공유용 입구)

기준일 2026-10-28. 이 문서는 **새로 설명하지 않고 모으기만 한다.** 각 영역의 설명은 그 영역의 `README.md`가 정본이다. 확인은 이 PC와 gpu-dev(둘 다 WSL2 + Docker Desktop) 두 환경에서 했다. 깨끗한 일반 리눅스 서버에서는 확인하지 못했다(U06, U12).

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
| model-runtime | 두 모델(LoRA-A 추출, LoRA-B 응답)을 불러 호출하는 라이브러리 겸 추론 서버 | [README](../../model-runtime/README.md) | v0.7.3 |
| survey-service | 환자 발화 한 턴을 받아 저장값으로 바꾸고 다음 말을 돌려주는 HTTP 서비스 | [README](../../survey-service/README.md) | main |
| release-gate | 문항 세트와 모델 조합을 검사하고 사람이 승인한 조합만 릴리스로 묶는 서비스 | [README](../../release-gate/README.md) | main |
| ops-feedback | 운영 중 trace를 받아 개인정보를 지우고 실패 사례를 가려내는 영역 | [README](../../ops-feedback/README.md) | main |
| question-authoring | 의료인이 올린 문항 자료를 검토·확인해 바꿀 수 없는 문항 버전으로 저장하는 서비스 | [README](../../question-authoring/README.md) | main |
| model-lab | 어댑터를 모델 패키지로 묶어 보관·제공(model-registry), 학습 서버 코드 감싸기 | [README](../../model-lab/README.md) | main |
| synthetic-data | 학습·검증 데이터를 만들어 게시하는 run-once 잡(역할은 결정 대기, G02) | [README](../../synthetic-data/README.md) | main |
| deploy | 여러 영역의 이미지를 한 서버에 묶어 띄우고 되돌리고 끝에서 끝까지 시험하는 영역 | [README](../../deploy/README.md) | main |
| kiosk-frontend | 환자용 키오스크 화면과 직원 콘솔 화면 | [README](../../kiosk-frontend/README.md) | 계약 v2.0.2 |
| admin-console | 출고 승인과 실패 사례 검토 화면 | [README](../../admin-console/README.md) | 계약 v2.0.2 |

서비스 영역의 기준 버전 `main`은 계약 v2.0.2, turn-engine v0.4.0, model-runtime v0.7.3에 맞춰져 있다. `deploy/scripts/check-versions.sh`가 **10개 영역의 28개 표기**가 표와 같은지 확인한다(두 프런트엔드는 오늘 뒤늦게 정렬하고 점검 대상에 넣었다: admin-console은 계약 v1.3.3 기준이라 단위 시험 2건이 실패하고 있었고 고쳐서 42건 모두 통과, kiosk-frontend는 모의 서버의 `pipeline_schema_version`이 "1.0"으로 하드코딩된 것을 고침).

## 4. 지금 확인된 것 (숫자는 주인 문서에서 본다)

사실은 그것을 아는 영역이 한 곳에서만 쓴다. 이 문서는 복사하지 않고 가리킨다.

| 무엇 | 주인 문서 |
|---|---|
| 서비스 사이 연결(가짜 모델 E2E, 이 PC와 gpu-dev 두 환경). **배선만 증명한다**: 모델은 가짜, 승인은 스크립트 | [`deploy/docs/E2E_RESULTS.md`](../../deploy/docs/E2E_RESULTS.md) |
| 장애 상황(서비스 중지·멈춤, DB 중지·멈춤, 모델 서버 멈춤)에서 환자 턴이 어떻게 끝나는가 | [`FAULT_POLICY.md`](FAULT_POLICY.md)(기준), [`FAULT_MATRIX.md`](FAULT_MATRIX.md)(칸별 정의·시험 여부, 분모 포함), E2E 단계 5q·5w·5p·5m·5u |
| 보안·개인정보·운영·배포·구조 근거를 표준 체크리스트로 점검한 결과 | [`AUDIT_CHECKLIST.md`](AUDIT_CHECKLIST.md), [`AUDIT_SUMMARY.md`](AUDIT_SUMMARY.md), 영역별 원문 `audit/*.md` |
| 구조 선택의 '왜'(저장소·프로토콜·한도·보존·인증 등) | 영역마다 `docs/adr/`(영역 README가 목록 링크), 시스템 수준은 [`adr/`](adr/README.md). 규칙은 D89 |
| 영역마다 자기 시험이 통과하는지 | 각 영역 README의 "현재 상태" 절 ([영역 지도](#3-영역-지도)의 링크) |
| 계약·turn-engine·model-runtime 버전이 영역 사이 일치하는지 | `deploy/scripts/check-versions.sh`, 기준표는 `deploy/scripts/lib.sh` |
| 영역 사이 정적 일관성(10규칙) | `deploy/scripts/check-all.sh` (규칙별 검증됨/대상 아님/검증 안 함 분모가 나온다) |
| 영역 하나가 바뀌었을 때 전체 E2E 없이 확인하는 법 | `deploy/scripts/verify-area.sh <영역>` (영역→E2E 단계 대응표 `deploy/config/verify-areas.yaml`) |
| 비밀이 컨테이너 환경 변수로 읽히지 않는지, 컨테이너가 비root·읽기 전용인지 | `deploy/scripts/check-secrets-hidden.sh`, `deploy/scripts/check-containers.sh` |
| 서빙 프롬프트와 학습 데이터의 글자 일치, 서비스 표·값 검증이 실제 학습 데이터에서 정답을 거부하는지 | [`OPEN_GAPS.md`](OPEN_GAPS.md) U03, G02, G03, G13 (2026-10-28 학습 서버의 최종 데이터 C1 전체 대조) |
| 실제 LLM이 12GB GPU에 올라가는지, 출력 형식 | [`OPEN_GAPS.md`](OPEN_GAPS.md) U01, U04, U07 (gpu-dev 측정 기록) |
| 실제 GPU(openit 서버)를 짧은 시간에 안전하게 쓰는 키트 | [`model-runtime/docs/GPU_SESSION.md`](../../model-runtime/docs/GPU_SESSION.md) |
| 키오스크 화면 브라우저 시험(컨테이너) | [`kiosk-frontend/README.md`](../../kiosk-frontend/README.md) |

## 5. 아직 안 되는 것

- **실제 GPU와 학습된 모델로 환자 한 턴.** 가짜 모델 E2E는 배선을 증명한다. 모든 시간 한도(턴 마감, 모델 서버 상한, 소켓·연결 한도)는 **측정 없는 초기값**이고 24GB급 실측(H1~H4) 뒤 다시 정해야 한다. 키트와 절차는 준비됐다. openit 서버의 GPU는 데이터셋 담당의 증강 작업이 점유 중이라 쓰지 못했다.
- **실제 기기**: 마이크·한국어 온디바이스 음성 인식·웹 푸시, 일반 리눅스 서버 설치(U05, U06, U12).
- **학습 데이터와 담당 확정**: `labels.py`를 B 입력의 기준으로 담당이 확정했는지(G03), 합성 데이터 게시기를 실제 데이터에 쓰도록 담당이 허락했는지(G02).
- **알려진 한계와 그 이유**는 [`OPEN_GAPS.md`](OPEN_GAPS.md) 3-0절(L01~L18)에 한 표로 있다. 코드로 안 닫은 것(로그인 속도 제한, 취약점 스캔, 서비스 간 TLS 등)과 병원 정보가 필요한 값(도메인·인증서, 보존 규정, 위험 문구의 임상 검토)을 구분한다.
- **전수 점검의 범위**: 점검은 체크리스트 63항목 안에서만 완전하다. 영역마다 '확인 못 함'이 남아 있고(점검 보고 참고), 이 목록 밖의 문제는 보장하지 않는다.

## 6. 열린 항목 수

[`OPEN_GAPS.md`](OPEN_GAPS.md) 기준. 상태별 개수는 이 문서에 적지 않는다(표마다 열 구성이 달라 세면 틀린다). 대장의 각 행이 상태를 갖는다. **"완료"가 아니라 "N건 열림"이다.**

## 7. 역할 분배 제안

코드는 헤드(에이전트)가 짠다. 팀원은 **입력을 주고, 결정하고, 서버·접근을 열고, 내용을 확정하는 일**을 맡는다. 프레임워크는 사용자 포함 3명이고, 학습(LoRA-A, LoRA-B)과 데이터셋 증강 담당 3명은 이미 자기 일이 있어 부탁만 한다. 누구에게 줄지는 사용자가 정한다. 값은 모두 잠정 기본값이라(D88) 병원 정보가 오면 설정만 바꾼다.

| 담당 | 사람이 할 일 | 코드 완성 뒤에 할 일 |
|---|---|---|
| **A: 서빙·인프라** | 24GB급 GPU를 쓸 수 있는 시간대 확보(openit은 증강 작업이 점유 중), 운영 도메인과 인증서 방식 결정(내부 CA 기본, [`deploy/docs/runbook.md`](../../deploy/docs/runbook.md) 9절), 백업 대상(서버 밖)과 복호 키를 서버 밖에 2곳 이상 보관(runbook 4절. **키를 잃으면 백업을 복구할 수 없다**) | 깨끗한 리눅스 서버에서 문서대로 설치 확인(U06, U12), 내부 CA 루트를 키오스크·직원 PC에 배포 |
| **B: 서비스·화면** | 위험 문구 기본 목록(`provisional`)의 임상 검토, 직원 호출 기준, 환자 대체 문구, 재질문·유휴 초기화·재시도 값의 현장 적합성(U10) | 실기기에서 마이크·음성 인식·푸시 확인(U05), 승인·검토 화면을 승인자 입장에서 써 보기 |
| **사용자: 결정과 창구** | **D92 확인**: 임상 승인을 저자≠검수자(4-eyes)로 바꿨다(이전 D30은 저자의 확인이 임상 승인). 의료인이 한 명뿐이면 막히므로 `QA_REQUIRE_TWO_PERSON=false`로 되돌릴 수 있다. 보존 기간(원본 30일, 세션 90일, 사례 180일, 백업 14일은 잠정), 확정 사례를 180일 뒤 지울지, 접수 연동 방식(환자마다 참조값이 오는가), 병원 연동, 외부 STT 허용 여부(기본 꺼짐) | — |
| **학습·데이터셋 담당(부탁)** | `labels.py`를 B 입력 기준으로 확정, 최종 데이터(C1)를 서비스 검증에 써도 되는지, 학습 서버 스크립트 해시 값 채우기 | 새 학습 결과의 어댑터 쌍과 시스템 프롬프트·run 기록 위치 알리기 |

**헤드가 짠 코드(만들어서 확인함)**: 이전 목록에 더해, 장애 정책 구현(턴 마감·멱등·게이트웨이 503/504·키오스크 재시도), 위험 감지 fail-safe, 기기별 토큰, 4-eyes, 보존 잡, 백업·복원, TLS, 영역별 빠른 검증 스크립트, GPU 세션 키트.

제품이 완성된 뒤의 일: 실제 GPU에서 학습된 어댑터로 한 턴 통과와 시간 한도 재정(H1~H3, [`deploy/docs/GPU_HOLE.md`](../../deploy/docs/GPU_HOLE.md)).

## 8. 문서 지도 (head/docs)

| 문서 | 무엇인가 | 누가 읽나 |
|---|---|---|
| 이 문서 `OVERVIEW.md` | 입구. 영역 지도, 상태, 역할 분배 | 모두 |
| 영역별 `README.md` | 그 영역의 정본 설명 | 모두 |
| [`OPEN_GAPS.md`](OPEN_GAPS.md) | 비워 두었거나 확인하지 못한 것, 알려진 한계(L01~L18)의 대장 | 모두 |
| [`DECISIONS.md`](DECISIONS.md) | 확정한 결정(D01~D92)과 근거 보강 | 결정 근거가 필요할 때 |
| [`adr/`](adr/README.md) | 시스템 수준 구조 결정의 '왜'(영역 내부 결정은 각 영역 `docs/adr/`) | 구조 근거가 필요할 때 |
| [`FAULT_POLICY.md`](FAULT_POLICY.md), [`FAULT_MATRIX.md`](FAULT_MATRIX.md) | 장애 대응 기준과 칸별 확인 표 | 장애 대응을 다룰 때 |
| [`AUDIT_CHECKLIST.md`](AUDIT_CHECKLIST.md), [`AUDIT_SUMMARY.md`](AUDIT_SUMMARY.md), `audit/` | 전수 점검 기준·종합·영역별 원문 | 점검 결과가 필요할 때 |
| [`STATUS.md`](STATUS.md) | 진행 기록 | 헤드 |
| [`COMPLETION_PLAN.md`](COMPLETION_PLAN.md) | 완성까지의 작업줄기와 GPU 구멍 | 헤드, 계획 확인 |
| [`STRUCTURE.md`](STRUCTURE.md) | 에이전트용 구조 요약이자 영역 작업의 기준 | 에이전트 |
| [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) | 사람용 구조 설명(턴 도식, 소유와 의존 방향) | 사람 |
| [`architecture.md`](architecture.md) | 흐름·시퀀스·상태·배포 도식(790줄) | 상세가 필요할 때 |
| `E2E.md`, `HANDOFF.md`, `impact-d74.md`, `migration-2.0.0.md`, `metrics-v2-proposal.md`, `dataset-requests.md` | 시험 시나리오, 인수인계, 변경 지시서·제안 | 해당 작업자 |

`STRUCTURE.md`, `PROJECT_STRUCTURE.md`, `architecture.md`는 내용이 겹친다. 하나로 합칠지는 정하지 않았고, 우선은 위 표처럼 역할만 구분해 둔다.

## 9. 문서 정리 결과와 남은 것

영역들이 README를 쓰며 찾은 낡은 문서는 영역 쪽에서 고쳤고, 오늘 전수 점검에서 나온 문서 불일치도 영역 에이전트가 고쳤다. 남은 것은 코드나 헤드의 판단이 필요한 것이다.

| 남은 것 | 이유 | 누가 |
|---|---|---|
| turn-engine CR-010(QuestionBank에서 표를 만드는 변환 함수), `docs/rules/` 삭제 여부 | 헤드 결정 | 헤드 |
| I2(DatasetStore)를 HTTP로 정할지 | 계약 설계 결정 | 헤드 |
| `METRICS.md` v1 지표 | [`metrics-v2-proposal.md`](metrics-v2-proposal.md) 참고 | 헤드 + 학습 담당 |
| `STRUCTURE.md`, `PROJECT_STRUCTURE.md`, `architecture.md` 겹침 | 합칠지 결정 안 함 | 헤드 |
| synthetic-data v1 생성 경로 삭제(D91) | 시드 경로 분리 뒤 | synthetic-data |
