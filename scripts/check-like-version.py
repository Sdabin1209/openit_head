#!/usr/bin/env python3
"""SQL 의 LIKE·문자열 포함으로 JSON 레코드의 버전·필드를 판별하지 않는다(D117 '받아들이는 조건은 전부 스키마', C43, 계약 CONVENTIONS 10절).
왜: 직렬화된 JSON 글에서 '"schema_version":"1' 이나 해시 문자열을 LIKE·instr·position 으로 찾으면 키 순서·공백·이스케이프·다른 필드의 같은 글자에
따라 판정이 갈리고, 스키마가 정한 필드가 아닌 글자 모양이 받아들이는 조건이 된다. 필드는 열로 두거나 JSON 연산자(->>, json_extract)로 꺼내 같음(=)으로 비교한다.
센다(SQL 을 담은 .py·.ts·.js·.sh·.sql, 시험 파일 포함 — 시험이 같은 판별을 굳히므로):
  L LIKE/ILIKE/GLOB 이 버전·JSON 단서(version, schema, json, record, payload, body, ::text, '%"' 같은 JSON 키 따옴표)와 같은 줄에 있는 것
  S instr( / strpos( / position( … in … ) / locate( 가 그 단서와 같은 줄에 있는 것(문자열 포함 검색)
  F JSON 연산자로 꺼낸 값에 LIKE(->> … LIKE, json_extract(…) LIKE): 버전을 접두 글자로 판별
셈하지 않는 것: 주석(#, --, //), DB 목록 조회(sqlite_master·information_schema·pg_catalog·PRAGMA·역할 이름: JSON 레코드가 아니다), 허용 목록(ALLOW, 빈 목록에서 시작).
사용: check-like-version.py [--self-test]. 종료 0 통과, 1 위반."""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _checklib as L  # noqa: E402

ALLOW = {}
CUE = re.compile(r"version|(?<!information_)schema(?!_name)|json|\brecord\b|payload|\bbody\b|::text|%\\?\"|\\?\"%|'\"", re.I)
LIKE = re.compile(r"\b(I?LIKE|GLOB)\b", re.I)
CONTAINS = re.compile(r"\b(instr|strpos|locate)\s*\(|\bposition\s*\([^)]*\bin\b", re.I)
FIELD_LIKE = re.compile(r"(->>?\s*'[^']*'\s*\)?|json_extract\s*\([^)]*\))\s*(NOT\s+)?I?LIKE\b", re.I)
CATALOG = re.compile(r"sqlite_master|information_schema|pg_catalog|pg_roles|pg_tables|PRAGMA|rolname|table_name", re.I)   # DB 목록 조회(테이블·역할 이름)는 JSON 레코드가 아니다
SQLISH = re.compile(r"\b(SELECT|UPDATE|DELETE|WHERE|FROM|AND|OR)\b")


def scan(a, rel, text):
    lg = L.lang(rel, text)
    if lg is None:
        return []
    lines = L.strip_js_comments(text) if lg == "js" else [re.sub(r"--\s.*$", "", x) for x in L.strip_hash_comments(text)] if lg in ("py", "sh") else [re.sub(r"--.*$", "", x) for x in text.splitlines()]
    out = []
    for i, ln in enumerate(lines, 1):
        if CATALOG.search(ln):
            continue
        if FIELD_LIKE.search(ln):
            out.append((i, "F", "JSON 필드 값을 LIKE 로 판별 — 같음(=)·열·스키마 필드로 비교한다"))
        elif LIKE.search(ln) and CUE.search(ln) and (SQLISH.search(ln) or lg == "sql" or re.search(r"\bLIKE\s+('|%s|\?|\$\d)", ln)):
            out.append((i, "L", "JSON 글을 LIKE 로 판별 — 필드를 꺼내 같음으로 비교한다"))
        elif CONTAINS.search(ln) and CUE.search(ln) and (SQLISH.search(ln) or lg == "sql"):
            out.append((i, "S", "JSON 글에서 문자열 포함 검색 — 필드·참조 열로 비교한다"))
    return out


def self_test():
    bad = []
    pos = [("x.py", "cur.execute(\"SELECT id FROM recs WHERE record LIKE '%\\\"schema_version\\\": \\\"1%'\")\n"),
           ("x.py", "q = \"AND NOT EXISTS (SELECT 1 FROM drafts WHERE position(%s in record) > 0)\"\n"),
           ("x.py", "q = \"AND NOT EXISTS (SELECT 1 FROM drafts WHERE instr(record, ?) > 0)\"\n"),
           ("x.sql", "select * from t where body::text like '%version%';\n"),
           ("x.ts", "db.query(`SELECT * FROM t WHERE data->>'version' LIKE '1.%'`)\n"),
           ("x.py", "c.execute(\"SELECT 1 FROM t WHERE json_extract(doc, '$.v') LIKE ?\", (p,))\n")]
    neg = [("x.py", "c.execute(\"SELECT * FROM t WHERE name LIKE ?\", (p,))\n"), ("x.py", "# WHERE record LIKE '%version%'\n"),
           ("x.sql", "-- where record like '%version%'\n"), ("x.py", "c.execute(\"SELECT 1 FROM t WHERE schema_version = ?\", (v,))\n"),
           ("x.py", "c.execute(\"SELECT 1 FROM t WHERE data->>'version' = %s\", (v,))\n"), ("x.md", "WHERE record LIKE '%v%'\n"),
           ("x.py", "c.execute(\"SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'\")\n"),
           ("x.py", "c.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'x%'\")\n")]
    for rel, t in pos:
        if not scan("z", rel, t):
            bad.append(f"놓침 {rel} {t!r}")
    for rel, t in neg:
        if scan("z", rel, t):
            bad.append(f"거짓양성 {rel} {t!r}")
    return bad


if __name__ == "__main__":
    sys.exit(L.run("SQL LIKE·문자열 포함 JSON 판별", scan, self_test, ALLOW, pathlib.Path(__file__).name))
