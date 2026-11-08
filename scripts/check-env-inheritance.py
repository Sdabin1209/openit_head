#!/usr/bin/env python3
"""규칙 C45(RUNTIME R9.1): 시험·잡은 상속받은 환경 변수를 통째로 쓰거나 하위 프로세스에 넘기지 않는다. 필요한 이름만 담은 최소 환경을
만들어 넘긴다(IN-ENV 는 스키마에 있는 이름만). 이름 하나를 읽는 것(os.environ["A"], .get, in)은 통째가 아니다.
보는 파일: 영역 리포(areas.json 의 목록, git 이 추적하는 파일)의 .py .js .mjs .cjs .ts .mts .cts .tsx .jsx .go .sh .bash 와
확장자 없는 셸·파이썬·node 스크립트(첫 줄 #!). 가상환경·node_modules 는 추적 대상이 아니라 보지 않는다.
언어별 규칙(종류 표지):
  W 환경 통째 사용 — Python 은 ast 로 본다: os.environ(또는 from os import environ, import os as x 의 별칭)이 인덱싱·.get/.setdefault/.pop/
    .update/.clear·`in`·len/bool 이 아닌 쓰임(인자·env=·**·|·for 순회·.items/.keys/.values/.copy·대입·반환)이면 통째다. JS/TS 는 process.env 가
    .이름·[이름]·`const {A} = process.env` 가 아닌 쓰임이면 통째다(env: process.env, ...process.env, Object.entries(process.env) 등). Go 는 os.Environ().
  I 상속 — env 를 주지 않거나 env=None 인 하위 프로세스 호출: Python subprocess.run/Popen/call/check_call/check_output/getoutput, os.system/popen/
    exec*/spawn*(e 가 없는 것), asyncio.create_subprocess_*; JS child_process spawn/exec/execFile/fork(Sync 포함)의 인자에 env 가 없는 것.
    **kwargs 로 넘기면 알 수 없으므로 세지 않는다.
  S 셸 — exec 뒤에 env -i 가 없는 exec(파일 기술자 지정 exec 3>&1 은 제외), -i 가 없는 env 명령(env VAR=x cmd, env | …: 환경을 통째로 물려주거나
    찍는다), export -p·declare -x·printenv(환경 전체 출력). 셸의 일반 명령은 모두 환경을 물려받으므로 명령마다 세지 않는다.
범위(W·I·S·X 모두): R9.1 은 RUNTIME 표상 '시험·잡의 실행' 규칙이라 시험·잡 파일에서만 센다. 시험·잡 파일(TESTJOB)은 tests/·test-*/·e2e*/·jobs?/·smoke 폴더,
  test_*·*_test.*·*.test.*·*.spec.*·*smoke*·*e2e*·*run-once*·*job* 이름, 그리고 제품 모듈 안의 잡 진입이다: 영역 deploy-jobs.json(JobsDeclaration)의
  argv 가 `python -m <모듈>` 로 부르는 모듈 파일과 그 모듈이 한 단계 가져오는 같은 패키지 모듈(components/·wiring/·__init__ 제외). 근거: deploy 의 잡 실행은
  JobsDeclaration 의 argv 를 그대로 실행한다(CONVENTIONS 13절). 서비스 진입점·개발 도구는 배포가 준 환경(*Env 스키마의 이름)을 물려받는 것이 정상이다(12-Factor III).
셈하지 않는 것(거짓 양성 방지, 모두 자기 줄이 아니라 쓰임으로 판정):
  - 이름만 읽는 함수에 넘김: NAME_ONLY 목록(함수 본문을 읽어 확인한 근거는 목록 주석). egress_proxy_from(os.environ)은 CONVENTIONS 13절이 정한 R9.1 준수 방식이다.
  - 주입 기본값: `X = os.environ if X is None else X`(대입·인자·`(a if a is not None else os.environ).get` 등 어느 자리든), `dict(os.environ if base is None else base)`,
    `def f(env=os.environ)`, JS `function f(base = process.env)`. 주입된 환경을 그 뒤 통째로 넘기는 일은 따라가지 않는다(보지 않는 것).
  - 허용 목록으로 거른 환경: `{k: v for k, v in os.environ.items() if k in <허용 이름>}` 만(제외 목록·접두 조건은 통째 전달로 센다).
  - 시험 격리용 지우기: 환경을 훑으며 delenv·pop·del 하는 순회, `env -u NAME cmd`, os.environ.update(저장해 둔 사본).
  - 통째 복사를 지역 이름에 담은 경우(env = dict(os.environ) 등): 담는 줄이 아니라 그 이름이 이름으로만 읽히는지(.get·[]·in·NAME_ONLY 호출) 본다. 통째로 넘기면 그 줄이 위반이다.
  - 셸 heredoc 본문(다른 언어 코드·데이터)과 따옴표 안 글자, 주석.
예외 표시: 줄(Python 은 호출·표현식의 줄 범위 또는 바로 윗줄)에 'R9.1-예외' 가 있으면 센다 안 한다(이유를 같은 줄에 적는다).
보지 않는 것(이유): 셸 heredoc·python -c 문자열 안에 든 다른 언어 코드(셸 규칙은 본문을 건너뛴다), 주입된 환경을 그 뒤 통째로 넘기는 일,
const base = process.env; 처럼 JS 에서 이름에 담은 뒤의 쓰임(첫 줄에서 잡는다), Go 의 exec.Command 에 cmd.Env 를 안 준 상속(자료 흐름 추적이 필요하다),
셸에서 환경 변수를 이름으로 읽는 일반 명령, 파싱에 실패한 Python 파일(줄 정규식으로 W 만 본다).
사용: check-env-inheritance.py [--self-test]. 종료 0 통과, 1 위반(줄 목록), 2 사용 오류."""
import ast
import json
import pathlib
import posixpath
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parents[2]
MARK = "R9.1-예외"
PY_SUB = {"run", "Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"}
OS_INHERIT = {"system", "popen", "execv", "execvp", "execl", "execlp", "spawnv", "spawnvp", "spawnl", "spawnlp"}
ASYNC_SUB = {"create_subprocess_exec", "create_subprocess_shell"}
ENV_OK_ATTR = {"get", "setdefault", "pop", "update", "clear", "__getitem__", "__setitem__", "__delitem__", "__contains__"}
LEN_OK = {"len", "bool"}
JS_EXT = (".js", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".tsx", ".jsx")
LINE_PAT = re.compile(r"env\s*=\s*os\.environ\b(?!\s*[.\[])|os\.environ\.(copy|items|keys|values)\(|\{\s*\*\*\s*os\.environ|dict\(\s*os\.environ\b")   # ast 파싱 실패 때만


