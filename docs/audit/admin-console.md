# 전수 점검: admin-console (2026-10-28, 읽기 전용)

점검 기준: `head/docs/AUDIT_CHECKLIST.md`(A~I, 63항목). 읽은 것: 체크리스트, FAULT_POLICY, FAULT_MATRIX(C7 관련), 영역 CLAUDE.md·README·docs/brief·boundary·runbook·STATUS·CR-004, `app/`·`api/`·`serve/`·`scripts/` 소스 전부(mock-server는 시험 지원이라 열지 않음), Dockerfile, package.json·lock 핀, `generated/` 머리말, 시험 일부(hygiene, schemas-generated, helpers 및 grep). 실행한 것: `node scripts/gen-schemas.mjs --check`(결과 "generated 최신", 쓰기 없음), `npm audit --offline`(아래 B9 참고). 시험 통과 여부는 실행하지 않았다(다른 에이전트가 간헐 실패를 조사 중).

## 요약

분모 63항목: OK 23, 문제 18, 해당 없음 13, 확인 못 함 9 (합 63). 문제 18항목은 아래 '문제 목록'의 원인 16건(M 5, L 11)에 걸친다(한 원인이 여러 항목에 걸림).

- **H 문제: 0건.** 승인·활성화·롤백 화면은 실패를 조용히 성공처럼 보이지 않고, 사람 승인을 우회하는 경로가 없다.
- **M 문제 5건(원인 기준):**
  - M1. 릴리스 운영 화면(활성화·롤백)이 실제 release-gate·게이트웨이와 한 번도 맞춰 보지 않았고, 본문이 계약과 다르다(`requested_by_role` 생략, HTTP.md:58, RollbackRequest 필수). 실서버에서 400/404일 수 있다. (D1, H1)
  - M2. 승인자·운영자의 행위자가 화면에 보이지 않는다(승인 화면은 "게이트웨이가 인증한 사용자", 운영 화면은 '활성화한 사람 알 수 없음'). 사람이 어떤 신원으로 기록되는지 확인할 수 없다. (C6)
  - M3. 활성화(activate) 요청에는 현재 포인터 버전/이전 릴리스(CAS)와 요청 ID가 없어, 오래된 화면에서 두 운영자가 동시에 활성화하면 서버가 겹침을 알 수 없다. (A7, D3) 계약 변경 필요.
  - M4. 승인 확인창의 첫 포커스가 '승인 확정'(되돌릴 수 없는 버튼)이다. Enter 키 반복 입력으로 확인 없이 확정될 수 있다. (영역 특유 승인 UI) 자율 수정 가능.
  - M5. 화면 자체 인증 없음: 사람 로그인·HTTPS는 미정(OPEN_GAPS D-A)이며, 정적 서버와 `/config.json`은 인증 없이 열린다. 게이트웨이가 정적 화면 앞에 인증을 거는지는 확인하지 못함. (B1, B8)
- L 문제 11건(L1~L11): 아래 목록 참고.

## 문제 목록 (같은 원인 묶음)

