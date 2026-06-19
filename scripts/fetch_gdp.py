"""拉取并绘制中国季度 GDP 同比增速。"""

from pathlib import Path
import re

import akshare as ak
import pandas as pd
import plotly.graph_objects as go

from dashboard import render_dashboard


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

RAW_GDP_PATH = DATA_DIR / "gdp_raw.csv"
CLEAN_GDP_PATH = DATA_DIR / "gdp_quarterly_yoy.csv"
GDP_CHART_PATH = OUTPUT_DIR / "gdp_yoy.html"


def ensure_dirs() -> None:
    """确保输出目录存在。"""
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def fetch_gdp_raw() -> pd.DataFrame:
    """从 AKShare 拉取中国 GDP 数据。"""
    gdp_df = ak.macro_china_gdp()
    gdp_df.to_csv(RAW_GDP_PATH, index=False, encoding="utf-8-sig")
    return gdp_df


def find_column(columns: list[str], keywords: list[str]) -> str:
    """根据关键词匹配 AKShare 返回字段，降低接口字段名变化带来的影响。"""
    for column in columns:
        if all(keyword in column for keyword in keywords):
            return column
    raise ValueError(f"未找到包含关键词 {keywords} 的字段，当前字段：{columns}")


def parse_quarter_label(label: str) -> pd.Period:
    """把“2025年第1-3季度”解析为 2025Q3，便于按时间排序。"""
    match = re.search(r"(\d{4})年第1(?:-(\d))?季度", label)
    if not match:
        raise ValueError(f"无法解析 GDP 季度标签：{label}")

    year = int(match.group(1))
    quarter = int(match.group(2) or 1)
    return pd.Period(year=year, quarter=quarter, freq="Q")


def clean_gdp_yoy(raw_df: pd.DataFrame) -> pd.DataFrame:
    """清洗 GDP 季度同比增速。"""
    raw_df = raw_df.copy()
    columns = [str(column) for column in raw_df.columns]
    raw_df.columns = columns

    quarter_col = find_column(columns, ["季度"])
    yoy_col = find_column(columns, ["国内生产总值", "同比"])

    clean_df = raw_df[[quarter_col, yoy_col]].rename(
        columns={
            quarter_col: "quarter",
            yoy_col: "gdp_yoy",
        }
    )
    clean_df["quarter"] = clean_df["quarter"].astype(str)
    clean_df["gdp_yoy"] = pd.to_numeric(clean_df["gdp_yoy"], errors="coerce")
    clean_df["period"] = clean_df["quarter"].apply(parse_quarter_label)
    clean_df = clean_df.dropna(subset=["gdp_yoy"]).sort_values("period")
    clean_df["period"] = clean_df["period"].astype(str)
    clean_df.to_csv(CLEAN_GDP_PATH, index=False, encoding="utf-8-sig")
    return clean_df


def build_gdp_chart(clean_df: pd.DataFrame) -> go.Figure:
    """生成 GDP 同比增速趋势图。"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean_df["quarter"],
            y=clean_df["gdp_yoy"],
            mode="lines+markers",
            name="GDP 同比增速",
            line={"color": "#2563eb", "width": 3},
            marker={"size": 6},
            hovertemplate="季度：%{x}<br>同比增速：%{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="中国 GDP 同比增速（季度）",
        xaxis_title="季度",
        yaxis_title="同比增速（%）",
        template="plotly_white",
        hovermode="x unified",
        margin={"l": 60, "r": 30, "t": 70, "b": 80},
    )
    fig.write_html(GDP_CHART_PATH, include_plotlyjs="cdn", full_html=True)
    return fig


def main() -> None:
    """执行 GDP 数据获取、清洗、绘图和看板生成。"""
    ensure_dirs()
    raw_df = fetch_gdp_raw()
    clean_df = clean_gdp_yoy(raw_df)
    gdp_fig = build_gdp_chart(clean_df)
    render_dashboard([("GDP 同比增速（季度）", gdp_fig)])
    print("GDP 指标已生成：")
    print(f"- 原始数据：{RAW_GDP_PATH}")
    print(f"- 清洗数据：{CLEAN_GDP_PATH}")
    print(f"- 图表页面：{GDP_CHART_PATH}")
    print(f"- 看板页面：{OUTPUT_DIR / 'dashboard.html'}")


if __name__ == "__main__":
    main()
