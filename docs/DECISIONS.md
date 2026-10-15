# 결정 기록

결정은 헤드가 사용자에게 권고와 함께 물어 확인을 받은 뒤에만 이 파일에 기록한다. 닫힌 열린 결정은 확정 표로 옮기고 날짜와 사유를 적는다.

## 확정

| ID | 결정 | 내용 |
| --- | --- | --- |
| D01 | 구조 | 영역 7개, 공유 저장소 6개, 계약 패키지 |
| D02 | 소통 방식 | 영역은 저장소로만 통신하고, 저장소마다 쓰는 영역은 하나다 |
| D03 | 게이트 판정 | 조합 단위의 판정(통과·반려)을 릴리스 레지스트리에 GateDecision으로 기록한다. ApprovalRecord와 StatusTransition은 폐기 |
| D04 | 리포지토리 | head 포함 11개(STRUCTURE.md 4절) |
| D05 | 경계 방식 | 소비자는 소유자가 배포한 SDK 인터페이스에만 의존한다. API냐 SDK냐는 네 질문 순서로 고르고 소유자가 바꿀 수 있다 |
| D06 | 공유 라이브러리 | turn-engine과 model-runtime을 분리한다 |
| D07 | 배포 | 코드(이미지 digest)와 내용(릴리스 묶음)을 두 축으로 나누고 각각 되돌린다 |
| D08 | 관리자 콘솔 | question-authoring 안에서 직접 만들고 저작 API의 클라이언트로만 구현한다 |
| D09 | 작업 방식 | 헤드는 경계 계약과 수용 기준을, 영역 에이전트는 내부 설계와 구현을 맡는다. 경계 항목은 구속, 컴포넌트 표와 내부 흐름 그림은 참고 시드다 |
| D10 | 장애 | 서버 전체 중단은 비보증으로 명시하고, 외부 감시로 유지보수 담당에게 알린다 |
| D11 | 배포 환경 | 단일 서버, Docker Compose, 외부 입구는 gateway 하나 |
| D12 | Frontend | 외부 접점이며 다른 팀 담당이다. 경계는 공개 API 명세다 |
| D13 | 모델 평가의 문항 접근 | model-lab은 문항 읽기 SDK에 의존해 문항 정의(QuestionBank)를 읽는다. 문항 유형·단위·범위별로 평가를 쪼개기 위함. 2026-10-14 사용자 확인 |
| D14 | 계약 버전 체계 | 문진 스키마(기존 12개 컴포넌트)는 기존 정수 버전(`CONTRACT_VERSION`, 정확 일치. 원래는 HealthCheckSchema의 `manifest.yaml`)을 유지한다. 경계 계약(신규, 구 "파이프라인 계약")은 `MAJOR.MINOR` 별도 체계로, 같은 MAJOR이고 MINOR가 필요 이상이면 읽기를 허용한다. 레코드는 `pipeline_schema_version`을 적고, ReleaseManifest는 두 버전을 모두 기록한다. 경계 계약의 위치는 D19가 정한다. 2026-10-14 사용자가 헤드에게 판단을 위임. TurnTrace의 릴리스 ID 처리는 D19가 대체. O02를 닫음 |
| D15 | 비식별 처리의 위치 | 비식별 처리기는 ops-feedback 안에 둔다. 문진 서비스는 원본 Trace를 보내기만 하고 비식별하지 않는다. 원본은 비식별 처리기만 읽고, FailureCase는 항상 비식별 뒤에만 만든다. 책임: 원본 보관·비식별·사례 생성은 모두 ops-feedback. 2026-10-14 사용자가 권고 채택을 위임 |
| D16 | Trace 전달 보장 | 최소 1회 전달. 수집 쪽이 (세션 ID, 턴 ID)로 멱등 처리한다. 책임: 전송 재시도는 문진 서비스, 중복 제거는 ops-feedback |
| D17 | 문항 변경 분류 | 문구 / 선택지·단위 / 슬롯 / 분기의 4종으로 시작한다. 추가·변경은 경계 계약 MINOR 변경 절차를 따른다. 분류는 question-authoring이 만든다 |
| D18 | SDK 언어와 배포 | Python 3.10 이상. 배포는 Git 태그 설치로 시작한다(별도 패키지 인덱스 서버를 두지 않음). 각 SDK의 태그는 소유 리포지토리가 붙인다 |
| D19 | 계약 소유와 위치 | 문진 스키마(위치는 D29)는 문진 서비스 영역의 데이터 스키마다. 헤드의 계약이 아니며 헤드는 수정하지 않는다. 다른 영역은 읽기 전용으로 의존한다. 변경이 필요하면 헤드를 거쳐 영향 영역을 정리한 뒤 문진 서비스 영역이 반영한다. 영역 사이 계약은 헤드 소유의 새 리포지토리 `boundary-contracts`에 둔다(D14의 "contracts 안 별도 디렉터리"를 대체). TurnTrace는 고치지 않고 경계 계약의 `TraceEnvelope`에 `release_id`를 둔다. 2026-10-15 사용자 지적에 따라 헤드가 결정 |
| D20 | 경계 계약의 세부 | 불변 산출물은 `ArtifactRef(id, version, content_hash)`로 가리킨다. 해시는 정규화 JSON(RFC 8785)의 SHA-256이며 ReleaseManifest의 `content_hash`는 자기 자신을 뺀 값에 대한 것이다. GateDecision은 `gate_policy_version`을 적고, PASS이면 모든 검사가 PASS이며 `release_id`가 있다. 검사 종류는 4종(CONTRACT_COMPAT, QUESTION_MODEL_COMPAT, ACCEPTANCE_EVAL, CLINICAL_SAFETY)으로 두고 필수 여부는 게이트 규칙 버전이 정한다. 사용자가 세부 결정을 헤드에 위임 |
| D21 | 문진 스키마 변경 담당 | 문진 스키마의 변경은 survey-service 영역 에이전트가 그 저장소의 절차(원본, 의미, 예시, `verify.py`)대로 반영한다. 다른 영역의 요청은 헤드가 영향을 정리해 전달하고, 계약 버전을 올리는 변경은 헤드가 영향 영역에 알린다. 2026-10-15 사용자 결정 |
| D22 | 컨테이너화와 개발 | 리포지토리 종류별로 다르다. (1) 서비스를 가진 영역(survey-service, question-authoring, release-gate, ops-feedback)은 자기 Dockerfile과 로컬용 `compose.dev.yaml`을 소유하고, CI에서 이미지를 빌드해 digest를 게시한다. (2) 작업형 영역(synthetic-data, model-lab)은 운영 서버 밖에서 돌리며 컨테이너 또는 환경 잠금 파일을 두되, 산출물은 불변 버전으로 게시한다. (3) 라이브러리(turn-engine, model-runtime, boundary-contracts, 각 SDK)는 이미지가 아니라 Git 태그 패키지다(D18). (4) deploy는 digest만 모아 Compose로 합친다. 이미지의 공통 모양과 개발 방식은 `shared/CLAUDE.root.md`의 규칙을 따른다. 개발은 컨테이너 밖(가상환경, 메모리 구현)에서 하고, 컨테이너화 가능성은 매 변경마다 이미지 빌드와 기동 확인(`/healthz`)으로 검증한다. 컨테이너 안에서 개발하는 방식과 컨테이너화를 미루는 방식은 택하지 않았다. 헤드가 결정 |
| D23 | 문진 스키마의 위치 | 워크스페이스 루트가 아니라 `survey-service/schema/`에 둔다. HealthCheckSchema를 clone한 별도 git 리포지토리이고, survey-service는 이를 `.gitignore`로 제외한다. 다른 영역은 이 경로를 읽기 전용으로만 읽는다. `contracts`라는 이름은 쓰지 않는다. 2026-10-15 사용자 지적에 따라 헤드가 결정 |
| D24 | 이미지 레지스트리와 빌드 | 서버 안의 로컬 레지스트리(`registry:2`)를 쓴다. 각 서비스 리포지토리의 CI가 이미지를 빌드해 레지스트리에 올리고 digest를 deploy에 PR로 제출한다. deploy가 digest 잠금 파일을 갱신한다. 외부 레지스트리와 쿠버네티스는 쓰지 않는다(필요해지면 digest 고정 방식이 그대로 이식된다). O17을 닫음. 헤드가 결정 |
| D25 | 경계 계약의 불변성 | 경계 계약의 레코드는 모두 불변이다. 그래서 `ModelPackageManifest`에는 상태 필드가 없고(승인 여부는 `GateDecision`), `FailureCase`는 검토 결과를 `version`을 올린 새 레코드로 낸다. `ParserSample`·`GeneratorSample`의 input·expected와 `TraceEnvelope.trace`는 `runtime_contract_version`의 문진 스키마로 따로 검증하며 경계 계약은 구조만 본다. `DatasetManifest`는 `scenario_disjoint_across_splits: true`인 것만 게시한다(경계 규칙 9). 실패 유형은 분류체계 미정(O11)이라 문자열이다. 헤드가 결정 |
| D26 | 계약 진화 규칙 | 모든 경계 레코드에 선택 필드 `ext`(키는 영역 이름)를 둔다. MINOR는 추가만 한다. 쓰는 쪽은 엄격히 검증하고 읽는 쪽은 모르는 필드를 무시하며 모르는 열거값을 '알 수 없음'으로 처리한다. 의미 변경은 새 필드로 한다. 상세는 `boundary-contracts/CONVENTIONS.md`. 사용자가 "계약을 매번 뜯어 고치지 않게"를 요구해 헤드가 결정 |
| D27 | 영역 경계 명세 | 영역이 서로 호출하는 모든 인터페이스(I1~I10)의 시그니처, 오류, 멱등성을 `boundary-contracts/INTERFACES.md`와 `CONVENTIONS.md`에 둔다. 영역은 상대를 블랙박스로 보고 이것만 믿는다. 게이트는 릴리스를 만들 때 문항 세트와 어댑터 내용을 릴리스에 묶어 서비스가 릴리스 읽기 SDK 하나만 쓰게 한다. 공통 오류 형식 `BoundaryError`, 수집 결과 `IngestResult`, 후보 접수 `GateSubmission`, 활성 포인터 `ActivePointer`, 롤백 결과 `RollbackReceipt`를 경계 계약에 추가. 사용자 요구에 따라 헤드가 결정 |
| D28 | 새 리포지토리와 문진 스키마 최소화 | 모든 리포지토리는 새로 만들며 이름은 `Sdabin1209/openit_<디렉터리 이름>`이다. 기존 HealthCheckSchema에 맞추지 않는다. 문진 스키마는 `survey-service/schema/`에서 스키마만 남기는 최소 구성으로 정리했다(`schemas/` 23개, `COMPONENTS.yaml`, `CONTRACT_VERSION`). 요구사항 케이스, 업무 규칙 문서, 정적 예시, 검증 도구, 웹은 뺐다(원본은 HealthCheckSchema와 로컬 클론의 git 이력에 남아 있다). 2026-10-15 사용자 결정 |
| D29 | 문진 스키마는 survey-service에 포함 | 문진 스키마는 별도 리포지토리가 아니라 `openit_survey-service` 안의 `schema/` 디렉터리다. 영역 리포지토리가 자기 스키마를 포함하고 소유한다. D23의 "별도 git 리포지토리"를 대체하고, 리포지토리 수는 D04의 11개로 돌아간다. 다른 영역은 survey-service를 clone해 `schema/`만 읽기 전용으로 읽는다. 2026-10-15 사용자 지적 |
| D30 | 임상 승인 (O12 닫음) | 문항을 올리는 사람은 의료인이며 신뢰한다. 별도의 임상 검수자를 두지 않고 저자의 확인이 임상 승인이다. `ReviewRecord`는 `reviewer_role`에 저자 역할을 적고 `clinical_basis_approved`를 true로 남긴다. 임상 승인은 정확한 문항 세트 버전에 묶이므로 내용이 바뀌면 새 확인이 필요하다. 게이트의 `CLINICAL_SAFETY`는 그 버전에 대한 승인 기록이 있는지 확인하고, 모델 출력의 안전 지표는 O11이 정한다. 2026-10-15 사용자 결정 |
| D31 | 문항 자료 등록 (O15 닫음) | question-authoring은 저자가 올린 문항 자료(PDF 등 정해진 형식)를 파싱해 문항 초안으로 만드는 파이프라인을 필수로 갖는다. 저자는 컴퓨터 전문가가 아니므로 개별 필드가 아니라 사람이 읽는 형태의 미리보기로 확인한다. 파싱 결과는 승인 전에는 게이트 후보가 될 수 없고, 저자의 확인 없이 문항 세트 버전이 되지 않는다. 지원할 형식은 O18 |
| D32 | 처음 보는 문항에 대한 일반화 | 모델은 문항이 입력으로 주어지면 처음 보는 문항도 다루도록 만드는 것이 목적이다. 그래서 평가에는 학습에 쓰지 않은 문항 세트의 샘플(보지 못한 문항 평가)을 포함하고, 새 문항 세트는 기존 모델과의 조합으로 게이트의 `ACCEPTANCE_EVAL`을 통과하면 재학습 없이 출고할 수 있다. 보지 못한 문항에서의 추출 실패는 `FailureCase`로 올려 그 문항의 샘플 생성과 재학습으로 되돌린다. 헤드가 결정(사용자 설명에 따름) |
| D33 | 문항 자료 형식 (O18 닫음) | 지원할 형식을 미리 정하지 않는다. 요구는 "저자가 가져온 문항을 등록할 수 있다"이다. question-authoring은 (1) 형식마다 추출기를 붙일 수 있는 구조로 만들고, (2) 어떤 형식이든 같은 미리보기·저자 확인 절차를 거치게 하고, (3) 파싱할 수 없거나 확신하지 못하면 추정하지 않고 알린 뒤 화면 입력(템플릿 양식)으로 이어 가게 해 등록이 항상 가능하게 하고, (4) 원본 자료의 해시를 문항 세트 버전에 출처로 남긴다(`ext`). 어떤 형식을 먼저 지원할지는 영역이 정한다. 2026-10-15 사용자 결정 |
| D34 | 해시의 기준 구현 | 해시(JCS 정규화 + SHA-256)는 `boundary-contracts`의 `boundary_contracts.canonical`이 유일한 기준 구현이다. SDK와 서비스는 자기 구현을 두지 않고 이것을 가져다 쓴다(RFC 8785 시험 벡터 포함). 어댑터의 `adapter_hash`는 `directory_hash`다. 헤드가 결정 |
| D35 | model-runtime 세부 | 문진 스키마 사본은 라이브러리에 묶지 않고 호출자가 `schema_dir`로 넘기며 `CONTRACT_VERSION`을 대조한다. `load`의 `backend`·`schema_dir` 선택 인자와 `last_call_info`를 승인한다. 첫 추론 백엔드는 vLLM(구조화 출력 + LoRA)을 잠정 채택하되, GPU 환경의 시험으로 확인한 뒤 확정한다. 헤드가 결정 |
| D36 | 모델 출력 보호 | 업무 규칙(원칙 9, 파서 대체 출력, 생성기 규칙 5)에 따라 `parse`와 `generate`는 모델 출력이 깨져도 예외 없이 규칙이 정한 대체 출력을 돌려준다. 파서는 형식 위반이면 빈 목록, 의도·대상·값이 규칙을 어기면 정해진 대로 고친다. 생성기는 모델이 `response_text`만 내고 `is_fallback`은 코드가 채우며, 지시를 못 지키면 문장 재료를 그대로 읽는 문장을 `is_fallback=true`로 낸다. 보호 적용은 `last_call_info`에 남기고, model-lab 평가용으로 보호 전 출력(`*_raw`)도 제공한다. 이 보호 규칙의 구현은 model-runtime이 맡는다. 이전의 `ModelOutputInvalid` 던지기를 대체한다. `configure()` 같은 전역 설정은 두지 않고 `schema_dir`를 인자로 받는다. 헤드가 결정 |
| D37 | 커밋 규칙 | 모든 세션은 작업 단위마다 자기 리포지토리에 커밋한다. 작성자는 사용자 noreply 주소, push는 사용자가 한다. Python 의존은 리포지토리의 `.venv`에 설치한다(pip와 venv는 설치됨). 2026-10-15 사용자 요청 |
| D38 | 완성 목표 | 목표는 임시 골격이 아니라 실제로 쓸 시스템을 모델 성능을 제외하고 제대로 만드는 것이다. 이후 남는 일이 모델 성능 향상뿐이어야 한다. 모델의 학습 품질과 통과 기준(O11)은 미루지만, 학습·평가·패키징·게시는 설정으로 반복 실행되는 파이프라인으로 만든다. 임시로 느슨한 기준이나 스텁을 박아 두지 않는다. 2026-10-15 사용자 결정 |
| D39 | 자동화 원칙 | 영역 사이의 자동 연결은 저장소를 보고 일하는 멱등 잡으로 한다. 각 영역은 잡을 한 번 실행하는 명령과 설정 파일을 갖고, deploy의 스케줄러가 주기를 정한다. 영역이 다른 영역을 직접 깨우지 않는다(D02와 같은 원칙). 헤드가 결정 |
| D40 | 서빙 서버와 학습·평가 서버 (가정) | 요구사항에 명시가 없어 다음을 가정한다. 서빙 서버는 활성 릴리스(기반 모델과 LoRA-A·B)만 올리고, 학습과 평가(model-lab의 학습, 게이트의 승인 평가, 합성 데이터 생성)는 별도의 GPU 서버에서 돈다. 서빙 서버에서 평가와 실서비스를 동시에 하지 않는다. GPU 서버의 작업은 저장소를 보고 일하는 워커가 가져가는 방식이며(D39) 서빙 서버가 외부 호출을 받지 않는다. LoRA-A·B가 같은 기반 모델을 쓰면 가중치를 공유해 서빙 VRAM이 줄어드므로, 같은 기반 모델을 쓰는 것을 기본 설계 방향으로 한다(미확정, 서빙 GPU 용량은 미정). 사용자가 알려주면 재검토. 2026-10-15 사용자 설명에 따름 |
| D41 | push 허락 | 모든 리포지토리의 push는 헤드가 허락한다. 영역이 시험 통과와 커밋을 알리면 헤드가 시험 결과와 작성자를 확인해 허락한다. 강제 push는 하지 않는다. 원격은 모두 비공개다. 2026-10-15 사용자가 헤드에게 위임 |
| D42 | 경계 계약 1.0 확정 | 영역의 첫 구간 보고(변경 요청 17건)를 반영해 `boundary-contracts`를 1.0.0으로 태그했다(릴리스된 레코드가 없을 때 보강). 변경: `ReleaseManifest.adapters`(어댑터 해시, serving_config, 해시) 필수 / `GateDecision.reject_codes`와 `checks[].result=SKIPPED` / `ModelPackageManifest.lineage.question_sets`(선택) / I1·I3 `list_ids` / 스키마를 패키지 데이터로 포함(`load_schema`, `validator`) / 역할은 토큰에 묶음 / 현재 판정은 가장 최근 것 / HTTP 규약과 상태 코드 / `SlotRef`는 `<question_id>.<slot_id>` / `QuestionBank.version`은 `ArtifactRef.version`의 정수 / `reviewed_only`는 가장 최근 검수 기준 / `serving_config_hash`는 `canonical.sha256_hash(serving_config)` / 비식별 Trace는 구조 정보만 쓴다 / `evidence_refs`는 불투명한 Id. 이후 변경은 `CONVENTIONS.md`의 진화 규칙(MINOR는 추가만)을 따른다 |
| D43 | 경계 계약 1.1 | synthetic-data의 변경 요청을 반영해 `FailureCase`에 선택 필드 `question_set`, `expected_kind`를 추가했다(MINOR, 1.0 레코드는 그대로 유효하며 하위 호환 시험이 있다). 읽기 규칙: `SlotRef` 문자열은 마지막 `.`에서 나눈다. 모든 산출물의 `version`은 Id 규칙을 따르고 SDK가 `INVALID_RECORD`로 강제한다. 재현성은 시각·버전을 뺀 내용 해시로 비교한다. 위험 신호 감지는 파서가 아니라 코드의 위험 표현 대조(G9)가 하고, 과거 증상 진술은 파서 라벨로 OUT_OF_SCOPE다. 태그 v1.1.0 |
| D44 | 라이브러리 태그와 정답 예시 | 영역이 의존하는 태그: boundary-contracts v1.1.0, turn-engine v0.2.0, model-runtime v0.2.0. turn-engine은 원본 요구사항 케이스의 입출력 쌍(golden)을 기준으로 비교해 868쌍 중 806쌍이 일치하고 나머지 62쌍을 구현 결함(0) / 규칙 해석 차이(25) / 예시 자체의 오류(37)로 분류했다. 정답 예시는 정적 예시이며 정답 보증이 아니므로 불일치는 분류해서 처리한다. 같은 방식의 golden을 survey-service, synthetic-data, model-lab, model-runtime에도 전달했다 |
| D45 | I9 역할별 설정 | `ReleaseManifest.adapters`와 모델 패키지가 역할별로 `serving_config`와 해시를 갖는데 I9 `load`가 하나만 받던 불일치를 고친다. `load`는 `serving_configs`와 `expected_serving_config_hashes`를 역할(LORA_A, LORA_B)별 맵으로 받는다. 파서는 결정적, 생성기는 다른 디코딩을 쓸 수 있기 때문이다. model-runtime 0.3.0으로 구현(라이브러리 API 변경) |
| D46 | 릴리스 적재 정책 | 서비스는 릴리스의 `turn_engine_version`·`model_runtime_version`의 MAJOR.MINOR가 설치본과 다르면 적재를 거부하고 이전 릴리스를 유지한다(PATCH 차이는 경고). 게이트가 승인한 동작과 서비스 동작이 달라지지 않게 하려는 것이다. 바깥 식별자가 경계 `Id` 형식에 맞지 않으면 `x-` + SHA-256 앞 32자로 봉투에 넣는다(Trace를 버리지 않는다). 문진 스키마 변경 후보(고정 문장 정보, 도움 요청 사유, `pending_id_seed`)는 정수 버전 1→2로 한 번에 모아 올린다 |
| D47 | GPU 호스트 사용 | 개발용 GPU 호스트 `gpu-dev`(RTX 4070급 12GB, Ubuntu 24.04 WSL2, 15GB RAM, Docker 없음, pip 없음, 서버가 꺼질 수 있음)를 ssh로 쓴다. 코드는 rsync로 보내고 비밀 값은 보내지 않는다. 작업 폴더는 `~/openit-gpu/`, sudo 금지, GPU는 flock으로 한 번에 한 작업. 12GB에 맞춘 값은 설정 프로파일로 빼고, 이 호스트의 학습 결과는 파이프라인 검증용이다(실제 스테이션은 더 크다). 임시 기반 모델은 Qwen/Qwen2.5-1.5B-Instruct(Apache-2.0)이며 실제 기반 모델 선정은 스테이션 사양 확인 뒤 별도 결정이다. 2026-10-15 사용자 결정 |
| D48 | 첫 추론 백엔드와 한계 | vLLM을 첫 백엔드로 확정한다(gpu-dev에서 확인: LoRA+구조화 출력 동시 사용, 두 어댑터를 한 기반 모델에 올리는 VRAM 증가 약 0.07GiB, 요청마다 어댑터 선택). 한계: 구조화 출력이 `allOf`·`if/then`·`not`을 조용히 무시하고 `uniqueItems`를 거부하므로 조건 규칙은 사후 검증과 보호가 맡고(보호 개입이 더 잦을 수 있어 model-lab 평가가 보호 전 유효율을 보고한다), 문진 스키마 v2 후보에 "조건 규칙을 oneOf 가지로 표현"을 올린다. 어댑터는 PEFT 형식이고 순위가 `max_lora_rank`를 넘으면 로딩 전에 거부한다(엔진이 죽는 것을 막는다). 재현성은 같은 서버 프로세스 안에서만 약속하고 평가는 온도 0에서 한다. 엔진·xgrammar 버전은 `serving_config.constraint.backend_version`으로 고정한다. 사용자 요청에 따른 GPU 시험 결과, 헤드가 결정 |
| D49 | 영역 사이 호출은 HTTP | 서비스끼리는 코드를 가져오지 않고 HTTP 서비스 API로 만난다. 경로와 응답은 `boundary-contracts/HTTP.md`가 정하고(I1·I3·I4·I5·I6·I7, 기존 경로 유지), 클라이언트는 `boundary_contracts.clients`(표준 라이브러리만, 해시는 클라이언트가 재검증, tar 안전 처리)가 한 번만 구현한다. 서버는 소유 영역이 구현한다. deploy의 E2E에서 소비 이미지에 이웃 클라이언트를 넣을 방법이 없어 서비스끼리 이어지지 않는 것이 확인되어 정했다(CR-D01 제안 A). 모델 레지스트리(I3)는 model-lab이 서버(`model-registry`)를 맡고 GPU 호스트의 model-lab이 HTTP로 게시한다. 데이터셋(I2)은 같은 호스트(GPU 호스트)의 파일 저장소로 둔다 |
| D50 | 저장소 계정과 DB (O10 닫음) | 저장소는 SQLite이고 소유 서비스의 볼륨 하나에만 쓴다. 이웃은 볼륨을 공유하지 않고 HTTP와 영역별 토큰으로만 읽는다(WAL 모드 SQLite가 읽기 전용 마운트에서 열리지 않는 문제도 이로써 피한다). DB 서버와 DB 계정 분리는 두지 않는다. 데이터가 커지거나 동시성이 문제가 되면 별도 결정으로 다시 연다. 이미지 라벨 키는 survey-service의 `io.openit.*`로 통일한다(`io.openit.service`, `io.openit.revision`, `io.openit.contracts.boundary`, `io.openit.contracts.survey-schema`, `io.openit.turn-engine`, `io.openit.model-runtime`) |
| D51 | 경계 계약 1.2와 클라이언트 | `boundary-contracts` v1.2.0(스키마 1.2, 클라이언트 포함)을 영역이 쓸 기준 태그로 한다(v1.1.1은 쓰지 않는다). 변경: `ModelPackageManifest.base_model.id`를 Id 패턴에서 비어 있지 않은 문자열(최대 200자)로 넓혀 허브 이름(`Qwen/…`)을 그대로 쓴다(허용 범위 확대라 MINOR, 1.1 레코드는 그대로 유효). 클라이언트는 응답을 읽기 모드로 검증한다(모르는 필드·열거값 허용, MAJOR 다르면 UNSUPPORTED_VERSION, 해시는 원본으로 재계산). 학습 재현성: 같은 호스트·같은 설정·같은 시드에서 같은 어댑터 해시를 목표로 하되(eager 어텐션 확인), 재개한 학습은 중단 없는 학습과 해시가 다를 수 있다. 어댑터의 정체는 그 해시이고 계보에 재개 여부를 남긴다 |
| D52 | E2E 막힘의 결정 | deploy의 E2E(실제 서비스 HTTP, 73 PASS)에서 남은 막힘을 정한다. (1) 실패 사례 검토 게시: `POST /v1/cases/{case_id}/review`(역할 `reviewer`)를 HTTP.md에 추가하고 ops-feedback이 구현한다. 검토 화면(UI)은 이 면의 클라이언트로 나중에 붙인다. (2) 환류: model-lab은 확정된(CONFIRMED, expected 있음) 실패 사례를 I7로 읽어 회귀 평가 집합으로 쓰고, question-authoring은 I7로 문항별 실패율·혼동 사례를 읽어 개선 신호 수신함을 만든다. (3) 승인 평가 실행기(`ACCEPTANCE_EVAL`)의 실제 구현은 **O11이 정해져야** 한다(평가셋의 소유자와 독립성, 지표, 임계치). 지금은 정책 형식과 실행기 플러그인 호출 형태를 문서화하고 시험용 실행기만 시험 구성에 둔다. (4) 개발 중 데이터셋 이동은 rsync(synthetic-data의 `FileDatasetStore` 출력 경로를 GPU 호스트로)이고, GPU 호스트가 서빙 서버의 model-registry에 닿는 길은 개발에서는 SSH 역터널(쓰기 토큰은 환경 변수로)이다. 운영의 네트워크 경계는 서빙·GPU 서버 구성이 정해질 때 사용자와 정한다 |
| D53 | 출고는 사람이 정한다 (O11 닫음) | 모델 조합의 출고는 AI 학습 담당자(`release-approver`)가 정한다. 지표 통과가 곧 서빙이 아니다. 평가는 임계치 없는 체계적 지표 보고서(`EvaluationReport`, 지표 카탈로그 `METRICS.md`는 제안이며 담당자가 다듬는다)를 낸다. 게이트는 기술 호환(계약·문항-모델 호환·보고서 형식)만 자동으로 검사해 어긋나면 반려하고, 통과하면 `AWAITING_APPROVAL`에서 멈춘다. 담당자는 후보와 현재 활성 릴리스를 같은 지표끼리 맞댄 `ReviewReport`를 보고 `POST /v1/approvals`로 APPROVE/REJECT(반려는 사유 필수)한다. PASS `GateDecision`에는 `HUMAN_APPROVAL` 검사가 PASS여야 한다. 경계 계약 1.3(MINOR) |
| D54 | 서버 토폴로지(가정) | 서빙·백 서버는 RTX 4090 24GB 1장에 Compose 서비스와 추론 컨테이너, 학습 서버는 A6000 48GB로 서로 다르다(D40). 학습은 워커 방식으로 서빙 서버의 model-registry에 HTTP로 게시한다. `gpu-dev`(개인 워크스테이션)는 개발 전용. **사용자 확인이 필요한 가정이다** |
| D55 | 공개 API와 실패 사례 입력 (O06, O19 일부) | 키오스크는 프론트팀 담당이라 협의하지 않고 우리가 계약을 정해 전달한다: `PUBLIC_API.md`(요청-응답 HTTP, 프론트가 STT 텍스트와 세션 ID·턴 ID를 보냄, 환자 식별 정보 없음, 같은 턴 ID 재전송은 멱등). survey-service가 구현한다. 실패 사례에는 검토자가 개인정보를 뺀 문장으로 고쳐 쓴 `reviewed_input`을 선택적으로 둔다(검토 POST로 게시). 원문을 그대로 보존할지는 사용자 확인(법적 근거 필요)이 끝나기 전까지 하지 않는다 |
| D56 | 복구 범위 (O16 일부) | 자동 백업과 시험된 복구 스크립트·런북(deploy)은 범위에 포함한다. 고가용성·대기 서버·상시 대응·현장 대체 절차는 범위 밖(D10). 백업 간격(권고 1시간)과 서버 밖 저장 위치(권고: 학습 서버)는 사용자가 정한다 |
| D57 | O19 잠정 결정: B안 | 사용자가 B안(검토자가 고쳐 쓴 `reviewed_input` 보존)으로 진행하라고 했다(2026-10-15). 원본의 보관 기간·접근 통제는 지금 고려하지 않는다. 설계 변경이 필요해지면 사용자가 알린다. 원문 그대로 보존(C)은 하지 않는다(D55) |

