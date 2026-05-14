from openai import OpenAI
from dotenv import load_dotenv
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import subprocess
import sys

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Directory to save generated charts
CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

GRAPH_CONTEXT = """
You are a senior data visualization engineer for SmartViz — an enterprise smart building
analytics platform used by facility managers, sustainability officers, and building directors.

Your job: Given query results and the user question, select the most impactful
industry-standard chart and write clean, professional Python matplotlib/seaborn code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHART SELECTION RULES — pick the FIRST matching rule:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TEXT_ONLY
   → 1 row + 1-2 columns (single value answer)

2. HEATMAP
   → 3 columns: one room/category + one time (hour/day/week/date) + one numeric
   → Keywords: "by hour", "by day", "by week", "by room and", "heatmap"
   → Use seaborn heatmap with pivot table
   → rooms on Y axis, time on X axis
   → Colormap: 'YlOrRd' for CO2/temp/risk, 'YlGn' for occupancy/utilisation
   → figsize=(16, 9)

3. DUAL-AXIS LINE CHART
   → 2 numeric metrics with different units over time (e.g. temp + occupancy over hours)
   → Use twinx() for second Y axis
   → Different colors for each metric, clear legend
   → figsize=(14, 6)

4. SCATTER PLOT with trend line
   → 2 continuous numeric columns (correlation analysis)
   → Keywords: "correlation", "relationship", "vs", "against"
   → Add numpy polyfit trend line + R2 annotation
   → figsize=(10, 7)

5. LINE CHART
   → Time series: timestamp/date/hour + numeric value(s)
   → Keywords: "trend", "over time", "by hour", "daily", "weekly", "pattern"
   → Add data point markers, grid lines
   → figsize=(14, 6)

6. GROUPED BAR CHART
   → Multiple numeric columns per category (side by side comparison)
   → Keywords: "compare", "vs", "versus", "working hours vs", "weekday vs"
   → figsize=(12, 7)

7. HORIZONTAL BAR CHART with threshold line
   → Single metric per room/category, many rows (>5 rooms)
   → Keywords: "top", "highest", "lowest", "worst", "best", "ranking", "rooms above/below"
   → Sort by value DESC, add threshold line if question mentions a limit
   → Add value labels on bars
   → figsize=(12, max(6, len(data)*0.4))

8. STACKED BAR CHART
   → Proportional breakdown across categories
   → Keywords: "breakdown", "proportion", "share", "distribution across"
   → figsize=(12, 7)

9. PIE / DONUT CHART
   → Proportional shares, <= 8 categories
   → Keywords: "pie", "donut", "proportion", "percentage of", "share of"
   → Use donut style (wedgeprops=dict(width=0.5)) for modern look
   → figsize=(10, 8)

10. HISTOGRAM
    → Distribution of a single numeric metric
    → Keywords: "distribution", "frequency", "how often", "spread"
    → figsize=(10, 6)

11. HORIZONTAL BAR CHART (default for categorical + numeric)
    → Any other categorical + numeric data
    → figsize=(12, 6)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFESSIONAL STYLING RULES (always apply):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COLOR PALETTES:
  Primary:   ['#2D6A4F', '#E76F51', '#264653', '#E9C46A', '#F4A261', '#A8DADC', '#457B9D', '#E63946']
  CO2/Risk:  Use red gradient
  Good/Safe: Use green gradient
  Sequential: Use 'YlOrRd' or 'RdYlGn_r' colormaps

CHART QUALITY:
  - figsize: always set explicitly per chart type above
  - DPI: 150 (already in savefig call)
  - Font sizes: title=14 bold, axis labels=11, tick labels=9, annotations=8
  - Always add grid lines with alpha=0.3
  - Add value labels on ALL bar charts
  - Add threshold lines where relevant
  - Remove top and right spines: ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
  - Always plt.tight_layout() before savefig
  - Title: descriptive, fontsize=14, fontweight='bold', pad=15

THRESHOLD ANNOTATIONS (add automatically when relevant):
  - CO2 > 800 ppm  → red dashed line labelled "Safe limit (800 ppm)"
  - CO2 > 1000 ppm → orange dashed line labelled "Poor air quality (1000 ppm)"
  - Temperature > 25 degrees C → orange dashed line labelled "Comfort limit (25 C)"
  - Battery < 20%  → red dashed line labelled "Low battery (20%)"

HEATMAP SPECIFICS:
  - import seaborn as sns
  - df = pd.DataFrame(data)
  - pivot the dataframe using room column as index, time column as columns, value column as values
  - fig, ax = plt.subplots(figsize=(22, 10))
  - sns.heatmap(pivot, annot=False, cmap='YlOrRd', ax=ax, linewidths=0.3,
                cbar_kws={'label': 'value', 'shrink': 0.8})
  - ax.set_xticklabels(ax.get_xticklabels(), fontsize=9, rotation=0)
  - ax.set_yticklabels(ax.get_yticklabels(), fontsize=9, rotation=0)
  - ax.set_xlabel('Hour of Day', fontsize=11)
  - ax.set_ylabel('Room Name', fontsize=11)
  - NEVER use annot=True for heatmaps — colour alone communicates the pattern
  - plt.tight_layout()

SCATTER PLOT SPECIFICS:
  - import numpy as np
  - Add trend line using np.polyfit
  - Annotate with R-squared value

DUAL AXIS SPECIFICS:
  - fig, ax1 = plt.subplots(figsize=(14,6))
  - ax2 = ax1.twinx()
  - Use different colors for each axis
  - Label each Y axis clearly with metric and unit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODE RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - `data` (list of dicts) and `CHART_PATH` (string) are PRE-DEFINED — never redefine them
  - matplotlib, plt, pd, sns, np are already imported — do not re-import them
  - Do NOT use plt.style.use() or matplotlib.style.use()
  - Save with: plt.savefig(CHART_PATH, dpi=150, bbox_inches='tight')
  - Do NOT call plt.show()
  - Return ONLY raw Python code — no explanation, no markdown, no backticks
"""


