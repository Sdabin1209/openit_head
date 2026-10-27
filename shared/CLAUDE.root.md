# 워크스페이스 공통 규칙

이 폴더는 문진 시스템 프로젝트의 워크스페이스다. 아래 하위 폴더는 각각 독립된 git 리포지토리이며, 이 폴더 자체는 git 리포지토리가 아니다. 이 파일은 `head/shared/CLAUDE.root.md`의 링크이며 모든 세션이 읽는다. 모든 영역에 해당하는 규칙만 둔다.

- `head/`: 설계 문서, 결정 기록, 영역 브리프
- `survey-service/schema/`: 문진 스키마. 문진 서비스 영역의 데이터 스키마이며 survey-service 리포지토리에 포함된다
- `boundary-contracts/`: 영역 사이 계약. 헤드 소유
- 그 밖의 폴더: 영역 리포지토리 또는 공유 라이브러리

## 모든 세션의 규칙

- 자기 리포지토리 안에서만 일한다. 다른 폴더를 수정하지 않는다. 읽는 것도 `../survey-service/schema`와 `../boundary-contracts`(둘 다 읽기 전용)만 허용한다. survey-service는 자기 `schema/`를 소유한다. 이웃 영역의 데이터는 그 영역이 배포한 읽기 SDK로만 읽는다.
- 문진 스키마와 `boundary-contracts`를 직접 수정하지 않는다(survey-service는 자기 `schema/`를 수정할 수 있다). 부족하거나 틀렸다고 판단하면 `docs/change-requests/`에 변경 요청을 써서 헤드에게 넘긴다.
- 영역 리포지토리끼리 코드를 가져오지 않는다. 의존할 수 있는 것은 문진 스키마, boundary-contracts, turn-engine, model-runtime과 이웃의 SDK뿐이다.
- 읽지 못한 것이나 확인하지 못한 것을 확인한 것처럼 쓰지 않는다. 확인한 것, 제안, 미정을 구분해서 말한다.
- 수용 테스트와 계약 검증을 통과하기 전에 완료했다고 말하지 않는다.
- 한국어로 답한다. 질문은 한 번에 하나씩 한다.
- 세션은 새 컨텍스트로 시작한다. 맥락은 이 리포지토리의 `CLAUDE.md`와 `docs/brief.md`에 있다.

## 컨테이너와 개발 (D22)

- 개발은 컨테이너 밖에서 한다(가상환경, 이웃 영역의 메모리 구현). 컨테이너는 개발 환경이 아니라 매 변경마다 확인하는 산출물이다.
- 서비스를 가진 영역은 자기 리포지토리에 `Dockerfile`을 두고, 변경을 완료했다고 말하기 전에 이미지가 빌드되고 `/healthz`에 응답하는 것을 확인한다(스모크 테스트 스크립트를 리포지토리에 둔다). 데이터베이스처럼 앱 밖의 의존이 필요하면 `compose.dev.yaml`로 그것만 띄운다.
- 이웃 영역이 필요하면 그 영역의 메모리 구현(가짜 SDK)으로 대신해, 다른 영역 없이 혼자 시험할 수 있어야 한다.
- 이미지는 다음을 지킨다: 설정은 환경 변수로 받는다. **비밀(토큰·salt 등)은 환경 변수가 아니라 파일로 받는다(D84): `NAME_FILE`로 경로를 받고 `boundary_contracts.read_secret(NAME)`으로 읽는다. 환경 변수 `NAME`은 개발·시험용 호환일 뿐이다. 비밀 값은 이미지, 리포지토리, 설정 파일, 로그, `/readyz`, 오류 응답에 넣지 않는다.** 로그는 표준 출력으로 낸다. root가 아닌 사용자로 실행한다. HTTP 서비스는 `/healthz`(살아 있음)와 `/readyz`(의존 준비됨)를 둔다. 이미지 라벨에 커밋, 소비하는 계약 버전, turn-engine·model-runtime 버전을 기록한다.
- `boundary-contracts`는 태그로 설치한다(현재 기준은 `deploy/scripts/lib.sh`의 `BOUNDARY_TAG`, 예: `v2.0.2`): `pip install git+ssh://git@github.com/Sdabin1209/openit_boundary-contracts.git@<태그>`. 스키마는 패키지에 들어 있으므로 `load_schema`, `validator`를 쓰고 복사본을 만들지 않는다.
- 라이브러리와 SDK는 Git 태그로 설치하고, 이미지를 빌드할 때 태그를 고정한다. 의존 버전은 잠금 파일로 고정한다.
- 스모크 시험은 고정 포트를 쓰지 않는다. 여러 영역이 같은 서버에서 동시에 돌리면 충돌한다. 호스트 포트를 Docker가 배정하게 하거나(`-p 127.0.0.1::8080`) `SMOKE_PORT` 기본값을 빈 포트로 고른다. 컨테이너 이름과 이미지 태그에는 리포지토리 이름을 넣는다.
- 이미지 라벨 키는 `io.openit.service`, `io.openit.revision`, `io.openit.contracts.boundary`, `io.openit.contracts.survey-schema`, `io.openit.turn-engine`, `io.openit.model-runtime`로 통일한다(D50).
- 영역 사이 호출은 `boundary-contracts/HTTP.md`의 HTTP API로 한다. 서버는 소유 영역이, 클라이언트는 `boundary_contracts.clients`가 맡는다. 이웃의 저장소 볼륨을 공유하지 않는다(D49).
- 이미지는 CI에서 빌드해 digest를 게시한다. 서버 안의 로컬 레지스트리에 올리고 digest를 deploy에 제출한다(D24).
- 문진 스키마(`../survey-service/schema`) 변경은 survey-service가 반영한다(D21). 다른 영역은 변경 요청을 낸다.

## 커밋 (D37)

- 작업 단위가 끝날 때마다 자기 리포지토리에 커밋한다(설계서 한 편, 기능 하나, 시험 통과 한 묶음). 커밋 없이 오래 두지 않는다. 세션을 끝내기 전에는 반드시 커밋한다.
- 작성자는 `git -c user.name=Sdabin1209 -c user.email=99588729+Sdabin1209@users.noreply.github.com commit`으로 한다. 개인 이메일을 쓰지 않는다.
- push는 헤드의 허락을 받아 한다(사용자가 헤드에게 위임, D41). 커밋하고 시험이 통과한 상태에서 헤드에게 알리면 헤드가 허락한다. 허락 없이 push하지 않고, 강제 push(`--force`)는 하지 않는다. 헤드는 push를 허락하기 전에 시험 결과와 커밋 작성자를 확인한다.
- Python 의존은 리포지토리의 가상환경(`python3 -m venv .venv`)에 설치하고 `.venv/`는 커밋하지 않는다.

## 자동화 (D39)

- 영역 사이의 자동 연결은 직접 호출이 아니라 **저장소를 보고 일하는 잡**으로 한다. 각 영역은 자기 잡을 한 번 실행하는 명령(`run-once` 같은 것)과 설정 파일을 갖고, 같은 입력에 대해 같은 결과를 내며 여러 번 실행해도 안전해야 한다(멱등).
- 잡을 언제 돌리는지는 deploy의 스케줄러가 정한다. 영역은 스스로 다른 영역을 깨우지 않는다.
- 모델의 성능 시행착오는 설정으로 바꾸며 반복한다. 파이프라인을 손으로 이어 치는 방식은 두지 않는다.
