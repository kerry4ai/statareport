# Stata AI Report Generator

Automate Stata data analysis and generate structured HTML reports.

This skill provides AI agents with a complete workflow: detect Stata installation, generate annotated do-files with `ishere` markers, execute Stata code, and produce self-contained HTML reports with code, results, figures, and regression tables.

## Requirements

| Item | Requirement |
|------|-------------|
| Stata | **17 or later** (`tohtml` depends on the built-in `markdown` command) |
| Stata Edition | MP / SE / IC all supported |
| Python | 3.8+ (for cross-platform detection and execution scripts) |
| Network | Required for first-time setup (installing SSC dependencies) |

## Installation

### 1. Get the Skill Files

```bash
git clone https://github.com/kerry4ai/statareport.git stata-ai-report
```

### 2. Install to WorkBuddy

[WorkBuddy](https://workbuddy.ai) is a Windows AI Agent desktop client that supports extending capabilities via skill directories.

1. Copy the skill folder to WorkBuddy's skills directory:

```powershell
# Default path
Copy-Item -Recurse -Path .\stata-ai-report -Destination "C:\Users\<YourUsername>\.workbuddy\skills\stata-ai-report"
```

2. Restart WorkBuddy or refresh the skill list. The agent will automatically recognize the `stata-ai-report` skill.

3. When generating do-files, the agent will follow the workflow defined in `SKILL.md` and copy the commands from the `ado/` directory to the working directory as needed.

> **Tip**: If WorkBuddy is installed in a custom path, replace `.workbuddy` in the path above with the actual installation directory.

### 3. Install on Other AI Agent Platforms

#### Claude Code (Anthropic)

Add the SKILL.md content to your project's `CLAUDE.md` or `~/.claude/CLAUDE.md`:

```bash
# Project-level (current project only)
cp stata-ai-report/SKILL.md ./CLAUDE.md

# User-level (all projects)
cat stata-ai-report/SKILL.md >> ~/.claude/CLAUDE.md
```

Then ensure the ado files are accessible to Stata:
```bash
cp stata-ai-report/ado/*.ado /path/to/your/project/
```

#### OpenAI Codex CLI

Add the SKILL.md content to `codex.md`:

```bash
# Project-level
cp stata-ai-report/SKILL.md ./codex.md

# User-level
cat stata-ai-report/SKILL.md >> ~/.codex/codex.md
```

#### OpenClaw (QClaw)

Install to the OpenClaw skills directory:

```bash
# macOS / Linux
cp -r stata-ai-report ~/.openclaw/skills/stata-ai-report

# Windows
xcopy /E /I stata-ai-report %USERPROFILE%\.openclaw\skills\stata-ai-report
```

Or install via SkillHub:
```bash
openclaw skill install stata-ai-report
```

#### Hermes Agent

Copy the skill to Hermes's skills directory and reference SKILL.md:

```bash
cp -r stata-ai-report ~/.hermes/skills/stata-ai-report
```

Add to your Hermes configuration:
```yaml
skills:
  - name: stata-ai-report
    path: ~/.hermes/skills/stata-ai-report/SKILL.md
```

### 4. Install Stata Dependencies

Open Stata and run:

```stata
do "stata-ai-report/install_deps.do"
```

This script automatically checks and installs the following SSC packages (if not already installed):

| Package | Purpose |
|---------|---------|
| `pathutil` | Path utilities for `tohtml` |
| `fs` | File listing for `tohtml` directory mode |
| `moremata` | `mm_outsheet` Mata function |

If you are offline, the script will error and prompt for a network connection.

## File Structure

```
stata-ai-report/
├── SKILL.md                  # Agent workflow documentation
├── README.md                 # Chinese README
├── README_EN.md              # This file
├── QUICKSTART.md             # Full quickstart example
├── install_deps.do           # Dependency auto-install script
├── demo4ai_agents.do         # Full demo do-file (auto dataset)
├── ado/                      # Core commands (no SSC install needed)
│   ├── ishere.ado
│   ├── tohtml.ado
│   ├── outreg2e.ado
│   ├── sopen.ado
│   └── logoute.ado
└── scripts/                  # Agent helper scripts
    ├── detect_stata.py       # Cross-platform Stata detection
    └── run_analysis.py       # Cross-platform do-file execution
```

## Core Commands

### `ishere` — Mark Report Content in Do-Files

```stata
ishere # Chapter Title
ishere ## Subtitle
ishere fig using "figure.png"
ishere tab using "table.html"
```

### `tohtml` — Convert Log to HTML Report

**Standard mode (results only):**
```stata
tohtml "analysis.log", html("report.html") css(githubstyle) replace
```

**Code + results mode (for teaching / reproducibility):**
```stata
tohtml "analysis.log", html("report.html") css(githubstyle) cleancode("analysis.do") replace
```

## Output Modes Comparison

| Mode | Command | Use Case |
|------|---------|----------|
| Standard | `css(githubstyle)` | Final client report, results only |
| CleanCode | `cleancode("do.do")` | Teaching, reproducible research, full workflow |

## FAQ

**Q: Can I use Stata 16?**  
A: No. `tohtml` calls Stata's built-in `markdown` command, which is available from Stata 17 onwards.

**Q: Why is `moremata` required?**  
A: `tohtml` internally uses the `mata: mm_outsheet()` function for table output. `install_deps.do` installs it automatically.

**Q: Can I use it offline?**  
A: You need internet for the first-time dependency installation. After that, the core commands (`ishere`, `tohtml`, `outreg2e`) and scripts work offline.

**Q: Does it support macOS / Linux?**  
A: Yes. `detect_stata.py` and `run_analysis.py` are cross-platform, supporting Windows, macOS, and Linux.
