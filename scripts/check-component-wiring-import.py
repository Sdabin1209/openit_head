#!/usr/bin/env python3
"""컴포넌트는 wiring 의 정책을 가져오지 않는다(구조 규칙 D104 3·4, C3·C4, D117).
왜: 컴포넌트는 자기 입출력 스키마와 자기 업무만 안다. wiring 은 영역이 컴포넌트를 잇는 곳이라 정책(재시도·경로·설정 해석·다른 컴포넌트 조립)을 가진다.
컴포넌트가 wiring 모듈을 import 하면 영역의 배선 구조를 알게 되고, 정책이 컴포넌트 밖에서 바뀌면 컴포넌트가 따라 바뀐다. 정책은 주입받는다.
허용(기반 도구, 정책이 아니다): wiring 의 clock(시계 주입형), pgbase(DB 연결 기반), validate(계약 검증 호출), schema_gate(스키마 위반 목록),
  errors/error/*_errors(오류형), deadline(마감 계산형). 그 밖의 wiring 모듈은 정책으로 본다(허용 모듈에서도 정책 함수는 가져오지 않는다 — 모듈 단위로만 판정한다).
센다: components/ 아래 파일이
  P 파이썬 `from ..wiring.X import …`, `from pkg.wiring.X import …`, `import pkg.wiring.X`, `from ..wiring import X`(X 가 허용 모듈이 아니면)
  J JS/TS `import … from '../wiring/X'`, `require('../wiring/X')`, `import('../wiring/X')`
셈하지 않는 것: 주석, 허용 목록(ALLOW, 빈 목록에서 시작).
사용: check-component-wiring-import.py [--self-test]. 종료 0 통과, 1 위반."""
import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _checklib as L  # noqa: E402

ALLOW = {}
BASE = {"clock", "pgbase", "validate", "schema_gate", "errors", "error", "deadline"}
COMP = re.compile(r"(^|/)components/")


def ok_mod(name):
    return name in BASE or name.endswith("_errors")


def py_hits(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            parts = (n.module or "").split(".")
            if "wiring" in parts:
                rest = parts[parts.index("wiring") + 1:]
                mods = [rest[0]] if rest else [a.name for a in n.names]
                for m in mods:
                    if not ok_mod(m):
                        out.append((n.lineno, "P", f"컴포넌트가 wiring.{m} 를 가져온다 — 정책은 주입받는다"))
        elif isinstance(n, ast.Import):
            for a in n.names:
                parts = a.name.split(".")
                if "wiring" in parts:
                    rest = parts[parts.index("wiring") + 1:]
                    if not rest or not ok_mod(rest[0]):
                        out.append((n.lineno, "P", f"컴포넌트가 {a.name} 를 가져온다 — 정책은 주입받는다"))
    return out


JS_IMP = re.compile(r"""(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*\(\s*|^\s*import\s+)['"]([^'"]*(?:^|/)wiring(?:/([\w.-]+))?)['"]""")


def js_hits(text):
    out = []
    for i, ln in enumerate(L.strip_js_comments(text), 1):
        for m in JS_IMP.finditer(ln):
            mod = re.sub(r"\.(m?[jt]s|cjs)$", "", m.group(2) or "")
            if not ok_mod(mod):
                out.append((i, "J", f"컴포넌트가 {m.group(1)} 를 가져온다 — 정책은 주입받는다"))
    return out


def scan(a, rel, text):
    if not COMP.search(rel) or L.TEST_FILE.search(rel):
        return []
    lg = L.lang(rel, text)
    return py_hits(text) if lg == "py" else js_hits(text) if lg == "js" else []


def self_test():
    bad = []
    pos = [("p/components/a.py", "from ..wiring.retry_policy import backoff\n"), ("p/components/a.py", "from pkg.wiring.build import make\n"),
           ("p/components/a.py", "import pkg.wiring.routes\n"), ("p/components/a.py", "from ..wiring import policy\n"),
           ("src/components/a.ts", "import { retry } from '../wiring/retry';\n"), ("src/components/a.ts", "const w = require(\"../wiring/config.js\");\n")]
    neg = [("p/components/a.py", "from ..wiring.errors import PipelineError\n"), ("p/components/a.py", "from ..wiring.clock import fmt_ts\n"),
           ("p/components/a.py", "from ..wiring.pgbase import PgBase\nfrom ..wiring.validate import check\nfrom ..wiring.schema_gate import violations\n"),
           ("p/components/a.py", "from ..wiring import errors, deadline\n"), ("p/components/a.py", "from ..wiring.gate_errors import X\n"),
           ("p/wiring/a.py", "from ..wiring.policy import x\n"), ("p/components/a.py", "# from ..wiring.policy import x\n"),
           ("src/components/a.ts", "// import { r } from '../wiring/retry';\n"), ("src/components/a.ts", "import { Clock } from '../wiring/clock';\n"),
           ("p/components/a.py", "from ..types import X\n")]
    for rel, t in pos:
        if not scan("z", rel, t):
            bad.append(f"놓침 {rel} {t!r}")
    for rel, t in neg:
        if scan("z", rel, t):
            bad.append(f"거짓양성 {rel} {t!r}")
    return bad


if __name__ == "__main__":
    sys.exit(L.run("컴포넌트의 wiring 정책 import", scan, self_test, ALLOW, pathlib.Path(__file__).name))
