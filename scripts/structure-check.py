#!/usr/bin/env python3
"""영역 구조 검사(DESIGN.md 6절, D117). 모든 영역을 같은 기준으로 본다. 읽기만 한다.
사용: python3 head/scripts/structure-check.py [영역 이름 또는 리포 경로 ...]   (비우면 areas.json의 코드 영역 전부. 경로를 주면 그 작업 트리·clone을 본다)
종료 코드: 0 전부 통과, 1 위반 있음.
"""
import json
import pathlib
import posixpath
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
NON_AREAS = {"head", "boundary-contracts", "link"}   # 영역이 아닌 헤드 소유물(문서·계약·통신 기반 라이브러리)
HTTP_PY = re.compile(r"^\s*(from|import)\s+(openit_link|boundary_contracts\.clients|urllib\.request|http\.client|http\.server|requests|waitress|wsgiref)\b", re.M)
HTTP_TS = re.compile(r"\bfetch\s*\(|from\s+['\"](node:)?http['\"]")
ENTRY = re.compile(r"(^|/)(__main__|main|app|server|config|settings|migrate|cli|index|setup|conftest|sw)\.(py|ts)$|(^|/)migrations?/")
# sw: 서비스 워커 스크립트. 브라우저가 페이지와 따로 실행하는 독립 시작점이다(W3C Service Workers, navigator.serviceWorker.register 의 스크립트 URL).
TEST_SH = re.compile(r"(^|/)(tests?|test-e2e)/|(^|/)(test[-_]|smoke|e2e)[^/]*\.sh$|(^|/)[^/]*(smoke|e2e)[^/]*\.sh$")   # 시험 셸은 진입점의 근거가 아니다
DOCKER_INSTR = {"ENTRYPOINT", "CMD", "RUN", "HEALTHCHECK"}   # 이 줄들이 실행하는 파일만 진입점이다(COPY·LABEL·주석·ENV 에 이름이 나와도 아니다)
BUILD_SH = re.compile(r"\bDockerfile\b|\bdocker\s+build\b|\$\{?DOCKER\}?\s+build\b|\bbuildx\b")   # Dockerfile 을 부르는 이미지 빌드 스크립트
TOKEN = re.compile(r"[^\s\"'\[\],;|&()<>`]+")


def _norm_ref(t):
    """셸·Dockerfile 토큰에서 경로를 꺼낸다: 따옴표·$VAR/·${VAR}/·$(...)/·./ 앞머리를 떼고, '/' 가 없는 낱말(이름만)은 경로가 아니라 버린다."""
    t = t.strip("\"'")
    t = re.sub(r"^(\$\{?\w+\}?|\$\(.*?\))/+", "", t)
    t = re.sub(r"^(\./)+", "", t)
    return t if "/" in t else None


def _instructions(text):
    """Dockerfile 을 (명령, 인자) 목록으로. 줄 이음(\\)을 잇고 주석 줄을 버린다."""
    out, cur = [], ""
    for ln in text.splitlines():
        if not cur and ln.lstrip().startswith("#"):
            continue
        cur += ln.rstrip()
        if cur.endswith("\\"):
            cur = cur[:-1] + " "
            continue
        m = re.match(r"\s*([A-Za-z]+)\s+(.*)$", cur)
        if m:
            out.append((m.group(1).upper(), m.group(2)))
        cur = ""
    return out


