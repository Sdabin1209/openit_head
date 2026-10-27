# 진행 상태

세션은 새 컨텍스트로 시작하므로, 맥락은 이 파일로 넘긴다. 세션을 끝낼 때 이 파일을 갱신한다.

## 현재 단계

(2026-10-26 갱신. 근거는 각 항목에 적었다. 이전 문구 "구조 확정 단계"는 2026-10-14 시점이라 낡았다.)

- 리포 13개가 모두 있다(`ls`: head, boundary-contracts, turn-engine, model-runtime, survey-service, question-authoring, synthetic-data, model-lab, release-gate, ops-feedback, deploy, kiosk-frontend, admin-console). 결정은 D71까지 기록했다(`DECISIONS.md`).
- 경계 계약 패키지는 `v1.3.3`이다(`git -C boundary-contracts tag`, `pyproject.toml` version 1.3.3). 파이프라인 스키마 버전은 1.3, 문진 스키마는 정수 1(`survey-schema-v1.0.0`). turn-engine `v0.2.0`, model-runtime `v0.5.1`.
- 서비스끼리 실제 HTTP로 도는 전체 시험(`deploy/scripts/e2e.sh`)은 개발 PC에서 87 PASS / 0 FAIL(`deploy/docs/STATUS.md` 여덟째 구간, 모델은 가짜 백엔드).
- 서버 검증 완료(사용자 보고, 2026-10-26): gpu-dev에서 `doctor.sh` 통과, 전체 시험 88 PASS. gpu-dev는 Docker Desktop 연동으로 Docker를 쓴다(D47의 "Docker 없음"은 이후 변경됨). 리포 기록으로는 확인하지 못했다.
- 남은 일(확인하지 못했거나 미정, 자세한 목록은 `architecture.md` 11절): 운영 도메인·HTTPS, 직원 콘솔·사람 계정의 운영 로그인, CI가 서버 로컬 레지스트리에 닿는 방법, 토큰 발급·회전, 주기 잡의 실행 주기(`config/jobs.yaml`의 `interval_seconds`가 모두 null), 백업 설정과 외부 감시, 원본 로그 보관 기간, 롤백 기준과 실패 유형 분류체계, 실제 브라우저 화면·한국어 STT·웹 푸시 수신, RTX 4090 실측과 GPU 모델 E2E(`E2E_GPU=1` 미검증), 문진 스키마 v2 후보 정리, 문항 저작 화면.

## 완료

