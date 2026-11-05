#!/usr/bin/env python3
"""영역 리포의 스키마 배치 규칙(CONVENTIONS, 2026-11-05)을 기계로 센다.

규칙:
  schemas/          그 영역 안에서만 도는 스키마. 담당자가 상의 없이 바꿔도 된다.
  types/contract/   계약(boundary-contracts)에서 생성한 것만 둔다. 바꾸지 않는다(바꾸려면 헤드에 변경 요청).
  계약 스키마의 사본은 어디에도 두지 않는다(계약은 boundary_contracts 패키지에서 읽는다).
센다(모두 0 이어야 통과):
  A schemas/ 에 계약 스키마와 이름이 같은 파일
  B schemas/ 에 계약 스키마와 칸 구조(properties 이름 집합 + required)가 같은 파일(이름을 바꾼 사본)
  C types/contract/ 밖에 계약 스키마와 이름이 같은 생성 타입 파일(.py .ts .cjs .d.ts)
변이 확인: --self-test 가 사본 하나를 넣은 가짜 리포에서 A·B·C 가 각각 잡히는지 본다.
종료 코드: 0 통과, 1 위반, 2 사용 오류. 값은 출력하지 않는다(파일 경로와 스키마 이름만).
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

WS = pathlib.Path(__file__).resolve().parents[2]
BC = WS / "boundary-contracts/boundary_contracts/schemas"
AREAS = [a["name"] for a in (lambda d: d["areas"] if isinstance(d, dict) else d)(json.loads((WS / "head/shared/areas.json").read_text()))]
SKIP = re.compile(r"(^|/)(tests?|fixtures|examples?|docs|build|node_modules|\.venv)(/|$)|example")
GEN = re.compile(r"\.(py|ts|cjs|d\.ts)$")


def shape(s):
    """사본 판정 열쇠: 칸 이름·각 칸의 정의·required·additionalProperties 가 모두 같으면 사본이다(설명문은 뺀다).
    칸 이름만 같고 조건을 더하거나 바꾼 내부 스키마(계약을 받아들이는 조건 등)는 사본이 아니다."""
    if not isinstance(s, dict) or not isinstance(s.get("properties"), dict) or len(s["properties"]) < 2:
        return None   # 칸이 2개 미만인 스키마는 모양만으로 사본이라 할 수 없다
    def strip(n):
        if isinstance(n, dict):
            return {k: strip(v) for k, v in n.items() if k not in ("description", "title", "$id", "$comment", "examples")}
        return [strip(x) for x in n] if isinstance(n, list) else n
    return json.dumps({k: strip(s.get(k)) for k in ("properties", "required", "additionalProperties")}, sort_keys=True)


def contract():
    names, shapes = set(), {}
    for f in BC.glob("*.schema.json"):
        n = f.name[: -len(".schema.json")]
        names.add(n)
        sh = shape(json.loads(f.read_text(encoding="utf-8")))
        if sh:
            shapes[sh] = n
    return names, shapes


def scan(root: pathlib.Path, names, shapes, label):
    r = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
    files = [p for p in r.stdout.splitlines() if not SKIP.search(p)] if r.returncode == 0 else []
    bad = []
    for p in files:
        base = p.rsplit("/", 1)[-1]
        stem = re.sub(r"\.(schema\.json|json|d\.ts|ts|py|cjs)$", "", base)
        in_schemas = re.search(r"(^|/)schemas/[^/]+\.json$", p) and not p.startswith("schema/")
        if in_schemas:
            if stem in names:
                bad.append(f"A {label}/{p}: 계약 {stem} 과 이름이 같다")
            try:
                sh = shape(json.loads((root / p).read_text(encoding="utf-8")))
            except ValueError:
                sh = None
            if sh and sh in shapes and shapes[sh] != stem:
                bad.append(f"B {label}/{p}: 계약 {shapes[sh]} 과 칸 구조가 같다(사본)")
        elif GEN.search(base) and stem in names and "/types/" in "/" + p and "/types/contract/" not in "/" + p:
            bad.append(f"C {label}/{p}: 계약 {stem} 의 생성 타입이 types/contract/ 밖에 있다")
    return len(files), bad


def self_test():
    names, shapes = {"Foo"}, {shape({"properties": {"a": {}, "b": {}}, "required": ["a"]}): "Foo"}
    with tempfile.TemporaryDirectory() as t:
        d = pathlib.Path(t)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        (d / "schemas").mkdir(); (d / "src/types").mkdir(parents=True); (d / "src/types/contract").mkdir()
        (d / "schemas/Foo.json").write_text('{"properties":{"x":{},"y":{}}}')
        (d / "schemas/Bar.json").write_text('{"properties":{"a":{},"b":{}},"required":["a"],"description":"이름만 바꾼 사본"}')
        (d / "schemas/Own.json").write_text('{"properties":{"p":{},"q":{}}}')
        (d / "src/types/Foo.ts").write_text("")
        (d / "src/types/contract/Foo.ts").write_text("")
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        _, bad = scan(d, names, shapes, "t")
        kinds = sorted(b[0] for b in bad)
        ok = kinds == ["A", "B", "C"]
        print("self-test", "통과" if ok else f"실패: {bad}")
        return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    trees = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    names, shapes = contract()
    allbad, total = [], 0
    for a in AREAS:
        if a in ("boundary-contracts", "head"):
            continue
        root = pathlib.Path(trees.get(a, WS / a))
        if not (root / ".git").exists():
            continue
        n, bad = scan(root, names, shapes, a)
        total += n
        allbad += bad
    print(f"영역 파일 {total}개, 위반 {len(allbad)}건 (A 이름 같은 사본, B 구조 같은 사본, C types/contract 밖 계약 타입)")
    for b in allbad:
        print(b)
    return 1 if allbad else 0


if __name__ == "__main__":
    sys.exit(main())
