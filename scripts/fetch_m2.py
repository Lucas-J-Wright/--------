"""拉取并绘制中国 M2 货币供应量同比增速。"""

from pathlib import Path
import re
from typing import Optional

import akshare as ak
import pandas as pd
import plotly.graph_objects as go

from dashboard import render_dashboard
from fetch_cpi import CLEAN_CPI_PATH, build_cpi_chart
from fetch_gdp import CLEAN_GDP_PATH, build_gdp_chart


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

RAW_M2_PATH = DATA_DIR / "m2_raw.csv"
CLEAN_M2_PATH = DATA_DIR / "m2_monthly_yoy.csv"
M2_CHART_PATH = OUTPUT_DIR / "m2_yoy.html"


def ensure_dirs() -> None:
    """确保输出目录存在。"""
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def fetch_m2_raw() -> pd.DataFrame:
    """从 AKShare 拉取中国货币供应量数据。"""
    m2_df = ak.macro_china_money_supply()
    m2_df.to_csv(RAW_M2_PATH, index=False, encoding="utf-8-sig")
    return m2_df


def parse_month_label(label: str) -> pd.Period:
    """把“2026年05月份”解析为 2026-05，便于按时间排序。"""
    match = re.search(r"(\d{4})年(\d{1,2})月份", label)
    if not match:
        raise ValueError(f"无法解析 M2 月份标签：{label}")

    year = int(match.group(1))
    month = int(match.group(2))
    return pd.Period(year=year, month=month, freq="M")


def clean_m2_yoy(raw_df: pd.DataFrame) -> pd.DataFrame:
    """清洗 M2 货币供应量月度同比增速。"""
    clean_df = raw_df[["月份", "货币和准货币(M2)-同比增长"]].rename(
        columns={
            "月份": "month",
            "货币和准货币(M2)-同比增长": "m2_yoy",
        }
    )
    clean_df["month"] = clean_df["month"].astype(str)
    clean_df["m2_yoy"] = pd.to_numeric(clean_df["m2_yoy"], errors="coerce")
    clean_df["period"] = clean_df["month"].apply(parse_month_label)
    clean_df = clean_df.dropna(subset=["m2_yoy"]).sort_values("period")
    clean_df["period"] = clean_df["period"].astype(str)
    clean_df.to_csv(CLEAN_M2_PATH, index=False, encoding="utf-8-sig")
    return clean_df


def build_m2_chart(clean_df: pd.DataFrame) -> go.Figure:
    """生成 M2 货币供应量同比增速趋势图。"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean_df["period"],
            y=clean_df["m2_yoy"],
            mode="lines+markers",
            name="M2 同比增速",
            line={"color": "#16a34a", "width": 3},
            marker={"size": 5},
            hovertemplate="月份：%{x}<br>同比增速：%{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="中国 M2 货币供应量同比增速（月度）",
        xaxis_title="月份",
        yaxis_title="同比增速（%）",
        template="plotly_white",
        hovermode="x unified",
        margin={"l": 60, "r": 30, "t": 70, "b": 80},
    )
    fig.write_html(M2_CHART_PATH, include_plotlyjs="cdn", full_html=True)
    return fig


def load_existing_gdp_chart() -> Optional[tuple[str, go.Figure]]:
    """如果 GDP 清洗数据已存在，则把 GDP 图表一起放入看板。"""
    if not CLEAN_GDP_PATH.exists():
        return None

    gdp_df = pd.read_csv(CLEAN_GDP_PATH)
    return ("GDP 同比增速（季度）", build_gdp_chart(gdp_df))


def load_existing_cpi_chart() -> Optional[tuple[str, go.Figure]]:
    """如果 CPI 清洗数据已存在，则把 CPI 图表一起放入看板。"""
    if not CLEAN_CPI_PATH.exists():
        return None

    cpi_df = pd.read_csv(CLEAN_CPI_PATH)
    return ("CPI 同比涨幅（月度）", build_cpi_chart(cpi_df))


def main() -> None:
    """执行 M2 数据获取、清洗、绘图和看板生成。"""
    ensure_dirs()
    raw_df = fetch_m2_raw()
    clean_df = clean_m2_yoy(raw_df)
    m2_fig = build_m2_chart(clean_df)

    charts = []
    for existing_chart in [load_existing_gdp_chart(), load_existing_cpi_chart()]:
        if existing_chart:
            charts.append(existing_chart)
    charts.append(("M2 货币供应量同比增速（月度）", m2_fig))
    render_dashboard(charts)

    print("M2 指标已生成：")
    print(f"- 原始数据：{RAW_M2_PATH}")
    print(f"- 清洗数据：{CLEAN_M2_PATH}")
    print(f"- 图表页面：{M2_CHART_PATH}")
    print(f"- 看板页面：{OUTPUT_DIR / 'dashboard.html'}")


if __name__ == "__main__":
    main()
