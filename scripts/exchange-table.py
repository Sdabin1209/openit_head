#!/usr/bin/env python3
r"""교환 전수표 G3: a1 교환 목록을 리포별 표로 나누고(split), 표의 검증 위치를 현재 커밋에 대조하고(check),
a1 에 없는 교환 후보를 다시 찾는다(rescan).

입력: head/progress/rep/a1-exchange-inventory.md 의 '## 교환 목록' 절(판정 목록 앞까지)에 있는 E번호 행(10열).
  쓰는 칸: 번호, 보내는 영역, 받는 영역, 주고받는 것, 계약 스키마 이름.
리포: head/shared/areas.json 의 areas 중 head 를 뺀 것(정본, 사본 목록을 두지 않는다).

split  리포별 표 head/progress/rep/final/exchange/<리포>.md 를 만든다. 보내는/받는 영역 칸에 리포 이름이 나오면 그 리포의 행이다
       (한 행이 여러 리포 표에 들어갈 수 있다). 양쪽 모두 리포 이름이 없으면 _미배정.md 에 넣는다.
       칸: 번호 | 역할 | 상대 | 주고받는 것 | 계약 스키마 | ① 보내는 쪽 계약 검증 | ② 받는 쪽 계약 검증 | ③ 입구 엄격 읽기 |
           ④ 오류에 값 없음 | 해당 없음 이유
       책임: 역할이 '보냄'이면 ①, '받음'이면 ②③④, '보냄·받음'이면 ①②③④. 책임 아닌 칸은 '— (상대 책임)'.
       책임 칸의 처음 값은 '미확인'. 다시 split 하면 이미 채운 칸(①~④·이유)은 번호로 찾아 보존한다(덮어쓰지 않는다).
check  모든 표를 읽어 책임 칸을 본다. rc=1 조건:
       (a) 빈칸·'미확인'·이유 없는 '해당 없음'(이유는 '해당 없음: 이유' 또는 '해당 없음 이유' 칸), 파일:줄 형식이 아닌 값,
           _미배정.md 의 행(리포가 정해지지 않은 교환)
       (b) 적힌 파일:줄(또는 파일:줄-줄)이 그 리포 HEAD 커밋(git show HEAD:path)에 없거나, 그 줄 ±3줄 안에 칸에 맞는 호출이 없다.
       칸에 맞는 호출(정규식, 아래 PATTERNS): ①② 계약 검증기, ③ 엄격 JSON 파서, ④ 값 없는 오류 표지.
rescan 각 리포 HEAD 커밋에서 HTTP 클라이언트·서버 라우트·link_* 컴포넌트·잡 입출력(argv·설정 파일) 지점을 git grep 으로 찾아
       a1 이 한 번도 인용하지 않은 파일, 또는 a1 본문에 없는 라우트 경로 문자열을 후보로 출력한다. 후보가 있으면 rc=1.
--self-test  가짜 리포(임시 git)·가짜 a1·가짜 표로 split 배정·보존, check 의 빈칸·미확인·이유 없는 해당 없음·없는 파일·
       없는 줄·호출 없는 줄·맞는 줄, rescan 의 새 라우트 판정을 시험한다.
종료 코드: 0 통과, 1 위반(또는 새 교환 후보), 2 사용 오류(입력을 못 읽음).
값은 출력하지 않는다: 파일 경로·줄 번호·E번호·칸 이름만 낸다. 비밀·환경 변수 값을 읽지 않는다.
git 은 최소 환경(PATH, LC_ALL)으로 부른다. 상속 환경을 통째로 넘기지 않는다(워크스페이스 CLAUDE.md 자동화 R9.1).
보지 못하는 것: 동적으로 조립한 경로·라우트, 표에 적힌 줄의 호출이 실제로 그 교환 값을 검증하는지(근처 호출 존재만 본다).
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]   # 워크스페이스(head/scripts 의 두 단계 위)
A1 = ROOT / "head/progress/rep/a1-exchange-inventory.md"
OUT = ROOT / "head/progress/rep/final/exchange"
UNASSIGNED = "_미배정"
WINDOW = 3   # 지시(G3): 적힌 줄 ±3줄 안에서 호출을 찾는다

COLS = ["번호", "역할", "상대", "주고받는 것", "계약 스키마",
        "① 보내는 쪽 계약 검증", "② 받는 쪽 계약 검증", "③ 입구 엄격 읽기", "④ 오류에 값 없음", "해당 없음 이유"]
CHECK_COLS = {"①": 5, "②": 6, "③": 7, "④": 8}
REASON_COL = 9
TODO = "미확인"
NOT_MINE = "— (상대 책임)"
# 칸에 맞는 호출. 근거: 계약 CONVENTIONS(validator·ContractValidator·schema_validator, 10절 strict_json/ijson,
# 오류는 스키마 위치·키워드만), link 서버는 HttpContract/contract_service 선언대로 검증한다(a1 '검증 위치' 참고).
PATTERNS = {
    "①": r"[Vv]alidat|ContractValidator|schema_validator|\bcheck\w*\s*\(|HttpContract|contract_service|valueProblem",
    "②": r"[Vv]alidat|ContractValidator|schema_validator|\bcheck\w*\s*\(|HttpContract|contract_service|valueProblem",
    "③": r"strict_json|strict_loads|ijson|max_json_depth|MAX_JSON_(DEPTH|BYTES)",
    "④": r"safe_error|schema_path|\bkeyword\b",
}
REF_RE = re.compile(r"([^\s,;()<>`\[\]|]+):(\d+)(?:\s*[-–]\s*(\d+))?")


def git(repo, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C.UTF-8",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)


def repos(root):
    d = json.loads((root / "head/shared/areas.json").read_text(encoding="utf-8"))
    return [a["name"] for a in d["areas"] if a["name"] != "head"]


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def read_a1(path):
    """'## 교환 목록' 부터 '## 판정 목록' 앞까지의 E번호 행."""
    rows, inside = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.startswith("## 교환 목록")
            continue
        if inside and re.match(r"\|\s*E\d+\s*\|", line):
            c = split_row(line)
            if len(c) != 10:
                raise ValueError(f"a1 행 열 수 {len(c)} (10이어야 한다): {c[0]}")
            rows.append({"no": c[0], "send": c[3], "recv": c[4], "what": c[5], "schema": c[6] or "(a1 공란)"})
    if not rows:
        raise ValueError("a1 에 교환 행이 없다")
    nos = [r["no"] for r in rows]
    if len(set(nos)) != len(nos):
        raise ValueError("a1 교환 목록에 중복 E번호")
    return rows


def names_in(text, names):
    found = []
    for n in sorted(names, key=len, reverse=True):
        if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", text) and n not in found:
            found.append(n)
    return found


def esc(s):
    return s.replace("\n", " ").replace("|", "\\|") if "\\|" not in s else s.replace("\n", " ")


def read_table(path):
    rows = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"\|\s*E\d+\s*\|", line):
            c = split_row(line)
            rows[c[0]] = c
    return rows


def do_split(root, a1, out):
    names = repos(root)
    rows = read_a1(a1)
    a1_hash = hashlib.sha256(a1.read_bytes()).hexdigest()[:12]
    per = {n: [] for n in names}
    per[UNASSIGNED] = []
    for r in rows:
        s, v = names_in(r["send"], names), names_in(r["recv"], names)
        mine = {}
        for n in s:
            mine.setdefault(n, set()).add("보냄")
        for n in v:
            mine.setdefault(n, set()).add("받음")
        if not mine:
            per[UNASSIGNED].append((r, "미배정"))
        for n, roles in mine.items():
            per[n].append((r, "보냄·받음" if len(roles) == 2 else roles.pop()))
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for n, items in per.items():
        path = out / f"{n}.md"
        old = read_table(path)
        if not items:
            if path.exists():
                path.unlink()
            continue
        head = git(root / n, "rev-parse", "--short", "HEAD").stdout.decode().strip() if n != UNASSIGNED else "-"
        lines = [f"# 교환 전수표 G3: {n}", "",
                 f"생성: head/scripts/exchange-table.py split. 입력 a1-exchange-inventory.md(sha256 {a1_hash}), 생성 시 리포 HEAD {head or '?'}.",
                 "책임: 역할 '보냄'은 ①, '받음'은 ②③④, '보냄·받음'은 ①~④. 값은 리포 루트 기준 `경로:줄`(여러 개는 `, `). "
                 "근거가 없으면 `해당 없음: 이유` 또는 '해당 없음 이유' 칸. check 는 HEAD 커밋의 그 줄 ±3줄을 본다.", "",
                 "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
        for r, role in items:
            if role == "보냄":
                other = "→ " + r["recv"]
            elif role == "받음":
                other = "← " + r["send"]
            else:
                other = f"← {r['send']} / → {r['recv']}"
            need = responsible(role)
            cells = [r["no"], role, other, r["what"], r["schema"]]
            prev = old.get(r["no"])
            for k, i in CHECK_COLS.items():
                default = TODO if k in need else NOT_MINE
                keep = prev[i] if prev and len(prev) == len(COLS) and prev[i] not in ("", TODO, NOT_MINE) and k in need else None
                cells.append(keep or default)
            reason = prev[REASON_COL] if prev and len(prev) == len(COLS) else ""
            cells.append(reason)
            lines.append("| " + " | ".join(esc(c) for c in cells) + " |")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        summary.append(f"{n}: {len(items)}행")
    print(f"split: a1 교환 {len(rows)}행 -> {out}")
    for s in summary:
        print("  " + s)
    return 0


def responsible(role):
    if role == "보냄":
        return {"①"}
    if role == "받음":
        return {"②", "③", "④"}
    return {"①", "②", "③", "④"}   # 보냄·받음, 미배정(누가 맡을지 정해야 한다)


class Files:
    """리포 HEAD 커밋의 파일 줄(캐시)."""
    def __init__(self, root):
        self.root, self.cache = root, {}

    def lines(self, repo, path):
        key = (repo, path)
        if key not in self.cache:
            p = git(self.root / repo, "show", f"HEAD:{path}")
            self.cache[key] = p.stdout.decode("utf-8", "replace").splitlines() if p.returncode == 0 else None
        return self.cache[key]


def check_cell(files, repo, col, cell, reason):
    """오류 문장 목록(값은 싣지 않는다)."""
    v = cell.strip()
    if v in ("", TODO) or TODO in v or v == NOT_MINE:
        return ["빈칸·미확인"]
    if v.startswith("해당 없음"):
        own = v[len("해당 없음"):].strip(" :：-—")
        r = reason.strip()
        if own or (r and r != TODO and r not in ("-", "—")):
            return []
        return ["이유 없는 해당 없음"]
    refs = REF_RE.findall(v)
    if not refs:
        return ["파일:줄 형식 아님"]
    errs = []
    for path, a, b in refs:
        lo, hi = int(a), int(b or a)
        lines = files.lines(repo, path)
        if lines is None:
            errs.append(f"{path}: HEAD 에 파일 없음")
            continue
        if lo < 1 or hi < lo or hi > len(lines):
            errs.append(f"{path}:{a}: HEAD 에 그 줄 없음({len(lines)}줄)")
            continue
        win = "\n".join(lines[max(0, lo - 1 - WINDOW):hi + WINDOW])
        if not re.search(PATTERNS[col], win):
            errs.append(f"{path}:{a}: ±{WINDOW}줄에 {col} 호출 없음")
    return errs


def do_check(root, out):
    if not out.is_dir():
        print(f"사용 오류: 표 폴더 없음 {out}", file=sys.stderr)
        return 2
    names = set(repos(root))
    files = Files(root)
    bad, total = [], 0
    for path in sorted(out.glob("*.md")):
        repo = path.stem
        if repo != UNASSIGNED and repo not in names:
            bad.append(f"{path.name}: areas.json 에 없는 리포")
            continue
        for no, c in read_table(path).items():
            total += 1
            if len(c) != len(COLS):
                bad.append(f"{repo} {no}: 열 수 {len(c)}(10이어야 한다)")
                continue
            if repo == UNASSIGNED:
                bad.append(f"{repo} {no}: 리포 미배정")
                continue
            for col in sorted(responsible(c[1])):
                for e in check_cell(files, repo, col, c[CHECK_COLS[col]], c[REASON_COL]):
                    bad.append(f"{repo} {no} {col}: {e}")
    for b in bad:
        print(b)
    print(f"check: 행 {total}, 위반 {len(bad)}")
    return 1 if bad else 0


# rescan: 교환 지점 표지(코드 파일만). 시험·생성물·문서·잠금 파일은 뺀다.
SCAN = {
    "HTTP 클라이언트": r"boundary_contracts\.clients|import .*Client\b|\w+Client\(|urlopen\(|requests\.(get|post|put|patch|delete)\(|httpx\.|\bfetch\(|http_send|HttpSend",
    "서버 라우트": r"\bRoute\(|HttpContract\(|contract_service|\.route\(|@app\.(get|post|put|delete)|createServer\(",
    "잡 입출력": r"add_argument\(|sys\.argv|run[-_]once|JobsDeclaration|io\.openit\.jobs",
}
SCAN_EXCLUDE = [":!*test*", ":!*tests/*", ":!*fixtures*", ":!*mock-server*", ":!*.md", ":!*.lock", ":!*node_modules*",
                ":!*types/*", ":!*validators.cjs", ":!*contract-validators*", ":!docs/*", ":!*.json"]
CODE_EXT = (".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".go", ".sh", ".yaml", ".yml", ".toml", "Dockerfile", "Caddyfile")
ROUTE_LIT = re.compile(r"""["'`]((?:/v\d+|/ui|/metrics|/healthz|/readyz|/api)(?:/[\w{}<>:.\-*]*)*)["'`]""")


def norm_route(s):
    return re.sub(r"\{[^}]*\}|<[^>]*>|:\w+", "{}", s).rstrip("/") or "/"


def do_rescan(root, a1):
    text = a1.read_text(encoding="utf-8")
    cited = set(re.findall(r"([\w.-]+/[^\s:\]\)|`]+?):\d+", text))
    a1_routes = {norm_route(m) for m in re.findall(r"(/[\w{}<>:.\-*/]+)", text)}
    cands = []
    for repo in repos(root):
        if not (root / repo / ".git").exists():
            continue
        hits = {}
        for kind, pat in SCAN.items():
            p = git(root / repo, "grep", "-n", "-I", "-E", pat, "HEAD", "--", ".", *SCAN_EXCLUDE)
            for line in p.stdout.decode("utf-8", "replace").splitlines():
                m = re.match(r"HEAD:(.+?):(\d+):(.*)", line)
                if m and m.group(1).endswith(CODE_EXT):
                    hits.setdefault(m.group(1), []).append((kind, m.group(2), m.group(3)))
        ls = git(root / repo, "ls-tree", "-r", "--name-only", "HEAD").stdout.decode("utf-8", "replace").splitlines()
        for f in ls:
            if re.search(r"(^|/)link_\w+\.(py|ts|js|mjs)$", f) and not re.search(r"test", f):
                hits.setdefault(f, []).append(("link_* 컴포넌트", "1", ""))
        for f, hs in sorted(hits.items()):
            if f"{repo}/{f}" not in cited:
                kinds = sorted({k for k, _, _ in hs})
                cands.append(f"{repo}/{f}:{hs[0][1]}: a1 이 인용하지 않은 파일 ({', '.join(kinds)})")
            for k, ln, src in hs:
                if k != "서버 라우트" and "link_" not in f:
                    continue
                for lit in ROUTE_LIT.findall(src):
                    if norm_route(lit) not in a1_routes:
                        cands.append(f"{repo}/{f}:{ln}: a1 에 없는 라우트 {lit}")
    for c in sorted(set(cands)):
        print(c)
    print(f"rescan: 새 교환 후보 {len(set(cands))}")
    return 1 if cands else 0


# ---------------------------------------------------------------- self-test
def self_test():
    fails = []

    def expect(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        (root / "head/shared").mkdir(parents=True)
        (root / "head/shared/areas.json").write_text(json.dumps({"areas": [
            {"name": "head"}, {"name": "alpha"}, {"name": "beta"}]}), encoding="utf-8")
        a = root / "alpha"
        (a / "src").mkdir(parents=True)
        (a / "src/send.py").write_text("\n".join([
            "import x",                                   # 1
            "",                                           # 2
            "def send(doc):",                             # 3
            "    validator('Foo').validate(doc)",         # 4
            "    return post(doc)",                       # 5
            "", "", "", "", "",                           # 6-10
            "def nothing():",                             # 11
            "    return 1",                               # 12
            "", "", "", "",                               # 13-16
            "def recv(raw):",                             # 17
            "    body = strict_json.loads(raw)",          # 18
            "    errs = [e.schema_path for e in v]",      # 19
            "ROUTES = [Route('POST', '/v1/new-thing', h)]",   # 20
        ]) + "\n", encoding="utf-8")
        (a / "src/link_recv.py").write_text("x = 1\n", encoding="utf-8")
        g = ["-c", "user.name=selftest", "-c", "user.email=selftest@invalid", "-c", "core.hooksPath=/dev/null"]
        git(a, "init", "-q")
        git(a, "add", ".")
        git(a, *g, "commit", "-q", "-m", "t")
        # 커밋 뒤 작업 트리만 바꾼 줄은 보지 않아야 한다(HEAD 기준)
        (a / "src/send.py").write_text("changed\n", encoding="utf-8")
        a1 = root / "a1.md"
        hdr = "| 번호 | 출처 | 방향 | 보내는 영역 | 받는 영역 | 주고받는 것 | 계약 | 보 | 받 | 상태 |\n|---|---|---|---|---|---|---|---|---|---|\n"
        a1.write_text("# a1\n## 교환 목록\n" + hdr +
                      "| E0001 | [alpha/src/send.py:4](x) | → | alpha | beta | POST /v1/foo | Foo | | | |\n"
                      "| E0002 | s | → | beta(x)/deploy | alpha/beta | GET /v1/bar | Bar | | | |\n"
                      "| E0003 | s | → | external:누군가 | 미확인 | GET /v1/baz | | | | |\n"
                      "## 판정 목록\n| E0001 | x | y | z |\n", encoding="utf-8")
        out = root / "out"
        expect("split rc=0", do_split(root, a1, out) == 0)
        ta, tb = read_table(out / "alpha.md"), read_table(out / "beta.md")
        tu = read_table(out / f"{UNASSIGNED}.md")
        expect("split: 판정 목록 행은 넣지 않는다(E0001 한 번)", len(ta) == 2 and set(ta) == {"E0001", "E0002"})
        expect("split: alpha E0001 역할 보냄", ta["E0001"][1] == "보냄")
        expect("split: beta E0002 역할 보냄·받음", tb["E0002"][1] == "보냄·받음")
        expect("split: alpha E0002 받음, ① 상대 책임", ta["E0002"][1] == "받음" and ta["E0002"][5] == NOT_MINE)
        expect("split: 리포 없는 행은 미배정", set(tu) == {"E0003"})
        expect("check: 갓 나눈 표는 미확인이라 rc=1", do_check(root, out) == 1)

        f = Files(root)
        cases = [
            ("빈칸", "①", "", "", False),
            ("미확인", "①", TODO, "", False),
            ("이유 없는 해당 없음", "①", "해당 없음", "", False),
            ("해당 없음 + 이유 칸", "①", "해당 없음", "본문 없는 GET", True),
            ("해당 없음: 이유", "②", "해당 없음: 원시 바이트", "", True),
            ("형식 아님", "①", "어딘가에서", "", False),
            ("없는 파일", "①", "src/nope.py:4", "", False),
            ("없는 줄", "①", "src/send.py:999", "", False),
            ("맞는 줄 ①", "①", "src/send.py:4", "", True),
            ("±3 안 ①(줄 7 → 4)", "①", "src/send.py:7", "", True),
            ("±3 밖 ①(줄 12)", "①", "src/send.py:12", "", False),
            ("맞는 줄 ③ strict_json", "③", "src/send.py:18", "", True),
            ("③ 칸에 검증기 줄은 틀림", "③", "src/send.py:4", "", False),
            ("맞는 줄 ④ schema_path", "④", "src/send.py:19", "", True),
            ("여러 값 중 하나라도 틀리면 위반", "①", "src/send.py:4, src/send.py:999", "", False),
            ("줄 범위", "②", "src/send.py:3-5", "", True),
        ]
        for name, col, cell, reason, ok in cases:
            expect(f"check_cell {name}", (check_cell(f, "alpha", col, cell, reason) == []) == ok)

        # 표를 채운 뒤 check rc=0, 다시 split 해도 채운 칸이 남는다
        def fill(path, mapping):
            t = path.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(t):
                c = split_row(line) if line.startswith("| E") else None
                if c and c[0] in mapping:
                    for k, v in mapping[c[0]].items():
                        c[k] = v
                    t[i] = "| " + " | ".join(c) + " |"
            path.write_text("\n".join(t) + "\n", encoding="utf-8")
        fill(out / "alpha.md", {"E0001": {5: "src/send.py:4"},
                                "E0002": {6: "src/send.py:4", 7: "src/send.py:18", 8: "src/send.py:19"}})
        fill(out / "beta.md", {"E0001": {6: "해당 없음", 7: "해당 없음", 8: "해당 없음", 9: "시험 리포에 코드 없음"},
                               "E0002": {5: "해당 없음: 시험", 6: "해당 없음: 시험", 7: "해당 없음: 시험", 8: "해당 없음: 시험"}})
        (out / f"{UNASSIGNED}.md").unlink()
        expect("check: 다 채운 표 rc=0", do_check(root, out) == 0)
        do_split(root, a1, out)
        expect("split 다시: 채운 칸 보존", read_table(out / "alpha.md")["E0001"][5] == "src/send.py:4")
        expect("split 다시: 미배정은 되살아나 check rc=1", do_check(root, out) == 1)

        # rescan: a1 에 없는 라우트·인용 안 된 link_* 파일은 후보
        expect("rescan: 새 교환 후보가 있으면 rc=1", do_rescan(root, a1) == 1)
        a1.write_text(a1.read_text(encoding="utf-8").replace(
            "## 판정 목록", "| E0004 | [alpha/src/link_recv.py:1](x) | → | x | alpha | POST /v1/new-thing | | | | |\n## 판정 목록"),
            encoding="utf-8")
        expect("rescan: a1 에 다 있으면 rc=0", do_rescan(root, a1) == 0)

    print(f"self-test: 실패 {len(fails)}")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", nargs="?", choices=["split", "check", "rescan"])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--a1", type=pathlib.Path, default=A1)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    a = ap.parse_args()
    try:
        if a.self_test:
            return self_test()
        if a.command == "split":
            return do_split(ROOT, a.a1, a.out)
        if a.command == "check":
            return do_check(ROOT, a.out)
        if a.command == "rescan":
            return do_rescan(ROOT, a.a1)
    except (OSError, ValueError, KeyError) as e:
        print(f"사용 오류: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
