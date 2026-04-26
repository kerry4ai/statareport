# Quick Start — 5 分钟上手

本指南带你从零开始，完成一次完整的 Stata 数据分析并生成 HTML 报告。

## 前置检查

确认 Stata 已安装且版本 >= 17：

```stata
display version
```

## Step 1: 安装依赖（只需一次）

在 Stata 命令窗口运行：

```stata
do "~/.workbuddy/skills/stata-ai-report/install_deps.do"
```

看到 `All dependencies verified.` 即表示成功。

## Step 2: 创建分析目录

新建一个文件夹作为工作目录，例如 `~/stata-report-demo/`。

将 Skill 自带的 ado 文件复制进去（让 Stata 能找到这些命令）：

**Windows:**
```powershell
Copy-Item "~\.workbuddy\skills\stata-ai-report\ado\*" -Destination "~/stata-report-demo/"
```

**macOS / Linux:**
```bash
cp ~/.workbuddy/skills/stata-ai-report/ado/*.ado ~/stata-report-demo/
```

然后在 Stata 中切换到该目录：

```stata
cd "~/stata-report-demo"
```

## Step 3: 编写 do-file

新建文件 `analysis.do`，写入以下内容：

```stata
capture log close
log using "analysis_run.log", replace text

* ============================================================
*  1. 数据加载与描述
* ============================================================
ishere # Data Overview

sysuse auto, clear
disp "Dataset: auto.dta | Obs: `c(N)' | Vars: `c(k)'"

tabstat price mpg weight, stat(mean sd min max) col(stat)

* ============================================================
*  2. 图表
* ============================================================
ishere # Figures

histogram price, normal title("Price Distribution") color(%50)
graph export "fig_price.png", replace width(1200)
ishere fig using "fig_price.png"

twoway (scatter price mpg) (lfit price mpg), ///
    title("Price vs MPG") legend(order(1 "Observed" 2 "Fitted"))
graph export "fig_scatter.png", replace width(1200)
ishere fig using "fig_scatter.png"

* ============================================================
*  3. 回归分析
* ============================================================
ishere # Regression Analysis

qui regress price mpg weight
estimates store m1

qui regress price mpg weight i.foreign, robust
estimates store m2

outreg2e [m1 m2] using "reg_table.html", replace html dec(3)
ishere tab using "reg_table.html"

* ============================================================
*  收尾
* ============================================================
capture log close
tohtml "analysis_run.log", html("report.html") css(githubstyle) replace
```

## Step 4: 执行

**方式 A — 直接调用 Stata：**

```bash
# Windows
"C:\Program Files\Stata19\StataMP-64.exe" /e do "analysis.do"

# macOS
/Applications/Stata/StataMP.app/Contents/MacOS/StataMP -e do "analysis.do"

# Linux
/usr/local/stata18/stata-mp -e do "analysis.do"
```

**方式 B — 使用跨平台脚本：**

```bash
python ~/.workbuddy/skills/stata-ai-report/scripts/run_analysis.py analysis.do
```

## Step 5: 查看报告

执行完成后，工作目录下会生成：

| 文件 | 说明 |
|------|------|
| `report.html` | **最终 HTML 报告**（含图表、回归表） |
| `analysis_run.log` | Stata 原始 log |
| `fig_price.png` | 价格分布直方图 |
| `fig_scatter.png` | 价格-油耗散点图 |
| `reg_table.html` | 回归表格（被嵌入 report.html） |
| `css/` | `githubstyle` 样式文件 |

用浏览器打开 `report.html` 即可查看完整报告。

## 进阶：代码+结果混合模式

如果你想在报告中同时展示原始代码和结果（适合教学或复现），将最后一句 `tohtml` 改为：

```stata
tohtml "analysis_run.log", html("report.html") css(githubstyle) cleancode("analysis.do") replace
```

这会生成一份代码与结果交织的报告，原始 do-file 中的注释和命令都会保留在 HTML 中。

## 完整演示文件

Skill 自带的 `demo4ai_agents.do` 是一个更完整的示例，包含动态文本插入（`ishere display %fmt val`）和多模型回归比较。可直接运行查看效果。
