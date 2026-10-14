# 진행 상태

세션은 새 컨텍스트로 시작하므로, 맥락은 이 파일로 넘긴다. 세션을 끝낼 때 이 파일을 갱신한다.

## 현재 단계

구조 확정 단계. 구조의 골격(D01~D12)은 확정했고, 경계 계약을 스키마로 쓰기 전에 닫을 열린 결정(O01~O07)이 남아 있다.

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
- 2026-10-15: model-runtime 에이전트가 I9를 FakeBackend로 구현(테스트 16개 통과, 커밋 전). 헤드 답변: D34(해시 기준 구현을 boundary-contracts에 둠, RFC 8785 벡터 테스트 8개 통과), D35(schema_dir 호출자 전달, vLLM 잠정). 세션 간 메시지는 SendMessage로 직접 조율. 환경: pip·GPU 없음(python3-pip, python3-venv 설치 필요)
- 워크스페이스 루트 `CLAUDE.md`는 `head/shared/CLAUDE.root.md`의 링크. 공통 규칙에 `../survey-service/schema` 읽기 허용을 추가

- 전체 설계서 작성(`ARCHITECTURE_FULL.md`, 내보낸 파일)
- 구조 골격 확정(`DECISIONS.md`의 D01~D12)
- 스타터 킷 생성(2026-10-14)

## 다음 작업(순서)

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

- 계약(경계 계약 세트, 공통 규약)은 사용자와 논의하며 쓴다. 논의 전에는 쓰지 않는다. 계약이 확정되면 브리프 9개의 계약 상태 안내문을 갱신해 다시 전달한다.
- 사용자가 영역 리포지토리의 내용은 맡기지 않았다. 헤드는 구조와 계약, 연결을 맡는다.
- 점검에서 나온 확인 사항: TurnTrace에 릴리스 ID가 없음(런타임 정수 버전을 올리고 optional로 추가, D14), turn-engine·model-runtime에 에이전트를 붙여야 함, SDK 공통 형태(인증·오류·불변 버전 읽기)를 공통 규약에 넣을 것.
- HANDOFF.md의 리포지토리 수를 10개에서 11개로 정정함(D04와 STRUCTURE.md 기준).
