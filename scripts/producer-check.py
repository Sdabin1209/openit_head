#!/usr/bin/env python3
"""생산자 검증 대조(R7, RULE_CHECKS 3번). 읽기만 한다.
계약 스키마마다 head/shared/producers.json에 적힌 생산자 영역의 동작 코드(시험·문서 제외)가 그 스키마 이름을 참조하는지 본다.
참조가 0이면 그 영역은 내보내기 전에 계약으로 검증할 수 없다(2026-10-31 발견한 결함 14건이 모두 이 경우였다).
이름을 표에서 고르는 경우처럼 문자열이 코드에 없을 수 있으면 producers.json의 "via"에 검증하는 파일을 적는다(그 파일이 있어야 통과).
사용: python3 head/scripts/producer-check.py   종료 코드: 0 전부 통과, 1 빠짐 있음.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKIP = {"outside", "defs"}   # 리포 밖 생산자, 정의 묶음: 생산자 코드가 이 워크스페이스에 없다
TEST_OR_DOC = re.compile(r"(^|/)(tests?|test-e2e|docs?|scripts/test[_-][^/]*)(/|$)|(^|/)test_[^/]*$|\.test\.ts$|\.md$|(^|/)(types|schemas)/|\.gen\.|(^|/)conformance/")


def code_files(repo):
    out = subprocess.run(["git", "-C", str(ROOT / repo), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    return [f for f in out if f.endswith((".py", ".ts", ".mjs", ".sh", ".json", ".yaml", ".yml")) and not TEST_OR_DOC.search(f) and "node_modules/" not in f]


def main():
    table = json.loads((ROOT / "head" / "shared" / "producers.json").read_text(encoding="utf-8"))
    schemas = sorted(p.name[:-len(".schema.json")] for p in (ROOT / "boundary-contracts" / "boundary_contracts" / "schemas").glob("*.schema.json"))
    bad, cache = [], {}
    for name in schemas:
        ent = table.get(name)
        if not ent:
            bad.append(f"{name}: producers.json에 없음")
            continue
        for repo in ent["producers"]:
            if repo in SKIP:
                continue
            if repo not in cache:
                cache[repo] = {f: (ROOT / repo / f).read_text(encoding="utf-8", errors="replace") for f in code_files(repo)}
            pat = re.compile(rf"\b{re.escape(name)}\b")
            hits = [f for f, t in cache[repo].items() if pat.search(t)]
            via = [v for v in ent.get("via", {}).get(repo, []) if (ROOT / repo / v).exists()]
            if not hits and not via:
                bad.append(f"{name}: 생산자 {repo}의 동작 코드가 이 스키마를 참조하지 않는다(내보내기 전 검증 없음)")
    for n in sorted(set(table) - set(schemas)):
        bad.append(f"{n}: 계약에 없는 이름이 producers.json에 있다")
    for b in bad:
        print("빠짐:", b)
    print(f"producer-check: 스키마 {len(schemas)}개, {'통과' if not bad else f'빠짐 {len(bad)}건'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
