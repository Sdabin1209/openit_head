# 규칙 전수 대응표(생성물, U76)

생성: `python3 scripts/rules-coverage.py`. 입력은 스크립트 머리 설명. **손으로 고치지 않는다.** 규칙을 추가하면 다시 만든다(`--check` 가 RULE_CHECKS 의 점검이다).

규칙 178개: 점검 있음 81, **점검 없음 21**, 기록 76. (헤드 CLAUDE/루트 CLAUDE 규칙은 C·H 접두)

대응 규칙: 규칙 문장과 점검 설명이 같은 ID(D##·U##·L##·G##·ADR)를 가리킬 때만 대응으로 센다. 낱말 겹침은 쓰지 않는다. `RECORD` 는 점검 대상이 아닌 결정 기록(스크립트의 RECORD_IDS, 이유 포함).

| ID | 규칙(앞 60자) | 대응 점검 | 상태 |
|---|---|---|---|
| D01 | 구조 | - | RECORD: 구조 선언(영역 수). 점검은 D104 구조 규칙이 맡는다 |
| D02 | 소통 방식 | - | RECORD: D49 로 대체(저장소 통신 폐기) |
| D03 | 게이트 판정 | survey-service/tests/test_role_token_strength.py | 있음 |
| D04 | 리포지토리 | - | RECORD: 리포 목록 선언. areas.json 이 정본 |
| D05 | 경계 방식 | - | RECORD: 경계 방식 선택 기준(판단 절차) |
| D06 | 공유 라이브러리 | - | RECORD: turn-engine 분리. D109 로 퇴역 |
| D07 | 배포 | - | RECORD: 배포 두 축 설계 선언(코드/내용). 점검은 publish-images·릴리스 흐름 시험이 맡으나 ID 미표기 → 점검 필요로 두지 않고 설계 기록으로 분류 |
| D08 | 관리자 콘솔 | - | RECORD: 관리자 콘솔 위치 선언 |
| D09 | 작업 방식 | - | RECORD: 작업 방식(헤드/영역 역할) |
| D10 | 장애 | - | RECORD: 비보증 선언(서버 전체 중단) |
| D11 | 배포 환경 | - | RECORD: 배포 환경 선언 |
| D12 | Frontend | - | RECORD: 프런트 선택 기록 |
| D13 | 모델 평가의 문항 접근 | - | RECORD: 모델 평가의 문항 접근 범위 선언(model-lab 평가 코드가 따름, ID 미표기) |
| D14 | 계약 버전 체계 | RULE_CHECKS#14 | 있음 |
| D15 | 비식별 처리의 위치 | ops-feedback/tests/test_raw_access.py | 있음 |
| D16 | Trace 전달 보장 | survey-service/tests/test_trace_export.py | 있음 |
| D17 | 문항 변경 분류 | question-authoring/tests/test_classify.py | 있음 |
| D18 | SDK 언어와 배포 | - | RECORD: SDK 언어 선택 기록 |
| D19 | 계약 소유와 위치 | - | RECORD: 계약 소유·위치 선언(구조 규칙 6 이 점검) |
| D20 | 경계 계약의 세부 | - | RECORD: 계약 세부 서술 |
| D21 | 문진 스키마 변경 담당 | - | RECORD: 문진 스키마 담당 선언(C31 과 같음) |
| D22 | 컨테이너화와 개발 | RULE_CHECKS#13 | 있음 |
| D23 | 문진 스키마의 위치 | survey-service/tests/test_readyz_db_outage.py | 있음 |
| D24 | 이미지 레지스트리와 빌드 | RULE_CHECKS#5 | 있음 |
| D25 | 경계 계약의 불변성 | survey-service/tests/test_audit_fixes.py | 있음 |
| D26 | 계약 진화 규칙 | synthetic-data/tests/test_job_http_publish.py | 있음 |
| D27 | 영역 경계 명세 | - | RECORD: 경계 명세 방식 기록 |
| D28 | 새 리포지토리와 문진 스키마 최소화 | question-authoring/tests/test_image_labels.py | 있음 |
| D29 | 문진 스키마는 survey-service에 포함 | - | RECORD: 문진 스키마 위치 선언 |
| D30 | 임상 승인 (O12 닫음) | - | RECORD: D92 로 대체됨 |
| D31 | 문항 자료 등록 (O15 닫음) | - | RECORD: 자료 등록 방식 결정(저작 영역 시험이 맡음, ID 미표기) |
| D32 | 처음 보는 문항에 대한 일반화 | model-lab/tests/test_d32_generalization.py | 있음 |
| D33 | 문항 자료 형식 (O18 닫음) | - | RECORD: 자료 형식 결정(저작 시험) |
| D34 | 해시의 기준 구현 | RULE_CHECKS#15 | 있음 |
| D35 | model-runtime 세부 | - | RECORD: model-runtime 세부 결정 기록 |
| D36 | 모델 출력 보호 | RULE_CHECKS#16 | 있음 |
| D37 | 커밋 규칙 | RULE_CHECKS#12 | 있음 |
| D38 | 완성 목표 | - | RECORD: 완성 목표 서술 |
| D39 | 자동화 원칙 | - | 없음 |
| D40 | 서빙 서버와 학습·평가 서버 (가정) | - | RECORD: 서버 가정 |
| D41 | push 허락 | - | RECORD: push 허락 절차(사람 절차, 기계 점검 불가) |
| D42 | 경계 계약 1.0 확정 | - | RECORD: 계약 1.0 릴리스 기록 |
| D43 | 경계 계약 1.1 | - | RECORD: 계약 1.1 릴리스 기록 |
| D44 | 라이브러리 태그와 정답 예시 | RULE_CHECKS#5 | 있음 |
| D45 | I9 역할별 설정 | RULE_CHECKS#16 | 있음 |
| D46 | 릴리스 적재 정책 | survey-service/tests/test_loader_retry.py | 있음 |
| D47 | GPU 호스트 사용 | - | RECORD: GPU 호스트 사용 기록 |
| D48 | 첫 추론 백엔드와 한계 | - | RECORD: 첫 백엔드와 한계 기록 |
| D49 | 영역 사이 호출은 HTTP | RULE_CHECKS#1 | 있음 |
| D50 | 저장소 계정과 DB (O10 닫음) | - | RECORD: 저장소 계정 결정 기록(ops L08 시험이 일부) |
| D51 | 경계 계약 1.2와 클라이언트 | - | RECORD: 계약 1.2 릴리스 기록 |
| D52 | E2E 막힘의 결정 | - | RECORD: E2E 막힘 때의 결정 기록 |
| D53 | 출고는 사람이 정한다 (O11 닫음) | release-gate/tests/test_gate_flow.py | 있음 |
| D54 | 서버 토폴로지(가정) | - | RECORD: 토폴로지 가정 |
| D55 | 공개 API와 실패 사례 입력 (O06, O19 일부) | - | RECORD: 공개 API 범위 결정(계약 PUBLIC_API 시험이 맡음) |
| D56 | 복구 범위 (O16 일부) | RULE_CHECKS#17 | 있음 |
| D57 | O19 잠정 결정: B안 | - | RECORD: O19 잠정안 기록 |
| D58 | 계약 1.3.1 정리 | - | RECORD: 계약 1.3.1 기록 |
| D59 | 사용자 답변 정리 (2026-10-15) | - | RECORD: 사용자 답변 정리 |
| D60 | 문진 런타임 동결 | - | RECORD: 런타임 동결 기록 |
| D61 | 목표는 작동하는 파이프라인 (모델 성능 비교 중단) | - | RECORD: 목표 서술 |
| D62 | 문진 런타임에 LangGraph 사용, D60 동결 해제 | boundary-contracts/tests/test_survey_env_302.py | 있음 |
| D63 | 이미지 라벨 확장 | - | 없음 |
| D64 | 직원 알림은 웹 화면 + 푸시 (가정) | survey-service/tests/test_staff_alerts.py | 있음 |
| D65 | 프론트는 떼어 낼 수 있는 별도 영역 (`kiosk-frontend`) | - | RECORD: 영역 신설 기록 |
| D66 | 공개 API 보완 (kiosk-frontend CR-001~003 회신) | survey-service/tests/test_public_api_v132.py | 있음 |
| D67 | 작업 단위와 E2E 개선 | - | RECORD: 작업 단위 기록 |
| D68 | 운영 콘솔 영역 (`admin-console`)과 승인 화면 | - | RECORD: 영역 신설 기록 |
| D69 | 승인 요청의 해시·충돌 사유·승인자 식별 (admin-console CR-001 회신) | release-gate/tests/test_gate_flow.py | 있음 |
| D70 | 승인 화면 게이트웨이 구성 확정 (deploy CR-D19 회신) | - | 없음 |
| D71 | 실패 사례 검토 화면 결정 (admin-console CR-003 회신) | - | 없음 |
| D72 | 추론 서버는 위치에 독립이다 / 데모에 실제 LLM | RULE_CHECKS#10<br>deploy/scripts/test-inference-location.sh | 있음 |
| D73 | 서버 디스크 사용 위임 | - | RECORD: 디스크 사용 위임 |
| D74 | 서비스 구조를 학습 데이터셋 v2 기준으로 바꾼다 | model-lab/tests/test_transform_v2.py<br>release-gate/tests/test_v2_contract.py<br>survey-service/tests/test_extraction.py<br>survey-service/tests/test_orchestrator.py | 있음 |
| D75 | 계약 2.0.0의 열린 항목 다섯 가지 | model-lab/tests/test_packager_v2.py<br>release-gate/tests/test_v2_contract.py<br>survey-service/tests/test_inference_client.py<br>turn-engine/tests/test_validation.py | 있음 |
| D76 | 문항 순서·건너뛰기 표의 소유 / 영역 이전 순서 (turn-engine CR-010 회신) | survey-service/tests/test_extraction.py | 있음 |
| D77 | 서빙의 모델 입력 글자는 학습 데이터와 글자 단위로 같아야 한다 / 학습 정본 | model-runtime/tests/test_prompt4.py | 있음 |
| D78 | 학습 정본과 비전문가 대상 / 빈 곳 대장 / 판단 위임 | - | RECORD: 정본·대상·위임 선언 |
| D79 | 문진 스키마 정수 버전 / 직원 알림 입력원 / 서비스 구조 이전 후속 | - | RECORD: 정수 버전 1 유지 결정(CONVENTIONS 12절·G11 로 규칙화) |
| D80 | CONTRACT_COMPAT의 버전 비교는 완전 일치로 유지한다 | release-gate/tests/test_new_tags.py | 있음 |
| D81 | 프로파일별 기반 모델: `gpu-12g`는 가벼운 Qwen3, 학습된 어댑터는 큰 GPU에서 | - | RECORD: 프로파일 선택 기록(model-runtime 프로파일 시험이 맡음, ID 미표기) |
| D82 | 제약 디코딩이 `pattern`·`minItems`를 지키게 한다(relax-2): model-runtime | RULE_CHECKS#16 | 있음 |
| D83 | `allOf`/`if-then` 의미 규칙을 제약 디코딩이 지키는 형태로 바꿔 건다: model-runtim | model-runtime/tests/test_anyof_constraint.py | 있음 |
| D84 | 비밀(서비스 토큰·salt)은 환경 변수가 아니라 **파일**로 받는다: 서비스는 `<이름>_FILE`로 받 | deploy/scripts/test_e2e_diag_safety.py<br>model-lab/tests/test_gateway_publish.py<br>model-lab/tests/test_secrets.py<br>model-runtime/tests/test_secrets_hidden.py | 있음 |
| D85 | 사용자 지시(2026-10-27)로 결함 목록의 결정을 닫는다 | deploy/scripts/test-gateway-auth.sh<br>release-gate/tests/test_actor.py<br>survey-service/tests/test_results_signals_retention.py | 있음 |
| D86 | 장애 대응 정책을 표준 관행으로 정한다(2026-10-28, 헤드 판단. 사용자 결정 항목은 FAULT_PO | survey-service/tests/test_readyz_db_outage.py<br>survey-service/tests/test_turn_db_outage_bounds.py | 있음 |
| D87 | 직원 알림 SSE에 `heartbeat`, `resync` 이벤트를 추가한다(2026-10-28, 헤드 판단 | survey-service/tests/test_fault_a6_a8_a10.py<br>survey-service/tests/test_staff_alerts.py | 있음 |
| D88 | 전수 점검(AUDIT_SUMMARY)의 사용자 결정 항목 U1~U12를 **가장 표준적인 방법으로 정해 적용 | boundary-contracts/tests/test_decide_303.py<br>question-authoring/tests/test_ops_hardening.py<br>question-authoring/tests/test_two_person.py<br>release-gate/tests/test_audit_fixes.py | 있음 |
| D89 | 구조 선택에는 항상 '왜'가 있어야 한다. 영역마다 `docs/adr/`에 ADR(Nygard 형식: 상태, | deploy/scripts/test-hash-password-argv.sh | 있음 |
| D90 | 스키마에서 생성한 검증기(admin-console `generated/contract-validators.c | - | 없음 |
| D91 | synthetic-data의 v1 생성 경로(CR-007)는 **바로 삭제하지 않고 폐기 표시만 한다**(2 | - | RECORD: L17 처리 기록(완료) |
| D92 | **D30을 대체한다**: 임상 근거 승인은 저자와 다른 검수자가 한다(4-eyes, 기본 켬, `QA_RE | question-authoring/tests/test_two_person.py | 있음 |
| D93 | **G04 respond 대체 문구**: 재료가 없을 때의 문구는 현행 "죄송합니다. 다시 한 번 말씀해 주 | model-runtime/tests/test_fallback_d93.py | 있음 |
| D94 | **G05 v1 G1(응답 숫자가 재료에 있는지) 검사는 v2 런타임에 두지 않는다. 대신 평가 지표 `un | model-lab/tests/test_metrics_v2.py | 있음 |
| D95 | **G12 되묻기 상한 N=3 확정**: N번 되묻고 N+1번째에 직원을 부른다(정지 `PAUSED_RISK | survey-service/tests/test_reask_limit.py<br>survey-service/tests/test_reask_limit_result.py | 있음 |
| D96 | **D-C: METRICS.md는 `metrics-v2-proposal.md`의 처분대로 v2로 바꾼다.** | model-lab/tests/test_metrics_v2.py | 있음 |
| D97 | **U11 의미 위반율 `semantic_violation_rate`를 평가에 넣는다**(그룹 `ACCURA | model-lab/tests/test_metrics_v2.py | 있음 |
| D98 | **D-E: 회귀 평가가 읽는 TurnTrace 입력 키는 `extract_input`, `extract_o | model-lab/tests/test_metrics_v2.py | 있음 |
| D99 | **D-F: turn-engine에 QuestionBank에서 `QuestionFlowTable`을 만드는  | - | RECORD: D-F 닫음 |
| D100 | **D-G: I2 DatasetStore도 HTTP로 한다**(D49와 같은 방식). 경로는 I3(Model | model-lab/tests/test_metrics_v2.py<br>synthetic-data/tests/test_service_contract.py | 있음 |
| D101 | **D-H: admin-console 생성 검증기는 커밋한다**: D90의 재확인이며 새 결정이 아니다(20 | - | 없음 |
| D102 | **D-I: 결과가 병원으로 나가는 경로 — 당겨 가기(pull)는 이미 정의돼 있어 범위 안, 밀어 넣기( | - | RECORD: D-I pull 기본(결정 대기) |
| D103 | **L03·L05·L06은 '수용된 한계 + 문서화'로 결정해 닫는다. L08은 닫지 않고 순서만 정한다** | - | RECORD: 수용된 한계 기록 |
| D122 | **원격 추론 서버는 게이트웨이의 기계 토큰 경로로 release-gate를 읽는다**(사용자 2026-11 | RULE_CHECKS#10 | 있음 |
| D123 | **시험은 샌드박스 방식**(사용자 지시 2026-11-01): 제품(운영 compose·config)에는  | RULE_CHECKS#11 | 있음 |
| D124 | **저자 환류 읽기 `GET /v1/signals`를 게이트웨이 저자 경로로 연다**(헤드 2026-11-0 | - | 없음 |
| D125 | **시간 상한: 목표(SLO)와 실패 판정을 나눈다**(사용자 지시 2026-11-02 00:3x: "응답  | deploy/scripts/test_time_chain.py<br>model-runtime/tests/test_deadline_budget.py<br>survey-service/tests/test_inference_time_budget.py<br>survey-service/tests/test_time_chain_vs_contract_u20.py | 있음 |
| D134 | **세 번째 계약(영역 밖에서 컨테이너에 주입하는 것)은 환경 변수만이 아니라 주입 전체다**(헤드, 202 | RULE_CHECKS#24 | 있음 |
| D135 | **잡 설정은 구현 모듈 경로가 아니라 역할별 HttpClientSettings 로 이웃을 고른다**(헤드, | - | 없음 |
| D136 | **키오스크 기기 인증은 mTLS(기기 인증서) 하나로**(사용자 결정 2026-11-07 "고쳐야지", 헤 | - | 없음 |
| D107 | **영역 경계 스키마 59개의 계약 승격(구조 규칙 6)**: 헤드 결정(2026-10-29). 각 영역이  | boundary-contracts/tests/test_promoted_schemas.py<br>model-lab/tests/test_u3_contracts.py<br>ops-feedback/tests/test_contract_schemas.py<br>question-authoring/tests/test_contract_u3.py | 있음 |
| D108 | **2.2.0 계약 묶음의 범위 결정**(헤드, 2026-10-29): (1) I9 extract 요청에 ` | model-runtime/tests/test_image_labels.py | 있음 |
| D109 | **turn-engine 퇴역의 2.x 범위**(헤드, 2026-10-29): 계약 2.x의 `turn_en | deploy/scripts/test_e2e_action_rules_version.py<br>model-lab/tests/test_semantic_diff.py<br>survey-service/tests/test_adr10_caller.py | 있음 |
| D110 | **문진 스키마 태그 갱신: survey-schema-v1.1.0**(헤드, 2026-10-29): `sur | - | RECORD: 문진 스키마 태그 기록 |
| D111 | **단위 4(표준 인프라 교체) 범위**: 사용자 확정(2026-10-29 06:35, '둘 다 교체').  | question-authoring/tests/test_server_properties.py | 있음 |
| D112 | **백업 암호와 저장소**: 사용자 확정(2026-10-29 08:43, 'restic + 추가만 저장소') | RULE_CHECKS#17 | 있음 |
| D113 | **키오스크 기기 인증 구현(4b, ADR 0012 실행)**: 계약 2.3.0. 게이트웨이(Caddy)가  | survey-service/tests/test_device_header.py | 있음 |
| D114 | **추론 경로 전송 보안은 TLS(사용자 결정 2026-10-29)**: survey-service → 추론 | RULE_CHECKS#10 | 있음 |
| D115 | **LoRA-A 출력 값 규칙(계약 2.4.0, U32·U33)**(헤드, 2026-10-29): 칸 규격  | question-authoring/tests/test_slot_fields_u32.py | 있음 |
| D116 | **계약 3.0.0을 GPU 일 전에 낸다**(헤드, 2026-10-30, 사용자 기준 'GPU를 뺀 나머지 | - | RECORD: 릴리스 시점 결정 |
| D117 | **영역 설계 규칙(DESIGN.md)**(헤드, 2026-10-30, 사용자와 논의해 확정): 컴포넌트는  | RULE_CHECKS#1<br>deploy/tests/test_structure.py<br>deploy:"$VENV/bin/python" -W ignore "$DEPLOY_ROOT/tests/test_structure.py"<br>model-lab/tests/test_schemas.py | 있음 |
| D118 | **영역 통신 기반 라이브러리 `link`를 둔다**(사용자 승인 2026-10-30): 받는 쪽(WSGI  | question-authoring/tests/test_standards_wo3.py | 있음 |
| D119 | **응답 생성 상한 5초와 시간 상한 사슬 재배분**(사용자 결정 2026-10-30 23:1x): resp | RULE_CHECKS#4<br>release-gate/tests/test_exposure_budget.py | 있음 |
| D120 | **사람용 요청에 서버 쪽 요청 전체 마감(마감 전파)**(헤드 결정 2026-10-31): release- | RULE_CHECKS#4<br>ops-feedback/tests/test_request_deadline.py<br>question-authoring/tests/test_request_deadline.py<br>release-gate/tests/test_deadline_hashing.py | 있음 |
| D121 | **최종 고정 패치 판**(2026-10-31 14:5x): boundary-contracts v3.1.2( | - | RECORD: 고정 판 기록 |
| C1 | 영역은 서로의 구조를 모른다. | RULE_CHECKS#1<br>model-runtime/tests/test_reference_data.py<br>release-gate/tests/test_upstream_faults.py<br>survey-service/tests/test_reference_data.py | 있음 |
| C2 | 영역은 작업의 단위인 컴포넌트를 가진다. | model-lab/tests/test_yaml12.py<br>release-gate/tests/test_upstream_faults.py<br>survey-service/tests/test_device_header.py<br>survey-service/tests/test_skipped_details_u35.py | 있음 |
| C3 | 컴포넌트는 다른 컴포넌트와 독립적이며 서로의 구조를 모른다. | RULE_CHECKS#1<br>release-gate/tests/test_audit_fixes.py<br>release-gate/tests/test_upstream_faults.py | 있음 |
| C4 | 컴포넌트는 자신에게 할당된 입력·출력 스키마와 자신이 할 업무밖에 모른다. | RULE_CHECKS#1<br>release-gate/tests/test_pg_timeouts.py<br>synthetic-data/tests/test_pii_strict_default.py | 있음 |
| C5 | 영역은 자기 컴포넌트 사이의 스키마를 알고, 컴포넌트가 교류할 수 있게 그 스키마를 책임진다. | release-gate/tests/test_upstream_faults.py | 있음 |
| C6 | 영역 간 스키마는 헤드가 책임진다. | RULE_CHECKS#18 | 있음 |
| C7 | 자기 리포지토리 안에서만 일한다. 다른 폴더를 수정하지 않는다. 읽는 것도 `../survey-service | - | RECORD: 자기 리포 안에서만 일한다 — 사람·에이전트 행동 규칙(커밋 작성자 점검 C37 과 리포별 커밋으로 간접 확인) |
| C8 | 문진 스키마와 `boundary-contracts`를 직접 수정하지 않는다(survey-service는 자기 | - | RECORD: 계약·문진 스키마 직접 수정 금지 — 행동 규칙(계약 커밋은 헤드 세션만, 기계 점검 불가) |
| C9 | 영역 리포지토리끼리 코드를 가져오지 않는다. 의존할 수 있는 것은 문진 스키마, boundary-contra | - | 없음 |
| C43 | 받아들이는 조건은 전부 스키마에 둔다. 코드 안에 스키마에 없는 거부 조건을 두지 않고, 같은 뜻의 타입은  | - | 없음 |
| C10 | 문서는 **자기 영역의 사실만** 쓴다. 이웃 영역의 사실(시험 개수, 결과, 상태, 버전)은 복사하지 않고 | RULE_CHECKS#13 | 있음 |
| C11 | 읽지 못한 것이나 확인하지 못한 것을 확인한 것처럼 쓰지 않는다. 확인한 것, 제안, 미정을 구분해서 말한다 | - | RECORD: 행동 규칙(확인 전 말하기 금지) — 기계 점검 불가 |
| C12 | 수용 테스트와 계약 검증을 통과하기 전에 완료했다고 말하지 않는다. | - | RECORD: 행동 규칙(완료 선언 조건) — 열차 절차가 맡음 |
| C13 | 한국어로 답한다. 질문은 한 번에 하나씩 한다. | - | RECORD: 언어·질문 규칙 |
| C14 | 세션은 새 컨텍스트로 시작한다. 맥락은 이 리포지토리의 `CLAUDE.md`와 `docs/brief.md`에 | - | RECORD: 세션 시작 규칙 |
| C15 | 코드·저장소·프로토콜·의존 라이브러리·기본값·한도(timeout, 상한, 보존 기간)를 고른 이유를 사용자가 | - | RECORD: '왜'를 답할 수 있어야 한다 — ADR 존재는 C16 점검 |
| C16 | 영역마다 `docs/adr/`에 ADR(Architecture Decision Record, Nygard 형 | RULE_CHECKS#13 | 있음 |
| C17 | ADR이 필요한 것: 저장소 종류(왜 SQLite/PostgreSQL), 프로토콜·서버 구현(왜 표준 라이브 | RULE_CHECKS#13 | 있음 |
| C18 | 코드의 비자명한 선택에는 그 자리에 한 줄 '왜' 주석을 단다(무엇을 하는지가 아니라 왜 그렇게 하는지).  | - | RECORD: 코드 주석 규칙(수동 검토) |
| C19 | 결정이 바뀌면 ADR을 지우지 않고 새 ADR이 이전 것을 대체(`Supersedes`)한다. | - | RECORD: ADR 대체 규칙(수동 검토) |
| C20 | 헤드의 `DECISIONS.md`는 영역 사이 결정의 기록이고, 영역 내부 구조 선택은 영역의 ADR이 정본 | - | RECORD: 기록 위치 규칙 |
| C21 | 개발은 컨테이너 밖에서 한다(가상환경, 이웃 영역의 메모리 구현). 컨테이너는 개발 환경이 아니라 매 변경마 | - | RECORD: 개발 방식 규칙 |
| C22 | 서비스를 가진 영역은 자기 리포지토리에 `Dockerfile`을 두고, 변경을 완료했다고 말하기 전에 이미지 | RULE_CHECKS#13 | 있음 |
| C23 | 이웃 영역이 필요하면 그 영역의 메모리 구현(가짜 SDK)으로 대신해, 다른 영역 없이 혼자 시험할 수 있어 | - | RECORD: 단독 시험 방식(계약 기준 서버) — 영역 스모크가 맡음 |
| C24 | **docker 호출은 프로젝트 자체 설정만 쓴다(2026-11-05).** 모든 리포의 스크립트·시험이 d | - | 없음 |
| C25 | 이미지는 다음을 지킨다: 설정은 환경 변수로 받는다. **비밀(토큰·salt 등)은 환경 변수가 아니라 파일 | - | 없음 |
| C26 | `boundary-contracts`는 태그로 설치한다(현재 기준은 `deploy/scripts/lib.sh | RULE_CHECKS#5 | 있음 |
| C27 | 라이브러리와 SDK는 Git 태그로 설치하고, 이미지를 빌드할 때 태그를 고정한다. 의존 버전은 잠금 파일로 | RULE_CHECKS#5 | 있음 |
| C28 | 스모크 시험은 고정 포트를 쓰지 않는다. 여러 영역이 같은 서버에서 동시에 돌리면 충돌한다. 호스트 포트를  | RULE_CHECKS#13 | 있음 |
| C29 | 이미지 라벨 키는 `io.openit.service`, `io.openit.revision`, `io.ope | - | 없음 |
| C30 | 영역 사이 호출은 `boundary-contracts/HTTP.md`의 HTTP API로 한다. 서버는 소유 | RULE_CHECKS#1 | 있음 |
| C31 | 영역 안에서 이웃과 통신하는 일은 `link_*` 통신 컴포넌트만 맡는다(D117). 서비스를 가진 영역은  | - | 없음 |
| C32 | jsonschema 검증기는 제품 코드(tests 밖)에서 `boundary_contracts.format_ | RULE_CHECKS#26 | 있음 |
| C33 | 시험은 샌드박스 방식으로 한다(D123). 제품 compose·config에 시험용 포트·플래그·줄을 두지  | - | 없음 |
| C44 | 영역 이미지는 스스로 서는 단위다. 자기 진입점 기본값·`HEALTHCHECK`·`USER`를 갖고, dep | - | 없음 |
| C34 | 이미지는 CI에서 빌드해 digest를 게시한다. 서버 안의 로컬 레지스트리에 올리고 digest를 depl | RULE_CHECKS#5 | 있음 |
| C35 | 문진 스키마(`../survey-service/schema`) 변경은 survey-service가 반영한다( | - | RECORD: 문진 스키마 담당 선언 |
| C36 | 작업 단위가 끝날 때마다 자기 리포지토리에 커밋한다(설계서 한 편, 기능 하나, 시험 통과 한 묶음). 커밋 | - | 없음 |
| C37 | 작성자는 `git -c user.name=Sdabin1209 -c user.email=99588729+Sda | RULE_CHECKS#12 | 있음 |
| C38 | push는 헤드의 허락을 받아 한다(사용자가 헤드에게 위임, D41). 커밋하고 시험이 통과한 상태에서 헤드 | - | RECORD: push 허락(사람 절차) |
| C39 | Python 의존은 리포지토리의 가상환경(`python3 -m venv .venv`)에 설치하고 `.venv | RULE_CHECKS#13 | 있음 |
| C40 | 영역 사이의 자동 연결은 직접 호출이 아니라 **저장소를 보고 일하는 잡**으로 한다. 각 영역은 자기 잡을 | - | 없음 |
| C45 | 시험·잡은 입력을 인자·설정 파일(환경 변수는 스키마에 있는 이름만)로 받고, 상속받은 환경 변수를 통째로  | - | 없음 |
| C41 | 잡을 언제 돌리는지는 deploy의 스케줄러가 정한다. 영역은 스스로 다른 영역을 깨우지 않는다. | - | 없음 |
| C42 | 모델의 성능 시행착오는 설정으로 바꾸며 반복한다. 파이프라인을 손으로 이어 치는 방식은 두지 않는다. | - | RECORD: 모델 시행착오 방식 |
| H1 | 영역 내부 설계와 구현을 정하지 않는다. 컴포넌트 표는 참고용 시드다. | - | RECORD: 헤드 역할 규칙 |
| H2 | 영역 리포지토리의 코드를 수정하지 않는다. 브리프를 넣는 것만 예외다. | - | RECORD: 헤드 역할 규칙 |
| H3 | 사용자의 확인 없이 결정을 기록하거나 구조를 바꾸지 않는다. | - | RECORD: 사용자 확인 절차 |
| H4 | 읽지 못한 것을 읽은 것처럼 쓰지 않는다. 리포지토리에서 확인한 것, 제안, 미정을 항상 구분해 말한다. | - | RECORD: 행동 규칙 |
| H5 | 사용자가 꼭 정해야 하는 결정(운영 정책, 영역의 존치, 환자 안전과 닿는 도메인 결정, 비용·외부 공개)만 | - | RECORD: 질문 범위 규칙 |
| H6 | 경계 계약을 바꿀 때는 영향받는 영역과 호환 여부를 먼저 정리해 보고하고, `../boundary-contr | - | RECORD: 계약 변경 절차(열차) |
| H7 | 질문은 한 번에 하나씩 한다. 한국어로 답한다. | - | RECORD: 언어·질문 규칙 |
| H8 | 일부러 비워 두거나 확인하지 못한 것이 생기면 같은 날 `docs/OPEN_GAPS.md`에 추가한다. "완 | - | RECORD: 대장 기록 절차 |
