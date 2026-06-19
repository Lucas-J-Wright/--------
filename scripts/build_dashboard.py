"""根据已存在的清洗数据重建完整 HTML 看板。"""

import pandas as pd

from dashboard import render_dashboard
from fetch_cpi import CLEAN_CPI_PATH, build_cpi_chart
from fetch_gdp import CLEAN_GDP_PATH, build_gdp_chart
from fetch_m2 import CLEAN_M2_PATH, build_m2_chart
from fetch_retail import CLEAN_RETAIL_PATH, build_retail_chart
from fetch_unemployment import CLEAN_UNEMPLOYMENT_PATH, build_unemployment_chart


def main() -> None:
    """加载已有清洗数据并生成看板。"""
    charts = []
    chart_configs = [
        (CLEAN_GDP_PATH, "GDP 同比增速（季度）", build_gdp_chart),
        (CLEAN_CPI_PATH, "CPI 同比涨幅（月度）", build_cpi_chart),
        (CLEAN_M2_PATH, "M2 货币供应量同比增速（月度）", build_m2_chart),
        (CLEAN_UNEMPLOYMENT_PATH, "城镇调查失业率（月度）", build_unemployment_chart),
        (CLEAN_RETAIL_PATH, "社会消费品零售总额同比增速（月度）", build_retail_chart),
    ]

    for path, title, builder in chart_configs:
        if path.exists():
            charts.append((title, builder(pd.read_csv(path))))

    if not charts:
        raise FileNotFoundError("未找到任何清洗后的指标数据，请先运行指标抓取脚本。")

    render_dashboard(charts)
    print("看板已重建：output/dashboard.html")


if __name__ == "__main__":
    main()
