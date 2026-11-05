#!/usr/bin/env python3
"""서비스별 OpenAPI 계약을 정본으로 읽고 실제 서버 경로와 대조한다. 계약을 코드에서 재생성하지 않는다.

왜: 엔드포인트·메서드·스키마의 정본이 md 문장이었다(사용자 지적 "md 는 정본이 되면 안 된다", OPEN_GAPS G-HTTP-MD-CANONICAL).
    OpenAPI 3.1 은 JSON Schema 2020-12 와 호환이라 계약 스키마를 $ref 로 그대로 가리킨다.
입력: 서비스별 OpenAPI 계약과 7개 서버 영역의 경로 선언.
출력: 표준 출력과 선택적인 --out 파일에 계약 참조·경로 대조 감사 결과(JSON).
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
AREAS = ["survey-service", "question-authoring", "ops-feedback", "release-gate", "model-lab", "synthetic-data", "model-runtime"]
SKIP_PATH = re.compile(r"^/(ui/|metrics$|healthz$|readyz$)|^\?$")


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
    path = WS / "survey-service/survey_service/components/link_public_api.py"
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_SPEC" for t in node.targets):
            return [(row[1], row[2], schema_name(row[5]), schema_name(row[7]), str(path))
                    for row in ast.literal_eval(node.value)]
    raise SystemExit("survey-service 경로표 _SPEC이 없다")


def main():
    from boundary_contracts.http_contracts import HttpContract, catalog
    services = {e["owner"]: name for name, e in catalog()["services"].items()}
    bad, summaries = [], []
    for area in AREAS:
        service = services[area]
        contract = HttpContract(service)
        summaries.append(contract.lint())
        actual = routes_survey() if area == "survey-service" else routes_ast(area)
        actual = {(method, norm(path)) for method, path, *_ in actual if not SKIP_PATH.search(path)}
        expected = {(method.upper(), norm(path)) for path, ops in contract.doc["paths"].items()
                    for method in ops if path.startswith("/v1/")}
        for method, path in sorted(actual - expected):
            bad.append(f"{area}: undeclared implementation {method} {path}")
        for method, path in sorted(expected - actual):
            bad.append(f"{area}: missing implementation {method} {path}")
    report = {"services": summaries, "violations": bad, "ok": not bad}
    if "--out" in sys.argv:
        path = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
        if path.resolve().is_relative_to(BC.resolve()):
            raise SystemExit("--out is an audit report, not a contract generator; use a path outside boundary-contracts")
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(bool(bad))


if __name__ == "__main__":
    sys.exit(main())
