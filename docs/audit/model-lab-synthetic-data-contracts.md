# 전수 점검: model-lab, synthetic-data, boundary-contracts

점검일 2026-10-28. 읽기 전용 감사(코드·설정·문서 수정 없음, 커밋 없음, 학습 서버 접속 없음, 설치·외부 전송 없음). 기준은 `head/docs/AUDIT_CHECKLIST.md` A~I 63개 항목과 `head/docs/FAULT_POLICY.md`. 판정은 영역마다 항목마다 하나이고, 칸의 첫 낱말이 판정(`OK`, `문제H/M/L`, `해당없음`, `확인못함`)이다. 같은 원인은 아래 "문제 목록"의 ID로 묶었다.

## 요약

항목 63개 x 영역 3 = 판정 189칸(분모 189). 칸의 첫 낱말 기준, 한 칸에 문제가 여럿이면 가장 무거운 것 하나로 셈.

| 영역 | OK | 문제H | 문제M | 문제L | 해당없음 | 확인못함 | 합 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| model-lab | 25 | 0 | 14 | 17 | 6 | 1 | 63 |
| synthetic-data | 12 | 0 | 13 | 17 | 17 | 4 | 63 |
| boundary-contracts | 20 | 0 | 5 | 5 | 33 | 0 | 63 |
| 합계 | 57 | 0 | 32 | 39 | 56 | 5 | 189 |

문제 칸이 많은 것은 같은 원인이 여러 항목에 걸리기 때문이다. 원인 기준 고유 문제는 M 19건, L 19건(아래 "문제 목록").

**H 문제: 없음.** 다만 SD-2(비식별·미검수 데이터 통과)는 "외부 데이터는 합성이다"라는 가정이 틀리면 H가 된다. 그 가정을 코드나 설정이 강제하지 않는다는 점이 M인 이유다.

**M 문제 (원인 기준 19건)**
- ML-1 model-registry 서버에 소켓 timeout·동시 연결 상한이 없다
- ML-2 디스크 가드가 게시·학습·파이프라인 경로에 없다(doctor의 경고뿐이고 runbook과 충돌)
- ML-3 게시가 중단된 뒤 재시도하면 `list_versions`가 같은 버전을 두 번 낸다(재현함), SIGTERM·`.tmp` 정리 없음
- ML-4 의존·이미지 핀이 약하고 시험 환경이 핀과 다르다(.venv의 model-runtime 0.6.5, turn-engine 0.3.0으로 158건 통과)
- ML-5 `package-adapters`의 학습 계보를 검증하지 않는다(데이터셋 ref는 입력 그대로, 서버 스크립트 해시와 학습 기록은 패키지에 안 들어감)
- ML-6 게시 무결성은 자기일관성 해시뿐이다(서명·출처 증명·게시자 기록 없음, 사용자 결정)
- ML-12 G06: 서버 학습 코드와의 어긋남을 자동으로 알 길이 없다(설정에 서버 절대 경로 고정, 인자 이름은 사람이 확인한 스냅샷)
- ML-14 레지스트리는 평문 HTTP이고 운영 접근 방식이 정해지지 않았다(사용자·헤드 결정)
- SD-1 게시기의 거부 사유에 행 값이 섞여 보고서와 불변 매니페스트에 남는다(실측)
- SD-2 비식별 확인 주체가 없다(model-lab은 데이터셋 쪽 책임, synthetic-data 게시기는 검사 없음). `origin`을 SYNTHETIC으로 고정, `pending` 행 통과
- SD-3 평가 누수 검사가 `scenario_id` 일치만 본다(같은 발화가 다른 시나리오 ID로 TRAIN·EVAL에 걸쳐도 통과, 실측)
- SD-4 게시기를 `version` 지정과 함께 다시 돌리면 CONFLICT가 난다(실측, `created_at` 기본값이 현재 시각)
- SD-7 핵심 경로 시험 15건 보류(생성 경로), 게시기는 실제 데이터로 돌린 적 없음, v2 의미 검사 없음
- BC-1 v2.0.2 태그 뒤 `PUBLIC_API.md`가 6커밋 바뀌었는데 버전·CHANGELOG·태그가 없다
- BC-2 오류 의미 규약이 어긋난다(retryable이 코드 고정인데 409 TURN_IN_PROGRESS는 재시도, 401·429·502·504 미정의, FAULT_POLICY의 UPSTREAM_UNAVAILABLE이 BoundaryError 열거에 없음, 클라이언트가 Retry-After를 무시)
- BC-3 HTTP.md·CONVENTIONS가 "토큰은 환경 변수"라고 적어 D84와 충돌한다
- BC-4 하위 호환 규칙을 기계가 검사하지 않는다(태그 간 스키마 diff 검사 없음)
- BC-5 태그 불변성 규칙·서명·원격 확인이 없다(경량 태그 4개)
- X-1 I2 DatasetStore에 HTTP 면이 없어 model-lab이 synthetic-data의 파일 배치를 직접 읽는다(D49 소지)


## 점검에서 직접 돌린 것

| 한 것 | 결과 | 환경 |
| --- | --- | --- |
| model-lab `.venv/bin/python -m pytest -q` | 158 passed, 0 skipped, 30초. 경고 787(대부분 `jsonschema.RefResolver` 폐기 예고) | 이 PC `.venv`. `pip list`: boundary-contracts 2.0.2, **model-runtime 0.6.5, turn-engine 0.3.0**(핀은 v0.7.2, v0.4.0), jsonschema 4.26.0 |
| synthetic-data `.venv/bin/python -m pytest -q` | 106 passed, 15 skipped, 4초 | boundary-contracts 2.0.2는 `../boundary-contracts` 작업 트리(editable), jsonschema 4.10.3 |
| boundary-contracts `python3 verify.py` | OK 102줄, FAIL 줄 없음(TurnTrace 검증은 survey-service 스키마가 있어 수행됨) | 시스템 python3, jsonschema 4.10.3 |
| boundary-contracts `python3 -m unittest discover -s tests` | Ran 110 tests, OK | 같은 환경 |
| 스크래치패드 재현 `dup_order.py` | 게시 중 매니페스트 쓰기 직전에 실패시킨 뒤 같은 패키지를 다시 게시하면 `list_versions == ['v1','v1']` | model-lab `.venv`, 임시 디렉터리 |
| 스크래치패드 재현 `imp_probe.py` | (a) `version`을 지정하고 `created_at` 없이 같은 입력을 두 번 게시하면 두 번째가 CONFLICT, (b) TRAIN과 EVAL에 같은 발화를 다른 `scenario_id`로 넣어도 PUBLISHED | synthetic-data `.venv`, 가짜 입력 |
| 스크래치패드 재현 `phi_probe*.py` | 검증 실패 사유 문자열에 입력 값이 들어간다(`{'a': 1} is not of type 'string'`). 키 이름은 항상 포함된다 | synthetic-data `.venv` |
| grep 위험 패턴(subprocess, shell, eval, pickle, yaml.load, urlopen, 0.0.0.0, verify=False, torch.load) | 아래 해당 항목에 반영 | 세 리포 |
| model-registry 라우트 전수 | 아래 표 | `model_lab/service/app.py` 읽기 |

