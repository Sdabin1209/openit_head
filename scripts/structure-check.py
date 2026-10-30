#!/usr/bin/env python3
"""영역 구조 검사(DESIGN.md 6절, D117). 모든 영역을 같은 기준으로 본다. 읽기만 한다.
사용: python3 head/scripts/structure-check.py [영역 ...]   (비우면 areas.json의 코드 영역 전부)
종료 코드: 0 전부 통과, 1 위반 있음.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
NON_AREAS = {"head", "boundary-contracts", "link"}   # 영역이 아닌 헤드 소유물(문서·계약·통신 기반 라이브러리)
HTTP_PY = re.compile(r"^\s*(from|import)\s+(openit_link|boundary_contracts\.clients|urllib\.request|http\.client|http\.server|requests|waitress|wsgiref)\b", re.M)
HTTP_TS = re.compile(r"\bfetch\s*\(|from\s+['\"](node:)?http['\"]")
ENTRY = re.compile(r"(^|/)(__main__|main|app|server|config|settings|migrate|cli|index)\.(py|ts)$|(^|/)migrations?/")


def areas():
    d = json.loads((ROOT / "head" / "shared" / "areas.json").read_text(encoding="utf-8"))["areas"]
    names = [a["name"] if isinstance(a, dict) else a for a in d]
    return [n for n in names if n not in NON_AREAS and (ROOT / n / ".git").exists()]


def files(repo):
    out = subprocess.run(["git", "-C", str(ROOT / repo), "ls-files"], capture_output=True, text=True).stdout.split("\n")
    return [f for f in out if f and "node_modules/" not in f]


def check(repo):
    fs = files(repo)
    code = [f for f in fs if f.endswith((".py", ".ts")) and not re.search(r"(^|/)(tests?|test)/|(^|/)test_|\.test\.ts$|(^|/)scripts/|\.d\.ts$|(^|/)conftest\.py$", f)]
    bad = []
    dirs = {name: [f for f in fs if f"/{name}/" in f"/{f}"] for name in ("schemas", "types", "components", "wiring")}
    for name, got in dirs.items():
        if not got:
            bad.append(f"{name}/ 없음")
    comps = [f for f in code if "/components/" in f"/{f}"]
    comp_names = {pathlib.Path(f).stem for f in comps}
    for f in comps:
        t = (ROOT / repo / f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?:from|import)\s+[\w.]*components[./](\w+)|from\s+['\"][./]*(?:components/)?(\w+)['\"]", t):
            other = m.group(1) or m.group(2)
            if other in comp_names and other != pathlib.Path(f).stem:
                bad.append(f"{f}: 다른 컴포넌트 {other}를 import")
    for f in code:
        t = (ROOT / repo / f).read_text(encoding="utf-8", errors="replace")
        uses = HTTP_PY.search(t) if f.endswith(".py") else HTTP_TS.search(t)
        if uses and not pathlib.Path(f).name.startswith("link_") and not ENTRY.search(f):
            bad.append(f"{f}: 통신 컴포넌트(link_*) 밖에서 HTTP")
    for f in code:
        if not re.search(r"/(components|wiring|types)/", f"/{f}") and not ENTRY.search(f) and not f.endswith("__init__.py"):
            bad.append(f"{f}: components/·wiring/·types/·진입점 어디에도 속하지 않음")
    schemas = [f for f in fs if re.search(r"(^|/)schemas/[^/]+\.json$", f)]
    for s in schemas:
        stem = pathlib.Path(s).name.replace(".schema.json", "").replace(".json", "")
        ex = [f for f in fs if re.search(rf"schemas/examples/{re.escape(stem)}\.(valid|invalid)", f)]
        if not any(".valid" in e for e in ex) or not any(".invalid" in e for e in ex):
            bad.append(f"{s}: 통과·거부 예시가 모두 있지 않음")
    return bad


def main(argv):
    targets = argv or areas()
    total = 0
    for r in targets:
        bad = check(r)
        total += len(bad)
        print(f"{r}: {'통과' if not bad else f'위반 {len(bad)}건'}")
        for b in bad[:15]:
            print(f"  - {b}")
        if len(bad) > 15:
            print(f"  ... 그 밖 {len(bad) - 15}건")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
