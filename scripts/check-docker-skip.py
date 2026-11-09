#!/usr/bin/env python3
"""Docker 가 없을 때 시험이 건너뛰어 rc=0 이 되지 않는다(D123 시험은 샌드박스, C33, C22 '이미지가 빌드되고 /healthz 응답을 확인', 워크스페이스 CLAUDE.md
'수용 테스트와 계약 검증을 통과하기 전에 완료라 말하지 않는다').
왜: pytest·unittest·node:test 는 skip 이 있어도 종료 0 이다. Docker 가 없는 환경에서 이미지·컨테이너 시험이 조용히 빠지면 검증하지 않은 것이 통과로
센다(platform ADR 0019, deploy run-self-checks.sh 의 77=SKIP 규약). Docker 가 필요한 시험은 엔진에 닿지 못하면 실패하거나, 리포 정본 실행이 skip 을 비0(77)로 바꿔야 한다.
센다(시험 파일: tests/·test-*/·e2e*/·test_*·*.test.*·*smoke* 등):
  P 파이썬 skip(pytest.skip, mark.skipif, unittest.skip/skipIf/skipUnless, self.skipTest, importorskip)이 Docker 단서와 같은 줄 또는 앞 4줄 안에 있다
  R Docker 단서가 있는 if 바로 뒤(3줄 안)의 맨 return(파이썬·JS) — 단언 없이 끝난다
  J JS/TS t.skip(·test.skip·it.skip·describe.skip·{ skip: … }·context.skip 이 Docker 단서와 같은 줄 또는 앞 4줄 안에 있다
  S 셸 docker 확인(command -v docker, docker info, which docker) 뒤 4줄 안의 exit 0·return 0·맨 exit
Docker 단서: docker(대소문자 무관)·have_docker·docker_ok·docker_ready 등 이름. 단서 줄이 `exit 77`·`sys.exit(77)`·raise·fail·assert 면 세지 않는다.
리포 정본 실행이 skip 을 비0으로 바꾸는 장치(SKIP_RC, 근거 파일을 실제로 읽어 확인):
  synthetic-data tests/conftest.py: pytest_sessionfinish 가 TOOLS_MISSING_MARK('[도구 없음: 종료 코드 77]')를 단 skip 이 있으면 exitstatus 를 77 로 바꾼다
    → skip 문 앞뒤 4줄에 TOOLS_MISSING_MARK 가 있는 것만 인정(표지 없는 skip 은 그대로 0 이므로 센다)
  deploy scripts/unittest_skip_rc.py: main() 이 skipTest 가 하나라도 있으면 77 로 끝난다 → `from unittest_skip_rc import main` 이 있는 시험 파일만 인정
  근거 파일이 없거나 표지가 사라지면 인정하지 않는다.
허용 목록(ALLOW, 빈 목록에서 시작). 사용: check-docker-skip.py [--self-test]. 종료 0 통과, 1 위반."""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _checklib as L  # noqa: E402

ALLOW = {}
DOCKER = re.compile(r"docker", re.I)
PY_SKIP = re.compile(r"\bpytest\.skip\s*\(|\.mark\.skipif\s*\(|\bskipif\s*\(|\bunittest\.skip\w*\s*\(|@(unittest\.)?skip(If|Unless)?\s*\(|\.skipTest\s*\(|\bimportorskip\s*\(")
JS_SKIP = re.compile(r"\b(t|test|it|describe|context|suite)\s*\.\s*skip\s*\(|\bskip\s*:\s*[^,}]|\bctx\.skip\s*\(")
NONZERO = re.compile(r"exit\s*\(?\s*77|\bexit\s+[1-9]|\braise\b|\bthrow\b|\bassert\b|\bfail\s*\(|\bprocess\.exit\s*\(\s*[1-9]")
SH_CHECK = re.compile(r"command\s+-v\s+docker|\bdocker\s+(info|version)\b|\bwhich\s+docker|type\s+docker")
SH_ZERO = re.compile(r"\b(exit|return)(\s+0\b|\s*(;|$|\}|\bfi\b))")


def skip_rc(a, rel, text, lines, i):
    """리포 정본 실행이 이 skip 을 77 로 바꾸는가(근거 파일을 읽어 확인)."""
    if a == "synthetic-data":
        conf = L.WS / a / "tests/conftest.py"
        if conf.is_file() and "session.exitstatus = 77" in conf.read_text(encoding="utf-8"):
            return any("TOOLS_MISSING_MARK" in x for x in lines[max(0, i - 5):i + 4])
    if a == "deploy":
        impl = L.WS / a / "scripts/unittest_skip_rc.py"
        if impl.is_file() and "SKIP_RC = 77" in impl.read_text(encoding="utf-8"):
            return bool(re.search(r"from\s+unittest_skip_rc\s+import\s+main", text))
    return False


def window(lines, i, n=4):
    return "\n".join(lines[max(0, i - 1 - n):i])


