#!/usr/bin/env python3
"""영역 코드가 이웃 리포의 작업 폴더를 직접 읽는 곳을 센다(2026-11-05, codex 보고 deploy test_gen_db_secrets 7건 실패에서).
규칙: 라이브러리(boundary-contracts, link, model-runtime, survey-service 의 문진 스키마)는 고정 태그로 받는다. 설치된 패키지에서 읽거나,
      리포에서 꺼낼 때는 태그로 꺼낸다(git archive/show/ls-tree/rev-parse <태그>, 환경 변수 → 옆 폴더 → 원격 태그 순서).
위반: 주석이 아닌 줄이 이웃 리포 경로를 쓰는데, 같은 줄이나 앞뒤 2줄에 태그로 꺼내는 git 명령이나 위치 결정 함수(dep_repo, depRepo, resolveRepo)가 없다.
대상 아님: deploy 의 워크스페이스 점검 도구(check-all 의 consistency_check, test_e2e_enum_constants: 워크스페이스 전체를 읽는 것이 그 일이다),
          영역의 개발용 설정 예시(configs/*.json: 공통 규칙이 허용하는 ../survey-service/schema 읽기 전용), 허용 목록을 정의하는 test_no_neighbour_files.py. 문서 문자열과 주석은 설명이다.
변이 확인(2026-11-05): model-lab f02cc82~1 의 tests/test_attach.py(옆 폴더 model-runtime 프로파일)를 잡는다.
종료 코드: 0 위반 없음, 1 있음."""
import pathlib, re, subprocess, sys
WS = pathlib.Path(__file__).resolve().parents[2]
AREAS = ["survey-service", "question-authoring", "ops-feedback", "release-gate", "model-lab", "synthetic-data", "model-runtime", "kiosk-frontend", "admin-console", "platform", "link", "deploy"]
TREES = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
NEIGH = re.compile(r'(\.\./+)+(boundary-contracts|link|model-runtime|survey-service)\b|parents?\[\d\][^\n]{0,40}"(boundary-contracts|link|model-runtime|survey-service)"|(ROOT|WS|here|HERE|SRC)[^\n]{0,20}parent[^\n]{0,40}"(boundary-contracts|survey-service|link|model-runtime)"')
OK = re.compile(r'\b(archive|show|ls-tree|rev-parse)\b|dep_repo|depRepo|resolveRepo|_REPO\b|--build-context')
SKIP_FILE = re.compile(r'(^|/)(docs/|CHANGELOG|[^/]*\.md$)|consistency_check\.py$|test_e2e_enum_constants\.py$|test_no_neighbour_files\.py$|^configs/[^/]*\.json$|/build/|\.gen\.cjs$|validators\.cjs$|contract-validators\.cjs$')
COMMENT = re.compile(r'^\s*(#|//|\*|/\*|"""|\'\'\')')
bad = []
for a in AREAS:
    root = pathlib.Path(TREES.get(a, WS / a))
    files = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True).stdout.splitlines()
    for f in files:
        if SKIP_FILE.search(f) or not re.search(r'\.(py|sh|mjs|js|ts|json|ya?ml|toml|cfg)$|Dockerfile$', f):
            continue
        try:
            lines = (root / f).read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        in_doc = False
        for i, l in enumerate(lines):
            q = l.count('"""') + l.count("'''")
            was = in_doc
            if q % 2 == 1:
                in_doc = not in_doc
            if was or (q and not was):   # 문서 문자열 안(시작 줄 포함)은 설명이다
                continue
            if not NEIGH.search(l) or COMMENT.match(l):
                continue
            code = l.split(" # ")[0].split(" // ")[0]
            if not NEIGH.search(code):
                continue   # 줄 끝 주석에만 있다
            ctx = "\n".join(lines[max(0, i - 2): i + 3])
            if OK.search(ctx):
                continue
            bad.append(f"{a}/{f}:{i + 1}: {l.strip()[:150]}")
print(f"이웃 리포 작업 폴더를 직접 읽는 곳 {len(bad)}건")
for b in bad:
    print(b)
sys.exit(1 if bad else 0)
