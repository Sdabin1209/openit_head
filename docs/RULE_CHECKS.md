# 규칙 ↔ 자동 점검 대응표

목적: 규칙마다 그것을 기계로 확인하는 점검을 하나 이상 둔다. 점검이 없는 규칙은 지켜지는지 알 수 없으므로 "완료"를 말하기 전에 이 표의 모든 행이 `있음`이고 통과해야 한다. 이 표에 없는 문제는 놓친 결함이 아니라 아직 정하지 않은 요구이며, 사용자 결정으로 올린다(2026-10-31). **점검을 넣을 때 '이 시험이 운영과 다른 조건으로 통과하는가'를 먼저 묻는다**: 시험용 구성 덮어쓰기로 통과하는 점검은 그 요구의 증거가 아니다(2026-11-01, U65·L27 사례).

| # | 규칙(정본) | 점검(어디서 돌아가나) | 상태 |
|---|---|---|---|
| 1 | 구조: schemas/·types/·components/·wiring/, 컴포넌트끼리 import 금지, HTTP는 link_*만 (D104, D117 DESIGN.md 6절; 구조 규칙 C1·C3·C4·C29, D49) | `head/scripts/structure-check.py` + 각 영역 `tests/test_structure.*` | 있음(단, DESIGN 6절의 'types/가 schemas/에서 다시 생성한 것과 같다'는 영역 시험이 본다 — structure-check는 예시 파일 존재까지) |
| 2 | 시험 판정에 실제 시간 없음, 컴포넌트는 시계를 주입받음 (U422, ADR: 영역별 시계 주입) | 각 영역 `tests/test_no_real_time.py` · `test_timing_table.py` · `timing.test.ts` · survey `test_structure.py::test_components_never_read_the_time_module_or_the_real_clock_config`, 표 `tests/TIMING.md` | 있음(영역마다 이름 다름) |
| 3 | 생산자는 내보내기 전에 계약으로 검증, 받는 쪽은 재검증 안 함 (R7, ADR 0010, CONVENTIONS 3절) | `head/scripts/producer-check.py`(계약 86개의 생산자 표 `head/shared/producers.json` ↔ 생산자 동작 코드의 참조 대조) + 경로별 openit_link Route `response_schema`/`request_schema`, 영역 생산자 검증 시험 | 있음(참조 대조: 문자열 참조가 있으면 통과하므로 '검증 호출'까지는 경로별 시험이 본다) |
| 4 | 시간 사슬: 화면 대기 > gateway > 서버 요청 마감 > 이웃·모델 호출 (CONVENTIONS 시간표, D119, D120) | deploy `scripts/test_time_chain.py`(ProxyChain: 모든 reverse_proxy, model-serving 상한), 영역 노출 선언 시험(`test_exposure*`, `test_exposure_budget.py`), deploy `check-exposure` | 있음 |
| 5 | 고정 버전 일치 (기준표 `deploy/scripts/lib.sh`: DEPLOY_BC_TAG, LINK, DEPLOY_MR_TAG, DEPLOY_SS_TAG; model-runtime의 Dockerfile ARG 포함; 태그 설치 규칙 C25·C26·D44, digest 게시 C30·D24 는 deploy `scripts/check-compose.sh`) | deploy `scripts/check-versions.sh`, link 고정 점검(`check-link-pins.sh`, E2E 시작 전), consistency_check(공개 이름). 고정을 올린 뒤에는 각 영역 작업 폴더에서 `scripts/setup-env.sh`를 다시 돌린다 — check-all은 작업 폴더 venv로 시험하므로 옛 패키지가 남으면 거짓 실패(2026-10-31 15:17 사례) | 있음 |
| 6 | 상시 서비스 재시작 정책 (U17) | deploy `scripts/test_compose_restart_policy.py` | 있음 |
| 7 | 서비스 목록 단일 정본(계약 PublishRequest.service ↔ lib.sh) (U46) | deploy `scripts/test_services_enum.py` | 있음 |
| 8 | 영역 전체 시험이 모두 동시에 돌아도 통과 | deploy `scripts/check-all.sh --strict`(E2E 시작 점검) | 있음 |
| 9 | 영역 사이 끝까지 맞물림 | deploy `scripts/e2e.sh` | 있음 |

