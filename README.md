# Stata AI Report Generator

**Automate Stata data analysis and generate structured HTML reports with code, results, figures, and tables.**

This is an AI Agent skill that enables automated Stata workflows: detect Stata installation, generate annotated do-files with `ishere` structural markers, execute Stata non-interactively, and produce self-contained HTML reports.

## ✨ Features

- 🤖 **AI Agent Ready** — Designed for AI coding agents (Claude, GPT, etc.) to autonomously run Stata analysis
- 📊 **One-Command Reports** — From raw data to publication-ready HTML with figures and regression tables
- 🏷️ **Structural Markers** — `ishere` command lets you annotate do-files with titles, figures, and tables
- 📝 **Two Output Modes** — Results-only (clean client reports) or Code+Results (teaching / reproducible research)
- 🔧 **Zero SSC Install** — Core commands (`ishere`, `tohtml`, `outreg2e`, `sopen`, `logoute`) are bundled; no manual SSC installation needed
- 🖥️ **Cross-Platform** — Python helper scripts detect and run Stata on Windows, macOS, and Linux

## 📋 Requirements

| Item | Requirement |
|------|-------------|
| Stata | **17 or later** (uses built-in `markdown` command) |
| Edition | MP / SE / IC all supported |
| Python | 3.8+ (for `detect_stata.py` and `run_analysis.py`) |
| Network | Only needed for first-time SSC dependency install |

## 🚀 Quick Start

### 1. Install SSC dependencies (one-time)

```stata
do "install_deps.do"
```

This auto-installs `pathutil`, `fs`, and `moremata` from SSC.

### 2. Copy bundled ado files to your working directory

```bash
cp ado/*.ado /path/to/your/project/
```

### 3. Write an annotated do-file

```stata
adopath ++ "."
cd "/path/to/your/project"
capture log close
log using "analysis_run.log", text replace

** # Automobile Price Analysis

** ## Data Overview
ishere
sysuse auto, clear
summarize price mpg weight

** ## Scatter Plot
ishere
scatter price mpg
graph export "scatter.png", replace
ishere fig using "scatter.png"

** ## Regression Results
ishere
regress price mpg weight
estimates store m1

regress price mpg weight i.foreign, robust
estimates store m2

outreg2e [m1 m2] using "reg_table.html", replace html
ishere tab using "reg_table.html"

capture log close
tohtml "analysis_run.log", html("report.html") css(githubstyle) replace
```

### 4. Execute

```bash
# Option A: Use the cross-platform wrapper
python scripts/run_analysis.py analysis.do

# Option B: Call Stata directly
# Windows
"C:\Program Files\Stata19\StataMP-64.exe" /e do "analysis.do"
# macOS
/Applications/Stata/StataMP.app/Contents/MacOS/StataMP -e do "analysis.do"
# Linux
/usr/local/stata18/stata-mp -e do "analysis.do"
```

### 5. View the report

Open `report.html` in your browser. Done! 🎉

## 📁 Project Structure

```
stata-ai-report/
├── SKILL.md              # Full workflow documentation for AI agents
├── README.md             # This file
├── QUICKSTART.md         # Detailed step-by-step tutorial
├── install_deps.do       # SSC dependency installer
├── demo4ai_agents.do     # Complete demo with auto data
├── ado/                  # Bundled Stata commands (no SSC install needed)
│   ├── ishere.ado        # Structural markers for reports
│   ├── tohtml.ado        # Log → HTML conversion engine
│   ├── outreg2e.ado      # Regression table export
│   ├── sopen.ado         # Open output files automatically
│   └── logoute.ado       # Summary statistics table export
└── scripts/              # Cross-platform helper scripts
    ├── detect_stata.py   # Find Stata installation
    └── run_analysis.py   # Execute do-files non-interactively
```

## 🔑 Core Commands

### `ishere` — Mark report structure in do-files

```stata
ishere # Chapter Title          // Section heading
ishere ## Subtitle              // Subsection heading
ishere                          // Code block boundary
ishere fig using "fig.png"      // Embed figure
ishere tab using "table.html"   // Embed regression table
ishere display %5.3f `r2'       // Dynamic text insertion
```

### `tohtml` — Convert log to HTML report

```stata
* Results-only mode (clean reports)
tohtml "analysis.log", html("report.html") css(githubstyle) replace

* Code + Results mode (teaching / reproducibility)
tohtml "analysis.log", html("report.html") css(githubstyle) cleancode("analysis.do") replace
```

### `outreg2e` — Export regression tables

```stata
estimates store model1
estimates store model2
outreg2e [model1 model2] using "table.html", replace html
```

## 📖 Output Modes

| Mode | When to Use |
|------|-------------|
| **Standard** (`css(githubstyle)`) | Final reports, presentations — results only |
| **CleanCode** (`cleancode("file.do")`) | Teaching, reproducible research — code + results interleaved |

## ❓ FAQ

**Q: Can I use Stata 16?**  
A: No. `tohtml` calls Stata's built-in `markdown` command, which requires Stata 17+.

**Q: Why is `moremata` needed?**  
A: `tohtml` uses `mata: mm_outsheet()` internally. `install_deps.do` installs it automatically.

**Q: Can it work offline?**  
A: First-time SSC install needs internet. After that, all bundled commands work offline.

**Q: Does it support macOS / Linux?**  
A: Yes. `detect_stata.py` and `run_analysis.py` are cross-platform.

## 📄 License

This project is provided as-is for research and educational purposes.

## 🙏 Acknowledgments

- `ishere` and `tohtml` are developed by [Kerui Du](https://github.com/kerry4ai)
- `outreg2e` extends the classic `outreg2` package
- SSC packages `pathutil`, `fs`, `moremata` by their respective authors