### model-registry 서버 라우트 전수표 (`model_lab/service/app.py:148-184`)

| 경로 | 메서드 | 인증 | 비고 |
| --- | --- | --- | --- |
| `/healthz` | 모든 메서드(`_handle`이 같은 처리) | 없음 | 200 `{"status":"ok"}` 고정(:151) |
| `/readyz` | 모든 메서드 | 없음 | 저장소 읽기+`.tmp` 쓰기 성공이면 200, 아니면 503(:153-155, :80-88) |
| `/v1/packages` | GET | 읽기 토큰 또는 쓰기 토큰 | 목록, `limit` 최대 500(:163-165, :242-249) |
| `/v1/packages` | POST | 쓰기 토큰(역할 `model-lab`만) | tar 게시. 201/200/409. `Content-Length` 필수, 상한 4GiB(:186-222) |
| `/v1/packages/{id}/versions` | GET | 읽기/쓰기 토큰 | 목록 |
| `/v1/packages/{id}/versions/{version}` | GET | 읽기/쓰기 토큰 | 매니페스트, 읽을 때 `content_hash` 재검증(registry.py:106-112) |
| `/v1/packages/{id}/versions/{version}/adapter` | GET | 읽기/쓰기 토큰 | 해시 검증 뒤에만 tar로 보냄(:176-180) |
| `/v1/eval-reports/{ref}` | GET | 읽기/쓰기 토큰 | 바이트 그대로(:181-183) |
| 그 밖의 경로, PUT/DELETE/PATCH | — | 인증 먼저(:156), 통과하면 404 | 인증 없는 호출은 403 PERMISSION_DENIED(401이 아님, CONVENTIONS §9 표에 401 없음). HEAD/OPTIONS는 핸들러가 없어 기본 501 |

기본 거부는 지켜진다(healthz·readyz 외 모든 경로가 `authorize`를 먼저 통과해야 한다, 토큰 비교는 `hmac.compare_digest`:68). 쓰기 토큰은 시작할 때 역할이 `model-lab`이 아니면 거부한다(:53-55).

## 항목별 판정

### A. 신뢰성

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| A1 외부 호출 timeout | 문제M ML-1: 서버 쪽 소켓 읽기 timeout이 없다(app.py:252-255, 느린 클라이언트가 스레드를 잡음). 학습 `subprocess.run`에 timeout 없음(train_wrap.py:209, brief는 `timeout` 감싸기를 요구하지만 감싸기는 호출자 몫). 클라이언트 쪽은 `registry.timeout` 설정이 있다(config.py:121-123) | OK: 이웃 어댑터 timeout 기본 10초(adapters.py:26-30)를 클라이언트가 소켓 timeout으로 쓴다(_http.py:100-108) | OK: `HttpClientBase`가 timeout을 받아 모든 `open`에 건다(_http.py:93-108). 총 마감이 아니라 소켓 단위 timeout이다 |
| A2 재시도는 멱등 호출만 | OK: 재시도 코드가 없다. `UNAVAILABLE`은 종료 코드 3으로 알리고 같은 명령 재실행이 안전(게시 멱등 registry.py:94-98, boundary.md 경계 오류 절) | OK: 재시도 코드 없음, 종료 코드 75를 스케줄러가 재실행(__main__.py:41), 게시 멱등(store/base.py publish) | OK: 클라이언트는 재시도하지 않고 `UNAVAILABLE`만 재시도 가능하다고 규정(_http.py 머리말, CONVENTIONS §4). 백오프·지터는 호출자 몫이라 규약에 없다 |
| A3 부분 쓰기 없음 | 문제M ML-3: 매니페스트를 마지막에 쓰므로 반쯤 게시된 패키지는 안 보인다(registry.py:272-273). 그러나 `_order.json`을 매니페스트보다 먼저 쓰므로(:269-271) 중단 뒤 재시도하면 버전이 중복된다(재현함) | 문제L SD-10: 임시 디렉터리 후 rename으로 원자적(file_store.py:49-56)이지만 `fsync`가 없어 전원 장애 뒤 빈 파일이 남을 수 있다. 보고서 쓰기는 비원자(importer.py:346) | OK: tar 받기가 실패하면 대상 디렉터리를 지운다(_http.py `_download_tar` BaseException 처리) |
| A4 우아한 종료 | 문제M ML-3: SIGTERM 핸들러가 없고 KeyboardInterrupt만 처리(app.py:271-275), `daemon_threads=True`(:254)라 진행 중 요청이 끊긴다 | 해당없음: run-once 잡(서비스 아님, README) | 해당없음: 서버가 없는 라이브러리 |
| A5 재시작 후 자동 정상화 | 문제M ML-3: 잔재 `final` 디렉터리를 지우고 다시 쓰는 복구(registry.py:260-261)는 있다. 그러나 `.tmp` 아래 남은 임시 디렉터리를 시작 때 지우지 않고(app.py:58-59) 중복 버전은 사람이 고쳐야 한다 | OK: `.tmp-` 접두 디렉터리를 목록에서 제외(file_store.py:48,79)하고 재실행이 멱등(importer.py:319-326) | 해당없음 |
| A6 무한 증가 없음 | 문제M ML-3: `.tmp`와 `runs/`(668MB) 정리 정책이 없다. 레지스트리는 불변 누적이라 보존 정책이 없다 | 문제L SD-5: 데이터셋 버전은 불변 누적, 보존·정리 정책 문서 없음. 보고서는 덮어쓰기라 증가 없음 | 해당없음 |
| A7 동시성 | 문제L ML-7, ML-13: 게시는 `flock`+`RLock`으로 직렬화(registry.py:93, :207-214)되어 안전. 다만 게시 응답 코드(200/201) 판정이 락 밖이라 경쟁하면 코드가 틀릴 수 있다(app.py:214-221). `run-once` 동시 실행 방어가 없고 runbook이 "같은 시각에 두 번 부르지 않는다"로만 막는다(runbook.md:85) | 문제L SD-10: 동시 게시 시 `seq` 계산이 락 없이 이뤄져 같은 번호가 나올 수 있다(file_store.py:48-54). 같은 버전 경쟁은 rename 실패로 처리(:55-62) | 해당없음 |
| A8 /healthz·/readyz | OK: healthz는 의존 없이 200, readyz는 저장소 읽기와 임시 쓰기를 확인해 503(app.py:151-155, :80-88). 시험 test_service.py:37,113 | 해당없음: 서비스가 아니라 `/healthz`도 없다고 명시(README) | 해당없음: 참조 서버(conformance)는 시험용 |
| A9 자원 한도 | 문제M ML-1, ML-2: 본문 상한 4GiB는 있으나(app.py:51,191) 스레드·연결 수 제한이 없고 디스크 여유 확인이 없다 | 문제L SD-5: 입력 파일 전체를 메모리에 읽는다(importer.py:195), 행 수·파일 크기 상한 없음 | OK: 클라이언트 상한이 있다(`max_tar_bytes` 8GiB, `max_body_bytes` 256MiB, tar 항목 20만: _http.py:112-113,142-143) |