def _alias_maps(tree):
    mods, names = {}, {}   # mods: 지역 이름→모듈, names: 지역 이름→(모듈, 원래 이름)
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                mods[a.asname or a.name.split(".")[0]] = a.name.split(".")[0] if not a.asname else a.name
        elif isinstance(n, ast.ImportFrom) and n.module:
            for a in n.names:
                names[a.asname or a.name] = (n.module, a.name)
    return mods, names


# 이름으로만 읽는 함수: environ 을 통째로 받아도 그 안에서 키 이름으로만 읽거나 필요한 이름만 골라 새 환경을 만든다(읽어서 확인한 근거).
#   egress_proxy_from            boundary_contracts.clients: OPENIT_EGRESS_PROXY 이름 하나만 꺼낸다. CONVENTIONS 13절이 R9.1 을 지키는 방식으로 정했다
#   validate_server_env          ops_feedback/config.py: OPS_ 접두 이름만 걸러 스키마로 검증한다
#   env_violations               release_gate/main.py: GATE_·OPENIT_·PORT 이름만 걸러 계약 Env 스키마로 검증하고 어긴 이름만 돌려준다
#   _setting                     ops_feedback/wiring/pgbase.py: environ.get(이름) 하나
#   server_settings              ops_feedback/wiring/check_settings.py: OPS_PORT·OPS_MAX_CONNECTIONS·OPS_READYZ_CACHE_SECONDS 를 .get 으로만 읽는다
#   backup_job.run/restore       release_gate/components/backup_job.py: _restic_env 가 쓸 이름만 골라 하위 프로세스 환경을 새로 만든다
#   backup_flow.run/restore      ops_feedback·question_authoring wiring/backup_flow.py: _restic 이 필요한 변수만으로 하위 프로세스 환경을 새로 만든다(R9.1 주석)
#   read_secret                  boundary_contracts/secrets.py: NAME_FILE 과 NAME 두 이름만 읽는다(D84)
#   require_verify               ops_feedback/wiring/storage.py: OPS_DB_SCHEMA 한 이름을 읽고 그 값만 바꾼 사본을 돌려준다. 사본은 아래 open_*·build_from_config 로만 간다
#   build_from_config            ops_feedback/wiring/build.py: env 를 read_secret·open_*_store·egress_proxy·_http_client(read_secret)로만 넘긴다
#   open_log_store/open_failure_store  ops_feedback/wiring/storage.py: read_secret 과 pgbase._setting(environ.get(이름))으로만 읽는다
#   _open                        ops_feedback/admin/__main__.py: read_secret 과 open_*_store 로만 넘긴다
# 함수가 바뀌어 통째로 넘기기 시작하면 이 목록의 근거가 깨지므로 이름만이 아니라 함수 본문을 읽어 확인한 것만 둔다.
NAME_ONLY = {"egress_proxy_from", "validate_server_env", "env_violations", "_setting", "server_settings",
             "backup_job.run", "backup_job.restore", "backup_flow.run", "backup_flow.restore",
             "read_secret", "require_verify", "build_from_config", "open_log_store", "open_failure_store", "_open"}


