# 코드 단계 끝 조건 대장 (계약 v3.4.7) — 헤드가 새 clone 으로 재현한 것만 "끝"

| 영역 | 커밋 | 시험 | 스모크 | 헤드 재현(워크스페이스 배치 새 clone) | 상태 |
|---|---|---|---|---|---|
| admin-console | e8b6a8b (wo-344-code, v3.4.9) | 헤드 새 clone: npm ci·test·tsc rc=0 | scripts/smoke.sh(정적 서버 시험 포함) 3회 연속 rc=0 | 11:44 재현 rc=0 | 끝. 영역 에이전트 첫 스모크 1회 rc=1(컨테이너 서버는 떴는데 호스트에서 /healthz 접속 안 됨, 부하 load≈14 시각) — 원인 미규명, 재발 시 docker 포트 게시부터 본다 |
| kiosk-frontend | da40216 (wo-344, v3.4.9) | 헤드 새 clone: npm ci·test·typecheck·test:image·test:dom·test:e2e 모두 rc=0 | smoke rc=0 | 11:49 재현 rc=0 | 끝(dom·e2e 재현 포함) |
| synthetic-data | 8a5bff7 (wo-320c, v3.4.9·v0.4.15) | 헤드 새 clone: setup rc=0, pytest 294 pass 1 skip rc=0 — skip: SD_REFERENCE_DATA_DIR(실제 참조 자료 경로) 없음 | smoke_service.sh rc=0 | 11:49 재현 rc=0 | 끝. skip 1 은 실제 참조 자료가 있는 곳에서만 도는 시험(최종 검증 때 자료 위치 확인) |
| 배치(Ansible) | bf1d876 (wo-450-place) | test_placement_areas·names·ops rc=0, test-split-placement·pki-playbook·sslrootcert rc=0, test-split-gateway.sh rc=0(실제 platform 게이트웨이 이미지) | — | 헤드 미재현 | 코드 끝, 아래 할 일 남음 |
| model-runtime | 13b3569 = v0.11.20 (v3.4.9·v0.4.15) | 헤드 새 clone: setup rc=0, pytest 385 pass 2 skip rc=0 — 같은 clone 에서 skip 난 두 파일만 다시 돌리니 50 pass 0 skip(setup-env 태그 받기 재시도 실패 skip 이 부하 때 남, 원인 미규명) | smoke.sh rc=0 | 11:46 재현 rc=0 | 끝 |
| model-lab | 48f30fd (wo-324, v3.4.9·v0.4.15·MR v0.11.20) | 헤드 새 clone: setup rc=0, pytest 393 pass 0 skip rc=0 | smoke_registry.sh rc=0 | 11:46 재현 rc=0 | 끝(기존 패키지 재게시는 최종 검증) |
| release-gate | 05ec36d (wo-344-code, v3.4.9·v0.4.15·MR v0.11.20) | 헤드 새 clone: setup rc=0, pytest(PG) 1053 pass 48 skip rc=0 — skip 은 전부 저장소 조합(메모리·SQLite·PG 전용) 매개변수, 환경 없음 skip 0 | smoke.sh SMOKE OK rc=0 | 11:47 재현 rc=0 | 끝 |
| ops-feedback | 3e7cfa0 (wo-c2-code, v3.4.9·v0.4.15; 시험 root 파일 수정) | 헤드 새 clone: setup rc=0, dev-postgres.sh 898 pass 0 skip rc=0, 실행 뒤 새 root 소유 파일 0 | smoke.sh SMOKE OK rc=0 | 12:38 재현 rc=0 | 끝 |
| platform | 651df91 (master, v3.4.9) | 헤드 새 clone: setup rc=0, pytest 36 pass rc=0, test-gateway-auth rc=0, test-idp-smoke(실제 Keycloak) rc=0 | scripts/smoke.sh rc=1 두 번(public-ingress /healthz 000) | 13:01 | 스모크 결함 platform 수정 중 |
| survey-service | 6ba8cbc (wo-344-code, v3.4.9·v0.4.15·MR v0.11.20) | 헤드 새 clone(PG): 전체 시험 rc=0, skip 5 — 4 실제 참조 자료 경로 없음, 1 HEAD 에 스키마 태그 없음(태그 커밋 전용 시험) | smoke.sh SMOKE OK rc=0 | 12:18 재현 rc=0 (앞 두 번 rc=1 은 Docker Desktop 포트 전달, 헤드 미러 설정 누락) | 0f1f926(시험 root 파일 정리) 재현 남음 |
| question-authoring | 1862a4b (wo-321-code, v3.4.9·v0.4.15) | 헤드 새 clone: setup rc=0, 자기 dev-postgres.sh 로 PG 포함 1034 pass 0 skip rc=0 | SMOKE_DB=postgres rc=0, sqlite rc=0 | 13:02 재현 rc=0 | 끝 |

## 최종 검증 단계에서 할 일(코드 단계에서 할 수 없는 것, 빼지 않는다)
- model-lab: 기존 모델 패키지를 lineage.question_sets 를 채운 새 버전으로 다시 게시(학습 서버 어댑터 읽기, 쓰기는 ~/dabin 안만, deploy 스택의 model-registry 필요). 절차는 model-lab docs.
- kiosk-frontend: test:dom·test:e2e 헤드 재현.
- 배치: test-split-gateway.sh 를 자체 점검 목록에 등록(잠금 파일에 AREA_GATEWAY_IMAGE 줄이 생긴 뒤), 실제 <서비스>-cert·step-ca 와 연결한 게이트웨이 인증서 갱신 확인.
- platform: 나가는 쪽 전용 게이트웨이(학습 서버) 지원 — 지시함 07:45.
- platform: tests/test_area_gateway.py 가 이웃 작업 트리에 기대던 결함(헤드 재현 07:50 rc=1) 고침 확인.
- 모든 DB 영역(survey·release-gate·question-authoring·ops-feedback): restore 잡 + 실제 rest-server backup→restore 왕복 시험(08:00 추가 지시, 계약 DATA_OWNERSHIP 백업 행). 백업 저장소 append-only 안 씀(platform).
- 시험 흔들림 공통 원인(12:00 확인): 이 PC 의 Docker Desktop 호스트 포트 전달이 부하 때 늦거나 빈 응답(admin 스모크 1회, survey 일회용 PG 2건, QA 브라우저). 제품 결함 아님. 시험은 호스트 포트를 거치지 않는 쪽(같은 docker 네트워크)으로 고친다 — QA 지시함.