### B. 보안

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| B1 인증 | OK: 위 라우트 표. healthz·readyz 외 전부 인증 필수, 쓰기 경로는 쓰기 토큰 전용(app.py:72-78,156-160). 시험 test_service.py:42 | 해당없음: 서버가 없다. 이웃 호출은 토큰을 보낸다(adapters.py) | 해당없음: 라이브러리(규약만 CONVENTIONS §6, §9) |
| B2 인가 | OK: 읽기·쓰기 토큰 분리, 읽기 토큰의 쓰기는 403, 쓰기 역할은 `model-lab`만(app.py:53-55,72-78). 사용자별 데이터가 없어 수평 권한 상승은 해당 없음 | 해당없음 | 해당없음: 규약 §6 "쓰기 권한은 소유 영역 하나" 문서화 |
| B3 비밀 | OK: `read_secret`으로 읽고(app.py:260-261), 설정에 비밀을 적으면 시작 거부(config.py:105-117, train_wrap.py:78), 로그는 경로만(app.py:101-102), 시험 test_secrets.py. SSH 개인키를 다루는 코드는 없다(grep `.ssh`, `ssh ` 0건). 학습 서버 접속은 사람이 하고 토큰은 표준 입력으로 넘기도록 문서화(runbook.md:36). 회전은 재시작이 필요(ML-14) | 문제L SD-9: 코드는 `read_secret`(adapters.py:14-23)이고 시험도 있으나 runbook의 GPU 절이 "토큰은 실행 셸의 환경 변수로만 준다"고 적어 D84와 충돌한다 | 문제M BC-3: `secrets.py`는 값을 오류에 안 넣는다(:20-27)는 점에서 OK이지만, HTTP.md "토큰: 서버는 환경 변수 `<이름>_TOKENS`"와 CONVENTIONS §6·§9 "토큰은 환경 변수로 받는다"가 D84와 어긋난다 |
| B4 입력 검증 | 문제L ML-9, ML-10: 게시 tar는 경로(`..`, 절대 경로)·링크·특수 파일·총량을 검사하고(tarutil.py:30-49, 시험 test_service.py:90) ID·limit·Content-Length도 검증한다. 남은 것: `fetch_dataset`가 매니페스트의 `path`를 검사 없이 `dest / path`로 쓴다(datasets.py:45-47), 비정본 학습기가 `torch.load`를 `weights_only` 없이 쓴다(trainers/hf.py:161-162) | 문제L SD-5, SD-6: 행 단위 검증은 충실(importer.py:130-177). 입력 파일 이름이 고정이라 `..` 조작은 불가하나 심볼릭 링크를 따라가고(:190), 크기 상한이 없다 | OK: 클라이언트가 tar 경로·링크·중복·크기를 검사(_http.py:108-155), Id·ArtifactRef 검사(:75-92). 시험 test_clients_models.py:105,146, test_clients_releases.py:78 |
| B5 인젝션 | OK: SQL 없음, 셸 없음(명령을 인자 목록으로 조립 train_wrap.py:131-151, `shell=True` grep 0건). 설정의 `factory`는 임의 모듈을 가져오나(factories.py:36-42) 설정은 신뢰 경계 안이다. 프롬프트 인젝션은 서비스 경로가 아니라 해당 없음 | OK: grep 위험 패턴 0건. `importlib`로 설정의 factory를 가져옴(job.py:47)은 설정이 신뢰 경계 안 | OK: grep 위험 패턴 0건 |
| B6 SSRF·외부 URL | OK: URL은 설정값뿐이고 리다이렉트를 따라가지 않으며 환경 프록시를 읽지 않는다(_http.py:41-45) | OK: 같음(클라이언트 공유) | OK: `_NoRedirect`, `ProxyHandler({})`(_http.py:41-45,98) |
| B7 웹 | 해당없음: 웹 화면 없음(API만) | 해당없음 | 해당없음 |
| B8 전송 | 문제M ML-14: 서버는 평문 HTTP이고 TLS 종료 지점·운영 주소가 "정해지지 않았다"(runbook.md:36). 개발은 SSH 역터널 | 확인못함: 이웃 호출 주소 예가 `http://question-authoring:8080`(adapters.py:5)이고 TLS는 deploy 몫이라 이 리포에서 판단할 수 없다 | 문제L BC-6: 클라이언트가 `http://`를 허용하고 TLS를 강제하지 않는다(_http.py:93-96) |
| B9 의존·공급망 | 문제M ML-4: 태그 설치와 lock은 있다. 그러나 `requirements.txt`의 `jsonschema>=4`, `pyyaml>=6`, `requirements-train.txt` 무핀, Dockerfile의 베이스 이미지가 digest가 아닌 태그(Dockerfile:10,17), 전이 의존(attrs, referencing, rpds-py)이 이미지에서 고정되지 않음(:14), `ssh-keyscan`으로 호스트 키를 처음 만났을 때 믿음(:12). 취약점 스캔(pip-audit)은 설치 금지로 못 돌림 | 문제L SD-8: lock이 있고 태그 고정이나 jsonschema 4.10.3은 model-lab 4.26.0과 다르다. 취약점 스캔은 못 돌림 | 문제M BC-5: 공급망의 근간이 Git 태그인데 불변성 규칙·서명이 없고 경량 태그가 4개다. `pyproject`의 `jsonschema>=4.10`은 상한이 없다(BC-6) |
| B10 속도 제한 | 문제M ML-1, ML-14: 토큰 시도 제한·연결 수 제한이 없다. 상수 시간 비교(app.py:68)만 있다 | 해당없음 | 해당없음 |
| B11 오류 노출 | OK: 오류 본문은 고정 문구, 내부 오류는 형식 이름만 로그(app.py:229-231), 토큰은 오류에 없음(test_secrets.py). 다만 알 수 없는 내부 오류를 재시도 가능한 503으로 낸다(ML-8) | 문제M SD-1: 검증 실패 사유에 jsonschema 메시지가 들어가 입력 값이 섞인다(schemas.py:21, importer.py:162-164,176). 사유가 `import_report.json`과 불변 매니페스트의 `ext.import.invalid_reasons`에 남는다(importer.py:313-316). 문서(design.md 부록 A, importer.py:131)의 "행 내용은 보고서에 넣지 않는다"와 다르다 | OK: 클라이언트가 메시지를 300자로 자르고 토큰을 가림(_scrub _http.py:86-89) |
| B12 토큰 수명·범위 | 문제L ML-14: 토큰은 정적이고 만료·회전은 서비스 재시작이 필요하다. 읽기/쓰기 분리는 있다 | OK: 읽기 토큰(이웃 읽기 전용) 두 개를 어댑터별로 따로 받는다(adapters.py:26-30). 쓰기는 로컬 파일 저장소라 토큰 없음 | 해당없음 |

