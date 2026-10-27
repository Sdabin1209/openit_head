# kiosk-frontend 전수 점검 (읽기 전용 감사)

점검일 2026-10-28. 기준: `head/docs/AUDIT_CHECKLIST.md` A~I 전 항목. 대상 커밋: kiosk-frontend 212f769(작업 트리 변경 없음). 코드·설정·문서는 수정하지 않았다. 이 문서가 유일한 쓰기다.

## 요약

항목 수: 63 (A9, B12, C10, D7, E8, F6, G3, H5, I3).

| 판정 | 개수 (분모 63) |
|---|---|
| OK | 19 |
| 문제 | 24 (항목 기준 H 2 / M 9 / L 13, 혼합 표기 항목은 앞쪽 심각도로 셈. 같은 원인은 아래 P번호로 묶음) |
| 해당 없음 | 12 |
| 확인 못 함 | 8 |

(OK 19에는 'OK / L', 'OK / 확인 못 함'처럼 일부 경계만 단서가 붙은 4항목을 포함. 문제 24 = H 2 + M 9 + L 13. 해당 없음 12, 확인 못 함 8. 합계 63.)

### H 문제 (2건, 원인 기준)
- **P1. 두 번째 환자 세션이 첫 환자의 `subject_ref`로 시작될 수 있다.** `apps/kiosk/main.ts:7-8`이 시작 값(`held`)을 페이지 로드 때 한 번만 읽고, `flow.reset()`/`start()`가 이를 비우지 않는다(`apps/kiosk/flow.ts:62-66`, `121-125`). 새로고침 없이 `ENDED -> IDLE -> 시작하기`를 하면 이전 환자의 참조가 다시 쓰인다. 이를 시험하는 것은 찾지 못했다. 환자 건강정보가 다른 환자 기록에 붙는 위험(B2, C1, I1).
- **P2. 환자 음성이 브라우저 STT 제공자(Chrome이면 Google 서버)로 나간다.** `apps/kiosk/stt.ts:23-51`이 Web Speech API를 쓰고, `docs/runbook.md`는 "인터넷 연결과 구글 음성 서비스에 의존"한다고 적었다. 그런데 `README.md`·`docs/design.md:1절`·`brief.md:4절`은 "외부 서비스에 남기지 않는다"고만 쓴다. TTS(`main.ts:21`)도 원격 음성일 수 있다. 사용자 결정 필요(온디바이스/자체 STT, 동의·고지, 또는 위험 수용).

### M 문제 (원인 기준 묶음)
- P3. 방치 시 화면 잔존·세션 만료 없음: LISTENING/REPEAT_PROMPT/WAITING_STAFF/CALL_STAFF에 유휴 타임아웃이 없고, 숨겨진 수동 입력창 값도 지우지 않는다(`main.ts:41-43,50,54,67`, `flow.ts:105-125`).
- P4. 마이크 거부·STT 오류 시 대체 경로 없음 + 다시 말하기 무한 반복 + REPEAT_PROMPT에 직원 호출/그만하기 버튼 없음(`main.ts:25,28,41,52-54`, `stt.ts:47-48`). runbook 체크리스트는 "텍스트 입력으로 이어진다"고 쓰지만 코드는 `stt.available()`이 true이면 입력창을 숨긴다.
- P5. WAITING_STAFF 무기한 폴링, 서버 장애·연결 끊김이 환자에게 안 보임(`flow.ts:159-176`).
- P6. 직원 콘솔의 인증·권한 분리·행위자 기록이 전부 게이트웨이 전제(CR-001)이고, 이 영역에서는 확인할 수 없다. 키오스크와 직원 콘솔이 같은 출처·같은 정적 서버(`server/static.mjs`)다.
- P7. 기기 토큰 보관: `#device=` 조각은 새로고침 시 사라지고(`runbook.md`), 안전한 경로로 권장된 `/config.json`은 이 이미지가 내지 않아(`test/static.test.ts:39` 404) 게이트웨이/기기 배포 몫이 됐다. 토큰 수명·회전·폐기 절차는 이 영역 문서에 없다.
- P8. 이미지 공급망: `node:24-alpine` 태그만 고정(digest 없음), SBOM·취약점 스캔 없음(`Dockerfile:2,13`).
- P9. 임상 판단 값이 임의로 박힘: `MIN_CONFIDENCE = 0.4`(`stt.ts:13`), 다시 말하기 상한 없음, ENDED 8초 후 초기화(`main.ts:67`)가 사용자 결정 표시 없이 코드에 있다(재시도 예산 20초만 표시됨).
- P10. 실제 gateway/survey를 거친 키오스크 시험이 없다(모의 서버 + 헤드리스 Chromium만). FAULT_MATRIX A1·A3도 같은 지적.
- P11. 장애 대응 런북 부재: `docs/runbook.md`는 시험·기기 토큰 증상 위주이고 정적 서버 장애, 키오스크 화면별 대응 절차가 없다(E4).
- P12. 키오스크 이상을 운영자가 알 길이 없다(E2/E5): RETRY_EXHAUSTED·AUTH로 직원 호출 화면에 간 사실이 서버 쪽에 신호로 남지 않는다(환자 정보를 보낼 수 없으므로 설계 선택. 사용자/헤드 결정 필요).