| ID | 심각도 | 제목 | 근거 | 제안 수정 | 구분 |
| --- | --- | --- | --- | --- | --- |
| M1 | M | 릴리스 운영 계약 불일치 가능·미검증 | `api/releases.ts:325-333`가 `{release_id}`만 보냄. `boundary-contracts/HTTP.md:58`은 `{release_id, requested_by_role}`, `schemas/RollbackRequest.schema.json`은 `requested_by_role` 필수. `app/ops-controller.ts:143-146`도 생략. CR-004 §2.2 열림. 게이트웨이 경로는 CR-004 시점 Caddyfile에 없었고 현재 상태는 확인 못 함. 시험은 모의 서버 기준(`tests/ops-conformance.test.ts`가 차이를 고정) | 헤드가 계약을 선택적/무시로 정리하거나 화면이 필드를 보내게 함. 실 release-gate+게이트웨이 E2E를 추가 | 사용자·헤드 결정(계약) + deploy |
| M2 | M | 행위자 표시 없음 | `app/views.ts:89,106`, `app/ops-view.ts:255` | 계약에 현재 사용자 확인 호출(whoami)이나 `activated_by`가 필요(CR-001/004). 그 전까지 완료 화면에 서버가 기록한 승인자 ID를 보이도록 `GateApproval.approver_id`를 표시 | 헤드 결정(계약), 부분 자율 |
| M3 | M | activate에 동시성 보호·멱등키 없음 | `api/releases.ts:325-328`, HTTP.md:58. 롤백은 `from_release_id`와 `request_id` 있음(`ops-controller.ts:143-146`) | activate에 `expected_pointer_version`, `request_id` 요청(CR) | 헤드 결정(계약) |
| M4 | M | 확인창 기본 포커스가 확정 버튼 | `app/views.ts:101-111`: `confirm-yes`가 `confirm-no`보다 앞, `showModal()`이 첫 요소에 포커스(`views.ts:111`) | 취소 버튼에 `autofocus`, 또는 순서 교체. 키 반복 방지 지연 | 자율 수정 가능 |
| M5 | M | 사람 인증·HTTPS 미정, 화면/`/config.json` 무인증 | README 5절 D-A. `serve/static-server.mjs:266-270`, `:262-265`. 게이트웨이 정적 라우트 인증 여부는 deploy를 읽지 못해 확인 못 함 | 사용자 결정 D-A 후 정적 화면도 인증 뒤에 둔다. `/config.json`은 운영에서 항상 `null`임을 시험으로 고정 | 사용자 결정 |
| L1 | L | 응답 대조 없음 | 승인 완료 화면은 서버가 준 `approval`을 그대로 표시(`views.ts:133-139`), 활성화/롤백 영수증도 요청 대상과 일치하는지 비교하지 않음(`ops-controller.ts:141-147`) | 완료 전에 `submission_id`·`decision`·`release_id`가 요청과 같은지 확인하고 다르면 경고 | 자율 |
| L2 | L | 결정 POST가 2xx인데 JSON이 아니면 "요청에 실패했다"로 보임 | `api/http.ts:76-81`, `app/controller.ts:19-20,122` | BAD_RESPONSE는 "기록 여부를 모른다. 같은 결정을 다시 보내도 안전" 안내로 | 자율 |
| L3 | L | 활성화 확인에 되돌리기 안내 없음 | `app/ops-view.ts:198`. 승인 쪽은 "되돌릴 수 없다"(`views.ts:107`) | 활성화 확인에 "이전 릴리스로 롤백하려면 '이전 릴리스로 롤백…'", 롤백 영수증에 다시 되돌리는 방법 | 자율 |
| L4 | L | 본문 읽기 timeout 없음 | `api/http.ts:60,73-75`: 헤더 수신 뒤 `clearTimeout`, `res.json()`은 무제한. 게이트웨이 프록시에도 상한 없음(FAULT_MATRIX C7) | `finally`를 본문 읽기 뒤로 | 자율 |
| L5 | L | 라우트 해시 잘못 인코딩 시 예외 | `app/main.ts:237,239`: `decodeURIComponent` 미보호, 화면이 이전 상태로 남음 | try/catch로 목록으로 | 자율 |
| L6 | L | 포커스 소실·접근성 | `app/main.ts:209-216`·`views.ts:116-118` `replaceChildren`: 분리 기준/정렬 select 변경 시 포커스 잃음. `index.html:7` title이 화면마다 같음. 표에 caption 없음. `.muted{opacity:.75}` 대비 미측정. 운영 확인 패널은 포커스 이동 없음 | 렌더 후 포커스 복원, title 갱신, 대비 측정, 실제 브라우저/스크린리더 확인 | 자율 |
| L7 | L | 시간·시각 | `ops-controller.ts:74,144` 요청 시각을 브라우저 시계로 만듦. 화면의 시각은 ISO 원문(UTC) 그대로 | 서버가 시각을 채우게 계약 확인, 표시는 KST 병기 | 자율/헤드 |
| L8 | L | 문서 불일치·부족 | `docs/brief.md:15` "릴리스 활성화/롤백 UI(후속)", `docs/boundary.md`에 I4/ops 소비 계약·`requested_by_role` 없음, `boundary.md:9` 변경 요청 목록이 CR-001/002뿐. runbook 장애 절이 2줄, 15초 timeout이 영역 문서(README/boundary/runbook/design)에 없음 | 문서 갱신, 활성화/롤백 결과 불명 시 절차를 런북에 | 자율 |
| L9 | L | 공급망·이미지 | `Dockerfile:3,16`: 태그만 고정(`node:24.14.0-alpine3.22`), digest 아님. HEALTHCHECK 없음. SBOM·스캔 없음. CI digest 게시(D24) 미완(README 4절) | digest 고정, CI 연결 | 자율 + deploy |
| L10 | L | 검토자 자유 입력의 개인정보 | `app/cases-view.ts:6` 경고문뿐, 자동 검사 없음. 서버 쪽 검증은 확인 못 함 | ops-feedback가 입력을 재검사하는지 확인, 화면에서 흔한 패턴(주민번호·전화번호) 경고 | 자율(경고)/타 영역 |
| L11 | L | 시험이 이웃 폴더에 의존 | `tests/schemas-generated.test.ts:8` 조건부 skip(사유 있음), `tests/ops-conformance.test.ts:10`·`v2-report-ui.test.ts:93`은 `../../boundary-contracts`를 직접 읽음(없으면 실패) | 환경 문서화(이미 README 명시 일부). XSS 음성 시험(`<script>` 포함 서버 텍스트가 텍스트로 보임) 추가 | 자율 |

