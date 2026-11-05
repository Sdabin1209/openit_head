#!/usr/bin/env python3
"""영역 내부 스키마(구조 규칙 5)의 제한 칸에 영역 코드가 넣는 값을 실행 없이 대조한다.

대상: 각 영역 리포 schemas/*.json(예시 제외)의 pattern·enum·const 가 걸린 문자열 칸.
생산 지점: 같은 영역 코드에서 그 칸 이름을 키로 쓰는 dict 리터럴 항목(py: ast; ts/mjs/js: 객체 리터럴 정규식)과 kwargs.
값 해석:
  - 문자열 리터럴 -> 직접 대조
  - 이름(변수) -> 같은 함수(또는 모듈)에서 그 이름이 모듈 상수 모음과 묶인 곳을 찾는다
    (`v in C`, `v not in C`, `C[v]`, `C.get(v)`, `for v in C`, `for v, _ in C.items()`) -> C 의 키·원소를 모두 대조
    모듈 상수 문자열(`V = "..."`) -> 그 값을 대조
  - 그 밖 -> 동적(입력에서 온 값). 개수와 위치를 보고한다(통과로 세지 않는다)
판정: 값이 그 칸 이름을 가진 영역 스키마 중 하나라도 어기면 '어긋남 후보'로 낸다(스키마 이름과 함께).
변이 확인(2026-11-05): deploy c723925(결함 있는 커밋)에서 cli_gen_jobs.py:99 compose_service='ops-feedback-migrate'(모음 JOB_NAMES) 를 확정으로 잡고, c3139a0 에서는 사라진다.
후보 판정: "확정" = 그 칸 이름을 가진 영역·계약 스키마 모두를 어긴다, "연결" = 그 파일이 이름으로 가리키는 스키마만 어긴다. 둘 다 사람이 읽어 판정하고 결과를 progress/rep 에 남긴다.
종료 코드: 어긋남 후보 0 이면 0, 있으면 1. 값·비밀은 출력하지 않는다(리터럴은 스키마 제한 문자열과 같은 종류의 이름만 다룬다).
"""
import ast
import json
import pathlib
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parents[2]
# 영역 작업 트리를 바꿔 볼 때: --tree 영역=경로 (예: deploy 의 작업 브랜치 worktree). 없으면 워크스페이스의 영역 폴더
TREES = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)


def root(area):
    return pathlib.Path(TREES[area]) if area in TREES else WS / area
AREAS = [a["name"] for a in (lambda d: d["areas"] if isinstance(d, dict) else d)(json.loads((WS / "head/shared/areas.json").read_text()))]
SKIP_DIR = re.compile(r"(^|/)(tests?|fixtures|examples|docs|build|node_modules|\.venv)(/|$)|(^|/)test_[^/]*$|\.test\.[a-z]+$")


def ls(area, pred):
    r = subprocess.run(["git", "-C", str(root(area)), "ls-files"], capture_output=True, text=True)
    return [p for p in r.stdout.splitlines() if pred(p)] if r.returncode == 0 else []


def constraints(node, out, name=None):
    if isinstance(node, dict):
        if name and ("type" in node or "$ref" in node or any(k in node for k in ("pattern", "enum", "const"))):
            # 제한 없는 칸({})도 기록한다: 같은 이름 칸이 제한 없이 있는 스키마 소속일 수 있으면 그 값은 어긋남이 아니다
            out.setdefault(name, []).append({k: node[k] for k in ("pattern", "enum", "const") if k in node})
        for k, v in node.items():
            if k == "properties" and isinstance(v, dict):
                for p, s in v.items():
                    constraints(s, out, p)
            elif k == "items":
                constraints(v, out, name)
            elif k in ("$defs", "definitions", "anyOf", "oneOf", "allOf", "additionalProperties", "patternProperties"):
                for s in (v.values() if isinstance(v, dict) else v if isinstance(v, list) else []):
                    constraints(s, out, None if k in ("$defs", "definitions", "patternProperties") else name)


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


SUFFIX = re.compile(r"(Request|Result|Input|Output|Record|Config|State)$")


