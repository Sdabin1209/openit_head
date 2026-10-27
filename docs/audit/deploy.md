# deploy 영역 전수 점검 (읽기 전용 감사)

> 2026-10-28. 기준: head/docs/AUDIT_CHECKLIST.md A~I. 대상: /home/user/sdabin/healthKiosk/deploy (작업 트리 상태). 코드·설정·문서는 수정하지 않았고 컨테이너는 띄우거나 멈추지 않았다. `secrets/`는 이 체크아웃에 없었고(`ls`로 확인) E2E 임시 폴더 `state/e2e-89132/secrets`는 `ls -l`/`stat` 권한만 봤다(내용 미열람). 실행하지 않은 것은 '확인 못 함' 또는 '읽은 것'으로 구분했다. 줄 번호는 이 시각 기준.

## 요약

- 항목 수: 63 (A 9, B 12, C 10, D 7, E 8, F 6, G 3, H 5, I 3). 분모는 63.
- 판정별: OK 17 / 문제 34 (H 2, M 24, L 8) / 해당 없음 6 / 확인 못 함 6. 합계 63.
- 같은 원인은 묶었다. 서로 다른 뿌리 원인은 약 14개다(아래 H·M 묶음).

### H 문제 (2건)

1. B8: 게이트웨이가 TLS 없이 HTTP 평문으로 기본 인증 암호, 기기 토큰, 환자 발화를 나른다(`auto_https off`, 도메인·인증서 미정). 기본 바인드가 127.0.0.1이라 지금은 밖에서 닿지 않지만, 키오스크가 붙으려면 바인드를 열어야 하므로 열기 전에 해결해야 한다. 사용자 결정(도메인·인증서).
2. C7: 백업이 실제로 돌지 않는다(`config/backup.env` 없음 -> backup 잡 거부). 설정이 생겨도 사본이 같은 호스트·무암호화이며, 정기 복원 시험이 없고, `models-data`와 레지스트리 볼륨이 스케줄 백업에 없으며, 5개 DB가 한 시점이 아니다. 사용자 결정(O16) + 일부 자율 수정.

### M 문제 묶음 (24건)

- 자원 한도 전무(A9, F3, G3): mem_limit, cpus, pids_limit 없음.
- 비밀 파일 권한 644, 평문 계정 암호 보관, 회전·폐기 절차 불완전(B3, F5, B12).
- 게이트웨이 방어 부재: 본문 크기 상한 없음(B4, D5, G3), 보안 헤더 없음(B7), 로그인 시도 속도 제한 없음(B10).
- 공급망: 취약점 스캔·SBOM 없음, 외부 이미지 태그를 한 번 digest로 고정하고 갱신 절차 없음(B9, F2), 레지스트리 인증·TLS 없음·CI 경로 미정(F6).
- 컨테이너 격리 빈틈: registry 무강화, 추론 서버 compose 기본 0.0.0.0 바인드, edge/serving 네트워크가 외부 접속 가능(F1).
- 업그레이드·롤백: 이미지 digest만 되돌리고 DB 마이그레이션 순서·업그레이드 전 백업 없음(C9, F4).
- 알림·감시: 점검과 스케줄러를 부르는 타이머 미설치, 알림 수단 미정(E2, E5), 런북 일부 낡음(D7, E4).
- 데이터: 보존·삭제 기본값 없음(C3), PostgreSQL 오류 로그에 SQL 값 노출 가능, 저장·전송 암호화 없음(C4, C5), 로그·레지스트리 무한 증가(A6), DB 계정 DDL 권한과 토큰 만료 없음(B12).

## 항목별 판정

표기: OK / 문제(심각도) / 해당 없음 / 확인 못 함. "자율" = deploy 에이전트가 사용자 결정 없이 고칠 수 있음. "결정" = 사용자 결정 필요.