| 10 | 추론 서버 위치 독립: 다른 호스트의 추론 서버가 운영 입구(게이트웨이 기계 토큰 경로)로 release-gate를 읽어 기동한다 (D72, D114 TLS, D122) | deploy `scripts/test-inference-location.sh`(샌드박스: 제품 무변경 + `compose.inference.yaml` 별도 프로젝트, 사람 계정 404·무토큰 401 음성 확인 포함), 전체 E2E 단계로 편입 | 있음(2026-11-01 18:31, wo-445: `test-inference-location.sh` 17/17, E2E 단계 5L 통과) |
| 11 | 시험용 문 0건: 운영 compose·overlay에 gateway 외 서비스의 `ports`·시험 플래그가 없고, E2E 드라이버는 게이트웨이·`docker exec/run`·다른 호스트 역할 컨테이너로만 닿는다 (U65, D123) | deploy `scripts/test_compose_no_test_doors.py`(check-all), e2e_steps 정적 검사(내부 포트 키 사용 0) | 있음(2026-11-01 18:31, wo-445: `test_compose_no_test_doors.py` check-all 연결, e2e_steps URL()이 내부 키를 거부, 전체 E2E 185/0) |

점검 없는 규칙의 목록은 `docs/RULE_COVERAGE.md`(생성물)의 "없음" 행이다. 헤드 점검(`structure-check.py`, `producer-check.py`, `commit-author-check.sh`, `area-presence-check.py`, `rules-coverage.py`)은 영역이 head를 읽을 수 없으므로(루트 CLAUDE.md 읽기 허용 목록) deploy check-all에 넣지 않고, 헤드가 "완료"를 말하기 전에 직접 돌려 통과를 확인한다.
| 12 | 커밋 작성자는 Sdabin1209 noreply (C33, D37) | `head/scripts/commit-author-check.sh`(리포 전체 최근 200 커밋) | 있음 |
| 13 | 영역마다 ADR(docs/adr)과 README 링크, 서비스 영역은 Dockerfile+스모크, 스모크는 고정 포트 금지, .venv 미커밋, README 에 시험 개수 숫자 금지 (C16, C17, C22, D22, C27, C35, C10, L26) | `head/scripts/area-presence-check.py` | 있음 |
| 14 | 계약 버전 체계: 패키지 버전 MAJOR.MINOR == pipeline_schema_version, 스키마 수 (D14) | boundary-contracts `tests/test_package.py` | 있음 |
| 15 | 해시의 기준 구현 하나(canonical JSON, D34) | boundary-contracts `tests/test_canonical.py` | 있음 |
| 16 | 모델 출력 보호: 형식·의미 규칙 위반은 내보내지 않고 재시도, 값 규칙 적용 (D36, D82, D45) | model-runtime `tests/test_extract_rules.py`, `tests/test_value_rules.py`; 계약 `tests/test_action_rules.py` | 있음 |
| 17 | 백업 필수·복구 범위 (D56, D112) | deploy `scripts/backup-check.sh`, `scripts/backup-restore-test.sh`, `scripts/test-backup.sh` | 있음 |
| 18 | 영역 사이 이름(설정 env·비밀 파일 이름)은 계약 선언에만 (U73, 구조 규칙 C6) | deploy `scripts/check_config_contracts.py`(서비스 8개 + gateway 선언), 각 영역 기동 검증 시험(release-gate `tests/test_gate_env.py` 등) | 있음 |
| 19 | next_item 은 서버가 정한다 (U74, 계약 ADR 0014) | boundary-contracts `tests/test_action_rules.py` FillNextItem, model-runtime `tests/test_extract_rules.py` ServerFillsNextItem | 있음 |
| 20 | 데모=제품: 데모 덮어쓰기는 모델 대역·포트·시험 계정 외 제품 설정을 못 바꾼다 (U75) | deploy `scripts/test-demo-parity.sh` | 있음 |
| 21 | 규칙 전수 대응표가 입력(DECISIONS·CLAUDE·RULE_CHECKS·self-checks)과 같다 (U76) | `head/scripts/rules-coverage.py --check` | 있음 |
| 22 | 게이트웨이 사이트 목록은 host:port(와일드카드·포트만 금지) (L20) | deploy `schemas/GatewayEnv` via `scripts/check_config_contracts.py` | 있음 |
| 23 | 모든 영역의 의존 고정이 deploy 기준표와 같고, 영역 사이 이름(문진표 선택·결과 푸시·역할 헤더·승인 대기 사유)을 생산자·소비자가 둘 다 쓴다 (정적 일관성, 2026-11-03) | `head/scripts/cross-area-check.py --deploy <deploy 작업 트리>` | 있음 |