def detect_chart_hint(col_names: list, data: list, user_question: str) -> str:
    """Detect data shape and inject chart type hint into the prompt."""
    hints = []
    col_lower  = [c.lower() for c in col_names]
    q_lower    = user_question.lower()

    time_cols  = {"hour", "hour_of_day", "day", "day_of_week", "date", "week", "month", "period"}
    room_cols  = {"room_name", "room", "display_name", "space"}
    corr_words = {"correlation", "relationship", "vs", "versus", "against"}
    pie_words  = {"pie", "donut", "proportion", "percentage", "share"}
    trend_words= {"trend", "over time", "daily", "weekly", "by day", "by week"}
    dual_words = {"compare", "both", "and", "vs"}

    has_time    = any(any(t in c for t in time_cols) for c in col_lower)
    has_room    = any(any(r in c for r in room_cols) for c in col_lower)
    num_numeric = sum(
        1 for col in col_names
        if data and isinstance(data[0].get(col), (int, float))
    )

    # Heatmap
    if has_time and has_room and len(col_names) == 3:
        time_col = next((c for c in col_names if any(t in c.lower() for t in time_cols)), "")
        room_col = next((c for c in col_names if any(r in c.lower() for r in room_cols)), "")
        val_col  = next((c for c in col_names if c not in [time_col, room_col]), "")
        hints.append(
            f"HEATMAP REQUIRED: pivot index='{room_col}', columns='{time_col}', values='{val_col}'"
        )

    # Scatter
    elif any(w in q_lower for w in corr_words) and num_numeric >= 2:
        hints.append("SCATTER PLOT with trend line required — correlation analysis.")

    # Pie/donut
    elif any(w in q_lower for w in pie_words):
        hints.append("PIE/DONUT CHART required — proportion question.")

    # Dual axis
    elif num_numeric >= 2 and has_time and any(w in q_lower for w in dual_words):
        hints.append("DUAL-AXIS LINE CHART required — two metrics over time.")

    # Line chart
    elif has_time and not has_room and num_numeric == 1:
        hints.append("LINE CHART required — time series data.")

    # Threshold bar
    elif any(w in q_lower for w in ["above", "below", "exceed", "threshold", "limit"]):
        hints.append("HORIZONTAL BAR CHART with threshold line required.")

    return "\n".join(hints)


