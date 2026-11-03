#!/usr/bin/env python3
"""영역 가로지르는 정적 점검(2026-11-03, 계획표 H6). E2E 전에 읽어서 알 수 있는 어긋남을 찾는다(메모리 '정적 일관성 먼저').

1) 잠금 판: 모든 영역의 의존 고정(requirements·lock·Dockerfile ARG·빌드 스크립트)이 deploy 기준표(scripts/lib.sh의
   DEPLOY_BC_TAG·DEPLOY_LINK_TAG·DEPLOY_MR_TAG·DEPLOY_SS_TAG) 값과 같은가. 기준표가 유일한 정본(워크스페이스 CLAUDE.md).
2) 영역 사이 이름: 계약에 있는 이름(필드·헤더·사유 코드·경로)을 생산자와 소비자 영역이 둘 다 쓰는가.
   한쪽에만 있으면 철자 어긋남이나 빠진 구현이다.
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


def files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not (set(p.relative_to(root).parts) & SKIP_DIRS) and not any(x.startswith(".") for x in p.relative_to(root).parts[:-1]) and "CHANGELOG" not in p.name:
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
    for b in bad:
        print(b)
    print(f"{'OK' if not bad else 'FAIL'}: 기준표 {want}, 어긋남 {len(bad)}건")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
