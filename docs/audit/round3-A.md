# 3차 점검 A (독립 코드 점검, diff 기준)

범위: survey-service b9ba3d8..73e9064, kiosk-frontend a32b44b..c7f54e9, model-lab 226a763..a092922, model-runtime 5c61125..f8e3588.
방법: diff 읽기 + survey-service .venv로 실제 실행. 수정·커밋 없음. 아래 "확인"은 실행해 본 것, "추정"은 읽기만 한 것.

## 지적

### H-1 위험 신호가 조용히 사라진다: 부정 표지 검사가 너무 넓다 (survey-service/risk_rules.py `phrase_context`, `_NEG_KO` 약 L167-175)
- 입력 -> 결과(확인, `RuleRiskSource.provisional_default().match`, 결과 None = 정지·알림 없음):
  - "죽고 싶고 아무 희망이 없어요" -> None (구절 뒤 같은 절의 "없"이 부정으로 처리)
  - "자살 생각이 계속 나요 없어지지 않아요" -> None
  - "가슴이 아파요 약을 먹어도 안 나아요" -> None ("안 나")
  - "가슴이 아파요 아니 정말 많이 아파요" -> None
  - 반대로 "가슴이 아파서 일을 못 해요"는 잡힌다(못 해는 걸리는데 "안 나"는 걸러지는 비일관).
- 구절 뒤 30자 안에 없/않/아니/안 나 등이 오면 위험 자체를 부정한 것으로 보지만, 위험 진술 뒤에 이어지는 다른 부정문(희망이 없다, 안 낫는다)을 구분하지 못한다. 환자 안전 영역에서 놓침 비용 > 거짓 알림 비용이라는 이 모듈의 원칙과 반대로 동작한다.
- 심각도 H. 시험(`test_risk_precision.py`)은 "자살 생각은 없어요" 류 정상 부정만 고정하고 이런 이어지는 부정문은 시험하지 않는다.
- 제안: 부정 판정을 구절 바로 뒤 서술어(어미 직후 1~2어절)로 좁히거나, 불확실하면 정지 쪽으로 기울인다. 거짓 알림/놓침 균형은 임상 결정이라 사용자 결정 필요.

### H-2 제3자 표지가 본인 위험을 지운다 (risk_rules.py `_THIRD`, `phrase_context`)
- 확인: "가족이 없어서 죽고 싶어요" -> None, "남편이 때려서 죽을 것 같아요" -> None, "엄마 때문에 자살하고 싶어요" -> None.
- 같은 절 앞쪽에 가족 단어가 있고 `_SELF`(제가/저는/나는…)가 없으면 제3자 이야기로 본다. 한국어는 주어를 생략하는 일이 흔하고, 가족 때문에/가족이 없어서는 자해 사유 진술의 전형이다. 학대 상황("남편이 때려서")은 특히 위험하다.
- "친구가 자살했어요 저도 죽고 싶어요"는 잡힌다(저도 때문). 주어 생략형이 구멍이다.
- 심각도 H. 제안: 가족 단어 뒤에 조사 "가/이/은/는"가 바로 붙은 주어 표지일 때만 제3자로 보고, "~때문에/~없어서/~때려서"처럼 원인으로 쓰인 경우는 제외. 사용자(임상) 결정 필요.

### H-3 경과 표지가 현재 지속되는 증상을 지운다 (risk_rules.py `_HISTORY`, `_NOW`)
- 확인: "3개월 전부터 가슴이 아파요" -> None, "한 달 전부터 숨쉬기 힘들어요" -> None. "개월 전/달 전/년 전" 이 "~전부터 (지속)"에도 걸려 history로 분류되고 "지금/오늘/계속" 같은 현재 표지가 없으면 정지하지 않는다. 지속 중인 흉통·호흡곤란이다.
- 심각도 H(M 이상). 제안: "전부터"(계속 진행)는 history에서 제외, "전에"/"전에는"/"~했었"만 과거로.

