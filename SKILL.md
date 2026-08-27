---
name: stata-ai-report
description: 用 ishere/tohtml 把 Stata 分析结果（代码、结果、图、表）转成 HTML 报告。触发：stata 出报告、stata html report、回归报告、跑stata生成html、cleancode 教学报告、embed 单文件报告。
---

# stata-ai-report

用 `ishere` 在 do-file 里标记要进报告的图/表/标题，用 `tohtml` 把 log 转成 HTML。两条命令搞定。

## 最简工作流

```stata
adopath ++ "."            // 让 Stata 找到捆绑的 ado + tohtml.css
cd "你的工作目录"
capture log close
log using "analysis_run.log", text replace
* ... 你的正常 Stata 分析（普通代码不用 ishere 标记）...
capture log close
tohtml "analysis_run.log", html("report.html") replace
```
打开 `report.html` 即可。（省略 `css()` 就用内置 `tohtml.css`，GitHub 风格。）

## 重点：用 ishere 插入图与表

报告里要出现的**图、表必须用 `ishere` 插入**，否则不会进 HTML。

**图**（先 `graph export`，再 `ishere fig`）：
```stata
scatter price mpg
graph export "scatter.png", replace
ishere fig using "scatter.png"
ishere fig using "scatter.png", zoom(80)          // 可缩放
ishere figure using "scatter.png", height(400px) width(600px)
```

**表**（`outreg2e` 导出 HTML，再 `ishere tab` 插入）：
```stata
qui regress price mpg weight
estimates store m1
outreg2e [m1] using "table.html", replace html      // 必须带 html
ishere tab using "table.html"
ishere table using "table.html", height(500px) width(100%)
```
也支持 `collect export` / `etable` / `dtable` 出的 HTML 或 MD，用 `cssfile()` 带上配套样式。

## ishere ### 给图/表加标题，便于 locate

每个图、表前面用 `ishere ###` 加一句标题/题注，HTML 里会生成带锚点的小标题，一眼可定位：
```stata
ishere ### "图1：各省份碳排放趋势"
ishere fig using "figs/co2_trend.png"

ishere ### "表2：DEA 效率估计结果"
ishere tab using "results_dea.html"
```

## 其它速查

- **叙述文字**：用 `/** ... **/`（不是 `ishere /* */`）。普通 Stata 代码不用标记，`tohtml` 自动加围栏。
- **动态数值**（可选）：`ishere display %5.3f e(r2)`，在后面的 `/** ... **/` 里用 `{ishere display %5.3f e(r2)}` 引用。
- **标题层级**：`ishere # 主标题` / `ishere ## 小节`（也支持 `** # ...`）。
- **tohtml 常用选项**：
  - `embed`：CSS + 图片内联，单文件自包含，可离线打开。
  - `clean`：只要标题/图/表/叙述，去掉代码与控制台。
  - `cleancode`：保留命令、去掉控制台噪声（无参数，只读 log）。
  - `mathjax`：渲染 `$...$` LaTeX 公式（需联网查看）。
  - `zip(.)` / `bundle`：打包资源成可移植文件夹/压缩包。
  - 目录模式：`tohtml "figures/" "tables/", html("r.html") width(700px) replace`。
- **日志命名**：log 文件名不要和 do 文件同名（如 do=`analysis.do` → log=`analysis_run.log`），避免批处理锁文件。
- **执行**：`stata /e do analysis.do`（Windows：`StataMP-64.exe /e do analysis.do`）。

## 捆绑命令（ado/）

`tohtml.ado`(v1.25)、`ishere.ado`(v1.11)、`tohtml.css`（默认样式）、`outreg2e`、`sopen`、`logoute`。首次用 `install_deps.do` 装 SSC 依赖（pathutil / fs / moremata）。
