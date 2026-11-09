#!/usr/bin/env python3
"""오류·예외·로그에 값을 싣지 않는다(계약 INTERFACES I7 '오류에 값을 싣지 않는다', 계약 safe_error, C25 '비밀 값은 로그·오류 응답에 넣지 않는다').
왜: jsonschema 의 e.message 는 인스턴스 값을 글로 담고(예: "'환자 문장' is not of type 'integer'"), e.instance 는 값 자체, absolute_path·
relative_path·json_path·path 와 ajv 의 instancePath 는 사용자가 정한 키(환자 문장일 수 있다)를 담는다. additionalProperties 위반의 추가 키 목록도
요청이 보낸 키 이름이다. 계약 boundary_contracts.safe_error 는 schema_path(스키마 쪽 위치)와 keyword 만 낸다 — 그것만 허용한다.
센다(제품 코드: 시험 파일·생성물 밖, jsonschema·ajv·ValidationError·iter_errors 를 쓰는 파일):
  M 파이썬 jsonschema 오류의 .message / .instance / .absolute_path / .relative_path / .json_path / .path / .params 사용(파이썬은 ast: 이름이 e·err·error·exc·ve·x 등
    오류 변수이거나 iter_errors·best_match·ValidationError 에서 온 이름)
  A JS/TS ajv 오류의 instancePath·params.additionalProperty·errorsText(·오류 배열의 .message(errors…message)
  K 오류·로그 문장(raise·throw·Error(·log·print·warn)에 추가·모르는 키 목록 변수({extra}·{unknown}·{unexpected}·{additional}…)를 끼워 넣는 것
셈하지 않는 것: safe_error 정의(계약 정본), 시험 파일, 생성물(types/contract/, *validators.cjs), 주석. 허용 목록(ALLOW, 빈 목록에서 시작).
사용: check-error-values.py [--self-test]. 종료 0 통과, 1 위반."""
import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _checklib as L  # noqa: E402

ALLOW = {}
CTX = re.compile(r"jsonschema|ValidationError|iter_errors|best_match|\bajv\b|Ajv|\.errors\b|validators?\.cjs|validate\(")
BAD_ATTR = {"message", "instance", "absolute_path", "relative_path", "json_path", "path", "params"}
ERRVAR = re.compile(r"^(e|err|error|exc|ex|ve|x|v|first|best|errs?\w*|\w*_?err(or)?s?)$")
KEYLIST = re.compile(r"\{[^{}]*\b(extra|unknown|unexpected|additional|surplus|extraneous)\w*[^{}]*\}|\$\{[^{}]*\b(extra|unknown|unexpected|additional)\w*[^{}]*\}")
MSGSITE = re.compile(r"\b(raise|throw|Error\s*\(|Exception\s*\(|log\w*\.\w+\s*\(|logger\.|console\.(log|error|warn)|print\s*\(|warn\w*\s*\(|fail\s*\()")


