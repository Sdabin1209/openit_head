#!/usr/bin/env python3
"""영역 서버의 실제 경로표에서 OpenAPI 3.1 문서를 만들고, 계약 문서(md)의 엔드포인트 목록과 대조한다.

왜: 엔드포인트·메서드·스키마의 정본이 md 문장이었다(사용자 지적 "md 는 정본이 되면 안 된다", OPEN_GAPS G-HTTP-MD-CANONICAL).
    OpenAPI 3.1 은 JSON Schema 2020-12 와 호환이라 계약 스키마를 $ref 로 그대로 가리킨다.
입력: 7개 서버 영역의 경로 선언(openit_link Route, survey-service _SPEC, question-authoring R()), boundary-contracts 의 md 와 스키마.
출력: --out 파일(OpenAPI 3.1). 표준 출력에 대조 결과: md 에만 있는 경로, 코드에만 있는 경로, 스키마 이름이 계약에 없는 경로.
종료 코드: 대조 어긋남 0 이면 0, 있으면 1.
"""
import ast
import json
import pathlib
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parents[2]
BC = WS / "boundary-contracts"
SCHEMAS = {p.name[: -len(".schema.json")] for p in (BC / "boundary_contracts/schemas").glob("*.schema.json")}
AREAS = ["survey-service", "question-authoring", "ops-feedback", "release-gate", "model-lab", "synthetic-data", "model-runtime"]
SKIP_PATH = re.compile(r"^/(ui/|metrics$|healthz$|readyz$)|^\?$")


# 계약 JSON 스키마가 아닌 응답의 분류(근거: HTTP.md·PUBLIC_API.md 의 해당 행). application/json 은 문진 스키마(survey-service schema/, survey_schema 패키지) 이름이다.
NON_CONTRACT = {
    ("GET", "/v1/datasets/{}/versions/{}/files"): ("application/x-tar", "데이터셋 파일 묶음(HTTP.md I2)"),
    ("GET", "/v1/datasets/{}/versions/{}/files/{}"): ("application/octet-stream", "파일 바이트(HTTP.md I2)"),
    ("GET", "/v1/eval-reports/{}"): ("application/octet-stream", "평가 보고서 바이트(HTTP.md I3)"),
    ("GET", "/v1/packages/{}/versions/{}/adapter"): ("application/x-tar", "어댑터 묶음(HTTP.md I3)"),
    ("GET", "/v1/releases/{}/bundle"): ("application/x-tar", "릴리스 묶음(HTTP.md I4)"),
    ("POST", "/v1/releases/{}/respond"): ("text/plain", "ResponseText(HTTP.md I9)"),
    ("GET", "/v1/staff/alerts/stream"): ("text/event-stream", "이벤트마다 계약 스키마(StaffAlert·ResultReadyEvent·HeartbeatEvent·ResyncEvent)"),
    ("POST", "/v1/staff/push-subscriptions/unsubscribe"): ("none", "204 본문 없음"),
    ("GET", "/v1/question-sets/{}/versions/{}"): ("application/json", "QuestionBank"),
    ("GET", "/v1/question-sets/{}/versions/{}/reviews"): ("application/json", "ListEnvelope + ReviewRecord(question-authoring 핸들러가 검증)"),
    ("GET", "/v1/results"): ("application/json", "ListEnvelope + SessionResult"),
    ("GET", "/v1/results/{}"): ("application/json", "SessionResult"),
    ("POST", "/v1/results/{}/ack"): ("application/json", "SessionResult"),
    ("GET", "/v1/staff/sessions/{}"): ("application/json", "StaffSessionView"),
    ("POST", "/v1/sessions"): ("application/json", "FrontendInput"),
    ("POST", "/v1/sessions/{}/turns"): ("application/json", "FrontendInput"),
    ("POST", "/v1/sessions/{}/end"): ("application/json", "FrontendInput"),
    ("POST", "/v1/sessions/{}/intervention"): ("application/json", "FrontendInput"),
}


def norm(p):
    return re.sub(r"\{[^}]+\}", "{}", p.split("?")[0].rstrip("*"))


def schema_name(v):
    """Route 인자의 스키마 표기 -> 계약 이름(#/$defs/X 는 '이름#X')."""
    if v is None:
        return None
    m = re.match(r"^([A-Za-z0-9]+)(?:#/\$defs/([A-Za-z0-9]+))?$", v)
    return (m.group(1) + ("#" + m.group(2) if m.group(2) else "")) if m else v


def str_expr(node, consts):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return consts.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = str_expr(node.left, consts), str_expr(node.right, consts)
        return a + b if a is not None and b is not None else None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("RQ", "D") and node.args:
        inner = str_expr(node.args[0], consts)
        return (("AuthoringRequests" if node.func.id == "RQ" else "AuthoringResponses") + "#/$defs/" + inner) if inner else None
    return None


