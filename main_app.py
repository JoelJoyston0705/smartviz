import streamlit as st
import sys
import os
import time
import json
import decimal
from pathlib import Path
import plotly.graph_objects as go
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.agent1_planner import plan_query
from agents.agent2_rag import retrieve_schema
from agents.agent3_sql import generate_sql
from agents.agent4_validator import validate_and_execute
from agents.agent5_graph import generate_chart


# ── DB connection ─────────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


# ── JSON serialiser ───────────────────────────────────────────────────────────
def json_serial(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)


# ── Session persistence ───────────────────────────────────────────────────────
def init_session_table():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id          SERIAL PRIMARY KEY,
                timestamp   TIMESTAMPTZ DEFAULT NOW(),
                question    TEXT,
                plan        TEXT,
                sql         TEXT,
                final_sql   TEXT,
                cols        JSONB,
                results     JSONB,
                chart_path  TEXT,
                model       TEXT,
                latency     FLOAT,
                attempts    INT,
                error       TEXT
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("[init_session_table OK] chat_sessions ready")
    except Exception as e:
        print(f"[init_session_table ERROR] {e}")


def save_entry(entry: dict):
    try:
        conn = get_conn()
        cur = conn.cursor()
        raw_results  = entry.get("results") or []
        safe_results = [list(r) for r in raw_results]
        safe_cols    = list(entry.get("cols") or [])
        cur.execute("""
            INSERT INTO chat_sessions
                (question, plan, sql, final_sql, cols, results,
                 chart_path, model, latency, attempts, error)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s)
        """, (
            entry.get("question"),
            entry.get("plan"),
            entry.get("sql"),
            entry.get("final_sql"),
            json.dumps(safe_cols,    default=json_serial),
            json.dumps(safe_results, default=json_serial),
            entry.get("chart_path"),
            entry.get("model"),
            entry.get("latency"),
            entry.get("attempts"),
            entry.get("error"),
        ))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[save_entry OK] saved: {entry.get('question')}")
    except Exception as e:
        print(f"[save_entry ERROR] {e}")


def load_recent_entries(limit: int = 10) -> list:
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT question, plan, sql, final_sql, cols, results,
                   chart_path, model, latency, attempts, error
            FROM chat_sessions
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        entries = []
        for row in reversed(rows):
            (question, plan, sql, final_sql, cols, results,
             chart_path, model, latency, attempts, error) = row
            cols_parsed    = cols    if isinstance(cols, list)    else (json.loads(cols)    if cols    else [])
            results_parsed = results if isinstance(results, list) else (json.loads(results) if results else [])
            results_parsed = [tuple(r) for r in results_parsed] if results_parsed else []
            entries.append({
                "question":   question or "",
                "plan":       plan or "",
                "sql":        sql or "",
                "final_sql":  final_sql or "",
                "cols":       cols_parsed,
                "results":    results_parsed,
                "chart_path": chart_path,
                "model":      model or "gpt4",
                "latency":    latency or 0.0,
                "attempts":   attempts or 1,
                "error":      error,
            })
        print(f"[load_recent_entries OK] loaded {len(entries)} entries")
        return entries
    except Exception as e:
        print(f"[load_recent_entries ERROR] {e}")
        return []


