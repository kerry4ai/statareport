---
name: stata-ai-report
description: Convert Stata analysis output (code, results, figures, tables) into an HTML report with ishere/tohtml. Trigger: stata report, stata html report, regression report, run stata to html, cleancode teaching report, embed single-file report.
---

# stata-ai-report

Use `ishere` to mark figures/tables/captions to include in the report, and `tohtml` to convert the log into HTML. Two commands, done.

## Simplest workflow

```stata
adopath ++ "."            // let Stata find the bundled ado + tohtml.css
cd "your working directory"
capture log close
log using "analysis_run.log", text replace
* ... your normal Stata analysis (plain code needs no ishere marker) ...
capture log close
tohtml "analysis_run.log", html("report.html") replace
```

Open `report.html`. (Omit `css()` to use the built-in `tohtml.css`, GitHub style.)

## Key: use ishere to insert figures and tables

Figures and tables that should appear in the report **must be inserted with `ishere`** — otherwise they won't be in the HTML.

**Figure** (export first, then `ishere fig`):

```stata
scatter price mpg
graph export "scatter.png", replace
ishere fig using "scatter.png"
ishere fig using "scatter.png", zoom(80)          // scalable
ishere figure using "scatter.png", height(400px) width(600px)
```

**Table** (`outreg2e` to HTML, then `ishere tab`):

```stata
qui regress price mpg weight
estimates store m1
outreg2e [m1] using "table.html", replace html      // html is required
ishere tab using "table.html"
ishere table using "table.html", height(500px) width(100%)
```

Also supports HTML/MD from `collect export` / `etable` / `dtable`; use `cssfile()` to bring along their bundled stylesheets.

## ishere ### adds captions for easy locate

Put `ishere ###` before each figure/table to add a caption. The HTML generates an anchored heading so you can locate it at a glance:

```stata
ishere ### "Fig 1: CO2 emission trend by province"
ishere fig using "figs/co2_trend.png"

ishere ### "Table 2: DEA efficiency estimates"
ishere tab using "results_dea.html"
```

## Quick reference

- **Narrative text**: use `/** ... **/` (not `ishere /* */`). Plain Stata code needs no marker — `tohtml` auto-fences it.
- **Dynamic values** (optional): `ishere display %5.3f e(r2)`, then reference it later inside `/** ... **/` with `{ishere display %5.3f e(r2)}`.
- **Headings**: `ishere # Title` / `ishere ## Section` (also `** # ...`).
- **tohtml common options**:
  - `embed`: inline CSS + images, single self-contained file, works offline.
  - `clean`: keep only headings/figures/tables/narrative, drop code & console.
  - `cleancode`: keep commands, drop console noise (no argument, reads the log).
  - `mathjax`: render `$...$` LaTeX (needs internet to view).
  - `zip(.)` / `bundle`: package resources into a portable folder/zip.
  - Directory form: `tohtml "figures/" "tables/", html("r.html") width(700px) replace`.
- **Log naming**: don't name the log the same as the do-file (do=`analysis.do` -> log=`analysis_run.log`) to avoid batch-file locking.
- **Run**: `stata /e do analysis.do` (Windows: `StataMP-64.exe /e do analysis.do`).

## Bundled commands (ado/)

`tohtml.ado` (v1.25), `ishere.ado` (v1.11), `tohtml.css` (default style), `outreg2e`, `sopen`, `logoute`. First use `install_deps.do` for SSC dependencies (pathutil / fs / moremata).
