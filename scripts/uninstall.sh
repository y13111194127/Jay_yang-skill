#!/usr/bin/env bash
# 移除由本仓库 install.sh 创建的技能软链。绝不删除真实目录/文件。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="$HOME/.claude/skills"
TARGET_SKILL_DIR="$REPO_ROOT/skills"

if [ ! -d "$TARGET_SKILL_DIR" ]; then
  echo "错误: 未找到技能目录 $TARGET_SKILL_DIR" >&2
  exit 1
fi

removed=0
for skill in "$TARGET_SKILL_DIR"/*/; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  link="$DEST_DIR/$name"

  if [ -L "$link" ] && [ "$(readlink "$link")" = "$skill" ]; then
    rm "$link"
    echo "已移除: $link"
    removed=$((removed + 1))
  fi
done

echo
if [ "$removed" -eq 0 ]; then
  echo "未找到由本仓库安装的技能软链，无需操作。"
else
  echo "共移除 $removed 个软链。"
  echo "提示: 安装前被备份的旧版本位于 ~/.claude/skills/.backup/，如需恢复可手动复制回 $DEST_DIR/。"
fi
