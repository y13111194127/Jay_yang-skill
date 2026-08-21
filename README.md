# Jay Yang Skill

Jay Yang 的 Claude Code **技能仓库**。所有技能以社区标准布局存放在 `skills/<skill-name>/`，可同时作为 **Claude Code 插件**安装，或通过 `install.sh` 软链到个人技能目录。

## 目录结构

```
.
├── skills/                    # ★ 所有技能都放这里
│   └── intelligent-reviewing/ # 技能示例：中文文本审校纠错
│       ├── SKILL.md           #   技能主文档（frontmatter: name + description）
│       └── references/        #   重型参考文件（国标、错别字表等）
├── .claude-plugin/            # Claude Code 插件清单
│   ├── plugin.json            #   插件元数据（name: jay-yang-skill）
│   └── marketplace.json       #   本地 marketplace（source: "./"）
├── scripts/                   # 仓库维护脚本
│   ├── install.sh             #   软链 skills/* → ~/.claude/skills/
│   ├── uninstall.sh           #   移除本仓库安装的软链
│   ├── new-skill.sh           #   从模板创建新技能
│   └── list.sh                #   列出技能与安装状态
├── templates/                 # 新技能模板（new-skill.sh 使用）
└── README.md / CLAUDE.md      # 使用说明 / 技能编写规范
```

## 快速开始

### 方式一：软链到个人技能目录（最简单）

```bash
./scripts/install.sh      # 将 skills/* 软链到 ~/.claude/skills/
./scripts/list.sh         # 查看技能与安装状态
./scripts/uninstall.sh    # 卸载（仅移除本仓库创建的软链，安全）
```

安装脚本非破坏性：若 `~/.claude/skills/<name>` 已存在真实目录，会先备份到
`~/.claude/skills/.backup/` 再替换为软链。

### 方式二：作为 Claude Code 插件安装

```bash
# 把本仓库作为 marketplace 添加（路径指向仓库根目录）
claude plugin marketplace add /lenovo/tysoft/Jay_yang-skill

# 安装其中的插件
claude plugin install jay-yang-skill@jay-yang-skill-marketplace
```

> 插件安装与软链安装**二选一**即可，重复使用会造成同名技能重复注册。

## 新增一个技能

```bash
./scripts/new-skill.sh my-new-skill   # 生成 skills/my-new-skill/
```

然后编辑 `skills/my-new-skill/SKILL.md`：

- frontmatter `name` 必须等于目录名（小写字母/数字/连字符）
- `description` 以 "Use when" 开头，只描述**何时使用**，不要概括流程
- 重型参考（规范原文、长文档）放 `references/`，可执行工具放技能内 `scripts/`

详见 [CLAUDE.md](CLAUDE.md) 的编写规范。

## 当前技能

| 技能 | 说明 |
|---|---|
| `intelligent-reviewing` | 中文文本审校纠错（错别字、标点、数字用法），严格依据 GB/T 15834-2011 与 GB/T 15835-2011 |

## 迁移说明

仓库从 Spring Boot/Gradle 工程改造而来，旧的 `~/.claude/skills/intelligent-reviewing/`
（含 `knowledge/` PDF 与 `examples/`）在首次执行 `install.sh` 时会自动备份到
`~/.claude/skills/.backup/`，不会丢失。是否将其中内容合并回仓库由你自行决定。