## 구조를 확정하기 전에 닫을 열린 결정(A)

이 결정들은 경계 계약의 모양이나 의존 관계를 바꾼다. 경계 계약을 쓰기 전에 하나씩 닫는다. 권고는 헤드의 제안이며 사용자가 정한다.

| ID | 결정할 것 | 권고 | 왜 지금 필요한가 |
| --- | --- | --- | --- |
| O06 | 공개 API 형태와 세션 방침 | Frontend 팀과 협의한다. 문진 대상 참조, 인증, 전송 방식, 실패 신호의 의미와 타임아웃을 정해야 한다 | survey-service 브리프의 핵심이고, 다른 팀과의 경계다 |

## 영역 설계 중에 정해도 되는 열린 결정(B)

| ID | 결정할 것 | 권고 또는 담당 |
| --- | --- | --- |
| O19 | 비식별 뒤 발화 문장의 보존 범위 | **(잠정 B, D57)** 사용자 결정, 헤드 권고는 B.** 지금(A)은 자유 문자열을 전부 마스킹한다. 그래서 실패 사례에서 얻는 것은 구조(어떤 문항·유형·의도·판정)뿐이고 발화 문장은 `[MASKED]`다. 이 때문에 (1) synthetic-data의 시드는 구조만 재사용하고 새 발화는 다시 만들며, (2) model-lab의 회귀 평가는 마스킹된 입력으로 돌아 모델을 실제로 다시 시험하지 못하고, (3) question-authoring의 신호는 문항별 통계로 한정된다. 선택지: **A** 전부 마스킹 유지(가장 안전, 환류는 구조 수준). **B** A에 더해 검토자가 확정할 때 개인정보 없는 발화로 **직접 고쳐 쓴 입력**(`reviewed_input`)을 함께 게시한다. 사람이 비식별을 책임지므로 안전하면서 확정된 사례에 한해 모델을 다시 시험하고 학습 시드로 쓸 수 있다(검토자 부담이 늘고 계약 MINOR 추가가 필요). **C** 패턴으로 발화를 자동 비식별해 남김(이름 같은 자유 서술 속 개인정보를 못 잡는다. 의료 도메인에서 권하지 않음). | 환류의 학습 가치와 개인정보 위험의 균형 |
| O10 | 저장소의 실제 기술 | SDK 뒤의 구현이므로 영역이 정한다. 단일 서버 기본값은 저장소마다 데이터베이스와 계정을 나눈 하나의 DB 인스턴스와 파일 볼륨 |
| O11 | 평가셋의 구성과 소유자(합성과 실제 발화의 비율) | 도메인 판단이라 사용자가 정한다. 파인튜닝 목적에 직결 |
| O13 | 모델 전환 시점 | 새 세션부터를 기본으로 한다 |
| O14 | 모델 출력 형식 보장 방식 | 스키마 제약 디코딩이나 검증 후 재시도, model-runtime이 정한다 |
| O16 | 허용 중단 시간과 복구 시점 | 백업 주기와 복구 순서에 영향. 사용자가 정한다 |

## 닫는 순서

O01~O05, O07은 닫혔다(D13~D18). O06은 Frontend 팀의 답이 필요하므로 다른 결정과 별개로 진행하고, 답이 올 때까지 survey-service 브리프의 해당 부분을 비워 둔다.
