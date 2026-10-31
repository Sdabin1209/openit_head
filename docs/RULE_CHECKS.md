# 규칙 ↔ 자동 점검 대응표

목적: 규칙마다 그것을 기계로 확인하는 점검을 하나 이상 둔다. 점검이 없는 규칙은 지켜지는지 알 수 없으므로 "완료"를 말하기 전에 이 표의 모든 행이 `있음`이고 통과해야 한다. 이 표에 없는 문제는 놓친 결함이 아니라 아직 정하지 않은 요구이며, 사용자 결정으로 올린다(2026-10-31).

| # | 규칙(정본) | 점검(어디서 돌아가나) | 상태 |
|---|---|---|---|
| 1 | 구조: schemas/·types/·components/·wiring/, 컴포넌트끼리 import 금지, HTTP는 link_*만 (D104, D117 DESIGN.md 6절) | `head/scripts/structure-check.py` + 각 영역 `tests/test_structure.*` | 있음 |
| 2 | 시험 판정에 실제 시간 없음, 컴포넌트는 시계를 주입받음 (U422, ADR: 영역별 시계 주입) | 각 영역 `tests/test_no_real_time.py` · `test_timing_table.py` · `timing.test.ts` · survey `test_structure.py::test_components_never_read_the_time_module_or_the_real_clock_config`, 표 `tests/TIMING.md` | 있음(영역마다 이름 다름) |
| 3 | 생산자는 내보내기 전에 계약으로 검증, 받는 쪽은 재검증 안 함 (R7, ADR 0010, CONVENTIONS 3절) | 경로별: openit_link Route `response_schema`/`request_schema`, 영역 `test_producer_validation.py`·`test_response_schemas.py`·`test_producer_contract_checks.py` 등. 전체 대조: `head/scripts/schema-usage.py`(문자열 이름 기준) + 2026-10-31 헤드 수동 대조(36개) | 부분: 계약 85개 전체를 기계로 대조하는 점검은 없음 — 생산자 표가 계약에 기계가 읽는 형태로 없다 |
| 4 | 시간 사슬: 화면 대기 > gateway > 서버 요청 마감 > 이웃·모델 호출 (CONVENTIONS 시간표, D119, D120) | deploy `scripts/test_time_chain.py`(ProxyChain: 모든 reverse_proxy, model-serving 상한), 영역 노출 선언 시험(`test_exposure*`, `test_exposure_budget.py`), deploy `check-exposure` | 있음 |
| 5 | 고정 버전 일치 (계약 v3.1.1, link v0.4.1, model-runtime v0.11.7, survey-schema-v3.0.0; 기준표 `deploy/scripts/lib.sh`) | deploy `scripts/check-versions.sh`, link 고정 점검, consistency_check(공개 이름) | 있음 |
| 6 | 상시 서비스 재시작 정책 (U17) | deploy `scripts/test_compose_restart_policy.py` | 있음 |
| 7 | 서비스 목록 단일 정본(계약 PublishRequest.service ↔ lib.sh) (U46) | deploy `scripts/test_services_enum.py` | 있음 |
| 8 | 영역 전체 시험이 모두 동시에 돌아도 통과 | deploy `scripts/check-all.sh --strict`(E2E 시작 점검) | 있음 |
| 9 | 영역 사이 끝까지 맞물림 | deploy `scripts/e2e.sh` | 있음 |

3번의 "부분"을 닫으려면 계약 스키마마다 생산자를 기계가 읽는 형태(예: 스키마의 `x-producer`)로 적어야 하는데, 계약은 v3.1.1로 고정이라 지금은 넣지 않는다. 대신 2026-10-31 수동 대조 결과(생산자 검증 없음 14건 → U424·U426에서 모두 고침)를 근거로 둔다. 다음 계약 판에서 `x-producer`를 넣고 schema-usage가 생산자 쪽 동작 코드 검증을 강제하게 한다.
