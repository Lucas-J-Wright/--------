# 中国宏观经济数据看板

本项目用于拉取中国宏观经济公开数据，生成趋势图，并汇总为 HTML 看板页面。

## 当前进度

- [x] 仓库骨架
- [x] GDP 同比增速（季度）：数据获取、清洗、绘图、看板输出
- [x] CPI 同比涨幅（月度）：数据获取、清洗、绘图、看板输出
- [x] M2 货币供应量增速（月度）：数据获取、清洗、绘图、看板输出
- [x] 城镇调查失业率（月度）：数据获取、清洗、绘图、看板输出
- [x] 社会消费品零售总额增速（月度）：数据获取、清洗、绘图、看板输出

## 技术栈

- Python
- AKShare
- pandas
- Plotly
- Git / GitHub
- VS Code

## 仓库结构

```text
.
├── data/          # 原始数据与清洗后的 CSV
├── output/        # 图表与 HTML 看板
├── scripts/       # 数据获取、清洗、绘图脚本
├── .vscode/       # VS Code 项目配置
├── requirements.txt
└── README.md
```

## 数据来源

- GDP 数据：AKShare `macro_china_gdp` 接口，底层公开数据通常来自国家统计局等公开发布渠道。
- CPI 数据：AKShare `macro_china_cpi` 接口，使用全国 CPI 同比增长字段。
- M2 数据：AKShare `macro_china_money_supply` 接口，使用货币和准货币 M2 同比增长字段。
- 城镇调查失业率：优先使用 AKShare `macro_china_urban_unemployment` 接口；若国家统计局接口临时不可用，则使用公开网页表格作为备用源。
- 社会消费品零售总额：AKShare `macro_china_consumer_goods_retail` 接口，使用当月同比增长字段。

## 使用方法

建议先创建虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

一键拉取全部指标并生成看板：

```bash
python scripts/run_all.py
```

拉取 GDP 数据并生成图表：

```bash
python scripts/fetch_gdp.py
```

拉取 CPI 数据并更新看板：

```bash
python scripts/fetch_cpi.py
```

拉取 M2 数据并更新看板：

```bash
python scripts/fetch_m2.py
```

拉取城镇调查失业率数据并更新看板：

```bash
python scripts/fetch_unemployment.py
```

拉取社会消费品零售总额数据并更新看板：

```bash
python scripts/fetch_retail.py
```

根据已有清洗数据重建看板：

```bash
python scripts/build_dashboard.py
```

在浏览器中打开 `output/dashboard.html` 即可查看完整看板。

运行后会生成：

- `data/gdp_raw.csv`：AKShare 返回的 GDP 原始数据
- `data/gdp_quarterly_yoy.csv`：清洗后的季度 GDP 同比增速
- `output/gdp_yoy.html`：GDP 同比增速趋势图
- `data/cpi_raw.csv`：AKShare 返回的 CPI 原始数据
- `data/cpi_monthly_yoy.csv`：清洗后的月度 CPI 同比涨幅
- `output/cpi_yoy.html`：CPI 同比涨幅趋势图
- `data/m2_raw.csv`：AKShare 返回的货币供应量原始数据
- `data/m2_monthly_yoy.csv`：清洗后的月度 M2 同比增速
- `output/m2_yoy.html`：M2 同比增速趋势图
- `data/unemployment_raw.csv`：AKShare 返回的城镇调查失业率原始数据
- `data/urban_unemployment_monthly.csv`：清洗后的月度城镇调查失业率
- `output/urban_unemployment.html`：城镇调查失业率趋势图
- `data/retail_sales_raw.csv`：AKShare 返回的社会消费品零售总额原始数据
- `data/retail_sales_monthly_yoy.csv`：清洗后的月度社会消费品零售总额同比增速
- `output/retail_sales_yoy.html`：社会消费品零售总额同比增速趋势图
- `output/dashboard.html`：宏观经济 HTML 看板

## Git 提交流程

每完成一个阶段后，建议手动提交：

```bash
git status
git add .
git commit -m "完成宏观经济看板核心指标"
git push origin main
```