# ── Live gauge data ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_gauge_data():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT ROUND(AVG(value)::numeric, 1) FROM pes_all_readings
            WHERE metric_name = 'temp' AND is_orphan = FALSE AND is_valid = 'TRUE'
            AND DATE(start_time_utc) = (SELECT MAX(DATE(start_time_utc)) FROM pes_all_readings)
        """)
        temp = float(cur.fetchone()[0] or 21.0)
        cur.execute("""
            SELECT ROUND(AVG(value)::numeric, 0) FROM pes_all_readings
            WHERE metric_name = 'co2' AND is_orphan = FALSE AND is_valid = 'TRUE'
            AND DATE(start_time_utc) = (SELECT MAX(DATE(start_time_utc)) FROM pes_all_readings)
        """)
        co2 = float(cur.fetchone()[0] or 466.0)
        cur.execute("""
            SELECT ROUND(AVG(value)::numeric, 1) FROM pes_all_readings
            WHERE metric_name = 'Occupancy' AND is_orphan = FALSE AND is_valid = 'TRUE'
            AND DATE(start_time_utc) = (SELECT MAX(DATE(start_time_utc)) FROM pes_all_readings)
        """)
        occ_raw = float(cur.fetchone()[0] or 0)
        occ_pct = round((occ_raw / 452) * 100, 1)
        conn.close()
        return temp, co2, occ_pct
    except Exception:
        return 21.0, 466.0, 45.0


def make_gauge(value, title, min_val, max_val, unit, green_max, yellow_max):
    if value <= green_max:
        status, color = "GOOD", "#2D6A4F"
    elif value <= yellow_max:
        status, color = "MODERATE", "#E9C46A"
    else:
        status, color = "HIGH", "#E76F51"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": unit, "font": {"size": 28, "color": "#1a1f2e", "family": "Inter"}},
        title={"text": f"<b>{title}</b><br><span style='font-size:0.75em;color:{color}'>{status}</span>",
               "font": {"size": 13, "family": "Inter", "color": "#1a1f2e"}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickfont": {"size": 10, "color": "#6b7280"}, "tickcolor": "#e9ecef"},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "white", "borderwidth": 0,
            "steps": [
                {"range": [min_val, green_max],    "color": "#d1fae5"},
                {"range": [green_max, yellow_max], "color": "#fef9c3"},
                {"range": [yellow_max, max_val],   "color": "#fee2e2"},
            ],
            "threshold": {"line": {"color": "#E8500A", "width": 3}, "thickness": 0.75, "value": value}
        }
    ))
    fig.update_layout(height=200, margin=dict(t=60, b=10, l=20, r=20),
                      paper_bgcolor="white", plot_bgcolor="white", font={"family": "Inter"})
    return fig


# ── Main app function ─────────────────────────────────────────────────────────
def show_main_app():

    # ── CSS ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1100px; }
    .stApp { background: #f4f5f7; color: #1a1f2e; }

    [data-testid="stSidebar"] { background: #1a1f2e !important; border-right: none !important; }
    [data-testid="stSidebar"] * { color: #9ba3b4 !important; }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] strong { color: #ffffff !important; }
    .sv-logo-smart { font-size:1.5rem; font-weight:700; color:#ffffff !important; letter-spacing:-0.5px; }
    .sv-logo-viz   { font-size:1.5rem; font-weight:700; color:#E8500A !important; letter-spacing:-0.5px; }
    .sv-tagline    { font-size:0.7rem; color:#4a5568 !important; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:1.8rem; }
    .mode-badge { display:inline-block; padding:0.25rem 0.7rem; border-radius:20px; font-size:0.72rem; font-weight:600; }
    .mode-badge-simple { background:#e8f4fd; color:#1565c0; }
    .mode-badge-dev    { background:#fff3e0; color:#E8500A; }
    .sidebar-label { font-size:0.68rem; text-transform:uppercase; letter-spacing:0.1em; color:#4a5568 !important; margin-bottom:0.3rem; margin-top:1rem; }

    .sv-header       { background:#ffffff; border-radius:14px; padding:1.4rem 1.8rem; margin-bottom:1.2rem; border-left:4px solid #E8500A; box-shadow:0 1px 4px rgba(0,0,0,0.06); }
    .sv-header-title { font-size:1.5rem; font-weight:700; color:#1a1f2e; margin-bottom:0.2rem; }
    .sv-header-title span { color:#E8500A; }
    .sv-header-sub   { font-size:0.85rem; color:#6b7280; margin:0; }

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .stButton button {
        background: #ffffff !important;
        color: #4a5568 !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.5rem !important;
        width: 100% !important;
        white-space: normal !important;
        line-height: 1.3 !important;
        min-height: 2.4rem !important;
        box-shadow: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] .stButton button:hover {
        border-color: #E8500A !important;
        color: #E8500A !important;
        background: #fff8f5 !important;
    }

    div[data-testid="stForm"] .stButton button {
        background: #E8500A !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.4rem !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    div[data-testid="stForm"] .stButton button:hover { background: #c94008 !important; }

    [data-testid="stSidebar"] .stButton button {
        background: #2a3044 !important;
        color: #e2e8f0 !important;
        border: 1px solid #3d4a63 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { background: #3d4a63 !important; }

    .user-bubble {
        background:#E8500A; border-radius:18px 18px 4px 18px;
        padding:0.8rem 1.2rem; margin:0.6rem 0 0.6rem auto; max-width:75%;
        color:#ffffff; font-size:0.92rem; font-weight:500;
        box-shadow:0 2px 8px rgba(232,80,10,0.25);
    }
    .assistant-bubble {
        background:#ffffff; border-radius:18px 18px 18px 4px;
        padding:1rem 1.3rem; margin:0.6rem 0; max-width:88%;
        color:#1a1f2e; font-size:0.92rem;
        box-shadow:0 1px 4px rgba(0,0,0,0.07); border:1px solid #e9ecef;
    }
    .answer-row { display:flex; align-items:center; gap:0.6rem; padding:0.4rem 0; border-bottom:1px solid #f1f3f5; }
    .answer-row:last-child { border-bottom:none; }
    .answer-dot   { width:8px; height:8px; border-radius:50%; background:#E8500A; flex-shrink:0; }
    .answer-label { color:#6b7280; font-size:0.82rem; }
    .answer-value { color:#1a1f2e; font-weight:600; font-family:'IBM Plex Mono',monospace; font-size:0.88rem; }

    .dev-card        { background:#ffffff; border:1px solid #e9ecef; border-radius:10px; padding:0.9rem 1.1rem; margin:0.5rem 0; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
    .dev-card-header { display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:#6b7280; font-weight:600; }
    .dev-card pre    { margin:0; font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#374151; white-space:pre-wrap; word-break:break-word; line-height:1.65; }

    .tag      { padding:0.18rem 0.55rem; border-radius:5px; font-size:0.68rem; font-weight:700; letter-spacing:0.04em; font-family:'IBM Plex Mono',monospace; }
    .tag-plan { background:#f0fdf4; color:#15803d; border:1px solid #bbf7d0; }
    .tag-rag  { background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }
    .tag-sql  { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
    .tag-val  { background:#fff7ed; color:#c2410c; border:1px solid #fed7aa; }
    .tag-ok   { background:#f0fdf4; color:#15803d; border:1px solid #bbf7d0; }
    .tag-warn { background:#fffbeb; color:#b45309; border:1px solid #fde68a; }

    .stats-row { display:flex; gap:0.6rem; flex-wrap:wrap; margin-bottom:0.8rem; }
    .stat-chip { background:#f8f9fa; border:1px solid #e9ecef; border-radius:6px; padding:0.3rem 0.7rem; font-size:0.76rem; color:#6b7280; font-family:'IBM Plex Mono',monospace; }
    .stat-chip b { color:#E8500A; }

    .error-bubble { background:#fff5f5; border:1px solid #fecaca; border-radius:10px; padding:0.8rem 1.1rem; color:#b91c1c; font-size:0.88rem; margin:0.5rem 0; }

    .stTextInput input { background:#ffffff !important; border:1.5px solid #d1d5db !important; border-radius:10px !important; color:#1a1f2e !important; font-family:'Inter',sans-serif !important; font-size:0.92rem !important; padding:0.65rem 1rem !important; }
    .stTextInput input:focus { border-color:#E8500A !important; box-shadow:0 0 0 3px rgba(232,80,10,0.1) !important; }
    .stTextInput input::placeholder { color:#9ca3af !important; }

    hr.sv-div { border:none; border-top:1px solid #e9ecef; margin:1rem 0; }

    [data-testid="stSelectbox"] > div > div { background:#2a3044 !important; border:1px solid #3d4a63 !important; border-radius:8px !important; color:#e2e8f0 !important; }

    [data-testid="stDownloadButton"] button { background:#ffffff !important; color:#E8500A !important; border:1.5px solid #E8500A !important; border-radius:8px !important; font-weight:600 !important; font-size:0.82rem !important; padding:0.4rem 1rem !important; width:auto !important; margin-top:0.5rem !important; }
    [data-testid="stDownloadButton"] button:hover { background:#fff8f5 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────────────
    if "history" not in st.session_state:
        init_session_table()
        st.session_state.history = load_recent_entries(limit=10)
    if "dev_mode" not in st.session_state:
        st.session_state.dev_mode = False
    if "chip_question" not in st.session_state:
        st.session_state.chip_question = None

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<span class="sv-logo-smart">Smart</span><span class="sv-logo-viz">Viz</span><br>'
            '<span class="sv-tagline">Better Buildings. Better Places.</span>',
            unsafe_allow_html=True
        )

        # Logged in user
        user_name = st.session_state.get("user_name", "")
        if user_name:
            st.markdown(f'<div style="font-size:0.78rem;color:#9ba3b4;margin-bottom:0.8rem;">Signed in as <b style="color:#fff;">{user_name}</b></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Interface Mode</div>', unsafe_allow_html=True)
        dev_mode = st.toggle("Developer Mode", value=st.session_state.dev_mode)
        st.session_state.dev_mode = dev_mode
        if dev_mode:
            st.markdown('<span class="mode-badge mode-badge-dev">⚙ Developer Mode</span>', unsafe_allow_html=True)
            st.markdown("""
            <div style="margin-top:0.8rem;font-size:0.78rem;color:#6b7280;line-height:1.9;">
            <span style="color:#15803d;">●</span> Agent 1 — Planner<br>
            <span style="color:#7c3aed;">●</span> Agent 2 — RAG Schema<br>
            <span style="color:#1d4ed8;">●</span> Agent 3 — SQL Generator<br>
            <span style="color:#c2410c;">●</span> Agent 4 — Validator<br>
            <span style="color:#be185d;">●</span> Agent 5 — Graph Builder
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<span class="mode-badge mode-badge-simple">● Simple Mode</span>', unsafe_allow_html=True)
            st.markdown('<div style="margin-top:0.8rem;font-size:0.78rem;color:#6b7280;">Clean view — answers and charts only.</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Agent 3 — SQL Model</div>', unsafe_allow_html=True)
        model_choice = st.selectbox("Model", ["gpt4", "sqlcoder", "gemma3"], label_visibility="collapsed")

        st.markdown("<hr style='border-color:#2a3044;margin:1.2rem 0;'>", unsafe_allow_html=True)

        if st.button("🗑 Clear Chat"):
            st.session_state.history = []
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_name = None
            st.session_state.page = "landing"
            st.rerun()

        st.markdown("""
        <div style="margin-top:2rem;font-size:0.72rem;color:#3d4a63;line-height:1.9;">
        PES Building · 32 rooms<br>1,048,575 sensor readings<br>pgvector · 23 embeddings<br>5-agent LLM pipeline
        </div>""", unsafe_allow_html=True)

    # ── Main header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sv-header">
        <div class="sv-header-title">Ask your building <span>anything.</span></div>
        <p class="sv-header-sub">Natural language → SQL → chart &nbsp;·&nbsp; 5-agent LLM pipeline &nbsp;·&nbsp; PES Building, University of Sheffield</p>
    </div>""", unsafe_allow_html=True)

    # ── Live Gauge Dashboard ──────────────────────────────────────────────────
    temp_val, co2_val, occ_val = fetch_gauge_data()
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        st.plotly_chart(make_gauge(temp_val, "Temperature", 0, 35, "°C", 23, 27), use_container_width=True, config={"displayModeBar": False})
    with gc2:
        st.plotly_chart(make_gauge(co2_val, "CO2 Air Quality", 0, 2000, " ppm", 800, 1200), use_container_width=True, config={"displayModeBar": False})
    with gc3:
        st.plotly_chart(make_gauge(occ_val, "People Utilisation", 0, 100, "%", 60, 85), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr class='sv-div'>", unsafe_allow_html=True)

    # ── Suggestion chips ──────────────────────────────────────────────────────
    suggestions = [
        "Which room has the highest CO2?",
        "Average temperature across all rooms",
        "Top 5 most occupied rooms today",
        "Rooms with mold risk",
        "Worst air quality last week",
        "Battery levels below 20%",
    ]

    chip_cols = st.columns(len(suggestions))
    for i, s in enumerate(suggestions):
        with chip_cols[i]:
            if st.button(s, key=f"chip_{i}"):
                st.session_state.chip_question = s

    # ── Chat history display ──────────────────────────────────────────────────
    for idx, entry in enumerate(st.session_state.history):
        st.markdown(f'<div class="user-bubble">💬 {entry["question"]}</div>', unsafe_allow_html=True)
        if entry.get("error"):
            st.markdown(f'<div class="error-bubble">⚠ {entry["error"]}</div>', unsafe_allow_html=True)
            continue
        if st.session_state.dev_mode:
            latency  = entry.get("latency", 0)
            attempts = entry.get("attempts", 1)
            model    = entry.get("model", "gpt4")
            st.markdown(f"""
            <div class="stats-row">
                <div class="stat-chip">⏱ <b>{latency:.2f}s</b></div>
                <div class="stat-chip">🔄 retries: <b>{attempts - 1}</b></div>
                <div class="stat-chip">🤖 <b>{model}</b></div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="dev-card">
                <div class="dev-card-header"><span class="tag tag-plan">AGENT 1</span> Planner</div>
                <pre>{entry.get('plan','')}</pre></div>""", unsafe_allow_html=True)
            rag = (entry.get('schema_context','') or '')[:500] + "…"
            st.markdown(f"""<div class="dev-card">
                <div class="dev-card-header"><span class="tag tag-rag">AGENT 2</span> RAG Schema Retrieval</div>
                <pre>{rag}</pre></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="dev-card">
                <div class="dev-card-header"><span class="tag tag-sql">AGENT 3</span> SQL Generator
                    <span style="color:#9ca3af;font-size:0.7rem;">· {model}</span></div>
                <pre>{entry.get('sql','')}</pre></div>""", unsafe_allow_html=True)
            ok        = entry.get("attempts", 1) == 1
            val_tag   = "tag-ok" if ok else "tag-warn"
            val_label = "✓ first pass" if ok else f"⚠ corrected after {entry.get('attempts',1)} attempts"
            st.markdown(f"""<div class="dev-card">
                <div class="dev-card-header"><span class="tag tag-val">AGENT 4</span> Validator
                    <span class="tag {val_tag}">{val_label}</span></div>
                <pre>{entry.get('final_sql', entry.get('sql',''))}</pre></div>""", unsafe_allow_html=True)
            chart_path   = entry.get("chart_path")
            chart_status = "TEXT_ONLY (no chart needed)" if chart_path == "TEXT_ONLY" else (
                os.path.basename(chart_path) if chart_path else "No chart generated"
            )
            st.markdown(f"""<div class="dev-card">
                <div class="dev-card-header"><span class="tag" style="background:#fff0f6;color:#be185d;border:1px solid #fbcfe8;">AGENT 5</span> Graph Builder</div>
                <pre>Output: {chart_status}</pre></div>""", unsafe_allow_html=True)

        results = entry.get("results", [])
        cols    = entry.get("cols", [])
        if results:
            rows_html = ""
            for row in results[:12]:
                for col, val in zip(cols, row):
                    rows_html += f'<div class="answer-row"><div class="answer-dot"></div><span class="answer-label">{col}</span><span class="answer-value">{val}</span></div>'
            st.markdown(f'<div class="assistant-bubble">{rows_html}</div>', unsafe_allow_html=True)

        chart_path = entry.get("chart_path")
        if chart_path and chart_path != "TEXT_ONLY" and os.path.exists(chart_path):
            st.image(chart_path, use_column_width=True)
            with open(chart_path, "rb") as f:
                chart_bytes = f.read()
            st.download_button(
                label="⬇ Download Chart",
                data=chart_bytes,
                file_name=os.path.basename(chart_path),
                mime="image/png",
                key=f"dl_{idx}",
            )

    # ── Input form ────────────────────────────────────────────────────────────
    st.markdown("<hr class='sv-div'>", unsafe_allow_html=True)
    with st.form("query_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input("question", placeholder="Ask anything about your building…", label_visibility="collapsed")
        with col_btn:
            submitted = st.form_submit_button("Ask →")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def build_conversation_context():
        if not st.session_state.history:
            return None
        lines = []
        for entry in st.session_state.history[-3:]:
            if entry.get("error"):
                continue
            q   = entry.get("question", "")
            sql = entry.get("final_sql") or entry.get("sql", "")
            lines.append(f"User asked: {q}")
            if sql:
                lines.append(f"SQL used: {sql}")
        return "\n".join(lines) if lines else None

    def get_last_good_entry():
        for entry in reversed(st.session_state.history):
            if not entry.get("error") and entry.get("results"):
                return entry
        return None

    # ── Pipeline runner ───────────────────────────────────────────────────────
    def run_pipeline(question: str):
        entry      = {"question": question, "model": model_choice}
        last_entry = get_last_good_entry()

        followup_keywords = ["pie chart", "bar chart", "line chart", "chart for that",
                             "chart for the same", "visualise that", "visualize that",
                             "graph for that", "graph for the same", "same question",
                             "previous result", "those results"]
        is_chart_followup = any(kw in question.lower() for kw in followup_keywords)

        with st.spinner("Running pipeline…"):
            start = time.time()
            try:
                if is_chart_followup and last_entry:
                    cols       = last_entry["cols"]
                    results    = last_entry["results"]
                    final_sql  = last_entry.get("final_sql") or last_entry.get("sql", "")
                    combined_q = f"{question} (original question: {last_entry['question']})"
                    chart_path = generate_chart(cols, results, combined_q, final_sql)
                    entry.update({
                        "plan":           f"[Follow-up] Reusing results from: {last_entry['question']}",
                        "schema_context": "",
                        "sql":            final_sql,
                        "final_sql":      final_sql,
                        "cols":           cols,
                        "results":        results,
                        "attempts":       1,
                        "chart_path":     chart_path,
                        "latency":        time.time() - start,
                    })
                else:
                    conv_context        = build_conversation_context()
                    contextual_question = question
                    if conv_context:
                        contextual_question = f"{question}\n\n[Conversation context for reference:\n{conv_context}]"

                    plan = plan_query(contextual_question)
                    entry["plan"] = plan

                    schema_context = retrieve_schema(plan)
                    entry["schema_context"] = schema_context

                    sql = generate_sql(plan, schema_context, model=model_choice)
                    entry["sql"] = sql

                    if not sql.strip().upper().startswith(("SELECT", "WITH")):
                        entry["error"] = "Agent 3 did not return valid SQL. Try rephrasing."
                        st.session_state.history.append(entry)
                        save_entry(entry)
                        st.rerun()

                    cols, results, final_sql, attempts = validate_and_execute(sql, question)
                    entry.update({"cols": cols, "results": results,
                                  "final_sql": final_sql, "attempts": attempts})

                    if not results:
                        entry["error"] = "No results found after validation. Try rephrasing."
                        st.session_state.history.append(entry)
                        save_entry(entry)
                        st.rerun()

                    chart_path          = generate_chart(cols, results, question, final_sql)
                    entry["chart_path"] = chart_path
                    entry["latency"]    = time.time() - start

            except Exception as e:
                entry["error"] = f"Pipeline error: {str(e)}"

        st.session_state.history.append(entry)
        save_entry(entry)
        st.rerun()

    # ── Chip trigger ──────────────────────────────────────────────────────────
    if st.session_state.chip_question:
        question = st.session_state.chip_question
        st.session_state.chip_question = None
        run_pipeline(question)

    # ── Form trigger ──────────────────────────────────────────────────────────
    if submitted and user_input.strip():
        run_pipeline(user_input.strip())