---
name: stata-ai-report
description: Automate Stata data analysis and generate structured HTML reports using the ishere/tohtml package. This skill should be used when users need to run Stata analysis and produce HTML reports with code, results, figures, and tables. Trigger phrases include run stata analysis, stata regression report, generate stata html report, 用stata做回归并出报告, stata分析报告, 跑stata并生成html, stata embed 单文件报告, stata cleancode 教学报告.
---

# Stata AI Report Generator

Automate Stata data analysis and generate structured HTML reports using the `ishere`/`tohtml` package. This skill enables AI agents to:

- Detect Stata installation (StataMP, StataSE, StataMP-64.exe)
- Generate standard do-files annotated only where needed (`ishere` markers are optional for ordinary code)
- Execute Stata code non-interactively
- Produce self-contained HTML reports with code, results, figures, and tables

## Design Philosophy

The `ishere`/`tohtml` workflow is built on three principles:

1. **Zero-intrusion** — You keep writing ordinary Stata do-files. `ishere` is an auxiliary marker that does not change statistical results.
2. **Minimal learning** — Two commands (`ishere`, `tohtml`) cover almost everything; advanced features are optional.
3. **Single source** — Code, results, figures, tables, and structure all live in one do-file and one log. `tohtml` post-processes the log into Markdown + HTML.

**Key behavior: automatic code-block inference.** In the standard workflow you do **not** need to mark ordinary Stata code blocks. `tohtml` reads the log and automatically recognizes logged Stata commands and output, wrapping them in balanced fenced code blocks. You only add explicit markers for:

- Section headings (`ishere # ...` / `ishere ## ...`)
- Narrative text blocks (`/** ... **/`)
- Figures (`ishere fig using "..."`)
- Tables (`ishere tab using "..."`)
- Dynamic values inside narrative (`ishere display ...` + `{ishere display ...}`)

Explicit code-boundary markers (`ishere` / `**\`\`\``) remain available for fine control in complex logs, but they are optional.

## Prerequisites

- **Stata 17 or later** (required for the built-in `markdown` command used by `tohtml`)
- Stata MP/SE/IC flavor is acceptable
- Internet connection for first-time setup (to install SSC dependencies)
- No permanent package installation required: the core `ishere`, `tohtml`, `outreg2e`, `sopen`, `logoute` ado files and the `tohtml.css` stylesheet are bundled in this skill under `ado/` and loaded via `adopath ++`

### External Dependencies

The following SSC packages are required and auto-installed by `install_deps.do`:

| Package | Provides | Auto-installed? |
|---------|----------|-----------------|
| `pathutil` | Path utilities for `tohtml` | Yes (via `install_deps.do`) |
| `fs` | File listing for `tohtml` directory mode | Yes (via `install_deps.do`) |
| `moremata` | `mm_outsheet` Mata function used by `tohtml` | Yes (via `install_deps.do`) |
| `markdown` | Built into Stata 17+ | N/A (comes with Stata) |

## Bundled Commands

The following files are included in `ado/` and loaded via `adopath ++`:

| File | Command | Purpose |
|------|---------|---------|
| `ishere.ado` | `ishere` | Structural markers / emit figures, tables, values |
| `tohtml.ado` | `tohtml` | Log-to-HTML (and directory) conversion engine |
| `tohtml.css` | — | Default GitHub-like stylesheet (used automatically when `css()` is omitted) |
| `outreg2e.ado` | `outreg2e` | Regression table export |
| `sopen.ado` | `sopen` | Open output files automatically |
| `logoute.ado` | `logoute` | Export summary statistics tables |

## Workflow

### Phase 1: First-Time Setup (install dependencies)

```stata
do "C:\Users\kerry\.workbuddy\skills\stata-ai-report\install_deps.do"
```

This checks your Stata version and installs `pathutil`, `fs`, and `moremata` from SSC if missing.

### Phase 2: Detect Stata

```bash
python scripts/detect_stata.py
```

Searches PATH and platform-specific installation directories:
- **Windows**: `C:\Program Files\Stata*`, `D:\Program\Stata*`
- **macOS**: `/Applications/Stata*/Stata*.app/Contents/MacOS`
- **Linux**: `/usr/local/stata*`, `/opt/stata*`, `~/stata*`

If not found, ask the user for the full path.

Known locations on this system:
- `D:\Program\StataNow19\StataMP-64.exe` (Stata 19)
- `C:\Users\kerry\app\Stata18` (Stata 18)

**Important**: Stata 19's profile.do redirects PLUS/PERSONAL paths to Stata 18's directories. Always use the explicit path to the Stata 19 executable to ensure correct package resolution.

