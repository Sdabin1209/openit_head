# 코드 단계 끝 조건 대장 (계약 v3.4.7) — 헤드가 새 clone 으로 재현한 것만 "끝"

| 영역 | 커밋 | 시험 | 스모크 | 헤드 재현(워크스페이스 배치 새 clone) | 상태 |
|---|---|---|---|---|---|
| admin-console | a5798eb (wo-344-code, 계약 v3.4.8) | npm test 206 pass·0 fail rc=0, tsc rc=0 | SMOKE OK rc=0 (smoke-a5798eb) | 07:47 재현 rc=0 | 끝 |
| kiosk-frontend | 6cf878f (wo-344, 계약 v3.4.8) | npm test rc=0, typecheck rc=0, test:image rc=0 (test:dom·test:e2e 는 최종 검증 때 헤드 재현) | SMOKE OK rc=0 | 07:50 재현 rc=0 | 끝(e2e·dom 재현 남음) |
| synthetic-data | 9e1bd4e (wo-320c) | setup-env rc=0, pytest 294 pass·1 skip rc=0 | smoke_service.sh SMOKE_OK rc=0 | 07:28 재현 rc=0 | 3.4.8 고정 올림 대기 |
| 배치(Ansible) | bf1d876 (wo-450-place) | test_placement_areas·names·ops rc=0, test-split-placement·pki-playbook·sslrootcert rc=0, test-split-gateway.sh rc=0(실제 platform 게이트웨이 이미지) | — | 헤드 미재현 | 코드 끝, 아래 할 일 남음 |
| model-runtime | a43ba5c = v0.11.18 (계약 v3.4.7) | pytest 385 pass rc=0, 변이 12건(영역 보고) | smoke.sh rc=0 | 07:44 재현 rc=0 | 3.4.8 고정판 0.11.19 대기 |

## 최종 검증 단계에서 할 일(코드 단계에서 할 수 없는 것, 빼지 않는다)
- model-lab: 기존 모델 패키지를 lineage.question_sets 를 채운 새 버전으로 다시 게시(학습 서버 어댑터 읽기, 쓰기는 ~/dabin 안만, deploy 스택의 model-registry 필요). 절차는 model-lab docs.
- kiosk-frontend: test:dom·test:e2e 헤드 재현.
- 배치: test-split-gateway.sh 를 자체 점검 목록에 등록(잠금 파일에 AREA_GATEWAY_IMAGE 줄이 생긴 뒤), 실제 <서비스>-cert·step-ca 와 연결한 게이트웨이 인증서 갱신 확인.
- platform: 나가는 쪽 전용 게이트웨이(학습 서버) 지원 — 지시함 07:45.
