"""生成宏观经济 HTML 看板。"""

from pathlib import Path

import plotly.graph_objects as go


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "output"
DASHBOARD_PATH = OUTPUT_DIR / "dashboard.html"


def render_dashboard(charts: list[tuple[str, go.Figure]]) -> None:
    """把多个 Plotly 图表汇总为一个 HTML 看板。"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    chart_sections = "\n".join(
        f"""    <section>
      <h2>{title}</h2>
      {fig.to_html(include_plotlyjs="cdn" if index == 0 else False, full_html=False)}
    </section>"""
        for index, (title, fig) in enumerate(charts)
    )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>中国宏观经济数据看板</title>
  <style>
    body {{
      margin: 0;
      color: #1f2937;
      background: #f7f8fb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 40px 18px;
      background: #ffffff;
      border-bottom: 1px solid #e5e7eb;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 24px 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      font-weight: 700;
    }}
    h2 {{
      margin: 0 0 16px;
      font-size: 18px;
      font-weight: 650;
    }}
    p {{
      margin: 0;
      color: #6b7280;
      line-height: 1.6;
    }}
    section {{
      margin-top: 24px;
      padding: 24px;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>中国宏观经济数据看板</h1>
    <p>集中展示 GDP、CPI 等中国宏观经济指标的趋势变化。</p>
  </header>
  <main>
{chart_sections}
  </main>
</body>
</html>
"""
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