### L 문제
dev 의존 취약점 3건(P13), 문서 낡음(P14), 헤더 보강(P15), 종료 실패 은폐(P16), 푸시 해지 UI 없음·알림 본문(P17), 입력 길이 제한 없음(P18), 시간 표기 UTC·문자열 정렬(P19), 응답 null일 때 빈 화면(P20), 접근성 잔여(P21), 로그 무회전(P22), 정적 서버 PORT 검증(P23), 직원 목록에 해결자 미표시(P24).

## 확인한 근거 (실행·검색)
- `npm test`(읽기 전용 실행): 117건 중 통과 109, 실패 0, 건너뜀 8. 건너뜀은 이 PC의 `node_modules`에 `jsdom`, `@types/jsdom`이 없어서다(`npm ls`가 UNMET). 대체는 `npm run test:dom`(Docker)이며 이 점검은 돌리지 않았다.
- `npm audit`(레지스트리에 패키지 목록을 조회하는 읽기 명령): 3건. playwright <1.55.1 high(GHSA-7mvr-c777-76hp, 브라우저 내려받기 때 인증서 미검증), ajv 8.17.1 moderate(`$data` 옵션 ReDoS), fast-uri moderate(전이 의존). 전부 devDependency이며 `Dockerfile`의 최종 단계는 `dist`와 `server/static.mjs`만 복사하므로 런타임 이미지에는 들어가지 않는다. 빌드 산출물 `dist/kiosk.js` 12 KB, `staff.js` 14 KB는 런타임 의존 없이 번들됐다.
- 위험 패턴 grep(`api apps server mock-server scripts`): `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `eval`, `new Function`, `document.write`, `localStorage`, `sessionStorage`, `indexedDB`, `document.cookie`, `caches.` 모두 0건. `console.*`는 서버 시작/요청 로그(`server/static.mjs:38,42`, 경로만, 쿼리 제외)와 스크립트·모의 서버뿐이며 환자 발화·토큰은 없다. `?token`, `location.search/href` 사용 0건. 모든 서버 문구는 `textContent`로 넣는다(`apps/staff/main.ts:44`, `record.ts:38-43`, `main.ts:43`).

## 항목별 판정

### A. 신뢰성

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| A1 timeout | OK | 클라이언트 요청마다 10초 AbortController(`api/client.ts:166-171`), 총 재시도 예산 20초(`retry.ts:23`). 마이크 STT는 브라우저가 끝낸다. 정적 서버는 Node 기본 요청 timeout을 쓴다(명시 설정 없음, 확인한 것은 코드뿐). SSE는 하트비트 무음 감시(`api/staff.ts:69-73`). |
| A2 재시도 | OK | 재시도 대상은 429/502/503/504/네트워크/무응답과 409 TURN_IN_PROGRESS만, 같은 `turn_id`, 지수 백오프 0.5초 x2 상한 5초 + 지터 50~100%, 예산 20초(`retry.ts:19-55`, `client.ts:121-136`). 시험 `test/retry.test.ts` 22건. 확인 못 한 한 가지: 세션 시작 POST를 같은 `session_id`로 재전송해도 서버가 멱등인지는 PUBLIC_API.md에서 찾지 못했다(턴만 명시) -> 헤드/survey에 확인 요청 필요(L). |
| A3 부분 쓰기 | 해당 없음 | 이 영역은 저장소가 없다(`docs/boundary.md`). 단 종료 요청 실패를 삼키고 "수고하셨습니다"를 보이는 점은 P16. |
| A4 우아한 종료 | OK | `server/static.mjs:43` SIGTERM에서 `server.close`. 정적 파일뿐이라 진행 중 요청 마무리가 충분하다. SIGINT 미처리는 컨테이너에서 무해. |
| A5 복구 | 문제 L | 정적 서버는 무상태라 재시작 후 정상. 브라우저는 새로고침하면 세션 상태(메모리)와 `#device` 조각 토큰이 사라진다(`runbook.md` 기기 토큰 절) -> 조각 방식 기기는 "설정이 필요합니다"로 간다. 제안: 기기는 `/config.json` 방식만 쓰도록 배포 문서에 못박기(자율: 문서, 결정: 토큰 배포 방식은 deploy와). |
| A6 무한 증가 | OK | 요청 큐는 완료 시 삭제(`client.ts:97-104`), 알림 목록 읽기는 20쪽 상한(`sync.ts:41`), 기록 보기는 닫으면 DOM 비움(`record.ts:164-168`). 로그는 stdout만(회전은 Docker 몫, L P22: `/healthz` 30초 주기 요청도 매번 한 줄). |
| A7 동시성 | OK | 세션별 직렬 큐(`client.ts:95-105`), 개입 결정은 `alert:결정` 키 중복 방지와 같은 `turn_id` 재사용(`decide.ts:18-34`), 키오스크 상태 가드(`flow.ts:56,81-82`)와 폴링 세대 번호(`flow.ts:52,158-160`). 시험 있음. 이중 처리 경로는 찾지 못했다. |
| A8 /healthz /readyz | OK | `/healthz` 항상 200, `/readyz`는 `index.html` 존재 여부(`static.mjs:21-22`). 의존이 없으므로 의미가 맞다. 스모크가 확인(`scripts/smoke.sh`, 이 점검에서는 실행 안 함). |
| A9 자원 한도 | 확인 못 함 | 이미지에 메모리·파일 핸들 한도 설정은 없고 deploy compose 몫. 파일을 요청마다 `readFile`로 통째로 읽지만 총 26 KB 수준이라 위험은 낮다. |