def py_hits(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    mods, names = _alias_maps(tree)
    lines = text.splitlines()
    parent = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parent[c] = p

    def is_environ(n):
        if isinstance(n, ast.Attribute) and n.attr in ("environ", "environb") and isinstance(n.value, ast.Name):
            return mods.get(n.value.id) == "os"
        return isinstance(n, ast.Name) and names.get(n.id, ("", ""))[0] == "os" and names[n.id][1] in ("environ", "environb")

    def dotted(f):
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            return f"{f.value.id}.{f.attr}"
        if isinstance(f, ast.Attribute):
            return f.attr
        return ""

    def name_only_call(p, n):
        if isinstance(p, ast.keyword):   # f(environ=os.environ): 키워드 값의 부모는 keyword 노드이고 그 부모가 호출이다
            p = parent.get(p)
        if not isinstance(p, ast.Call) or not (n in p.args or any(k.value is n for k in p.keywords)):
            return False
        d = dotted(p.func)
        return d in NAME_ONLY or d.rsplit(".", 1)[-1] in {x for x in NAME_ONLY if "." not in x}

    def inject_default(n, p):
        """주입 가능한 환경의 기본값 네 형: `X = os.environ if X is None else X`(대입·인자·`(environ if environ is not None else os.environ).get` 등
        어느 자리든), `dict(os.environ if base is None else base)`, 함수 인자 기본값 `def f(env=os.environ)`. 이름만 읽는 배선 관용구이고 그 뒤
        주입된 환경을 통째로 넘기는 일은 따라가지 않는다(보지 않는 것)."""
        if isinstance(p, ast.arguments):
            return n in p.defaults or n in p.kw_defaults
        return isinstance(p, ast.IfExp) and isinstance(p.test, ast.Compare) and isinstance(p.test.left, ast.Name) \
            and len(p.test.ops) == 1 and isinstance(p.test.ops[0], (ast.Is, ast.IsNot)) \
            and (isinstance(p.orelse, ast.Name) and p.orelse.id == p.test.left.id and p.body is n
                 or isinstance(p.body, ast.Name) and p.body.id == p.test.left.id and p.orelse is n)

    def filtered_items(n, p):
        """`{k: v for k, v in os.environ.items() if …}`: 조건으로 거른 환경(허용 목록으로 최소 환경 만들기, 또는 시험 격리용 접두 변수 지우기)."""
        if not (isinstance(p, ast.Attribute) and p.value is n and p.attr == "items"):
            return False
        c = parent.get(p)
        g = parent.get(c)
        if not (isinstance(c, ast.Call) and isinstance(g, ast.comprehension) and c is g.iter and g.ifs):
            return False
        # 허용 목록만 인정한다(codex C2 H1): 모든 if 가 `키 in <허용 이름 모음>` 이어야 한다. 제외 목록(!=, not in)·접두 조건·항상 참은 통째 전달과 같다
        key = g.target.elts[0] if isinstance(g.target, ast.Tuple) and g.target.elts else g.target
        return isinstance(key, ast.Name) and all(
            isinstance(cond, ast.Compare) and len(cond.ops) == 1 and isinstance(cond.ops[0], ast.In)
            and isinstance(cond.left, ast.Name) and cond.left.id == key.id
            and isinstance(cond.comparators[0], (ast.Tuple, ast.List, ast.Set, ast.Name, ast.Attribute))
            for cond in g.ifs)

    def isolation_loop(n):
        """`for k in list(os.environ): if k.startswith("OPS_"): monkeypatch.delenv(k)` 와 `for k in [k for k in os.environ if …]: os.environ.pop(k)`:
        환경을 훑어 시험 격리용 변수를 지우는 순회(지우기만 하고 통째로 넘기지 않는다). 순회 본문에 delenv·pop·del 이 있을 때만 인정한다."""
        child, cur = n, parent.get(n)
        while cur is not None:
            if isinstance(cur, ast.For) and cur.iter is child:
                return any(isinstance(x, ast.Delete) or (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr in ("delenv", "pop"))
                           for b in cur.body for x in ast.walk(b))
            if isinstance(cur, (ast.stmt, ast.Lambda)):
                return False
            child, cur = cur, parent.get(cur)
        return False

    def ok_use(n, p):
        return (isinstance(p, ast.Subscript) and p.value is n) \
            or (isinstance(p, ast.Attribute) and p.value is n and p.attr in ENV_OK_ATTR) \
            or (isinstance(p, ast.Compare) and n in p.comparators and all(isinstance(o, (ast.In, ast.NotIn)) for o in p.ops)) \
            or (isinstance(p, ast.Call) and n in p.args and isinstance(p.func, ast.Name) and p.func.id in LEN_OK) \
            or name_only_call(p, n) \
            or (isinstance(p, ast.Call) and n in p.args and isinstance(p.func, ast.Attribute) and p.func.attr == "update" and is_environ(p.func.value))   # os.environ.update(저장해 둔 사본): 시험 뒤 환경 되돌리기

    def marked(n):
        lo, hi = n.lineno, getattr(n, "end_lineno", n.lineno)
        return any(MARK in lines[i - 1] for i in range(max(1, lo - 1), min(len(lines), hi) + 1))

    def callee(call):
        f = call.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            return mods.get(f.value.id, ""), f.attr
        if isinstance(f, ast.Name) and f.id in names:
            return names[f.id]
        return "", ""

    def scope_of(n):
        while n in parent:
            n = parent[n]
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.Module)):
                return n
        return tree

    def whole_expr(n):
        """n(os.environ)을 통째 복사하는 식의 꼭대기: dict(environ, …), environ.copy(), {**environ, …}."""
        p = parent.get(n)
        if isinstance(p, ast.Call) and isinstance(p.func, ast.Name) and p.func.id == "dict" and n in p.args:
            return p
        if isinstance(p, ast.Attribute) and p.value is n and p.attr == "copy" and isinstance(parent.get(p), ast.Call):
            return parent[p]
        if isinstance(p, ast.Dict) and any(k is None and v is n for k, v in zip(p.keys, p.values)):
            return p
        return None

    out, aliases = [], {}   # aliases: (범위, 이름) -> 만든 줄. 통째 복사를 지역 이름에 담으면 쓰이는 자리에서 본다(이름으로만 읽으면 통과, 넘기면 그 줄이 위반)
    for n in ast.walk(tree):
        if is_environ(n):
            p = parent.get(n)
            if ok_use(n, p) or inject_default(n, p) or filtered_items(n, p) or isolation_loop(n) or marked(n):
                continue
            top = whole_expr(n)
            holder = parent.get(top) if top is not None else p
            if (top is not None or isinstance(p, (ast.Assign, ast.AnnAssign))) and isinstance(holder, (ast.Assign, ast.AnnAssign)) \
                    and getattr(holder, "value", None) is (top if top is not None else n):
                tgt = holder.targets[0] if isinstance(holder, ast.Assign) and len(holder.targets) == 1 else getattr(holder, "target", None)
                if isinstance(tgt, ast.Name):
                    aliases[(scope_of(n), tgt.id)] = n.lineno
                    continue
            out.append((n.lineno, "W"))
        elif isinstance(n, ast.Call):
            mod, fn = callee(n)
            inherit = (mod == "subprocess" and fn in PY_SUB) or (mod == "os" and fn in OS_INHERIT) or (mod == "asyncio" and fn in ASYNC_SUB)
            if inherit and not any(k.arg is None for k in n.keywords) and not marked(n):
                envkw = [k for k in n.keywords if k.arg == "env"]
                if not envkw or (isinstance(envkw[0].value, ast.Constant) and envkw[0].value.value is None):
                    out.append((n.lineno, "I"))
    if aliases:
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and (scope_of(n), n.id) in aliases:
                p = parent.get(n)
                if not (ok_use(n, p) or inject_default(n, p) or marked(n)):
                    out.append((n.lineno, "W"))
    return sorted(set(out))


