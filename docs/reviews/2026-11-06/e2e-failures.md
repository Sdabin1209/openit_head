# E2E 실패 조사 (2026-11-06)

범위: `progress/rep/e2e-final-0028.log` 및 deploy 작업 트리 `../deploy/build/wt-deploy-450-lg`의 진단 `state/e2e-diag-20261106-005803`. 전체 E2E 재실행·제품 코드 수정 없이 로그와 현재 소스를 대조했다. deploy 기본 체크아웃과 실제 E2E 작업 트리는 다르다.

## 1. ops-feedback DB 비밀 읽기 실패를 무시한 초기화 (높음, 미해결)

진단 `logs/deploy-e2e-17432-ops-feedback-db-1.log:36`부터 계정 4개의 비밀 파일 읽기에 Permission denied가 발생한다. 곧바로 PostgreSQL이 `empty string is not a valid password, clearing password`를 기록하고, 이후 `User "ops_log_owner" has no password assigned`로 준비 확인이 계속 실패한다.

현재 `../ops-feedback/db/10-accounts.sh:19`는 psql 백틱에서 `head`로 암호를 읽는다. 외부 명령 실패가 SQL 오류로 전달되지 않아 `set -e`·ON_ERROR_STOP으로 막지 못한다. 파일 존재·크기 검사만으로 읽기 성공을 보장하지 못한다. 읽기 권한 문제와 실패 후 진행 문제를 함께 수정해야 한다. postgres로 사용자 전환 시 보조 그룹이 유지되는지도 확인해야 한다(이 원인은 아직 실증하지 않음). 암호를 읽을 수 없거나 비었으면 계정 생성 전 실패해야 한다.

## 2. 문항 DB의 쓰기 경로가 읽기 전용 배포와 불일치 (높음, 수정 커밋 있음)

진단 question-authoring-db 로그 첫 줄부터 `/var/lib/postgresql-tls` 생성·복사가 실패한다. 뒤의 “인증서가 없다”는 메시지는 복사 실패의 후속 증상이다. Compose는 루트를 읽기 전용으로 하고 `/tmp`, `/run`만 tmpfs로 제공한다.

현재 question-authoring `94666e0`은 인증서 사본을 `/run`으로 옮기고 같은 배포 조건의 이미지 시험을 추가했다. 해당 수정 이미지를 사용한 전체 E2E 통과는 이번 조사에서 확인하지 않았다.

## 3. 사용자 등록 잡의 필수 입력과 실행 경로 불일치 (높음, 재검증 필요)

E2E 로그 228행: `IdentityEnv 위반: IDENTITY_PUBLIC_URL: 필수인데 없다`. deploy Compose의 identity 서버에는 이 값이 있지만 `job-identity-register-users`에는 없다. 잡 실행이 서버용 환경 검사로 들어간 것이 직접 실패 지점이다.

platform `808410d`는 잡 argv를 절대 경로로 실행하도록 진입점을 수정했다. 이 수정이 실제 실행 이미지에 반영되고 잡 전용 입력만으로 동작하는지 단독 확인해야 한다. 서버용 값을 무조건 추가하기 전에 잡의 선언과 실제 진입점을 대조해야 한다.

## 4. 단독 시험의 비밀 권한이 배포보다 느슨함 (중간, 미해결)

현재 `../ops-feedback/scripts/smoke.sh:48`은 비밀 파일에 644를 준다. deploy `scripts/gen-db-secrets-all.sh:19`는 폴더 750·파일 640을 준다. 이 스모크 통과는 운영 권한에서의 읽기 성공 근거가 아니다. 앱 스모크 외에 DB 이미지 초기화도 실제 UID/GID·권한·읽기 전용 조건으로 시험해야 한다.

## 5. 선행 실패 뒤 사용자 등록을 실행해 실패를 중복 집계 (중간, 미해결)