### Phase 3: Prepare Working Directory

Before executing the do-file, check which bundled commands are already available in Stata and only copy the missing files (including `tohtml.css`) to the working directory.

```stata
foreach cmd in ishere tohtml outreg2e sopen logoute {
    capture which `cmd'
    if _rc display "`cmd' NOT FOUND — needs copy"
    else    display "`cmd' already available"
}
```

**Windows (PowerShell):**
```powershell
$source = "C:\Users\kerry\.workbuddy\skills\stata-ai-report\ado\"
$dest   = "C:\Users\kerry\Desktop\YourProject\"
Copy-Item -Path "$source\ishere.ado","$source\tohtml.ado","$source\tohtml.css" -Destination $dest
```

**macOS/Linux (bash):**
```bash
SOURCE="$HOME/.workbuddy/skills/stata-ai-report/ado/"
DEST="$HOME/Desktop/YourProject/"
cp "$SOURCE"{ishere,tohtml}.ado "$SOURCE"tohtml.css "$DEST"
```

If all commands are already available, skip the copy step (the default `tohtml.css` still loads from the package/ado path).

### Phase 4: Generate Do-File

Write a **standard** do-file. You do NOT need `ishere` before ordinary code — `tohtml` infers code blocks automatically. Add markers only for headings, narrative, figures, tables, and dynamic values.

```stata
* ============================================================
* Stata Analysis Report - Generated by AI Agent
* Date: $date
* Task: $description
* ============================================================

* Add bundled ado files + css to search path (current directory)
adopath ++ "."

* Set working directory
cd "$working_dir"

* Close any existing log to avoid conflicts
capture log close

* Start logging with a name DIFFERENT from the do-file name
log using "analysis_run.log", text replace

** # $main_title

** ## Data Overview
sysuse auto, clear
summarize price mpg weight

** ## Price vs MPG Scatter Plot
scatter price mpg
graph export "scatter_price_mpg.png", replace
ishere fig using "scatter_price_mpg.png"

** ## Regression Analysis
regress price mpg weight
estimates store ols_model

** ## Model Summary
ishere display %5.3f e(r2)
/**
The OLS regression yields an R-squared of {ishere display %5.3f e(r2)}.
**/

outreg2e [ols_model] using "regression_table.html", replace html
ishere tab using "regression_table.html"

* Close log BEFORE calling tohtml
capture log close

* Generate HTML report (default GitHub-like styling via bundled tohtml.css)
tohtml "analysis_run.log", html("report.html") replace
```

#### Do-File Structure Rules

1. **Add ado path**: Include `adopath ++ "."` so Stata finds the bundled commands and `tohtml.css`. Optional only if all commands were already available and `tohtml.css` resolves from the package path.

2. **Set working directory**: Use `cd` so outputs land in the right place.

3. **Log naming**: The log filename must differ from the do-file filename (e.g. do-file `analysis.do` → log `analysis_run.log`, NOT `analysis.log`) to avoid file locks in batch mode.

4. **Code blocks are automatic.** Do **not** wrap ordinary Stata code in `ishere`. `tohtml` recognizes logged commands and output and fences them automatically. Optional explicit boundaries: `ishere`, `ishere ```` ``` ````, or `**\`\`\`` placed at a code boundary.

5. **Headings**:
   ```stata
   ishere # Main Title
   ishere ## Subsection
   ```
   (Also valid: `** # Main Title`, `** ## Subsection`.)

6. **Figures — ALWAYS use `ishere fig using`** after `graph export`:
   ```stata
   scatter price mpg
   graph export "scatter.png", replace
   ishere fig using "scatter.png"
   ishere fig using "scatter.png", zoom(80%)
   ishere figure using "scatter.png", height(400px) width(600px)
   ```
   Supported image formats: PNG, JPG, JPEG, SVG, GIF, BMP, WEBP.

7. **Tables — `outreg2e` (or `collect export`) then `ishere tab using`** (two separate steps; do NOT add `ishere` as an option to `outreg2e`):
   ```stata
   qui regress price mpg weight
   estimates store model1
   outreg2e [model1] using "table.html", replace html
   ishere tab using "table.html"
   ishere table using "table.html", height(500px) width(100%)
   ```
   Tables may be HTML/HTM or Markdown (`.md`). For `collect export` / `etable` / `dtable` HTML with a sidecar CSS, pass `cssfile()`:
   ```stata
   collect export "table1.html", tableonly cssfile("mystyle.css") replace
   ishere tab using "table1.html", cssfile("mystyle.css")
   ```

