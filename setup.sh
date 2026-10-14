#!/usr/bin/env bash
# 워크스페이스를 구성한다. head를 clone한 뒤 실행한다.
#   git clone git@github.com:Sdabin1209/openit_head.git <루트>/head
#   bash <루트>/head/setup.sh
# 하는 일: 루트의 CLAUDE.md를 head/shared/CLAUDE.root.md의 링크로 만들고(안 되면 복사),
#          head/workspace.yaml의 나머지 리포지토리를 clone한다. 이미 있는 것은 건드리지 않는다.
set -euo pipefail

HEAD_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HEAD_DIR")"

( cd "$ROOT" && ln -sfn head/shared/CLAUDE.root.md CLAUDE.md ) \
  || cp "$HEAD_DIR/shared/CLAUDE.root.md" "$ROOT/CLAUDE.md"

python3 - "$ROOT" <<'PY'
import os, re, subprocess, sys
root = sys.argv[1]
text = open(os.path.join(root, "head", "workspace.yaml")).read()
host = re.search(r"^host:\s*(\S+)", text, re.M).group(1)
missing = []
for m in re.finditer(r"\{path:\s*(\S+?),\s*remote:\s*(\S+?),\s*tag:\s*(\S+?)\s*\}", text):
    path, remote, tag = m.groups()
    dest = os.path.join(root, path)
    if os.path.exists(os.path.join(dest, ".git")):
        print(f"있음: {path}"); continue
    cmd = ["git", "clone", "-q"] + ([] if tag == "null" else ["--branch", tag]) + [f"{host}/{remote}.git", dest]
    if subprocess.run(cmd, stderr=subprocess.DEVNULL).returncode == 0:
        print(f"clone: {path}")
    else:
        missing.append(f"{path}  <- {host}/{remote}")
if missing:
    print("\n받지 못함(원격이 없거나 접근 권한 없음):", file=sys.stderr)
    for x in missing: print("  " + x, file=sys.stderr)
    sys.exit(1)
PY

cat <<EOF

완료: $ROOT
  CLAUDE.md  공통 규칙 (head/shared/CLAUDE.root.md의 링크)

헤드 세션: cd $ROOT/head && claude --add-dir ../boundary-contracts --add-dir ../survey-service/schema
영역 세션: cd $ROOT/<영역 디렉터리> && claude
EOF