### B. 보안

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| B1 인증 | 문제 M (P6) | 이 영역은 인증을 하지 않는다. `/staff/`와 `/v1/staff/**`, 개입 호출은 게이트웨이가 사람 인증과 토큰을 붙인다는 CR-001 전제에 의존한다. 정적 서버는 `/staff/`를 인증 없이 낸다(파일에 비밀은 없음). 실제 게이트웨이는 이 영역에서 확인하지 못했다. 제안: deploy 쪽 검증을 FAULT_MATRIX/E2E에서 확인(키오스크 단말에서 `/staff/**`가 거부되는지). 사용자 결정: 직원 로그인 방식(D-A). |
| B2 인가 | 문제 H (P1) / M (P6) | 수평 권한: P1(이전 환자 참조 재사용) `main.ts:7-8`, `flow.ts:62-66`. 제안: `start()`마다 시작 값을 새로 받거나(조각은 일회용으로 소비 후 null), `reset()`/`ENDED`에서 `held.subjectRef = null`로 비우고 시험 추가. 자율 수정 가능(단 접수 연동 방식이 "기기당 고정 참조"인지 "환자마다 새 URL"인지 결정이 필요한지는 헤드 확인). 역할 분리(키오스크 vs 직원)는 토큰 헤더를 `/sessions*`에만 붙이는 것으로 클라이언트 쪽은 OK(`client.ts:158-159`, `test/d85.test.ts`). 서버 쪽 강제는 확인 못 함. |
| B3 비밀 | OK | 이미지·리포·소스에 비밀 없음. VAPID는 공개키만. 기기 토큰은 메모리(`main.ts:7`), 조각은 읽자마자 `replaceState`로 지움(`device.ts:39`), 헤더로만 전송(`client.ts:158`), 쿼리 미사용. `test/static.test.ts:19`가 산출물에 토큰·외부 URL 없음을 확인. README가 D84 `_FILE` 규칙을 "해당 없음"으로 판단한 것은 이 영역에 서버 비밀이 없으므로 타당. 회전 절차는 P7. |
| B4 입력 검증 | OK / L | `session_id` 정규식(`client.ts:86`), `subject_ref`·토큰 형식 검사(`device.ts:6-7`), 응답 본문 모양 검사(`validate.ts`), 알림 커서 `encodeURIComponent`(`staff.ts:16`), 정적 서버 경로 탈출 차단과 시험(`static.mjs:24-27`, `static.test.ts:29`). 경계: 수동 입력창에 `maxlength` 없음(`apps/kiosk/index.html:15`) -> P18 L (서버 상한 8MiB는 서버 몫). 자율 수정 가능. |
| B5 인젝션 | 해당 없음 / OK | SQL·명령·템플릿·프롬프트 인젝션은 서버 몫. 클라이언트 측 DOM 인젝션은 위 grep대로 없음. 로그 인젝션: 정적 서버 로그는 `JSON.stringify`로 직렬화(`static.mjs:38`). |
| B6 SSRF | 해당 없음 | 브라우저가 같은 출처 `/v1`과 `/config.json`만 부른다(`main.ts:9`, `device.ts:44`). 임의 URL 입력 경로 없음. |
| B7 웹 | 문제 L (P15) | XSS: OK(`textContent`만, CSP `script-src 'self'; style-src 'self'`로 인라인 스크립트·스타일 없음). CSP·`nosniff`·`Referrer-Policy: no-referrer`·`frame-ancestors 'none'` 정적 서버가 모든 응답에 붙임(`static.mjs:10,17`). 부족: `Permissions-Policy`(마이크는 self만 등), `form-action`/`object-src`는 `default-src`로 일부 덮임, HSTS는 gateway 몫(확인 못 함). CSRF/CORS/쿠키: 이 영역은 쿠키를 설정하지 않고 같은 출처 JSON POST만 한다. 직원 개입 POST의 CSRF 방어(쿠키 인증을 쓸 경우)는 게이트웨이 설계 몫이라 확인 못 함. 서비스 워커: 직원 콘솔 전용 `/staff/sw.js`, 범위 `/staff/`(`push.ts:19`), `fetch` 핸들러·캐시 없음(`sw.ts` 12줄 전체), 키오스크는 서비스 워커 없음. OK. 이 CSP가 gateway 뒤에서도 유지되는지는 E2E 5a가 본다고 FAULT_MATRIX가 적음(미확인). |
| B8 전송 | 확인 못 함 | HTTPS 종단은 deploy(CR-001 4항). 마이크 STT·서비스 워커·푸시가 보안 출처를 요구하는데 실제 HTTPS 배포에서 확인한 적이 없다(`runbook.md` 체크리스트 미체크). gateway -> 정적 서버 구간은 내부 평문이다. |
| B9 의존성 | 문제 L / M | 런타임 의존 0(번들), devDependency 8개 모두 정확 버전 핀(`@types/node`만 `^24.19.2`)과 `package-lock.json`, `npm ci --ignore-scripts`(`Dockerfile:5`). npm audit 3건(P13): playwright high는 브라우저 다운로드 TLS 검증(빌드/시험 시점, 런타임 아님), ajv/fast-uri는 시험·스키마 대조 도구 한정. 제안(자율): playwright 1.55.1 이상으로 올리고 `test-e2e/Dockerfile`의 베이스 태그도 함께, ajv/fast-uri는 `npm audit fix`. 공급망: 베이스 이미지 digest 미고정, SBOM/스캔 없음(P8 M, F2와 같은 원인). |
| B10 속도 제한 | 해당 없음 | 서버·게이트웨이 몫. 클라이언트는 재시도에 지터와 예산이 있어 폭주하지 않는다(`retry.ts`). 세션 시작 남발 방어는 이 영역에서 확인 못 함. |
| B11 오류 노출 | OK | 키오스크는 사유를 일반 문구로만 보인다(`main.ts:59-65`), 기록 보기 오류 문구에 내용 없음(`record.ts:9-16`), 정적 서버 오류는 짧은 고정 문구(`static.mjs:27,31`). 푸시 실패 메시지는 브라우저 오류 문자열을 보이지만 환자 정보 아님(`staff/main.ts:97`). |
| B12 토큰 수명·범위 | 확인 못 함 | 기기 토큰의 발급·만료·폐기는 서버/deploy 영역이고 이 영역 문서에 없다(P7). 클라이언트 쪽 범위 제한(`/sessions*`에만 전송)은 확인. |