### C. 데이터·개인정보

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| C1 개인정보 목록 | 문제L ML-15: 어디에 무엇이 있는지 문서에 목록이 없다. 확인한 것: 평가 리포트의 실패 목록은 `sample_id`와 검증 오류뿐이고 발화 원문이 없다(evaluate.py:229-231), 데이터셋 읽기 오류는 줄 번호만(datasets.py:60-62), 회귀 평가는 검토자가 고친 입력을 우선 쓴다(regression.py:59-60). 로컬에 학습 서버 데이터 사본 18MB가 있다(runs/_server_ds, gitignore) | 문제M SD-2: 입력 6개 파일에 어떤 정보가 있는지 목록·보증이 없다. 가정은 "합성"뿐이다 | 해당없음: 데이터를 저장하지 않는다. 계약 문서가 `subject_ref`를 식별 값으로 규정(PUBLIC_API.md §A) |
| C2 최소 수집 | OK: 학습 기록은 데이터 본문이 아니라 해시만 남긴다(train_wrap.py:227), 패키지에는 어댑터·프롬프트·설정뿐 | 문제M SD-2: 외부 행의 `human_review`와 입력·정답을 그대로 싣는다(importer.py:170-173). 걸러내는 기준이 없다(CR-006 4번) | OK: 직원 알림·푸시에 발화를 넣지 않고 `subject_ref`를 로그·알림에 넣지 않는다(PUBLIC_API.md 직원 콘솔, §A) |
| C3 보존·삭제 | 문제L ML-15: 불변 패키지의 보존 기간·삭제 경로와 `runs/` 정리 정책이 없다 | 문제L SD-5: 데이터셋 불변 누적, 보존·삭제 경로 문서가 없다 | 해당없음 |
| C4 비식별 | OK: 로그·평가 리포트에 발화 원문이 들어가는 경로를 찾지 못했다(evaluate.py:229-231, datasets.py:60-62). 단 `raw_errors`(모델 출력 검증 오류) 내용은 얕게만 봤다 | 문제M SD-1, SD-2: 사유에 값이 섞이고, 비식별 검사는 실패 사례 시드에만 있다(seeds.py:44-45). 게시기에는 없다. model-lab design.md:119는 "데이터셋 쪽 책임"이라 적어 아무도 검사하지 않는 공백이다 | 해당없음 |
| C5 저장·전송 암호화 | 문제L ML-15: `runs/_server_ds` 파일이 0644이고 볼륨 암호화는 deploy 몫이다. 전송은 ML-14 | 확인못함: 저장소 디렉터리는 0700으로 만들어진다(`mkdtemp`)는 것만 확인. 볼륨 암호화는 deploy 몫 | 해당없음 |
| C6 접근 기록 | 문제M ML-6: 누가 게시했는지 기록이 없다(서버 로그는 메서드·경로·상태만 app.py:101-102, 쓰기 토큰 역할이 하나라 행위자 구분도 없음) | 해당없음: 배치 잡. 보고서에 입력 파일 sha256이 남아 계보는 추적된다(importer.py:242) | 해당없음 |
| C7 백업·복원 | 문제L ML-17: 레지스트리 볼륨의 백업·복원 절차 문서가 없다 | 문제L SD-5: 데이터셋 저장소 백업 문서가 없다 | 해당없음: Git |
| C8 DB 계정 | 해당없음: DB 없음(파일 저장소) | 해당없음 | 해당없음 |
| C9 마이그레이션 | 해당없음: 스키마 마이그레이션 없음. 파일 배치에 버전 표시가 없어 배치를 바꿀 때 수단이 없다는 점은 L로 적어 둔다(ML-17) | 해당없음 | OK: MAJOR 병행 예외와 이전 방법이 문서화(CONVENTIONS §1.4, CHANGELOG 2.0.0 "v1에서 옮기는 방법") |
| C10 정합성 | 문제L X-2: 시각은 UTC Z, 해시는 JCS로 일관(packager, canonical). 한글 유니코드 정규화 규칙이 없다 | 문제L X-2: 누수 판정이 문자열 일치라 NFC/NFD 차이를 못 잡는다. 규칙이 없다 | 문제L X-2: CONVENTIONS §2 시각·해시 규칙은 명확하나 정규화(NFC) 규정이 없다 |

### D. 정확성·계약

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| D1 공개 API가 계약과 일치 | OK: HTTP.md I3 표와 라우트가 일치(위 표), 상태 코드 매핑이 CONVENTIONS §9와 같음(app.py:29-30), 적합성 시험 test_service.py:120 | 문제M X-1: I2는 HTTP 면이 없고 파일 배치(`<root>/<id>/<version>/…`)가 영역 사이 약속이 되어 있다 | 문제M BC-2, X-1: 오류·상태 코드 규약이 문서마다 다르다(아래 문제 목록). HTTP.md에 I2 절이 없다(HTTP.md:25) |
| D2 불가능한 전이 방어 | OK: 불변·멱등 규칙(registry.py:94-102), 파이프라인 단계 상태 기록(pipeline.py `_mark`) | OK: 게시 검증 순서가 한 곳(store/base.py publish) | 해당없음 |
| D3 멱등키·중복 요청 | OK: 같은 ID·같은 해시는 200, 다르면 409(registry.py:94-102, 시험 test_service.py:59) | 문제M SD-4: 게시기에서 `version`을 지정하면 재실행이 CONFLICT가 된다(importer.py:310,319-328, 실측). `version`을 비우면 digest로 ALREADY_PUBLISHED | OK: CONVENTIONS §4 멱등 규칙, PUBLIC_API의 `turn_id` 멱등 |
| D4 시간·시계 | OK: `created_at`을 패키징이 고정하고 파일 mtime에서 얻는 방식도 재현 가능(attach.py:61-63,104) | 문제M SD-4: `created_at` 기본이 현재 시각이라 `content_hash`가 실행마다 달라진다(importer.py:287). 고정하면 같다 | OK: UTC Z 규칙(CONVENTIONS §2) |
| D5 인코딩·크기 | 확인못함: 본문 상한은 있다(app.py:191). 긴 한글·이모지·null 문자 전용 시험은 찾지 못했다 | 문제L SD-5: UTF-8이 아닌 행은 거부(importer.py:136)하나 크기 상한이 없고 이모지·null 시험은 못 찾았다 | OK: JSON 정수 2**53 상한(CONVENTIONS §2), 응답·tar 크기 상한(_http.py) |
| D6 값 지어내기 금지 | OK: 평가가 원출력 유효성과 보호 후 정확도를 따로 센다(evaluate.py:229). 서빙 쪽 규칙은 model-runtime·turn-engine 몫 | 문제M SD-7: 외부 정답을 스키마로만 검증하고 v2 의미 검사(targets, next_item, save)를 안 한다(CR-006 2번) | OK: `extract`는 끝내 깨지면 값을 만들지 않고 503 OUTPUT_INVALID, `respond` 대체는 헤더로 구분(HTTP.md I9) |
| D7 문서·코드 일치 | 문제L ML-11: README·boundary.md가 model-runtime v0.7.0(요구는 v0.7.2), README 시험 156건(실제 158), runbook.md:90 "df 점검은 쓰지 않는다"와 `train-doctor`의 df 점검(train_wrap.py:296-302)이 충돌, `pyproject` 0.1.0과 CHANGELOG 0.2.3 | 문제L SD-9: README "시험 104건 수집, CR-001~005"는 현재(121건 수집, CR-006 있음)와 다르고 pyproject 0.2.0과 CHANGELOG 0.2.2가 어긋남 | 문제L BC-7, BC-1: METRICS.md가 v1 용어(:11,24)로 알려진 항목(D-C). PUBLIC_API 변경이 CHANGELOG에 없음 |

