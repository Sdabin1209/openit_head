#!/usr/bin/env python3
"""규칙 전수 열거와 점검 대응(U76). 기억이 아니라 파일에서 뽑는다.
입력: docs/DECISIONS.md(결정 D##), 루트 CLAUDE.md(구조·세션·컨테이너·커밋·자동화 규칙), head CLAUDE.md(규칙), docs/RULE_CHECKS.md(수동 대응),
      ../deploy/scripts/self-checks.list(deploy 자체 점검), 영역별 tests/ 파일 이름.
출력: docs/RULE_COVERAGE.md(생성물). `--check` 는 생성물이 현재 입력과 같은지 확인한다(다르면 종료 1: 규칙을 적었으면 표도 다시 만들어야 한다).
대응 방식: 규칙 문장에 적힌 ID(D##, U##, ADR 번호)와 점검 설명에 적힌 ID 가 겹치면 대응. 그 밖은 수동 표(RULE_CHECKS.md)의 ID 참조만 인정한다. 낱말 겹침으로 추측하지 않는다.
분류: `RECORD`(점검 대상이 아닌 결정 기록: 역할·범위·시점·채택 사실)는 아래 RECORD_IDS 에 헤드가 근거와 함께 적는다. 나머지는 모두 점검이 있어야 한다."""
from __future__ import annotations
import re, sys, pathlib, glob
ROOT = pathlib.Path(__file__).resolve().parents[1]; WS = ROOT.parent
OUT = ROOT / "docs/RULE_COVERAGE.md"
# 점검 대상이 아닌 결정(기록): 이유를 적는다. 여기 없는 결정은 점검이 있어야 한다.
RECORD_IDS = {
 "D07":"배포 두 축 설계 선언(코드/내용). 점검은 publish-images·릴리스 흐름 시험이 맡으나 ID 미표기 → 점검 필요로 두지 않고 설계 기록으로 분류",
 "D11":"배포 환경 선언",
 "D12":"프런트 선택 기록",
 "D13":"모델 평가의 문항 접근 범위 선언(model-lab 평가 코드가 따름, ID 미표기)",
 "D18":"SDK 언어 선택 기록",
 "D19":"계약 소유·위치 선언(구조 규칙 6 이 점검)",
 "D20":"계약 세부 서술",
 "D21":"문진 스키마 담당 선언(C31 과 같음)",
 "D27":"경계 명세 방식 기록",
 "D29":"문진 스키마 위치 선언",
 "D30":"D92 로 대체됨",
 "D31":"자료 등록 방식 결정(저작 영역 시험이 맡음, ID 미표기)",
 "D33":"자료 형식 결정(저작 시험)",
 "D35":"model-runtime 세부 결정 기록",
 "D38":"완성 목표 서술",
 "D40":"서버 가정",
 "D41":"push 허락 절차(사람 절차, 기계 점검 불가)",
 "D42":"계약 1.0 릴리스 기록",
 "D43":"계약 1.1 릴리스 기록",
 "D47":"GPU 호스트 사용 기록",
 "D48":"첫 백엔드와 한계 기록",
 "D50":"저장소 계정 결정 기록(ops L08 시험이 일부)",
 "D51":"계약 1.2 릴리스 기록",
 "D52":"E2E 막힘 때의 결정 기록",
 "D54":"토폴로지 가정",
 "D55":"공개 API 범위 결정(계약 PUBLIC_API 시험이 맡음)",
 "D57":"O19 잠정안 기록",
 "D58":"계약 1.3.1 기록",
 "D59":"사용자 답변 정리",
 "D60":"런타임 동결 기록",
 "D61":"목표 서술",
 "D65":"영역 신설 기록",
 "D67":"작업 단위 기록",
 "D68":"영역 신설 기록",
 "D73":"디스크 사용 위임",
 "D78":"정본·대상·위임 선언",
 "D79":"정수 버전 1 유지 결정(CONVENTIONS 12절·G11 로 규칙화)",
 "D81":"프로파일 선택 기록(model-runtime 프로파일 시험이 맡음, ID 미표기)",
 "D91":"L17 처리 기록(완료)",
 "D99":"D-F 닫음",
 "D102":"D-I pull 기본(결정 대기)",
 "D103":"수용된 한계 기록",
 "D110":"문진 스키마 태그 기록",
 "D116":"릴리스 시점 결정",
 "D121":"고정 판 기록",
 "C11":"행동 규칙(확인 전 말하기 금지) — 기계 점검 불가",
 "C12":"행동 규칙(완료 선언 조건) — 열차 절차가 맡음",
 "C13":"언어·질문 규칙",
 "C14":"세션 시작 규칙",
 "C15":"'왜'를 답할 수 있어야 한다 — ADR 존재는 C16 점검",
 "C18":"코드 주석 규칙(수동 검토)",
 "C19":"ADR 대체 규칙(수동 검토)",
 "C20":"기록 위치 규칙",
 "C21":"개발 방식 규칙",
 "C23":"단독 시험 방식(계약 기준 서버) — 영역 스모크가 맡음",
 "C31":"문진 스키마 담당 선언",
 "C34":"push 허락(사람 절차)",
 "C38":"모델 시행착오 방식",
 "C7":"자기 리포 안에서만 일한다 — 사람·에이전트 행동 규칙(커밋 작성자 점검 C33 과 리포별 커밋으로 간접 확인)",
 "C8":"계약·문진 스키마 직접 수정 금지 — 행동 규칙(계약 커밋은 헤드 세션만, 기계 점검 불가)",
 "H1":"헤드 역할 규칙",
 "H2":"헤드 역할 규칙",
 "H3":"사용자 확인 절차",
 "H4":"행동 규칙",
 "H5":"질문 범위 규칙",
 "H6":"계약 변경 절차(열차)",
 "H7":"언어·질문 규칙",
 "H8":"대장 기록 절차",
 "D01":"구조 선언(영역 수). 점검은 D104 구조 규칙이 맡는다","D02":"D49 로 대체(저장소 통신 폐기)","D04":"리포 목록 선언. areas.json 이 정본","D05":"경계 방식 선택 기준(판단 절차)",
 "D06":"turn-engine 분리. D109 로 퇴역","D08":"관리자 콘솔 위치 선언","D09":"작업 방식(헤드/영역 역할)","D10":"비보증 선언(서버 전체 중단)",
}
def decisions():
    rows=[]
    for line in (ROOT/"docs/DECISIONS.md").read_text(encoding="utf-8").splitlines():
        m=re.match(r"^\|\s*(D\d+)\s*\|\s*(.*?)\s*\|\s*(.*)\|\s*$", line)
        if m: rows.append((m.group(1), m.group(2)[:60], m.group(2)+" "+m.group(3)))
    return rows
