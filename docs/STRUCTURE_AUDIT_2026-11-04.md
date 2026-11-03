# 구조 전수 점검 (헤드, 2026-11-04 04:15) — 표준에서 벗어난 것 전부

대상: deploy compose 전부(compose*.yaml 10개), config/, systemd 타이머, 영역 사이 경로. 기준: 구조 규칙 6개(D104), 12-Factor(III 설정·IV 백킹 서비스·V 빌드/릴리스/실행 분리·XII 관리 프로세스), Database per Service, 배포 도구와 실행 플랫폼의 분리(플랫폼 엔지니어링 관행).
모든 항목은 고친다. "남김" 항목은 없다.

## S. 구조 결함 (고칠 것)

| # | 결함 | 표준 | 고침 |
|---|---|---|---|
| S1 | deploy(배포 도구)가 실행 중 서비스를 소유: gateway | 12-Factor V(빌드·릴리스·실행 분리), 도구≠플랫폼 | 플랫폼 영역으로 옮김. deploy 는 이미지·설정을 놓고 실행만 |
| S2 | 사람 인증: oauth2-proxy, keycloak, keycloak DB | 같음 | 플랫폼 영역 |
| S3 | 인증서: step-ca, pki-root, pki-tokens, 인증서 컨테이너 12개(*-cert, postgres-cert) | 같음 | 플랫폼 영역 |
| S4 | 서비스 TLS 종단: *-tls 사이드카 11개, *-net(pause) 10개 | 사이드카는 플랫폼이 주입하는 패턴(서비스 메시 관행) | 플랫폼 영역이 사이드카 이미지·설정(tls-sidecar.caddy)을 소유, deploy 는 놓기만 |
| S5 | 데이터베이스: postgres, postgres-reload, config/postgres, pg-*.sh | 12-Factor IV(백킹 서비스는 설정으로 붙는 자원) | 플랫폼 영역이 서버를 소유. 영역마다 따로 주는 데이터베이스·계정(이미 분리됨)만 영역 사이 계약 |
| S6 | 감시: prometheus, alertmanager, blackbox, json-exporter, node-exporter, gateway-root, config/prometheus | 같음 | 플랫폼 영역 |
| S7 | 백업: backup-target, backup*.sh, openit-backup*.timer | 같음 | 플랫폼 영역 |
| S8 | 잡 스케줄러: systemd 타이머 6개, run-job.sh, sd_jobs.py | 같음 | 플랫폼 영역(스케줄러). 영역 잡과는 JobsDeclaration·*JobResult 로만 |
| S9 | 게이트웨이가 영역 API 경로·메서드·역할을 Caddyfile 에 직접 적음(경로 규칙 48곳) | 구조 규칙 1·4: 남의 구조를 모른다. 계약 Exposure 스키마가 이미 있음 | 게이트웨이 경로 표를 영역 이미지의 `io.openit.exposure` 선언(Exposure)에서 만든다. 손으로 쓴 영역 경로 금지 |
| S10 | deploy compose 가 영역 잡 명령(`python -m …`)을 직접 적음(5곳 + migrate 1곳) | 구조 규칙 1·4. 계약 JobsDeclaration 이 이미 있음 | 잡 정의를 이미지의 `io.openit.jobs` 선언에서 만든다 |
| S11 | 영역 사이 계약(RUNTIME 3.4.4 이전)이 deploy 내부 구조를 정함 | 구조 규칙 5·6 | 3.4.4(60dc386)에서 정정함. 플랫폼 영역이 생기면 R 조항의 "배포"를 "플랫폼"으로 |
| S12 | 계약 스키마 94개 중 54개에 생산자·소비자(누구의 입력·출력인지)가 없음 | 계약 = 누구의 입력 → 누구의 출력 | 모든 스키마에 x-producer·x-consumers, 빠지면 실패하는 시험 |
| S13 | RUNTIME 행에 "출력하는 쪽·받는 쪽" 칸 없음 | 같음 | 칸 추가 |
| S14 | 영역 의존 태그(link v0.4.9, boundary-contracts v3.4.3)가 원격에 없어 5개 영역 빌드 시험 실패 | 의존은 Git 태그로 설치(워크스페이스 규칙). 원격 동결 중 | 로컬 리포를 받는 표준 경로 하나(git `url.<base>.insteadOf` 를 `GIT_CONFIG_GLOBAL` 파일로)로 점검·빌드 모두 같게 |
| S15 | 게이트웨이 `header Cache-Control no-store`(? 없음 3곳)가 앱이 정한 값을 덮어씀 | RUNTIME R2.1 | `?` 접두(앱이 정하지 않았을 때만) |
| S16 | 호출 × 실패 표의 칸 확정이 끝나지 않음(이전 초안 빈칸·모순 약 250줄) | 계약 = 모든 입력에 출력 | 칸 확정 → 열린 칸은 계약 행으로 |
| S17 | 독립 검토 없이 계약을 고정해 옴 | — | 고정 전 독립 검토 2건 |

## C. 계약 대비 코드 결함 (계약 고정 뒤 영역별로 고칠 것, 04:00 보고에서)

| 영역 | 빠진 것 |
|---|---|
| survey-service | R2.4 스트림 종료, SSE 상한 초과 429, R3.10, R4.1, R10.3, R3.18 Retry-After 재전송 |
| release-gate | 전체 시험 1건 실패(test_graceful_stop…[sqlite]), R8.1·R10.3·R10.5 확인 |
| model-lab | R9.1, R4.1, R3.10 |
| synthetic-data | R4.1 |
| question-authoring | 마지막 커밋 뒤 전체 시험 재실행 |
| ops-feedback | 변이 확인 |
| deploy·플랫폼 | R3.12 인증 확인 시간 한도→503, R10.4 속도 제한, R3.16 포화→503, R4.6 전체 재시작 시험, R6.1·R6.2·R6.4 점검, R2.2 |
| 전 영역 | 폐지된 조항 번호(R2.3·R4.2·R4.4·R4.5·R5.2·R5.3·R8.2·R10.7·R10.10)를 참조하는 커밋·대응표를 새 번호/자기 문서로 |

## 결정 필요 (사용자, 1건)
- 플랫폼 서비스(S1~S8)를 **영역 하나(platform)** 로 묶을지, 넷(입구·인증 / 인증서 / 데이터베이스·백업 / 감시·스케줄러)으로 나눌지.
