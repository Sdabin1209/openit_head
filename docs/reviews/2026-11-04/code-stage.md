# 코드 단계 끝 조건 대장 (계약 v3.4.7) — 헤드가 새 clone 으로 재현한 것만 "끝"

| 영역 | 커밋 | 시험 | 스모크 | 헤드 재현(워크스페이스 배치 새 clone) | 상태 |
|---|---|---|---|---|---|
| admin-console | 431d9a3 (wo-344-code; ad646e4 뒤는 README 문서만, 헤드가 diff 로 확인) | npm test 206 pass·0 fail rc=0, tsc rc=0 | SMOKE OK rc=0 (smoke-ad646e4) | 07:11 재현 rc=0 | 끝 |
| kiosk-frontend | 68ce379 (wo-344) | npm test 318 pass·0 fail rc=0, typecheck rc=0, test:image 16 pass rc=0 (test:dom 27·test:e2e 34 는 영역 보고, 헤드 미재현) | SMOKE OK rc=0 | 07:24 재현 rc=0 | 끝(e2e·dom 헤드 재현은 최종 검증 때) |
| synthetic-data | 9e1bd4e (wo-320c) | setup-env rc=0, pytest 294 pass·1 skip rc=0 | smoke_service.sh SMOKE_OK rc=0 | 07:28 재현 rc=0 | 끝 |

## 최종 검증 단계에서 할 일(코드 단계에서 할 수 없는 것, 빼지 않는다)
- model-lab: 기존 모델 패키지를 lineage.question_sets 를 채운 새 버전으로 다시 게시(학습 서버 어댑터 읽기, 쓰기는 ~/dabin 안만, deploy 스택의 model-registry 필요). 절차는 model-lab docs.
- kiosk-frontend: test:dom·test:e2e 헤드 재현.
