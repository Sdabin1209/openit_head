#!/usr/bin/env python3
"""규칙 C16·C17(영역마다 docs/adr 와 README 의 ADR 링크), C22·D22(서비스 영역은 Dockerfile 과 스모크 스크립트), C28(스모크 고정 포트 금지), C39(.venv 는 커밋하지 않음), C10·L26(README 에 시험 개수 숫자 금지: 개수는 실행 명령으로 센다).
areas.json 의 영역을 돈다. 사용: area-presence-check.py  (종료 1 이면 위반)"""
import json, pathlib, re, sys
WS = pathlib.Path(__file__).resolve().parents[2]
areas = json.loads((WS/"head/shared/areas.json").read_text(encoding="utf-8"))["areas"]
names = [a["name"] if isinstance(a, dict) else a for a in areas]
# C10·L26: 문서에 시험 개수를 쓰지 않는다. 시험 결과 낱말 앞뒤에 붙은 숫자를 잡는다.
# 왜 이 모양인가(2026-11-08 Opus 검토): 옛 정규식은 "324개 통과"·"217개 중 통과 217"·"시험 7개"를 놓치고 날짜 "-08 통과"를 잡았다.
# 숫자 앞이 [\w.\-/:=] 이면(날짜·버전·rc=0·시각) 개수가 아니다. 숫자 뒤가 초·ms·분이면 시간이다. "시험 3개 파일"처럼 개수가 아닌 문장은
# 잡힐 수 있다 → 문서는 "파일 3개"처럼 쓴다(경계를 단순하게 두는 선택).
# 0 은 개수가 아니라 불변 주장(실패 0·건너뜀 0)이라 허용한다. 4xx·5xx 세 자리는 HTTP 상태(예: "실패 401")라 개수로 보지 않는다.
_N = r"(?<![\w.\-/:=])(?!0(?!\d))(?![45]\d\d(?!\s*(?:개|건|tests?)))\d+(?!\s*(?:초|ms|분|시|일|\d))"
TEST_COUNT = re.compile(
    _N + r"\s*(?:개|건)?\s*(?:(?:시험|테스트|tests?)\s*)?(?:중\s*)?(?:passed|pass|failed|skipped|통과|실패|건너뜀)"   # 324개 통과, 324 tests passed, 217개 중 통과
    + r"|" + r"(?:passed|pass|통과|실패|건너뜀|failed|skipped)\s*[:=]?\s*" + _N                                              # 통과 324, pass: 324
    + r"|" + r"(?:시험|테스트)\s*" + _N + r"\s*(?:개|건)"
    + r"|" + _N + r"\s*/\s*\d+\s*(?:passed|pass|통과)", re.I)                                                    # 324/324 통과                                                              # 시험 7개
def test_count_lines(text):
    # 줄 번호와 맞은 부분 앞뒤만 싣는다(줄 앞부분만 보이면 맞은 곳이 빠졌다, 2026-11-08 검토)
    out=[]
    for i,l in enumerate(text.splitlines(),1):
        m=TEST_COUNT.search(l)
        if m: out.append(f"{i}행: …{l[max(0,m.start()-15):m.end()+15].strip()}…")
    return out
def self_test():
    pos = ["시험 162건", "393건 통과", "건너뜀 1", "3개 실패", "500개 통과", "324개 통과", "324 passed", "324 tests passed", "324건 통과", "통과 324", "pass: 324", "324개 시험 통과",
           "실패 0, 통과 217", "217개 중 통과 217", "시험 7개", "3개 통과", "324/324 통과"]
    neg = ["실패 0", "건너뜀 0", "실패 401", "실패 503 을 낸다", "2026-11-08 통과", "rc=0 통과", "v4.0.5 통과", "파일 3개", "12초 통과", "10:05 통과", "통과 기준", "4개 동시 실행"]
    bad = [x for x in pos if not TEST_COUNT.search(x)] + [f"거짓양성:{x}" for x in neg if TEST_COUNT.search(x)]
    print("self-test:", "OK" if not bad else bad); sys.exit(1 if bad else 0)
# 일부러 받아들인 한계(잡지 않는다): "통과 404"·"통과 503"(HTTP 상태와 구별 불가), "324 tests"·"시험 324"(결과 낱말·단위 없음),
#   "324개의 시험이 통과"(조사 사이), "총 42개"(문맥 없음). 거짓 양성: "단계 2 통과"(앞 낱말을 보지 않음).
if "--self-test" in sys.argv: self_test()
_pos_neg_ok = True
try:
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()): self_test()
except SystemExit as e:
    _pos_neg_ok = (e.code == 0)
if not _pos_neg_ok: print("시험 개수 정규식 자기 시험 실패: --self-test 로 확인"); sys.exit(1)
fails = []
for n in names:
    d = WS/n
    if not d.is_dir(): continue
    adr = d/"docs/adr"
    if not adr.is_dir() or not list(adr.glob("*.md")): fails.append(f"{n}: docs/adr 없음(C16)")
    readme = (d/"README.md").read_text(encoding="utf-8") if (d/"README.md").exists() else ""
    if adr.is_dir() and "adr" not in readme.lower(): fails.append(f"{n}: README 가 ADR 을 링크하지 않음(C16)")
    if test_count_lines(readme): fails.append(f"{n}: README 에 시험 개수 숫자가 박혀 있다(C10·L26: 개수는 실행 명령으로 센다): {test_count_lines(readme)[:3]}")
    gi = (d/".gitignore").read_text(encoding="utf-8") if (d/".gitignore").exists() else ""
    if (d/"requirements.txt").exists() or (d/"pyproject.toml").exists():
        if not re.search(r"^\.?venv/?$|^\.venv", gi, re.M): fails.append(f"{n}: .gitignore 에 .venv 없음(C39)")
    if (d/"Dockerfile").exists():
        smokes = list((d/"scripts").glob("smoke*"))
        if not smokes: fails.append(f"{n}: Dockerfile 은 있는데 scripts/smoke* 없음(C22)")
        for sm in smokes:   # C28: 스모크는 고정 호스트 포트를 쓰지 않는다(여러 영역이 같은 서버에서 동시에 돌면 충돌). 허용: 127.0.0.1::8080(배정) 또는 SMOKE_PORT 변수
            txt = sm.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"-p\s+(127\.0\.0\.1:)?[0-9]{2,5}:[0-9]{2,5}\b", txt): fails.append(f"{n}: {sm.name} 이 고정 호스트 포트를 쓴다(C28)")
print("\n".join(fails) if fails else f"OK: 영역 {len(names)}개 ADR·스모크·.venv 규칙")
sys.exit(1 if fails else 0)