### C. 데이터·개인정보

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| C1 목록 | 문제 H (P2) | 이 영역이 다루는 값과 위치(코드로 확인): (a) 환자 발화 텍스트: STT 결과 -> `flow.hear` 메모리 -> `POST /turns`(`flow.ts:87-94`), 성공 후 `pendingUtterance` 삭제(`flow.ts:96`). (b) 환자 음성 원본: 브라우저 STT로 제공자에게 전송(P2). (c) 서버 응답 문장·`resume_text`: DOM과 메모리. (d) `subject_ref`: 조각/`config.json` -> 메모리 `held` -> 세션 시작 본문, 직원 기록 화면에 표시(`record.ts:74`). (e) 기기 토큰: 메모리. (f) 직원 콘솔: 알림 목록(세션 ID, 종류, 시각), 기록 보기 대화 전문·값(닫으면 DOM 비움). (g) 푸시 구독(endpoint, keys): `sub.toJSON()`을 서버로 보내고 로컬 보관 안 함(`push.ts:23`). (h) 브라우저 저장소·쿠키·서비스 워커 캐시: 사용 0(grep). (i) TTS: 서버 문구를 `speechSynthesis`로 읽음(`main.ts:21`, 원격 음성 여부는 단말 의존, 확인 못 함). 이 목록이 문서에 한 곳으로 정리돼 있지는 않다. 제안: 이 표를 `docs/design.md`에 추가(자율). P2는 사용자 결정. |
| C2 최소 수집 | OK | 이름·환자 번호를 요구하지 않는다. `subject_ref`만 보낸다(D85). 단 `brief.md:6절`("환자 개인정보를 보내지 않는다")과 D85의 참조 값 전송이 문서상 어긋남 -> P14. |
| C3 보존·삭제 | 문제 M (P3) | 서버 저장은 없다. 브라우저 메모리 보존: ENDED는 8초 뒤 초기화(`main.ts:67`)하지만 LISTENING/REPEAT_PROMPT/WAITING_STAFF/CALL_STAFF는 사람이 떠나도 무기한 남는다(응답 문장이 DOM에 있음). 숨겨진 수동 입력창의 미전송 텍스트는 어떤 상태 전이에서도 지워지지 않는다(`main.ts:50,54`에서 전송 성공 뒤에만 비움) -> 다음 사용자가 보게 될 수 있다. 제안: 상태별 유휴 타임아웃(안전한 값은 사용자/임상 결정)과 `reset()` 때 `input.value=""`, `text.textContent=""`. 입력창 비우기는 자율, 타임아웃 값은 사용자 결정. |
| C4 비식별 | OK | 로그에 발화·토큰 없음(grep, `test/d85.test.ts` "콘솔·로그 누출 없음"). 스크린샷 `e2e-artifacts/`는 가짜 문장만, gitignore(`runbook.md`). |
| C5 암호화 | 확인 못 함 | 저장은 없음. 전송 TLS는 gateway(B8). |
| C6 접근 기록 | 문제 M/L (P6, P24) | 직원 콘솔 쪽 열람·결정 기록은 서버/게이트웨이가 `X-Openit-User`로 남기는 구조이고 본문 값은 신뢰하지 않는다(`PUBLIC_API.md:93`, `STATUS.md` D85). 이 영역이 보내는 개입 본문에는 행위자가 없어 위조 표면이 없는 점은 OK. 문제: 알림 목록에 누가 해결했는지 표시가 없다(`staff/main.ts:44`는 상태/결정만, 해결 직원은 기록 보기 표에만 `record.ts:109`) -> P24 L. 기록 열람(GET) 자체의 접근 기록은 서버 몫이라 확인 못 함. |
| C7 백업·복원 | 해당 없음 | 저장소 없음. |
| C8 DB 계정 | 해당 없음 | DB 없음. |
| C9 마이그레이션 | 해당 없음 | DB·스키마 없음. |
| C10 정합성 | 문제 L / 확인 못 함 | 시각: 직원 목록 정렬이 ISO 문자열 비교(`staff/main.ts:69`)라 UTC `Z` 고정이면 맞고 오프셋이 섞이면 틀림, 화면에는 원문 UTC 문자열을 그대로 보임(`main.ts:44`, `record.ts:87`) -> P19 L. 한글 유니코드 정규화는 클라이언트에서 하지 않음(서버 몫, 확인 못 함). |