### E. 운영성

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| E1 구조화 로그 | 문제L ML-17: 로그는 한 줄 평문이고 상관 ID·수준이 없다(app.py:101-102). 비밀·본문은 제외 | 문제M SD-1: 잡 출력은 JSON 한 줄과 `report.json`으로 구조화(__main__.py:38)되어 있으나 사유에 행 값이 섞인다 | 해당없음 |
| E2 지표·경보 | 문제L ML-17: 지표 노출·경보 기준이 없다 | OK: 상태는 종료 코드와 `report.json`/`import_report.json`으로 드러난다(__main__.py 머리말). 스케줄러가 읽는 쪽은 확인 못 함 | 해당없음 |
| E3 설정 | OK: 알 수 없는 키 거부(config.py `additionalProperties:false`), 잘못된 설정은 시작 거부(app.py:266-268), 임계치 기본값 없음(config.py:3-4) | OK: 설정 검증과 종료 코드 2(config.py:67-130), `split.ratios` 기본값 없음(:7-8) | 해당없음 |
| E4 런북 | OK: 문제 확인 표와 절차(runbook.md:96-104, 162-170) | OK: 문제 대응 표(runbook.md) | 해당없음 |
| E5 감시·알림 | 문제L ML-17: 감시 대상·알림 경로 정의가 이 영역 문서에 없다(readyz만 있음) | 확인못함: deploy 스케줄러 몫이라 이 리포에서 판단 불가 | 해당없음 |
| E6 용량 근거 | 문제L ML-17: 레지스트리 용량 측정 없음(어댑터 크기 언급만 runbook.md:49) | 문제L SD-5: 측정 없음. 규모(V2_DRAFT의 5천 행대)는 작다 | 해당없음 |
| E7 시작 순서 | OK: 의존 서비스가 없다. readyz가 저장소 준비를 반영 | 해당없음 | 해당없음 |
| E8 시간 불변식 | 문제L ML-1: timeout 체인 문서가 없고 서버 timeout이 없어 불변식을 잡을 수 없다 | 해당없음 | 해당없음 |

### F. 배포·이미지

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| F1 비root·권한 | OK: uid 10001 비root(Dockerfile:19-20), 쓰기는 `/data`만이라 읽기 전용 루트 가능성은 있으나 시험된 적 없음, 라벨 6개(:27-33). 포트 호스트 바인딩은 deploy 몫(서버 기본 `0.0.0.0`은 컨테이너 안) | 해당없음: 이미지 없음(헤드 승인) | 해당없음 |
| F2 이미지 핀·SBOM | 문제M ML-4: 베이스 이미지 digest 없음, 전이 의존 미고정, SBOM·스캔 없음 | 해당없음 | 해당없음 |
| F3 compose | 해당없음: compose는 deploy 소관(이 리포에 없음) | 해당없음 | 해당없음 |
| F4 되돌리기·업그레이드 순서 | 문제L ML-11: 패키지는 불변이라 되돌림은 새 버전 게시. 영역 버전 정렬 표기(boundary.md의 v0.7.0)가 낡음 | 확인못함: 업그레이드 순서 문서를 찾지 못했다 | 문제M BC-1, BC-5: 태그 뒤 문서 변경이 버전에 안 묶이고 태그 정책이 없다 |
| F5 비밀 파일 권한 | OK: `/run/secrets:ro` 마운트와 0600 파일을 문서화(runbook.md:20,36). 권한 강제는 코드에 없음(BC-8) | 문제L SD-9: 문서가 환경 변수 방식을 적어 둠 | 문제L BC-8: `read_secret`이 파일 권한을 확인하지 않는다(secrets.py:20-27) |
| F6 레지스트리·CI 신뢰 경계 | 문제M ML-4: Dockerfile `ssh-keyscan`(TOFU)과 빌드 때 `--ssh default`, 로컬 레지스트리·CI는 이 리포 밖이라 확인 못 함 | 해당없음 | 문제M BC-5: 태그가 신뢰 단위인데 서명이 없다 |

### G. 성능·용량

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| G1 측정 처리량 | 문제L ML-17: 게시 처리량·지연 측정 문서가 없다 | 문제L SD-5: 측정 없음 | 해당없음 |
| G2 N+1·인덱스·풀 | 해당없음: DB 없음. 목록은 JSON 전체 읽기(규모 작음) | 해당없음 | 해당없음 |
| G3 큰 입력 폭주 | 문제M ML-1, ML-2: 4GiB 본문을 `.tmp`에 쓰고(app.py:196-202), 풀고(:203), 최종 위치에 또 복사(registry.py:262)하므로 최대 약 3배 디스크 | 문제L SD-5: 입력 전체를 메모리에 읽는다(importer.py:195) | OK: 응답·tar 크기·항목 수 상한(_http.py:112-113,142-143) |

### H. 시험 품질

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| H1 핵심 경로가 실제 구성요소로 | OK: 레지스트리는 memory/file/http 세 구현이 같은 시험을 통과하고 http는 실제 서버+실제 클라이언트다(test_registry.py:25-36, test_service.py:120). 단 학습·평가는 가짜 오라클 모델뿐(U10) | 문제M SD-7: 게시기는 가짜 행으로만 시험(실제 파일 0), 행 형식은 추정(importer.py:3-8) | OK: conformance 참조 서버+실제 클라이언트(tests/test_clients_*) |
| H2 간헐 실패 | OK: 포트 0 사용(test_registry.py:38), 고정 포트·sleep grep 0건. 과거 연결 초기화 간헐 실패를 고친 기록(app.py:133-134, test_service.py:138) | OK: 고정 포트 grep 0건. `ref_server.py:132`의 sleep은 지연 시험용 | OK: grep 0건 |
| H3 건너뛰는 시험 | OK: 158 passed, 0 skipped(실행 확인) | 문제M SD-7: 15 skipped(`needs_generator_v2`, 사유는 conftest에 있으나 대체 수단 없음). 생성 경로의 종단·분리·재현 시험이 모두 여기에 있다 | OK: skip 0건. 단 `verify.py`가 survey-service 스키마가 없으면 TurnTrace 검증을 건너뛴다(verify.py:48-54) |
| H4 부정 시험 | OK: 토큰 분리·오류 코드·위험 tar·변조 탐지·검증 오류(test_service.py:42,80,90, test_registry.py:96,140,147) | 문제M SD-3: 거부 시험은 충실(test_import.py:96,128,145,155)하나 같은 발화가 다른 시나리오 ID로 걸치는 누수의 부정 시험이 없고, 실측하니 통과해 버린다 | OK: 거부 예시 22건 이상(verify.py), `tools/negatives_v2.py`, 위험 tar 시험 |
| H5 환경 독립 | 문제M ML-4: 시험이 통과한 `.venv`는 핀과 다르다(model-runtime 0.6.5, turn-engine 0.3.0). 핀 환경에서의 통과는 확인 못 함. 두 번째 환경 검증(U12)도 열려 있다 | 문제L SD-8: 시험이 `../survey-service/schema` 형제 폴더와 작업 트리 boundary-contracts에 의존(tests/conftest.py:14-15) | 문제L BC-9: 새 venv·두 번째 환경에서 돌린 적이 없다(README §4가 인정). 이번 점검도 시스템 python3 한 환경 |

