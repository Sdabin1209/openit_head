#!/usr/bin/env python3
"""E2E 시나리오(deploy scripts/e2e_steps.py)가 기대하는 (경로, 상태 코드)가 계약 OpenAPI(boundary-contracts/openapi/openapi.json)와
CONVENTIONS 9절 상태 표 안에 있는지 실행 없이 센다(보장 계획 7번).
판정: 경로가 OpenAPI 의 어떤 경로 틀과도 맞지 않으면 어긋남. 상태 코드가 허용 집합 밖이면 어긋남.
허용 집합: 2xx, 401(인증 없음·틀림, D106), CONVENTIONS 9절 표(400 403 404 409 412 413 422 429 503), 게이트웨이 사람 경로의 302(OIDC 로그인 이동).
종료 코드: 0 어긋남 없음, 1 있음."""
import json, pathlib, re, sys
WS = pathlib.Path(__file__).resolve().parents[2]
D = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else WS / "deploy"
spec = json.loads((WS / "boundary-contracts/openapi/openapi.json").read_text(encoding="utf-8"))
tmpl = [(re.compile("^" + re.sub(r"\\\{[^}]+\\\}", "[^/]+", re.escape(p)) + "$"), set(ops)) for p, ops in spec["paths"].items()]
ALLOWED = {401, 400, 403, 404, 405, 409, 412, 413, 422, 429, 503, 302}   # 405: 없는 메서드(부정 시험)
src = (D / "scripts/e2e_steps.py").read_text(encoding="utf-8").splitlines()
n, bad = 0, []
for i, line in enumerate(src, 1):
    for m in re.finditer(r'f?"(/v1/[^"?]*)', line):
        codes = [int(c) for c in re.findall(r'(?:==|!=)\s*"?(\d{3})\b', line)] + [int(c) for g in re.findall(r'in \(([0-9, ]+)\)', line) for c in re.findall(r"\d{3}", g)]
        if not codes:
            continue
        path = re.sub(r"\{[^}]*\}", "x", m.group(1))
        if path.endswith("/") and re.match(r'"\s*\+', line[m.end():]):
            path += "x"   # 문자열 덧셈으로 끝 칸을 붙인 경로("/v1/x/" + ref)
        n += 1
        mm = re.search(r'"(GET|POST|PUT|DELETE|PATCH)",\s*f?"' + re.escape(m.group(1)), line)
        meth = mm.group(1).lower() if mm else None
        hits = [ops for t, ops in tmpl if t.match(path)]
        if hits and meth and any(200 <= c < 300 for c in codes) and not any(meth in ops for ops in hits):
            bad.append(f"e2e_steps.py:{i}: {meth.upper()} {m.group(1)} 성공을 기대하지만 OpenAPI 의 그 경로에 {meth.upper()} 가 없다")
        if not hits and not set(codes) <= {404, 405}:   # 없는 경로가 404·405 를 내는지 보는 부정 시험은 맞다
            bad.append(f"e2e_steps.py:{i}: 경로 {m.group(1)} 가 OpenAPI 에 없다")
        for c in codes:
            if not (200 <= c < 300 or c in ALLOWED):
                bad.append(f"e2e_steps.py:{i}: 상태 {c} 는 허용 집합 밖이다 ({m.group(1)})")
print(f"기대 (경로, 상태) {n}건, 어긋남 {len(bad)}건")
for b in bad: print(b)
sys.exit(1 if bad else 0)
