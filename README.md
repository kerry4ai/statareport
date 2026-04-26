# Stata AI Report Generator

自动化 Stata 数据分析并生成结构化 HTML 报告。

本 Skill 为 AI Agent 提供了一套完整的工作流：检测 Stata 安装位置、生成带 `ishere` 标记的注释 do-file、执行 Stata 代码、输出自包含的 HTML 报告（含代码、结果、图表和回归表格）。

## 系统要求

| 项目 | 要求 |
|------|------|
| Stata | **17 或更高版本**（`tohtml` 依赖内置 `markdown` 命令） |
| Stata 版本 | MP / SE / IC 均可 |
| Python | 3.8+（用于跨平台检测和执行脚本） |
| 网络 | 首次安装时需要联网（安装 SSC 依赖包） |

## 安装

### 1. 获取 Skill 文件

```bash
git clone https://github.com/kerry4ai/statareport.git stata-ai-report
```

### 2. 安装到 WorkBuddy

[WorkBuddy](https://workbuddy.ai) 是 Windows 上的 AI Agent 桌面客户端，支持通过 skill 目录扩展能力。

1. 将 skill 文件夹拷贝到 WorkBuddy 的 skills 目录：

```powershell
# 默认路径
Copy-Item -Recurse -Path .\stata-ai-report -Destination "C:\Users\<你的用户名>\.workbuddy\skills\stata-ai-report"
```

2. 重启 WorkBuddy 或刷新 skill 列表，Agent 即可自动识别 `stata-ai-report` skill。

3. Agent 在生成 do-file 时会自动引用 `SKILL.md` 中的工作流，并将 `ado/` 目录下的命令拷贝到工作目录。

> **提示**：如果 WorkBuddy 安装在自定义路径，请将上述路径中的 `.workbuddy` 替换为实际安装目录。

### 3. 在各 AI Agent 平台中安装

#### Claude Code (Anthropic)

将 SKILL.md 内容添加到项目的 `CLAUDE.md` 或 `~/.claude/CLAUDE.md`：

```bash
# 项目级（仅当前项目生效）
cp stata-ai-report/SKILL.md ./CLAUDE.md

# 用户级（所有项目生效）
cat stata-ai-report/SKILL.md >> ~/.claude/CLAUDE.md
```

然后确保 ado 文件可被 Stata 访问：
```bash
cp stata-ai-report/ado/*.ado /path/to/your/project/
```

#### OpenAI Codex CLI

将 SKILL.md 内容添加到 `codex.md`：

```bash
# 项目级
cp stata-ai-report/SKILL.md ./codex.md

# 用户级
cat stata-ai-report/SKILL.md >> ~/.codex/codex.md
```

#### OpenClaw (QClaw)

安装到 OpenClaw skills 目录：

```bash
# macOS / Linux
cp -r stata-ai-report ~/.openclaw/skills/stata-ai-report

# Windows
xcopy /E /I stata-ai-report %USERPROFILE%\.openclaw\skills\stata-ai-report
```

或使用 SkillHub 安装：
```bash
openclaw skill install stata-ai-report
```

#### Hermes Agent

将 Skill 放到 Hermes 的 skills 目录并引用 SKILL.md：

```bash
cp -r stata-ai-report ~/.hermes/skills/stata-ai-report
```

在 Hermes 配置中添加：
```yaml
skills:
  - name: stata-ai-report
    path: ~/.hermes/skills/stata-ai-report/SKILL.md
```

### 4. 安装 Stata 依赖

打开 Stata，运行：

```stata
do "stata-ai-report/install_deps.do"
```

该脚本会自动检查并安装以下 SSC 包（如尚未安装）：

| 包名 | 用途 |
|------|------|
| `pathutil` | `tohtml` 的路径处理工具 |
| `fs` | `tohtml` 目录模式的文件列表 |
| `moremata` | `mm_outsheet` Mata 函数 |

如果处于离线环境，脚本会报错并提示需要网络连接。

## 文件结构

```
stata-ai-report/
├── SKILL.md                  # Agent 使用的工作流文档
├── README.md                 # 本文件
├── QUICKSTART.md             # 完整上手示例
├── install_deps.do           # 依赖自动安装脚本
├── demo4ai_agents.do         # 完整演示 do-file（auto 数据）
├── ado/                      # 核心命令（无需 SSC 安装）
│   ├── ishere.ado
│   ├── tohtml.ado
│   ├── outreg2e.ado
│   ├── sopen.ado
│   └── logoute.ado
└── scripts/                  # Agent 辅助脚本
    ├── detect_stata.py       # 跨平台 Stata 检测
    └── run_analysis.py       # 跨平台 do-file 执行
```

## 核心命令简介

### `ishere` — 在 do-file 中标记报告内容

```stata
ishere # 章节标题
ishere ## 子标题
ishere fig using "figure.png"
ishere tab using "table.html"
```

### `tohtml` — 将 log 转换为 HTML 报告

**标准模式（仅结果）：**
```stata
tohtml "analysis.log", html("report.html") css(githubstyle) replace
```

**代码+结果模式（适合教学/复现）：**
```stata
tohtml "analysis.log", html("report.html") css(githubstyle) cleancode("analysis.do") replace
```

## 两种输出模式对比

| 模式 | 命令 | 适用场景 |
|------|------|---------|
| 标准模式 | `css(githubstyle)` | 最终交付报告，只展示结果 |
| CleanCode | `cleancode("do.do")` | 教学、可复现研究、展示完整工作流 |

## 常见问题

**Q: Stata 16 可以用吗？**  
A: 不行。`tohtml` 调用 Stata 内置的 `markdown` 命令，该命令从 Stata 17 开始提供。

**Q: 为什么需要 `moremata`？**  
A: `tohtml` 内部使用 `mata: mm_outsheet()` 函数输出表格数据。`install_deps.do` 会自动安装。

**Q: 可以离线使用吗？**  
A: 首次安装依赖需要联网。安装完成后，核心命令（`ishere`、`tohtml`、`outreg2e`）和脚本均可离线使用。

**Q: 支持 macOS / Linux 吗？**  
A: 支持。`detect_stata.py` 和 `run_analysis.py` 已针对 Windows、macOS、Linux 三平台做了适配。
