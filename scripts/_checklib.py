"""헤드 정적 점검 공용 틀(2026-11-09). 점검 스크립트 check-strict-json-entry·check-like-version·check-error-values·
check-component-wiring-import·check-docker-skip·check-hand-contract-types·check-real-time-tests 가 쓴다.
왜 한 곳: 영역 목록(areas.json 정본)·추적 파일(git ls-files)·제외 폴더·허용 목록·종료 코드 규약을 점검마다 따로 두면 범위가 갈린다(D117 '같은 뜻은 한 번').
제외 폴더: node_modules·.venv·venv·build·vendor(남의 코드·생성 산출물, 영역이 쓴 코드가 아니다), head/progress(헤드 작업 기록·리포 사본).
허용 목록: 점검마다 {"영역/경로:줄": "이유"}. 줄이 바뀌면 다시 위반으로 뜬다(이유를 다시 확인하게 하려는 것).
종료 코드: 0 통과, 1 위반 또는 self-test 실패, 2 사용 오류."""
import json
import pathlib
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parents[2]
EXCLUDE = re.compile(r"(^|/)(node_modules|\.venv|venv|build|vendor)/")
# 시험 파일: 폴더 tests/·test/·test-*/·e2e*/·__tests__/, 이름 test_*·*_test.*·*.test.*·*.spec.*·conftest.py·*smoke*
TEST_FILE = re.compile(r"(^|/)(tests?|test-[\w-]+|e2e[\w-]*|__tests__)/|(^|/)(test_[^/]*|[^/]*_test\.[^/]*|[^/]*\.(test|spec)\.[^/]*|conftest\.py|[^/]*smoke[^/]*)$")
# 생성물: 계약에서 생성한 타입(types/contract/), 생성 검증기(*validators.cjs). 손으로 쓴 코드가 아니다(워크스페이스 CLAUDE.md 스키마 배치).
GENERATED = re.compile(r"(^|/)types/contract/|(^|/)[^/]*validators(\.gen)?\.cjs$|\.gen\.[cm]?[jt]s$")
GEN_MARK = re.compile(r"generated|자동 생성|생성물|DO NOT EDIT|손으로 고치지", re.I)


def generated(rel, text):
    """생성물: 경로 형(GENERATED) 또는 머리 5줄의 생성 표지."""
    return bool(GENERATED.search(rel) or GEN_MARK.search("\n".join(text.splitlines()[:5])))
PY = (".py",)
JS = (".js", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".tsx", ".jsx")
SH = (".sh", ".bash")


def areas():
    d = json.loads((WS / "head/shared/areas.json").read_text(encoding="utf-8"))
    return [a["name"] for a in (d["areas"] if isinstance(d, dict) else d)]


def lang(rel, text):
    first = text.split("\n", 1)[0]
    suf = pathlib.PurePath(rel).suffix
    if rel.endswith(PY) or (not suf and re.match(r"#!.*python", first)):
        return "py"
    if rel.endswith(JS) or (not suf and re.match(r"#!.*node", first)):
        return "js"
    if rel.endswith(SH) or (not suf and re.match(r"#!.*(ba)?sh\b", first)):
        return "sh"
    if rel.endswith(".sql"):
        return "sql"
    return None


def tracked(skip=()):
    """(영역, 상대 경로, 글) — 영역 리포가 git 으로 추적하는 파일 중 점검할 언어의 것."""
    for a in areas():
        r = subprocess.run(["git", "-C", str(WS / a), "ls-files"], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        if r.returncode != 0:
            continue
        for rel in r.stdout.splitlines():
            if EXCLUDE.search(rel) or (a == "head" and (rel.startswith("progress/") or rel in skip)):
                continue
            f = WS / a / rel
            if not f.is_file() or f.stat().st_size > 2_000_000:
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if lang(rel, text):
                yield a, rel, text


def strip_js_comments(text):
    """주석을 빈칸으로 바꾼다(줄 번호 유지). 따옴표 안의 // 는 남긴다."""
    out, in_block = [], False
    for ln in text.splitlines():
        if in_block:
            if "*/" not in ln:
                out.append("")
                continue
            ln, in_block = ln.split("*/", 1)[1], False
        ln = re.sub(r"/\*.*?\*/", "", ln)
        if "/*" in ln and "*/" not in ln.split("/*", 1)[1]:
            ln, in_block = ln.split("/*", 1)[0], True
        q, i, cut = None, 0, None
        while i < len(ln):
            c = ln[i]
            if q:
                if c == "\\":
                    i += 2
                    continue
                if c == q:
                    q = None
            elif c in "\"'`":
                q = c
            elif c == "/" and ln[i + 1:i + 2] == "/":
                cut = i
                break
            i += 1
        out.append(ln if cut is None else ln[:cut])
    return out


def strip_hash_comments(text):
    """# 주석을 지운다(파이썬·셸 줄 단위, 따옴표 밖만)."""
    out = []
    for ln in text.splitlines():
        q = None
        for i, c in enumerate(ln):
            if q:
                if c == q:
                    q = None
            elif c in "\"'":
                q = c
            elif c == "#" and (i == 0 or ln[i - 1].isspace() or ln[:i].strip() == ""):
                ln = ln[:i]
                break
        out.append(ln)
    return out


def run(title, scan, self_test, allow, me):
    """scan(area, rel, text) -> [(줄, 종류, 설명)]. self_test() -> 실패 목록. allow: {"영역/경로:줄": 이유}."""
    st = self_test()
    print(f"self-test: {'OK' if not st else st}")
    if "--self-test" in sys.argv:
        return 0 if not st else 1
    if st:
        return 1
    out, used = [], set()
    for a, rel, text in tracked(skip={"scripts/" + me, "scripts/_checklib.py"}):
        lines = text.splitlines()
        for ln, kind, why in scan(a, rel, text):
            key = f"{a}/{rel}:{ln}"
            if key in allow:
                used.add(key)
                continue
            src = lines[ln - 1].strip()[:140] if 0 < ln <= len(lines) else ""
            out.append(f"{key}: [{kind}] {why} | {src}")
    stale = sorted(set(allow) - used)
    out = sorted(set(out))
    print(f"{title}: 위반 {len(out)}건, 허용 목록 {len(allow)}건(쓰인 것 {len(used)})")
    if stale:
        print("허용 목록 중 지금 해당 줄에 위반이 없는 항목(줄이 옮겨졌거나 고쳐졌다. 목록을 고친다): " + ", ".join(stale))
    print("\n".join(out) if out else "OK")
    return 1 if out or stale else 0
