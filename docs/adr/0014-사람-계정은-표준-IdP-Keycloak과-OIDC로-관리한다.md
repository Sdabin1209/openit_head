# 0014. 사람 계정은 표준 IdP(Keycloak)와 OIDC로 관리한다

- 상태: 채택 (2026-11-03, 사용자 결정 U82)
- 관련: OPEN_GAPS U82·L08(계정), D84(비밀은 파일), D88(사람 인증), D106(X-Openit-User), 영역 ADR: deploy(구현), admin-console(화면)

## 맥락
사람 계정은 조직이 주는 정적 파일(`secrets/staff-accounts.conf`)을 게이트웨이 basic_auth 조각으로 바꾸는 방식뿐이었다. 가입 신청, 승인(어떤 역할을 줄지), admin 역할, 초기 admin 계정, 로그인 기록이 없었다. 사용자는 역할을 계정마다 붙는 플래그로 보고(한 사람이 reviewer이면서 clinician일 수 있다), 가입 신청과 승인을 요구했다.

## 결정
1. **IdP는 Keycloak(26.x) 컨테이너.** realm `openit` 하나. 같은 PostgreSQL에 별도 데이터베이스 `keycloak`과 별도 계정(최소 권한, L08과 같은 원칙).
2. **역할은 그룹(계정마다 여러 개).** 그룹 이름 = 지금 게이트웨이 역할 이름: `staff`, `operator`, `release-approver`, `reviewer`, `author`, `clinical-reviewer`, `clinician`, 그리고 새 `admin`(계정 승인·역할 부여).
3. **게이트웨이는 OIDC로 사람을 인증한다.** oauth2-proxy(OIDC 클라이언트)를 두고 Caddy가 사람 경로에 `forward_auth`로 묻는다. oauth2-proxy가 돌려준 사용자 ID·그룹을 Caddy가 받아 `X-Openit-User`(D106 그대로)와 역할 판정에 쓴다. 클라이언트가 보낸 같은 이름의 헤더는 지금처럼 지운다. 서비스는 바뀌지 않는다(계약 변경 없음: 서비스는 이미 `X-Openit-User`와 게이트웨이 역할 판정만 믿는다).
4. **가입 신청 = Keycloak 자가 등록**(realm 설정 registrationAllowed). 새 계정은 그룹이 없어 로그인은 되지만 모든 사람 경로에서 403이고, admin-console은 "승인 대기" 안내를 보인다.
5. **가입 승인 = admin 그룹 계정이 그룹을 부여**하는 것. 화면은 Keycloak 표준 관리 화면(사용자 → 그룹 지정)을 쓴다. admin-console은 승인 대기 안내, 현재 사용자·역할 표시, 로그아웃, Keycloak 관리 화면 링크만 둔다(같은 기능을 다시 만들지 않는다).
6. **초기 admin**: 설치 때 `gen-secrets.sh`가 초기 admin 비밀번호 파일을 만든다. Keycloak의 부트스트랩 관리자(`KC_BOOTSTRAP_ADMIN_USERNAME/PASSWORD`)는 비밀을 환경 변수로만 받으므로 deploy 엔트리포인트 래퍼가 `*_FILE`을 읽어 넘긴다(D84). 일회성 초기화 잡이 realm을 가져오고(import), `openit` realm에 초기 admin 계정을 만들어 `admin` 그룹에 넣는다. 첫 로그인 때 비밀번호 변경을 요구한다(required action UPDATE_PASSWORD).
7. **로그인 기록 1년**(사용자 결정 D-A: 감사 1년): realm 이벤트 저장 켜고 만료 365일.
8. **정적 계정 파일 경로는 제거한다**(`staff-accounts.conf`, `apply-accounts.sh`, basic_auth 조각). 기계 토큰 경로(기기 토큰, 추론·레지스트리 기계 토큰)는 사람 계정이 아니므로 그대로 둔다.
9. **E2E 계정**은 E2E 스크립트가 운영 입구(Keycloak 관리 API, admin 자격)로 만든다. 제품 구성에 시험용 계정·플래그를 넣지 않는다.

## 왜
- 표준: OpenID Connect Core 1.0(인증), OAuth 2.0(RFC 6749). Keycloak은 CNCF 인큐베이팅 프로젝트로 자가 등록·그룹·이벤트 기록·관리 화면을 기본 제공한다. oauth2-proxy + 리버스 프록시 forward_auth는 기존 앱을 OIDC 뒤에 두는 표준 배치다.
- 서비스와 계약을 바꾸지 않는다: 신원 전달(`X-Openit-User`)과 역할 판정 위치(게이트웨이)가 그대로라 영역 구조 규칙(D104)상 변경이 deploy와 admin-console 화면에 머문다.
- 가입 승인을 Keycloak 관리 화면으로 하면 계정 관리 화면을 새로 만들고 시험할 필요가 없다.

## 검토한 대안
- **Authentik**: 기능은 충분하나 Redis 등 구성 요소가 더 많고, 이 프로젝트의 PostgreSQL 하나 원칙에 덜 맞는다.
- **게이트웨이 basic_auth 유지 + 가입 화면 직접 구현**: 비밀번호 저장·재설정·잠금·기록을 직접 만들어야 하고 표준이 아니다.
- **Caddy 플러그인으로 OIDC 직접 처리**: 커스텀 Caddy 빌드가 필요(L03에서 이미 위험으로 판정).
- **admin-console에 승인 화면 구현(Keycloak Admin REST)**: 브라우저에 관리 토큰이 필요하고 같은 기능의 재구현이다.

## 결과
- 얻는 것: 가입 신청·승인·admin·초기 admin·로그인 기록·한 계정 여러 역할.
- 감수하는 것: 컨테이너 둘(Keycloak, oauth2-proxy)이 늘고 Keycloak 기동 시간(수십 초, 측정 전)이 생긴다. Keycloak 버전 관리가 운영 일에 더해진다.
- 시험(완료 조건): IdP 기동 → 가입 신청 → 승인 전 403·승인 대기 안내 → admin이 그룹 부여 → 로그인 → 역할별 허용·거부 → 로그아웃 → 로그인 이벤트 기록. 전체 E2E 사람 경로 전부가 OIDC로 통과.

## 되돌리는 조건
병원이 자체 IdP(AD/LDAP, SAML)를 요구하면 Keycloak의 사용자 연동(federation)이나 IdP 위임으로 바꾸고 게이트웨이 구성은 그대로 둔다.