### D. 정확성·계약

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| D1 계약 일치 | OK(모의 서버 기준) / 확인 못 함(실서버) | `scripts/check-schema.mjs`가 열거값·계약 버전 v2.0.2·Dockerfile ARG·모의 서버 표기·`StaffSessionView`를 대조(`STATUS.md`, `boundary.md`). 실제 survey-service/gateway와는 붙여 본 적이 없다(README "확인 못 한 것"). 이 점검은 `check-schema`를 재실행하지 않았다. |
| D2 상태 기계 | OK | 불가능한 전이는 상태 가드로 무시(`flow.ts:56,81-82,106`), 위험 정지 중 발화 거부, 404/401/403/409 분기(`flow.ts:179-189`). 시험 `test/flow.test.ts` 11건. |
| D3 멱등 | OK | 같은 발화 재시도는 같은 `turn_id`(`flow.ts:89`), 개입 결정은 알림 단위 `turn_id` 유지(`decide.ts`). 세션 시작의 서버 멱등은 A2 참조(확인 못 함). |
| D4 시간 | 문제 L (P19) | 클라이언트 시계는 타임아웃·백오프에만 쓰고 만료 판단에 쓰지 않는다. 표기 문제는 C10. |
| D5 인코딩·크기 | 문제 L (P18) | 입력 길이·null 문자 클라이언트 제한 없음. 긴 한글·이모지는 JSON으로 그대로 전달(확인은 코드 읽기뿐). |
| D6 값 지어내기 | OK | 클라이언트는 서버가 준 `response_text`만 보이고, 형식이 틀리면 재시도 후 직원 호출(`validate.ts`, 원칙 10). 단 `response_text`가 null인 정상 응답이면 빈 문장 화면(P20 L, `main.ts:43`). |
| D7 문서-코드 일치 | 문제 L (P14) | 낡은 곳: `brief.md:4절`의 "3회 실패하면 직원 호출"(코드는 예산 20초), `retry.ts:11` 주석의 "서버 턴 마감(8초)"(정책 6초), `CR-001` 7항의 `VAPID_PUBLIC_KEY`/`/config.json` 설명(코드는 둘 다 없음), `design.md:37`(FAULT_MATRIX도 낡음으로 지적), `brief.md:6절`의 "개인정보를 보내지 않는다"와 D85 참조값, `README`/`design.md` "외부 서비스에 남기지 않는다"와 STT 현실(P2). 자율 수정 가능(문서). |

