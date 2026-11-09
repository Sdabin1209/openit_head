#!/usr/bin/env python3
"""JSON 첫 읽기는 엄격 파서로(계약 CONVENTIONS 10절 'JSON 값의 범위', D117, C43).
왜: json.load/loads·JSON.parse 는 중복 키를 마지막 값으로 덮고 NaN·Infinity·1e999 를 받으며 깊이·크기 한도가 없다. 사람·설정·요청·이웃 산출물을
처음 읽는 곳에서 이것을 쓰면 계약 JSON 공통 규칙(I-JSON, 깊이 64, 1 MiB)을 지키지 못한 값이 안으로 들어온다. 파이썬은 계약 boundary_contracts.strict_json
(loads)을, 노드는 리포의 엄격 파서(예: admin-console scripts/ijson-check.cjs 의 parse)를 쓴다.
센다(제품 코드: 시험 파일·생성물 밖):
  P 파이썬 json.load/json.loads(import json as x, from json import loads 별칭 포함)·orjson/ujson/simplejson.loads
  R 응답 본문을 비엄격으로 해석: 파이썬 <응답>.json(), JS await <응답>.json()
  J JS/TS JSON.parse(
셈하지 않는 것: 엄격 파서 구현 파일 자체(STRICT_IMPL: 그 안의 json.loads 는 object_pairs_hook·parse_constant 로 엄격 규칙을 거는 정본이다),
  시험 파일(제품 입구가 아니다, R7), 생성물(types/contract/, *validators.cjs).
허용 목록(ALLOW, 빈 목록에서 시작): 자기 저장 데이터 decode·생성 스크립트 등은 '영역/경로:줄' 과 이유를 적는다.
사용: check-strict-json-entry.py [--self-test]. 종료 0 통과, 1 위반."""
import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _checklib as L  # noqa: E402

# 엄격 파서 구현 파일(정의상 대상 밖): 계약 정본과 노드 엄격 파서
STRICT_IMPL = {"boundary-contracts/boundary_contracts/strict_json.py", "admin-console/scripts/ijson-check.cjs"}
ALLOW = {}
MODS = {"json", "orjson", "ujson", "simplejson"}


def py_hits(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return [(i, "P", "json.load(s) (파싱 실패 파일, 줄 정규식)") for i, ln in enumerate(L.strip_hash_comments(text), 1) if re.search(r"\bjson\.loads?\(", ln)]
    mods, fns = {}, {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name in MODS:
                    mods[a.asname or a.name] = a.name
        elif isinstance(n, ast.ImportFrom) and n.module in MODS:
            for a in n.names:
                if a.name in ("load", "loads"):
                    fns[a.asname or a.name] = n.module
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in mods and f.attr in ("load", "loads"):
            out.append((n.lineno, "P", f"{mods[f.value.id]}.{f.attr} 비엄격 해석 — boundary_contracts.strict_json.loads 를 쓴다"))
        elif isinstance(f, ast.Name) and f.id in fns:
            out.append((n.lineno, "P", f"{fns[f.id]}.{f.id} 비엄격 해석 — boundary_contracts.strict_json.loads 를 쓴다"))
        elif isinstance(f, ast.Attribute) and f.attr == "json" and not n.args and not n.keywords and isinstance(f.value, ast.Name) \
                and re.search(r"(resp|response|res|r)$", f.value.id, re.I):
            out.append((n.lineno, "R", "응답 .json() 비엄격 해석 — 본문 바이트를 strict_json.loads 로 읽는다"))
    return out


JS_PARSE = re.compile(r"(?<![\w$.])JSON\s*\.\s*parse\s*\(")
JS_RESP = re.compile(r"\b(res|resp|response|r)\s*\.\s*json\s*\(\s*\)")


def js_hits(text):
    out = []
    for i, ln in enumerate(L.strip_js_comments(text), 1):
        if JS_PARSE.search(ln):
            out.append((i, "J", "JSON.parse 비엄격 해석 — 리포의 엄격 파서를 쓴다"))
        if JS_RESP.search(ln):
            out.append((i, "R", "응답 .json() 비엄격 해석 — 본문 글을 엄격 파서로 읽는다"))
    return out


def scan(a, rel, text):
    if f"{a}/{rel}" in STRICT_IMPL or L.TEST_FILE.search(rel) or L.generated(rel, text):
        return []
    lg = L.lang(rel, text)
    return py_hits(text) if lg == "py" else js_hits(text) if lg == "js" else []


def self_test():
    bad = []
    pos = [("a/x.py", "import json\njson.loads(s)\n"), ("a/x.py", "import json as j\nj.load(f)\n"), ("a/x.py", "from json import loads as L\nL(s)\n"),
           ("a/x.py", "import orjson\norjson.loads(b)\n"), ("a/x.py", "r = httpx.get(u)\nd = r.json()\n"),
           ("a/x.mjs", "const x = JSON.parse(readFileSync(p, 'utf8'));\n"), ("a/x.ts", "const d = await res.json();\n"),
           ("a/scripts/build.mjs", "try { req = JSON.parse(t); } catch {}\n")]
    neg = [("a/x.py", "from boundary_contracts.strict_json import loads\nloads(s)\n"), ("a/x.py", "import json\njson.dumps(x)\n"),
           ("a/x.py", "# json.loads(s)\n"), ("a/x.py", "s = 'json.loads(x)'\n"), ("a/tests/test_x.py", "import json\njson.loads(s)\n"),
           ("a/x.mjs", "// JSON.parse(x)\n"), ("a/x.mjs", "const t = JSON.stringify(x);\n"), ("a/x.ts", "const v = parse(text);\n"),
           ("a/x.test.ts", "JSON.parse(x)\n"), ("a/src/types/contract/X.ts", "JSON.parse(x)\n")]
    for rel, t in pos:
        if not scan("z", rel, t):
            bad.append(f"놓침 {rel} {t!r}")
    for rel, t in neg:
        if scan("z", rel, t):
            bad.append(f"거짓양성 {rel} {t!r}")
    if scan("boundary-contracts", "boundary_contracts/strict_json.py", "import json\njson.loads(s)\n"):
        bad.append("엄격 파서 구현을 셌다")
    return bad


if __name__ == "__main__":
    sys.exit(L.run("JSON 첫 읽기 비엄격 파서", scan, self_test, ALLOW, pathlib.Path(__file__).name))
