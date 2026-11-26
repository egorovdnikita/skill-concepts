#!/bin/bash
# Для облачной сессии Claude: копирует сохранённую версию скилла из claude.ai в репо и пушит, если есть изменения.
set -e
cd "$(dirname "$0")/.."
SRC=$(ls -d /root/.claude/skills/synced/*/concepts 2>/dev/null | head -1)
[ -f "$SRC/SKILL.md" ] || { echo "Скилл concepts не найден в synced"; exit 1; }
cp "$SRC/SKILL.md" SKILL.md
git add SKILL.md
if git diff --cached --quiet; then echo "Без изменений"; exit 0; fi
git commit -q -m "sync: concepts из claude.ai $(date -u +%F)"
git -c push.negotiate=true push -q origin HEAD:main
echo "Запушено"