### E. 운영성

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| E1 로그 | OK / L | 정적 서버: 한 줄 JSON(시각, 메서드, 쿼리 제외 경로, 상태), 비밀·PHI 없음(`static.mjs:38`). 상관 ID·수준은 없다(정적 서버라 영향 작음). 브라우저 쪽 로그는 의도적으로 없음. |
| E2 메트릭 | 문제 L (P12) | 지표·경보 없음. 키오스크의 직원 호출 화면 진입 횟수 등 현장 이상 신호를 보낼 경로가 없다. 환자 정보 없이 사유 코드만 보내는 방안이 있을 수 있으나 계약 변경이므로 헤드/사용자 결정. |
| E3 설정 | 문제 L (P23) | 설정은 `PORT`, `STATIC_DIR` 환경 변수. `PORT`가 숫자가 아니면 `Number()`가 NaN이 되어 `listen`이 던지므로 시작 거부는 되지만 메시지가 불친절(확인은 코드 읽기뿐). `STATIC_DIR`이 없으면 `/readyz` 503. 기본값 안전(`0.0.0.0` 바인딩은 컨테이너 안이라 정상, 호스트 노출은 deploy). |
| E4 런북 | 문제 M (P11) | `docs/runbook.md`: 시험 명령, 브라우저 시험 전제, 사람 확인 체크리스트, 기기 토큰 화면 증상. 부족: 정적 서버가 죽었을 때/게이트웨이 503이 계속될 때/직원 콘솔 연결 끊김 때 운영자 조치 절차. 자율 수정 가능(문서). |
| E5 감시·알림 | 해당 없음 | 감시는 deploy의 몫(FAULT_POLICY 14). 이 영역의 `/healthz`·`/readyz`가 감시 대상으로 제공됨. 키오스크 쪽 신호는 P12. |
| E6 용량 | 확인 못 함 | 측정 없음. 정적 파일 26 KB와 SSE 연결 수 정도로 용량 위험은 낮아 보이나 근거는 측정이 아니라 추정이다. |
| E7 시작 순서 | 해당 없음 | 의존이 없다. gateway가 이 서비스에 의존(FAULT_MATRIX A3). |
| E8 시간 불변식 | 문제 L (P14) | 키오스크 10초 > gateway 9.5초 > 서버 6초 중 키오스크 값은 `client.ts:44`(10초)와 일치. `retry.ts:11` 주석이 서버 마감을 8초로 적어 정책(6초)과 다름. 세 값을 한 곳에서 맞춰 보는 시험은 없다(FAULT_MATRIX도 지적). |

### F. 배포·이미지

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| F1 권한·포트 | OK / 확인 못 함 | `USER node`(`Dockerfile:21`), 스모크가 uid≠0 확인(`smoke.sh`). 포트 노출은 `EXPOSE 8080`뿐이고 호스트 바인딩은 deploy. 읽기 전용 루트 파일시스템으로 돌려 본 적은 없다(정적 서버는 쓰기 없음으로 보이나 확인 못 함). capabilities/privileged/docker.sock 사용 없음(이 영역에 compose가 없다). |
| F2 핀·재현·스캔 | 문제 M (P8) | `FROM node:24-alpine` 태그만(digest 없음, `Dockerfile:2,13`), `npm ci --ignore-scripts`로 의존은 잠금 파일 고정. SBOM·이미지 취약점 스캔 없음. 제안: digest 고정과 스캔을 deploy CI(D24)와 맞춰 도입(자율 가능하나 레지스트리 접근 필요, 설치 금지 제약으로 이 점검은 하지 않음). |
| F3 compose | 해당 없음 | 이 리포지토리에 compose 없음(deploy 소유). |
| F4 되돌리기·정렬 | 확인 못 함 | 이미지 라벨에 리비전·계약 버전이 있어 추적은 가능(`Dockerfile:9-14`). 업그레이드 순서는 정적 이미지라 서버와 독립이나, 응답 열거값이 늘면 이 영역이 직원 호출로 거부할 수 있어(`design.md` 보수적 동작) 서버를 먼저 올리면 안 된다는 점이 문서에 없다. |
| F5 비밀 파일 권한 | 해당 없음 | 이 영역은 비밀을 이미지/compose에 두지 않는다(기기 토큰은 런타임 외부 주입). |
| F6 레지스트리·CI | 확인 못 함 | CI/레지스트리는 이 리포지토리에 없고 deploy 협의(`STATUS.md`). |

