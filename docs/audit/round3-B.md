# 3차 독립 점검 B (diff만 보고 작성)

대상: release-gate 6ee206c..9672f1c, ops-feedback eb2c7d3..f7ac95f, question-authoring c527509..20934c6, deploy 3539072..693e006.
표기: [확인]=실제로 돌리거나 코드 줄로 확정, [추정]=돌려 보지 못함. 코드 수정 없음.

## 지적

### M1. ops-feedback: failed_raw_days 기본 90일이 raw_days보다 짧거나 "forever"를 무시한다 (데이터 손실, 보존 설정 우회) [확인: 코드 읽기]
- `ops-feedback/src/ops_feedback/job.py:209-211`, `config.py:32`(`failed_raw_days`=90 기본 채움)
- 입력: 설정 `raw_days: 365`(또는 `raw_days: forever`)이고 `failed_raw_days`는 적지 않음 -> `load_config`가 90을 채운다 -> 재시도 대상(DEID_FAILED, PUBLISH_FAILED) 원본이 **90일에 삭제**된다. 변경 전에는 raw_days에 삭제되었으니 "더 길게 보관하겠다"고 설정한 운영자의 재처리 대상이 설정보다 먼저 사라진다. `raw_days: forever`는 "원본 삭제 없음"이라는 뜻인데 실패 원본만 90일에 지워진다.
- 제안: failed_raw_days 기본값을 `max(raw_days, 90)` 또는 raw_days와 같게 하고, `raw_days: forever`이면 failed도 forever로 한다. 사용자 결정 대상(문서에 이미 임의값으로 적힘).

### M2. question-authoring: 날짜 치환이 전화번호 경고를 지운다 (새 코드가 만든 회귀, 환자 정보 경고 누락) [확인: 실제 실행]
- `question-authoring/question_authoring/service.py:35, 344` (`_DATE.sub("날짜", text)` 후 `_PHI` 검사)
- 입력: `010-20120101`, `010 20120101`, `+82 10 20120101`, `02-20120101`, `031-19991231`, `0312012.01.01` -> `_PHI` 경고 **없음**(`[]`). 같은 구조의 `010-2012-0101`은 경고된다. 변경 전에는 `010-2012-0101`/`010-20120101` 형태 모두 전화번호 패턴에 걸렸다. 뒤 8자리가 날짜처럼 보이는 번호가 구분자 뒤에 붙어 있으면 `(?<!\d)`가 통과해 "날짜"로 바뀐다.
- 코드 주석이 "놓치는 것보다 거짓 경고가 낫다(D88 U5)"라고 적은 방침과 반대 방향이다. 경고 전용 탐지라 H는 아니고 M.
- 제안: 날짜 치환 전에 PHI 검사를 먼저 하고 날짜 치환은 "날짜 뒤 숫자 연쇄" 오탐 제거용으로만 쓴다. 또는 `_DATE` 앞에 `(?<![\d-])`처럼 구분자도 막는다.

### M3. release-gate: 정리(prune)가 PRUNED 표시를 먼저 쓰고 삭제를 락 밖에서 하여 중간 실패 시 영구 누수 [확인: 코드 읽기, 재현 못 함]
- `release-gate/release_gate/store.py` `prune_unprotected`(PRUNED write 후 `rmtree(ignore_errors=True)`)
- 상태: PRUNED 기록 후 프로세스가 죽거나(SIGKILL 포함) rmtree 일부가 실패(권한·열린 파일) -> `is_pruned`가 True라 `plan_bundles`가 다시 고르지 않고, 재호출은 `return 0`. 어댑터 파일이 디스크에 영구히 남는다. 반대로 해당 릴리스는 활성화도 거부되어 되돌릴 수 없다(의도 범위 안). 데이터 손실은 아니고 디스크 누수라 M(낮음 쪽).
- 제안: `is_pruned`이고 `adapters/`가 남아 있으면 삭제를 이어서 한다(멱등 마무리).

### M4. deploy backup_prune: 60분 넘게 걸리는 진행 중 백업의 임시 파일을 지울 수 있다 [추정]
- `deploy/scripts/backup-lib.sh:53` (`-mmin +60 ... rm -rf`), `backup.sh`에 flock 없음(`grep lock`은 images.lock 경로뿐)
- 상태: `.partial-<시각>` 디렉터리는 안에서 큰 파일 하나를 쓰는 동안 디렉터리 mtime이 바뀌지 않는다. 두 번째 백업(겹친 cron, 수동 실행)이 같은 저장소 폴더의 `backup_prune`을 부르면 60분 지난 진행 중 partial을 지운다 -> 첫 백업이 `mv`에서 실패하거나(비정상 종료) 부분 스냅샷. 주석 "실행 중인 백업은 건드리지 않는다"는 60분 안에 끝난다는 가정일 뿐이다. 잠금이 없어 겹침 방지도 없다.
- 제안: backup.sh 시작에 `flock`, 또는 mtime 대신 트리의 최신 mtime을 기준으로 삼는다(release-gate의 purge_stale_tmp가 이번에 같은 수정을 했다).