### I. 도메인·안전

| 항목 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| I1 환자 안전 결정이 코드에 박히지 않음 | OK: 임계치·합격 판정이 설정 스키마에 들어갈 수 없고(config.py:3-4) 리포트에 합격 여부가 없다(attach.py:67-72). O11은 비워 둠 | OK: `split.ratios` 기본값 없음, 예시 값은 자리 표시임을 명시(config.py:7-8, configs/dev.job.json). 게시기 허용치는 설정에서 필수 | 해당없음: 위험 신호 처리 규칙은 survey-service 몫. 계약은 입력 경로만 정의(PUBLIC_API §D) |
| I2 환자 문구 출처·임상 검토 표시 | 문제L ML-16: `prompts/lora_*.system.txt`가 환자에게 가는 문장의 생성 지시인데 임상 검토 표시가 없다(문서·프롬프트에서 "임상" 0건) | 문제M SD-2: LoRA-B 정답 문장이 `human_review: pending`(미검수)인 채 학습 정답으로 통과한다(CR-006 4번 미결정) | 해당없음 |
| I3 실패 시 환자 화면 | 해당없음: 환자 경로가 아니다(레지스트리가 멈춰도 서비스는 영향 없음, boundary.md 장애 영향) | 해당없음 | OK: 값을 지어내지 않는 실패 규칙(HTTP.md I9), `DELIVERY_FAILED`면 직원 호출 화면(PUBLIC_API.md) |

## 문제 목록 (원인별 묶음)

심각도 H 0건, M 19건, L 19건. "자율"은 영역 에이전트가 사용자 결정 없이 고칠 수 있다는 뜻이다(계약·경계 변경은 헤드).

### M