### G. 성능·용량

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| G1 측정 | 확인 못 함 | 처리량·지연 측정 문서 없음. 번들 크기(12+14 KB)는 확인. 키오스크 지연 UX는 모의 서버 `delay` 시나리오로만 시험. |
| G2 쿼리·풀 | 해당 없음 | DB 없음. |
| G3 큰 입력 | 문제 L | 응답 크기 상한 없이 `res.json()`/`JSON.parse`(`client.ts:176-182`), 기록 보기는 모든 턴을 DOM에 만든다(`record.ts:84-95`). 직원 PC에서 매우 긴 세션이면 느려질 수 있으나 측정 안 함. |

### H. 시험 품질

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| H1 핵심 경로 | 문제 M (P10) | 환자 턴·직원 개입·푸시 핸들러는 모의 서버 + 실제 헤드리스 Chromium(합성 PushEvent)으로 시험(`test-e2e/browser.e2e.test.ts`). 실제 gateway·survey·실제 마이크·실제 푸시 서비스는 거치지 않았다(`runbook.md`, README). 모의 서버가 실제 서버 동작을 가릴 수 있다. |
| H2 간헐 실패 | OK | 실제 타이머 의존을 가짜 시계·조건 대기로 교체(커밋 8688bdf). 모의 서버는 빈 포트(`mock-server/main.ts`), e2e는 컨테이너 안 빈 포트. 이 점검에서 `npm test` 1회 통과(재현 반복은 안 함). |
| H3 건너뜀 | 문제 L | 8건이 이 PC에서 건너뜀(jsdom 없음, `test/staffview.test.ts:13`). 대체는 `npm run test:dom`이며 이 점검에서는 실행하지 않아 대체 통과는 확인 못 함. `npm ci`로 설치하면 해소(설치 금지로 하지 않음). |
| H4 부정 시험 | OK | 형식 틀린 `subject_ref`·토큰, 토큰 없음/틀림 화면, 헤더 범위, 깨진 본문, 4xx/5xx 분기, 경로 탈출 등(`test/d85.test.ts`, `retry.test.ts`, `static.test.ts`). 없는 것: 두 번째 세션의 `subject_ref` 재사용(P1), 마이크 거부(P4), XSS 문자열 주입(`<script>`를 서버 문구로 주는 시험을 찾지 못함, 구조상 `textContent`라 위험은 낮음). |
| H5 환경 의존 | 문제 L | e2e는 Docker와 `mcr.microsoft.com` 이미지 pull, `fonts-noto-cjk` 설치가 필요(`runbook.md`)해 네트워크·레지스트리 의존. 단위 시험은 환경 의존이 적다(jsdom만 선택). 호스트 직접 e2e는 돌려 보지 못했다고 기록됨. |

### I. 도메인·안전

| 항목 | 판정 | 근거 / 제안 |
|---|---|---|
| I1 환자 안전 결정 | 문제 M (P9) | 재시도 예산 20초는 "정한 것/사용자 결정 대기"로 표시됨(`retry.ts:2`, `design.md`). 그러나 `MIN_CONFIDENCE=0.4`(`stt.ts:13`), 다시 말하기 상한 없음(G12 연동), 위험 정지 화면 무기한 대기(P5), ENDED 8초(`main.ts:67`)는 표시가 없다. 신뢰도가 낮은 증상 발화가 조용히 버려지고 "다시 말씀해 주세요"만 반복될 수 있다. 사용자 결정 필요(값, 상한, 상한 후 직원 호출). 직원 호출 버튼이 LISTENING/REPEAT_PROMPT에 없는 점은 P4. |
| I2 문구 출처 | 문제 L | 고정 문구는 `main.ts`에 흩어져 있다("그대로 기다려 주세요. 직원이 오면 이어서 안내해 드립니다", "직원이 곧 도와드립니다" 등). 재시도 문구만 "임상 문구가 아닌 임시 UI 문구"로 표시(`design.md`). 나머지 환자 문구의 임상 검토 필요 표시가 없다. 자율 수정 가능(표시), 문구 확정은 임상 검토. |
| I3 실패 시 환자 화면 | 문제 M (P4, P5) / L (P16, P20) | 좋은 점: 재시도 중 대기 문구 + 직원 부르기/그만하기(`main.ts:32-37`), 예산 소진·401/403·토큰 없음은 직원 호출 화면, 깨진 본문은 값을 지어내지 않음. 나쁜 점: (1) 마이크 거부 시 무한 "다시 말씀해 주세요"(P4), (2) WAITING_STAFF에서 서버가 죽어도 "직원이 곧 도와드립니다"가 그대로(P5), (3) 종료 요청이 실패해도 "수고하셨습니다"(P16, `flow.ts:109`), (4) `response_text`가 null이면 빈 화면(P20), (5) 최초 로드/새로고침 때 정적 서버 장애는 브라우저 기본 오류 화면(문서화된 한계, `design.md` A3, 보완은 gateway). |

