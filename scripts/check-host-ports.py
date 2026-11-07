#!/usr/bin/env python3
"""직접 고른 호스트 포트를 Docker 에 넘기는 코드를 실행 없이 센다(공통 규칙 '고정 포트 금지', 2026-11-07).

왜: 소켓으로 빈 포트를 골라 docker -p 로 넘기면 WSL 에서 비어 있어도 Windows 호스트 예약 범위라 Docker Desktop 이 bind 를 거부한다
(2026-11-07 E2E 사전 점검에서 release-gate DB 이미지 시험이 실제로 실패). 허용하는 방식:
  (1) Docker 배정: -p 127.0.0.1::<포트> / compose 의 빈 호스트 포트 + docker port 로 읽기
  (2) 기동 전에 포트가 설정 값으로 들어가야 할 때만: 그 변수로 Docker 실제 게시를 해 보고 성공했을 때만 쓰기
판정(변수 단위, 주석 줄 무시, Git 추적 + 추적 안 된 새 파일):
  고른 변수   = 소켓 bind(0) 로 얻은 값, 또는 확인 없는 포트 함수($(free_port) 등, 다른 파일에 정의돼 있어도)의 결과
  확인된 변수 = 같은 변수로 'docker run --rm ... -p ...$V... true' 를 실행하고 그 성공에 && 로 이어 쓰는 줄이 있는 변수(|| true 로 실패를 무시하면 확인이 아니다,
                --network none 이 그 줄 어디에 있어도 확인이 아니다: none 망은 게시하지 않는다), 또는 그런 확인을 거쳐 echo 하는 함수의 결과
  위반        = docker -p/--publish·compose 포트·파이썬 f"127.0.0.1:{x}:" 로 고른 변수(확인 안 됨)를 넘기는 줄, 그리고 --network none 으로 게시를 확인하는 줄
한계(정적 점검): 변수를 다른 이름으로 여러 번 옮기거나 파일 사이로 넘기는 흐름은 따라가지 않는다. 자체 시험(--self-test)의 반례 목록이 덮는 범위다.
종료 코드: 0 위반 없음, 1 위반. 사용: check-host-ports.py [<영역>=<작업 트리> ...]
"""
import pathlib
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parents[2]
AREAS = ["boundary-contracts", "link", "model-runtime", "survey-service", "question-authoring", "ops-feedback", "release-gate",
         "model-lab", "synthetic-data", "kiosk-frontend", "admin-console", "platform", "deploy"]
SOCKET_PICK = re.compile(r"\.bind\(\(\s*['\"][0-9.]*['\"]\s*,\s*0\s*\)\)")
ASSIGN_SH = re.compile(r"(?:^|[;{(]\s*|\bdo\s+)(?:export\s+|local\s+)?([A-Za-z_]\w*)=\"?\$\(([^)]*)")
FUNC_DEF = re.compile(r"^\s*([A-Za-z_]\w*)\s*\(\)\s*\{")
PROBE_LINE = re.compile(r"(?i)docker\"?\s+run\s+--rm\b.*\s-p\s")
NONE_NET = re.compile(r"--network[ =]none\b")
PY_FSTR = re.compile(r"""f["'](?:127\.0\.0\.1:|0\.0\.0\.0:)?\{([a-z_]\w*)\}:""")
PY_ASSIGN_SOCKET = re.compile(r"\b([a-z_]\w*)\s*=\s*\w+\.getsockname\(\)\[1\]")
DOCKER_CTX = re.compile(r"(?i)docker|compose|ports:|\[\s*[\"']run[\"']|_sh\(|_docker\(")


def code_lines(text):
    return [(i, l) for i, l in enumerate(text.splitlines(), 1) if not l.lstrip().startswith("#")]


def var_pat(v):
    return r"\$\{?" + re.escape(v) + r"\b\}?"


def verified_vars(lines):
    """같은 변수로 실제 게시해 보고 그 성공에 이어 쓰는 줄에서 확인된 변수(시험한 변수와 그 결과를 받는 변수). '__echo__' 는 확인 뒤 그 값을 echo 했다는 표시."""
    ok = set()
    for _, l in lines:
        if not PROBE_LINE.search(l) or NONE_NET.search(l) or re.search(r"\|\|\s*true", l) or "&&" not in l:
            continue
        for m in re.finditer(r"\s-p\s+[\"']?[^\s\"']*\$\{?([A-Za-z_]\w*)\}?:", l):
            v = m.group(1)
            ok.add(v)
            for a in re.finditer(r"([A-Za-z_]\w*)=" + var_pat(v), l):
                ok.add(a.group(1))
            if re.search(r'echo\s+"?' + var_pat(v), l):
                ok.add("__echo__")
    return ok


def verified_funcs(text):
    """확인을 거쳐 echo 하는 셸 함수 이름(예: docker_free_port, freeport)."""
    out, cur, body = set(), None, []
    for l in text.splitlines():
        m = FUNC_DEF.match(l)
        if m and cur is None:
            cur, body = m.group(1), [l]
            if l.rstrip().endswith("}") and l.count("{") == l.count("}"):
                if "__echo__" in verified_vars(code_lines("\n".join(body))):
                    out.add(cur)
                cur = None
            continue
        if cur:
            body.append(l)
            if re.match(r"^\}", l):
                if "__echo__" in verified_vars(code_lines("\n".join(body))):
                    out.add(cur)
                cur = None
    return out


