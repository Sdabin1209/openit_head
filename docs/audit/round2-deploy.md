# deploy 수정분 2차 독립 점검 (읽기 전용)

점검일 2026-10-28. 대상: `deploy/` 의 `git log --since='2026-10-28 03:50'` 커밋(첫 커밋 799a9a2 ~ 3539072, 갈래 A·B·C 병합 상태). 코드·설정·문서는 수정하지 않았고 secrets/ 는 열지 않았다.

## 요약

발견: 높음(H) 0건, 중간(M) 5건, 낮음(L) 11건.

- M1 암호화 백업이 실패하면 평문 tar 가 남고 아무도 지우지 않는다 (확인·재현)
- M2 사람 경로(Basic 인증)에 교차 사이트 요청(CSRF) 방어가 없다 (코드 읽기로 확인, 악용 가능성은 추정)
- M3 gateway 내부 CA 루트 키가 든 볼륨 `gateway-data` 가 어떤 백업에도 없다 (확인)
- M4 자동 경로가 닿지 않는 시험들과 거짓 안심: Caddy 접근 규칙의 동작 시험이 없고(validate 뿐), E2E 백업 단계는 평문 모드이며, 백업·권한·컨테이너 점검 시험은 어떤 자동 실행에도 없다 (확인)
- M5 verify-area: 기본 변경 판정이 마지막 커밋 하나뿐이라 E2E 를 잘못 건너뛸 수 있고, 단계 5a·5d 는 어느 영역에도 대응되지 않는다 (코드 읽기로 확인)

게이트웨이의 핵심 보안 경계(기기 토큰 검증, 역할 분리, X-Openit-User 덮어쓰기, 본문 상한, 열지 않는 경로 404)는 임시 Caddy 로 우회를 시도했으나 뚫지 못했다(아래 "관점별 확인 범위").

방법: 실제 Caddyfile 사본에 가짜 비밀·가짜 상류(echo 서버)를 붙여 임시 Caddy 2.11.7 을 127.0.0.1 포트로 띄우고 직접 요청을 보냈다. 임시 컨테이너·네트워크·볼륨은 모두 지웠다. 실행 중인 스택·볼륨·secrets 는 건드리지 않았다. 재현 자료는 스크래치패드(`.../scratchpad/rig`, `bk`, `tt2`)에 있다.

---

## 중간 (M)

### M1. 암호화 실패 시 평문 tar 가 남는다 (backup.sh)
- 근거: `scripts/backup.sh:28-29` (`tar ... -cf .tar-$TS` 뒤 `backup_encrypt` 실패 시 `die`), `scripts/backup-lib.sh:38,44` (평문 입력은 성공했을 때만 지움). trap 이 없다. 커밋 4b0fd98 / 18cb00b.
- 재현: 스크래치패드에 임시 볼륨 `rigp_models-data`(파일 `f.txt`)를 만들고, 수신자 공개키 파일이 엉터리인 설정(gpg)으로 `backup.sh models-data` 를 실행했다. 결과: "암호화 실패" 로 종료하고, `$BACKUP_DIR/models-data/.tar-<시각>`(평문 tar, 모드 600, `./f.txt` 포함)과 빈 `.partial-<시각>` 이 남았다. 접두어가 `.`+`2` 로 시작하지 않아 `backup_prune`(이름 `2*`)이 영영 지우지 않는다. 잡이 매일 실패하면 하루에 하나씩 쌓인다(저장소 전체의 평문 사본). 대상은 gate-data·models-data·registry-data.
- 영향: 암호화를 필수로 한 목적(개인정보가 든 백업을 평문으로 두지 않기)이 실패 경로에서 깨진다. 폴더 700 안이라 외부 사용자는 못 읽지만 "평문은 디스크에 남기지 않는다"는 약속과 어긋난다. 같은 모양으로 `backup_tool.py` 가 중간에 실패하면 `.partial-*` 디렉터리도 남는다. (pg-backup.sh 와 backup-secrets.sh 는 trap 으로 지워 문제없음)
- 제안: backup.sh 에 `trap` 으로 `$P_DIR`·`.tar-$TS` 를 지우고, `backup_encrypt` 실패 시 입력을 지운다(또는 `shred`급이 아니어도 `rm`). 시작할 때 이전 실행의 `.partial-*`/`.tar-*` 잔재를 지운다. 이 경로(암호화 실패)의 시험을 test-backup.sh 에 더한다.
- 자율 수정: 가능 (deploy 안, 스크립트와 시험만 바뀐다).