## 이 영역 특유 점검 요약
- 환자 발화·개인정보의 저장·로그·URL·서비스 워커 캐시 잔존: 브라우저 저장소/쿠키/캐시/콘솔/URL은 0건(grep과 코드 읽기). 잔존은 DOM·메모리 쪽(P3)과 STT 제공자 전송(P2).
- 기기 토큰·직원 인증 보관: 기기 토큰은 메모리, 직원 인증은 이 영역에 없음(게이트웨이). P6, P7.
- XSS: 서버 문구는 `textContent`로만 DOM에 들어가며 문제 없음. CSP 있음.
- 서비스 워커 범위: `/staff/` 하나, 캐시·fetch 가로채기 없음.
- 푸시 구독: 서버로 보내고 로컬 보관 안 함. 해지 API(`unregisterPush`, `api/staff.ts:29`)는 있으나 화면에서 부르는 곳을 찾지 못함(P17 L). OS 알림 본문에 세션 ID·종류가 노출(`sw.ts:6`, `requireInteraction`)되며 잠금 화면에 보일 수 있음.
- 세션 종료 후 화면 잔존: ENDED는 8초 뒤 비움, 방치 경로는 P3.
- 접근성: 키오스크 글자 32/40/56 px, 버튼 44 px와 큰 터치 영역, 대비 `#0b3d91` 대 흰색(약 9:1, 계산한 것은 아니고 색상값 기준 추정), 포커스 링 6 px, `lang="ko"`, 라벨 있는 입력창, `aria-live`. 부족(P21 L): TTS 음소거·음량·재생 반복 컨트롤 없음, 글자 크기 조절 UI 없음(브라우저 확대는 viewport가 허용), 직원 콘솔 본문 18 px, 스크린 리더 실제 확인 없음(체크리스트 미체크).
- 오프라인/지연 UX: 키오스크는 재시도 대기 화면과 직원 호출이 있고 직원 콘솔은 연결 상태 배너와 목록 실패 표시가 있다. 사각: WAITING_STAFF(P5)와 최초 로드.
- 한국어 입력/음성 인식 실패 대체: STT 미지원 브라우저는 입력창 대체(OK), 마이크 거부·오류는 대체 없음(P4).
- 직원 콘솔 권한·행위자 표시: 게이트웨이 전제(P6), 목록에 해결자 미표시(P24).

## 이 점검이 읽지 못한/얕게 본 곳
- 실제 게이트웨이(Caddyfile), survey-service, deploy는 읽지 않았다(이웃 영역 읽기 금지 범위). CSP/HSTS가 gateway 뒤에서 유지되는지, 직원 경로 인증, 토큰 발급·폐기, CSRF는 확인하지 못했다.
- `boundary-contracts`는 `PUBLIC_API.md`에서 몇 줄(409 행, 세션 시작 행, 행위자 헤더)만 grep했다. 스키마 JSON 전체와 실서버 응답 대조는 하지 않았다.
- 실행한 것: `npm test`(통과 109, 건너뜀 8), `npm audit`, `npm ls`. 실행하지 않은 것: `typecheck`, `check-schema`, `doctor`, `smoke`, `test:dom`, `test:e2e`(Docker 필요, 점검 범위 밖으로 둠). 시험 본문은 이름·일부 줄만 읽었고 주장하는 단언 전부를 확인하지는 않았다.
- `mock-server/app.ts`(273줄), `scripts/doctor.mjs`, `scripts/check-schema.mjs`, `test-e2e/browser.e2e.test.ts` 본문은 훑지 않았다(모의 서버는 운영 경로 아님).
- 색 대비는 값으로 추정했을 뿐 도구로 측정하지 않았고, 스크린 리더·실제 기기·실제 마이크·실제 TTS 음성·실제 푸시는 확인할 수 없다.
- 세션 시작 요청의 서버 멱등성, 브라우저 STT/TTS가 실제로 외부로 전송하는 데이터 범위(브라우저·단말 구성에 따라 다름)는 확인하지 못했다.
