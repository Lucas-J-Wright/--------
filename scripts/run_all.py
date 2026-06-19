"""一键更新全部宏观经济指标并生成 HTML 看板。"""

from build_dashboard import main as build_dashboard
from fetch_cpi import main as fetch_cpi
from fetch_gdp import main as fetch_gdp
from fetch_m2 import main as fetch_m2
from fetch_retail import main as fetch_retail
from fetch_unemployment import main as fetch_unemployment


def main() -> None:
    """按顺序更新全部指标。"""
    tasks = [
        ("GDP 同比增速（季度）", fetch_gdp),
        ("CPI 同比涨幅（月度）", fetch_cpi),
        ("M2 货币供应量同比增速（月度）", fetch_m2),
        ("城镇调查失业率（月度）", fetch_unemployment),
        ("社会消费品零售总额同比增速（月度）", fetch_retail),
    ]

    for title, task in tasks:
        print(f"\n开始更新：{title}")
        task()

    print("\n统一重建看板")
    build_dashboard()
    print("\n全部指标已更新完成。")


if __name__ == "__main__":
    main()
