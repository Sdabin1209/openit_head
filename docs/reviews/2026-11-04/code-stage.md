# 코드 단계 끝 조건 대장 (계약 v3.4.7) — 헤드가 새 clone 으로 재현한 것만 "끝"

| 영역 | 커밋 | 시험 | 스모크 | 헤드 재현(워크스페이스 배치 새 clone) | 상태 |
|---|---|---|---|---|---|
| admin-console | 2cce473 (wo-344-code, v3.4.12) | 헤드 새 clone: ci·test·tsc rc=0 | smoke.sh rc=0 | 16:18 재현 rc=0 | 끝 |
| kiosk-frontend | 46ffc75 (wo-344, v3.4.12) | 헤드 새 clone: ci·test·typecheck·test:image·test:dom·test:e2e rc=0 | smoke rc=0 | 16:18 재현 rc=0 | 끝 |
| synthetic-data | b8b3238 (wo-320c, v3.4.12·v0.4.18) | 헤드 새 clone: setup·pytest rc=0 | smoke_service.sh rc=0 | 16:18 재현 rc=0 | 끝 |
| 배치(Ansible) | bf1d876 (wo-450-place) | test_placement_areas·names·ops rc=0, test-split-placement·pki-playbook·sslrootcert rc=0, test-split-gateway.sh rc=0(실제 platform 게이트웨이 이미지) | — | 헤드 미재현 | 코드 끝, 아래 할 일 남음 |
| model-runtime | b6d99ae = v0.11.21 (v3.4.12·v0.4.18) | 헤드 새 clone: setup rc=0, pytest 385 pass 2 skip rc=0 — skip: xgrammar 없음(GPU 쪽 선택 의존), MODEL_RUNTIME_REFERENCE_DATA_DIR 없음 | smoke.sh rc=0 | 16:30 재현 rc=0 | 끝 |
| model-lab | 48f30fd (wo-324, v3.4.9·v0.4.15·MR v0.11.20) | 헤드 새 clone: setup rc=0, pytest 393 pass 0 skip rc=0 | smoke_registry.sh rc=0 | 11:46 재현 rc=0 | 끝(기존 패키지 재게시는 최종 검증) |
| release-gate | 9005a46 (wo-344-code, v3.4.12·v0.4.18·MR v0.11.21; release-gate-db 이미지) | 헤드 새 clone: setup rc=0, PG 포함 1064 pass 50 skip rc=0 — 추가 skip 2 는 재현 공간 옆 리포에 v0.11.21 태그가 없던 탓(태그 받은 뒤 그 파일 21 pass 0 skip) | 앱 smoke rc=0, smoke-db.sh(variant db) rc=0 | 16:45 재현 rc=0 | 끝 |
| ops-feedback | 387a4dc (wo-c2-code, v3.4.12·v0.4.18; ops-feedback-db 이미지) | 헤드 새 clone: setup rc=0, dev-postgres.sh 전체 시험 rc=0 | smoke.sh rc=0 | 16:52 재현 rc=0 | 끝 |
| platform | 5a3b9f7 (master, v3.4.9; 651df91 뒤 스모크 준비 확인 결함 수정 5eb788f, egg-info 추적 제거 5a3b9f7 — 헤드 diff 확인: .gitignore 와 산출물 삭제뿐) | 헤드 새 clone(651df91): setup rc=0, pytest 36 pass rc=0, test-gateway-auth rc=0, test-idp-smoke(실제 Keycloak) rc=0 | 5eb788f: scripts/smoke.sh 2회 연속 rc=0(변형 5개 PASS 15) | 13:12 재현 rc=0 | 끝 |
| survey-service | 724a5e8 (wo-344-code, v3.4.12·v0.4.18·MR v0.11.21; survey-db 이미지) | 헤드 새 clone(PG): setup rc=0, 전체 시험 rc=0, skip 5(4 실제 참조 자료 경로 없음, 1 HEAD 에 스키마 태그 없음) | smoke.sh rc=0 | 16:50 재현 rc=0 | 끝 |
| question-authoring | 13ad63a (wo-321-code, v3.4.12·v0.4.18; question-authoring-db 이미지) | 헤드 새 clone: setup rc=0, 자기 dev-postgres.sh PG 포함 1043 pass 0 skip rc=0 | SMOKE_DB=postgres rc=0, sqlite rc=0 | 16:39 재현 rc=0 | 끝 |

## 최종 검증 단계에서 할 일(코드 단계에서 할 수 없는 것, 빼지 않는다)
- model-lab: 기존 모델 패키지를 lineage.question_sets 를 채운 새 버전으로 다시 게시(학습 서버 어댑터 읽기, 쓰기는 ~/dabin 안만, deploy 스택의 model-registry 필요). 절차는 model-lab docs.
- kiosk-frontend: test:dom·test:e2e 헤드 재현.
- 배치: test-split-gateway.sh 를 자체 점검 목록에 등록(잠금 파일에 AREA_GATEWAY_IMAGE 줄이 생긴 뒤), 실제 <서비스>-cert·step-ca 와 연결한 게이트웨이 인증서 갱신 확인.
- platform: 나가는 쪽 전용 게이트웨이(학습 서버) 지원 — 지시함 07:45.
- platform: tests/test_area_gateway.py 가 이웃 작업 트리에 기대던 결함(헤드 재현 07:50 rc=1) 고침 확인.
- 모든 DB 영역(survey·release-gate·question-authoring·ops-feedback): restore 잡 + 실제 rest-server backup→restore 왕복 시험(08:00 추가 지시, 계약 DATA_OWNERSHIP 백업 행). 백업 저장소 append-only 안 씀(platform).
- 시험 흔들림 공통 원인(12:00 확인): 이 PC 의 Docker Desktop 호스트 포트 전달이 부하 때 늦거나 빈 응답(admin 스모크 1회, survey 일회용 PG 2건, QA 브라우저). 제품 결함 아님. 시험은 호스트 포트를 거치지 않는 쪽(같은 docker 네트워크)으로 고친다 — QA 지시함.
