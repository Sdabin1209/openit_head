#!/usr/bin/env python3
"""Docker context 해석 실패를 삼키는 코드를 찾는다(워크스페이스 CLAUDE.md 'docker 호출은 프로젝트 자체 설정만', 2026-11-09 codex C2 3묶음).

규칙: 사용자 context 의 엔드포인트를 DOCKER_HOST 로 옮길 때 `docker context inspect` 가 실패하면 기본 엔진으로 조용히 바꾸지 않고 실패해야 한다.
왜: 실패를 삼키면 DOCKER_CONTEXT 로 다른 엔진(원격·TLS·ssh)을 고른 호스트에서 시험·빌드가 기본 엔진에 붙거나, Docker 가 있어야 하는 시험이 조용히 건너뛰어진다.
보는 형(알려진 관용구 세 가지, 새 형이 생기면 여기에 더한다):
  셸: context inspect 가 있는 줄(또는 이어진 줄)에 `|| true` / `|| :`
  JS: context inspect 를 부르는 try 의 catch 가 다시 던지거나 종료하지 않음
  Python: context inspect 를 부르는 subprocess 호출 뒤 같은 함수 안에 check=True 도 returncode 검사도 없음
사용: check-docker-context.py [리포 ...]   (없으면 head/shared/areas.json 의 리포 + boundary-contracts·link 제외 전부), --self-test
종료 코드: 0 위반 없음, 1 위반 있음."""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKIP_DIR = re.compile(r"(^|/)(node_modules|\.venv|build|dist|vendor|wt-[^/]*)/")
INSPECT = re.compile(r"context[\"',\s]+inspect")
ARGV_INSPECT = re.compile(r"[\"']context[\"']\s*,\s*[\"']inspect[\"']")


def _sh(text):
    bad, lines = [], text.splitlines()
    i = 0
    while i < len(lines):
        start, buf = i, lines[i]
        while buf.rstrip().endswith("\\") and i + 1 < len(lines):   # 줄 잇기는 한 명령이다
            i += 1
            buf += "\n" + lines[i]
        if not buf.lstrip().startswith("#") and INSPECT.search(buf) and re.search(r"\|\|\s*(true\b|:(?!\w))", buf):
            bad.append(start + 1)
        i += 1
    return bad


def _js(text):
    bad = []
    for m in INSPECT.finditer(text):
        tail = text[m.end():m.end() + 600]
        c = re.search(r"catch\s*(\([^)]*\))?\s*\{(?P<body>[^{}]*)\}", tail)
        if c and not re.search(r"\bthrow\b|process\.exit|\breturn\s+fail|\bfail\(", c.group("body")):
            bad.append(text.count("\n", 0, m.start()) + 1)
    return bad


def _py(text):
    bad, lines = [], text.splitlines()
    for idx, ln in enumerate(lines):
        if ARGV_INSPECT.search(ln) and not ln.lstrip().startswith("#"):   # 실제 호출(argv 목록)만 본다. 시험의 match="context inspect" 같은 문자열은 호출이 아니다
            window = "\n".join(lines[max(0, idx - 3): idx + 12])
            if not re.search(r"check\s*=\s*True|\.returncode|CalledProcessError", window):
                bad.append(idx + 1)
    return bad


CHECKERS = {".sh": _sh, ".mjs": _js, ".js": _js, ".cjs": _js, ".ts": _js, ".py": _py}


def check_files(root, files):
    out = []
    for f in files:
        if SKIP_DIR.search(f) or pathlib.PurePosixPath(f).name == "check-docker-context.py":
            continue
        fn = CHECKERS.get(pathlib.PurePosixPath(f).suffix)
        if not fn:
            continue
        try:
            text = (root / f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not INSPECT.search(text):
            continue
        out += [f"{f}:{n}" for n in fn(text)]
    return out


def repos():
    d = json.loads((ROOT / "head" / "shared" / "areas.json").read_text(encoding="utf-8"))["areas"]
    names = [a["name"] if isinstance(a, dict) else a for a in d]
    return [n for n in names if (ROOT / n / ".git").exists()]


def self_test():
    import tempfile
    cases = {
        "bad.sh": ('h=$(docker context inspect --format x 2>/dev/null || true)\n', 1),
        "bad2.sh": ('h=$(docker context inspect \\\n  --format x || :)\n', 1),
        "ok.sh": ('h=$(docker context inspect --format x) || { echo "context 해석 실패" >&2; exit 1; }\n# docker context inspect || true\n', 0),
        "bad.mjs": ('try { host = execFileSync("docker", ["context", "inspect"]).trim(); } catch { /* 기본 */ }\n', 1),
        "ok.mjs": ('try { host = execFileSync("docker", ["context", "inspect"]).trim(); } catch (e) { throw new Error("context 해석 실패"); }\n', 0),
        "bad.py": ('r = subprocess.run(["docker", "context", "inspect"], capture_output=True)\nhost = r.stdout\n', 1),
        "ok.py": ('r = subprocess.run(["docker", "context", "inspect"], capture_output=True, check=True)\n', 0),
        "ok3.py": ('with pytest.raises(RuntimeError, match="context inspect"):\n    f()\n', 0),
        "ok2.py": ('r = subprocess.run(["docker", "context", "inspect"], capture_output=True)\nif r.returncode != 0:\n    raise SystemExit(1)\n', 0),
    }
    bad = []
    with tempfile.TemporaryDirectory() as t:
        d = pathlib.Path(t)
        for name, (body, _) in cases.items():
            (d / name).write_text(body, encoding="utf-8")
        for name, (_, want) in cases.items():
            got = len(check_files(d, [name]))
            if got != want:
                bad.append(f"{name}: 기대 {want} 실제 {got}")
    print("self-test:", "OK" if not bad else bad)
    return not bad


def main(argv):
    if "--self-test" in argv:
        return 0 if self_test() else 1
    total = 0
    for r in argv or repos():
        root = ROOT / r
        files = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
        bad = check_files(root, [f for f in files if f])
        total += len(bad)
        for b in bad:
            print(f"{r}/{b}: context 해석 실패를 삼킨다")
    print(f"위반 {total}건")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
