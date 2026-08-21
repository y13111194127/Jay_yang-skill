#!/usr/bin/env bash
# 将 skills/ 下的每个技能软链到 ~/.claude/skills/，供 Claude Code 个人级发现。
# 非破坏性：若目标已存在真实目录/文件，先备份到 ~/.claude/skills/.backup/ 再替换为软链。
set -euo pipefail

# 仓库根目录（脚本所在目录的上一级）
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="$HOME/.claude/skills"
BACKUP_DIR="$DEST_DIR/.backup"
TARGET_SKILL_DIR="$REPO_ROOT/skills"

if [ ! -d "$TARGET_SKILL_DIR" ]; then
  echo "错误: 未找到技能目录 $TARGET_SKILL_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

installed=0
skipped=0
for skill in "$TARGET_SKILL_DIR"/*/; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  link="$DEST_DIR/$name"

  if [ -L "$link" ]; then
    if [ "$(readlink "$link")" = "$skill" ]; then
      echo "已安装: $name -> $skill"
      installed=$((installed + 1))
      continue
    fi
    # 指向别处的软链：先移除再重建
    rm "$link"
    echo "移除旧软链: $link"
  fi

  if [ -e "$link" ]; then
    # 真实目录/文件（例如旧的手动复制版本），备份后替换
    mkdir -p "$BACKUP_DIR"
    backup="$BACKUP_DIR/$name-$(date +%Y%m%d-%H%M%S)"
    mv "$link" "$backup"
    echo "已备份旧版本: $link -> $backup"
  fi

  ln -s "$skill" "$link"
  echo "已安装: $name -> $skill"
  installed=$((installed + 1))
done

if [ "$installed" -eq 0 ]; then
  echo "未发现可安装的技能（$TARGET_SKILL_DIR 下没有技能目录）。" >&2
  exit 1
fi

echo
echo "完成。共安装 $installed 个技能。"
echo "提示: 若同时以插件形式安装（claude plugin install），请勿重复使用本脚本，避免同名技能冲突。"
