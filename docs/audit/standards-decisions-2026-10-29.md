# 표준성 점검 결정표 (2026-10-29, D106 초안)

근거: 영역별 `docs/audit/standards-2026-10-29.md`(10개 전부 도착). 원칙: 표준이 있으면 표준으로 대체하고 근거에 표준 이름을 적는다. 표준 이름과 요구 내용은 헤드의 기억에 근거한 것이 많고 **원문 대조 전**이다(각 항목에 "원문 대조" 표시). 사용자 호출은 표준이면서 대칭적인 선택지가 여럿일 때만 한다.

## 1. 단계 구분
- **단계 A (지금 지시)**: 다른 영역·계약 변경이 필요 없는 영역 안 수정. 안전·데이터 손실·개인정보에 가까운 것부터.
- **단계 B (헤드가 계약 v2.2.0을 낸 뒤 지시)**: 영역 간 계약이 바뀌어야 하는 것.
- **단계 C (인프라 대체, B 뒤)**: 직접 만든 것을 표준 도구로 갈아끼우는 큰 작업.
- **사용자 판단 대기**: 아래 4절.

## 2. 단계 A — 영역별 지시 항목 (이 표의 해당 영역 줄만 수행)

| 영역 | 항목 | 결정(표준) | 표준·근거 |
|---|---|---|---|
| deploy | 시험 자격이 운영 구성에 들어감 (R-관찰) | `gen-secrets.sh`는 기본으로 **운영 자격만** 만든다. 시험 기기(`e2e`, `e2e-a/b/c`)와 `*-e2e` 시험 계정은 `--test-fixtures` 인자(E2E·데모가 넘김)가 있을 때만 만들고, 게이트웨이가 시험 계정이 든 구성으로 운영 기동하는 것을 점검이 막는다 | 시험 데이터와 운영 구성 분리(12-factor 10·OWASP 기본 자격 금지) |
| deploy | ADR 0022 문서와 코드 불일치(암호가 docker run 인자로 보이는가) | 코드를 확인해 문서를 사실로 고친다 | D89 |
| release-gate | G29 정책 경로가 틀리면 조용히 기본 정책 | 정책 파일이 없거나 읽지 못하면 **기동 거부**(fail-closed). runbook과 코드를 일치시킨다 | 안전 관문의 fail-closed |
| release-gate | G46 이웃 버전을 못 읽으면 `"unset"` 허용 | 읽지 못하면 매니페스트를 만들지 않고 거부 | 같은 원칙 |
| release-gate | `directory_hash`가 파일 심볼릭 링크를 포함, 번들 tar는 제외 | 둘이 같은 규칙을 쓰게 한다(심볼릭 링크는 양쪽 모두 거부) | 보증된 해시의 일관성 |
| question-authoring | #12 토큰 비교가 dict 조회(상수 시간 아님) | `hmac.compare_digest`로 모든 후보를 끝까지 비교 | RFC 2104 구현 관행·OWASP 타이밍 공격 대응(원문 대조) |
| question-authoring | #18 `uuid4().hex[:16]` 64비트 절단 | 절단하지 않고 uuid4 전체 hex(122비트 무작위) | RFC 4122 |
| survey-service | H02 outbox가 같은 트랜잭션이 아님(유실 창) | 세션 commit과 **같은 DB 트랜잭션**에 outbox 행을 쓰고, 별도 전송기가 읽어 보낸다. 크래시 주입 시험 | Transactional Outbox 패턴(microservices.io, 원문 대조) |
| survey-service | A01 ADR-0001의 12-factor 인용 | 12factor.net 10항 원문을 읽고 ADR을 사실로 정정 | D89 |
| survey-service | D03 역할 토큰 강도 기준 없음 | 기기 토큰과 같은 최소 길이 규칙을 역할 토큰에도 적용하고 ADR에 기록 | 일관성 |
| ops-feedback | B4 키 해시를 SHA-256(JCS(salt,key,value))로 직접 구성 | **HMAC-SHA256(키=salt)**로 바꾼다(`deid.pseudonym_of` 한 함수에서만) | RFC 2104, NIST SP 800-107(원문 대조) |
| ops-feedback | B6 salt 전역 하나·정책 없음 | salt는 배포마다 CSPRNG 32바이트 이상을 비밀 파일로 생성(길이 검사 후 기동), 회전은 "재가명화 절차"로 문서화(자동 회전 안 함). ADR 작성 | 가명처리 관행: 추가정보 분리 보관 |
| ops-feedback | B7 잔존 패턴(주민번호 `[1-4]`) | 외국인등록번호 뒷자리 시작 `[5-8]`까지 포함 | 한국 주민·외국인등록번호 체계(원문 대조) |
| ops-feedback | ADR 0002 결정과 결과의 모순(DB 계정 분리) | 사실(읽기 전용 계정 없음)에 맞게 ADR을 정정 | D89 |
| synthetic-data | B3 jsonschema 오류 메시지에 입력 값이 실려 보고서·stderr·HTTP 본문으로 나감(개인정보 위험) | 오류에는 **경로와 규칙 이름만** 싣고 값은 싣지 않는다. 재현 시험 | OWASP 로깅·오류 처리(값 비노출) |
| synthetic-data | A3 `fsync` 없이 rename 게시 | 임시 파일 쓰기 → 파일 `fsync` → rename → 디렉터리 `fsync` | POSIX 원자적 교체 관행 |
| synthetic-data | A10 `ALREADY_PUBLISHED` 판정이 import와 run에서 다름 | 한 함수로 통일 | 일관성 |
| synthetic-data | B14·C4 PII 의심 패턴 기본 '경고만', 시드 경로에는 검사 없음 | 기본값을 **거부(strict)**로, 시드 경로에도 같은 검사 | ADR 0005 제목("기본값은 가장 엄격하다")과 일치 |
| synthetic-data | A7 버전 이름이 digest 앞 12자리(48비트) | 앞 32자리(128비트) | 충돌 확률 무시 가능 수준 |
| kiosk-frontend | #61 환자에게 보이는 문구의 임상 검토 표식 불완전 | 환자 노출 문구를 **한 모듈**에 모으고 항목마다 `reviewed: true|false` 필드를 두며, 그 밖에 문구 리터럴이 없음을 시험으로 확인 | 임상 문구 통제(D89) |
| kiosk-frontend | #29 유휴 60초 초기화에 경고·연장 없음 | 만료 전 경고와 연장 수단을 제공 | WCAG 2.2 SC 2.2.1 Timing Adjustable(원문 대조) |
| kiosk-frontend | #42 푸시 해지가 엔드포인트 URL을 쿼리 문자열로 보냄 | 요청 본문으로 보낸다 | URL에 민감값 금지 |
| kiosk-frontend | #60 글꼴 미포함 | 오프라인 글꼴(OFL 등 재배포 가능한 것)을 이미지에 포함 | 브리프 요구 |
| admin-console | C5 릴리스 목록이 20쪽에서 조용히 잘리고 후보 계산에 쓰임 | 상한 초과 시 오류(실패 사례 목록과 같게) 또는 끝까지 읽는다. 다쪽 시험 | 조용한 데이터 손실 금지 |
| admin-console | E2·E4 위험도와 확인 강도 반대 | **되돌릴 수 없는 승인에 더 강한 확인**, 되돌릴 수 있는 활성화·롤백은 단순 확인 | 파괴적 행동 확인 UX 관행 |
| admin-console | C9 `retryable`을 쓰지 않고 상태 코드로 재판정 | 계약 `BoundaryError.retryable`을 쓴다 | 계약 준수(R7) |
| model-runtime | 문서 불일치(design.md `gpu-12g`가 4B, 프로파일은 1.7B) | 문서를 사실로 정정 | D89 |
| model-runtime | 값(3.5초, 재시도 3, util 단계 등) 근거 없음 | 새 ADR에 "초기값, 측정 안 함, 측정 계획" 기록 | D89 |
| model-lab | T22 `package-adapters`의 `created_at`이 파일 mtime(복사 방법에 따라 같은 어댑터가 다른 `content_hash`가 되어 `CONFLICT`) | 시각을 파일 시스템 mtime에서 읽지 않고 입력에서 결정적으로 정한다(어댑터 해시나 명시 인자). 재현 시험: 같은 내용의 복사본 두 개가 같은 `content_hash`를 낸다 | 재현 가능한 빌드·콘텐츠 주소 지정 |
| model-lab | C2 YAML 1.1 함정(`off`·`no`가 False, `0123`이 정수 83, 중복 키 무음) | YAML 1.2 규칙으로 읽고(예: ruamel.yaml 또는 JSON Schema로 타입 강제) **중복 키는 거부**. 설정 스키마에서 문자열이어야 할 키가 불리언으로 읽히면 거부 | YAML 1.2 사양 |
| model-lab | H19 Dockerfile `ssh-keyscan github.com \|\| true`(처음 본 호스트 키를 신뢰) | GitHub가 공개한 호스트 키 지문과 대조해 고정하거나, 태그 소스를 SSH 없이 받는 방식으로 바꾼다. 실패를 삼키지 않는다 | SSH 호스트 키 검증(TOFU 회피) |
| model-lab | T24 비공개 속성 `config._commit_hash` 사용, HF 캐시 배치를 직접 해석 | 공개 API(`huggingface_hub`의 `snapshot_download` 반환 경로·`HfApi.model_info(...).sha`)로 바꾼다 | 공개 API 사용 |
| model-lab | C6 ADR 0005가 배척한 '설정 속 임의 코드'를 `module:callable` 팩토리가 허용 | ADR에 신뢰 경계를 적는다: 설정 작성자는 운영자(신뢰 대상)이며 외부 입력이 아님. 허용 목록 방식으로 팩토리 이름을 제한 | 위협 모델 명시 |
| 전 영역 | N-(근거 없는 임의 값) | 각 값의 출처를 측정·표준·제약으로 분류해 ADR에 기록하고 측정하지 않았으면 그렇게 적는다. 값을 바꾸지 않는다 | D89 |