- 2026-10-14: `contracts`(HealthCheckSchema) 읽음. 문진 서비스 런타임 계약만 있는 일부 스키마임을 확인(신규 계약 10개는 모두 이 저장소 밖). 계약 버전은 정수 하나(`manifest.yaml`)
- 2026-10-14: D13(O01 닫음), D14(O02 닫음, 계약 버전 체계 분리) 기록
- 2026-10-14: 영역 리포지토리 6개와 turn-engine, model-runtime, deploy를 `scripts/new-area.sh`로 생성. 브리프 9개를 `briefs/`에 쓰고 각 리포의 `docs/brief.md`로 배치(계약 필드와 SDK 시그니처는 미정으로 표시)
- 2026-10-15: D19(contracts는 문진 서비스 스키마, 영역 사이 계약은 새 리포지토리 `boundary-contracts`), D20(경계 계약 세부), D15~D18 기록. `boundary-contracts`에 ReleaseManifest, GateDecision, TraceEnvelope 초안과 `verify.py`(통과)
- 2026-10-15: D21(문진 스키마 변경은 survey-service가 반영), D22(컨테이너화·개발 규약)를 기록하고 공통 규칙에 반영
- 2026-10-15: D23(문진 스키마를 `survey-service/schema/`로 이동, setup.sh·README·브리프 경로 갱신), D24(로컬 레지스트리, O17 닫음). Docker는 WSL에서 `docker.exe`로 동작(29.2.0)
- 2026-10-15: `boundary-contracts`에 경계 계약 11개 전부 초안 작성, `verify.py` 통과(예시 12개, 위반 거부 13건). D25 기록. 사용자 논의 전이므로 확정이 아니다
- 2026-10-15: 사용자가 계약 논의 생략과 "영역을 블랙박스로 개발할 수 있게 명시"를 요구. `boundary-contracts`에 `CONVENTIONS.md`, `INTERFACES.md`(I1~I10), 스키마 5개(BoundaryError, IngestResult, GateSubmission, ActivePointer, RollbackReceipt)와 모든 레코드의 `ext` 추가, 브리프 8개에 경계 명세 절 추가. D26, D27
- 2026-10-15: D28. 문진 스키마를 최소 구성으로 정리(`survey-service/schema`: schemas/ 23개, COMPONENTS.yaml, CONTRACT_VERSION). 브리프의 읽기·버전 안내 갱신. 모든 리포지토리는 새로 만들며 이름은 openit_<디렉터리 이름>. 
- 2026-10-15: D29. 문진 스키마를 survey-service 리포지토리에 포함시킴(중첩 .git과 .gitignore 제거). 리포지토리는 다시 11개
- 2026-10-15: `head/workspace.yaml`(11개 리포, openit_<디렉터리>), `head/setup.sh`(링크 + clone, 원격 없을 때 목록 보고 확인함), `head/README.md` 작성. 루트의 킷 파일 `setup.sh`, `README.md` 삭제(head로 흡수). head를 git init(커밋 없음)
- 2026-10-15: D30(O12 닫음: 저자=의료인 신뢰, 저자 확인이 임상 승인), D31(O15 닫음: 문항 자료 파싱은 필수, 미리보기로 저자 확인), D32(보지 못한 문항 평가와 일반화), O18(문항 자료 형식) 신설. DatasetManifest에 files[].question_sets(선택) 추가. 브리프 4개 갱신
- 2026-10-15: D33(O18 닫음: 지원 형식을 정하지 않고 "가져온 문항을 등록할 수 있다"가 요구, 항상 화면 입력으로 폴백). 남은 사용자 결정은 O06, O11, O16
- 2026-10-15: 10개 리포지토리를 main으로 첫 커밋하고 SSH 원격(git@github.com:Sdabin1209/openit_*)에 push(모두 비공개). 커밋 작성자는 Sdabin1209 <99588729+Sdabin1209@users.noreply.github.com>(noreply 주소)로 고쳐 쓰고 force push함. turn-engine은 원격 생성 뒤 `git push -u origin main`만 남음. workspace.yaml·setup.sh는 SSH 주소 사용
- 2026-10-15: model-runtime 에이전트 시작(파일럿). 에이전트 질의에 헤드가 답함: INTERFACES I9에 expected_serving_config_hash 강제, validate_serving_config, serving_config_hash 추가, 어댑터에는 버전 기록 없음, 재시도는 시드만 변경. 변경 요청 없이 헤드가 직접 반영(boundary-contracts 로컬 커밋, push 전)
- 2026-10-15: model-runtime 에이전트가 I9를 FakeBackend로 구현(테스트 16개 통과, 커밋 전). 헤드 답변: D34(해시 기준 구현을 boundary-contracts에 둠, RFC 8785 벡터 테스트 8개 통과), D35(schema_dir 호출자 전달, vLLM 잠정). 세션 간 메시지는 SendMessage로 직접 조율. 환경: GPU 없음. pip·venv는 설치됨(2026-10-15)
- 2026-10-15: model-runtime 26개 테스트 통과·커밋(fbe0460). 헤드 답변: D36(출력 보호: 규칙이 정한 대체 출력, 모델은 is_fallback을 채우지 않음, *_raw 제공), I9 개정(schema_dir 단일화, configure 금지). 파서 대체 출력과 생성기 규칙 원문을 model-runtime에 전달
- 2026-10-15: 사용자가 목표를 명확히 함(D38: 실제로 쓸 시스템을 모델 성능 제외하고 제대로, 모델 학습은 설정으로 반복 가능한 파이프라인), D39(자동화는 저장소를 보고 일하는 멱등 잡, 스케줄러는 deploy). docs/E2E.md에 합격 시나리오 9단계. 브리프 5개와 공통 규칙에 반영. 이전에 제안한 "느슨한 정책·스텁"은 철회
- 2026-10-15: model-runtime 파일럿 구간 완료(GPU·실제 백엔드 제외): 헤드가 pytest 61개 통과와 커밋 확인. 변경 요청 001 처리, 보호 정책 protect-1(잠정 문구는 사용자 확인 대기), D40(서빙·학습 서버 분리 가정). 교훈: 업무 규칙 문서(원본 HealthCheckSchema의 work/rules)는 영역이 시작하기 전에 필요한 것을 헤드가 전달해야 한다. 영역별 규칙 대응은 아래 메모 참조
- 2026-10-15: question-authoring(pytest 111·스모크 OK), ops-feedback(85), release-gate(112, 2 skip) 첫 구간 완료를 헤드가 직접 확인(pytest, 스모크, 작성자). 변경 요청 17건 처리: D42, boundary-contracts 1.0.0 태그·push. 스모크 시험 고정 포트 충돌(병렬) 규약화. 남은 것: synthetic-data, turn-engine 보고 대기. 새 열린 결정 O19(비식별 뒤 발화 보존)
- 2026-10-15: ops-feedback 후속 작업 확인(pytest 85, 스모크 OK, 포트 자동 배정) 후 push(헤드 허락, D41). 남은 후속: question-authoring, release-gate
- 2026-10-15: question-authoring(114)·release-gate(118/2skip)·ops-feedback(85) 후속까지 확인 후 push. synthetic-data(83, 잡 재현 확인) 변경 요청 5건 처리: boundary-contracts 1.1.0(D43). synthetic-data·ops-feedback 후속 지시. 남은 보고: turn-engine, synthetic-data·ops-feedback 후속. 기술 부채: boundary_contracts.validator가 jsonschema RefResolver(폐기 예고)를 씀
- 2026-10-15: turn-engine 첫 구간 보고(329 passed, 변경 요청 8건). 원본 semantics로 CR-003(위험 표현 안전망: 발화에 risk_phrases가 들어 있으면 맞은 표현을 근거로 risk_signal, 케이스 G2·G9·S3c) 등 결정. 원본 요구사항 케이스의 입출력 쌍 209개를 turn-engine/tests/golden에 전달(해석 갈림을 가리는 정답 예시). synthetic-data 후속(86)·ops-feedback 1.1 반영(91) 확인·push. 남은 것: turn-engine 후속 보고, 이어서 survey-service 시작. 같은 golden의 파서·생성기 쌍은 synthetic-data·model-lab·model-runtime용으로 따로 전달할 것
- 2026-10-15: turn-engine v0.2.0(1205 passed, golden 806/868, 위험 표현 안전망 직접 확인)·model-runtime v0.2.0 태그 push. golden을 survey-service·synthetic-data·model-lab·model-runtime에 전달(D44). survey-service 시작(사용자 승인). 사용자에게 올릴 것: golden 예시 오류 37건(CR-009), 설계서 9-2절 효과표, 비식별 O19. 알림 규칙을 어긴 일 있음 → 완료·결정 필요 시 Discord+소리 필수
- 2026-10-15: survey-service 첫 구간 확인(148 passed, 스모크 OK, golden 1215/1220, 불일치는 예시 오류 5). 변경 요청 결정 D45(I9 역할별 설정, model-runtime 0.3.0 진행)·D46(릴리스 적재 거부 정책, ID 변환, 스키마 v2 후보 모음). bindings.yaml 등 입력 출처 표를 survey-service에 전달. 후속: survey-service(bindings 대조·정책), model-runtime 0.3.0. 그 뒤 deploy 시작 가능. survey-service는 아직 push 전(후속 뒤에 push)
- 2026-10-15: survey-service 후속 확인(pytest 통과, 스모크 OK, 라벨 model-runtime v0.3.0·turn-engine v0.2.0·boundary v1.1.0) 후 push, 태그 survey-schema-v1.0.0(문진 스키마 패키지, 설치: git+ssh://git@github.com/Sdabin1209/openit_survey-service.git@survey-schema-v1.0.0#subdirectory=schema). model-runtime v0.3.0(D45). 완료 영역: model-runtime, turn-engine, question-authoring, ops-feedback, release-gate, synthetic-data, survey-service. 남은 것: deploy(시작 가능), model-lab(GPU 서버 필요)
- 2026-10-15: gpu-dev 접속 확인(RTX 4070급 12GB, 12코어, RAM 15GB, 디스크 954GB, Ubuntu 24.04 WSL2, Python 3.12, pip·Docker 없음, HF·PyPI 접속 가능, GitHub SSH 불가). D47(사용 규칙). 사용자 조치 필요: gpu-dev에 python3-pip·python3-venv 설치(sudo). model-lab 시작, model-runtime vLLM 시험 지시
- 2026-10-15: model-runtime vLLM 시험 완료(pytest 81, GPU 확인: LoRA+구조화 출력, 한계: allOf/if/then/not 무시). D48(vLLM 확정, 어댑터 PEFT 형식, 재현성 범위). 후속: rank 사전 검사, 0.4.0 태그. deploy 시작(사용자 허락: 관리 여유가 되면). 실행 중: model-lab, deploy
- 2026-10-15: deploy 첫 구간(E2E 62 PASS, 1·4a·6수집·8a·9 실제, 3 대신, 나머지 막힘). 막힘의 원인: 영역끼리 이어지는 원격 클라이언트·읽기 면 없음(CR-D01). D49(영역 사이 호출은 HTTP, HTTP.md, boundary_contracts.clients), D50(SQLite 볼륨 소유 서비스만, 이웃은 HTTP, 라벨 통일, O10 닫음). 진행: 클라이언트 라이브러리(v1.1.1 예정), 각 영역 서버 읽기 면. 열린 것: D08 모델 추론 GPU의 서빙 서버 위치(사용자 확인)
- 2026-10-15: model-lab 완료 확인(pytest 61, GPU 실제 학습·평가·패키징·게시 한 바퀴: Qwen2.5-1.5B 4비트 r=16 3스텝, 어댑터 PEFT), push. release-gate 후속(135, 스모크 OK) push. boundary-contracts v1.2.0 태그·push(클라이언트 6종 + 읽기 관대 모드 + base_model.id 완화, D51). 다음: 소비 영역이 v1.2.0·클라이언트로 전환, deploy가 연결·E2E 재실행. 확인 못 한 것: model-lab의 재개 결정성
- 2026-10-15: deploy 재검증(E2E 직접 재실행: PASS 전부, FAIL 0, 정리 완료, 남은 컨테이너 없음) 후 push. 소비 영역 전환 지시(v1.2.0·클라이언트): survey-service, synthetic-data, ops-feedback, question-authoring, release-gate, model-lab(진행). 이후 deploy가 연결·E2E 재실행
- 2026-10-15: deploy E2E 직접 재검증(73 PASS/0 FAIL, 정리 완료). 소비 영역 v1.2.0 전환과 D52(ops-feedback 검토 POST, release-gate 정책 스키마·실행기 규약·운영 모드 거부, model-lab 회귀 평가·파일 저장소, question-authoring 개선 신호) 모두 확인·push. deploy 재실행 지시. 발견: 비식별 기본이 자유 문자열 전부 마스킹이라 환류가 구조 수준(O19 권고안 B 기록). 사용자 결정 대기: O11, O06, O16, O19, 서빙 GPU 추론 위치와 GPU 서버 접근, 도메인·TLS·외부 감시·스케줄 주기, 정답 예시 오류 검토
- 워크스페이스 루트 `CLAUDE.md`는 `head/shared/CLAUDE.root.md`의 링크. 공통 규칙에 `../survey-service/schema` 읽기 허용을 추가

- 전체 설계서 작성(`ARCHITECTURE_FULL.md`, 내보낸 파일)
- 구조 골격 확정(`DECISIONS.md`의 D01~D12)
- 스타터 킷 생성(2026-10-14)

## 다음 작업(순서)

(2026-10-14 시점의 계획이다. 현재 단계는 위 "현재 단계"를 따른다.)

1. 경계 계약과 명세는 확정 상태(사용자가 논의 생략). 변경은 `CONVENTIONS.md`의 진화 규칙 안에서만 한다.
2. 영역 에이전트를 시작할 준비가 끝났다. 시작은 사용자 지시 후.
2. (완료) contracts 읽기와 STRUCTURE.md 점검. 어긋난 곳은 메모 참조.
4. O06은 Frontend 팀과의 협의 항목으로 따로 정리한다.
5. 경계 계약 세트를 JSON Schema로 쓴다. TurnTrace의 릴리스 ID 필드 추가, ReleaseManifest, GateDecision을 먼저 확정하고 나머지 신규 계약 7개를 잇는다.
6. 공통 규약(오류 분류, ID·버전 규칙, 시간·인코딩, 턴 ID 추적, 인증)을 쓴다.
7. 영역 브리프를 쓰고(`briefs/`), `scripts/new-area.sh`로 영역 리포지토리를 만들고, 브리프를 `docs/brief.md`로 배치한다.
8. 모델 영역의 도메인 정의(지표, 통과 임계치, 평가셋 구성, 실패 유형 분류체계)는 사용자와 함께 정한다(O11).

## 진행 중인 것

없음

## 메모

- 업무 규칙 문서 전달 계획(원본 HealthCheckSchema `work/rules/`, 읽기만 했고 영역 시작 때 해당 영역 `docs/rules/`로 전달): turn-engine = answer_normalizer, answer_judge, record_writer, dialogue_planner, preconditions, mapping, principles, timing / survey-service = orchestrator, session_store, timing, trace_contract / synthetic-data·model-lab = utterance_parser(라벨 기준), response_generator / model-runtime = 전달 완료(파서 대체 출력, 생성기 규칙). question-authoring과 release-gate는 해당 규칙을 먼저 확인할 것.

- 계약(경계 계약 세트, 공통 규약)은 사용자와 논의하며 쓴다. 논의 전에는 쓰지 않는다. 계약이 확정되면 브리프 9개의 계약 상태 안내문을 갱신해 다시 전달한다.
- 사용자가 영역 리포지토리의 내용은 맡기지 않았다. 헤드는 구조와 계약, 연결을 맡는다.
- 점검에서 나온 확인 사항: TurnTrace에 릴리스 ID가 없음(런타임 정수 버전을 올리고 optional로 추가, D14), turn-engine·model-runtime에 에이전트를 붙여야 함, SDK 공통 형태(인증·오류·불변 버전 읽기)를 공통 규약에 넣을 것.
- HANDOFF.md의 리포지토리 수를 10개에서 11개로 정정함(D04와 STRUCTURE.md 기준).

## 진행 기록 (2026-10-26 갱신)

- 구현·검증: 리포 13개, 계약 v1.3.3. 개발 PC에서 전체 시험 87건, 서버(gpu-dev)에서 88 PASS / 0 FAIL(옵션 없이 처음부터).
- 서버 설치 정리(D62 이후): WSL 전용 분기·자격증명 우회를 모두 제거하고 표준 docker 경로만 쓴다. 사전 점검 `deploy/scripts/doctor.sh`, 설치 문서 `deploy/docs/SETUP.md`, 실행 안내 `deploy/docs/RUN.md`, 수명주기 `down.sh` `status.sh`, 사람이 써 보는 `demo.sh`.
- 지금 진행 중: **데모에 실제 LLM**(D72, D73). ① model-runtime: 작은 GPU 프로파일, 효과 없는 LoRA 패키지 생성 도구, 단독 실행 안내(코드·테스트·문서까지). ② deploy: 추론 서버 외부 주소 모드·단독 추론 서버 컴포즈·위치 독립 시험(작업 16). ③ 그다음: 서버에 GPU 이미지(약 13GB)를 내려받아 `demo.sh up --llm`을 연결하고 서버에서 확인.
- 확인 못 한 것: 실제 브라우저(화면·음성 인식·웹 푸시 수신), RTX 4090 실측, 일반 리눅스 서버(WSL이 아닌 곳)에서의 설치, GPU 컨테이너의 서버(gpu-dev) 실행.
- 미정: 운영 도메인·HTTPS, 직원 콘솔 로그인, CI가 서버 레지스트리에 닿는 방법, 토큰 발급·회전, 원본 보관 기간, 금지 표현 목록 없음(D59).
- 사용자 지침(반복해서 지적됨): 꼼수·우회 금지, 표준 경로, 환경별 분기 금지(D62 이후 정리). 질문 전 알림, 5분 넘는 작업은 직접 붙잡지 않기, 작업 단위는 짧게, Artifact 금지(문서는 md), 자잘한 판단은 헤드가 한다.

## 진행 기록 (2026-10-27)

- 서버 실제 LLM 데모 성공(2026-10-26 밤): survey-service 로더 재시도 수정(8e0ba7e)과 deploy `llm-demo`(f76a94b)를 main에 병합·push했다. 응답은 실제 vLLM이 냈다. 다만 시작 응답이 "죄송합니다, 도와드리기 어렵습니다."였다(학습 전 모델과 입력 형식 불일치로 추정, 확인하지 못함).
- 학습 서버(`openit`)를 탐색했다(읽기 전용). 최신 학습 데이터셋은 `~/taehyeon/data/dataset_10_14`. 형식은 정규화·절차·다음 문항을 LoRA-A가 하고 서비스는 표 찾기만 하는 v2다. 학습 기반은 Qwen3-4B/8B/14B(rank 16).
- D74: 서비스 구조를 이 데이터셋 v2에 맞춘다. 영향 목록은 `docs/impact-d74.md`(초안). 구현은 아직 시작하지 않았다.
- 다음: 형식 확정(boundary-contracts 새 스키마·예시)부터. 12GB 적재, 두 어댑터 동시 적재, 정규화 담당자의 수정 시점은 미확인.

- 2026-10-27 계약 `v2.0.0` push. 1단계 영역 이전 병합: turn-engine v0.3.0, model-runtime v0.6.0(태그), release-gate, ops-feedback, synthetic-data. model-lab은 브랜치에서 진행 중, survey-service 이전 진행 중. 결정 D75, D76. 지시서 `docs/migration-2.0.0.md`.

- 2026-10-27 D81: `gpu-12g`는 Qwen3-1.7B(파이프라인 데모용). model-runtime v0.6.3(스모크 통과, 태그 push) 후 survey-service(fa86fb7), release-gate(9286300), model-lab(21a05bb), deploy(1f0cb64)를 v0.6.3으로 맞춰 push. deploy E2E 88 PASS / 0 FAIL(헤드가 직접 재실행, 이 PC 한 환경). 확인 못 한 것: gpu-dev에서 Qwen3-1.7B 적재·두 어댑터 동시 적재(U01), 실제 LLM 데모. 다음: gpu-dev 켜서 실제 LLM 데모 → U01/U04/U07 갱신.
