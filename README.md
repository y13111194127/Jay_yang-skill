

# Jay Yang Skill

Jay Yang 的 Claude Code **技能仓库**。所有技能以社区标准布局存放在 `skills/<skill-name>/`，可同时作为 **Claude Code 插件**安装，或通过 `install.sh` 软链到个人技能目录。

## 目录结构

```
.
├── skills/                           # ★ 所有技能都放这里
│   ├── intelligent-reviewing/        #   中文文本审校纠错技能
│   │   ├── SKILL.md                  #     技能主文档
│   │   └── references/               #     参考文件（国标、错别字表等）
│   └── government-speech-skill/      #   政务讲话格式与语言校核技能
│       ├── SKILL.md                  #     技能主文档
│       ├── examples/                 #     任务示例与边界案例
│       └── references/               #     规则文档集
├── .claude-plugin/                   # Claude Code 插件清单
│   ├── plugin.json                   #     插件元数据
│   └── marketplace.json              #     本地 marketplace
├── scripts/                          # 仓库维护脚本
│   ├── install.sh                    #     软链 skills/* → ~/.claude/skills/
│   ├── uninstall.sh                  #     移除本仓库安装的软链
│   ├── new-skill.sh                  #     从模板创建新技能
│   └── list.sh                       #     列出技能与安装状态
├── templates/                        # 新技能模板
│   └── skill-template/               #     标准技能模板
└── README.md / CLAUDE.md             # 使用说明 / 技能编写规范
```

## 快速开始

### 方式一：软链到个人技能目录（推荐）

```bash
./scripts/install.sh      # 将 skills/* 软链到 ~/.claude/skills/
./scripts/list.sh         # 查看技能与安装状态
./scripts/uninstall.sh    # 卸载（仅移除本仓库创建的软链）
```

安装脚本非破坏性：若 `~/.claude/skills/<name>` 已存在真实目录，会先备份到 `~/.claude/skills/.backup/` 再替换为软链。

### 方式二：作为 Claude Code 插件安装

```bash
# 把本仓库作为 marketplace 添加
claude plugin marketplace add /path/to/jay-yang-skill

# 安装其中的插件
claude plugin install jay-yang-skill@jay-yang-skill-marketplace
```

> 插件安装与软链安装**二选一**即可。

## 当前技能

| 技能 | 说明 |
|------|------|
| `intelligent-reviewing` | 中文文本审校纠错（错别字、标点、数字用法），严格依据 GB/T 15834-2011 与 GB/T 15835-2011 |
| `government-speech-skill` | 政务讲话格式与语言校核，支持讲话稿、演讲稿、发言稿、主持词、致辞等多种文种，具备素材处理、规则校核、降 AI 味等功能 |

## 新增一个技能

```bash
./scripts/new-skill.sh my-new-skill   # 生成 skills/my-new-skill/
```

编辑 `skills/my-new-skill/SILL.md`：
- frontmatter `name` 必须等于目录名（小写字母/数字/连字符）
- `description` 以 "Use when" 开头，只描述**何时使用**
- 重型参考放 `references/`，可执行工具放技能内 `scripts/`

## 技能验证

`government-speech-skill` 包含技能包验证脚本：

```bash
python3 skills/government-speech-skill/scripts/validate_package.py skills/government-speech-skill/
```

该脚本会检查 frontmatter 格式规范、文件结构完整性等。

## 迁移说明

仓库从 Spring Boot/Gradle 工程改造而来，旧的 `~/.claude/skills/intelligent-reviewing/` 在首次执行 `install.sh` 时会自动备份到 `~/.claude/skills/.backup/`，不会丢失。

## 许可

本仓库内容遵循各技能自身的许可协议。