8. **Dynamic text** (optional) — emit a value and reference it inside a narrative block:
   ```stata
   ishere display %5.3f e(r2)
   /**
   R-squared is {ishere display %5.3f e(r2)}.
   **/
   ```
   `ishere display` accepts the same arguments as Stata's `display` (so `e(r2)` works directly — no intermediate local macro needed). Each `ishere display` applies only to the **first** `/** ... **/` narrative block that follows it; issue another `ishere display` before each further block that should reuse the value. Narrative blocks follow Markdown and may contain LaTeX math.

9. **Narrative text blocks use `/** ... **/`** (NOT `ishere /* ... */` or `ishere */` — those are unsupported):
   ```stata
   /**
   This is explanatory text in Markdown. It can include math:
   the fitted line is $price = \beta_0 + \beta_1 mpg$.
   **/
   next_stata_command
   ```
   After a `/** ... **/` block, the next Stata command is recognized automatically; no trailing `ishere` is required.

10. **Report generation** (default styling; omit `css()` to use the bundled `tohtml.css`):
    ```stata
    capture log close
    tohtml "analysis_run.log", html("report.html") replace
    ```

### Phase 5: Execute Stata

```bash
python scripts/run_analysis.py analysis.do
```

Or call Stata directly:

**Windows:**
```powershell
& "D:\Program\StataNow19\StataMP-64.exe" /e do "analysis.do"
```

**macOS/Linux:**
```bash
/Applications/Stata/StataMP.app/Contents/MacOS/StataMP -e do "analysis.do"
# or
/usr/local/stata18/stata-mp -e do "analysis.do"
```

### Phase 6: Deliver Report

1. Check `report.html` exists in the working directory
2. Return the HTML file path to the user
3. Optionally provide a summary of key findings

## Reference: Command Details

### ishere Command

`ishere` has two syntax-dependent forms — the form is chosen automatically by the syntax used.

**Mode 1 — Placeholder (mark structure; produces no visible output):**

| Usage | Meaning |
|-------|---------|
| `ishere` | Generic code-boundary marker (optional; code is auto-fenced otherwise) |
| `ishere ```` ``` ```` | Explicit code-block boundary |
| `**\`\`\`` | Same as above (comment form) |
| `ishere # Title` | Main heading |
| `ishere ## Subtitle` | Subheading |
| `/** ... **/` | Narrative Markdown text block |

**Mode 2 — Emit (writes Markdown/HTML into the log):**

```stata
ishere display %fmt value            // emit a formatted scalar/macro (e(r2) allowed)
ishere fig|figure using "f.png" [, zoom(string) height(string) width(string)]
ishere tab|table using "t.html" [, height(string) width(string) cssfile(filename)]
```

- `ishere display` prints the same output as `display`; place a matching `{ishere display %fmt value}` tag inside the next `/** ... **/` block and `tohtml` replaces it with the printed value.
- Figures: image formats PNG, JPG, JPEG, SVG, GIF, BMP, WEBP; backslashes in paths become forward slashes.
- Tables: HTML/HTM or MD; `cssfile()` links a `collect`/`etable`/`dtable` sidecar stylesheet so the table keeps its style inside the iframe.
- `ishere /*` / `ishere */` are **not** supported — use `/** ... **/` for narrative.

### tohtml Command

`tohtml` has two syntax-dependent forms, chosen by the first positional argument.

**Log-file form** (convert a Stata log, optionally with `ishere` markers):
```stata
tohtml "analysis_run.log" [, md(filename) html(filename) replace css(filename)
    embed zip(filename|.) bundle clean cleancode mathjax]
```

**Directory form** (gather exported figures/tables from one or more folders into one report):
```stata
tohtml "figures/" "tables/" [, html(filename) replace embed zip(filename|.) bundle
    css(filename) width(string) height(string) zoom(string)]
```

**Options**

| Option | Form | Effect |
|--------|------|--------|
| `md(filename)` | log | Markdown output path (defaults to the HTML stem with `.md`) |
| `html(filename)` | both | HTML report path (defaults to the log/dir stem with `.html`) |
| `replace` | both | Overwrite existing output |
| `css(filename)` | both | Custom stylesheet. **Omitted → bundled `tohtml.css` (GitHub-like layout)** |
| `mathjax` | both | Inject MathJax CDN for `$...$`, `$$...$$`, `\(...\)`, `\[...\]` formulas (needs internet to view) |
| `embed` | both | Single self-contained HTML: inlines CSS, images (Base64), and tables |
| `bundle` | both | Folder package: copies linked CSS/figures/tables into `css/`, `figures/`, `tables/` beside the HTML with relative links |
| `zip(filename \| .)` | both | Runs `bundle`, then ZIPs the package; `zip(.)` names the archive after the HTML |
| `clean` | log | Clean variant: keep headings, figures, tables, narrative blocks; drop all code and console output |
| `cleancode` | log | Code variant: keep headings, narrative, figures, tables, and the Stata commands from the log; drop console output (highlight.js for code) |
| `width(string)` | dir | Default width for all images/tables |
| `height(string)` | dir | Default height for all images/tables |
| `zoom(string)` | dir | Default zoom for all images |

