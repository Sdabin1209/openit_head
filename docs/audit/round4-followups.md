# 4차 후속 작업 목록 (D93~D103에서 나온 것)

작성: 2026-10-28, 헤드. 이 문서는 **할 일의 목록**이다. 구현하지 않았고, 완료 여부를 확인하지 않았다. 각 영역은 자기 리포지토리에서 `docs/change-requests/` 또는 작업 단위로 받아 처리한다. 근거는 `../DECISIONS.md`의 해당 번호.

## model-runtime (D93, D94)
- `empty_fallback_text`: 현행 문구를 유지한다. 도메인 소유자가 문구를 정하면 새 정책 버전(`protect-3`)으로 바꾼다. 사용자 확인 대기(D93).
- `docs/rules.md`와 `change-requests/004`의 'G1 대응 검사는 미정'을 '두지 않기로 함(D94), 평가 지표로 측정'으로 갱신한다.

## model-lab (D94, D96, D97, D98, D100)
- 평가 지표를 `metrics-v2-proposal.md`와 D96의 기본값대로 v2로 구현한다(`value_precision/recall`, `action/reason/status/next_item_accuracy`, `output_invalid_rate`, `ungrounded_number_rate`, `material_coverage`). 먼저 `boundary-contracts/METRICS.md` 개정을 기다린다.
- `semantic_violation_rate`: turn-engine `validate_extraction` 의존을 더한다(버전 고정). 학습 데이터 A 출력 전수에서 위반 0을 기준 시험으로 둔다(D97).
- 회귀 평가의 TurnTrace 입력 키를 `extract_input`, `extract_output`, `response_input`, `response_output`으로 확정한다(D98).
- I2를 HTTP 클라이언트로 전환한다(CR-L004와 연결, D100).

## turn-engine (D99)
- CR-010을 종결한다(변환 함수는 만들지 않는다). `DATASET_V2_FLOW`는 시험용이라고 명시한다.
- `docs/rules/` 중 v1 전용 문서에 '보관(v1)' 표시를 하고 참조(README, design, CR)를 끊은 뒤 한 릴리스 뒤 삭제한다. v2에도 유효한 문서가 있는지는 문서별로 읽어 판단한다(헤드는 읽지 않았다).

## survey-service (D95)
- `docs/boundary.md` 43행의 'G12 기본 0=끔·값은 미정'을 66행(기본 3, ADR-0014)과 맞게 정정한다.

## ops-feedback (D98)
- `STATUS.md`의 '확인하지 못한 것: v2 TurnTrace의 키'를 확인한다. 문진 스키마(`survey-service/schema/schemas/TurnTrace.json`)에 키가 있다. 비식별 사본과 규칙을 그 키에 맞춘다(필요한 경우).

## boundary-contracts (헤드 소유, 별도 단계) (D96, D97, D100)
- `METRICS.md`를 v2로 개정한다(절 제목, 폐기 지표 표시, 신설 지표, 분리 기준 `ACTION`·`REASON`). `verify.py` 통과를 확인한다. 이 세션은 head 밖이라 수정하지 않았다.
- `HTTP.md`에 I2 DatasetStore 절을 더한다(I3의 파일 묶음 전달 형식을 따름). `boundary_contracts.clients` 클라이언트와 `conformance` 참조 서버를 더한다. 계약 MINOR.
- slice `kind`가 열거인지 확인하고 열거면 `ACTION`·`REASON`을 더한다(MINOR).

## synthetic-data (D100)
- I2 HTTP 서버를 구현한다.

## deploy (D103)
- runbook에 L03 요건(내부망 제한, 강한 암호, 실패 로그 감시)과 L06 요건(데이터 볼륨 암호화 디스크)을 쓴다.
- ADR에 L05(내부 TLS 없음의 범위와 위험)를 쓴다.
- `gen-schemas --check`(admin-console)가 check-all에 연결됐는지 확인한다(D101).
- L08(`OPS_DB_SCHEMA=verify`, migrate 분리, DB 계정 분리)을 다음 라운드 첫 작업으로 잡는다.

## 사용자 확인 필요 (임시 기본값 적용 중)
- D93 respond 대체 문구.
- D102 결과 전달: 'pull만' 기본. push가 필요한지와 형식.
- D103 L06: 병원 서버의 디스크 암호화 여부.
- D96: METRICS 정의의 기본값은 학습 담당 확인 대상.
