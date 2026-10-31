# 규칙 ↔ 자동 점검 대응표

목적: 규칙마다 그것을 기계로 확인하는 점검을 하나 이상 둔다. 점검이 없는 규칙은 지켜지는지 알 수 없으므로 "완료"를 말하기 전에 이 표의 모든 행이 `있음`이고 통과해야 한다. 이 표에 없는 문제는 놓친 결함이 아니라 아직 정하지 않은 요구이며, 사용자 결정으로 올린다(2026-10-31).

| # | 규칙(정본) | 점검(어디서 돌아가나) | 상태 |
|---|---|---|---|
| 1 | 구조: schemas/·types/·components/·wiring/, 컴포넌트끼리 import 금지, HTTP는 link_*만 (D104, D117 DESIGN.md 6절) | `head/scripts/structure-check.py` + 각 영역 `tests/test_structure.*` | 있음(단, DESIGN 6절의 'types/가 schemas/에서 다시 생성한 것과 같다'는 영역 시험이 본다 — structure-check는 예시 파일 존재까지) |
| 2 | 시험 판정에 실제 시간 없음, 컴포넌트는 시계를 주입받음 (U422, ADR: 영역별 시계 주입) | 각 영역 `tests/test_no_real_time.py` · `test_timing_table.py` · `timing.test.ts` · survey `test_structure.py::test_components_never_read_the_time_module_or_the_real_clock_config`, 표 `tests/TIMING.md` | 있음(영역마다 이름 다름) |
| 3 | 생산자는 내보내기 전에 계약으로 검증, 받는 쪽은 재검증 안 함 (R7, ADR 0010, CONVENTIONS 3절) | `head/scripts/producer-check.py`(계약 86개의 생산자 표 `head/shared/producers.json` ↔ 생산자 동작 코드의 참조 대조) + 경로별 openit_link Route `response_schema`/`request_schema`, 영역 생산자 검증 시험 | 있음(참조 대조: 문자열 참조가 있으면 통과하므로 '검증 호출'까지는 경로별 시험이 본다) |
| 4 | 시간 사슬: 화면 대기 > gateway > 서버 요청 마감 > 이웃·모델 호출 (CONVENTIONS 시간표, D119, D120) | deploy `scripts/test_time_chain.py`(ProxyChain: 모든 reverse_proxy, model-serving 상한), 영역 노출 선언 시험(`test_exposure*`, `test_exposure_budget.py`), deploy `check-exposure` | 있음 |
| 5 | 고정 버전 일치 (기준표 `deploy/scripts/lib.sh`: DEPLOY_BC_TAG, LINK, DEPLOY_MR_TAG, DEPLOY_SS_TAG; model-runtime의 Dockerfile ARG 포함) | deploy `scripts/check-versions.sh`, link 고정 점검(`check-link-pins.sh`, E2E 시작 전), consistency_check(공개 이름). 고정을 올린 뒤에는 각 영역 작업 폴더에서 `scripts/setup-env.sh`를 다시 돌린다 — check-all은 작업 폴더 venv로 시험하므로 옛 패키지가 남으면 거짓 실패(2026-10-31 15:17 사례) | 있음 |
| 6 | 상시 서비스 재시작 정책 (U17) | deploy `scripts/test_compose_restart_policy.py` | 있음 |
| 7 | 서비스 목록 단일 정본(계약 PublishRequest.service ↔ lib.sh) (U46) | deploy `scripts/test_services_enum.py` | 있음 |
| 8 | 영역 전체 시험이 모두 동시에 돌아도 통과 | deploy `scripts/check-all.sh --strict`(E2E 시작 점검) | 있음 |
| 9 | 영역 사이 끝까지 맞물림 | deploy `scripts/e2e.sh` | 있음 |


헤드 점검(`structure-check.py`, `producer-check.py`)은 영역이 head를 읽을 수 없으므로(루트 CLAUDE.md 읽기 허용 목록) deploy check-all에 넣지 않고, 헤드가 "완료"를 말하기 전에 직접 돌려 통과를 확인한다.