### H-4 어절 시작 제약이 이전에 잡던 표현을 놓친다 (회귀) (risk_rules.py `_BOUNDARY`, `_phrase_regex`, `match`)
- 확인(구 compact 방식이면 잡혔던 입력): "반신마비가 왔어요" -> None, "전신마비 같아요" -> None, "너무죽고싶어요" -> None, "극심한가슴통증" -> None, "심한호흡곤란이에요" -> None.
- 구절 앞이 한글이면 매칭하지 않는다(`(?<![0-9A-Za-z가-힣])`). 복합어 접두("반신마비", "극심한가슴통증", "심한호흡곤란")와 STT가 띄어쓰기를 붙여 내는 경우를 잃는다. 병원이 `SURVEY_RISK_RULES_FILE`로 준 `contains` 규칙에도 같은 제약이 걸려 기존 운영 규칙의 동작이 바뀐다(문서 CHANGELOG에 호환성 변경으로 적혀 있는지 확인 못 함).
- 심각도 H. 제안: 구절 앞 경계는 완화하고(예: 앞이 한글이어도 허용하되 오탐 구절만 목록으로 제외), 규칙 파일의 `contains`는 이전 부분문자열 의미를 유지.

### H-5 알림 멱등이 전달 실패를 성공으로 바꾼다 (survey-service/alerts.py `raise_alert` L446-456, graph.py `_deliver`)
- 확인(실행): 구독자가 없는 상태에서 `CURRENT_TURN=("s1","t1")`로 `raise_alert` -> 첫 호출 `DeliveryFailed`(알림은 저장). 같은 턴 재시도 -> 예외 없이 기존 알림 반환(`delivered` 증가 없음, SSE 재게시·푸시 재시도 없음). 서비스는 이를 DELIVERED로 기록해 키오스크가 "직원 호출 화면"(DELIVERY_FAILED 신호)을 보이지 않고 직원도 실시간으로 받지 못한다.
  이 재시도는 NOT_COMMITTED 재전송 경로(같은 turn_id)의 목적이기도 하다. 새 시험(`test_same_turn_resend_reuses_the_alert`)은 구독자를 미리 붙여(`svc.hub.subscribe()`) 이 경로를 가린다.
- 같은 (세션, 턴)에서 종류가 다른 알림도 합쳐진다(확인): RISK 알림 뒤 같은 턴의 `CALL_STAFF` 요청이 RISK_STOP으로 반환되고 새 행이 없다. `find_by_turn`이 kind를 보지 않는다.
- 심각도 H. 제안: 멱등 키를 (session, turn, kind)로 하고, 기존 알림이 전달 성공한 적 없으면(delivered 기록이 없으면) 재게시·재푸시하고 그 결과로 DeliveryFailed 여부를 결정.

### M-1 위험 선별 세션 존재 확인이 위험을 버리는 조건 (graph.py L286-307)
- `store.load(sid)["status"] == "NOT_FOUND"`이면 알림 없이 `{}`. 시험은 `rig.store.load`를 람다로 대체(DB_ERROR)해 NOT_FOUND와 장애를 가른다(모킹). 실제 저장소가 보존기간 삭제·다른 인스턴스로 NOT_FOUND를 줄 때도 위험 발화가 조용히 버려진다(그 뒤 흐름이 같은 NOT_FOUND 오류로 끝난다면 환자 화면은 오류이지만 직원 알림은 없다). 추정(실제 NOT_FOUND 경로는 실행 안 함).
- 심각도 M. 허위 알림 억제와 놓침 사이의 결정이므로 사용자 결정 필요. 최소한 `risk_prescreen_unknown_session` 카운터에 경보를 건다.
- 부수: probe 스레드가 `store.load`에서 막히면(세션 락 보유 중 등) 예산(0.1~1.0s)만큼 매 턴 지연, 스레드는 daemon으로 남는다(L).

### M-2 정규식(매칭) 비용이 입력 길이에 이차 (risk_rules.py `_clause_bounds`)
- 확인: "자살 은 아니고 " x8000(72k자) 14초, x4000 3.9초. 적중마다 `text[:start]` 전체에 `finditer`하므로 적중 수에 이차. API는 utterance를 1000자로 자르므로(`api_max_utterance_chars`) 현재 노출은 작다(1000자는 ms 수준). 상한이 다른 경로(외부 위험 신호 API, 큰 설정, 모델 출력)로 들어오면 CPU 폭주.
- 심각도 L. 제안: 절 경계를 한 번 미리 계산.

