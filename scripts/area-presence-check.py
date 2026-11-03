#!/usr/bin/env python3
"""규칙 C16·C17(영역마다 docs/adr 와 README 의 ADR 링크), C22·D22(서비스 영역은 Dockerfile 과 스모크 스크립트), C27(스모크 고정 포트 금지), C35(.venv 는 커밋하지 않음), C10·L26(README 에 시험 개수 숫자 금지: 개수는 실행 명령으로 센다).
areas.json 의 영역을 돈다. 사용: area-presence-check.py  (종료 1 이면 위반)"""
import json, pathlib, re, sys
WS = pathlib.Path(__file__).resolve().parents[2]
areas = json.loads((WS/"head/shared/areas.json").read_text(encoding="utf-8"))["areas"]
names = [a["name"] if isinstance(a, dict) else a for a in areas]
fails = []
for n in names:
    d = WS/n
    if not d.is_dir(): continue
    adr = d/"docs/adr"
    if not adr.is_dir() or not list(adr.glob("*.md")): fails.append(f"{n}: docs/adr 없음(C16)")
    readme = (d/"README.md").read_text(encoding="utf-8") if (d/"README.md").exists() else ""
    if adr.is_dir() and "adr" not in readme.lower(): fails.append(f"{n}: README 가 ADR 을 링크하지 않음(C16)")
    if re.search(r"\b\d{2,}\s*(passed|통과)\b", readme): fails.append(f"{n}: README 에 시험 개수 숫자가 박혀 있다(C10·L26: 개수는 실행 명령으로 센다)")
    gi = (d/".gitignore").read_text(encoding="utf-8") if (d/".gitignore").exists() else ""
    if (d/"requirements.txt").exists() or (d/"pyproject.toml").exists():
        if not re.search(r"^\.?venv/?$|^\.venv", gi, re.M): fails.append(f"{n}: .gitignore 에 .venv 없음(C35)")
    if (d/"Dockerfile").exists():
        smokes = list((d/"scripts").glob("smoke*"))
        if not smokes: fails.append(f"{n}: Dockerfile 은 있는데 scripts/smoke* 없음(C22)")
        for sm in smokes:   # C27: 스모크는 고정 호스트 포트를 쓰지 않는다(여러 영역이 같은 서버에서 동시에 돌면 충돌). 허용: 127.0.0.1::8080(배정) 또는 SMOKE_PORT 변수
            txt = sm.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"-p\s+(127\.0\.0\.1:)?[0-9]{2,5}:[0-9]{2,5}\b", txt): fails.append(f"{n}: {sm.name} 이 고정 호스트 포트를 쓴다(C27)")
print("\n".join(fails) if fails else f"OK: 영역 {len(names)}개 ADR·스모크·.venv 규칙")
sys.exit(1 if fails else 0)