deploy `scripts/e2e.sh:296-300`은 compose 기동과 사용자 등록을 모두 `chk`로 실행한 뒤 의존성과 중단을 설정한다. 기동 실패 뒤에도 등록 잡을 실행한다. 등록 잡 자체의 결함은 별개로 존재하지만, 기동 실패 실행에서는 등록 성공을 요구할 수 없다. 기동 실패 시 등록은 SKIP하고 독립적인 잡 시험에서 검증해야 한다.

## 다음 검증 순서

1. DB 비밀 읽기 불가·빈 암호의 음성 시험과 실제 권한의 빈 볼륨 초기화.
2. 수정된 문항 DB 이미지의 읽기 전용 기동.
3. identity 잡 선언 argv 그대로 실행하는 사용자 등록 단독 시험.
4. E2E 선행 의존성 판정 확인 후 통합 실행.

이 실행은 준비 단계에서 중단되었으므로 문진·릴리스·복구 시나리오의 정상 여부는 판정할 수 없다. 별도 `smoke-ro2-0153/sum.txt`에는 survey-service rc=1도 남아 있지만, 해당 로그만으로 원인을 확정하지 않았다.


## 수정·검증 결과 (2026-11-06)

- ops-feedback `6f1234d`: 배치 비밀 0640 유지, postgres 전용 tmpfs 사본 준비, 읽기 실패·빈 첫 줄 거부, psql 외부 명령 실패의 SQL 예외 처리, postgres 사용자로 TLS 갱신 신호. DB·잡 선언·비밀 시험 37개 통과. 최종 SQL 변경 뒤 계정 접속·빈 암호·비밀 누락 시험 4개 추가 확인, 0640 앱 스모크 통과.
- question-authoring `88df89a`: 같은 비밀 사용자 전환 문제 수정, 배포 권한의 이미지 시험 13개 통과. 기존 /run TLS 경로 수정도 이 시험에 포함된다.
- survey-service `d06156b`: 같은 비밀 사용자 전환 문제 수정. DB 이미지 전체 회귀 통과, 최종 capability 조건의 계정·TLS·권한 시험도 별도 통과.
- release-gate `3a8e696`: TLS 갱신 신호를 postgres 사용자로 보냄. 배포 capability·읽기 전용 조건의 DB 시험 10개 통과.
- deploy 작업 트리 `5a806ab`: 기동 실패 시 사용자 등록 SKIP. 의존성 시험 3개 통과.
- platform: 기존 `808410d`의 잡 진입점 수정을 실제 Keycloak 스모크로 검증했다. 라벨 argv 그대로 사용자 등록·멱등성·잘못된 관리자 암호 거부·로그인·출구 차단 변이가 통과했다. 새 코드 변경 없음.
- boundary-contracts: verify.py 종료 0. 계약 스키마는 변경하지 않았다. 이번 결함은 기존 AreaDatabaseEnv·DatabaseDeclaration·JobsDeclaration을 따르는 구현으로 수정 가능했으며, 이 범위에서 스키마 정의 오류는 발견하지 못했다.

추가 발견: 제한된 capability에서 root가 postgres에 직접 SIGHUP을 보내지 못했다. CAP_KILL을 더하지 않고 같은 postgres 사용자로 신호를 보내도록 수정했다.

원칙: 부족하거나 잘못된 스키마는 계약 소유자가 먼저 수정하고 생산자·소비자가 모두 정렬한다. 구현 예외나 이웃 내부 구조 의존으로 우회하지 않는다.

범위 한계: 수정은 로컬 커밋이며 push하지 않았다. 전체 E2E는 재실행하지 않았으므로 통합 성공을 선언하지 않는다. 준비 도구는 커밋된 HEAD를 복제하므로 다음 실행 전에 새 HEAD 기준 setup-env 보고·이미지 생성이 필요하다. 기존 작업자의 스모크 변경은 이번 커밋에 섞지 않고 보존했다.