### A. 신뢰성

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| A1 timeout | OK | Caddyfile 모든 reverse_proxy에 dial/응답 헤더 timeout(:19-22, :38-43, :66-70, :219-221, :237-240). postgres healthcheck도 timeout 있음(compose.yaml:156-161). 스크립트의 docker 호출 자체 timeout은 확인하지 않았다. |
| A2 재시도 | OK | gateway 재시도 없음 `lb_try_duration 0`(Caddyfile:18, :39, :65, :217). 같은 `turn_id`는 키오스크가 재시도(영역 몫). |
| A3 부분 쓰기 | 문제 L | scheduler 상태 파일 `os.replace`(scheduler.py:44), 백업 `.partial`->`mv`(backup.sh:27, pg-backup.sh:33)는 원자적. 그러나 `rollback.sh:21` `cp "$TO" "$LOCK"`은 비원자적이고, 이어지는 `up.sh`가 실패하면 잠금만 바뀌고 적용 안 된 상태가 남는다(`rollback.sh:22-23`). 제안: 임시 파일+mv, 실패 시 이전 잠금 복원. 자율. |
| A4 우아한 종료 | 확인 못 함 | postgres `stop_grace_period: 30s`(compose.yaml:155)만 확인. 나머지는 기본 10초이고 앱의 SIGTERM 처리는 각 영역 몫이며 읽지 않았다. 스케줄러 timeout 시 `docker compose run` 컨테이너가 남는지는 FAULT_MATRIX도 미확인이라 적었다. |
| A5 자동 복구 | 문제 L | `restart: unless-stopped`(compose.yaml:7)와 depends_on healthy(:175-181, :218-222). E2E 5q/5p가 복구를 확인(FAULT_MATRIX 기록, 이번 점검에서 실행 안 함). 호스트 재부팅 뒤 기동 순서는 보장 안 됨(FAULT_MATRIX N12, D10 비보증). 제안: 재부팅 후 `up.sh` 절차를 런북에 명시하거나 systemd 유닛 제공. 자율(문서). |
| A6 무한 증가 | 문제 M | 상시 서비스 로그는 json-file 10m x 5(compose.yaml:12)로 제한. 그러나 (1) `job-*` 서비스는 `<<: *hardening`을 쓰지 않아 로그 회전 설정이 없다(compose.yaml:314-349). (2) 레지스트리 `registry-data`는 삭제만 켜고(compose.registry.yaml:14) GC 절차가 없어 이미지가 계속 쌓인다. (3) cron 예의 `state/scheduler.log`는 회전 없음(runbook.md 5절). (4) `state/e2e-*` 임시 폴더가 남아 있다(state/e2e-22306 등). 제안: job 서비스에 logging 옵션, 레지스트리 GC 주기, logrotate 안내. 자율. |
| A7 동시성 | OK | 잡별 `flock` 비차단 잠금(scheduler.py:60-63)으로 이중 실행 방지. 백업 스냅샷은 UTC 초 단위 폴더. 한 tick 안에서 잡은 순차 실행이라 상태 파일 갱신이 겹치지 않는다(긴 잡이 다른 잡을 지연시키는 점은 E1 근처 참고). |
| A8 healthz/readyz | OK | gateway `/healthz` 정적 200, `/readyz`는 survey `/readyz` 반영(Caddyfile:32-54). 서비스마다 healthcheck(compose.yaml:156, 185, 196, 215 등). kiosk-frontend는 compose에 healthcheck가 없고 이미지 `HEALTHCHECK`에 의존(compose.yaml:187-190, build/ctx/kiosk-frontend/Dockerfile:28). |
| A9 자원 한도 | 문제 M | `grep mem_limit|cpus|pids|ulimits compose*.yaml`에 운영 파일 결과 없음(GPU 예약만 compose.llm.yaml:37). 한 서버에 postgres와 모델 서빙이 같이 있어 한 서비스의 폭주가 환자 경로를 막을 수 있다. 제안: 서비스별 `mem_limit`, `cpus`, `pids_limit`, postgres `shm_size`와 `max_connections`. 값은 측정 근거가 없어 시작값으로 두고 측정 후 조정. 자율(값은 시작값, 용량 결정은 결정). |