## 항목별 판정

### A. 신뢰성
| 항목 | 판정 |
| --- | --- |
| A1 timeout | 문제 L4. 연결·헤더 15초(`api/http.ts:54,60`), 본문은 무제한. 서버(정적)는 외부 호출 없음 |
| A2 재시도 | OK. 자동 재시도 없음(`api/http.ts` 전체). 사람이 다시 누르는 재전송만: 승인은 서버 멱등(HTTP.md:63), 롤백은 같은 `request_id` 유지(`ops-controller.ts:101,107`, 오류 시 pending 유지 `:152-154`). 활성화는 멱등키 없음 -> M3 |
| A3 부분 쓰기 | OK. 브라우저·서버 모두 상태 저장 없음(`docs/boundary.md:3`). 쓰기는 서버 단일 POST |
| A4 우아한 종료 | OK(얕게). `serve/static-server.mjs:285` SIGTERM에서 `server.close`. SIGINT 처리 없음, 강제 종료 상한 없음. 정적 응답이라 영향 작음 |
| A5 재시작 복구 | OK. 무상태 정적 서버. 화면은 새로고침으로 복구. restart 정책은 deploy 몫 |
| A6 무한 증가 | OK. 릴리스 목록 20쪽×500 상한(`api/releases.ts:312`), 승인 목록은 메모리 내(`loadMore`). 로그·캐시 없음. 상한 도달 시 조용히 잘림(문서화 안 됨, L급) |
| A7 동시성 | 문제 M3(활성화). 중복 클릭: 승인 `inflight`(`controller.ts:86-88`), 사례 검토(`cases-controller.ts`), 운영 `phase==="submitting"` 가드(`ops-controller.ts:127`). 롤백은 `from_release_id`로 겹침 검출 가능 |
| A8 healthz/readyz | OK. 둘 다 정적 200(`static-server.mjs:262-265`), 외부 의존이 없어 의미상 동일. 의존(게이트)이 죽어도 200이 맞음(boundary.md:장애 영향) |
| A9 자원 한도 | 확인 못 함. 이미지에 한도 없음, compose는 deploy 몫. 정적 파일 `readFile`을 요청마다(캐시 없음, 크기 작음) |