### L1. deploy rotate-account.sh:15: 빈 해시 검사가 주석 안으로 들어가 사라졌다 [확인: 줄 읽기]
- `H=$(...)   # 표준 입력(점검 L6 ...); [ -n "$H" ] || die "caddy hash-password 실패"` — `#` 뒤라서 `die` 검사가 실행되지 않는다. 현재는 `set -euo pipefail`이라 docker 실패는 메시지 없이 중단된다. 그러나 docker가 0으로 끝나면서 빈 출력(예: caddy가 비TTY stdin의 두 번 입력을 받지 못했을 때 tail -1이 빈 줄)이면 빈 해시가 `account-$ID-hash`를 덮어쓰고 평문 파일은 이미 지워졌으며 `gw_write_accounts`가 새 난수 암호를 만든다(출력한 암호와 다름) -> 계정 잠김. 가능성 낮아 L. 같은 줄 gateway-lib.sh:38은 검사가 다음 줄에 있어 정상.
- 또한 `caddy hash-password`가 stdin 비TTY에서 두 번 읽는 동작은 이 점검에서 돌려 확인하지 못했다(docker/caddy 실행 안 함) [확인 못 함].

### L2. deploy backup.sh: 평문 모드에서 gateway-data를 조용히 건너뛰고 종료 0 [확인: 코드 읽기]
- `backup.sh:34` 기본 목록에 gateway-data가 있는데 `BACKUP_CRYPT=none`이면 stderr 한 줄만 쓰고 계속하여 전체 종료 코드 0. CA 비밀키 백업이 없다는 사실이 cron 성공으로 보인다. 평문 모드는 시험 전용이라고 문서에 있으나, 운영에서 평문 허용이 켜진 채라면 알아채기 어렵다. 제안: 건너뛴 저장소가 있으면 종료 코드 또는 check-health 경고.

### L3. ops-feedback admin delete-session --dry-run: 원본만 있는 세션을 "찾지 못함"(3)으로 보고 [확인: 코드 읽기]
- `admin.py:90-92` dry-run은 `traces`만 센다(`raw_rows`는 항상 0). 아직 비식별되지 않은 세션(원본만 있음)은 dry-run이 exit 3 NOTHING_FOUND인데 실제 삭제는 원본을 지운다. 운영자가 "지울 게 없다"고 오해할 수 있다. 제안: dry-run에서도 원본 건수를 센다.

### L4. ops-feedback review `_has_email`이 정규식과 다른 경우 [확인: 실제 실행]
- 20만 건 무작위 문자열 퍼즈는 원래 정규식과 불일치 0건. 단 도메인 부분이 254자를 넘고 TLD가 255자째 이후에 있으면(`"a@"+"b"*300+".com"`) 원 정규식은 매칭, `_has_email`은 미매칭. 유효 도메인은 253자 이하라 실사용 영향 거의 없음. 선형 시간은 확인(2만 자 입력 4ms 이내).

### L5. release-gate 종료 시간 합이 stop_grace_period를 넘을 수 있다 [추정]
- `main.py:315-319`: grace 20 + (필요 시) 대기 5 + loop.join 최대 10 = 최악 35초, compose `stop_grace_period: 25s`(compose.yaml:345). 주기 작업이 길게 돌 때 SIGKILL이 먼저 와서 이번 수정의 목적(닫힌 연결에 쓰지 않기)과 무관하게 작업이 중간에 끊긴다. 주기 작업이 트랜잭션이면 롤백되어 안전하다고 보나 확인하지 못했다.

### L6. Gateway CSRF 규칙의 가정 [확인 못 함 / 추정]
- 규칙 자체(대소문자: Caddy 헤더 조회는 대소문자 무관, 중복 Origin은 첫 값만 비교, Sec-Fetch-Site와 Origin을 OR로 모두 검사)는 읽기상 우회 경로를 찾지 못했다. 시험(`test-gateway-auth.sh`)은 포트가 있는 Host(127.0.0.1:port)만 확인한다. 기본 443(Host에 포트 없음)에서도 `{http.request.hostport}`는 Host 헤더 문자열 그대로라 Origin과 맞는다고 보지만 시험은 없다 [추정].
- `Referrer-Policy: no-referrer`(Caddyfile:68) 아래에서 브라우저는 mode가 cors가 아닌 POST(HTML form 제출, `sendBeacon`, `fetch(mode:'no-cors'|'same-origin')`)에 `Origin: null`을 보낸다. 그러면 정상 같은 출처 요청도 `Origin != https://host`로 403이 된다. 키오스크·직원 화면(다른 리포)이 이런 POST를 쓰는지 읽을 권한이 없어 확인하지 못했다 [확인 못 함]. E2E는 브라우저를 쓰지 않아 이 경우를 가리지 못한다. 담당 영역에 "화면의 POST는 fetch 기본 모드(cors)뿐인가"를 확인 요청할 것.
- 키오스크 기기의 "정적 서버"가 gateway와 다른 출처에서 화면을 낸다면 같은 출처 가정이 깨진다(Caddyfile에 CORS 설정이 없어 이미 동작하지 않는 구성이므로 현 구조에선 해당 없음으로 판단).