def _container_map(repo_files, df, instrs):
    """COPY/ADD 로 이미지 안 경로 -> 리포 파일. 원본은 Dockerfile 폴더 기준(없으면 리포 루트 기준). --from= 은 다른 단계라 뺀다."""
    out, workdir = {}, "/"
    ddir = posixpath.dirname(df)
    fset = set(repo_files)
    for ins, args in instrs:
        if ins == "WORKDIR":
            w = args.strip().strip("\"'")
            workdir = w if w.startswith("/") else posixpath.join(workdir, w)
        if ins not in ("COPY", "ADD") or "--from" in args:
            continue
        toks = [t.strip("\"'") for t in TOKEN.findall(args) if not t.startswith("--")]
        if len(toks) < 2:
            continue
        *srcs, dest = toks
        dest = dest if dest.startswith("/") else posixpath.join(workdir, dest)
        for src in srcs:
            for root in (ddir, ""):
                sp = posixpath.normpath(posixpath.join(root, src)) if root else posixpath.normpath(src)
                if sp in fset:
                    out[posixpath.join(dest, posixpath.basename(sp)) if dest.endswith("/") or len(srcs) > 1 else dest] = sp
                    break
                pre = sp.rstrip("/") + "/"
                under = [f for f in fset if f.startswith(pre)]
                if under:
                    for f in under:
                        out[posixpath.join(dest, f[len(pre):])] = f
                    break
    return out


def launched(repo, fs):
    """이미지·빌드가 **경로로** 실행하는 코드 파일은 그 프로그램의 진입점이다. 근거(시험 셸·tests/ 는 뺀다):
      1. Dockerfile 의 ENTRYPOINT·CMD·RUN·HEALTHCHECK 줄이 부르는 경로(이미지 안 경로는 COPY 로 리포 파일에 대응시킨다)
      2. 이미지에 COPY 된 셸(엔트리포인트·상태 확인·이미지가 가진 명령)의 본문이 부르는 경로
      3. package.json scripts 가 부르는 경로
      4. 이미지 빌드 스크립트(Dockerfile 을 부르는 .sh)가 부르는 경로
    components/·wiring/ 아래 파일과 __init__.py 는 진입점으로 인정하지 않는다(컴포넌트는 진입점이 아니라 진입점이 가져다 쓰는 부품이다, D104).
    왜 경로인가: 이름(basename)만 맞춰 보면 주석·LABEL·사용법 문구·무관한 셸에 이름이 나오기만 해도 통과해 구조 검사가 구멍이 난다(2026-11-09 Opus 검토).
    왜 이 근거인가: db/gen.py 같은 이미지 빌드 생성기와 컨테이너 시작 때 도는 설정 생성기는 영역 서비스의 컴포넌트가 아니라 이미지가 직접 실행하는 프로그램이다(2026-11-09 헤드 결정)."""
    fset = set(fs)
    root = base(repo)

    def read(f):
        return (root / f).read_text(encoding="utf-8", errors="replace")

    found = set()

    def ref(t, cmap, script_dir):
        n = _norm_ref(t)
        if not n:
            return
        if n.startswith("/") and n in cmap:
            found.add(cmap[n])
            return
        for cand in (n, posixpath.normpath(posixpath.join(script_dir, n)) if script_dir else n):
            if cand in fset:
                found.add(cand)

    def shell_body(f, cmap, seen):
        if f in seen or TEST_SH.search(f):
            return
        seen.add(f)
        for ln in read(f).splitlines():
            ln = ln.strip()
            if ln.startswith("#"):
                continue
            for t in TOKEN.findall(ln):
                ref(t, cmap, posixpath.dirname(f))

    for df in (f for f in fs if posixpath.basename(f).startswith("Dockerfile") and not re.search(r"(^|/)(tests?|test-e2e)/", f)):
        instrs = _instructions(read(df))
        cmap = _container_map(fs, df, instrs)
        seen = set()
        for ins, args in instrs:
            if ins in DOCKER_INSTR:
                for t in TOKEN.findall(args):
                    ref(t, cmap, "")
        for src in cmap.values():   # 이미지에 들어간 셸(ENTRYPOINT 로 지정한 것 포함)은 그 이미지의 명령이다(예: --entrypoint 로 부르는 selfcheck)
            if src.endswith(".sh"):
                shell_body(src, cmap, seen)
    for f in fs:
        if f.endswith(".sh") and not TEST_SH.search(f) and BUILD_SH.search(read(f)):
            for ln in read(f).splitlines():
                if not ln.strip().startswith("#"):
                    for t in TOKEN.findall(ln):
                        ref(t, {}, posixpath.dirname(f))
        if posixpath.basename(f) == "package.json" and "node_modules/" not in f:
            try:
                scripts = (json.loads(read(f)).get("scripts") or {}).values()
            except ValueError:
                scripts = []
            for v in scripts:
                for t in TOKEN.findall(str(v)):
                    ref(t, {}, posixpath.dirname(f))
    return {f for f in found if f.endswith((".py", ".ts")) and not re.search(r"/(components|wiring)/", "/" + f) and not f.endswith("__init__.py")}