| ID | 문제 | 근거 | 제안 수정 | 자율/결정 |
| --- | --- | --- | --- | --- |
| ML-1 | 서버에 소켓 timeout·동시 연결 상한·요청 속도 제한이 없다. 느린 클라이언트가 스레드와 `.tmp` 공간을 잡는다 | app.py:252-255, :196-202 | 연결 timeout, 최대 동시 게시 수, 게시 동시 1건 | 자율 |
| ML-2 | 디스크 가드가 없다. 게시는 최대 약 3배 공간(.tmp 본문, 해제본, 최종 복사)을 쓰고(app.py:196-203, registry.py:262) 여유를 확인하지 않는다. 학습 실행 전 확인도 없다(check_ready train_wrap.py:189-197, doctor의 WARN뿐 :296-302). runbook.md:90은 "df 점검은 쓰지 않는다"고 하여 코드와 충돌. FAULT_POLICY 13항(가득 차면 503, 경보) 미충족 | 같음 | 게시 전 여유 확인 후 UNAVAILABLE, 경보 기준 문서화, 문서·코드 통일 | 코드는 자율. 예산 값(WSL에서 df를 믿을지)은 헤드·사용자 결정 |
| ML-3 | 게시 중단 뒤 재시도하면 `list_versions`가 `['v1','v1']`(재현함, `_order.json`을 매니페스트보다 먼저 쓰고 중복 제거가 없음). 시작 때 `.tmp` 정리와 SIGTERM 처리 없음 | registry.py:269-273, :277-279, app.py:58-59, :271-275 | order에 이미 있으면 추가하지 않기, `_s_versions` 중복 제거, 시작 때 `.tmp` 비우기, SIGTERM에서 `shutdown` | 자율 |
| ML-4 | 핀·재현: `.venv`가 핀과 다른 라이브러리로 158건 통과(model-runtime 0.6.5, turn-engine 0.3.0 대 v0.7.2, v0.4.0), 범위 핀(`jsonschema>=4`, `pyyaml>=6`, 무핀 requirements-train.txt), 이미지 베이스 digest 없음, 전이 의존 미고정, `ssh-keyscan` 처음 만남 신뢰, 취약점 스캔 못 함 | requirements.txt, requirements-train.txt, Dockerfile:10-17 | `.venv`를 lock으로 다시 만들어 시험, 이미지 digest·전이 의존 고정, 호스트 키 고정, pip-audit 실행(설치 허락 필요) | 대부분 자율. 스캔 도구 설치는 허락 필요 |
| ML-5 | `package-adapters`가 계보를 검증하지 않는다. 데이터셋 ref는 입력 형식만 확인(attach.py:146-148), `dataset_manifest={"files": []}`라 문항 세트 계보가 비고(:124-127), 학습 기록(서버 스크립트 sha256, 데이터 파일 해시: train_wrap.py:219-241)은 패키지에 안 들어가고 `ext`는 `trainer: external`뿐. 기반 모델 revision은 `main`/`unspecified`(attach.py:94, configs/train.yaml:36) | 같음 | 학습 기록 파일을 입력으로 받아 해시를 대조하고 `ext."model-lab"`에 담기. 정식 필드 승격은 CR | 영역 안은 자율, 계약 필드는 헤드 |
| ML-6 | 게시 무결성은 자기일관성이다. 쓰기 토큰 하나로 임의 패키지 게시, `content_hash`는 게시자가 만든 값. 저장 뒤 변조는 읽을 때 탐지(registry.py:110,127)하나 파일 쓰기 권한자가 매니페스트와 해시를 함께 바꾸면 탐지 못 함. 게시자 행위 기록 없음 | registry.py:68-104 | 서명 또는 외부 해시 장부, 게시 로그에 토큰 역할·시각·해시 기록 | 로그는 자율, 서명 도입은 사용자·헤드 결정 |
| ML-12 | G06: 서버 코드와의 어긋남을 자동으로 알 수 없다. `args_verified`는 사람의 진술이고 시험은 서버 `run_config.json`의 스냅샷과만 대조(test_train_wrap.py:177). 설정에 서버 절대 경로(`/home/openit/taehyeon/...`)와 타인 홈(`~/taehyeon`)이 박혀 있다(configs/train.yaml:30,31). 어긋나면 서버에서 argparse 오류로 실패(PipelineError)할 뿐 사전 경고는 없다 | configs/train.yaml, train_wrap.py:267-271 | doctor가 서버 스크립트 sha256을 기록된 값과 비교해 경고(코드는 이미 해시를 기록 :222), 경로를 프로파일 변수로 분리 | 해시 비교는 자율. 서버 읽기는 헤드 몫(이 점검은 접속 금지) |
| ML-14 | 레지스트리는 평문 HTTP이고 운영 주소·인증·방화벽이 "정해지지 않았다"(runbook.md:36). 토큰은 정적(만료 없음), 회전은 재시작. 읽기 토큰 역할 이름이 자유롭다 | runbook.md:36, app.py:260-269 | TLS 종료 지점·주소 결정, 토큰 회전 절차 문서화 | 사용자·헤드 결정 |
| SD-1 | 게시기의 거부 사유에 입력 값이 섞인다(실측). jsonschema 메시지가 인스턴스를 담고(예 `{'a': 1} is not of type 'string'`), 사유 문자열이 `import_report.json`과 불변 매니페스트 `ext."synthetic-data".import.invalid_reasons`로 남는다. 문서는 "행 내용은 담지 않는다"고 적음 | schemas.py:21, importer.py:162-164,176,313-316, design.md 부록 A | 사유를 검증기 이름+스키마 경로로 정규화하고 값은 제외 | 자율 |
| SD-2 | 비식별 책임 공백. 게시기는 외부 파일을 `origin: SYNTHETIC`으로 고정 표기하고(importer.py:170-171) 환자 정보 검사·서약이 없으며, `human_review: pending`을 걸러내지 않는다(CR-006 4번). model-lab은 design.md:119에서 "데이터셋 쪽 책임"이라 적음. 아무도 검사하지 않는다 | importer.py:130-177, model-lab design.md:119 | 설정에 데이터 출처·비식별 서약 필드(필수)를 두고 매니페스트에 기록, pending 처리 정책 확정 | 서약 필드는 자율, 정책(pending 포함 여부, 검사 기준)은 사용자·헤드 결정 |
| SD-3 | 평가 누수 검사가 `scenario_id` 일치만 본다. 같은 발화가 다른 시나리오 ID로 TRAIN과 EVAL에 있어도 게시된다(실측). 게시기에는 중복 제거도 없다 | importer.py:270-277, store/base.py publish | 정규화한 입력 해시로 분할 간 중복 거부 또는 경고 | 검사 추가는 자율, 거부 기준은 결정 |
| SD-4 | `version`을 지정하고 `created_at`을 안 주면 같은 입력의 재실행이 CONFLICT(실측). `ALREADY_PUBLISHED`는 `version`이 없을 때만 판정 | importer.py:287,310,319-328 | 지정 버전도 저장된 `dataset_digest`와 비교해 ALREADY_PUBLISHED | 자율 |
| SD-7 | 핵심 경로 시험 15건 보류(생성 경로 종단·분리·재생성, test_job.py 8, test_units.py 7), 게시기는 실제 파일로 돈 적이 없고 행 형식이 추정이며 v2 의미 검사가 없다(G02, CR-006) | tests/conftest.py, importer.py:3-8 | 생성 경로 처분(삭제 또는 v2 이식) 결정, 실제 파일로 첫 게시 | 처분은 사용자·헤드 결정 |
| BC-1 | v2.0.2(88df21f) 뒤 6커밋이 `PUBLIC_API.md`와 HTTP.md를 바꿨다(새 엔드포인트 results, risk-signals, staff sessions, `subject_ref`, SSE heartbeat·resync, 409 TURN_IN_PROGRESS). 스키마·코드는 변경 없음(diff 확인)이나 버전·CHANGELOG·태그가 없다. 소비자는 어느 판이 기준인지 알 수 없다 | `git log v2.0.2..HEAD`, CHANGELOG.md 맨 위 | 문서 버전을 두거나 PATCH 태그와 CHANGELOG 항목 | 헤드 몫(자율 가능) |
| BC-2 | 오류 의미 불일치. CONVENTIONS §3은 retryable을 코드로 고정(errors.py:7-15, CONFLICT=false)하는데 PUBLIC_API는 409 TURN_IN_PROGRESS를 Retry-After 뒤 재시도하라고 한다. 401·429·502·504가 CONVENTIONS §9 표에 없는데 PUBLIC_API는 401·429를 정의하고 클라이언트는 429를 매핑하지 않아 UNAVAILABLE로 떨어지며 `Retry-After`를 읽지 않는다(_http.py:35-36,118-137). FAULT_POLICY 6항의 `UPSTREAM_UNAVAILABLE`은 BoundaryError 열거(스키마 enum, errors.py)에 없다 | CONVENTIONS.md §3·§9, PUBLIC_API.md 오류 표, FAULT_POLICY.md 6항 | 상태 코드 표를 PUBLIC_API와 합치고, `details.reason` 기반 재시도 의미와 `Retry-After`를 규약에 적고 클라이언트가 읽게 하기 | 계약 변경이라 헤드 결정 |
| BC-3 | HTTP.md 공통 절과 CONVENTIONS §6·§9가 "토큰은 환경 변수로 받는다"이고 `<이름>_TOKENS` 형식만 적어 D84(`NAME_FILE`)와 충돌한다. 영역이 문서를 따르면 규칙을 어기게 된다 | HTTP.md 공통, CONVENTIONS.md §6, §9 | `NAME_FILE` 우선으로 문구 정정 | 헤드 몫(자율 가능) |
| BC-4 | 하위 호환 규칙(CONVENTIONS §1.2)을 기계가 검사하지 않는다. `verify.py`는 예시 통과·거부만 본다. 수동 검토 결과: 2.0.0은 MAJOR로 처리, 2.0.1은 `ActionExtraction` properties 순서만 바꿈(의미 동일), 2.0.2는 코드만 추가하여 규칙 위반은 못 찾았다 | verify.py:1-3, `git diff --stat v2.0.0 v2.0.1` | 이전 태그 스키마와 비교해 필수 추가·삭제·열거 축소를 잡는 검사 | 자율(헤드 소유 리포) |
| BC-5 | 태그 불변성 규칙이 문서에 없다. v1.3.0~v1.3.3은 경량 태그(나머지는 주석 태그), 서명 태그 없음, 로컬 reflog에 이동 흔적은 없으나 원격 상태는 접속하지 않아 확인 못 함 | `git cat-file -t`, README §4 | "게시된 태그는 이동·삭제하지 않는다"를 CONVENTIONS에 쓰고 새 태그는 주석(가능하면 서명) | 규칙 문서화는 헤드 몫 |
| X-1 | I2에 HTTP 면이 없다(HTTP.md:25). model-lab은 `DATASET_ROOT`의 파일 배치를 직접 읽고(file_dataset_store.py, runbook.md:36) synthetic-data 문서가 같은 배치를 약속한다(boundary.md §1, runbook GPU 절). D49("이웃의 저장소 볼륨을 공유하지 않는다")와 맞지 않는다. 알려진 CR-L004 | 같음 | I2 HTTP 면 정의 또는 예외를 결정에 기록 | 헤드·사용자 결정 |

(위 표는 M 19건이고 요약 절의 목록과 같다.)

### L

