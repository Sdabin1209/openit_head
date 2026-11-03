#!/usr/bin/env python3
"""영역 가로지르는 정적 점검(2026-11-03, 계획표 H6). E2E 전에 읽어서 알 수 있는 어긋남을 찾는다(메모리 '정적 일관성 먼저').

1) 잠금 판: 모든 영역의 의존 고정(requirements·lock·Dockerfile ARG·빌드 스크립트)이 deploy 기준표(scripts/lib.sh의
   DEPLOY_BC_TAG·DEPLOY_LINK_TAG·DEPLOY_MR_TAG·DEPLOY_SS_TAG) 값과 같은가. 기준표가 유일한 정본(워크스페이스 CLAUDE.md).
2) 영역 사이 이름: 계약에 있는 이름(필드·헤더·사유 코드·경로)을 생산자와 소비자 영역이 둘 다 쓰는가.
   한쪽에만 있으면 철자 어긋남이나 빠진 구현이다.
3) 평문 주소·인증서 검증 끄기 금지(U99, 글자 그대로와 조립한 주소 모두. 거부 시험 줄은 그 줄에 plaintext-rejection-test 표시): 서비스 사이 http:// 주소와 verify=False 류가 코드·설정에 없어야 한다(같은 기계 안 loopback 주소만 예외, 계약 3.4.1 과 같은 규칙).
시험·문서·변경 기록·생성물 폴더는 보지 않는다(옛 판을 인용할 수 있다).

사용: python3 head/scripts/cross-area-check.py [--deploy <deploy 작업 트리>]   종료 코드 0 통과, 1 어긋남.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
AREAS = ["survey-service", "release-gate", "question-authoring", "ops-feedback", "model-runtime", "model-lab",
         "synthetic-data", "kiosk-frontend", "admin-console", "link"]
SKIP_DIRS = {"node_modules", ".venv", "build", "dist", "docs", "tests", "test", "test-e2e", "test-image", "__pycache__", ".git"}
PIN_FILES = re.compile(r"(requirements[^/]*\.(txt|lock)|Dockerfile|pyproject\.toml|build[-_][^/]*\.sh|smoke[^/]*\.sh|setup-env\.sh)$")
PIN_PATTERNS = {   # 기준표 키 -> 영역 파일에서 판을 뽑는 정규식들
    "DEPLOY_BC_TAG": [r"openit_boundary-contracts\.git@(v[0-9][0-9.]*)", r"ARG BOUNDARY_(?:VERSION|CONTRACTS?)=(v[0-9][0-9.]*)"],
    "DEPLOY_LINK_TAG": [r"openit_link\.git@(v[0-9][0-9.]*)", r"ARG LINK_VERSION=(v[0-9][0-9.]*)"],
    "DEPLOY_MR_TAG": [r"openit_model-runtime\.git@(v[0-9][0-9.]*)"],
    "DEPLOY_SS_TAG": [r"(survey-schema-v[0-9][0-9.]*)", r"SURVEY_SCHEMA_TAG=(survey-schema-v[0-9][0-9.]*)"],
}
# 계약 이름 -> (생산자 영역들, 소비자 영역들). 둘 다 비어 있지 않아야 한다.
NAMES = {
    "question_set_id": (["survey-service", "release-gate", "question-authoring"], ["kiosk-frontend", "admin-console", "DEPLOY"]),
    "/v1/question-sets": (["survey-service"], ["kiosk-frontend", "DEPLOY"]),
    "QUESTION_SET_REQUIRED": (["survey-service"], ["kiosk-frontend"]),
    "UNKNOWN_QUESTION_SET": (["survey-service"], ["kiosk-frontend", "DEPLOY"]),
    "question_set_title": (["survey-service"], ["admin-console"]),
    "RESULT_READY": (["survey-service"], ["admin-console"]),
    "X-Openit-Roles": (["DEPLOY"], ["question-authoring"]),
    "ACCOUNT_PENDING_APPROVAL": (["DEPLOY"], ["admin-console"]),
    "pause_reason": (["survey-service"], ["admin-console", "kiosk-frontend"]),
    "question_banks/": (["release-gate"], []),          # 소비자는 계약 클라이언트(load_bundle)
}


def files(root: Path, skip=SKIP_DIRS):
    for p in root.rglob("*"):
        if p.is_file() and not (set(p.relative_to(root).parts) & skip) and not any(x.startswith(".") for x in p.relative_to(root).parts[:-1]) and "CHANGELOG" not in p.name:
            yield p


def table(deploy: Path) -> dict:
    s = (deploy / "scripts" / "lib.sh").read_text(encoding="utf-8")
    out = {}
    for k in PIN_PATTERNS:
        m = re.search(rf'^{k}="(?:\$\{{[A-Z_]+:-)?([^"}}]+)', s, re.M)
        out[k] = m.group(1) if m else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", default=str(WS / "deploy"))
    a = ap.parse_args()
    deploy = Path(a.deploy)
    want = table(deploy)
    bad = []
    for area in AREAS:
        root = WS / area
        for p in files(root):
            if not PIN_FILES.search(p.name):
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            for key, pats in PIN_PATTERNS.items():
                for pat in pats:
                    for v in re.findall(pat, text):
                        if want[key] and v != want[key]:
                            bad.append(f"판 어긋남: {p.relative_to(WS)} {v} (기준표 {key}={want[key]})")
    roots = {a: WS / a for a in AREAS} | {"DEPLOY": deploy}
    cache: dict[str, str] = {}

    def has(area: str, name: str) -> bool:
        if area not in cache:
            cache[area] = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files(roots[area])
                                    if p.suffix in {".py", ".ts", ".mjs", ".js", ".json", ".sh", ".yaml", ".yml", ".env", ""} or p.name == "Caddyfile")
        return name in cache[area]
    for name, (prod, cons) in NAMES.items():
        for side, areas in (("생산자", prod), ("소비자", cons)):
            for ar in areas:
                if not has(ar, name):
                    bad.append(f"이름 누락: {name} 이 {side} {ar} 코드에 없다")
    # 3) 평문·검증 끄기 금지(U99 원칙: 모든 영역 사이 통신 TLS, 배치 무관). 서비스 사이 주소가 http:// 이면 서버를 나누는 순간 평문이 된다.
    #    예외는 같은 기계 안(loopback)뿐이다. 경로(/healthz)로 봐주면 망을 건너는 감시 프로브까지 빠진다.
    plain = re.compile(r"http://(?!localhost[:/]|127\.)[a-z0-9][a-z0-9.-]*:[0-9]+")   # loopback(localhost·127.x)만 예외. 계약 3.4.1 클라이언트 규칙과 같다. 포트가 붙은 주소만 본다($schema 같은 식별자 URL 제외)
    import yaml as _y   # 서비스 이름 목록: deploy compose 의 서비스들. 포트 없는 http://<서비스> 도 평문이다(23:05 E2E 단계 6 이 잡은 구멍)
    _svcs = set()
    for _c in deploy.glob("compose*.yaml"):
        try:
            _svcs |= set((_y.safe_load(_c.read_text(encoding="utf-8")) or {}).get("services", {}) or {})
        except Exception:
            pass
    bare = re.compile(r"http://(" + "|".join(sorted(map(re.escape, _svcs), key=len, reverse=True)) + r")(?=[/\"'\s:,)}]|$)") if _svcs else None
    built = re.compile(r"http://(\{|\$\{?|%s|%\(|'\s*\+|\"\s*\+)")   # 조립한 평문 주소(f"http://{name}:8080", "http://$HOST", "http://%s" 등) — 글자 그대로가 아니라 정규식 plain 이 못 잡는다
    noverify = re.compile(r"verify\s*=\s*False|ssl\.CERT_NONE|check_hostname\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED|rejectUnauthorized\s*:\s*false")
    # deploy 의 test/ 는 E2E·시험이 실제로 쓰는 설정이다(예: test/ops-job/test-ops-job.yaml) — 평문 점검에서 빼지 않는다(23:05 E2E 단계 6 이 잡은 구멍)
    for name, root in [*((a, WS / a) for a in AREAS), ("DEPLOY", deploy)]:
        for p in files(root, SKIP_DIRS - {"test", "test-e2e", "test-image"} if name == "DEPLOY" else SKIP_DIRS):
            if p.suffix not in {".py", ".ts", ".mjs", ".js", ".env", ".yaml", ".yml", ".json", ".sh"} and p.name != "Caddyfile":
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith("#") or "plaintext-rejection-test" in line:
                    continue   # plaintext-rejection-test: "평문이면 거부된다"를 확인하는 시험 줄임을 그 줄에 밝힌 것만 예외(파일 단위 예외는 두지 않는다)
                if plain.search(line):
                    bad.append(f"평문 주소: {p.relative_to(root.parent if name != 'DEPLOY' else root)}:{i}: {plain.search(line).group(0)}")
                if bare and bare.search(line) and not plain.search(line):
                    bad.append(f"평문 서비스 주소(포트 없음): {p.relative_to(root.parent if name != 'DEPLOY' else root)}:{i}: {bare.search(line).group(0)}")
                if built.search(line) and not re.search(r"http://(\{|\$\{?)(localhost|127\.)", line):
                    bad.append(f"조립한 평문 주소: {p.relative_to(root.parent if name != 'DEPLOY' else root)}:{i}: {line.strip()[:80]}")
                if noverify.search(line):
                    bad.append(f"인증서 검증 끄기: {p.relative_to(root.parent if name != 'DEPLOY' else root)}:{i}")
    for b in bad:
        print(b)
    print(f"{'OK' if not bad else 'FAIL'}: 기준표 {want}, 어긋남 {len(bad)}건")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
