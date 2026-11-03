#!/usr/bin/env bash
# 규칙 C33·D37: 모든 리포의 커밋 작성자는 Sdabin1209 noreply 다(개인 이메일 금지). 사용: commit-author-check.sh [커밋 수(기본 200)]
set -uo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd); N=${1:-200}; FAILS=0
for r in $(python3 -c "import json;print(' '.join(a['name'] if isinstance(a,dict) else a for a in json.load(open('$WS/head/shared/areas.json'))['areas']))" 2>/dev/null || ls -d "$WS"/*/ | xargs -n1 basename); do
  [ -d "$WS/$r/.git" ] || continue
  bad=$(git -C "$WS/$r" log --all -n "$N" --format='%ae %h' | grep -v '^99588729+Sdabin1209@users.noreply.github.com ' | head -3)
  if [ -n "$bad" ]; then echo "FAIL $r: 작성자가 다른 커밋: $(echo "$bad" | tr '\n' ' ')"; FAILS=$((FAILS+1)); fi
done
[ $FAILS = 0 ] && echo "OK: 커밋 작성자 규칙(최근 $N 커밋, 리포 전체)" || exit 1