### B. 보안
| 항목 | 판정 |
| --- | --- |
| B1 인증 | 문제 M5. 앱 자체 인증 없음(설계상 게이트웨이). API는 게이트웨이/토큰이 역할 강제(E2E 5 단언, FAULT_MATRIX:394, 직접 열지 않음). 정적 화면 인증은 확인 못 함 |
| B2 인가 | OK(화면 범위). 역할 판단을 화면이 하지 않고 403을 구분 안내(`controller.ts:17,116`, `ops-controller.ts:39`). 서버·게이트웨이 강제는 이 점검이 보지 못함 |
| B3 비밀 | OK. 토큰·Authorization 코드 없음(grep 결과 없음, `tests/hygiene.test.ts:12-18`), Dockerfile에 비밀 없음. 비밀 파일 방식 해당 없음(README 3절) |
| B4 입력 검증 | OK(L5 제외). ID는 `encodeURIComponent`(`api/client.ts:129,135`), 쿼리는 `URLSearchParams`. 정적 서버 경로 이탈 차단(`static-server.mjs:272-274`, smoke.sh의 `/../../etc/passwd` 404). 크기 상한은 없음(검토자 JSON 입력, 브라우저 내) |
| B5 인젝션 | OK. DOM에 `textContent`/`append(string)`만(`app/views.ts:7-16`의 `h`), innerHTML·eval·document.write 없음(grep, hygiene 시험). 서버·모델 텍스트(노트, 체크 detail, trace JSON, 서버 message)도 텍스트 노드/`pre`. 단 XSS 음성 시험은 없음(L11). SQL·프롬프트 해당 없음 |
| B6 SSRF | 해당 없음. 요청 대상은 같은 출처 `/v1` 고정(`baseUrl:""`, `main.ts`), 사용자 입력 URL 없음 |
| B7 웹 | CSP는 OK: `default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`(`static-server.mjs:257`), 인라인 스타일/스크립트 없음, nosniff, no-referrer, no-store. 클릭재킹 OK(frame-ancestors). CSRF·쿠키·CORS·HSTS는 게이트웨이 몫이라 확인 못 함: 사람 인증이 기본 인증이면 브라우저가 자격을 자동 첨부하므로 서버가 `Content-Type: application/json`을 강제하는지 확인 필요. 서비스 워커 없음. 실제 브라우저에서 CSP 아래 번들 실행은 미확인(STATUS) |
| B8 전송 | 확인 못 함. TLS 종료는 게이트웨이/D-A 미정(M5). 컨테이너는 `0.0.0.0:8080` 평문 바인딩(`static-server.mjs:284`, 호스트 바인딩은 deploy) |
| B9 의존성 | 일부 OK. lock에 모두 integrity 포함, 핵심 devDeps 정확 핀(ajv 8.17.1, esbuild 0.25.5, typescript 5.8.3), `^`는 jsdom·@types/jsdom뿐(시험용). 최종 이미지에 node_modules 없음(`Dockerfile:21-31`). `npm audit --offline`은 "0 vulnerabilities"를 냈으나 오프라인 캐시 기준이라 **신뢰하지 않는다 -> 취약점은 확인 못 함**(외부 전송 금지로 온라인 감사 안 함). 이미지 digest 미고정 -> L9 |
| B10 속도 제한 | 확인 못 함(게이트웨이 몫). 앱에는 로그인·세션 시작 없음 |
| B11 오류 노출 | OK. 서버 `message`는 표시되나(`controller.ts:20`, `ops-controller.ts:40,41,44,45`) 서버가 준 BoundaryError 문구일 뿐 화면이 내부 정보를 더하지 않음. 정적 서버 404는 "not found" |
| B12 토큰 범위 | OK(화면 범위). 브라우저에 토큰 없음. 개발용 `ADMIN_DEV_APPROVER_ID`가 운영에 설정되면 본문에 `approver_id`를 보내지만 서버가 헤더 있으면 무시(HTTP.md:68). 게이트웨이가 클라이언트의 `X-Openit-User`를 지운다는 것은 문서 서술이며 확인 못 함 |

