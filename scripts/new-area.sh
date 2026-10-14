#!/usr/bin/env bash
# 영역 리포지토리를 만든다: CLAUDE.md, 브리프 템플릿, git init
# 사용법: head/scripts/new-area.sh <리포지토리 이름>
set -euo pipefail

NAME="${1:?usage: new-area.sh <repo-name>}"
HEAD_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(dirname "$HEAD_DIR")"
DEST="$ROOT/$NAME"

if [ -e "$DEST" ]; then
  echo "이미 있음: $DEST" >&2
  exit 1
fi

mkdir -p "$DEST/docs/change-requests"
cp "$HEAD_DIR/templates/area-CLAUDE.md" "$DEST/CLAUDE.md"
sed -i.bak "s/{{REPO}}/$NAME/g" "$DEST/CLAUDE.md" && rm -f "$DEST/CLAUDE.md.bak"
cp "$HEAD_DIR/templates/BRIEF_TEMPLATE.md" "$DEST/docs/brief.md"
(cd "$DEST" && git init -q)

echo "만들었음: $DEST"
echo "다음: $DEST/docs/brief.md를 채운 뒤 cd $NAME && claude"