def routes_ast(area):
    out = []
    files = subprocess.run(["git", "-C", str(WS / area), "grep", "-lE", r"Route\(|\bR\(", "--", "*.py", ":!tests", ":!scripts"],
                           capture_output=True, text=True).stdout.split()
    for f in files:
        tree = ast.parse((WS / area / f).read_text(encoding="utf-8"))
        consts = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                v = str_expr(n.value, consts)
                if v is not None:
                    consts[n.targets[0].id] = v
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("Route", "R") and len(n.args) >= 2):
                continue
            method = str_expr(n.args[0], consts)
            path = str_expr(n.args[1], consts)
            if method not in ("GET", "POST", "PUT", "DELETE", "PATCH") or path is None:
                continue
            kw = {k.arg: k.value for k in n.keywords}
            req = str_expr(kw["request_schema"], consts) if "request_schema" in kw else (str_expr(kw["request"], consts) if "request" in kw else None)
            res = str_expr(kw["response_schema"], consts) if "response_schema" in kw else (str_expr(kw["response"], consts) if "response" in kw else None)
            out.append((method, path, schema_name(req), schema_name(res), f"{area}/{f}:{n.lineno}"))
    return out


def routes_survey():
    py = WS / "survey-service/.venv/bin/python"
    code = "import json;from survey_service.components import link_public_api as m;print(json.dumps([[s[1],s[2],s[5],s[7]] for s in m._SPEC]))"
    r = subprocess.run([str(py), "-c", code], cwd=WS / "survey-service", capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("survey-service 경로표를 읽지 못했다: " + r.stderr[-300:])
    return [(m, p, schema_name(q), schema_name(s), "survey-service/survey_service/components/link_public_api.py:_SPEC") for m, p, q, s in json.loads(r.stdout)]


def md_endpoints():
    out = set()
    for doc in ("HTTP.md", "PUBLIC_API.md"):
        for line in (BC / doc).read_text(encoding="utf-8").splitlines():
            for mm in re.finditer(r"`((?:GET|POST|PUT|DELETE|PATCH)) (/[^` ]*)[^`]*`", line):
                out.add((mm.group(1), norm(mm.group(2))))
    return out


def main():
    out_file = None
    if "--out" in sys.argv:
        out_file = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
    routes = []
    for a in AREAS:
        rs = routes_survey() if a == "survey-service" else routes_ast(a)
        routes += [(a, *r) for r in rs if not SKIP_PATH.search(r[1])]
    paths, bad = {}, []
    code_set = set()
    for area, m, p, req, res, where in routes:
        code_set.add((m, norm(p)))
        for nm in (req, res):
            if nm and nm.split("#")[0] not in SCHEMAS:
                bad.append(f"계약에 없는 스키마 이름 {nm}: {m} {p} ({where})")
        op = {"x-owner": area, "x-source": where, "responses": {"default": {"description": "BoundaryError(CONVENTIONS 9절 상태 표)",
              "content": {"application/json": {"schema": {"$ref": "../boundary_contracts/schemas/BoundaryError.schema.json"}}}}}}
        if req:
            base, _, frag = req.partition("#")
            op["requestBody"] = {"content": {"application/json": {"schema": {"$ref": f"../boundary_contracts/schemas/{base}.schema.json" + (f"#/$defs/{frag}" if frag else "")}}}}
        ok = {"description": "성공"}
        if res:
            base, _, frag = res.partition("#")
            ok["content"] = {"application/json": {"schema": {"$ref": f"../boundary_contracts/schemas/{base}.schema.json" + (f"#/$defs/{frag}" if frag else "")}}}
        elif (m, norm(p)) in NON_CONTRACT:
            kind, ref = NON_CONTRACT[(m, norm(p))]
            ok["content"] = {kind: ({"x-survey-schema": ref} if kind == "application/json" else {"x-body": ref})}
        else:
            ok["x-unschematized"] = True   # 분류표(NON_CONTRACT)에도 없다: 대조 실패로 센다
        op["responses"]["2XX"] = ok
        paths.setdefault(p, {})[m.lower()] = op
    md = md_endpoints()
    md = {x for x in md if not SKIP_PATH.search(x[1])}
    only_md = sorted(md - code_set)
    only_code = sorted(code_set - md)
    doc = {"openapi": "3.1.0", "info": {"title": "openit 영역 사이 HTTP", "version": "draft",
           "description": "영역 서버의 경로 선언에서 만든 엔드포인트 정본 초안(head/scripts/build-openapi.py). 스키마는 계약 패키지의 것을 $ref 로 가리킨다."},
           "paths": dict(sorted(paths.items()))}
    if out_file:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    uns = [(m, p) for p, ops in paths.items() for m, o in ops.items() if o["responses"]["2XX"].get("x-unschematized")]
    print(f"코드 경로 {len(code_set)}, md 경로 {len(md)}, md 에만 {len(only_md)}, 코드에만 {len(only_code)}, 계약에 없는 스키마 이름 {len(bad)}, 응답 스키마 없음 {len(uns)}")
    for x in only_md:
        print("md 에만", *x)
    for x in only_code:
        print("코드에만", *x)
    for b in bad:
        print(b)
    for m, p in sorted(uns):
        print("응답 스키마 없음", m.upper(), p)
    # md 는 정본이 아니다: 코드에만 있는 경로는 OpenAPI 가 채운다(정보로만 낸다). md 에만 있는 경로·계약에 없는 이름·분류 없는 응답은 어긋남이다
    return 1 if (only_md or bad or uns) else 0


if __name__ == "__main__":
    sys.exit(main())