### C. 데이터·개인정보
| 항목 | 판정 |
| --- | --- |
| C1 목록 | OK. 저장 없음(boundary.md:3, 브라우저 저장소·콘솔 없음 grep). 화면에 나오는 것: 제출·보고서(PHI 없음), 비식별 trace와 검토자가 입력하는 reviewed_input/expected(`cases-*`), 메모리에만 |
| C2 최소 수집 | OK. 보내는 값은 결정·사유·릴리스 ID·검토 내용뿐 |
| C3 보존·삭제 | 해당 없음. 이 영역에 저장소가 없다 |
| C4 비식별 | 문제 L10. 비식별은 ops-feedback 몫이고 화면은 마스킹 값을 그대로 보여 줌(`cases-view.ts:75`). 검토자 자유 입력은 경고문만 |
| C5 암호화 | 해당 없음(저장). 전송은 B8 |
| C6 접근 기록·행위자 | 문제 M2. 기록은 서버가 `X-Openit-User`로 함(HTTP.md:68). 화면은 본문에 행위자·역할을 보내지 않음(위조 불가 방향 OK, `ops-controller.ts:1`). 단 개발 모드는 본문 `approver_id`가 먼저(헤더 없을 때) -> 게이트웨이를 우회하면 위조 가능, 운영에서 `ADMIN_DEV_APPROVER_ID` 미설정을 보장하는 장치 없음 |
| C7 백업 | 해당 없음. 상태 없음 |
| C8 DB 계정 | 해당 없음. DB 없음 |
| C9 마이그레이션 | 해당 없음. 생성 검증기 재생성 절차는 runbook에 있음(OK) |
| C10 정합성 | 해당 없음(DB 없음). 시각은 L7 |

### D. 정확성·계약
| 항목 | 판정 |
| --- | --- |
| D1 계약 일치 | 문제 M1. 승인 쪽은 OK: 해시를 계산하지 않고 `X-Openit-Report-Hash`를 형식 검사 후 그대로 반환(`api/client.ts:134-139`), 409는 `details.reason`으로만 구분(`http.ts:31-36`), 모의 서버 출력을 스키마로 검증(`mock-conformance.test.ts`). 생성 검증기는 boundary-contracts 2.0.2 스키마 4개의 sha256과 현재 일치(`--check` 통과, `generated/...cjs:1-2` 머리말). 도구가 만든 파일을 커밋한 상태(CR-003 정책 결정 대기) |
| D2 상태 기계 | OK. 단계 가드(`controller.ts:67,85`, `ops-controller.ts:127`). 릴리스 순서를 "목록이 최신부터"로 가정(`ops-controller.ts:55-67`)하며 계약이 정의하지 않음(CR-004 §2.3). 서버가 최종 검증 |
| D3 멱등 | 문제 M3(활성화). 승인·롤백·검토는 OK(서버 멱등 + 클라이언트 `inflight`) |
| D4 시간 | 문제 L7 |
| D5 인코딩·크기 | 확인 못 함. 긴 한글·이모지·null 문자·큰 보고서 시험을 찾지 못함 |
| D6 값 지어내기 | OK. 화면은 합격/불합격을 판정하지 않음(`views.ts:73`, 임계치 없음), 해시 계산 없음, 모르는 값은 그대로/새 그룹 표시(STATUS 작업 단위 4) |
| D7 문서-코드 | 문제 L8. 시험 개수 등 숫자(README 66개)는 이 점검이 실행해 확인하지 않음 |

### E. 운영성
| 항목 | 판정 |
| --- | --- |
| E1 로그 | 문제 L(경미). 서버 로그는 기동 한 줄뿐(`static-server.mjs:284`), 접근 로그·상관 ID 없음(정적 서버, 게이트웨이 접근 로그가 대신). 브라우저 콘솔 로그 없음(OK) |
| E2 메트릭 | 해당 없음. 정적 서버. 감시는 gateway `/readyz`(FAULT_POLICY 14) |
| E3 설정 | OK. env `PORT`,`STATIC_DIR`, 개발용 승인자. 잘못된 PORT는 listen 예외로 시작 거부. 개발 변수 운영 차단 장치 없음(C6) |
| E4 런북 | 문제 L8. `docs/runbook.md`에 승인/활성화/롤백 결과 불명 시 절차, 잘못 활성화했을 때 롤백 절차가 부족 |
| E5 감시·알림 | 확인 못 함(deploy) |
| E6 용량 | 해당 없음. 측정 없음, 정적 화면 |
| E7 시작 순서 | 해당 없음. 시작 시 의존 없음 |
| E8 timeout 체인 | 문제 L4/L8. 클라이언트 15초와 게이트 프록시 상한 없음은 FAULT_MATRIX C7에 있으나 영역 문서에는 없음. 게이트가 멈추면 15초 뒤 "연결 못 함/적용 여부 모름" 안내가 나오는 것은 OK(`controller.ts:119-121`, `ops-controller.ts:42`) |