### B. 보안

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| B1 인증 | OK | 기본 거부: `handle /v1/*` -> 404(Caddyfile:229-231), 직원·승인·운영·검토 경로는 `import authenticate` + 역할(:57-200), 키오스크는 기기 토큰 목록 대조 후에만 서비스 토큰으로 교체(:208-228), 위험 신호·결과 조회는 404로 닫음(:204-207). 공개 경로는 정적 화면과 /healthz, /readyz뿐. 자체 시험 `scripts/test-gateway-auth.sh`가 있으나 실행하지 않았다. |
| B2 인가 | OK | 계정 -> 역할 매핑을 `gateway-lib.sh`가 생성, 역할 불일치는 403(Caddyfile:73-75 등). 읽기/쓰기 토큰 분리(:93, :107, :178, :192). 환자 세션 간 수평 접근(기기 토큰이 모든 세션 ID에 접근, Caddyfile:208-209)은 survey-service 영역 몫이라 이 점검 범위 밖. |
| B3 비밀 | 문제 M | 좋은 점: 비밀은 파일 마운트와 `NAME_FILE`(compose.yaml:54-138), Caddy `{file./run/secrets/..}`, 환경 변수 평문 검사 스크립트(check-secrets-hidden.sh)가 있다. 문제: (1) 파일 권한이 644다(gen-secrets.sh:14, 19, 50; gateway-lib.sh:35, 41, 53, 59 `chmod 644`). 폴더 700에 의존한다(이유: compose 파일 secrets가 호스트 모드를 그대로 마운트). (2) 계정 평문 암호가 `tokens/account-<id>-password`로 디스크에 계속 남는다(gateway-lib.sh:34). 해시만 필요하다. (3) DSN 파일에 DB 암호가 들어 있다(gen-secrets.sh:38). (4) 회전: 토큰 파일 삭제 후 재실행(runbook.md 7절)이지만 DB 암호는 `pg-roles.sh sync`가 필요하고 runbook 7절에 없으며, 기기 토큰 폐기는 게이트웨이 재시작 필요. 제안: 암호 평문은 생성 직후 한 번만 보여 주고 삭제(또는 600 + 컨테이너 uid 그룹 읽기), 회전 절차를 서비스별로 런북에 표로. 결정(권한 모델), 문서는 자율. |
| B4 입력 크기 | 문제 M | Caddyfile에 `request_body max_size` 없음(grep 결과 0). 직원·키오스크 API에 본문 상한이 없어 큰 본문으로 서비스 메모리를 압박할 수 있다(FAULT 계약의 8MiB와도 불일치 가능). 제안: 경로별 `request_body { max_size 8MB }`. 자율(값은 계약 D5 8MiB 근거). |
| B5 인젝션 | OK | deploy 코드에 SQL 조립이 있는 곳은 `pg-restore.sh:13`의 `$DB`뿐이며 정규식 검증 후 사용(:5, 9). `pg-backup.sh:22` 동일. 계정 이름도 정규식(10-roles.sh:15). 프롬프트 인젝션은 deploy 범위 밖. |
| B6 SSRF | OK | 사용자 제공 URL은 추론 서버 주소뿐이며 http/https 검사와 계정 포함 거부(lib.sh `external_inference_setup`). 서비스 간 주소는 compose에 고정. |
| B7 웹 보안 헤더 | 문제 M | gateway가 설정하는 헤더는 Cache-Control/Content-Type/Retry-After/WWW-Authenticate뿐(Caddyfile grep). `X-Content-Type-Options`, `X-Frame-Options`/CSP `frame-ancestors`, `Referrer-Policy`, HSTS(TLS 후) 없음. 정적 이미지(kiosk-frontend, admin-console)가 자체로 붙이는지는 읽지 않았다. 쿠키·CORS는 쓰지 않음(기본 인증). 제안: 공통 `header` 블록 추가. CSP는 kiosk-frontend 변경 요청이 필요할 수 있다. 자율(헤더) / 결정 불필요. |
| B8 전송 | 문제 H | `auto_https off`, 리스너 `:8080` 평문(Caddyfile:1-4, 24). 기본 인증 암호, 기기 Bearer 토큰, 환자 발화가 평문이다(design.md:80, RUN.md:361, Caddyfile:232가 '미정'이라 적음). 내부 구간(gateway->서비스->postgres)도 평문(RUN.md:109)이며 서버 한 대 안의 Docker 네트워크라 노출 범위는 호스트 안. 추가: `compose.inference.yaml:54`는 GPU 서버의 추론 포트를 기본 `0.0.0.0` HTTP로 연다(Bearer 토큰만 보호) -> M. 완화: gateway 기본 바인드 127.0.0.1(compose.yaml:183, .env.example:5). 제안: 도메인·인증서 확정 전에는 바인드를 열지 말고, 확정되면 Caddy TLS 종단, 추론 서버는 사설망 바인드 또는 TLS. 결정. |
| B9 의존성·공급망 | 문제 M | 좋은 점: 영역 이미지와 서드파티 모두 digest 참조(compose.yaml:144, 165, 189 등; locks/images.lock), deploy 의존은 `==` 핀(requirements.txt). 문제: (1) 취약점 스캔·SBOM 도구 없음(`grep trivy|grype|sbom|pip-audit|npm audit` 결과 0). (2) `lock-third-party.sh:7-16`은 `caddy:2-alpine`, `postgres:16`, `registry:2`, `python:3.12-slim` 태그를 처음 한 번 pull해 digest로 고정하고 "이미 있으면 바꾸지 않는다" -> 보안 패치를 받는 절차가 없다. 서명(cosign 등) 검증 없음. (3) requirements.txt에 해시 없음. (4) `compose.llm.local.yaml`은 digest 없는 로컬 태그(데모 한정, compose.llm.yaml 주석). 제안: CI에서 이미지 스캔(오프라인 DB 필요 여부는 사용자 환경 결정), 서드파티 갱신 주기와 절차, `pip --require-hashes`. 일부 결정(스캔 도구·설치는 이 점검 제약상 하지 않음). |
| B10 속도 제한 | 문제 M | Caddyfile에 rate limit 없음. 기본 인증 시도 횟수 제한 없음(완화: 암호와 토큰이 `token_hex(24)` 무작위, gen-secrets.sh:21). 세션 시작 남발 방지도 없음. Caddy 기본 배포엔 rate_limit 모듈이 없어 커스텀 빌드 또는 호스트 방화벽/fail2ban 필요. 제안: 호스트 앞단 제한 또는 모듈 포함 빌드. 결정(배포 방식). |
| B11 오류 노출 | OK | 상류 장애는 고정 JSON `{"code":"UPSTREAM_UNAVAILABLE"}`, 내부 주소·오류 문구 없음(Caddyfile:255-272), `/readyz`는 `{"ready":false}`만(:51). 거부 응답도 고정 문자열. |
| B12 토큰·DB 최소 권한 | 문제 M | 좋은 점: 서비스별 DB·계정, PUBLIC CONNECT 회수, 슈퍼유저 아님(10-roles.sh:21-24, 40, 42), 암호 파일은 postgres만 마운트(compose.yaml:149), 서비스별 읽기/쓰기/역할별 토큰. 문제: (1) DB 계정이 자기 DB의 소유자라 DDL 권한이 상시 있다(10-roles.sh 머리말). 마이그레이션 계정과 런타임 계정 분리 없음. (2) 토큰에 만료·회전 주기 없음(수동). (3) 시험용 계정(staff-e2e, operator-e2e, trainer-e2e, reviewer-e2e)이 `config/gateway-accounts.conf`의 유일한 계정이라 운영 계정 정의 경로가 아직 없다(파일 머리말이 개발/E2E용이라 적음). 제안: 운영 계정·IdP 확정, 마이그레이션 계정 분리는 영역과 협의. 결정. |

