# 技能仓库开发约定（CLAUDE.md）

本文件面向在该仓库中**编写/维护技能**的开发者（含 Claude）。所有技能遵循统一的包结构与规范。

## 仓库结构

```
skills/<skill-name>/            # 每个技能一个目录，目录名 = 技能名
├── SKILL.md                    # 技能主文档（必需，frontmatter 含 name + description）
├── references/                 # 重型参考（规范原文、长文档、数据表）——允许中文文件名
├── scripts/                    # 技能内可执行工具（可选）
└── examples/                   # 示例输入输出（可选）
```

## 新增技能的流程（铁律）

1. **一律用 `scripts/new-skill.sh <skill-name>`** 从模板创建，不要手写目录。
2. 创建后编辑 `SKILL.md` 完善内容。
3. 新技能必须经 Claude 实际试用验证后再发布（可运行 `./scripts/list.sh` 确认可发现）。

## SKILL.md frontmatter 规范

```yaml
---
name: my-skill
description: Use when ...
version: 1.0.0        # 可选
---
```

- `name`：**必须等于目录名**。仅小写字母 `a-z`、数字 `0-9`、连字符 `-`；不得以下划线/空格/大写/括号等开头。
- `description`：**只描述何时使用（触发条件），不要概括技能的工作流程**。以 "Use when" 开头最佳。字数 ≤ 1024。写流程会让 Claude 跳过正文、直接照 description 执行。
- 可加 `version` 等扩展字段。

## 正文写作要点

- **Overview**：1-2 句说明技能是什么、核心原则。
- **When to Use**：具体触发症状/场景；注明何时不应使用。
- **结构化输出**：若技能要求固定输出（JSON/表格），给出明确字段 schema 与示例。
- **不要写叙事**：只写可复用的方法/规则，不写「某次我遇到……」。
- 重型参考（>100 行的 API 文档、规范原文）放到 `references/`，正文用链接引用，避免正文臃肿。

## 引用约定

- 引用本技能内的参考文件：写相对路径 `references/xxx.md`。
- 引用其它技能：用「技能名」文字提及即可，**不要**用 `@路径`（会强制加载、浪费上下文）。

## 与安装/分发的交互

- 技能被 `scripts/install.sh` 软链到 `~/.claude/skills/`，被 Claude Code 自动发现；修改仓库内文件即时生效。
- 修改技能后需重新验证：让 Claude 用该技能跑一次真实任务。
- 若技能名需要更换：改目录名 + 改 frontmatter `name`，再重跑 `install.sh`（旧软链会被替换）。

## 禁止

- 把 `templates/` 当技能安装（它只是脚手架，不是技能）。
- 在 `skills/` 之外新增技能目录。
- 修改 `intelligent-reviewing` 的国标判定规则时，脱离 GB/T 15834/15835 原文。