def scan_text(text, label, p, known_ok_funcs):
    bad = []
    lines = code_lines(text)
    for i, l in lines:
        if NONE_NET.search(l) and PROBE_LINE.search(l):
            bad.append(f"{label}/{p}:{i}: --network none 으로 게시를 확인한다(none 망은 게시하지 않으므로 확인이 아니다)")
    funcs_ok = known_ok_funcs | verified_funcs(text)
    picked = set()
    for _, l in lines:
        for m in ASSIGN_SH.finditer(l):
            v, expr = m.group(1), m.group(2)
            fn = expr.split()[0] if expr.split() else ""
            if SOCKET_PICK.search(expr + l) and "python" in expr or (re.fullmatch(r"\w*free_?port", fn) and fn not in funcs_ok):
                picked.add(v)
        pm = PY_ASSIGN_SOCKET.search(l)
        if pm:
            picked.add(pm.group(1))
    if not picked:
        return bad
    ok = verified_vars(lines)
    for i, l in lines:
        if PROBE_LINE.search(l) and not NONE_NET.search(l):
            continue   # 확인 줄 자체
        for v in sorted(picked - ok):
            sh_pub = re.search(r"(-p|--publish)[ =][\"']?[^\s\"']*" + var_pat(v) + r"[\"']?:", l) and DOCKER_CTX.search(l)
            compose = re.search(r"ports:.*" + var_pat(v), l)
            py = any(x.group(1) == v for x in PY_FSTR.finditer(l))
            if sh_pub or compose or py:
                bad.append(f"{label}/{p}:{i}: 고른 포트 {v} 를 Docker 에 넘기는데 그 변수로 실제 게시 확인을 하지 않았다")
    return bad


def files_of(root):
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True).stdout.splitlines()
    new = subprocess.run(["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.splitlines()
    return sorted(set(tracked) | set(new))


def scan(root: pathlib.Path, label: str):
    texts = {}
    for p in files_of(root):
        if p.endswith((".sh", ".py", ".mjs", ".ts", ".yaml", ".yml")) and "node_modules" not in p:
            try:
                texts[p] = (root / p).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                pass
    known = set()   # 다른 파일(예: lib.sh)에 정의된 확인 함수도 이름으로 안다
    for t in texts.values():
        known |= verified_funcs(t)
    bad = []
    for p, t in texts.items():
        bad += scan_text(t, label, p, known)
    return bad


def self_test():
    import tempfile
    sock = "python3 -c 'import socket;s=socket.socket();s.bind((\"\",0));print(s.getsockname()[1])'"
    cases = {
        "bad.py": ('import socket\ns=socket.socket(); s.bind(("127.0.0.1", 0)); port=s.getsockname()[1]\nargs=["docker","run","-p", f"127.0.0.1:{port}:5432"]\n', True),
        "none.sh": ('docker run --rm --network none -p "127.0.0.1:$p:1" img true && P=$p\n', True),
        "none_after.sh": (f'p=$({sock})\ndocker run --rm -p "127.0.0.1:$p:1" --network none img true && P=$p\ndocker run -d -p "127.0.0.1:$P:80" app\n', True),
        "other_var.sh": (f'a=$({sock})\nb=$({sock})\ndocker run --rm -p "$a:1" img true && A=$a\ndocker run -d -p "127.0.0.1:$b:80" app\n', True),
        "ignored.sh": (f'p=$({sock})\ndocker run --rm -p "$p:1" img true || true\ndocker run -d -p "127.0.0.1:$p:80" app\n', True),
        "comment.sh": (f'p=$({sock})\n# docker run --rm -p "$p:1" img true && Q=$p\ndocker run -d -p "127.0.0.1:$p:80" app\n', True),
        "lib.sh": (f'free_port() {{ {sock}; }}\n', False),
        "uses_lib.sh": ('P=$(free_port)\ndocker run -d -p "127.0.0.1:$P:80" app\n', True),
        "ok.sh": (f'p=$({sock})\ndocker run --rm -p "127.0.0.1:$p:1" img true && PORT=$p\ndocker run -d -p "127.0.0.1:$PORT:8080" app\n', False),
        "okfunc.sh": (f'docker_free_port() {{\n  local p\n  for t in 1 2; do p=$({sock})\n    "$DOCKER" run --rm -p "127.0.0.1:$p:1" img true >/dev/null 2>&1 && {{ echo "$p"; return 0; }}\n  done\n}}\nG=$(docker_free_port)\ndocker run -d -p "127.0.0.1:$G:80" app\n', False),
        "assigned.py": ('args=["docker","run","-p","127.0.0.1::5432"]\n', False),
        "mkdir.sh": (f'p=$({sock})\nmkdir -p "$p"\n', False),
    }
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d); subprocess.run(["git", "init", "-q", str(d)], check=True)
        for n, (t, _) in cases.items():
            (d / n).write_text(t)
        subprocess.run(["git", "-C", str(d), "add", "bad.py", "lib.sh"], check=True)   # 나머지는 추적 안 된 새 파일(그래도 본다)
        got = {b.split(":")[0].rsplit("/", 1)[-1] for b in scan(d, "t")}
        want = {n for n, (_, b) in cases.items() if b}
        ok = got == want
        print("self-test", "통과" if ok else f"실패: 놓침 {sorted(want - got)}, 오탐 {sorted(got - want)}")
        return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    trees = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    bad = []
    for a in AREAS:
        root = pathlib.Path(trees.get(a, WS / a))
        if (root / ".git").exists():
            bad += scan(root, a)
    print(f"직접 고른 호스트 포트 점검: 위반 {len(bad)}건")
    for b in bad:
        print(b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
