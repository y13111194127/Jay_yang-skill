#!/usr/bin/env bash
# 从 templates/skill-template/ 复制并创建一个新技能到 skills/<skill-name>/。
# 用法: ./scripts/new-skill.sh <skill-name>
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$REPO_ROOT/templates/skill-template"
SKILLS_DIR="$REPO_ROOT/skills"

name="${1:-}"
if [ -z "$name" ]; then
  echo "用法: $0 <skill-name>" >&2
  echo "说明: skill-name 需为小写字母/数字/连字符，且与目录名一致。" >&2
  exit 1
fi

if ! [[ "$name" =~ ^[a-z][a-z0-9]*(-[a-z0-9]+)*$ ]]; then
  echo "错误: '$name' 不合法。仅允许小写字母、数字、连字符（如 intelligent-reviewing）。" >&2
  exit 1
fi

skill_dir="$SKILLS_DIR/$name"
if [ -e "$skill_dir" ]; then
  echo "错误: $skill_dir 已存在。" >&2
  exit 1
fi

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "错误: 模板目录不存在 $TEMPLATE_DIR" >&2
  exit 1
fi

mkdir -p "$SKILLS_DIR"
cp -R "$TEMPLATE_DIR" "$skill_dir"

# 替换 SKILL.md 中的占位符
sed -i "s/{{skill-name}}/$name/g" "$skill_dir/SKILL.md"

echo "已创建技能: $skill_dir"
echo "请编辑 $skill_dir/SKILL.md 完善 description 与正文。"
echo "安装到 Claude Code: ./scripts/install.sh"