def claude_rules(path, sections, prefix):
    rows=[]; sec=None; n=0
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "): sec = line[3:].strip(); continue
        if sec and any(s in sec for s in sections) and re.match(r"^\s*(-|\d+\.)\s+", line):
            n+=1; text=re.sub(r"^\s*(-|\d+\.)\s+","",line).strip(); rows.append((f"{prefix}{n}", text[:60], text))
    return rows
def checks():
    out=[]
    for line in (ROOT/"docs/RULE_CHECKS.md").read_text(encoding="utf-8").splitlines():
        m=re.match(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", line)
        if m: out.append(("RULE_CHECKS#"+m.group(1), m.group(2)+" "+m.group(3)))
    p=WS/"deploy/scripts/self-checks.list"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "::" in line and not line.startswith("#"): d,c=line.split("::",1); out.append(("deploy:"+c.strip()[:70], d.strip()))
    for area in sorted(WS.glob("*/tests/test_*.py"))+sorted(WS.glob("*/scripts/test_*.py"))+sorted(WS.glob("*/scripts/test-*.sh")):
        try: head="\n".join(area.read_text(encoding="utf-8").splitlines()[:6])
        except Exception: head=""
        out.append((str(area.relative_to(WS)), head))
    return out
IDPAT=re.compile(r"\b(D\d{2,3}|U\d{2,3}|L\d{2}|G\d{2}|C\d{1,2}|H\d{1,2}|ADR[- ]?0?\d{3,4})\b")
def ids(text): return {re.sub(r"ADR[- ]?0*","ADR",x) for x in IDPAT.findall(text)}
def build():
    rules=decisions()+claude_rules(WS/"CLAUDE.md",["구조 규칙","모든 세션의 규칙","컨테이너와 개발","커밋","자동화","구조 선택"],"C")+claude_rules(ROOT/"CLAUDE.md",["규칙","하지 않는 일","세션을 끝낼 때"],"H")
    chk=checks(); chk_ids=[(name, ids(desc)) for name,desc in chk]
    lines=["# 규칙 전수 대응표(생성물, U76)","", f"생성: `python3 scripts/rules-coverage.py`. 입력은 스크립트 머리 설명. **손으로 고치지 않는다.** 규칙을 추가하면 다시 만든다(`--check` 가 RULE_CHECKS 의 점검이다).","",
           "대응 규칙: 규칙 문장과 점검 설명이 같은 ID(D##·U##·L##·G##·ADR)를 가리킬 때만 대응으로 센다. 낱말 겹침은 쓰지 않는다. `RECORD` 는 점검 대상이 아닌 결정 기록(스크립트의 RECORD_IDS, 이유 포함).","",
           "| ID | 규칙(앞 60자) | 대응 점검 | 상태 |","|---|---|---|---|"]
    n_has=n_none=n_rec=0
    for rid,short,full in rules:
        if rid in RECORD_IDS: st="RECORD: "+RECORD_IDS[rid]; n_rec+=1; matched=[]
        else:
            my={rid} | (ids(full) if rid.startswith(("C","H")) else set())
            my.add(rid)
            matched=[name for name,cids in chk_ids if rid in cids or (rid.startswith(("C","H")) and my & cids)]
            st="있음" if matched else "없음"
            if matched: n_has+=1
            else: n_none+=1
        lines.append(f"| {rid} | {short.replace('|','/')} | {'<br>'.join(sorted(set(matched))[:4]) if matched else '-'} | {st} |")
    summary=f"규칙 {len(rules)}개: 점검 있음 {n_has}, **점검 없음 {n_none}**, 기록 {n_rec}. (헤드 CLAUDE/루트 CLAUDE 규칙은 C·H 접두)"
    lines.insert(4, summary); lines.insert(5,"")
    return "\n".join(lines)+"\n"
if __name__=="__main__":
    text=build()
    if "--check" in sys.argv:
        cur=OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if cur!=text: print("RULE_COVERAGE.md 가 입력과 다르다: python3 scripts/rules-coverage.py 로 다시 만든다"); sys.exit(1)
        print("RULE_COVERAGE.md 최신"); sys.exit(0)
    OUT.write_text(text,encoding="utf-8"); print(text.splitlines()[4])
