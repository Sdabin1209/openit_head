#!/usr/bin/env python3
"""계약 고정 문(2026-11-04, 사용자 지시 "빈칸·생략 없이 단계를 마치고 넘어간다"). 이 점검이 rc=0 이 아니면 계약을 고정하지 않고 코드 단계로 넘어가지 않는다.

왜: 헤드가 "다 했다"고 말한 뒤 칸 대부분이 검토되지 않은 채 넘어가려 한 일이 있었다(2026-11-04 04:52). 말이 아니라 셈으로 막는다.

점검:
1) 전수 대조 결과(docs/reviews/2026-11-04/full-P1~P5.md)의 표 줄 수가 칸 파일(boundary-contracts RUNTIME-MATRIX-CELLS.md)의 그 묶음 칸 수와 같고, 칸 (호출, 실패) 쌍이 하나도 빠지거나 겹치지 않는다.
2) 계약 재검토(full-P6.md)가 있고, 읽은 범위 절이 있다.
3) 결과 표에서 판정이 '맞음'이 아닌 칸과 P6 의 결함 번호가 모두 고친 기록(fixes.md)에 커밋 번호와 함께 있고, 그 커밋이 boundary-contracts 에 있다.
4) boundary-contracts 시험(pytest)·verify.py, head cross-area-check 가 모두 rc=0.

사용: python3 head/scripts/contract-freeze-gate.py   종료 코드 0 = 고정해도 된다, 1 = 안 된다(이유를 출력).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
BC = WS / "boundary-contracts"
REV = WS / "head" / "docs" / "reviews" / "2026-11-04"
DEPLOY = str(WS / "deploy" / "build" / "wt-deploy-450-lg")   # 왜: 오늘 합친 deploy 작업 트리(wo-450-lg)가 대조 대상이다. 기본 deploy 체크아웃은 그보다 낡았다
BUNDLE_OF = {"P1": "2", "P2": "3", "P3": "4", "P4": "1", "P5": "5"}


def cells_by_bundle() -> dict[str, set[tuple[str, str]]]:
    text = (BC / "RUNTIME-MATRIX-CELLS.md").read_text(encoding="utf-8")
    out: dict[str, set[tuple[str, str]]] = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^## 묶음 (\d)", line)
        if m:
            cur = m.group(1)
            out[cur] = set()
            continue
        m = re.match(r"^\| (C\d+)[^|]*\| (F\d+) \|", line)
        if cur and m:
            out[cur].add((m.group(1), m.group(2)))
    return out


def result_rows(path: Path) -> list[tuple[str, str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (C\d+)[^|]*\| (F\d+) \| ([^|]+)\|", line)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3).strip()))
    return rows


def main() -> int:
    bad: list[str] = []
    want = cells_by_bundle()
    fixes_p = REV / "fixes.md"
    fixes = fixes_p.read_text(encoding="utf-8") if fixes_p.exists() else ""
    if not fixes:
        bad.append(f"고친 기록 없음: {fixes_p}")
    for part, bundle in BUNDLE_OF.items():
        p = REV / f"full-{part}.md"
        if not p.exists():
            bad.append(f"결과 없음: {p}")
            continue
        rows = result_rows(p)
        got = [(c, f) for c, f, _ in rows]
        exp = want.get(bundle, set())
        if len(got) != len(set(got)):
            bad.append(f"{part}: 같은 칸이 두 번 있다")
        miss = exp - set(got)
        extra = set(got) - exp
        if miss:
            bad.append(f"{part}: 대조하지 않은 칸 {len(miss)}개(예: {sorted(miss)[:3]})")
        if extra:
            bad.append(f"{part}: 칸 파일에 없는 칸 {len(extra)}개(예: {sorted(extra)[:3]})")
        for c, f, verdict in rows:
            if not verdict.startswith("맞음"):
                key = f"{part} {c} {f}"
                m = re.search(re.escape(key) + r"[^\n]*\b([0-9a-f]{7,40})\b", fixes)
                if not m:
                    bad.append(f"고치지 않은 칸: {key} ({verdict})")
                elif subprocess.run(["git", "-C", str(BC), "cat-file", "-e", m.group(1) + "^{commit}"], capture_output=True).returncode:
                    bad.append(f"고친 커밋이 없다: {key} {m.group(1)}")
    p6 = REV / "full-P6.md"
    if not p6.exists():
        bad.append(f"결과 없음: {p6}")
    else:
        t = p6.read_text(encoding="utf-8")
        if "읽은" not in t:
            bad.append("P6: 읽은 범위 절이 없다")
        for d in sorted(set(re.findall(r"^#+\s*(R6-\d+)", t, re.M))):
            m = re.search(r"\bP6 " + re.escape(d) + r"\b[^\n]*\b([0-9a-f]{7,40})\b", fixes)
            if not m:
                bad.append(f"고치지 않은 재검토 결함: {d}")
    py = BC / ".venv" / "bin" / "python"
    for name, cmd, cwd in [("계약 시험", [str(py), "-m", "pytest", "-q", "tests"], BC),
                           ("verify", [str(py), "verify.py"], BC),
                           ("cross-area-check", [sys.executable, str(WS / "head/scripts/cross-area-check.py"), "--deploy", DEPLOY], WS)]:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{name} rc={r.returncode}")
    for b in bad:
        print(b)
    print("OK: 계약을 고정해도 된다" if not bad else f"FAIL: 고정하지 않는다({len(bad)}건)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