**Three output variants (log-file form)**

- **Standard** (default): full session — code, output, headings, figures, tables.
- **`clean`**: presentation-ready — headings + figures + tables + narrative only.
- **`cleancode`**: teaching/reproducible — commands + figures + tables + narrative, no console output. Reads only the input log (no do-file argument needed).

`css()` and `clean`/`cleancode`/`mathjax` can be combined; the option controls structure/styling independently.

### outreg2e Command (for tables)

```stata
outreg2e [model1 model2] using "output.html", replace html
```

Must use `replace html` to generate HTML that `ishere tab` can embed. Store estimates with `estimates store name` first; use `[model*]` to include all stored models.

## Important Guidelines

### Log File Naming
- Never reuse the do-file name for the log (`analysis.do` + `analysis.log` locks in batch mode)
- Recommended: do-file `analysis.do`, log `analysis_run.log`

### Figure Handling
- Always `graph export` before `ishere fig using`
- PNG is the most reliable; SVG/WEBP/etc. also supported
- Size with `zoom()`, `height()`, `width()`

### Table Handling
- `outreg2e` must include `html`
- Store estimates before `outreg2e`; `[model*]` includes all stored models
- Embed with a separate `ishere tab using` line

### Styling
- Omit `css()` to get the bundled GitHub-like `tohtml.css`. To customize, pass `css(filename)` with a real file path. (`css(githubstyle)` is **no longer valid** — there is no built-in style named `githubstyle`.)

### Path Management
- `adopath ++ "."` loads bundled ado + `tohtml.css` from the working directory
- `cd` sets the working directory explicitly; forward slashes work on Windows

### Error Handling
- Start with `capture log close` to avoid log conflicts
- Close the log with `capture log close` before `tohtml`
- Check that Stata exits with code 0

## Example: Complete Agent Workflow

**User**: "Analyze auto data: regress price on mpg and weight, include a scatter plot, and give me a self-contained report."

**Agent prepares**:
1. Copy missing ado + `tohtml.css` to the working directory
2. Generate `analysis.do`:

```stata
* ============================================================
* Auto Data Analysis - Price vs MPG and Weight
* Generated by AI Agent
* ============================================================

adopath ++ "."
cd "C:\Users\kerry\Desktop\YourProject"
capture log close
log using "analysis_run.log", text replace

** # Automobile Price Analysis

** ## Data Overview
sysuse auto, clear
summarize price mpg weight

** ## Price vs MPG Scatter Plot
scatter price mpg
graph export "scatter_price_mpg.png", replace
ishere fig using "scatter_price_mpg.png", zoom(80%)

** ## Regression Analysis
regress price mpg weight
estimates store ols_model

** ## Model Summary
ishere display %5.3f e(r2)
/**
The OLS regression yields an R-squared of {ishere display %5.3f e(r2)}.
**/

outreg2e [ols_model] using "regression_table.html", replace html
ishere tab using "regression_table.html"

capture log close
* Single self-contained file (CSS + images inlined):
tohtml "analysis_run.log", html("report.html") embed replace
```

**Agent executes**:
```bash
python scripts/run_analysis.py analysis.do --stata-path "D:\Program\StataNow19\StataMP-64.exe"
```

**Agent delivers**: "Report generated: `report.html` (self-contained, open offline). Key finding: a one-unit increase in mpg is associated with a $[coef] change in price, controlling for weight."

### Variants quick reference
- Teaching/tutorial or "show me the code": `tohtml "analysis_run.log", html("r.html") cleancode replace`
- Minimal client report: `tohtml "analysis_run.log", html("r.html") clean replace`
- Portable package: `tohtml "analysis_run.log", html("r.html") zip(.) replace`
- Batch from folders: `tohtml "figures/" "tables/", html("r.html") width(700px) replace`

## Output Files

| File | Description |
|------|-------------|
| `*.log` | Stata execution log |
| `*.md` | Cleaned Markdown (intermediate, unless `md()` omits it) |
| `*.html` | Final HTML report |
| `*.png` / `*.svg` / ... | Exported figures |
| `*_table.html` / `*.md` | Exported tables |
| `css/`, `figures/`, `tables/` | Created by `bundle`/`zip` |
| `*.zip` | Portable archive from `zip()` |