def judge(key, value, cons, rel, text):
    """그 파일이 쓰는 스키마(파일 이름 또는 본문의 스키마 이름으로 연결)가 있으면 그것들, 없으면 그 칸을 가진 모든 스키마.
    한 dict 가 어느 스키마 것인지 정적으로 정할 수 없으므로 후보 스키마 모두를 어길 때만 어긋남이다."""
    stem = pathlib.Path(rel).stem
    cs = cons[key]
    linked = [c for c in cs if snake(SUFFIX.sub("", c["s"].split(".")[0])) == stem or c["s"].split(".")[0] in text]
    def all_bad(pool):
        by = {}
        for c in pool:
            by.setdefault(c["s"], []).append(c["c"])
        # 한 스키마 안에서 같은 이름 칸이 여럿이면 그중 하나라도 받으면 그 스키마는 받는다
        return sorted(by) if by and all(all(violates(value, x) for x in xs) for xs in by.values()) else []
    full = all_bad(cs + CONTRACT.get(key, []))
    if full:
        return ["확정"] + full
    lk = all_bad(linked) if linked else []
    return (["연결"] + lk) if lk else []


def violates(value, c):
    if "const" in c and value != c["const"]:
        return True
    if "enum" in c and value not in c["enum"]:
        return True
    if "pattern" in c and re.search(c["pattern"], value) is None:
        return True
    return False


def module_consts(tree):
    coll, strs = {}, {}
    for st in tree.body:
        if isinstance(st, (ast.Assign, ast.AnnAssign)):
            tgts = st.targets if isinstance(st, ast.Assign) else [st.target]
            for t in tgts:
                if not isinstance(t, ast.Name) or st.value is None:
                    continue
                v = st.value
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    strs[t.id] = v.value
                elif isinstance(v, ast.Dict):
                    ks = [k.value for k in v.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)]
                    vs = [x.value for x in v.values if isinstance(x, ast.Constant) and isinstance(x.value, str)]
                    coll[t.id] = (ks, vs)
                elif isinstance(v, (ast.List, ast.Tuple, ast.Set)):
                    coll[t.id] = ([x.value for x in v.elts if isinstance(x, ast.Constant) and isinstance(x.value, str)], [])
    return coll, strs


def bound_collections(scope, var, coll):
    """var 가 모듈 상수 모음 C 와 묶인 곳 -> 대조할 값 목록과 근거."""
    found = []
    for n in ast.walk(scope):
        if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name) and n.left.id == var:
            for op, c in zip(n.ops, n.comparators):
                if isinstance(op, (ast.In, ast.NotIn)) and isinstance(c, ast.Name) and c.id in coll:
                    found.append((c.id, coll[c.id][0]))
        elif isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id in coll and isinstance(n.slice, ast.Name) and n.slice.id == var:
            found.append((n.value.id, coll[n.value.id][0]))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and isinstance(n.func.value, ast.Name) \
                and n.func.value.id in coll and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id == var:
            found.append((n.func.value.id, coll[n.func.value.id][0]))
        elif isinstance(n, (ast.For, ast.comprehension)):
            it, tg = n.iter, n.target
            names = [tg.id] if isinstance(tg, ast.Name) else [e.id for e in getattr(tg, "elts", []) if isinstance(e, ast.Name)]
            if var not in names:
                continue
            base = it.args[0] if isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id in ("sorted", "list", "enumerate") and it.args else it
            if isinstance(base, ast.Call) and isinstance(base.func, ast.Attribute) and isinstance(base.func.value, ast.Name) and base.func.value.id in coll:
                ks, vs = coll[base.func.value.id]
                idx = names.index(var)
                found.append((base.func.value.id + "." + base.func.attr, vs if base.func.attr == "values" or (base.func.attr == "items" and idx == 1) else ks))
            elif isinstance(base, ast.Name) and base.id in coll:
                found.append((base.id, coll[base.id][0]))
    return found


