#!/usr/bin/env python3
"""스키마 형식(format) 강제를 실행 없이 센다(2026-11-06).

왜: jsonschema 는 format_checker 를 주지 않거나, 줘도 형식별 검증기 패키지가 설치돼 있지 않으면 date-time·uri 같은 형식을 조용히 통과시킨다.
계약 3.5.0 은 boundary_contracts.format_checker(schema) 를 둔다: 스키마에 쓴 형식의 검증기가 없으면 검증기를 만들지 않고 실패한다.
센다(모두 0 이어야 통과):
  A 제품 코드(tests 밖)에서 jsonschema 검증기 클래스를 만들면서 format_checker= 를 주지 않은 곳
  B format_checker= 로 jsonschema.FormatChecker() 를 직접 준 곳(검증기 패키지가 없으면 조용히 건너뛴다) — boundary_contracts.format_checker 를 써야 한다
  C 그 영역의 잠금 파일에 rfc3339-validator·rfc3986-validator 가 없는 곳(date-time·uri 검증기)
변이 확인: --self-test 가 A·B 를 각각 넣은 가짜 파일에서 잡히는지 본다.
종료 코드: 0 통과, 1 위반.
"""
import ast
import pathlib
import re
import subprocess
import sys
import tempfile

WS = pathlib.Path(__file__).resolve().parents[2]
AREAS = ["boundary-contracts", "link", "model-runtime", "survey-service", "question-authoring", "ops-feedback", "release-gate",
         "model-lab", "synthetic-data", "platform", "deploy", "head"]
VALIDATORS = {"Draft202012Validator", "Draft7Validator", "Draft4Validator", "Draft6Validator", "Draft201909Validator"}
LOCK = re.compile(r"(^|/)requirements[^/]*\.(lock|txt)$")
NEED = ("rfc3339-validator", "rfc3986-validator")


def calls(src: str):
    """(줄, 종류) — 검증기 생성 호출마다 format_checker 인자 상태."""
    out = []
    for n in ast.walk(ast.parse(src)):
        if not isinstance(n, ast.Call):
            continue
        name = n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else None)
        if name not in VALIDATORS:
            continue
        kw = {k.arg: k.value for k in n.keywords}
        fc = kw.get("format_checker")
        if fc is None:
            out.append((n.lineno, "A"))
        elif isinstance(fc, ast.Call) and (getattr(fc.func, "attr", None) == "FormatChecker" or getattr(fc.func, "id", None) == "FormatChecker"):
            out.append((n.lineno, "B"))
        elif isinstance(fc, ast.Attribute) and fc.attr == "FORMAT_CHECKER":
            out.append((n.lineno, "B"))
    return out


def scan(root: pathlib.Path, label: str):
    r = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
    files = r.stdout.splitlines() if r.returncode == 0 else []
    bad = []
    for p in files:
        if not p.endswith(".py") or re.search(r"(^|/)(tests?|fixtures)(/|$)|(^|/)test_[^/]*\.py$", p):
            continue
        try:
            src = (root / p).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not any(v in src for v in VALIDATORS):
            continue
        for line, kind in calls(src):
            bad.append(f"{kind} {label}/{p}:{line}")
    uses = any(p.endswith(".py") for p in files) and label not in ("head",)
    locks = [p for p in files if LOCK.search(p) and "docs/" not in p]
    if uses and locks:
        text = "\n".join((root / p).read_text(encoding="utf-8", errors="replace").lower() for p in locks)
        for need in NEED:
            if not re.search(rf"(^|\n){re.escape(need)}\b", text):
                bad.append(f"C {label}: 잠금 파일({', '.join(locks)})에 {need} 가 없다")
    return bad


def self_test():
    with tempfile.TemporaryDirectory() as t:
        d = pathlib.Path(t)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        (d / "a.py").write_text("import jsonschema\nv = jsonschema.Draft202012Validator({})\n")
        (d / "b.py").write_text("import jsonschema\nv = jsonschema.Draft202012Validator({}, format_checker=jsonschema.FormatChecker())\n")
        (d / "c.py").write_text("import jsonschema\nfrom boundary_contracts import format_checker\nv = jsonschema.Draft202012Validator({}, format_checker=format_checker({}))\n")
        (d / "requirements.lock").write_text("jsonschema==4.26.0\nrfc3339-validator==0.1.4\nrfc3986-validator==0.1.1\n")
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        kinds = sorted(b.split()[0] for b in scan(d, "t"))
        ok = kinds == ["A", "B"]
        print("self-test", "통과" if ok else f"실패: {kinds}")
        return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    trees = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    allbad = []
    for a in AREAS:
        root = pathlib.Path(trees.get(a, WS / a))
        if (root / ".git").exists():
            allbad += scan(root, a)
    kinds = {k: sum(1 for b in allbad if b.startswith(k + " ")) for k in "ABC"}
    print(f"위반 {len(allbad)}건 (A format_checker 없음 {kinds['A']}, B 조용히 건너뛰는 FormatChecker {kinds['B']}, C 잠금에 형식 검증기 없음 {kinds['C']})")
    for b in allbad:
        print(b)
    return 1 if allbad else 0


if __name__ == "__main__":
    sys.exit(main())