### M-3 인증 실패 제한이 무차별 대입을 막지 못한다 (model-lab service/app.py L236-247)
- 유효한 토큰은 제한과 무관하게 통과하도록 바꿨고(프록시 뒤 정상 호출자 보호) 틀린 토큰은 503. 그러나 제한이 걸린 주소에서도 옳은 추측은 200이라 시도 횟수 제한 효과가 사라진다(공격자는 503을 계속 받으며 무한히 추측 가능). 토큰 엔트로피(16바이트 hex 등)가 실제 방어다. 추정(코드와 시험 `test_repeated_bad_tokens_are_throttled...` 읽기).
- 심각도 M(토큰이 충분히 길면 실질 위험 낮음). ADR/주석에 "제한은 로그 소음·서비스 보호용이며 추측 방어는 토큰 길이"라고 쓰고 최소 토큰 길이를 시작 때 강제하는 것을 제안.

### M-4 유휴 초기화 제거로 키오스크가 영구 대기 화면에 머문다 (kiosk-frontend flow.ts L76-87, main.ts ENDED/CALL_STAFF)
- 의도된 설계(문서 표)이지만 부작용: CALL_STAFF(NO_DEVICE_TOKEN, BAD_SUBJECT_REF, REPEAT_LIMIT 포함)와 WAITING_STAFF, 종료 실패 안내는 사람이 와서 누르기 전까지 영구. 환자가 떠난 뒤 이전 환자의 상태(WAITING_STAFF의 안내 문구, 서버의 PAUSED_RISK 세션)가 다음 사람에게 보이는 것은 줄었지만, 그 키오스크는 직원이 올 때까지 사용 불가다. 또한 CALL_STAFF 화면의 "처음으로"는 여전히 `reset()`만 호출해 서버 세션을 끝내지 않는다(문서의 "벗어나는 길은 직원 결정이나 환자의 명시적 동작뿐"과 달리 환자가 눌러 PAUSED_RISK 세션이 열린 채 다음 사람이 시작한다. 이 경우 DELIVERY_FAILED 위험 알림이 직원에게 안 닿은 상태가 사라진다).
- 심각도 M. 제안: 직원 호출 전달 실패(CALL_STAFF의 DELIVERY_FAILED 사유)에서는 "처음으로"를 숨기거나 서버 종료/직원 확인 후만 허용. 확인 못 함: 실제 브라우저 동작(코드 읽기 기준).

### L-1 STT 설치 시간 초과 후 재확인 없음 (stt.ts L47-57)
- `install()`이 10초를 넘기면 `st="unavailable"`로 굳고 `init()`은 한 번뿐이라 이후 언어 팩이 받아져도 새로고침 전까지 글자 입력만 쓴다(시험이 "다시 확인하지 않는다"를 고정). `allowRemote`가 켜진 기기에서는 시간 초과가 곧 외부 인식(remote)으로 전환되어 음성이 기기 밖으로 나간다(환자 고지 문구는 뜸). 의도라면 문서에 명시. 추정.

### L-2 기기 토큰 소유 없는 세션 차단의 이행 (api.py `_device_denied`)
- 기기 토큰을 쓰는 구성에서 이전 버전이 만든 세션(`session_meta.device_id` NULL)은 업그레이드 후 기기 토큰으로 접근하면 404. 진행 중 세션이 업그레이드 시점에 끊긴다. `_NEW_COLUMNS`로 열만 추가되고 이전 값은 채워지지 않는다. 추정(실행 안 함). 운영 절차로 "업그레이드는 진행 중 세션이 없을 때"를 적을 것.