### M2. 사람 경로에 교차 사이트 요청 방어가 없다 (Caddyfile)
- 근거: `config/Caddyfile:121-253`. 승인(POST /v1/approvals), 운영(POST /v1/activate, /v1/rollback), 검토 게시(POST /v1/cases/*/review), 저자 경로(POST /v1/materials, /v1/reviews)는 모두 브라우저가 캐시한 Basic 인증 자격으로 허용된다. gateway 에 Origin/`Sec-Fetch-Site`/Content-Type 검사가 없다. `X-Frame-Options: DENY` 는 있어 클릭재킹은 막지만 다른 사이트의 form/fetch POST 는 막지 않는다.
- 재현: 코드 읽기와 echo 상류로 확인한 것은 "인증된 요청이 Origin·Sec-Fetch-Site 와 무관하게 통과한다"는 점까지다(재현 요청의 헤더에 `Sec-Fetch-Site: cross-site` 를 줘도 막는 규칙이 없다). 실제 악용 가능 여부는 추정: 브라우저가 Basic 자격을 교차 사이트 요청에도 붙이는지(브라우저별), 서비스(release-gate 등)가 `text/plain` 본문의 JSON 을 거부하는지에 달려 있어 확인하지 못했다.
- 제안: 상태를 바꾸는 메서드(POST/PUT/DELETE)에 대해 `Sec-Fetch-Site` 가 `cross-site` 이면 403, 또는 `Origin` 이 사이트 이름 목록과 다르면 403 하는 매처를 사람 경로 앞에 둔다. 서비스 쪽에서 `application/json` 만 받는지는 각 영역에 확인을 요청한다.
- 자율 수정: 가능(Caddyfile). 단 정책(허용할 Origin 목록)은 GATEWAY_HOSTS 와 맞춰야 하므로 헤드 확인 권장.

### M3. gateway 내부 CA 루트 키가 백업되지 않는다
- 근거: `compose.yaml:51` 이 `gateway-data` 에 "비밀키가 들어 있어 백업·유출에 주의" 라 적었으나, `scripts/backup.sh` 의 기본 저장소는 gate-data·models-data·registry-data, `backup-secrets.sh` 는 `secrets/` 만 묶는다. `grep gateway-data` 결과 문서·스크립트에 백업 언급이 없고 runbook 9-1 은 "볼륨을 지우면 루트가 바뀌어 모든 기기가 다시 신뢰해야 한다" 고만 말한다.
- 영향: 서버를 잃으면(또는 `down.sh --purge`) 루트가 새로 만들어져 모든 키오스크·직원 PC 의 신뢰 저장소를 다시 손으로 고쳐야 한다. 복구 절차(runbook 4절)에 이 단계가 없다.
- 제안: gateway-data 를 `backup.sh` 의 저장소에 넣거나(비밀키가 있으니 암호화 필수라 현재 구조로 가능), 최소한 runbook 복구 절에 "루트가 바뀐다, 재배포 절차는 9-1" 을 넣는다. 둘 중 무엇을 택할지는 운영 결정.
- 자율 수정: 문서는 가능, 저장소 추가는 가능하나 정책 판단(루트 키를 백업 매체에 두는 위험)이 있어 헤드 확인 권장.

### M4. 시험이 닿지 않는 곳, 거짓 안심 가능성
- 근거와 확인:
  1. `scripts/test-gateway-auth.sh` 는 `caddy validate` 와 파일 모양만 본다. 역할·경로·헤더·본문 상한 규칙의 **동작**은 무거운 전체 E2E(단계 5a·5f 등)에서만 본다. 이번 점검에서 쓴 임시 Caddy + echo 상류 방식은 Docker 만 있으면 10초 안에 돌아, E2E 없이 우회 시도(대소문자, `//`, `..`, %2f, 헤더 중복, 청크 본문)를 회귀 시험으로 둘 수 있다.
  2. `scripts/e2e.sh` 단계 9 는 `BACKUP_ALLOW_PLAINTEXT=1` 로 백업을 돈다(e2e.sh diff 의 `backup-test.env`). 암호화 경로는 test-backup.sh(gpg)에서만 본다.
  3. `test-backup.sh`, `test-backup-secrets.sh`, `test-secret-perms.sh`, `test-check-containers.sh`, `test-postgres.sh` 는 `e2e.sh`·`check-all.sh`·`config/verify-areas.yaml`(deploy 의 tests.commands 는 4개)·`docs/ci*` 어디에서도 부르지 않는다(grep 확인). 사람이 기억해 돌려야 한다.
  4. 백업의 권장 도구는 age 인데 이 PC 에는 `age` 가 없어 age 분기(`-R`, `.age`)는 한 번도 실행되지 않았다(`command -v age` 비어 있음, test-backup.sh 는 gpg 로만 시험).
  5. `backup-restore-test.sh` 의 "실제 백업 무결성"은 MANIFEST 의 해시와 암호문 파일 해시를 대조할 뿐이라 수신자 키가 틀렸거나(오타) 개인키가 없는 백업도 PASS 한다. 스크립트 머리말이 이 한계를 밝히고 있어(분기별 사람 시험) 거짓 단언은 아니다.
- 제안: (1) gateway 접근 규칙 동작 시험 스크립트 추가, (3) 위 시험들을 deploy 영역 tests.commands 나 check-all 의 Docker 가능 환경 선택 단계에 연결, (2) 단계 9 에 암호화 모드 한 번.
- 자율 수정: 가능.

### M5. verify-area 의 범위 판정 구멍
- 근거: `scripts/verify_area.py` `changed_files()`: `--since` 도 커밋 안 된 변경도 없으면 `git diff HEAD~1 HEAD`(마지막 커밋 하나)만 본다. 여러 커밋짜리 작업에서 마지막이 문서뿐이면 `skippable()` 이 참이 되어 "E2E 필요 없음" 으로 건너뛴다. 코드로 확인했고 실행 재현은 하지 않았다.
- 같은 파일/`config/verify-areas.yaml`: STEPS 의 `5a`(저자 경로: gateway 인증·역할·4-eyes)와 `5d`(기기 사이 세션 격리·폐기)는 어느 영역의 `e2e` 에도 없다(grep 확인). question-authoring 의 `QA_GATEWAY_TOKENS`/`X-Openit-User` 처리나 survey-service 의 기기 토큰 표 소유 확인을 바꿔도 verify-area 는 이 단계를 돌리지 않는다. 또 ops-feedback 의 검토 게시 경로(gateway 경유)와 release-gate 승인 X-Openit-User 는 5u(무응답)만 대응되어 있다. 대응표가 "모든 단계가 어느 영역엔가 속한다"는 것을 시험으로 강제하지 않는다.
- 제안: 기본 비교 기준을 "원격 추적 브랜치 또는 마지막 E2E 기록 커밋" 으로 하거나 최소한 건너뛰기 판정에 HEAD~N 을 쓰고 경고를 낸다. 5a→question-authoring·(gateway 쪽) deploy, 5d→survey-service·kiosk-frontend 를 표에 더하고, test_verify_area.py 에 "STEPS 의 5 계열 단계가 최소 한 영역에 대응" 단언을 둔다.
- 자율 수정: 가능.

---

## 낮음 (L)

### L1. 정적 화면·기본 경로로 클라이언트 헤더와 사람 자격이 그대로 간다
- 근거: `config/Caddyfile` `/staff/*`(299-312), `/admin/*`(206-211), 기본 `handle`(313-320), `/readyz`(81-98)에는 `header_up` 이 없다.
- 재현: staff 계정 Basic 인증 + `X-Openit-User: evil` 로 `/staff/`, `/admin/` 요청 → echo 상류가 받은 것: `Authorization: Basic <staff 자격 base64>` 와 `X-Openit-User: ['evil','evil2']`(클라이언트 값 그대로). 인증 없는 `/`, `/readyz` 도 클라이언트 헤더를 그대로 전달한다.
- 영향: 서비스 경로(/v1/…)에서는 덮어쓰기·삭제가 모든 경우에 확인되었으나(아래), 정적 컨테이너(kiosk-frontend, admin-console)가 직원의 Basic 자격(암호 복원 가능)을 받아 자기 접근 로그에 남길 수 있다. 정적 서버라 헤더를 믿는 코드는 없을 것이다(추정).
- 제안: 해당 `reverse_proxy` 에 `header_up -Authorization`, `header_up -X-Openit-User`.
- 자율 수정: 가능.

### L2. Caddy 가 매칭하는 경로와 상류로 보내는 경로가 다르다 (정리된 경로 vs 원본)
- 재현: 기기 토큰으로 `GET /v1/results/../sessions`, `/v1/drafts/../sessions`, `/v1/submissions/../sessions/x`(curl `--path-as-is`) → Caddy 는 `/v1/sessions` 로 정리해 키오스크 경로로 판정하고 상류에는 원본 `/v1/results/../sessions` 를 보낸다(echo 상류가 받은 path 로 확인). 반대로 `/v1/sessions/../staff/x`, `//v1/staff/x`, `/V1/STAFF/x`, `/v1/%73taff/x`, `/v1/staff%2fx` 는 모두 staff 로 판정되어 401 이 나왔다(인증 우회 없음). `/staff/..`·`//staff/x`·`/x/../staff/x`·`/%73taff/x`·`/ADMIN/x` 도 401.
- 영향: 판정과 상류 해석이 어긋나려면 상류가 `..`·`%2e%2e` 를 접어야 한다. 그때도 survey-service 는 기기 토큰 역할만 받아 staff/결과/위험 신호 면은 자기 토큰 검사로 막는다(2차 방어, 추정: survey 코드는 읽지 않았다). 다른 상류(release-gate 등)로 가는 경로는 모두 같은 상류 안에서만 어긋난다. 현재 악용 경로는 찾지 못했다.
- 제안: 정리된 경로로 상류에 보낸다(예: `rewrite` 없이 `@dots path_regexp \.\.|%2e|%2f` 면 400), 또는 `..`·`%2e%2e`·`%2f` 를 포함한 요청을 일괄 400. 
- 자율 수정: 가능.

### L3. restore-secrets.sh 의 `..` 방어가 큰 tar 에서 건너뛰어진다
- 근거: `scripts/restore-secrets.sh:179` `tar -tf "$TAR" | grep -qE ... && die` 가 `set -o pipefail` 아래에 있다. grep -q 가 일찍 끝나면 tar 가 SIGPIPE(141)로 죽어 파이프라인 상태가 비영이 되고 `&& die` 가 실행되지 않는다.
- 재현: 첫 멤버가 `tokens/../../escaped.txt` 이고 뒤에 3000개 긴 이름이 있는 tar → 가드가 통과하고 추출까지 갔다(GNU tar 자체가 "Member name contains '..'" 로 거부해서 파일은 만들어지지 않음). 작은 tar 는 가드가 정상 거부. 심볼릭 링크 경유 쓰기는 GNU tar 가 거부함(확인). 따라서 GNU tar 에서는 실해 없음, BSD/busybox tar 에서는 추정 불가.
- 제안: `tar -tf "$TAR" > "$tmp"` 후 `grep` 하거나 `if grep ... < <(tar -tf)` 로 파이프라인 상태를 보지 않게 한다. 실패한 추출이 남긴 부분 폴더(`$DST`)를 정리한다.
- 자율 수정: 가능.

### L4. `kiosk-add-device.sh from-list --apply` 가 실패한다
- 근거: `scripts/kiosk-add-device.sh:26` `LIST=${2:-...}` 가 `--apply` 를 목록 파일로 읽는다. 머리말은 `from-list [파일] ... [--apply]` 를 안내한다.
- 재현: `kiosk-add-device.sh from-list --apply` → "오류: 기기 목록 파일이 없다: --apply" (확인). 파일을 주고 `from-list FILE --apply` 는 가능.
- 제안: `--apply` 를 인자에서 먼저 걸러낸다.
- 자율 수정: 가능.

### L5. 기기 토큰 표·목록 파일 쓰기가 원자적이지 않다
- 근거: `scripts/gateway-lib.sh:59-68`. `gateway-devices.caddy` 와 `survey-kiosk-device-tokens` 는 바인드 마운트라 같은 inode 로 `>` 덮어쓴다(주석에 이유 있음). survey 표는 `: >` 로 비운 뒤 줄마다 `>>` 한다. 중간에 중단되거나 Caddy/survey 가 그 사이 파일을 읽으면 일부 기기만 있는 표를 본다. 두 파일이 서로 어긋나는 시점도 생긴다(gateway 는 통과시키고 survey 는 모르는 기기).
- 영향: 짧은 창. survey 가 표를 요청마다 다시 읽는지 시작 때만 읽는지는 확인하지 못했다(추정). 시작 때만이면 `--apply` 재시작 순간만 문제.
- 제안: 임시 파일에 다 쓰고 `cat tmp > target`(같은 inode 유지, 한 번의 write)로 바꾼다.
- 자율 수정: 가능.

### L6. 계정 암호가 `docker run` 인자로 `ps` 에 보인다 (피할 수 있다)
- 근거: `scripts/gateway-lib.sh:38`, `scripts/rotate-account.sh:7-8` 의 `caddy hash-password --plaintext "$PW"`. ADR 0022 가 "한계"로 인정한다.
- 확인: `printf 'pw\n' | docker run -i --rm caddy:2-alpine caddy hash-password` 가 bcrypt 해시(60자, `$2a$14$`)를 낸다(대화형이 아니어도 표준 입력으로 읽음). 즉 한계가 아니라 구현 선택이다.
- 제안: `--plaintext` 대신 표준 입력으로 넘기고 ADR 의 한계 문단을 고친다.
- 자율 수정: 가능.

### L7. 문서·주석 불일치 (기기 토큰 pass-through 이후)
- `docs/runbook.md:253`: "gateway는 기기 토큰을 확인한 뒤 서비스 kiosk 토큰으로 바꿔 붙이는 지금 구조 그대로이므로 … 기기 ID 를 서비스에 전해 주는 변경이 따로 필요하다 (이 리포는 아직 하지 않았다)". 4644f96 이후 사실이 아니다(Authorization 은 바뀌지 않고 survey 가 표로 검증).
- `docs/RUN.md:120`: "통과하면 게이트웨이가 서비스 kiosk 토큰으로 바꿔 붙인다(기기 토큰은 서비스로 가지 않는다)". 같은 이유로 틀림.
- `config/Caddyfile:254-255` 주석 "서비스 kiosk 토큰으로 바꿔 붙인다", `:298` "HTTPS 종단은 운영 도메인이 정해지면 여기에 더한다" (이미 HTTPS).
- `scripts/gen-secrets.sh:48` 은 더는 쓰이지 않는 `survey-api-kiosk` 토큰을 여전히 만든다(compose 에 마운트 없음, E2E 가 "틀린 서비스 토큰" 용으로만 읽음).
- `scripts/e2e.sh` `tls_checks` 마지막 echo 가 "사이트 기본 본문 상한 설정" 을 확인한 것처럼 말하지만 그 함수는 본문 상한을 검사하지 않는다(단계 5a 가 검사). `export ... GATEWAY_TLS_PORT= GATEWAY_TLS_PORT=` 중복.
- `Caddyfile:59` 는 "사람이 쓰는 승인·운영·검토 경로는 1MiB" 라 하나 `/v1/staff/*`(직원 개입 등)는 8MiB 다(재현: staff POST 2MB → 통과, 청크 10MB → 413). 환자 경로 `/v1/sessions/*` 도 8MiB 다. 필요한 상한인지 영역 확인 필요.
- 자율 수정: 가능.

### L8. gateway 의 작은 구성 문제
- healthcheck(`compose.yaml:234`)는 평문 8080 `/healthz` 만 본다. HTTPS 리스너나 인증서 문제는 컨테이너를 unhealthy 로 만들지 못한다. 외부 감시(check-health 의 https 대상)가 정상 감지 수단인데 기본 `external-monitor.example.yaml` 이 https 대상을 포함하는지는 확인하지 않았다.
- 응답에 `alt-svc: h3=":8443"` 가 붙는데 compose 는 UDP 8443 을 게시하지 않는다(확인: 헤더 존재). 클라이언트가 h3 시도 뒤 TCP 로 되돌아가느라 지연이 생길 수 있다(추정). 전역 옵션 `servers { protocols h1 h2 }` 로 끈다.
- 평문 308 의 `Location` 이 `Host` 헤더를 그대로 쓴다(`Host: evil.example` → `https://evil.example:18443/..`, 확인). 요청자 본인에게만 영향이라 실해는 작다. `/config.json/`(끝 슬래시)와 `/config.json%00` 은 404 가 아니라 kiosk-frontend 로 간다(확인; 중앙 frontend 에 기기 파일이 없으므로 실노출 아님).
- 확인한 것 하나: up.sh 의 `chown 10001 /data` 는 새로 만든 볼륨에만, 비재귀(`/data` 한 곳)로 도는 일회성 컨테이너라 데이터를 파괴하지 않는다. 또 이미지의 `/data/caddy` 가 이미 1777 이라 root 소유 볼륨이어도 비루트 Caddy 가 HTTPS 를 서비스했다(확인) — 이 chown 은 사실상 불필요하지만 해가 없다.
- 자율 수정: 가능.

### L9. check-health 백업 신선도가 DB 백업만 본다
- 근거: `scripts/check_health.py` 5절은 `pg-*` 만 열거한다. gate-data·models-data·registry-data·secrets 백업이 멈춰도 CRIT 가 나지 않는다(잡 실패는 스케줄러 상태에서 따로 잡힐 수 있음, 확인하지 않음). 한 데이터베이스 폴더가 통째로 없어도(새 DB 추가 후 백업 누락) 있는 것들만 보고 OK 가 난다.
- 제안: 기대 저장소 목록(PG_DBS + 파일 저장소 + secrets)과 대조.
- 자율 수정: 가능.

### L10. E2E 시간 상수 (근거 점검)
- `scripts/e2e_steps.py:703-717`. 상수는 Caddyfile 값의 복사본이고 일치를 기계적으로 대조하는 곳이 없다(`GW_PATIENT_CAP_S` 는 정의만 있고 쓰이지 않음). Caddyfile 의 dial/헤더 시간을 바꾸면 E2E 단언이 조용히 엉뚱한 숫자를 본다(거짓 통과는 `READYZ_PAUSED_MAX_S`·`TURN_CLIENT_MAX_S` 같은 상한형 단언에서 가능: 상류가 더 빨리 끝나도 통과). `CLIENT_EXTRA_S=2.0`, `DOCKER_DNS_FAIL_S=3.0` 은 각 한두 환경의 관찰값이라 느린 환경에서는 오히려 거짓 실패가 난다(주석이 이를 밝힘).
- 제안: check-all 에 Caddyfile 의 `dial_timeout`·`response_header_timeout` 값을 읽어 상수와 대조하는 정적 점검.
- 자율 수정: 가능.

### L11. 자원 한도 위험 (추정, 실측 없음)
- `compose.yaml` 기본값 중 실제 모델·큰 입력에서 OOM 이 날 수 있는 곳(모두 추정):
  - release-gate 1g: 모델 패키지(LoRA 어댑터)·번들을 검증하며 파일을 메모리에 읽는다면 어댑터 크기에 따라 부족. release-gate 의 번들 처리 방식은 읽지 않았다.
  - survey-service 512m + `tmpfs /tmp`(크기 제한 없음, 메모리로 계산): 본문 상한이 8MiB 라 동시 요청 × 8MiB 가 겹치면 여유가 줄어든다.
  - model-serving 기본 1g 는 가짜 백엔드용이다. 실제 LLM 은 `compose.llm.yaml` 16g 로 덮어쓰지만 `compose.inference.yaml`(분리 서버)에는 한도가 없다. CPU 로 실제 모델을 `compose.yaml` 기본값만으로 띄우면 즉시 OOM 이다. ADR 0023 이 이를 인정한다.
  - tmpfs `/tmp`·`/data` 는 크기 제한이 없어 한 컨테이너가 한도 안에서 tmpfs 로 메모리를 채울 수 있다(`size=` 지정 권장).
- 확인한 것: healthcheck `start_interval: 1s` 는 엔진 25 미만이면 compose 가 거부하며 doctor 가 이를 FAIL 로 잡는다. `restart: unless-stopped` 는 OOM 종료만 되살리고 unhealthy 는 되살리지 않는다(Docker 동작; 파일의 주석은 "OOM kill(컨테이너 재시작)" 이라고만 말함).
- 제안: 운영 전 실측 항목으로 남기고(이미 "측정 근거 없음" 표기), tmpfs 에 `size=` 를 준다.
- 자율 수정: 가능(실측 불가, 값은 시작값 유지).

---

## 관점별 확인 범위

1. **gateway Caddyfile — 깊게 봄(실제 Caddy 로 재현).** 확인한 것: 평문 308(메서드·쿼리 보존)과 `/healthz` 평문 200, HTTPS 응답의 HSTS·nosniff·X-Frame-Options·Referrer-Policy·`Server` 제거. 기기 토큰: 목록 밖/빈/`Bearer ` 만/대소문자 변형/뒤 공백/`Authorization` 헤더 중복(양쪽 순서)/없음은 모두 401, 정확한 한 값만 통과. 통과한 요청에서 클라이언트의 `X-Openit-User`(대소문자 변형 둘)는 상류에 도달하지 않음. 직원·승인·운영·검토·저자 경로: 인증 없음 401, 다른 역할 403, 올바른 역할에서만 서비스 토큰 부착, 클라이언트의 `X-Openit-User` 는 계정 ID 로 덮어쓰임(모든 사람 경로 확인), 클라이언트 `Authorization` 도 덮어쓰임. 열지 않는 경로(`/v1/results*`, `/v1/sessions/*/risk-signals`, `/v1/releases/*`, `PUT/POST /v1/releases`, `/v1/traces`, `/v1/question-sets/*`, `/config.json` 대소문자·`//`·`./`)는 404. 경로 우회 시도(`//`, `/./`, `/x/../`, `%73`, `%2f`, 대소문자, 끝 슬래시)는 인증 경로에서 모두 막힘. 본문 상한: 사람 쓰기 경로 1MiB(Content-Length 와 청크 모두 413), 사이트 8MiB. 못 본 것: 실제 상류(survey 등)의 경로 정규화 방식, 브라우저의 Basic 캐시 동작, TLS 프로토콜·암호군 세부, 인증 실패 속도 제한(없음, 문서화됨).
2. **백업·복원 — 중간.** 코드 전체를 읽고 M1(재현), L3(재현)을 확인. 수신자 공개키만 서버에 두는 구조(개인키 파일 거부 검사, 서버에 복호 경로 없음)는 코드상 맞다. 평문 잔존: 성공 경로에서는 `.partial`→tar→암호화→삭제 순이고 중간 평문은 700 폴더 안이다. umask: `backup_load_config` 가 `umask 077` 를 현재 셸에 걸어 파일은 600 으로 생성되고 이후 `chmod -R u=rwX,go=` 로 정리, 경쟁 창은 찾지 못했다. 보존 삭제: 최신 하나는 남기는 로직이 맞다(정렬순 오래된 것부터, `total>1`); 단 mtime 기반이라 원격 복사로 mtime 이 바뀌면 보존이 어긋날 수 있다(추정). 직접 실행하지 못한 것: age 분기, `backup-secrets.sh` 전체(코드만), pg-backup 병렬 실패 경로.
3. **비밀 처리 — 중간.** gen-secrets/kiosk-add-device/rotate-account 는 값을 출력하지 않고(rotate 의 의도된 stdout 한 줄 제외) argv 에 비밀을 싣는 곳은 L6 의 `--plaintext` 뿐이다. 기기 토큰은 `umask 077` 하위 셸에서 600 으로 생성된다. 확인한 임시 재현: `kiosk-add-device.sh add/from-list` 를 스크래치 SECRETS_DIR 로 실행(모드 600/700 확인, 토큰 값은 출력하지 않음). 원자성은 L5.
4. **compose — 중간(실행 없이 코드 읽기와 한 번의 소유자 확인).** L8, L11. 의존 순서(gateway depends_on, 재부팅 시 depends_on 미적용이지만 Caddy 는 상류 이름을 요청 때 해석)는 문제를 찾지 못했다.
5. **스크립트 안전 — 얕게~중간.** `set -e`/`pipefail` 누락과 `rm -rf` 변수: `backup_prune`·`backup-secrets` 의 `rm -rf "$d"` 는 `find` 가 낸 경로라 빈 변수 위험 없음, `restore-secrets` 는 `${2:?}`, `rm -rf "$W"` 류는 mktemp 결과. `backup-check.sh`/`backup-restore-test.sh`/`doctor.sh` 는 `set -e` 없이 명시 검사로 도는 설계다. 이 점검에서 새로 찾은 `|| true` 오용은 없다. 모든 스크립트를 한 줄씩 정독하지는 않았다(특히 build-images.sh, publish*.sh, demo.sh, scheduler.py).
6. **E2E·verify-area·check-health — 중간.** M4, M5, L9, L10. e2e_steps.py 1493줄은 시간 상수와 주요 단언 주변만 읽었다. 단계 본문의 단언이 항상 참인 곳을 전수 확인하지는 못했다.
7. **문서 불일치 — 중간.** L7. runbook 전체와 모든 ADR 을 대조하지는 않았다(ADR 0022·0023 와 runbook 9절 위주).

## 읽지 못했거나 얕게 본 곳
- `survey-service`/`release-gate` 등 영역 코드(규칙: 읽지 않음) — 경로 정규화, 기기 토큰 표를 읽는 시점, Content-Type 검사는 추정.
- `scheduler.py`, `build-images.sh`, `publish-image(s).sh`, `registry.sh`, `rollback.sh`, `demo.sh`, `check_all.py` 본문.
- `config/postgres/initdb`, `pg-config-check.sh`, `check-containers.sh` 본문(diff 일부만).
- 실행 중인 E2E 스택: 이 점검은 실행하지 않았다(전체 E2E 통과는 전달받은 사실).