### C. 데이터·개인정보

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| C1 PHI 목록 | 문제 L | deploy 관점에서 PHI가 닿는 곳: `pg-data`(survey 세션 등), gate-data 번들(PHI 아님으로 추정), 백업 덤프(pg-backup.sh:7이 개인정보 가능성을 적음), 컨테이너 json-file 로그, Caddy 접근 로그(원격 IP, URI의 세션 ID, 로그인 계정; 본문과 Authorization은 안 남음, Caddyfile:25-31). 이 목록을 한곳에 정리한 문서를 deploy docs에서 찾지 못했다(전체 grep은 하지 않았음). 제안: boundary.md에 저장·전송·기록 위치 표. 자율. |
| C2 최소 수집 | 해당 없음 | deploy는 데이터를 수집하지 않는다. 접근 로그 항목(원격 IP)만 해당하며 C1에 적었다. |
| C3 보존·삭제 | 문제 M | 백업 보존일은 설정이 없으면 거부(코드에 기본값 없음, backup.sh:10-12)라 안전하나 현재 설정이 없어 백업 자체가 없다(C7). 설정 후에도 환자 삭제 요청이 백업에 남는 기간 정책이 문서에 없다. ops-feedback 보존값은 사용자 결정 전(ops-feedback-job.yaml 주석, runbook 5-2). pg-data 자체의 TTL 잡 없음(jobs.yaml). 제안: 보존 기간 결정 + 백업에서의 삭제 처리 방침. 결정. |
| C4 비식별 | 문제 M | 로그 본문·Authorization은 접근 로그에 없음. 문제: PostgreSQL에 설정 파일이 없어 `log_min_error_statement` 기본(error)이 적용된다. 오류가 난 SQL 문장이 서버 로그에 리터럴 값과 함께 남을 수 있고(파라미터화 쿼리는 DETAIL에 파라미터), 그 로그는 호스트 json-file에 쌓인다(config/postgres에는 initdb 스크립트만, 확인함). 제안: `log_min_error_statement=panic`, `log_statement=none`, `log_parameter_max_length_on_error=0` 명시. 자율. |
| C5 저장·전송 암호화 | 문제 M | DB TLS 없음, 볼륨 디스크 암호화 없음(RUN.md:109 '확인하지 못한 것'으로 적음). 백업 덤프 암호화 없음(pg-backup.sh는 권한 700/600만, :14, 17). `gate-data` 백업은 `umask` 지정이 없어 기본 755/644(backup.sh:19-20, backup_tool.py에 chmod 없음; 번들이라 PHI는 아닌 것으로 추정). 제안: 호스트 디스크 암호화(LUKS) 확인, 덤프 암호화(age/gpg), 백업 폴더 700. 결정(키 관리). |
| C6 접근 기록 | 문제 L | 게이트웨이가 인증된 계정 ID를 `X-Openit-User`로 덮어써 서비스에 전함(Caddyfile:63, 94, 108 등), 키오스크 경로는 클라이언트 헤더 제거(:216). Caddy 접근 로그에는 user_id가 남지만 json-file 10m x 5로 회전되어(compose.yaml:12) 장기 감사 기록이 아니다. 감사 기록의 영속 저장은 서비스 DB 몫. 제안: 접근 로그를 호스트로 장기 보관할지 결정. 결정. |
| C7 백업·복원 | 문제 H | (1) `config/backup.env`가 없다(`ls`로 확인). backup 잡은 설정이 없으면 종료 코드 2로 거부(backup.sh:9, pg-backup.sh:10)하고 스케줄러가 FAIL로 기록한다. 즉 현재 운영 백업은 동작하지 않는다(O16 사용자 결정 대기, jobs.yaml:5). (2) `BACKUP_DIR`이 같은 호스트일 수 있고 오프사이트 사본·암호화 없음. (3) 복원 시험은 E2E가 지웠다 복구하는 한 번의 시험(runbook.md 4절)이고 정기 시험 잡 없음. (4) `backup-all.sh`는 `backup.sh` 인자 없이 호출해 `gate-data`만 백업한다(backup.sh:21, backup-all.sh:5). `models-data`(모델 패키지 레지스트리)와 `registry-data`는 스케줄 백업 밖이다(compose.yaml:44는 serving-data만 '다시 받을 수 있음'). (5) 5개 DB는 순차 pg_dump라 각자 다른 시점이다(pg-backup.sh:30-36). DB 간 참조 정합(survey와 ops_log 등)과 gate DB와 gate-data 번들 파일의 쌍이 보장되지 않는다. (6) 복구 후 서비스 재가동과 DB 정합 확인 절차 없음. 좋은 점: 덤프 폴더 700/파일 600(pg-backup.sh:14), MANIFEST sha256 검증 후 복구(pg-restore.sh:11-13), 보존 삭제 시 최근 1개 유지, 복구는 서비스 중지를 강제(:14-15). 제안: backup.env 결정 후 `models-data` 포함, 덤프 직후 일관 스냅샷 방식(또는 쓰기 정지 구간) 결정, 정기 복원 시험 잡, 암호화·오프사이트. 결정(O16: 허용 중단 시간·복구 시점) + 자율(스크립트·문서). |
| C8 DB 계정 | OK | 서비스별 DB·계정·전용 네트워크(compose.yaml:30-37, 154), PUBLIC CONNECT 회수(10-roles.sh:21-24, 40), 서비스별 DSN 비밀은 소유 서비스만 마운트(compose.yaml:212, 234, 254, 274). 소유자 권한 문제는 B12. 마이그레이션 시 슈퍼유저 필요 여부는 확인하지 못했다. |
| C9 마이그레이션 순서·되돌리기 | 문제 M | `rollback.sh`는 이미지 digest만 되돌린다(rollback.sh:2 머리말이 내용 축은 게이트 몫이라 명시). 스키마 마이그레이션이 서비스 기동 시 자동인지, 롤백한 이전 이미지가 이미 올라간 스키마를 읽는지에 대한 deploy 문서가 없다. `up.sh`는 적용 전에 자동 백업을 만들지 않는다(up.sh 전체 확인). PostgreSQL 주 버전 업그레이드(16 고정, locks/images.lock) 절차 없음. 제안: 업그레이드 전 `pg-backup.sh` 실행을 `up.sh`/런북 필수 단계로, 영역별 마이그레이션 호환(롤백 가능 범위) 표. 자율(문서·스크립트), 영역과 협의. |
| C10 정합성 | 해당 없음 | 스키마·제약은 영역 DB 몫. deploy는 `--data-checksums`(compose.yaml:148)와 UTC 타임스탬프(백업 폴더 `date -u`, backup_tool.py gmtime)만 맡는다. |

