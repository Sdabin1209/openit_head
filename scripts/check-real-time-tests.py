#!/usr/bin/env python3
"""시험 판정에 실제 시간을 쓰지 않는다(RUNTIME R8.1·R9.1 '같은 입력이면 같은 출력', RULE_CHECKS #2(U422) 시계 주입, 워크스페이스 CLAUDE.md 자동화 C45).
왜: 실제로 자거나 벽시계 차이를 재서 판정하는 시험은 기계 부하·동시 실행(check-all --strict 가 영역 시험을 함께 돌린다)에 따라 결과가 바뀐다.
같은 코드에서 통과와 실패가 갈리면 시험이 아니다. 시간은 주입한 가짜 시계로 진행시키고, 마감은 가짜 시계의 값으로 단언한다.
센다(시험 파일: tests/·test-*/·e2e*/·test_*·*.test.*·*.spec.*·*smoke*·conftest.py):
  S 파이썬 time.sleep(0 이 아닌 값)·asyncio.sleep(0 이 아닌 값)
  D 벽시계 차이: time.time()/monotonic()/perf_counter()(_ns), Date.now()·performance.now()·process.hrtime 가 뺄셈에 쓰인 줄
  E elapsed·duration·took 이름을 비교(<, >, <=, >=)·assertLess/Greater 로 단언
  J join(숫자)·join(timeout=숫자): 실제 시간 동안 스레드를 기다려 판정
  T JS setTimeout 으로 실제 대기(await new Promise(r => setTimeout(r, N)), sleep(N) 헬퍼 정의)
  C 셸 SECONDS 로 경과 측정, $(date +%s) 차이
셈하지 않는 것: 주석, asyncio.sleep(0)(양보일 뿐), 시험이 아닌 파일. 허용 목록(ALLOW, 빈 목록에서 시작).
보지 않는 것: 셸 폴링 루프의 sleep(컨테이너 준비 대기는 판정이 아니라 대기다. 판정은 상한 횟수로 한다), 가짜 시계 객체의 sleep 메서드(time.sleep 이 아닌 것).
사용: check-real-time-tests.py [--self-test]. 종료 0 통과, 1 위반."""
import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _checklib as L  # noqa: E402

ALLOW = {}
CLOCKS = {"time", "monotonic", "perf_counter", "time_ns", "monotonic_ns", "perf_counter_ns"}
ELAPSED = re.compile(r"\b\w*(elapsed|duration|took|spent)\w*\b", re.I)


def py_hits(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    tmods, tfns, amods = set(), set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "time":
                    tmods.add(a.asname or "time")
                if a.name == "asyncio":
                    amods.add(a.asname or "asyncio")
        elif isinstance(n, ast.ImportFrom) and n.module == "time":
            tfns.update(a.asname or a.name for a in n.names if a.name in CLOCKS | {"sleep"})

    def clock(c):
        if not isinstance(c, ast.Call):
            return False
        f = c.func
        return (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in tmods and f.attr in CLOCKS) \
            or (isinstance(f, ast.Name) and f.id in tfns and f.id != "sleep")

    def nonzero(c):
        return not (c.args and isinstance(c.args[0], ast.Constant) and c.args[0].value == 0)
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and ((f.value.id in tmods and f.attr == "sleep") or (f.value.id in amods and f.attr == "sleep")) and nonzero(n):
                out.append((n.lineno, "S", "실제로 잔다 — 가짜 시계를 진행시킨다"))
            elif isinstance(f, ast.Name) and f.id == "sleep" and "sleep" in tfns and nonzero(n):
                out.append((n.lineno, "S", "실제로 잔다 — 가짜 시계를 진행시킨다"))
            elif isinstance(f, ast.Attribute) and f.attr == "join" and not isinstance(f.value, ast.Constant) \
                    and ((n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, (int, float)))
                         or any(k.arg == "timeout" for k in n.keywords)):
                out.append((n.lineno, "J", "join(timeout) 으로 실제 시간을 기다려 판정한다"))
            elif isinstance(f, ast.Attribute) and f.attr in ("assertLess", "assertLessEqual", "assertGreater", "assertGreaterEqual") and ELAPSED.search(ast.unparse(n)):
                out.append((n.lineno, "E", "경과 시간을 단언한다"))
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub) and (clock(n.left) or clock(n.right)):
            out.append((n.lineno, "D", "벽시계 차이로 잰다"))
        elif isinstance(n, ast.Compare) and any(isinstance(o, (ast.Lt, ast.Gt, ast.LtE, ast.GtE)) for o in n.ops) \
                and any(isinstance(x, ast.Name) and ELAPSED.fullmatch(x.id) for x in [n.left, *n.comparators]):
            out.append((n.lineno, "E", "경과 시간을 비교한다"))
    return out