def generate_chart(col_names: list, results: list, user_question: str, sql: str = "") -> str:
    """
    Agent 5 — Graph Builder
    Generates a professional industry-level chart from query results.
    Returns path to saved chart image or 'TEXT_ONLY'.
    """

    # Convert Decimal to float
    data = []
    for row in results:
        clean_row = {}
        for col, val in zip(col_names, row):
            if isinstance(val, Decimal):
                clean_row[col] = float(round(val, 2))
            else:
                clean_row[col] = val
        data.append(clean_row)

    # Single value — no chart
    if len(results) <= 1 and len(col_names) <= 2:
        print("\n📊 AGENT 5: Single result — text answer sufficient")
        return "TEXT_ONLY"

    # Data summary
    data_summary = f"Columns: {col_names}\nRows: {len(data)}\nFirst 5 rows:\n"
    for row in data[:5]:
        data_summary += f"  {row}\n"
    if len(data) > 5:
        data_summary += f"  ... and {len(data) - 5} more rows\n"

    # Chart hint
    chart_hint = detect_chart_hint(col_names, data, user_question)

    # Filename
    safe_q     = re.sub(r'[^a-zA-Z0-9]', '_', user_question[:40]).strip('_')
    chart_path = os.path.join(CHARTS_DIR, f"{safe_q}.png")

    # Prompt
    prompt = f"""User question: {user_question}

SQL used: {sql}

Data:
{data_summary}
{chart_hint}

Write professional Python code to visualize this data.
`data` and `CHART_PATH` are already defined — use them directly.
Return ONLY raw Python code."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": GRAPH_CONTEXT},
            {"role": "user",   "content": prompt}
        ]
    )

    code = response.choices[0].message.content.strip()

    if code.strip() == "TEXT_ONLY":
        print("\n📊 AGENT 5: LLM decided text answer sufficient")
        return "TEXT_ONLY"

    # Strip markdown fences
    if code.startswith("```"):
        code = code.split("\n", 1)[-1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    code = code.strip()

    # Full executable script
    full_script = f"""import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.style
matplotlib.style.use = lambda *a, **k: None
plt.style.use = lambda *a, **k: None
import pandas as pd
import seaborn as sns
import numpy as np

data = {repr(data)}
CHART_PATH = {repr(chart_path)}

{code}
"""

    print(f"\n📊 AGENT 5 — Generating chart")
    print(f"   Hint applied: {chart_hint[:80] if chart_hint else 'auto-detected'}")
    print(f"   Saving to: {chart_path}")

    try:
        temp_script = os.path.join(CHARTS_DIR, "_temp_chart.py")
        with open(temp_script, 'w') as f:
            f.write(full_script)

        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            print(f"\n⚠️  AGENT 5: First attempt failed — auto-fixing...")
            print(f"   Error: {result.stderr[:300]}")
            fixed = fix_chart_code(full_script, result.stderr)
            if fixed:
                with open(temp_script, 'w') as f:
                    f.write(fixed)
                result2 = subprocess.run(
                    [sys.executable, temp_script],
                    capture_output=True, text=True, timeout=30
                )
                if result2.returncode == 0 and os.path.exists(chart_path):
                    print(f"\n✅ AGENT 5: Chart fixed and saved")
                    cleanup_temp(temp_script)
                    return chart_path
            print(f"\n❌ AGENT 5: Could not generate chart")
            cleanup_temp(temp_script)
            return "TEXT_ONLY"

        if os.path.exists(chart_path):
            print(f"\n✅ AGENT 5: Chart saved to {chart_path}")
            cleanup_temp(temp_script)
            return chart_path
        else:
            print(f"\n❌ AGENT 5: Code ran but no chart file created")
            cleanup_temp(temp_script)
            return "TEXT_ONLY"

    except subprocess.TimeoutExpired:
        print(f"\n❌ AGENT 5: Timed out")
        cleanup_temp(temp_script)
        return "TEXT_ONLY"
    except Exception as e:
        print(f"\n❌ AGENT 5: Error: {e}")
        cleanup_temp(temp_script)
        return "TEXT_ONLY"


def fix_chart_code(failed_code: str, error: str) -> str:
    """Ask GPT-4 to fix failed chart code."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Python matplotlib/seaborn expert. Fix the code and return only the complete corrected Python script, no markdown, no explanation."},
            {"role": "user",   "content": f"Fix this code:\n\n{failed_code}\n\nError:\n{error[:500]}"}
        ]
    )
    code = response.choices[0].message.content.strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[-1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    print(f"   🔧 Auto-fix applied")
    return code.strip()


def cleanup_temp(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except:
        pass


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing heatmap...")
    cols = ["room_name", "hour_of_day", "avg_co2"]
    rows = [
        ("PES Seminar Room 3", 9,  Decimal('580.5')),
        ("PES Seminar Room 3", 12, Decimal('670.3')),
        ("PES Seminar Room 3", 15, Decimal('720.1')),
        ("PES Dining Room",    9,  Decimal('450.2')),
        ("PES Dining Room",    12, Decimal('510.6')),
        ("PES Dining Room",    15, Decimal('490.9')),
    ]
    path = generate_chart(cols, rows, "Show me average CO2 for each room by hour of day")
    print(f"Result: {path}")