def areas():
    d = json.loads((ROOT / "head" / "shared" / "areas.json").read_text(encoding="utf-8"))["areas"]
    names = [a["name"] if isinstance(a, dict) else a for a in d]
    return [n for n in names if n not in NON_AREAS and (ROOT / n / ".git").exists()]


def base(repo):
    p = pathlib.Path(repo)
    return p if p.is_absolute() or (p.exists() and (p / ".git").exists()) else ROOT / repo


def files(repo):
    out = subprocess.run(["git", "-C", str(base(repo)), "ls-files"], capture_output=True, text=True).stdout.split("\n")
    return [f for f in out if f and "node_modules/" not in f]


def check(repo):
    fs = files(repo)
    code = [f for f in fs if f.endswith((".py", ".ts")) and not re.search(r"(^|/)(tests?|test)/|(^|/)test_|\.test\.ts$|(^|/)scripts/|\.d\.ts$|(^|/)conftest\.py$", f)]
    bad = []
    entries = launched(repo, fs)
    dirs = {name: [f for f in fs if f"/{name}/" in f"/{f}"] for name in ("schemas", "types", "components", "wiring")}
    for name, got in dirs.items():
        if not got:
            bad.append(f"{name}/ 없음")
    comps = [f for f in code if "/components/" in f"/{f}"]
    comp_names = {pathlib.Path(f).stem for f in comps}
    for f in comps:
        t = (base(repo) / f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?:from|import)\s+[\w.]*components[./](\w+)|from\s+['\"][./]*(?:components/)?(\w+)['\"]", t):
            other = m.group(1) or m.group(2)
            if other in comp_names and other != pathlib.Path(f).stem:
                bad.append(f"{f}: 다른 컴포넌트 {other}를 import")
    for f in code:
        t = (base(repo) / f).read_text(encoding="utf-8", errors="replace")
        uses = HTTP_PY.search(t) if f.endswith(".py") else HTTP_TS.search(t)
        if uses and not pathlib.Path(f).name.startswith("link_") and not ENTRY.search(f) and f not in entries:
            bad.append(f"{f}: 통신 컴포넌트(link_*) 밖에서 HTTP")
    for f in code:
        if not re.search(r"/(components|wiring|types|ui)/", f"/{f}") and not ENTRY.search(f) and f not in entries and not f.endswith("__init__.py"):   # ui/: 화면 부품(DESIGN.md 3절)
            bad.append(f"{f}: components/·wiring/·types/·ui/·진입점 어디에도 속하지 않음")
    schemas = [f for f in fs if re.search(r"(^|/)schemas/[^/]+\.json$", f)]
    for s in schemas:
        stem = pathlib.Path(s).name.replace(".schema.json", "").replace(".json", "")
        ex = [f for f in fs if re.search(rf"schemas/examples/{re.escape(stem)}\.(valid|invalid)", f)]
        if not any(".valid" in e for e in ex) or not any(".invalid" in e for e in ex):
            bad.append(f"{s}: 통과·거부 예시가 모두 있지 않음")
    return bad


