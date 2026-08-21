#!/usr/bin/env bash
# 列出仓库内的技能及其在 ~/.claude/skills/ 下的安装状态。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
DEST_DIR="$HOME/.claude/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "错误: 未找到技能目录 $SKILLS_DIR" >&2
  exit 1
fi

shopt -s nullglob
skills=("$SKILLS_DIR"/*/)
if [ "${#skills[@]}" -eq 0 ]; then
  echo "仓库内暂无技能。用 ./scripts/new-skill.sh <skill-name> 创建第一个。"
  exit 0
fi

printf "%-28s %-10s %s\n" "技能" "状态" "说明"
printf "%-28s %-10s %s\n" "----" "----" "----"

for skill in "${skills[@]}"; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  link="$DEST_DIR/$name"

  if [ -L "$link" ] && [ "$(readlink "$link")" = "$skill" ]; then
    status="软链已装"
  elif [ -e "$link" ]; then
    status="占用(非软链)"
  elif [ -e "$DEST_DIR/.backup/$name-"* ] 2>/dev/null; then
    status="已备份"
  else
    status="未安装"
  fi

  desc=""
  if [ -f "$skill/SKILL.md" ]; then
    desc="$(awk -F': *' '/^description:/{sub(/^description: *"/,"",$2); gsub(/"/,"",$2); print $2; exit}' "$skill/SKILL.md")"
  else
    desc="(缺少 SKILL.md)"
  fi
  printf "%-28s %-10s %s\n" "$name" "$status" "$desc"
done

echo
echo "插件安装状态: $([ -f "$REPO_ROOT/.claude-plugin/plugin.json" ] && echo "已配置 .claude-plugin/" || echo "未配置")"