def scan_py(area, rel, cons, rep):
    try:
        TEXT[0] = (root(area) / rel).read_text(encoding="utf-8")
        tree = ast.parse(TEXT[0])
    except (SyntaxError, UnicodeDecodeError):
        rep["unparsed"].append(f"{area}/{rel}")
        return
    coll, strs = module_consts(tree)
    scopes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def scope_of(node):
        best = tree
        for s in scopes:
            if s.lineno <= node.lineno <= (s.end_lineno or s.lineno) and (best is tree or s.lineno >= best.lineno):
                best = s
        return best

    pairs = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            pairs += [(k.value, v, n) for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant) and k.value in cons]
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":   # 함수 인자(argparse action= 등)는 스키마 값이 아니다
            pairs += [(kw.arg, kw.value, n) for kw in n.keywords if kw.arg in cons]
    for key, v, node in pairs:
        where = f"{area}/{rel}:{v.lineno}"
        vals = []
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            vals = [("리터럴", v.value)]
        elif isinstance(v, ast.Name) and v.id in strs:
            vals = [(f"상수 {v.id}", strs[v.id])]
        elif isinstance(v, ast.Name):
            for src, xs in bound_collections(scope_of(node), v.id, coll):
                vals += [(f"모음 {src}", x) for x in xs]
        if not vals:
            rep["dynamic"].append(f"{where} {key}")
            continue
        rep["checked"] += 1
        for src, x in vals:
            bad = judge(key, x, cons, rel, TEXT[0])
            if bad:
                rep["bad"].append(f"{where} {key}={x!r} ({src}) 어기는 스키마: {bad}")


TEXT = [""]
JS_PAIR = re.compile(r"""(?<![\w$.])["']?([A-Za-z_][\w]*)["']?\s*:\s*(["'])([^"'\\\n]{0,200})\2""")


def scan_js(area, rel, cons, rep):
    text = (root(area) / rel).read_text(encoding="utf-8", errors="replace")
    for m in JS_PAIR.finditer(text):
        key, val = m.group(1), m.group(3)
        if key not in cons:
            continue
        rep["checked"] += 1
        bad = judge(key, val, cons, rel, text)
        if bad:
            line = text.count("\n", 0, m.start()) + 1
            rep["bad"].append(f"{area}/{rel}:{line} {key}={val!r} (리터럴) 어기는 스키마: {bad}")


CONTRACT = {}


def load_contract():
    """영역 코드는 계약 스키마 값도 dict 로 만든다: 연결된 내부 스키마가 없으면 계약 스키마도 후보로 둔다."""
    for f in sorted((WS / "boundary-contracts/boundary_contracts/schemas").glob("*.json")):
        out = {}
        constraints(json.loads(f.read_text(encoding="utf-8")), out)
        for k, cs in out.items():
            CONTRACT.setdefault(k, []).extend({"s": "계약:" + f.name, "c": c} for c in cs)


def main():
    load_contract()
    total = {"schemas": 0, "fields": 0, "checked": 0}
    allbad, alldyn, unparsed = [], [], []
    for area in AREAS:
        if not (root(area) / ".git").exists():
            continue
        files = ls(area, lambda p: re.search(r"(^|/)schemas/[^/]+\.json$", p) and "example" not in p and not SKIP_DIR.search(p.rsplit("/schemas/", 1)[0] + "/") and not p.startswith("schema/"))
        cons = {}
        for f in files:
            try:
                d = json.loads((root(area) / f).read_text(encoding="utf-8"))
            except ValueError:
                unparsed.append(f"{area}/{f}")
                continue
            out = {}
            constraints(d, out)
            for k, cs in out.items():
                cons.setdefault(k, []).extend({"s": pathlib.Path(f).name, "c": c} for c in cs)
        if not files:
            continue
        rep = {"checked": 0, "bad": [], "dynamic": [], "unparsed": unparsed}
        for rel in ls(area, lambda p: p.endswith((".py", ".ts", ".mjs", ".js")) and not SKIP_DIR.search(p)):
            (scan_py if rel.endswith(".py") else scan_js)(area, rel, cons, rep)
        total["schemas"] += len(files)
        total["fields"] += len(cons)
        total["checked"] += rep["checked"]
        allbad += rep["bad"]
        alldyn += rep["dynamic"]
        print(f"{area}: 스키마 {len(files)}, 제한 칸 이름 {len(cons)}, 값 대조 지점 {rep['checked']}, 어긋남 후보 {len(rep['bad'])}, 동적 지점 {len(rep['dynamic'])}")
    print(f"합계: 스키마 {total['schemas']}, 제한 칸 이름 {total['fields']}, 값 대조 지점 {total['checked']}, 어긋남 후보 {len(allbad)}, 동적 지점 {len(alldyn)}, 못 읽은 파일 {len(unparsed)}")
    for b in allbad:
        print("어긋남 후보", b)
    for d in alldyn:
        print("동적", d)
    for u in unparsed:
        print("못 읽음", u)
    return 1 if allbad else 0


if __name__ == "__main__":
    sys.exit(main())