## 문제 없다고 본 부분 (근거)
- release-gate 보호 집합: `keep=0`에서도 활성·직전·활성보다 새 미활성 릴리스 보호, 활성 이력이 없으면 전부 보호(retention.py). 삭제 직전에 같은 락/트랜잭션에서 재확인(SQLite BEGIN IMMEDIATE + RLock, PG advisory lock + 같은 연결의 `_q`, 재진입 문제 없음), `switch_pointer`가 같은 락에서 PRUNED 대상 거부. 경쟁 시험이 의도한 순서를 실제로 돌린다. 삭제 범위가 의도보다 넓어지는 경로는 찾지 못함.
- release-gate tmp 정리: 트리 최신 mtime 기준으로 바뀌었고 OSError는 건너뜀(깨진 심볼릭 링크가 있으면 그 임시 디렉터리는 영구히 안 지워질 수 있으나 L 이하, 추정).
- RecursionError -> 400, loop.join: 읽기상 정상.
- ops-feedback 이메일 선형 탐지: 위 퍼즈, 선형성 확인. 길이 상한(20,000/4,096)은 의도대로 닫는다. 단 deid의 4,096자 상한이 정상 trace의 긴 허용 문자열을 DEID_FAILED로 만들 수 있는지는 스키마를 읽지 않아 확인 못 함(이 경우 failed_raw_days 90일 뒤 원본 소실, M1과 연결).
- 엄격한 불리언(config, detect): `isinstance(bool)` 검사로 "false" 문자열 거부, 정상.
- delete-session 두 값 조회, 종료 코드 우선순위(`A and B or C and D`)는 의도대로 동작.
- 조건부 삭제(question-authoring): 초안은 저장된 JSON(`sort_keys, ensure_ascii=False`) 동일성 비교로 라운드트립 안정, 갱신된 초안은 지우지 않음. blob은 한 문장 NOT EXISTS + 쓰기 락(SQLite BEGIN IMMEDIATE, PG advisory lock)으로 경쟁 없음. 재업로드 시 created_at 갱신 정상.
- 이메일형 사용자 ID: `^...$`와 `user_roles.get(user)` 정확 일치가 먼저라 개행 우회 없음. `:at:` 치환은 128자 안. 이전에 허용되던 ':'를 포함한 ID는 이제 401(회귀 가능성, 현 QA_USER_ROLES 파서가 ':'로 split해 실제로 쓰지 못하므로 영향 없다고 봄).
- SIGTERM(question-authoring): inflight 계수와 유예 대기는 읽기상 정상(헤더 파싱 중인 연결은 세지 않음, 미미).
- backup.sh trap: `.tar-<TS>`/`.partial-<TS>`는 실패·INT·TERM에서 지워지고 못 지우면 3으로 종료. 암호화 실패 경로(가짜 gpg 시험)가 시험에 있음. SIGKILL은 trap이 못 막으나 다음 실행 prune이 정리(M4 참조).
- restore-secrets.sh: `tar -tf`를 변수로 받아 pipefail 문제 제거, 경로 검사 정상. 단 `grep` 정규식은 `./../x`처럼 `..` 중간 구성요소도 잡지만 심볼릭 링크 항목을 통한 탈출은 검사하지 않음(추출 대상이 새 빈 폴더, 낮은 위험, 추정).
- verify_area.py 범위: 기준 브랜치와 merge-base 비교로 바뀐 파일이 많아지는 방향이라 E2E를 건너뛰는 오류 쪽으로는 약해지지 않음. origin/main이 오래되면 과다 실행(안전한 방향).
- Caddyfile 헤더 제거: 대상 3곳 모두 `-X-Openit-User`, `-Authorization` 적용(들여쓰기만 어긋남, 동작 영향 없음).
- test 품질: CSRF 시험은 실제 Caddy를 띄운다(좋음). gateway-data 백업 시험은 root 소유 파일 하나만 쓴다: Caddy가 쓰는 uid 10001 소유·0600 파일을 백업 도구가 읽는지는 시험이 가리지 않는다 [확인 못 함].
