# 코드 단계 끝 조건 대장 (계약 v3.4.7) — 헤드가 새 clone 으로 재현한 것만 "끝"

| 영역 | 커밋 | 시험 | 스모크 | 헤드 재현(워크스페이스 배치 새 clone) | 상태 |
|---|---|---|---|---|---|
| admin-console | a5798eb (wo-344-code, 계약 v3.4.8) | npm test 206 pass·0 fail rc=0, tsc rc=0 | SMOKE OK rc=0 (smoke-a5798eb) | 07:47 재현 rc=0 | 끝 |
| kiosk-frontend | 6cf878f (wo-344, 계약 v3.4.8) | npm test rc=0, typecheck rc=0, test:image rc=0 (test:dom·test:e2e 는 최종 검증 때 헤드 재현) | SMOKE OK rc=0 | 07:50 재현 rc=0 | 끝(e2e·dom 재현 남음) |
| synthetic-data | dbff5b3 (wo-320c, 계약 v3.4.8·link v0.4.14) | setup-env rc=0, pytest 294 pass·1 skip rc=0 | smoke_service.sh SMOKE_OK rc=0 | 07:47 재현 rc=0 | 끝 |
| 배치(Ansible) | bf1d876 (wo-450-place) | test_placement_areas·names·ops rc=0, test-split-placement·pki-playbook·sslrootcert rc=0, test-split-gateway.sh rc=0(실제 platform 게이트웨이 이미지) | — | 헤드 미재현 | 코드 끝, 아래 할 일 남음 |
| model-runtime | affec9b = v0.11.19 (계약 v3.4.8·link v0.4.14) | setup rc=0, pytest rc=0 | smoke.sh rc=0 | 07:55 재현 rc=0(385 pass) | 끝(3.4.9 뒤 고정만 올린 판 필요) |
| model-lab | ca1d86e (wo-324, 계약 v3.4.8·MR v0.11.19; a349143 뒤 고정 파일만, 헤드 diff 확인) | a349143 에서 setup·pytest 393·smoke rc=0 재현 | SMOKE_OK | 07:51 재현(a349143) | 3.4.9 고정 뒤 재현 |
| release-gate | cb5d1d4 (wo-344-code, v3.4.8·v0.4.14·MR v0.11.19) | pytest(PG) 1043 pass rc=0(영역 보고) | 깨끗한 clone smoke rc=0(영역 보고) | 헤드 미재현 | 실제 restic 왕복·R10.5 변이 남음 |
| ops-feedback | a054593 (wo-c2-code, v3.4.8·v0.4.14) | pytest(PG) 894 pass 1 skip rc=0, 변이 41건, 실제 restic 왕복(영역 보고) | smoke rc=0(영역 보고) | 헤드 미재현 | skip 1 이유·restore 잡 남음 |

## 최종 검증 단계에서 할 일(코드 단계에서 할 수 없는 것, 빼지 않는다)
- model-lab: 기존 모델 패키지를 lineage.question_sets 를 채운 새 버전으로 다시 게시(학습 서버 어댑터 읽기, 쓰기는 ~/dabin 안만, deploy 스택의 model-registry 필요). 절차는 model-lab docs.
- kiosk-frontend: test:dom·test:e2e 헤드 재현.
- 배치: test-split-gateway.sh 를 자체 점검 목록에 등록(잠금 파일에 AREA_GATEWAY_IMAGE 줄이 생긴 뒤), 실제 <서비스>-cert·step-ca 와 연결한 게이트웨이 인증서 갱신 확인.
- platform: 나가는 쪽 전용 게이트웨이(학습 서버) 지원 — 지시함 07:45.
- platform: tests/test_area_gateway.py 가 이웃 작업 트리에 기대던 결함(헤드 재현 07:50 rc=1) 고침 확인.
- 모든 DB 영역(survey·release-gate·question-authoring·ops-feedback): restore 잡 + 실제 rest-server backup→restore 왕복 시험(08:00 추가 지시, 계약 DATA_OWNERSHIP 백업 행). 백업 저장소 append-only 안 씀(platform).