JS_DIFF = re.compile(r"(Date\.now\(\)|performance\.now\(\)|process\.hrtime(\.bigint)?\(\))\s*-|-\s*(Date\.now\(\)|performance\.now\(\))")
JS_WAIT = re.compile(r"new\s+Promise\s*\([^)]*=>\s*setTimeout\s*\(|\bsetTimeout\s*\(\s*(r|res|resolve|done|ok)\s*,\s*\d|\bsetTimeout\s*\(\s*(r|res|resolve|ok)\s*,\s*\w+\s*\)")
JS_ELAPSED = re.compile(r"\b\w*(elapsed|duration|took)\w*\s*[<>]=?|[<>]=?\s*\w*(elapsed|duration|took)\w*\b", re.I)
SH = re.compile(r"\$SECONDS\b|\bSECONDS\s*=|\$\{SECONDS\}|\$\(\s*date\s+\+%s\s*\)")


def scan(a, rel, text):
    if not L.TEST_FILE.search(rel):
        return []
    lg = L.lang(rel, text)
    if lg == "py":
        return py_hits(text)
    out = []
    if lg == "js":
        for i, ln in enumerate(L.strip_js_comments(text), 1):
            if JS_DIFF.search(ln):
                out.append((i, "D", "벽시계 차이로 잰다"))
            elif JS_WAIT.search(ln):
                out.append((i, "T", "setTimeout 으로 실제 대기한다 — 가짜 타이머·주입 시계를 쓴다"))
            elif JS_ELAPSED.search(ln) and re.search(r"assert|expect|ok\(", ln):
                out.append((i, "E", "경과 시간을 단언한다"))
    elif lg == "sh":
        for i, ln in enumerate(L.strip_hash_comments(text), 1):
            if SH.search(re.sub(r"'[^']*'", "", ln)):
                out.append((i, "C", "SECONDS·date +%s 로 경과를 잰다"))
    return out


def self_test():
    bad = []
    pos = [("tests/test_a.py", "import time\ntime.sleep(0.2)\n"), ("tests/test_a.py", "import time\nt0 = time.monotonic()\nrun()\nassert time.monotonic() - t0 < 1\n"),
           ("tests/test_a.py", "from time import perf_counter\ns = perf_counter()\nd = perf_counter() - s\n"), ("tests/test_a.py", "import asyncio\nawait asyncio.sleep(0.5)\n"),
           ("tests/test_a.py", "assert elapsed < 2.0\n"), ("tests/test_a.py", "th.join(5)\n"), ("tests/test_a.py", "th.join(timeout=t)\n"),
           ("tests/test_a.py", "self.assertLess(elapsed, 1)\n"),
           ("test/a.test.ts", "await new Promise((r) => setTimeout(r, 50));\n"), ("test/a.test.ts", "const ms = Date.now() - start;\n"),
           ("test/a.test.ts", "assert.ok(elapsed < 100);\n"), ("tests/smoke.sh", "start=$SECONDS\nrun\nif [ $((SECONDS-start)) -gt 5 ]; then exit 1; fi\n"),
           ("tests/a.sh", "t0=$(date +%s)\n")]
    neg = [("tests/test_a.py", "import asyncio\nawait asyncio.sleep(0)\n"), ("tests/test_a.py", "clock.sleep(5)\n"), ("tests/test_a.py", "import time\n# time.sleep(1)\n"),
           ("tests/test_a.py", "','.join(xs)\n"), ("tests/test_a.py", "th.join()\n"), ("pkg/a.py", "import time\ntime.sleep(1)\n"),
           ("tests/test_a.py", "now = clock.now()\nd = now - start\n"), ("test/a.test.ts", "// setTimeout(r, 50)\n"), ("test/a.test.ts", "clock.tick(50);\n"),
           ("tests/a.sh", "for i in $(seq 30); do curl -fs x && break; sleep 1; done\n"), ("tests/test_a.py", "assert duration_ms == 5\n")]
    for rel, t in pos:
        if not scan("z", rel, t):
            bad.append(f"놓침 {rel} {t!r}")
    for rel, t in neg:
        if scan("z", rel, t):
            bad.append(f"거짓양성 {rel} {t!r}")
    return bad


if __name__ == "__main__":
    sys.exit(L.run("시험 판정의 실제 시간", scan, self_test, ALLOW, pathlib.Path(__file__).name))