### D. 정확성·계약

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| D1 API 계약 | 확인 못 함 | gateway 경로 목록(Caddyfile)이 `boundary-contracts/HTTP.md` 및 PUBLIC_API와 일치하는지 대조하지 않았다(읽기 허용 범위지만 이번에 열지 않음). |
| D2 상태 기계 | 해당 없음 | deploy는 상태 기계를 갖지 않는다. |
| D3 멱등·중복 | OK | gateway가 요청을 재전송하지 않는다(`lb_try_duration 0`, Caddyfile:213, 217)라 중복 처리가 생기지 않는다. 스케줄러 잡은 flock과 멱등 설계(jobs.yaml 머리말, scheduler.py:60). |
| D4 시간·시계 | 문제 L | 스케줄러는 `time.time()` 벽시계 기준(scheduler.py:54, 58)이라 시계가 뒤로 가면 `t-last`가 음수가 되어 다음 실행이 지연된다. NTP 동기 확인이 doctor/check-health에 없다. 제안: monotonic 병행 또는 시계 역행 감지, 시간 동기 점검. 자율. |
| D5 인코딩·크기 | 문제 M | B4와 같은 원인(본문 상한 없음). 8MiB 계약 상한을 gateway가 강제하지 않는다. |
| D6 값 지어내기 | 해당 없음 | 모델 출력 검증은 영역 몫. |
| D7 문서-코드 일치 | 문제 M | (1) `docs/runbook.md` 4절은 낡았다: 저장소 `survey-data qa-data ops-data`, `registry.sqlite3`(runbook.md 4절)를 말하지만 현재 파일 저장소는 `gate-data`뿐이고 DB는 PostgreSQL이다. 비상 때 이 절차로는 PostgreSQL을 복구하지 못한다(최신 절차는 RUN.md:98-100에 있음). (2) runbook 8절의 SQLite 오류 행도 PostgreSQL 이전 내용. (3) `down.sh`의 `describe()`가 존재하지 않는 `qa-data`, `ops-data` 볼륨을 설명(down.sh 앞부분). (4) gen-secrets.sh 머리말은 644 이유를 설명하나 체크리스트 F5(0600/0400)와 문서 상 불일치. 제안: runbook 4절을 pg-backup/pg-restore 기준으로 교체, 낡은 이름 정리. 자율. |

