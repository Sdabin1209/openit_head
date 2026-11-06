# 스키마 결함 전수조사: 중간 집계

2026-11-06. **전체 수정 대상 수는 아직 미확정이다.** 이 문서는 완료 보고가 아니다.

| 구분 | 원본 파일 수 | 반례로 결함 확정 | 결함 미확정 |
|---|---:|---:|---:|
| JSON Schema | 611 | 67 | 544 |
| OpenAPI 서비스 문서 | 7 | 6 | 1 |
| 합계 | 618 | 73 | 545 |

파일 경로로 중복을 제거한다. `$defs`, HTTP operation, 실패한 시험 수는 별도 스키마로 세지 않는다. JSON Schema와 이를 참조하는 OpenAPI는 서로 다른 원본 문서이므로 표에서 구분한다. 73개가 73개의 독립적인 근본 원인이라는 뜻은 아니다. 현재 확정된 공통 원인은 검증 경로에서 `format` 규칙이 적용되지 않는 것이다.

## 확정 기준과 결과

정상 대조 입력을 기존 실제 검증기가 받아들이고, 선언된 `format`을 위반한 입력도 받아들이는 경우만 결함으로 확정했다. 불가능한 날짜 `2026-02-30T00:00:00Z` 또는 잘못된 URI를 사용했다. 독립적인 엄격 검증기로 해당 입력이 `format`을 위반하는지도 확인했다.

JSON Schema의 영역별 확정 파일 수는 boundary-contracts 26, ops-feedback 18, question-authoring 16, survey-service 4, model-lab 3이다. OpenAPI는 dataset-store, model-registry, ops-feedback, question-authoring, release-gate, survey-service의 6개다. 공통 검증기와 의존성 문제이므로 스키마 파일마다 별도 조건을 덧붙이는 방식으로 해결해서는 안 된다.

기본 메타스키마·참조 점검과 기존 정상 예시 865개·비정상 예시 934개에서는 불일치를 찾지 못했다. 이것은 전체 규칙의 시험 충족이나 정의의 완전성을 입증하지 않는다. **정상 확정은 0개다.** 미판정 545개를 결함 없음으로 읽으면 안 된다. format 참조가 있으나 이번 반례에서 재현하지 못한 추가 16개는 `format-candidates.json`에 분리했다. 후보를 결함 확정 수에 넣지 않았다.

## 기준 상태와 한계

이 집계는 기존 설치된 검증 경로의 결함을 센다. 패키지 버전과 인터프리터는 `environments.json`, 원본 파일 해시는 `inventory.json`에 있다. 특히 boundary-contracts와 HTTP 검증은 설치된 v3.4.21을 사용했다. 작업 중인 v3.4.22를 적용 완료로 간주하지 않았다. source 해시는 조사 시점 작업 트리 기준이며 설치된 wheel의 해시와 같다는 뜻은 아니다.

앞서 확인했던 StepCaEnv의 DNS 이름 정의와 CommonEnv의 proxy 조건 결함은 이 **format 반례 73개에 포함하지 않았다**. 따라서 73은 이번 조사에서 재현한 확정 하한이며, 과거 결함을 합한 전체 수 또는 남은 수정 수가 아니다. 과거 항목의 수정·이미지 반영 상태는 [기존 후속 기록](../pki-startup-followup.md)을 따른다.

업무 규칙의 선언 누락, 모든 조건 분기별 시험, 상태·파일·프로세스·이미지 경계를 통한 전체 전달 경로는 아직 완전 판정하지 못했다. 모든 원본 행에 미검토 항목을 남겼다. 전체 E2E와 서비스 기동은 실행하지 않았다.

## 증거와 재현

- `inventory.json`: 618개 원본의 경로·해시·기본 검사·결함 근거·미검토 상태.
- `runtime-evidence.json`, `openapi-evidence.json`: 실제 검증기의 정상/비정상 입력 수용 결과.
- `runtime-cases.json`, `openapi-cases.json`: 재현 입력. 기존 시험 예시로 만든 인공 데이터이며 실제 사용자 데이터가 아니다.

head에서 기존 각 영역 가상환경으로 재현한다. 환경을 고친 뒤에는 확정 수가 줄어야 한다. 서비스나 Docker를 실행하지 않는다.

```bash
python3 scripts/replay-schema-census.py > /tmp/schema-census-replayed.json
../boundary-contracts/.venv/bin/python scripts/audit-schema-inventory.py \
  --out /tmp/schema-census-base.json --cases /tmp/schema-census-generated-cases.json
```

기본 조사기는 예시에서 103개 반례 후보를 생성한다. 저장된 재현 입력 108개에는 `_common`의 Timestamp 및 `HttpPages`의 4개 페이지에 대한 추가 정상/비정상 대조 5개가 포함된다. 이 5개도 실제 검증기로 재현한 결과만 확정 수에 포함했다.