def py_hits(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    parent = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parent[c] = p
    srcvars = set()   # iter_errors·best_match·ValidationError 에서 온 이름
    for n in ast.walk(tree):
        if isinstance(n, (ast.For, ast.comprehension)) and re.search(r"iter_errors|errors", ast.unparse(n.iter)) and isinstance(n.target, ast.Name):
            srcvars.add(n.target.id)
        elif isinstance(n, ast.ExceptHandler) and n.name and n.type is not None and re.search(r"ValidationError|SchemaError", ast.unparse(n.type)):
            srcvars.add(n.name)
        elif isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and re.search(r"best_match|iter_errors", ast.unparse(n.value.func)):
            srcvars.update(t.id for t in n.targets if isinstance(t, ast.Name))
    safe = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == "safe_error":
            safe.update(range(n.lineno, (n.end_lineno or n.lineno) + 1))
    out = []
    for n in ast.walk(tree):
        up = parent.get(n)
        if isinstance(up, ast.Attribute) and up.attr in ("appendleft", "append", "extendleft", "extend"):   # 경로를 고치는 일(값을 싣는 것이 아니다)
            continue
        if isinstance(n, ast.Attribute) and n.attr in BAD_ATTR and isinstance(n.value, ast.Name) and n.lineno not in safe:
            v = n.value.id
            if v in srcvars or (ERRVAR.match(v) and n.attr != "path" and n.attr != "params"):
                if n.attr == "message" and v not in srcvars and not re.search(r"jsonschema|ValidationError|iter_errors|best_match", text):
                    continue
                out.append((n.lineno, "M", f"검증 오류의 {n.attr} 를 쓴다 — safe_error(schema_path·keyword)만 싣는다"))
    return out


JS_A = re.compile(r"\binstancePath\b|\.params\s*\.\s*additionalProperty\b|\berrorsText\s*\(|\berrors\b[^;]*\.message\b|\bajvErr\w*\.message\b")


def scan(a, rel, text):
    if L.TEST_FILE.search(rel) or L.generated(rel, text) or not CTX.search(text):
        return []
    lg = L.lang(rel, text)
    out = []
    if lg == "py":
        out += py_hits(text)
        lines = L.strip_hash_comments(text)
    elif lg == "js":
        lines = L.strip_js_comments(text)
        out += [(i, "A", "ajv 오류의 인스턴스 위치·값·추가 키를 싣는다 — schemaPath·keyword 만") for i, ln in enumerate(lines, 1) if JS_A.search(ln)]
    else:
        return []
    out += [(i, "K", "오류·로그 문장에 추가·모르는 키 목록을 싣는다 — 키 이름은 요청 값이다") for i, ln in enumerate(lines, 1) if MSGSITE.search(ln) and KEYLIST.search(ln)]
    return out


def self_test():
    bad = []
    pre = "import jsonschema\n"
    pos = [("x.py", pre + "for e in v.iter_errors(x):\n    log.warning(e.message)\n"), ("x.py", pre + "try:\n    v.validate(x)\nexcept jsonschema.ValidationError as ve:\n    raise Bad(str(ve.instance))\n"),
           ("x.py", pre + "e = best_match(v.iter_errors(x))\nraise Bad(list(e.absolute_path))\n"), ("x.py", pre + "for err in errs:\n    msg = err.message\n"),
           ("x.py", pre + "raise ValueError(f'unknown keys: {sorted(extra)}')\n"),
           ("x.ts", "import Ajv from 'ajv';\nthrow new Error(`${v.errors[0].instancePath} bad`);\n"), ("x.ts", "const ajv = new Ajv();\nconsole.error(ajv.errorsText(validate.errors));\n"),
           ("x.ts", "const ajv = new Ajv();\nconst m = validate.errors.map((x) => x.message);\n"),
           ("x.mjs", "import Ajv from 'ajv';\nthrow new Error(`unexpected: ${unexpectedKeys.join(',')}`);\n")]
    neg = [("x.py", pre + "def safe_error(e):\n    return {'schema_path': '/'.join(e.absolute_schema_path), 'keyword': e.validator}\n"),
           ("x.py", pre + "for e in v.iter_errors(x):\n    out.append(safe_error(e))\n"), ("x.py", "def f(e):\n    return e.message\n"),
           ("tests/test_x.py", pre + "for e in v.iter_errors(x):\n    print(e.message)\n"), ("x.py", pre + "p = pathlib.Path(x).path\n"),
           ("x.ts", "import Ajv from 'ajv';\nthrow new Error(`${errors[0].schemaPath} ${errors[0].keyword}`);\n"),
           ("x.ts", "const e = new Error('x');\nconsole.log(e.message);\n"), ("x.py", pre + "# raise X(e.message)\n"), ("x.py", pre + "for e in v.iter_errors(x):\n    e.path.appendleft(p)\n"), ("src/types/validators.gen.cjs", "const ajv = 1; e.instancePath\n"),
           ("x.py", pre + "raise ValueError(f'unknown keys: {len(extra)}건')\n".replace("unknown keys: {len(extra)}건", "추가 키가 있다"))]
    for rel, t in pos:
        if not scan("z", rel, t):
            bad.append(f"놓침 {rel} {t!r}")
    for rel, t in neg:
        if scan("z", rel, t):
            bad.append(f"거짓양성 {rel} {t!r}")
    return bad


if __name__ == "__main__":
    sys.exit(L.run("오류·로그의 검증 값", scan, self_test, ALLOW, pathlib.Path(__file__).name))