def self_test():
    """가짜 리포로 launched() 의 인정·불인정을 본다. 변이는 이 판정을 되돌리면 여기서 실패해야 한다."""
    import tempfile
    files = {
        # 인정: 이미지 빌드 생성기(RUN 이 이미지 안 경로로 부름), 엔트리포인트 셸 본문이 부르는 것, 이미지에 들어간 셸(--entrypoint 로 부르는 명령)이 부르는 것,
        #       이미지 빌드 스크립트가 경로로 부르는 것, package.json scripts 가 부르는 것
        "db/Dockerfile": "FROM x\nCOPY database.json gen.py /work/\nRUN python /work/gen.py /work/database.json /out\n",
        "db/gen.py": "", "db/database.json": "{}",
        "Dockerfile": "FROM x\nCOPY entry.sh /usr/local/bin/entry.sh\nCOPY gen_cfg.py /usr/local/bin/gen_cfg.py\nCOPY chk.sh /usr/local/bin/chk\nCOPY chk.py /usr/local/bin/chk.py\n"
                      "COPY copyonly.py /app/copyonly.py\nCOPY tests/img.sh /t/img.sh\n# RUN python /usr/local/bin/cmt.py\nCOPY cmt.py /usr/local/bin/cmt.py\n# lonely.py 는 주석에만 있다\nLABEL note=\"lonely.py\"\nENTRYPOINT [\"/usr/local/bin/entry.sh\"]\n",
        "entry.sh": "#!/bin/sh\n# python /usr/local/bin/cmt.py\nexec python /usr/local/bin/gen_cfg.py \"$@\"\n",
        "gen_cfg.py": "", "chk.sh": "#!/bin/sh\nexec python /usr/local/bin/chk.py\n", "chk.py": "", "copyonly.py": "", "lonely.py": "",
        "scripts/build-image.sh": "#!/bin/sh\ndocker build -f Dockerfile .\npython tools/mk.py out\necho bare_name.py\n",
        "tools/mk.py": "", "bare_name.py": "",
        "tests/img.sh": "#!/bin/sh\npython tools/via_test_sh.py\n", "tools/via_test_sh.py": "",   # 이미지에 들어간 시험 셸은 근거가 아니다
        "scripts/helper.sh": "#!/bin/sh\npython tools/helper_only.py\n", "tools/helper_only.py": "",   # Dockerfile 을 안 부르는 일반 셸은 근거가 아니다
        "cmt.py": "",
        "package.json": "{\"scripts\": {\"gen\": \"tsx tools/gen.ts\"}}", "tools/gen.ts": "",
        # 불인정: 시험 셸만 부르는 파일, components/·wiring/ 파일, __init__.py, 이름만 나오는 파일
        "scripts/test-all.sh": "python tools/only_test.py\npython pkg/components/x.py\nbuild: docker build -f Dockerfile .\npython tools/test_only.py\n",
        "tests/run.sh": "python tools/only_test2.py\n",
        "tools/only_test.py": "", "tools/test_only.py": "", "tools/only_test2.py": "",
        "pkg/components/x.py": "", "pkg/wiring/w.py": "", "pkg/__init__.py": "", "pkg/plain.py": "",
        "tools/gen.sh": "#!/bin/sh\npython pkg/components/x.py\npython pkg/wiring/w.py\npython pkg/__init__.py\n",   # Dockerfile 을 안 부르는 셸은 근거가 아니다
    }
    # components·wiring·__init__ 가 Dockerfile 에서 직접 불려도 인정하지 않는다
    files["Dockerfile"] += "RUN python /app/pkg/components/x.py && python /app/pkg/wiring/w.py && python /app/pkg/__init__.py\nCOPY pkg/ /app/pkg/\n"
    want = {"db/gen.py", "gen_cfg.py", "chk.py", "tools/mk.py", "tools/gen.ts"}
    with tempfile.TemporaryDirectory() as t:
        d = pathlib.Path(t)
        for rel, body in files.items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            (d / rel).write_text(body, encoding="utf-8")
        got = launched(str(d), sorted(files))
    bad = []
    if got != want:
        bad.append(f"빠짐 {sorted(want - got)} 넘침 {sorted(got - want)}")
    print("self-test:", "OK" if not bad else bad)
    return not bad


def main(argv):
    if "--self-test" in argv:
        return 0 if self_test() else 1
    targets = argv or areas()
    total = 0
    for r in targets:
        bad = check(r)
        total += len(bad)
        print(f"{r}: {'통과' if not bad else f'위반 {len(bad)}건'}")
        for b in bad[:15]:
            print(f"  - {b}")
        if len(bad) > 15:
            print(f"  ... 그 밖 {len(bad) - 15}건")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