| ID | 문제 | 근거 | 제안 | 자율 |
| --- | --- | --- | --- | --- |
| ML-7 | `eval_report` 바이트를 `EvaluationReport`로 검증하지 않음, 게시 200/201 판정 경쟁 | app.py:214-221, registry.py:84-86 | 서버에서 스키마 검증, 판정을 락 안으로 | 자율 |
| ML-8 | 알 수 없는 내부 오류를 재시도 가능한 503으로 응답 | app.py:229-231 | 재시도 불가 응답 코드는 계약에 없음. CR | 헤드(CR) |
| ML-9 | `fetch_dataset`가 매니페스트 `path`의 `..`를 검사하지 않음 | datasets.py:45-47 | 경로 검사 | 자율 |
| ML-10 | 비정본 학습기가 `torch.load`를 `weights_only` 없이 사용 | trainers/hf.py:161-162 | `weights_only=True` | 자율 |
| ML-11 | 문서 어긋남: model-runtime v0.7.0 표기, 시험 156건, 버전 0.1.0 대 0.2.3, df 점검 서술 충돌 | README.md:69,73,113-115, boundary.md:3,22, runbook.md:90 | 정정 | 자율 |
| ML-13 | `run-once` 동시 실행 방어가 없음 | runbook.md:85 | run 디렉터리 락 | 자율 |
| ML-15 | 개인정보 위치 목록 없음, `runs/_server_ds` 0644(18MB), 보존·삭제 정책 없음 | runs/_server_ds | 목록 문서화, 권한 0600 | 자율 |
| ML-16 | `prompts/*.txt`의 임상 검토 표시 없음 | prompts/ | 출처·검토 상태 표시 | 임상 검토 여부는 사용자 결정 |
| ML-17 | 로그 구조화·상관 ID, 지표·경보, 용량·처리량 측정, 백업·복원 문서, 파일 배치 버전 표시 없음 | app.py:101-102 | 문서·로그 보강 | 자율 |
| SD-5 | 입력 크기·행 수 상한 없음, 사유 종류 무제한, 보고서 비원자 쓰기, 보존·백업·용량 문서 없음 | importer.py:195,252,346 | 상한·원자 쓰기·문서 | 자율 |
| SD-6 | 입력 파일 심볼릭 링크를 따라감(설정이 신뢰 경계) | importer.py:190 | 링크 거부 | 자율 |
| SD-8 | lock의 jsonschema 4.10.3(model-lab 4.26.0과 다름), 시험이 형제 폴더·작업 트리 의존, 취약점 스캔 못 함 | requirements.lock, tests/conftest.py:14-15 | 버전 정렬(헤드 기준표) | 자율 |
| SD-9 | 문서 어긋남: runbook GPU 절 토큰 서술(D84 충돌), README의 시험 개수·CR 범위, 버전 불일치 | runbook.md, README.md §4,§7 | 정정 | 자율 |
| SD-10 | `fsync` 없음, `seq` 경쟁 | file_store.py:48-56 | fsync, 락 | 자율 |
| BC-6 | 클라이언트가 평문 `http://` 허용, `RefResolver` 폐기 예고(_http.py:65, 소비 영역 시험 경고 787건), `jsonschema>=4.10` 상한 없음 | _http.py:93-96, pyproject.toml | `referencing`으로 이전, 상한 | 헤드 몫 |
| BC-7 | METRICS.md가 v1 용어(알려진 D-C) | METRICS.md:11,24 | 갱신 | 헤드 |
| BC-8 | `read_secret`이 파일 권한을 확인하지 않음 | secrets.py:20-27 | 0600 경고 | 헤드 |
| BC-9 | 두 번째 환경 검증 없음, `verify.py`의 TurnTrace 검증이 survey-service 부재 시 건너뜀 | README §4, verify.py:48-54 | 새 venv에서 실행 | 자율 |
| X-2 | 한글 유니코드 정규화(NFC) 규칙이 어디에도 없다 | grep `normalize|NFC` 0건 | 규약에 한 줄 | 헤드 결정 |

## FAULT_POLICY와의 대조

| 원칙 | model-lab | synthetic-data | boundary-contracts |
| --- | --- | --- | --- |
| 4 의존 무한 대기 금지 | 서버는 의존이 없고 클라이언트는 timeout 있음. 서버 소켓 timeout 없음(ML-1) | 이웃 호출 timeout 10초 | 클라이언트 timeout 있음 |
| 5 healthz/readyz | 지켜짐(readyz는 저장소 확인) | 해당 없음 | 해당 없음 |
| 7 Retry-After·지터 | 해당 없음 | 종료 코드 75로 스케줄러에 위임 | 클라이언트가 `Retry-After`를 읽지 않음(BC-2) |
| 9 인증 실패 가시화 | 403 즉시 | 3(재시도 불가)으로 종료 | 401·403 모두 PERMISSION_DENIED로 매핑 |
| 12 재시작 후 정상화 | 부분(ML-3) | 지켜짐 | 해당 없음 |
| 13 디스크 가득 | 미충족(ML-2) | 저장소 쓰기 실패는 UNAVAILABLE(file_store.py:65-66)이나 사전 경보 없음 | 해당 없음 |

## 이 점검이 읽지 못한/얕게 본 곳

- 읽지 못함: 세 영역의 `docs/rules/`, `docs/change-requests/` 본문(synthetic-data CR-006만 읽음), model-lab `docs/STATUS.md` 후반·`docs/base-model-comparison.md`·`CHANGELOG.md`, `head/docs/DECISIONS.md`, `OPEN_GAPS.md`. boundary-contracts에는 CLAUDE.md와 docs/brief.md가 없다(README가 인정).
- 얕게 봄: model-lab `pipeline.py`, `transform.py`, `evaluate.py`, `metrics.py`, `regression.py`, `backends/`, `trainers/hf.py`(위험 패턴 grep과 일부 발췌만, 단계 간 상태 전이·평가 `raw_errors` 내용 미확인), synthetic-data의 생성 경로(`scenario.py`, `generators/`, `noise.py`, `labeler.py`, v1 내용이라 보류), `seeds.py` 일부, boundary-contracts `clients/{models,ops,questions,releases,runtime}.py`와 `conformance/servers.py`(공통부 `_http.py`만 정독), 스키마 28개 개별 내용(ModelPackageManifest·DatasetManifest·BoundaryError·_common만 확인).
- 돌리지 않음: pip-audit·컨테이너 스캔(설치 금지), 이미지 빌드·스모크(Docker 사용 안 함), 핀 환경(lock 그대로)에서의 시험(이 `.venv`는 핀과 다름), GPU 관련 전부, 학습 서버 코드 대조(접속 금지), 원격 Git 태그 상태(외부 접속 금지), 실제 학습 데이터로 게시기 실행.
- 판단 한계: 모든 시험 결과는 이 PC 한 환경 값이다. model-registry의 부하·느린 클라이언트 거동, 동시 게시 경쟁은 코드 읽기로 판단했고 직접 재현하지 않았다. 직접 재현한 것은 ML-3(중복 버전), SD-1(값 포함 사유), SD-3(누수 통과), SD-4(CONFLICT) 네 가지다.
- 이 파일의 숫자는 아래 스크립트로 세었다(칸의 첫 낱말 기준). 같은 칸에 문제가 여럿이면 가장 무거운 하나로 센다.