### E. 운영성

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| E1 구조화 로그 | 문제 L | Caddy 접근 로그는 JSON stdout(Caddyfile:28-31). 스케줄러는 잡 출력의 마지막 한 줄만 `last_msg`에 저장(scheduler.py:66-67)하고 전체 출력을 버려(capture_output 후 폐기) 잡 실패 원인 추적이 어렵다. 한 tick 안에서 긴 잡이 다른 잡을 지연시킨다(순차 실행). 제안: 잡별 로그 파일 또는 stdout 전달. 자율. |
| E2 메트릭·경보 | 문제 M | 메트릭 수집 없음. 경보 기준은 check-health.sh의 80/90% 등 시작값(runbook.md 5-1). 컨테이너 로그·Docker 볼륨·postgres 디스크 경보는 '아직 하지 않은 것'으로 문서가 인정(runbook 5-1). 제안: 도커 볼륨 사용량 점검 추가. 자율. |
| E3 설정 | OK | 필수 값은 `${VAR:?}`로 시작 거부(compose.yaml:144, 165, 189), 백업 설정 누락·비정수 거부(backup.sh:9-12), 스케줄러 설정 검증(scheduler.py:34-40), compose 사전 점검 `check-compose.sh`(up.sh), 기본 바인드 127.0.0.1. |
| E4 런북 | 문제 M | runbook.md는 상당히 갖췄다(설치, 롤백, 백업, 감시, 흔한 문제). 빠진 것: PostgreSQL 복구 절차(D7), 디스크 가득, 비밀 노출 시 전체 회전, 호스트 재부팅 후 절차, 레지스트리 유실(이미지 prune) 대응(FAULT_MATRIX G2가 '문서 없음'). 제안: 장애별 표 추가. 자율. |
| E5 감시·알림 경로 | 문제 M | `check-health.sh`와 스케줄러를 부르는 systemd 유닛은 예시 파일로만 있고 설치되지 않았다(config/systemd/*.service 머리말 '이 리포는 설치하지 않는다'). 알림 수단 `OnFailure=`은 주석 처리(openit-check-health.service). `external-monitor.example.yaml`의 url은 null(SKIP). 즉 CRIT가 나도 아무도 모른다. 백업 실패(C7)와 겹치면 조용히 무백업이 된다. 제안: 알림 수단 결정 후 유닛 설치 절차 확정. 결정. |
| E6 용량 계획 | 확인 못 함 | deploy 문서에서 디스크·메모리 용량 산정 근거를 찾지 못했다(전체 문서를 읽지 않음). E2E 소요 시간 외 측정은 확인 못 함. |
| E7 시작 순서 | OK | `depends_on: condition: service_healthy` 체인(compose.yaml:175-181, 218-222, 237-239, 257-258, 277-278), postgres는 TCP 기반 healthcheck로 초기화 완료 후 healthy(:156-161). |
| E8 시간 불변식 | OK | 키오스크 10초 > gateway 1+8.5=9.5초 > 서버 6초가 Caddyfile 주석(:211-213)에 있고 코드(:219-220)와 같다. 사람용 화면의 상한(2s+15s/10s)도 명시(:14-23). 세 값이 서로 다른 리포에 있어 어긋날 위험은 FAULT_MATRIX N21가 이미 지적. |

### F. 배포·이미지

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| F1 비root·읽기전용·권한·포트 | 문제 M | 서비스별 표(운영 compose.yaml): 모든 상시 서비스가 `x-hardening`(restart, `no-new-privileges`, `cap_drop: ALL`, `read_only: true`, tmpfs, 로그 회전; compose.yaml:6-12). privileged, docker.sock, host network, pid 공유 없음(`grep` 결과 없음; 스케줄러는 호스트에서 돌고 소켓을 컨테이너에 주지 않는다, scheduler.py 머리말). 비root: postgres `999:999`(:145), gateway `10001`(:166), 나머지는 이미지 `USER`(Dockerfile: app, 10001, node, gate; build/ctx/*/Dockerfile). 호스트 포트: 운영에서 gateway만 `127.0.0.1:8080` 기본(:183), registry도 127.0.0.1(compose.registry.yaml:12). 문제: (1) 레지스트리 컨테이너에 강화 설정이 전혀 없다(read_only, cap_drop, no-new-privileges, user, tmpfs 없음; compose.registry.yaml:7-17). (2) `compose.inference.yaml:54` 기본 `0.0.0.0` 바인드. (3) `job-*`는 `read_only`와 `cap_drop`은 있으나 `user:`를 지정하지 않아 이미지 USER에 의존(compose.yaml:314-349). (4) gateway에 `cap_add: NET_BIND_SERVICE`(:167)는 8080 포트라 불필요해 보이나 주석은 바이너리 파일 권한 때문이라 설명(추정, 제거 시험 안 함). (5) `edge`, `serving`, `authoring` 네트워크는 internal이 아니라(compose.yaml:21-23, release/logs/db-*만 internal) 이 네트워크의 모든 컨테이너가 외부 인터넷에 나갈 수 있다. 제안: 레지스트리 강화, 추론 서버 바인드 기본을 127.0.0.1 또는 명시 필수, 서비스가 외부에 나가야 하는 곳이 없으면 egress 차단. 자율(레지스트리·바인드 기본), 네트워크 변경은 영역 호출 확인 필요. |
| F2 이미지 핀·재현·스캔 | 문제 M | 핀: 영역 이미지와 서드파티 digest 고정(locks/images.lock, compose.yaml:189 등). 라벨: 커밋 정보 `*_REVISION`이 잠금에 있음. 문제: B9와 같다(스캔·SBOM 없음, 서드파티 갱신 절차 없음). 재현 가능 빌드: pip/npm 해시 고정을 확인하지 못했다(requirements.txt 해시 없음, build-images.sh 전체는 읽지 않음). |
| F3 compose 자원·restart·네트워크·볼륨 | 문제 M | restart: 상시 서비스 `unless-stopped`(compose.yaml:7)와 registry(compose.registry.yaml:8), 잡은 일회성이라 없음. healthcheck: 있음(kiosk-frontend은 이미지 의존). 네트워크 분리: DB 네트워크 4개를 internal로 분리해 클라이언트끼리 서로 닿지 않게 한 점은 양호(compose.yaml:28-37). 볼륨: 이름 있는 볼륨 파일 저장소별 하나, 설정은 `:ro`(:152, :326). 문제: 자원 한도 전무(A9), job 서비스에 logging 옵션 없음(A6), 볼륨 파일 권한은 이미지 소유자에 의존. |
| F4 롤백·업그레이드 순서 | 문제 M | `rollback.sh`는 잠금 이력으로 digest를 되돌리고 `check-compose.sh` 후 `up.sh`(rollback.sh:11-23). 업그레이드는 "바뀐 서비스만 교체"(runbook 2절). 문제: C9와 같다(DB 호환, 업그레이드 전 백업 없음), 영역 버전 정렬은 `check-versions.sh`와 계약 태그 단일 출처 `lib.sh`(DEPLOY_BC_TAG 등)로 처리. 서비스 교체 순서(예: release-gate, survey)가 compose `depends_on`에 의존하고 롤링 교체는 없다(다운타임 허용, D10 비보증). |
| F5 비밀 파일 권한·compose 환경 | 문제 M | compose 환경에 비밀 값 없음: `*_FILE=/run/secrets/..`만(compose.yaml:204-211 등), 정적·동적 검사 스크립트 있음(check-secrets-hidden.sh 머리말; 실행은 안 함). 권한은 0600/0400이 아니라 644(B3). E2E 임시 비밀 폴더도 폴더 700, tokens 62개 파일이 644임을 `stat`으로 확인(`state/e2e-89132/secrets/tokens`). 폴더 700이 호스트 다른 사용자를 막지만 같은 사용자·docker 그룹은 읽는다. 결정(B3). |
| F6 레지스트리·CI 신뢰 경계 | 문제 M | `registry:2`는 인증·TLS 없음, 그래서 127.0.0.1에만 바인드(compose.registry.yaml:1 주석), 삭제 기능 켜짐(:14). push 경로(CI->서버)는 미정(ci.md:34, runbook.md 1절). 완화: 소비 쪽은 digest 고정이라 레지스트리가 바뀐 이미지를 내놓아도 digest 불일치로 거부된다(compose.yaml:189 형식). 문제: digest를 올리는 PR/CI 경로 자체의 신뢰, 서드파티 이미지 서명 미검증, 레지스트리 컨테이너 강화 없음(F1). 제안: CI 경로 확정(self-hosted runner 등), 서명 또는 최소 digest 검토 절차. 결정(CI 접근 방식). |

