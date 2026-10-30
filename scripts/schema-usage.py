#!/usr/bin/env python3
"""영역 경계 스키마를 실제로 누가 쓰는지 영역 코드에서 센다(OPEN_GAPS U46).

왜: conformance/promoted/*.MANIFEST.json 의 producer/consumers 는 승격 시점에 영역이 낸 기록이라 코드가 바뀌면 어긋난다.
기록을 고쳐 쓰는 대신, 지금 코드에서 스키마 이름이 검증 호출(validator/load_schema/check_record/check_outgoing/validate 등)에
나타나는 곳을 세어 현재 사용표를 만든다. 결과는 head/docs/SCHEMA_USAGE.md(생성 파일, 손으로 고치지 않는다).
한계: 문자열 이름으로 부르는 호출만 센다. 변수로 이름을 넘기는 곳(예: 잡 선언의 config.schema)은 '간접'으로 따로 찾지 않는다.
사용: python3 head/scripts/schema-usage.py  (워크스페이스 루트 기준 경로를 스스로 찾는다)
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "boundary-contracts" / "boundary_contracts" / "schemas"
AREAS = json.loads((ROOT / "head" / "shared" / "areas.json").read_text(encoding="utf-8"))
OUT = ROOT / "head" / "docs" / "SCHEMA_USAGE.md"
# 검증·읽기 호출 모양(Python·TypeScript·셸). 스키마 이름이 따옴표 안에 그대로 나오는 곳만 센다
CALL = r"""(validator|load_schema|check_record|check_outgoing|check_incoming|validate|validate_survey|_validate_if_known|schemaFor|validateAgainst|assertSchema|ajv\.getSchema|getValidator)\s*\(\s*["'`]{name}["'`]"""


def area_names():
    a = AREAS.get("areas", AREAS)
    names = [x["name"] if isinstance(x, dict) else x for x in (a if isinstance(a, list) else a.keys())]
    return [n for n in names if (ROOT / n / ".git").exists() and n not in ("head", "boundary-contracts")]


def tracked_files(repo):
    out = subprocess.run(["git", "-C", str(ROOT / repo), "ls-files"], capture_output=True, text=True).stdout.split("\n")
    return [ROOT / repo / f for f in out if f.endswith((".py", ".ts", ".js", ".sh", ".mjs")) and "/node_modules/" not in f]


def main():
    names = sorted(p.name[: -len(".schema.json")] for p in SCHEMAS.glob("*.schema.json") if not p.name.startswith("_"))
    texts = {r: [(f, f.read_text(encoding="utf-8", errors="replace")) for f in tracked_files(r)] for r in area_names()}
    rows, unused = [], []
    for n in names:
        rx = re.compile(CALL.format(name=re.escape(n)))
        users = {}
        for repo, files in texts.items():
            hits = [str(f.relative_to(ROOT / repo)) for f, t in files if rx.search(t)]
            prod = [h for h in hits if not re.search(r"(^|/)(tests?|test_[^/]*|[^/]*\.test\.ts)", h)]
            if prod or hits:
                users[repo] = (len(prod), len(hits) - len(prod))
        if users:
            rows.append((n, users))
        else:
            unused.append(n)
    lines = ["# 영역 경계 스키마 사용표(생성 파일)", "",
             "`head/scripts/schema-usage.py`가 영역 리포지토리의 추적 파일에서 스키마 이름이 검증 호출에 나타나는 곳을 센 결과다. 손으로 고치지 않는다.",
             "승격 기록(`boundary-contracts/conformance/promoted/*.MANIFEST.json`)의 producer/consumers는 승격 시점의 기록이고, 현재 사용은 이 표가 정본이다(U46).",
             "칸의 값은 `코드 파일 수/시험 파일 수`. 문자열 이름으로 부르는 호출만 센다(변수로 이름을 넘기는 곳은 세지 않는다).", "",
             "| 스키마 | " + " | ".join(texts) + " |", "|---|" + "---|" * len(texts)]
    for n, users in rows:
        lines.append(f"| {n} | " + " | ".join(f"{users[r][0]}/{users[r][1]}" if r in users else "" for r in texts) + " |")
    lines += ["", f"## 이 방식으로 찾지 못한 스키마 {len(unused)}개", "",
              "공통 정의·하위 정의($ref로만 쓰임)이거나, 변수로 이름을 넘겨 쓰이거나, 실제로 읽는 쪽이 없는 것이다. 하나씩 따진 결과는 OPEN_GAPS U47.", ""]
    lines += [f"- {n}" for n in unused]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"schema-usage: 스키마 {len(names)}개, 사용 확인 {len(rows)}개, 찾지 못함 {len(unused)}개 -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
