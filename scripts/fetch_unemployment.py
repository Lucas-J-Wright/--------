"""拉取并绘制中国城镇调查失业率。"""

from pathlib import Path
from io import StringIO
from typing import Optional

import akshare as ak
import pandas as pd
import plotly.graph_objects as go
import requests

from dashboard import render_dashboard
from fetch_cpi import CLEAN_CPI_PATH, build_cpi_chart
from fetch_gdp import CLEAN_GDP_PATH, build_gdp_chart
from fetch_m2 import CLEAN_M2_PATH, build_m2_chart


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

RAW_UNEMPLOYMENT_PATH = DATA_DIR / "unemployment_raw.csv"
CLEAN_UNEMPLOYMENT_PATH = DATA_DIR / "urban_unemployment_monthly.csv"
UNEMPLOYMENT_CHART_PATH = OUTPUT_DIR / "urban_unemployment.html"


def ensure_dirs() -> None:
    """确保输出目录存在。"""
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def fetch_unemployment_raw() -> pd.DataFrame:
    """从 AKShare 拉取国家统计局城镇调查失业率数据。"""
    try:
        unemployment_df = ak.macro_china_urban_unemployment()
    except Exception as exc:
        print(f"AKShare 国家统计局接口暂不可用，改用公开网页备用数据源：{exc}")
        unemployment_df = fetch_unemployment_fallback()

    unemployment_df.to_csv(RAW_UNEMPLOYMENT_PATH, index=False, encoding="utf-8-sig")
    return unemployment_df


def fetch_unemployment_fallback() -> pd.DataFrame:
    """从公开网页表格抓取近年城镇调查失业率，作为接口不可用时的备用源。"""
    url = "https://zh.wikipedia.org/wiki/中国大陆失业率"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))
    year_table_map = {
        2022: tables[6],
        2023: tables[7],
        2024: tables[8],
    }

    rows = []
    for year, table in year_table_map.items():
        rate_col = "城镇调查失业率"
        if rate_col not in table.columns:
            rate_col = "全国城镇调查失业率"

        for _, row in table.iterrows():
            month_text = str(row["月份"]).replace(" ", "")
            month = int(month_text.replace("月", ""))
            rate = str(row[rate_col]).replace("%", "")
            rows.append(
                {
                    "date": f"{year}{month:02d}",
                    "item": "城镇调查失业率",
                    "value": rate,
                    "source": "Wikipedia fallback, 原始引用来自国家统计局月度发布",
                }
            )

    return pd.DataFrame(rows)


def clean_unemployment(raw_df: pd.DataFrame) -> pd.DataFrame:
    """清洗城镇调查失业率月度数据。"""
    clean_df = raw_df[["date", "value"]].rename(
        columns={
            "date": "month",
            "value": "urban_unemployment_rate",
        }
    )
    clean_df["period"] = pd.to_datetime(clean_df["month"], format="%Y%m").dt.to_period("M")
    clean_df["urban_unemployment_rate"] = pd.to_numeric(
        clean_df["urban_unemployment_rate"], errors="coerce"
    )
    clean_df = clean_df.dropna(subset=["urban_unemployment_rate"]).sort_values("period")
    clean_df["period"] = clean_df["period"].astype(str)
    clean_df.to_csv(CLEAN_UNEMPLOYMENT_PATH, index=False, encoding="utf-8-sig")
    return clean_df


def build_unemployment_chart(clean_df: pd.DataFrame) -> go.Figure:
    """生成城镇调查失业率趋势图。"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean_df["period"],
            y=clean_df["urban_unemployment_rate"],
            mode="lines+markers",
            name="城镇调查失业率",
            line={"color": "#7c3aed", "width": 3},
            marker={"size": 5},
            hovertemplate="月份：%{x}<br>失业率：%{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="中国城镇调查失业率（月度）",
        xaxis_title="月份",
        yaxis_title="失业率（%）",
        template="plotly_white",
        hovermode="x unified",
        margin={"l": 60, "r": 30, "t": 70, "b": 80},
    )
    fig.write_html(UNEMPLOYMENT_CHART_PATH, include_plotlyjs="cdn", full_html=True)
    return fig


def load_existing_chart(path: Path, title: str, builder) -> Optional[tuple[str, go.Figure]]:
    """如果清洗数据已存在，则加载并返回对应图表。"""
    if not path.exists():
        return None

    return (title, builder(pd.read_csv(path)))


def main() -> None:
    """执行失业率数据获取、清洗、绘图和看板生成。"""
    ensure_dirs()
    raw_df = fetch_unemployment_raw()
    clean_df = clean_unemployment(raw_df)
    unemployment_fig = build_unemployment_chart(clean_df)

    charts = []
    existing_charts = [
        load_existing_chart(CLEAN_GDP_PATH, "GDP 同比增速（季度）", build_gdp_chart),
        load_existing_chart(CLEAN_CPI_PATH, "CPI 同比涨幅（月度）", build_cpi_chart),
        load_existing_chart(CLEAN_M2_PATH, "M2 货币供应量同比增速（月度）", build_m2_chart),
    ]
    charts.extend(chart for chart in existing_charts if chart)
    charts.append(("城镇调查失业率（月度）", unemployment_fig))
    render_dashboard(charts)

    print("城镇调查失业率指标已生成：")
    print(f"- 原始数据：{RAW_UNEMPLOYMENT_PATH}")
    print(f"- 清洗数据：{CLEAN_UNEMPLOYMENT_PATH}")
    print(f"- 图表页面：{UNEMPLOYMENT_CHART_PATH}")
    print(f"- 看板页面：{OUTPUT_DIR / 'dashboard.html'}")


if __name__ == "__main__":
    main()