### G. 성능·용량

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| G1 측정 한계 | 확인 못 함 | gateway 응답 시간 실측은 있다(E2E 5w 8.5s, FAULT_MATRIX 기록). 처리량·동시 키오스크 수 한계는 deploy 문서에서 찾지 못했다. |
| G2 연결·풀·인덱스 | 문제 L | PostgreSQL 설정 파일이 없어 `max_connections=100` 기본이며, 서비스별 `ALTER ROLE ... CONNECTION LIMIT`도 없다(10-roles.sh 전체 확인). 서비스 풀 크기 합이 한도를 넘는지 확인하지 못했다. 한 서비스의 연결 폭주가 다른 서비스를 막을 수 있다. 제안: 계정별 연결 상한과 postgres 메모리 설정. 자율(값은 시작값). |
| G3 큰 입력 폭주 | 문제 M | B4(본문 상한 없음) + A9(메모리 한도 없음)의 조합. |

### H. 시험 품질

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| H1 핵심 경로 | 문제 L | E2E가 실제 compose, 실제 postgres, 실제 스케줄러, 백업·복구, 코드 롤백까지 돌고 두 환경에서 실패 0이라고 FAULT_MATRIX:16이 기록(실행하지 않고 기록만 읽음). 한계: 모델 백엔드는 fake, 알림·실패 주입은 일부만(스케줄러 단계는 정상 상태만, FAULT_MATRIX 389행 근방), 백업 실패 알림 경로는 시험 불가(알림 수단 없음). |
| H2 간헐 실패 | OK | 고정 포트를 쓰지 않는다: 컨테이너 포트는 Docker 배정(compose.test.yaml:13-32 `127.0.0.1::8080`), `free_port`(lib.sh), 레지스트리 재시도 루프(registry.sh). 프로젝트 이름에 pid(`deploy-e2e-<pid>`). |
| H3 건너뛰는 시험 | 확인 못 함 | `--fast`가 생략 구간과 '전체 합격 아님'을 표시한다고 runbook 6절이 적으나 시험 코드를 읽지 않았다. |
| H4 부정 시험 | 확인 못 함 | `test-gateway-auth.sh`, `test-check-secrets-hidden.sh`, `backup-bad.env` 등이 존재함은 확인했으나(파일 목록) 내용과 통과 여부는 열지 않았다. |
| H5 환경 의존 | OK | 두 환경(이 PC, gpu-dev)에서 전체 E2E 통과 기록(FAULT_MATRIX:16). `doctor.sh`, `check-relocatable.sh`, `check-standalone.sh`가 설치 방식 의존을 점검. 둘 다 실행하지 않고 기록을 읽었다. |