def strip_js_comments(text):
    out, in_block = [], False
    for ln in text.splitlines():
        if in_block:
            if "*/" not in ln:
                out.append("")
                continue
            ln = ln.split("*/", 1)[1]
            in_block = False
        ln = re.sub(r"/\*.*?\*/", "", ln)
        if "/*" in ln:
            ln = ln.split("/*", 1)[0]
            in_block = True
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


JS_WHOLE = re.compile(r"process\.env\b(?!\s*(\.\s*[A-Za-z_$]|\[|\?\.))")
JS_DEFAULT_PARAM = re.compile(r"[(,]\s*\w+\s*=\s*process\.env\s*(?=[,)])")
JS_DESTRUCT = re.compile(r"\}\s*=\s*process\.env\b")
JS_SPAWN = re.compile(r"(?<![.\w$])(spawn|spawnSync|exec|execSync|execFile|execFileSync|fork)\s*\(|\b(?:child_process|childProcess|cp)\.(spawn|spawnSync|exec|execSync|execFile|execFileSync|fork)\s*\(")


def js_hits(text):
    lines = strip_js_comments(text)
    raw = text.splitlines()
    out = []
    for i, ln in enumerate(lines):
        ln = JS_DEFAULT_PARAM.sub("", ln)   # 주입 기본값 function f(base = process.env): 이름만 읽는 배선 관용구
        if (JS_WHOLE.search(ln) and not JS_DESTRUCT.search(ln)) and MARK not in raw[i]:
            out.append((i + 1, "W"))
    if "child_process" in text:
        joined = "\n".join(lines)
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln) + 1)
        for m in JS_SPAWN.finditer(joined):
            depth, j = 0, m.end() - 1
            while j < len(joined) and j - m.end() < 4000:
                if joined[j] == "(":
                    depth += 1
                elif joined[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            args = joined[m.end():j]
            lineno = joined.count("\n", 0, m.start()) + 1
            if not re.search(r"\benv\b", args) and not re.search(r"\.\.\.\s*\w+", args) and MARK not in raw[lineno - 1]:
                out.append((lineno, "I"))
    return sorted(set(out))


def sh_strip(ln):
    q = None
    for i, c in enumerate(ln):
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "#" and (i == 0 or ln[i - 1].isspace()):
            return ln[:i]
    return ln


SH_EXEC = re.compile(r"(?:^|[;&|(]\s*|\bthen\s+|\bdo\s+)exec\s+(?!env\s+-i\b)(?![0-9]*[<>])")
SH_ENV = re.compile(r"(?:^|[;&|(`]\s*|\$\(\s*|\bexec\s+|\bsudo\s+)env(?![\w./=-])(?!\s*[=(])(?!\s+-[iu]\b)")   # env -i 는 최소 환경, env -u 는 시험 격리용 변수 지우기(허용)
SH_DUMP = re.compile(r"\bexport\s+-p\b|\bdeclare\s+-x\b|\bprintenv\b")


def sh_unquote(ln):
    """따옴표 안의 글자는 명령이 아니다(echo "exec env" 등)."""
    return re.sub(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'", '""', ln)


HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")


def sh_hits(text):
    out, tag = [], None
    for i, raw in enumerate(text.splitlines(), 1):
        if tag:   # heredoc 본문은 다른 언어 코드(python 등)나 데이터이지 셸 명령이 아니다
            if raw.strip() == tag:
                tag = None
            continue
        if i == 1 and raw.startswith("#!"):
            continue
        ln = sh_unquote(sh_strip(raw))
        hd = HEREDOC.search(sh_strip(raw))
        if hd:
            tag = hd.group(2)
        if MARK in raw:
            continue
        if SH_ENV.search(ln) or SH_DUMP.search(ln):
            out.append((i, "S"))
        elif SH_EXEC.search(ln):
            out.append((i, "X"))
    return out


def go_hits(text):
    return [(i, "W") for i, ln in enumerate(text.splitlines(), 1) if re.search(r"\bos\.Environ\(\)", ln) and not ln.lstrip().startswith("//") and MARK not in ln]


# 범위: R9.1 은 '시험·잡의 실행' 규칙이다. 상속(I)·셸 exec(X)는 시험·잡 파일에서만 센다. 서비스 컨테이너의 진입점·개발 도구는 배포가 준 환경
# (*Env 스키마의 이름)을 물려받는 것이 정상이고 12-Factor III 가 그 방식이다. 통째 사용(W)·환경 찍기(S)는 어디서든 센다.
TESTJOB = re.compile(r"(^|/)(tests?|test-[\w-]+|e2e[\w-]*|jobs?|smoke)(/|$)|(^|/)(test[_-][^/]*|[^/]*_test\.[^/]*|[^/]*\.(test|spec)\.[^/]*|[^/]*(smoke|e2e|run-once)[^/]*|[^/]*job[^/]*)$")


def hits_for(name, text):
    first = text.split("\n", 1)[0]
    if name.endswith(".py") or (not pathlib.PurePath(name).suffix and re.match(r"#!.*python", first)):
        h = py_hits(text)
        if h is None:
            return [(i, "W") for i, ln in enumerate(text.splitlines(), 1) if LINE_PAT.search(ln) and not ln.lstrip().startswith("#") and MARK not in ln]
        return h
    if name.endswith(JS_EXT) or (not pathlib.PurePath(name).suffix and re.match(r"#!.*node", first)):
        return js_hits(text)
    if name.endswith((".sh", ".bash")) or (not pathlib.PurePath(name).suffix and re.match(r"#!.*(ba)?sh\b", first)):
        return sh_hits(text)
    if name.endswith(".go"):
        return go_hits(text)
    return []


def job_files(root, fs):
    """제품 모듈 안의 잡 진입: 영역의 deploy-jobs.json(JobsDeclaration)이 `python -m <모듈>` 로 부르는 모듈 파일과, 그 모듈이 바로(한 단계) 가져다 쓰는
    같은 패키지의 모듈(release_gate/__main__.py 가 부르는 main.py 등). 근거: deploy 의 잡 실행은 JobsDeclaration 의 argv 를 그대로 실행한다(CONVENTIONS 13절).
    components/·wiring/ 파일은 한 단계 따라가기에서 뺀다(다른 컴포넌트·배선은 잡 진입이 아니다)."""
    f = pathlib.Path(root) / "deploy-jobs.json"
    if "deploy-jobs.json" not in fs or not f.exists():
        return set()
    try:
        jobs = json.loads(f.read_text(encoding="utf-8")).get("jobs", [])
    except ValueError:
        return set()
    fset, out = set(fs), set()

    def resolve(mod):
        path = mod.replace(".", "/")
        return {x for x in fset if x in (path + ".py", path + "/__main__.py") or x.endswith(("/" + path + ".py", "/" + path + "/__main__.py"))}
    for j in jobs:
        argv = j.get("argv") or []
        if "-m" not in argv or argv.index("-m") + 1 >= len(argv):
            continue
        for mf in resolve(argv[argv.index("-m") + 1]):
            out.add(mf)
            try:
                tree = ast.parse((pathlib.Path(root) / mf).read_text(encoding="utf-8"))
            except (SyntaxError, ValueError, OSError):
                continue
            pkg = posixpath.dirname(mf)
            for n in ast.walk(tree):
                if not isinstance(n, ast.ImportFrom):
                    continue
                mod2 = n.module or ""
                if n.level:
                    d = pkg
                    for _ in range(n.level - 1):
                        d = posixpath.dirname(d)
                    sub = mod2.replace(".", "/")
                    cands = [posixpath.join(d, sub) + ".py"] if sub else []
                else:
                    cands = list(resolve(mod2)) if mod2 else []
                for c in cands:
                    if c in fset and not re.search(r"/(components|wiring)/", "/" + c) and not c.endswith("__init__.py"):
                        out.add(c)
    return out


def in_scope(rel, jobs=frozenset()):
    return bool(TESTJOB.search(rel)) or rel in jobs


def areas():
    d = json.loads((WS / "head/shared/areas.json").read_text())
    return [a["name"] for a in (d["areas"] if isinstance(d, dict) else d)]


OUTSCOPE = {}


def scan(root=WS):
    out = []
    me = pathlib.Path(__file__).name
    for a in areas():
        r = subprocess.run(["git", "-C", str(root / a), "ls-files"], capture_output=True, text=True)
        if r.returncode != 0:
            continue
        tracked = r.stdout.splitlines()
        jobs = job_files(root / a, tracked)
        for rel in tracked:
            if rel.startswith("progress/") or rel.endswith("/" + me) or rel == "scripts/" + me:
                continue
            f = root / a / rel
            if not f.is_file():
                continue
            suf = f.suffix
            if suf and suf not in (".py", ".sh", ".bash", ".go") and not rel.endswith(JS_EXT):
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            lines = text.splitlines()
            for ln, kind in hits_for(rel, text):
                if in_scope(rel, jobs):
                    out.append((a, kind, f"{a}/{rel}:{ln}: [{kind}] {lines[ln - 1].strip()[:100]}"))
                else:
                    OUTSCOPE[kind] = OUTSCOPE.get(kind, 0) + 1
    return out


def self_test():
    py_pos = ["for k in list(os.environ):\n    print(k)", "for k in os.environ:\n    x[k] = 1", "snap = dict(os.environ)\nsend(snap)", "os.environ.items()", "x.update(os.environ)", "os.environ | {'A': '1'}", "dict(os.environ)", "{**os.environ, 'A': '1'}",
              "subprocess.run(c, env=os.environ)", "os.environ.copy()", "e = os.environ\nsend(e)", "e = dict(os.environ)\nsubprocess.run(c, env=e)", "e = os.environ.copy()\nfor k in e: pass", "e = {**os.environ, 'A': '1'}\nsend(**e)", "for k in os.environ: pass", "return os.environ",
              "subprocess.run(['x'])", "sp.check_output(['x'])", "run(['x'])", "dict(environ)", "dict(E)", "Popen(c, env=None)", "os.system('x')",
              "subprocess.run(['x'],\n    check=True)", "e = os.environ if flag else {}", "dict(os.environ, A='1')",
              # 제외 목록·접두 조건·항상 참은 허용 목록이 아니다(codex C2 H1)
              "{k: v for k, v in os.environ.items() if not k.startswith('OPS_')}", "subprocess.run(c, env={k: v for k, v in os.environ.items() if k != 'PYTHONPATH'})",
              "{k: v for k, v in os.environ.items() if k not in ('X',)}", "{k: v for k, v in os.environ.items() if True}"]
    py_neg = ["os.environ['A']", "os.environ.get('A')", "'A' in os.environ", "os.environ.setdefault('A', 'b')", "os.environ['A'] = 'b'",
              "subprocess.run(c, env=env)", "subprocess.run(c, **kw)", "os.environ.update({'A': 'b'})", "x = 1  # R9.1-예외: 이유",
              "# os.environ.copy()", "s = 'os.environ.copy()'", "x = dict(os.environ)  # R9.1-예외: 이유", "subprocess.run(['x'],  # R9.1-예외: 이유\n    check=True)", "# R9.1-예외: 이유\nx = dict(os.environ)", "subprocess.run(['x'], env={'PATH': p})", "len(os.environ)",
              "subprocess.run(['x'],\n    env=env)", "'''\nos.environ.copy()\n'''", "d = {}.get('x')", "re.run(['x'])",
              "def f(env=None):\n    env = os.environ if env is None else env", "def f(env=os.environ):\n    pass",
              # 이름만 읽는 함수에 넘김(NAME_ONLY): 근거는 NAME_ONLY 주석
              "egress_proxy_from(os.environ)", "bc.egress_proxy_from(os.environ)", "validate_server_env(os.environ)", "env_violations(os.environ, cmd='x')",
              "pgbase._setting('A', os.environ)", "read_secret('A', environ=os.environ)", "build_from_config(cfg, require_verify(os.environ))", "e = dict(os.environ)\n_open(a, e)\nopen_log_store(e, 'p')", "backup_job.run(os.environ, now=n)", "backup_flow.restore(os.environ, 'latest')", "server_settings(os.environ, tokens=[])",
              # 주입 기본값 네 형
              "go(os.environ if environ_ is None else environ_)", "(environ_ if environ_ is not None else os.environ).get('A')",
              "def f(base=None):\n    env = dict(os.environ if base is None else base)\n    return env", "def f(env=os.environ):\n    return env.get('A')",
              # 조건으로 거른 환경: 허용 목록(최소 환경), 시험 격리용 접두 변수 지우기
              "for k in list(os.environ):\n    if k.startswith('A'):\n        monkeypatch.delenv(k)", "for k in [k for k in os.environ if k.startswith('A')]:\n    os.environ.pop(k)",
              "snap = dict(os.environ)\nos.environ.update(snap)",
              "{k: v for k, v in os.environ.items() if k in ('PATH', 'HOME')}", "{k: v for k, v in os.environ.items() if k in ALLOWED}",
              # 통째 복사를 이름에 담고 이름으로만 읽거나 이름만 읽는 함수에 넘김
              "env = os.environ\nv = env.get('A')\nx = env['B']\ny = 'C' in env", "env = dict(os.environ)\nvalidate_server_env(env)\nenv['A'] = 'b'\nenv.pop('X', None)"]
    pre = "import os, subprocess\nimport subprocess as sp\nfrom subprocess import run, Popen\nfrom os import environ\nfrom os import environ as E\n"
    js_pre = "const cp = require('child_process');\n"
    js_pos = ["spawn(c, {env: process.env})", "const e = {...process.env, A: 1}", "Object.assign({}, process.env)", "Object.entries(process.env)",
              "const e = process.env;", "spawn('x')", "cp.execSync('x')", "cp.spawn('x',\n  ['a'])", "child_process.fork('x.js')"]
    js_neg = ["const h = process.env.HOME", "const a = process.env['A']", "const {A} = process.env;", "spawn('x', {env: {PATH: p}})",
              "const ok = re.exec(s)", "// const e = {...process.env}", "/* process.env */", "cp.spawn('x',\n  {env: m})", "spawn('x') // R9.1-예외: 이유",
              "const h = process.env?.HOME", "const e = {...process.env} // R9.1-예외: 이유",
              "function f(base = process.env) { return base.A; }", "const g = (a, base = process.env) => base.A;", "export function dockerEnv(base = process.env) {\n  return { ...base, X: 1 };\n}"]
    sh_pos = ["cat <<EOF\nx\nEOF\nenv FOO=1 cmd", "exec python3 app.py", "env FOO=1 cmd", "env | sort", "export -p", "printenv", "if x; then exec ./run; fi", "x=$(env)", "sudo env A=1 cmd", "declare -x"]
    sh_neg = ["env = lambda s: s", "env(s)", "exec env -i PATH=$P python3 x", "env -i A=1 cmd", "#!/usr/bin/env bash", "env -u OPS_X cmd", "python3 - <<'E'\nprintenv\nexec python x\nenv FOO=1 cmd\nE", "cat <<-EOF\n\texec python x\n\tEOF", "exec 3>&1", "exec >log", "docker run --env-file x img",
              "docker run -e NAME img", "# env FOO=1", "echo .env", "export A=1", "cmd # env x", "exec python x  # R9.1-예외: 이유", "ENV_X=1 cmd"]
    bad = []

    def run(kind, name, text, want, jobs=frozenset()):
        got = any(in_scope(name, jobs) for _, k in hits_for(name, text))
        if got != want:
            bad.append(("놓침: " if want else "거짓양성: ") + kind + " " + repr(text[:60]))
    for t in py_pos:
        run("py", "tests/a.py", pre + t + "\n", True)
    for t in py_neg:
        run("py", "tests/a.py", pre + t + "\n", False)
    for t in js_pos:
        run("js", "tests/a.mjs", js_pre + t + "\n", True)
    for t in js_neg:
        run("js", "tests/a.mjs", js_pre + t + "\n", False)
    for t in sh_pos:
        run("sh", "tests/a.sh", t + "\n", True)
    for t in sh_neg:
        run("sh", "tests/a.sh", t + "\n", False)
    run("scope", "tools/a.py", pre + "subprocess.run(['x'])\n", False)
    run("scope", "tools/a.py", pre + "dict(os.environ)\n", False)
    run("scope", "tools/a.sh", "exec python x\n", False)
    run("scope", "db/entrypoint.sh", "exec docker-entrypoint.sh \"$@\"\n", False)
    run("scope", "tools/a.sh", "env FOO=1 cmd\n", False)
    run("scope", "tools/a.sh", "printenv\n", False)
    run("scope", "pkg/main.py", pre + "dict(os.environ)\n", False)
    run("scope", "pkg/main.py", pre + "dict(os.environ)\n", True, jobs=frozenset({"pkg/main.py"}))   # 잡 진입 모듈은 범위 안
    run("scope", "scripts/run-once-x.sh", "exec python x\n", True)
    run("scope", "src/x/jobs/a.py", pre + "subprocess.run(['x'])\n", True)
    run("sh-quote", "tests/a.sh", "echo \"exec env FOO\" ; grep 'env = x' f\n", False)
    run("go", "tests/a.go", "e := os.Environ()\n", True)
    run("go", "tests/a.go", "e := os.Getenv(\"A\")\n// os.Environ()\n", False)
    run("shebang", "tests/tool", "#!/usr/bin/env python3\nimport os\nx = dict(os.environ)\nfoo(x)\n", True)
    run("py-parse-fail", "tests/a.py", "def (:\nenv=os.environ.copy()\n", True)
    # 잡 진입 모듈 해석: deploy-jobs.json 의 python -m 모듈 + 그 모듈이 한 단계 가져오는 같은 패키지 모듈(components·wiring·__init__ 제외)
    import tempfile
    jf = {"deploy-jobs.json": json.dumps({"jobs": [{"argv": ["python", "-m", "pkg", "backup"]}, {"argv": ["python", "-m", "pkg2.job", "--config", "c"]}]}),
          "pkg/__main__.py": "import sys\nfrom .main import main\nfrom .components.c import x\nfrom .wiring.w import y\nfrom . import z\nsys.exit(main())\n",
          "pkg/main.py": "", "pkg/other.py": "", "pkg/components/c.py": "", "pkg/wiring/w.py": "", "pkg/__init__.py": "",
          "src/pkg2/job/__main__.py": "from pkg2.runner import go\ngo()\n", "src/pkg2/runner.py": "", "src/pkg2/unrelated.py": ""}
    with tempfile.TemporaryDirectory() as t:
        for rel, body in jf.items():
            (pathlib.Path(t) / rel).parent.mkdir(parents=True, exist_ok=True)
            (pathlib.Path(t) / rel).write_text(body, encoding="utf-8")
        got = job_files(t, sorted(jf))
    if got != {"pkg/__main__.py", "pkg/main.py", "src/pkg2/job/__main__.py", "src/pkg2/runner.py"}:
        bad.append(f"잡 진입 모듈 해석: {sorted(got)}")
    print("self-test:", "OK" if not bad else bad)
    return not bad


def main():
    if "--self-test" in sys.argv:
        return 0 if self_test() else 1
    if not self_test():
        return 1
    v = scan()
    kinds, repos = {}, {}
    for a, k, _ in v:
        kinds[k] = kinds.get(k, 0) + 1
        repos[a] = repos.get(a, 0) + 1
    print(f"위반 {len(v)}줄 (W 환경 통째 사용, I env 미지정 상속, S 환경 찍기·env 명령, X 셸 exec) 종류별 {sorted(kinds.items())} 리포별 {sorted(repos.items())}")
    print(f"범위 밖이라 세지 않은 것(시험·잡 파일이 아니다): " + ", ".join(f"{k} {OUTSCOPE.get(k, 0)}줄" for k in ("W", "I", "S", "X")))
    print("\n".join(x[2] for x in v) if v else "OK: 상속 환경 통째 전달 없음(C45, R9.1)")
    return 1 if v else 0


if __name__ == "__main__":
    sys.exit(main())