### F. 배포·이미지
| 항목 | 판정 |
| --- | --- |
| F1 | OK(이미지). `USER node`(`Dockerfile:25`), 쓰기 없는 서버라 읽기 전용 rootfs 가능성 높음(시험 안 함), capabilities·docker.sock 설정 없음. 포트 호스트 바인딩은 deploy 몫 -> 확인 못 함 |
| F2 | 문제 L9 |
| F3 | 확인 못 함(compose는 deploy). 이미지에 HEALTHCHECK 없음 |
| F4 | 확인 못 함(릴리스 되돌리기·업그레이드 순서는 deploy). 앱의 ops 화면이 모델 릴리스 롤백을 담당(I와 M1) |
| F5 | 해당 없음. 비밀 없음 |
| F6 | 문제 L9. CI 빌드·digest 게시 미완(README 4절) |

### G. 성능·용량
| 항목 | 판정 |
| --- | --- |
| G1 | 해당 없음. 측정 대상 아님(정적 화면, 소수 운영자) |
| G2 | OK. 쿼리 없음. 릴리스 목록을 매번 최대 20쪽 순차 조회(`api/releases.ts:312`), 동작 뒤 전체 재조회(`ops-controller.ts:162`) |
| G3 | 확인 못 함. 큰 보고서의 매 변경 전체 재그리기(`views.ts:116-118`) 부하는 측정하지 않음 |

### H. 시험 품질
| 항목 | 판정 |
| --- | --- |
| H1 | 문제 M1. 승인·검토·운영 흐름이 실제 클라이언트 코드 + 모의 서버(HTTP 실사용, `tests/helpers.ts:11`)로 시험되고 모의 출력은 계약 스키마로 검증됨. 그러나 상대는 모의이고 승인 경로의 gateway 경유 E2E는 있다(FAULT_MATRIX:394) 운영 화면 E2E는 없다. 실제 브라우저·CSP 아래 번들 실행 시험 없음 |
| H2 | OK(얕게). 고정 포트 없음(`listen(0,...)`, `helpers.ts:11`), 고정 대기를 `waitFor`로 교체한 커밋(`214a456`), 시험에 `setTimeout`/`sleep` grep 결과 없음. 간헐 실패 조사는 다른 에이전트가 진행 중이라 이 점검은 판단하지 않음 |
| H3 | OK. skip은 `schemas-generated.test.ts:8` 한 곳, 사유 문자열 있음. 대체 수단은 `gen-schemas.mjs --check`이나 같은 이웃 폴더 필요 -> L11 |
| H4 | 일부. 부정 시험 있음: 반려 사유 없음, STALE_REPORT, 403/409/412, 네트워크(STATUS 작업 단위 5, `flow.test.ts`). 없음: 서버 텍스트 속 `<script>`/HTML 렌더, 확인창 키 입력 -> L11, M4 |
| H5 | 문제 L11. 일부 시험이 `../../boundary-contracts`를 직접 읽음. 그 밖의 시계·디스크 의존은 찾지 못함 |