### I. 도메인·안전

| 항목 | 판정 | 근거·제안 |
|---|---|---|
| I1 환자 안전 결정 | 해당 없음 | deploy에는 직원 호출·위험 신호 판단 코드가 없다(위험 신호 입력 경로는 게이트웨이에 열지 않음, Caddyfile:204-207). |
| I2 환자 문구 출처 | 해당 없음 | deploy는 환자 문구를 만들지 않는다. gateway 오류 본문은 JSON 코드뿐. |
| I3 실패 시 환자 화면 | OK | gateway가 상류 장애를 `503/504 UPSTREAM_UNAVAILABLE` + `Retry-After`로 구분해 알리고 빈 응답을 내지 않는다(Caddyfile:257-272). 화면 처리는 kiosk-frontend 몫(FAULT_POLICY 7). |

## 이 점검이 읽지 못한/얕게 본 곳

- `secrets/` 내용은 열지 않았다. 이 체크아웃에는 `secrets/` 폴더가 없어(`ls`) 운영 비밀 파일의 실제 권한은 확인하지 못했고, E2E 임시 비밀 폴더(`state/e2e-89132/secrets`)의 `stat` 권한(폴더 700, 파일 644)으로 gen-secrets.sh의 결과를 추정했다.
- 실행한 검증이 없다. E2E, `test-*.sh`, `check-secrets-hidden.sh`, `doctor.sh`, `check-compose.sh`를 돌리지 않았고, 통과 상태는 FAULT_MATRIX와 문서의 기록을 읽은 것이다. 컨테이너가 실제로 비root, 읽기 전용으로 도는지(`docker inspect`)는 확인하지 못했다. Dockerfile의 `USER`는 `build/ctx`의 사본을 읽은 것이라 게시된 이미지와 같은지는 모른다.
- 읽지 않은 파일: `build-images.sh`, `publish-image.sh`, `publish-images.sh`, `check_health.py`, `check-health.sh`, `doctor.sh`, `status.sh`, `demo.sh`, `e2e.sh`, `e2e_steps.py`, `backup_tool.py`(권한 관련 grep만), `kiosk-add-device.sh`, `prepare-host.sh`, `compose.test.yaml`/`compose.llm*.yaml`(일부), `docs/design.md`, `boundary.md`, `E2E.md`, `ci.md`(제목 줄만), `RUN.md`(일부 줄만), `SETUP.md`, `.env.example` 값, 영역 CI 예시(`docs/ci-example`).
- Caddy 동작 가정: `path` 패턴의 `*`가 슬래시를 넘는지, `handle` 블록 간 순서, `header_up`이 클라이언트 값을 덮어쓰는지는 Caddy 문서 지식에 따른 추정이다. 이 영역의 E2E/`test-gateway-auth.sh`가 위조 헤더를 시험하는지는 열지 않았다(B1·B2의 OK는 설정 읽기 근거).
- PostgreSQL 실제 설정(`SHOW`)과 `pg_hba.conf` 최종 상태는 initdb 스크립트(10-roles.sh)를 읽은 것이고 실행 중 서버에서 확인하지 않았다. `log_*` 기본값 판단(C4)은 공식 이미지의 기본값에 대한 지식이다.
- 이미지의 취약점, 서드파티 이미지 서명, 호스트 방화벽·Docker 데몬 설정(userns, live-restore, 로그 드라이버 기본값)은 범위 밖으로 보고 확인하지 못했다.
- 다른 영역(survey-service 세션 소유권, 마이그레이션 방식, 서비스의 SIGTERM 처리)과 boundary-contracts HTTP.md 대조는 하지 않았다(D1, A4).