def scan(a, rel, text):
    if not L.TEST_FILE.search(rel):
        return []
    lg = L.lang(rel, text)
    if lg not in ("py", "js", "sh") or not DOCKER.search(text):
        return []
    lines = L.strip_js_comments(text) if lg == "js" else L.strip_hash_comments(text)
    out = []
    for i, ln in enumerate(lines, 1):
        w = window(lines, i)
        if lg == "py" and PY_SKIP.search(ln) and DOCKER.search(w) and not skip_rc(a, rel, text, lines, i):
            out.append((i, "P", "Docker 없음을 skip 으로 처리 — 실패시키거나 정본 실행이 77 로 끝나게 한다"))
        elif lg == "js" and JS_SKIP.search(ln) and DOCKER.search(w):
            out.append((i, "J", "Docker 없음을 skip 으로 처리 — 실패시키거나 정본 실행이 77 로 끝나게 한다"))
        elif lg in ("py", "js") and re.match(r"\s*return\s*;?\s*$", ln):
            prev = "\n".join(lines[max(0, i - 4):i - 1])
            if re.search(r"\bif\b", prev) and DOCKER.search(prev) and not NONZERO.search(prev):
                out.append((i, "R", "Docker 없음에서 단언 없이 return — 시험이 통과로 센다"))
        elif lg == "sh" and SH_ZERO.search(re.sub(r"\"[^\"]*\"|'[^']*'", "", ln)) and not NONZERO.search(ln):
            prev = "\n".join(lines[max(0, i - 5):i])
            if SH_CHECK.search(prev):
                out.append((i, "S", "docker 확인 실패 뒤 exit 0 — 77 이나 실패로 끝낸다"))
    return out


def self_test():
    bad = []
    pos = [("tests/test_a.py", "@pytest.mark.skipif(shutil.which('docker') is None, reason='x')\ndef test_a(): pass\n"),
           ("tests/test_a.py", "def test_a():\n    if not _docker_ok():\n        pytest.skip('docker 없음')\n"),
           ("tests/test_a.py", "pytestmark = pytest.mark.skipif(not docker_ready(), reason='Docker 없음')\n"),
           ("tests/test_a.py", "class T(unittest.TestCase):\n    def test_a(self):\n        if shutil.which('docker') is None:\n            self.skipTest('no docker')\n"),
           ("tests/test_a.py", "def test_a():\n    if not have_docker():\n        return\n    run()\n"),
           ("test/a.test.ts", "test('img', { skip: !hasDocker() }, () => {});\nconst d = 'docker';\n"),
           ("test/a.test.ts", "test('img', (t) => {\n  if (!dockerOk) { t.skip('no docker'); return; }\n});\n"),
           ("scripts/smoke.sh", "if ! command -v docker >/dev/null; then\n  echo skip\n  exit 0\nfi\n")]
    neg = [("tests/test_a.py", "@pytest.mark.skipif(sys.platform == 'win32', reason='x')\ndef test_a(): pass\n"),
           ("tests/test_a.py", "def test_a():\n    if not _docker_ok():\n        pytest.fail('docker 없음')\n"),
           ("pkg/a.py", "if not have_docker():\n    pytest.skip('docker')\n"),
           ("scripts/smoke.sh", "if ! command -v docker >/dev/null; then\n  echo skip\n  exit 77\nfi\n"),
           ("scripts/smoke.sh", "if ! docker info >/dev/null; then\n  echo 'no docker' >&2\n  exit 1\nfi\n"),
           ("test/a.test.ts", "// docker\ntest('x', () => { assert.ok(1); });\n"), ("tests/test_a.py", "# docker\n# pytest.skip('docker')\n")]
    for rel, t in pos:
        if not scan("z", rel, t):
            bad.append(f"놓침 {rel} {t!r}")
    for rel, t in neg:
        if scan("z", rel, t):
            bad.append(f"거짓양성 {rel} {t!r}")
    syn = "def test_a():\n    if not have_docker():\n        pytest.skip(f'{TOOLS_MISSING_MARK} docker')\n"
    if (L.WS / "synthetic-data/tests/conftest.py").is_file() and scan("synthetic-data", "tests/test_a.py", syn):
        bad.append("synthetic-data 77 표지 skip 을 셌다")
    if not scan("synthetic-data", "tests/test_a.py", syn.replace("{TOOLS_MISSING_MARK} ", "")):
        bad.append("synthetic-data 표지 없는 skip 을 놓침")
    dep = "from unittest_skip_rc import main\nclass T:\n    def test(self):\n        if not shutil.which('docker'):\n            self.skipTest('docker')\n"
    if (L.WS / "deploy/scripts/unittest_skip_rc.py").is_file() and scan("deploy", "scripts/test_a.py", dep):
        bad.append("deploy unittest_skip_rc 사용 파일을 셌다")
    return bad


if __name__ == "__main__":
    sys.exit(L.run("Docker 없음 skip(rc=0)", scan, self_test, ALLOW, pathlib.Path(__file__).name))
