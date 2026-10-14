# openit 문진 시스템: 헤드

이 리포지토리(`openit_head`)가 워크스페이스 전체의 기준이다. 설계 문서, 결정 기록, 영역 브리프, 공통 규칙, 워크스페이스 구성을 가진다. 영역의 실제 동작은 각 영역 리포지토리에 있다.

## 워크스페이스

```
<루트>/                     git 리포지토리가 아니다
├── CLAUDE.md               head/shared/CLAUDE.root.md의 링크(setup.sh가 만든다)
├── head/                   이 리포지토리
├── boundary-contracts/     영역 사이 계약(헤드 소유)
├── turn-engine/            공유 라이브러리: 판단 로직
├── model-runtime/          공유 라이브러리: 모델 로딩·추론
├── survey-service/         영역 1. schema/(문진 스키마)를 포함
├── question-authoring/     영역 2
├── synthetic-data/         영역 3
├── model-lab/              영역 4
├── release-gate/           영역 5
├── ops-feedback/           영역 6
└── deploy/                 단일 서버 배포
```

리포지토리는 11개이고 이름은 `Sdabin1209/openit_<디렉터리 이름>`이다. 목록과 원격은 `workspace.yaml`에 있다.

## 설치

```
git clone git@github.com:Sdabin1209/openit_head.git <루트>/head
bash <루트>/head/setup.sh
```

`setup.sh`는 루트의 `CLAUDE.md` 링크를 만들고 나머지 리포지토리를 clone한다. 이미 있는 것은 건드리지 않고, 받지 못한 것은 목록으로 알린다. Windows에서 링크가 만들어지지 않으면 복사로 대신한다.

## 헤드 세션

```
cd <루트>/head
claude --add-dir ../boundary-contracts --add-dir ../survey-service/schema
```

`--add-dir`로 추가한 디렉터리의 CLAUDE.md는 자동으로 읽히지 않는다. 헤드는 `head/CLAUDE.md`의 순서대로 `docs/STATUS.md`, `docs/HANDOFF.md`, `docs/STRUCTURE.md`, `docs/DECISIONS.md`를 읽고 시작한다. 세션을 끝낼 때 `docs/STATUS.md`를 갱신한다.

## 영역 세션

```
cd <루트>/<영역 디렉터리> && claude
```

Claude Code는 시작한 디렉터리에서 위로 올라가며 CLAUDE.md를 읽으므로, 루트의 공통 규칙이 모든 영역에 따라온다. 영역 에이전트는 자기 리포지토리의 `CLAUDE.md`와 `docs/brief.md`로 시작한다. 새 영역은 `head/scripts/new-area.sh <이름>`으로 만든다.

## 어디에 무엇이 있나

| 찾는 것 | 위치 |
| --- | --- |
| 구조의 기준 | `docs/STRUCTURE.md` |
| 확정·열린 결정 | `docs/DECISIONS.md` |
| 진행 상태와 다음 작업 | `docs/STATUS.md` |
| 영역이 받고 내는 것 | `../boundary-contracts/INTERFACES.md`, `CONVENTIONS.md` |
| 영역 브리프 | `briefs/<영역>.md` (각 영역의 `docs/brief.md`로 복사됨) |
| 모든 세션의 공통 규칙 | `shared/CLAUDE.root.md` |

## 알아 둘 것

- 첫 커밋과 원격 설정은 사용자가 한다. 헤드는 영역 리포지토리의 내용을 수정하지 않는다.
- 설계서 전체(`ARCHITECTURE_FULL.md`)는 리포지토리에 없다. 필요하면 `docs/`에 넣는다.
