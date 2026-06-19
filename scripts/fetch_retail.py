"""拉取并绘制中国社会消费品零售总额同比增速。"""

from pathlib import Path
import re
from typing import Optional

import akshare as ak
import pandas as pd
import plotly.graph_objects as go

from dashboard import render_dashboard
from fetch_cpi import CLEAN_CPI_PATH, build_cpi_chart
from fetch_gdp import CLEAN_GDP_PATH, build_gdp_chart
from fetch_m2 import CLEAN_M2_PATH, build_m2_chart
from fetch_unemployment import CLEAN_UNEMPLOYMENT_PATH, build_unemployment_chart


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

RAW_RETAIL_PATH = DATA_DIR / "retail_sales_raw.csv"
CLEAN_RETAIL_PATH = DATA_DIR / "retail_sales_monthly_yoy.csv"
RETAIL_CHART_PATH = OUTPUT_DIR / "retail_sales_yoy.html"


def ensure_dirs() -> None:
    """确保输出目录存在。"""
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def fetch_retail_raw() -> pd.DataFrame:
    """从 AKShare 拉取社会消费品零售总额数据。"""
    retail_df = ak.macro_china_consumer_goods_retail()
    retail_df.to_csv(RAW_RETAIL_PATH, index=False, encoding="utf-8-sig")
    return retail_df


def parse_month_label(label: str) -> pd.Period:
    """把“2026年05月份”解析为 2026-05，便于按时间排序。"""
    match = re.search(r"(\d{4})年(\d{1,2})月份", label)
    if not match:
        raise ValueError(f"无法解析社零月份标签：{label}")

    year = int(match.group(1))
    month = int(match.group(2))
    return pd.Period(year=year, month=month, freq="M")


def clean_retail_yoy(raw_df: pd.DataFrame) -> pd.DataFrame:
    """清洗社会消费品零售总额月度同比增速。"""
    clean_df = raw_df[["月份", "同比增长"]].rename(
        columns={
            "月份": "month",
            "同比增长": "retail_sales_yoy",
        }
    )
    clean_df["month"] = clean_df["month"].astype(str)
    clean_df["retail_sales_yoy"] = pd.to_numeric(
        clean_df["retail_sales_yoy"], errors="coerce"
    )
    clean_df["period"] = clean_df["month"].apply(parse_month_label)
    clean_df = clean_df.dropna(subset=["retail_sales_yoy"]).sort_values("period")
    clean_df["period"] = clean_df["period"].astype(str)
    clean_df.to_csv(CLEAN_RETAIL_PATH, index=False, encoding="utf-8-sig")
    return clean_df


def build_retail_chart(clean_df: pd.DataFrame) -> go.Figure:
    """生成社会消费品零售总额同比增速趋势图。"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean_df["period"],
            y=clean_df["retail_sales_yoy"],
            mode="lines+markers",
            name="社零同比增速",
            line={"color": "#ea580c", "width": 3},
            marker={"size": 5},
            hovertemplate="月份：%{x}<br>同比增速：%{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="中国社会消费品零售总额同比增速（月度）",
        xaxis_title="月份",
        yaxis_title="同比增速（%）",
        template="plotly_white",
        hovermode="x unified",
        margin={"l": 60, "r": 30, "t": 70, "b": 80},
    )
    fig.write_html(RETAIL_CHART_PATH, include_plotlyjs="cdn", full_html=True)
    return fig


def load_existing_chart(path: Path, title: str, builder) -> Optional[tuple[str, go.Figure]]:
    """如果清洗数据已存在，则加载并返回对应图表。"""
    if not path.exists():
        return None

    return (title, builder(pd.read_csv(path)))


def main() -> None:
    """执行社零数据获取、清洗、绘图和看板生成。"""
    ensure_dirs()
    raw_df = fetch_retail_raw()
    clean_df = clean_retail_yoy(raw_df)
    retail_fig = build_retail_chart(clean_df)

    charts = []
    existing_charts = [
        load_existing_chart(CLEAN_GDP_PATH, "GDP 同比增速（季度）", build_gdp_chart),
        load_existing_chart(CLEAN_CPI_PATH, "CPI 同比涨幅（月度）", build_cpi_chart),
        load_existing_chart(CLEAN_M2_PATH, "M2 货币供应量同比增速（月度）", build_m2_chart),
        load_existing_chart(CLEAN_UNEMPLOYMENT_PATH, "城镇调查失业率（月度）", build_unemployment_chart),
    ]
    charts.extend(chart for chart in existing_charts if chart)
    charts.append(("社会消费品零售总额同比增速（月度）", retail_fig))
    render_dashboard(charts)

    print("社会消费品零售总额指标已生成：")
    print(f"- 原始数据：{RAW_RETAIL_PATH}")
    print(f"- 清洗数据：{CLEAN_RETAIL_PATH}")
    print(f"- 图表页面：{RETAIL_CHART_PATH}")
    print(f"- 看板页面：{OUTPUT_DIR / 'dashboard.html'}")


if __name__ == "__main__":
    main()