## 3. 단계 B·C (계약/인프라, 헤드 선행 필요)

**단계 B — 헤드가 먼저 계약 v2.2.0에 반영한 뒤 영역에 지시**
- 인증 실패는 **401 + `WWW-Authenticate`**, 인증됐으나 권한 없음만 403. 오류 코드 `UNAUTHENTICATED` 추가. (RFC 9110 15.5.2, RFC 6750; 원문 대조) — release-gate G23, ops-feedback D10, synthetic-data D4, 전 영역.
- 시간 예산: 한 환자 턴의 모델 호출이 둘(extract, respond)이라 호출별 상한의 합이 턴 마감(6초)을 넘으면 안 된다. 호출별 예산을 **계약 상수로 배분**한다(extract 3.0초 + respond 2.0초 + 여유 1.0초). 재시도는 남은 예산이 있을 때만. 측정하지 않은 배분값임을 명시. (survey F03·model-runtime #22/#28)
- 세션 ID는 서버가 CSPRNG로 생성(OWASP 세션 관리, 원문 대조). (survey D05)
- 영역 경계를 넘는 문진 스키마 8개와 각 영역이 낸 경계 형식 초안을 계약으로 승격(영역 CR 초안 수용).
- ADR 0010: LoRA-A 컴포넌트가 출력 합격을 보증하고 survey-service는 재검증·재시도를 제거(SV-02).
- ADR 0012: 키오스크는 기기 인증서(mTLS)로 인증하고 게이트웨이가 `X-Openit-Device`를 붙인다. 기기 토큰·`/config.json`·`NO_DEVICE_TOKEN` 제거.

**단계 C — 표준 도구로 대체(직접 만든 것 O)**
- 학습 루프·단계 캐시(model-lab T12, T18): `transformers.Trainer`/TRL, DVC·MLflow 대비 직접 구현 근거가 없다. 규모가 커서 사용자 결정 대기(4절)에 넣는다.
- Python 서비스의 `http.server` 직접 구현(연결 상한, timeout, slowloris 방어, 우아한 종료): **WSGI(PEP 3333) 앱 + waitress**. 근거: Python 문서가 `http.server`를 운영용이 아니라고 경고한다(원문 대조). 선택 이유: 서비스들이 프로세스 안 락·상태에 기대는 단일 프로세스·다중 스레드 설계라 prefork(gunicorn)보다 waitress가 맞는다.
- 정적 프런트엔드 서버(node:http 직접 구현): **Caddy file_server**(스택에 이미 있는 표준 서버).
- DB 스키마: 시작 때 임시 `ALTER`/`IF NOT EXISTS` DDL → **버전 있는 마이그레이션(yoyo-migrations)**. 선택 이유: 원시 SQL 서비스(sqlite3, psycopg)에 ORM 없이 쓸 수 있다.
- 자체 스케줄러(`scheduler.py`) → **systemd timer**(운영), 상태는 journald. 백업 → **restic**(암호화 저장소). 헬스 점검·경보 → **Prometheus + blackbox exporter + Alertmanager**(메트릭 레지스트리가 이미 있다).
- 직원 계정: 자체 발급·회전 스크립트 → 조직이 제공하는 계정 파일(`caddy hash-password`로 만든 bcrypt)로 **HTTP Basic(RFC 7617) over HTTPS**. 자격 발급은 조직의 일이며 프로젝트는 소유하지 않는다. IdP(OIDC)가 정해지면 인증 블록을 교체한다.

## 4. 사용자 판단 대기 (대칭적인 표준 선택지 / 위협 모델)

1. **G15 릴리스 매니페스트·승인 기록의 무결성**: 해시만 쓰는 현행 vs 분리 서명(cosign/Sigstore 또는 릴리스 키 서명). 둘 다 표준이고 위협 모델(저장소에 쓸 수 있는 공격자를 가정하는가)에 따라 갈린다.
2. **스케줄러/모니터링 대체의 범위**: systemd timer + Prometheus 스택까지 갈지, 이번 범위에서는 문서화된 한계로 둘지. 구현 규모가 크다.
3. model-lab T12·T18: 학습 루프와 단계 캐시를 표준 도구(`transformers.Trainer`/TRL, DVC·MLflow)로 갈아끼울지. 표준 후보가 여럿이고 규모가 크다.
4. KF-11(직원 호출 전달 실패 화면)과 QA-15(4-eyes 기본값)는 앞서 올린 사용자 결정 대기 항목 그대로다.