### I. 도메인·안전
| 항목 | 판정 |
| --- | --- |
| I1 | OK. 사람 판단 우회 없음(아래 영역 특유). 화면에 임의 임계치·자동 판정 없음(`views.ts:73`). 롤백 기준·자동 롤백은 이 화면에 없음(FAULT_POLICY 사용자 결정 항목은 화면과 무관) |
| I2 | 해당 없음. 환자용 문구 없음(운영 화면) |
| I3 | OK(운영자 관점). 실패 시 `role=alert` 오류, 조용히 비거나 성공처럼 보이는 경로를 찾지 못함: 목록 실패 `controller.ts:29-31`, 보고서 `:52-54`, 결정 `:101-122`, 운영 `ops-controller.ts:93-96,151-155`, 롤백 거절 상태는 error 스타일(`ops-view.ts:229-230`). 적용 후 재조회 실패도 알림(`ops-controller.ts:164-165`) |

## 영역 특유 점검

| 점검 | 판정 |
| --- | --- |
| 자동 승인·기본 선택값 | OK. 기본 선택 없음. 승인/반려 버튼은 보고서 단계에서 누르고 확인창을 거쳐야 전송(`controller.ts:65-76,83-90`). 사유 없는 반려는 막음(`:69-71`). 페이지 로드·URL·쿼리로 결정이 실행되는 경로 없음. 단 M4(확인창 첫 포커스) |
| report_hash 일치 | OK. 해시는 보고서를 받은 응답 헤더에서 같은 요청으로 얻고(`client.ts:135-139`), `no-store`로 캐시 방지(`http.ts:68`), 결정 시점에 `loaded.reportHash`를 `pending`에 고정(`controller.ts:74`)해 확인창·전송이 같은 값을 쓴다(시험 `flow.test.ts:45-59`). 확인창은 해시 앞 19자 표시(`views.ts:104`). 서버가 대조해 409 STALE_REPORT(HTTP.md:63-66), 그 경우 자동 재전송 없이 다시 읽게 함(`controller.ts:109-112`). 한계: 화면이 해시를 계산하지 않으므로 본문과 헤더가 어긋나면 클라이언트는 알 수 없음(설계 결정 D69) |
| 위험 동작 확인 | OK. 활성화·롤백: 대상 릴리스 ID를 직접 입력해야 버튼 활성(`ops-controller.ts:120-123,129`, `ops-view.ts:193-196`), 롤백은 사유·근거 필수. 되돌리기 안내: 승인은 "되돌릴 수 없다" 명시, 활성화·롤백 확인에는 안내 부족 -> L3 |
| 오류 시 화면 | OK (I3 참고) |
| XSS | OK (B5). 서버 텍스트는 모두 텍스트 노드 |
| CSP | OK (B7) |
| 행위자 표시 | 문제 M2 |
| 접근성 | 문제 L6. 좋은 점: `lang="ko"`, `main`/`nav aria-label`, `th scope`, `label for`, `dialog`+`aria-labelledby`+`showModal`, 오류 `role=alert`, 색이 아닌 텍스트('▲ 나빠짐'), `:focus-visible` 스타일. 실제 브라우저·스크린리더 확인 안 함(STATUS) |

## 이 점검이 읽지 못한/얕게 본 곳

- 읽지 않음: `deploy/`(Caddyfile, 게이트웨이 인증·헤더·정적 라우트·ops 라우트의 현재 상태), release-gate·ops-feedback 구현(읽기 금지), `docs/design.md` 본문, `mock-server/` 소스, 시험 본문 대부분(grep과 hygiene·schemas-generated·helpers만).
- 실행하지 않음: `npm test`, `npm run typecheck`, 이미지 빌드·스모크, 실제 브라우저. 따라서 "66개 통과" 같은 영역 문서의 수치는 확인하지 않았다.
- `npm audit`는 오프라인 모드뿐(외부 전송 금지). 실제 취약점 유무는 확인 못 함.
- 게이트웨이가 클라이언트 `X-Openit-User`를 지우는지, 정적 화면에 인증을 거는지, CSRF/CORS/HSTS는 이 영역 밖이라 확인하지 못함.
- 번들(`dist/app.js`)은 소스에서 빌드한 산출물이라 따로 점검하지 않았고, 소스 최신성과 같은지 확인하지 않음.
- 접근성과 레이아웃은 코드 읽기뿐이다.