### L-3 model-lab 거절 응답 처리 (app.py `_drain`, `_publish`)
- 큰 업로드가 거절(UNAVAILABLE 동시 게시 상한 등)되면 서버는 1MiB만 버리고 연결을 닫아 클라이언트는 503 대신 연결 초기화를 볼 수 있다(코드 주석과 시험이 인정). 클라이언트가 이를 재시도 가능으로 다루는지는 확인 못 함.
- `_consumed`/`_sent_close`가 핸들러 인스턴스(= keep-alive 연결) 단위라, 성공한 게시 뒤 같은 연결의 거절 POST는 본문을 버리지 않는다(기존 동작). 추정.

### L-4 (경계) NAT64 등 SSRF 추가 (netguard.py)
- 변경 자체는 타당(IPv4-mapped/NAT64/6to4/Teredo/`::/96` 처리). 실행해 보지 않았다. ISATAP(`::5efe:a.b.c.d`가 글로벌 접두 아래)와 `64:ff9b::/96`의 로컬 IPv4 임베딩은 위 로직이 임베딩된 IPv4로 판정하므로 닫힘. 남은 위험은 DNS 재바인딩(검사 시점과 연결 시점 차이)이며 이 diff 범위 밖 -> 확인 못 함.

## 문제 없다고 판단한 부분
- survey-service 깊은 중첩: `_has_surrogate` 반복화와 `RecursionError` 처리는 타당. 단 JSON 파서를 통과한 깊이(약 900단계)가 이후 단계(검증·직렬화)에서 RecursionError를 내는지는 실행하지 않아 확인 못 함.
- kiosk-frontend `take()/confirm()`: confirm이 시작 성공 뒤에만 불리고 값이 바뀌었으면 비우지 않는 동일성 비교가 있어 경쟁에 안전(코드 읽기).
- kiosk-frontend `stt.cancel()`을 비듣기 상태 렌더마다 호출: `abort()`가 `onerror("aborted")`/`onend`를 내도 `sttError`/`hear`가 상태(LISTENING/REPEAT_PROMPT)가 아니면 무시하므로 화면을 덮어쓰지 않음.
- kiosk-frontend 발화 자르기를 코드 포인트 단위로 바꾼 것은 서버의 문자 수 기준(Python len)과 일치.
- model-lab SIGTERM 우아한 종료: 유휴/진행 중 구분, 8초 유예 < Docker 10초, 시험 2개(실제 프로세스) 통과. `test_hardening.py`, `test_service.py` 30개 통과 확인.
- model-lab `.tmp-*` 정리를 게시 잠금 안에서 하도록 한 것은 타당.
- model-runtime: `prepare_bundle.py` release-id 검증(`fullmatch`, `.`/`..` 거절, out 직계 확인, 심볼릭 링크 거절, 표식 파일)과 `run_session.sh`의 검사 후 생성(`realpath -m`), 캐시 표식/활성 PID 파일, 값 없는 옵션 종료 코드 2는 의도대로 보임. 표식 파일이 릴리스 tar에 포함되지만 `PREPARE_REPORT.json`도 이미 포함되는 구조라 추가 위험 없음(추정).
  - 주의(추정): `curl -H @파일`은 curl 7.55 이상 필요. 이 PC는 8.5.0이다. GPU 서버의 curl 버전은 확인하지 않았다(서버 접속 안 함). 낮으면 readyz가 401로 영원히 실패해 세션이 준비 시간 초과로 끝난다. `docs/GPU_SESSION.md`에 최소 버전을 적을 것.
  - 시험 `test_token_is_not_in_curl_arguments`는 스크립트 텍스트 검사라 실제 ps 노출을 확인하지는 않는다(H1 약함, 영향 낮음).

## 시험이 실제 동작을 가리는 곳 (H1)
- survey-service `test_risk_phrase_on_unknown_session_...`: `store.load`를 람다로 교체. `test_same_turn_resend_reuses_the_alert`: 구독자를 미리 붙여 전달 실패 경로를 시험하지 않음(H-5).
- `test_risk_precision.py`: 정상 부정문 중심. H-1~H-4 입력은 시험에 없다.

## 요약
H 5건(위험 문구 매칭 부정/제3자/경과 3건, 어절 경계 회귀, 알림 멱등이 전달 실패를 성공으로 바꿈), M 4건, L 4건. 가장 급한 것은 H-5(실행으로 재현)와 H-1/H-2(실행으로 재현).
