# ---------- PATH FIX ----------
import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------- IMPORTS ----------
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="EV Analytics India",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- ETL IMPORTS ----------
try:
    from elt.column_mapper import map_columns
    from elt.data_cleaner import clean_data
    HAS_ETL = True
except ImportError:
    HAS_ETL = False

# ---------- CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    /* Dark navy foundation — matches reference */
    --bg:           #0d1117;
    --surface:      #161b27;
    --surface-2:    #1e2535;
    --surface-3:    #252d40;
    --sidebar-bg:   #0b0f1a;

    /* Borders */
    --border:       rgba(255,255,255,0.07);
    --border-2:     rgba(255,255,255,0.12);

    /* Text hierarchy */
    --text:         #e8edf5;
    --text-2:       #8b95b0;
    --text-3:       #4a5270;

    /* Brand accent — teal/cyan like reference gradient */
    --teal:         #00d4b1;
    --teal-dim:     rgba(0,212,177,0.12);
    --teal-glow:    rgba(0,212,177,0.25);
    --cyan:         #00b8d4;
    --blue:         #3b82f6;
    --blue-dim:     rgba(59,130,246,0.12);
    --violet:       #8b5cf6;
    --violet-dim:   rgba(139,92,246,0.12);
    --amber:        #fbbf24;
    --amber-dim:    rgba(251,191,36,0.12);
    --coral:        #f87171;
    --coral-dim:    rgba(248,113,113,0.12);

    /* Chart gradient — teal to deep navy like reference area chart */
    --chart-top:    #00d4b1;
    --chart-mid:    #00b8d4;
    --chart-bot:    rgba(0,184,212,0);

    --font:         'DM Sans', sans-serif;
    --mono:         'DM Mono', monospace;
    --radius:       12px;
    --radius-lg:    18px;

    --shadow:       0 1px 3px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2);
    --shadow-lg:    0 8px 32px rgba(0,0,0,0.4);
    --glow-teal:    0 0 20px rgba(0,212,177,0.15), 0 0 40px rgba(0,212,177,0.08);
}

/* ── Global ── */
.stApp {
    background: var(--bg) !important;
    font-family: var(--font) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
    padding: 0 !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font) !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text-2) !important;
    font-size: 0.78rem !important;
}
[data-testid="stSidebar"] .stMultiSelect > label {
    color: var(--text-3) !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* Sidebar multiselect input */
[data-testid="stSidebar"] [data-baseweb="select"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: var(--teal-dim) !important;
    color: var(--teal) !important;
    border: 1px solid rgba(0,212,177,0.2) !important;
    border-radius: 4px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface-2) !important;
    border: 1.5px dashed var(--border-2) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small {
    color: var(--text-2) !important;
}

/* ── Main content ── */
.main .block-container {
    padding: 0 2rem 2rem 2rem !important;
    max-width: 100% !important;
}

/* ── Top nav bar ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0.875rem 2rem;
    margin: 0 -2rem 2rem -2rem;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-left {
    display: flex;
    align-items: center;
    gap: 2rem;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.nav-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--teal), var(--cyan));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    box-shadow: var(--glow-teal);
}
.nav-logo-text {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
}
.nav-tabs {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}
.nav-tab {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-3);
    padding: 0.4rem 0.875rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.01em;
}
.nav-tab.active {
    color: var(--text);
    background: var(--surface-3);
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.nav-search {
    display: flex; align-items: center; gap: 0.5rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.35rem 0.875rem;
    font-size: 0.75rem;
    color: var(--text-3);
}
.nav-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; color: white;
}
.nav-badge {
    width: 8px; height: 8px;
    background: var(--coral);
    border-radius: 50%;
    position: relative; top: -8px; left: -6px;
}
.nav-icon-btn {
    width: 32px; height: 32px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; cursor: pointer;
    position: relative;
}
.nav-notif-dot {
    position: absolute;
    top: 4px; right: 4px;
    width: 6px; height: 6px;
    background: var(--coral);
    border-radius: 50%;
    border: 1px solid var(--sidebar-bg);
}

/* ── Sidebar brand block ── */
.sb-inner {
    padding: 1.5rem 1.25rem;
}
.sb-brand {
    display: flex; align-items: center; gap: 0.75rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.sb-logo {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--teal), var(--cyan));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: var(--glow-teal);
    flex-shrink: 0;
}
.sb-title { font-size: 0.9rem; font-weight: 700; color: var(--text); line-height: 1.2; }
.sb-sub   { font-size: 0.65rem; color: var(--text-3); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px; }

/* Sidebar nav items */
.sb-nav-item {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.625rem 0.875rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-3);
    margin-bottom: 0.125rem;
    cursor: pointer;
    transition: all 0.15s;
}
.sb-nav-item.active {
    background: var(--teal-dim);
    color: var(--teal);
    border: 1px solid rgba(0,212,177,0.15);
}
.sb-nav-item .nav-icon { font-size: 0.9rem; }
.sb-section {
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-3) !important;
    margin: 1.25rem 0 0.5rem;
    display: block;
    padding: 0 0.25rem;
}

/* ── KPI Cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.375rem 1.5rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}
/* Glowing top accent line */
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 20%; right: 20%;
    height: 1px;
    border-radius: 0 0 4px 4px;
    opacity: 0.7;
}
/* Subtle radial glow in corner */
.kpi::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%;
    opacity: 0.08;
}
.kpi.teal::before  { background: var(--teal); }
.kpi.teal::after   { background: var(--teal); }
.kpi.violet::before { background: var(--violet); }
.kpi.violet::after  { background: var(--violet); }
.kpi.amber::before { background: var(--amber); }
.kpi.amber::after  { background: var(--amber); }
.kpi.blue::before  { background: var(--blue); }
.kpi.blue::after   { background: var(--blue); }

.kpi-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.kpi-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 0.375rem;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.04em;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.kpi-note {
    font-size: 0.7rem;
    color: var(--text-3);
    margin-top: 0.4rem;
    font-weight: 400;
}
.kpi-trend {
    display: inline-flex; align-items: center; gap: 0.2rem;
    font-size: 0.68rem; font-weight: 600;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    margin-top: 0.4rem;
}
.kpi-trend.up   { color: var(--teal); background: var(--teal-dim); }
.kpi-trend.down { color: var(--coral); background: var(--coral-dim); }

/* ── Chart Cards ── */
.chart-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.375rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
}
.chart-card-hd {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
}
.chart-card-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
}
.chart-card-sub {
    font-size: 0.7rem;
    color: var(--text-3);
    margin-top: 0.15rem;
}
.chart-badge {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--teal);
    background: var(--teal-dim);
    border: 1px solid rgba(0,212,177,0.15);
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
}
.chart-badge-violet {
    color: var(--violet);
    background: var(--violet-dim);
    border-color: rgba(139,92,246,0.15);
}
.chart-badge-amber {
    color: var(--amber);
    background: var(--amber-dim);
    border-color: rgba(251,191,36,0.15);
}

/* ── Activity feed (right panel like reference) ── */
.activity-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.375rem 1.5rem;
    box-shadow: var(--shadow);
    height: 100%;
}
.activity-hd {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.25rem;
    padding-bottom: 0.875rem;
    border-bottom: 1px solid var(--border);
}
.activity-title { font-size: 0.88rem; font-weight: 600; color: var(--text); }
.activity-count {
    background: var(--coral);
    color: white;
    font-size: 0.62rem; font-weight: 700;
    padding: 0.1rem 0.45rem;
    border-radius: 10px;
    min-width: 20px; text-align: center;
}
.activity-item {
    display: flex; align-items: flex-start; gap: 0.75rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
}
.activity-item:last-child { border-bottom: none; }
.activity-dot {
    width: 32px; height: 32px; border-radius: 8px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
}
.activity-body { flex: 1; min-width: 0; }
.activity-text { font-size: 0.75rem; color: var(--text-2); line-height: 1.4; }
.activity-text strong { color: var(--text); font-weight: 600; }
.activity-time { font-size: 0.65rem; color: var(--text-3); margin-top: 0.2rem; }

/* ── Progress rings (like reference 65%, 55%, 27%) ── */
.progress-row {
    display: flex; gap: 1.25rem;
    margin-top: 0.5rem;
}
.progress-item {
    display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
}
.ring-wrap { position: relative; width: 72px; height: 72px; }
.ring-wrap svg { transform: rotate(-90deg); }
.ring-center {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700; color: var(--text);
}
.ring-label { font-size: 0.65rem; color: var(--text-3); font-weight: 500; text-align: center; }

/* ── Download buttons ── */
.stDownloadButton button {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border-2) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.625rem 1.25rem !important;
    width: 100%;
    transition: all 0.2s !important;
}
.stDownloadButton button:hover {
    background: var(--teal-dim) !important;
    border-color: rgba(0,212,177,0.3) !important;
    color: var(--teal) !important;
    box-shadow: 0 4px 12px rgba(0,212,177,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] {
    background: var(--surface) !important;
}

/* ── Alerts ── */
.stSuccess,.stWarning,.stError,.stInfo {
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-2) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 2px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Empty state ── */
.empty-wrap {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 5rem 2rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}
.empty-wrap::before {
    content: '';
    position: absolute;
    top: -80px; left: 50%; transform: translateX(-50%);
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,212,177,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title {
    font-size: 1.35rem !important; font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.03em; margin-bottom: 0.5rem;
}
.empty-body {
    font-size: 0.82rem !important;
    color: var(--text-2) !important;
    max-width: 360px; line-height: 1.75;
}
.fmt-chips { display: flex; gap: 0.5rem; justify-content: center; margin-top: 1.25rem; }
.fmt-chip {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.07em;
    text-transform: uppercase; color: var(--teal);
    background: var(--teal-dim);
    border: 1px solid rgba(0,212,177,0.2);
    border-radius: 6px; padding: 0.25rem 0.65rem;
}
.step-grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 1rem; margin-top: 2rem; max-width: 560px;
}
.step {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem; text-align: left;
}
.step-num {
    font-size: 0.6rem; font-weight: 800; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--teal);
    background: var(--teal-dim); border-radius: 4px;
    padding: 0.15rem 0.5rem; display: inline-block; margin-bottom: 0.5rem;
}
.step-text { font-size: 0.75rem; color: var(--text-2); font-weight: 400; line-height: 1.55; }

/* Section divider */
.section-label {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--text-3);
    margin: 0.5rem 0 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──
PALETTE = ["#00d4b1", "#3b82f6", "#8b5cf6", "#fbbf24", "#f87171", "#06b6d4", "#f97316"]

def base_layout(**kw):
    d = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#4a5270", size=11),
        margin=dict(t=16, l=8, r=8, b=8),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b95b0", size=11)
        ),
        xaxis=dict(
            showgrid=False, color="#4a5270",
            linecolor="rgba(255,255,255,0.06)",
            tickcolor="rgba(0,0,0,0)"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            color="#4a5270",
            linecolor="rgba(0,0,0,0)"
        ),
    )
    for k, v in kw.items():
        if k in ("xaxis", "yaxis") and isinstance(v, dict):
            d[k] = {**d[k], **v}
        else:
            d[k] = v
    return d

def chart_card_start(title, badge, badge_class="chart-badge", sub=""):
    sub_html = f"<div class='chart-card-sub'>{sub}</div>" if sub else ""
    return f"""<div class='chart-card'>
    <div class='chart-card-hd'>
        <div>
            <div class='chart-card-title'>{title}</div>
            {sub_html}
        </div>
        <span class='{badge_class}'>{badge}</span>
    </div>"""

def kpi_html(icon, label, value, note, color_class, icon_bg, trend="", trend_dir="up"):
    trend_html = f"<div class='kpi-trend {trend_dir}'>{trend}</div>" if trend else f"<div class='kpi-note'>{note}</div>"
    return f"""<div class='kpi {color_class}'>
        <div class='kpi-icon' style='background:{icon_bg}'>{icon}</div>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        {trend_html}
    </div>"""

def smart_money(v):
    if v >= 1e7:  return f"₹{v/1e7:.1f}Cr"
    if v >= 1e5:  return f"₹{v/1e5:.0f}L"
    return f"₹{v:,.0f}"

def progress_ring(pct, color, label):
    r, cx, cy = 28, 36, 36
    circ = 2 * 3.14159 * r
    dash = pct / 100 * circ
    return f"""<div class='progress-item'>
        <div class='ring-wrap'>
            <svg width='72' height='72' viewBox='0 0 72 72'>
                <circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='rgba(255,255,255,0.06)' stroke-width='5'/>
                <circle cx='{cx}' cy='{cy}' r='{r}' fill='none' stroke='{color}' stroke-width='5'
                    stroke-dasharray='{dash:.1f} {circ:.1f}' stroke-linecap='round'
                    style='filter:drop-shadow(0 0 4px {color}66)'/>
            </svg>
            <div class='ring-center'>{pct}%</div>
        </div>
        <div class='ring-label'>{label}</div>
    </div>"""

# ── Data processing ──
def process_data(df):
    if HAS_ETL:
        df = map_columns(df)
        df = clean_data(df)
    else:
        col_map = {
            "Vehicle_ID":"VehicleID","Battery_kWh":"BatterykWh","Range_km":"Rangekm",
            "Ex_Showroom_Price_INR":"PriceINR","Avg_Charging_Time_Hours":"ChargingTimeHours",
            "Energy_Consumed_kWh":"EnergykWh","Operating_Cost_INR":"OperatingCostINR",
            "Revenue_INR":"RevenueINR","Usage_Type":"UsageType","Customer_Location_Type":"LocationType"
        }
        df = df.rename(columns=col_map)
        if "ProfitINR" not in df.columns:
            df["ProfitINR"] = df["RevenueINR"] - df["OperatingCostINR"]
        df = df.dropna(subset=["Segment","Manufacturer"])
    return df

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div class='sb-inner'>
        <div class='sb-brand'>
            <div class='sb-logo'>⚡</div>
            <div>
                <div class='sb-title'>EV Analytics</div>
                <div class='sb-sub'>India Platform</div>
            </div>
        </div>

        <div class='sb-nav-item active'>
            <span class='nav-icon'>📊</span> Overview
        </div>
        <div class='sb-nav-item'>
            <span class='nav-icon'>💬</span> Reports
        </div>
        <div class='sb-nav-item'>
            <span class='nav-icon'>📈</span> Analytics
        </div>
        <div class='sb-nav-item'>
            <span class='nav-icon'>⚙️</span> Performance
        </div>
        <div class='sb-nav-item'>
            <span class='nav-icon'>🏭</span> Manufacturers
        </div>
        <div class='sb-nav-item'>
            <span class='nav-icon'>💰</span> Accounting
        </div>
        <div class='sb-nav-item'>
            <span class='nav-icon'>⚙</span> Settings
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:0 1.25rem'>", unsafe_allow_html=True)
    st.markdown("<span class='sb-section'>Data Source</span>", unsafe_allow_html=True)
    file = st.file_uploader("Upload Dataset", ["csv","xlsx"], label_visibility="collapsed")
    st.markdown("<span class='sb-section'>Filters</span>", unsafe_allow_html=True)
    _seg = st.multiselect("Segment", [], key="seg0")
    _mfr = st.multiselect("Manufacturer", [], key="mfr0")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""<div style='padding:1.5rem 1.25rem 1rem;margin-top:auto'>
        <div style='font-size:0.65rem;color:#2a3050;text-align:center;line-height:2'>
            EV Analytics v2.0 · Streamlit + Plotly
        </div></div>""", unsafe_allow_html=True)

# ── TOP NAV BAR ──
st.markdown("""
<div class='top-nav'>
    <div class='nav-left'>
        <div class='nav-tabs'>
            <div class='nav-tab active'>Overview</div>
            <div class='nav-tab'>Analytics</div>
            <div class='nav-tab'>Performance</div>
            <div class='nav-tab'>Reports</div>
        </div>
    </div>
    <div class='nav-right'>
        <div class='nav-search'>🔍&nbsp; Search...</div>
        <div class='nav-icon-btn'>🔔<div class='nav-notif-dot'></div></div>
        <div class='nav-icon-btn'>⚡</div>
        <div style='display:flex;align-items:center;gap:0.5rem'>
            <div class='nav-avatar'>EV</div>
            <span style='font-size:0.78rem;color:#8b95b0;font-weight:500'>Admin ▾</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MAIN ──
if file:
    try:
        df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
        df = process_data(df)

        # Live sidebar filters
        with st.sidebar:
            st.markdown("<div style='padding:0 1.25rem'>", unsafe_allow_html=True)
            st.markdown("<span class='sb-section'>Active Filters</span>", unsafe_allow_html=True)
            seg_sel = st.multiselect("Segment", sorted(df["Segment"].unique()),
                                     default=list(df["Segment"].unique()), key="seg1")
            mfr_sel = st.multiselect("Manufacturer", sorted(df["Manufacturer"].unique()),
                                     default=list(df["Manufacturer"].unique()), key="mfr1")
            st.markdown("</div>", unsafe_allow_html=True)

        fdf = df[df["Segment"].isin(seg_sel) & df["Manufacturer"].isin(mfr_sel)]

        # ── KPI CARDS ──
        rev   = fdf["RevenueINR"].sum()
        prof  = fdf["ProfitINR"].sum()
        bat   = fdf["BatterykWh"].mean()
        rng   = fdf["Rangekm"].mean()
        marg  = (prof / rev * 100) if rev > 0 else 0

        st.markdown(
            "<div class='kpi-row'>" +
            kpi_html("🚗", "Total Vehicles", f"{len(fdf):,}",
                     f"{fdf['Segment'].nunique()} segments",
                     "teal", "rgba(0,212,177,0.12)",
                     trend=f"↑ {fdf['Manufacturer'].nunique()} brands", trend_dir="up") +
            kpi_html("💹", "Total Revenue", smart_money(rev),
                     f"₹{rev:,.0f}",
                     "violet", "rgba(139,92,246,0.12)",
                     trend=f"↑ {marg:.1f}% margin", trend_dir="up") +
            kpi_html("💰", "Net Profit", smart_money(prof),
                     f"Margin {marg:.1f}%",
                     "amber", "rgba(251,191,36,0.12)",
                     trend=f"↑ {marg:.0f}% of revenue", trend_dir="up") +
            kpi_html("🔋", "Avg Battery", f"{bat:.0f} kWh",
                     f"≈ {rng:.0f} km avg range",
                     "blue", "rgba(59,130,246,0.12)",
                     trend=f"↑ {rng:.0f} km range", trend_dir="up") +
            "</div>",
            unsafe_allow_html=True
        )

        # ── ROW 1: Main chart + Activity panel ──
        main_col, side_col = st.columns([3, 1], gap="medium")

        with main_col:
            st.markdown(chart_card_start(
                "Revenue Distribution by Segment",
                "Bar Chart",
                sub="Segment-level revenue breakdown"
            ), unsafe_allow_html=True)
            seg_rev = fdf.groupby("Segment")["RevenueINR"].sum().reset_index().sort_values("RevenueINR", ascending=False)

            # Use an area-style filled bar to echo the reference gradient chart
            fig1 = go.Figure()
            for i, row in seg_rev.iterrows():
                fig1.add_trace(go.Bar(
                    x=[row["Segment"]],
                    y=[row["RevenueINR"]],
                    name=row["Segment"],
                    marker_color=PALETTE[i % len(PALETTE)],
                    text=[f"₹{row['RevenueINR']:,.0f}"],
                    textposition="outside",
                    textfont=dict(size=10, color="#8b95b0"),
                    marker_line_width=0,
                    width=0.5,
                ))
            fig1.update_layout(**base_layout(
                showlegend=False, height=300,
                bargap=0.4,
            ))
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with side_col:
            # Compute top segments for activity panel
            top_segs = fdf.groupby("Segment")["RevenueINR"].sum().sort_values(ascending=False).head(5)
            total_r  = top_segs.sum() or 1

            items_html = ""
            icons = ["🚗","⚡","🔋","🏭","📊"]
            colors = ["rgba(0,212,177,0.15)","rgba(59,130,246,0.15)","rgba(139,92,246,0.15)","rgba(251,191,36,0.15)","rgba(248,113,113,0.15)"]
            icon_colors = ["#00d4b1","#3b82f6","#8b5cf6","#fbbf24","#f87171"]
            for idx, (seg, val) in enumerate(top_segs.items()):
                items_html += f"""<div class='activity-item'>
                    <div class='activity-dot' style='background:{colors[idx]};color:{icon_colors[idx]}'>{icons[idx]}</div>
                    <div class='activity-body'>
                        <div class='activity-text'><strong>{seg}</strong> · {val/total_r*100:.1f}% share</div>
                        <div class='activity-time'>{smart_money(val)} revenue</div>
                    </div>
                </div>"""

            st.markdown(f"""<div class='activity-card'>
                <div class='activity-hd'>
                    <div class='activity-title'>Top Segments</div>
                    <div class='activity-count'>{len(top_segs)}</div>
                </div>
                {items_html}
            </div>""", unsafe_allow_html=True)

        # ── ROW 2 ──
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(chart_card_start("Battery Capacity vs Range", "Scatter", badge_class="chart-badge chart-badge-violet"), unsafe_allow_html=True)
            hov = ["Manufacturer","Model"] if "Model" in fdf.columns else ["Manufacturer"]
            fig2 = px.scatter(fdf, x="BatterykWh", y="Rangekm", size="RevenueINR",
                              color="Segment", hover_data=hov,
                              labels={"BatterykWh":"Battery (kWh)","Rangekm":"Range (km)"},
                              color_discrete_sequence=PALETTE)
            fig2.update_traces(marker=dict(line=dict(width=0), opacity=0.75))
            fig2.update_layout(**base_layout(height=300))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown(chart_card_start("Top 10 Manufacturers by Profit", "Ranked", badge_class="chart-badge chart-badge-amber"), unsafe_allow_html=True)
            top10 = (fdf.groupby("Manufacturer")["ProfitINR"].sum()
                       .sort_values(ascending=False).head(10).reset_index())
            fig3 = px.bar(top10, x="Manufacturer", y="ProfitINR", text="ProfitINR",
                          color="ProfitINR",
                          color_continuous_scale=["#1e2535","#00d4b1"])
            fig3.update_traces(
                texttemplate="₹%{text:,.0f}", textposition="outside",
                textfont=dict(size=9, color="#8b95b0"),
                marker_line_width=0, width=0.5
            )
            fig3.update_layout(**base_layout(
                showlegend=False, height=300,
                coloraxis_showscale=False,
                xaxis={"tickangle":-40}
            ))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── ROW 3: Three small charts ──
        c3, c4, c5 = st.columns(3, gap="medium")

        with c3:
            st.markdown(chart_card_start("Usage Type Split","Donut"), unsafe_allow_html=True)
            if "UsageType" in fdf.columns:
                usage = fdf.groupby("UsageType").size().reset_index(name="Count")
                fig4  = px.pie(usage, values="Count", names="UsageType",
                               color_discrete_sequence=PALETTE, hole=0.62)
                fig4.update_traces(
                    textinfo="percent+label", textfont_size=10,
                    textfont_color="#8b95b0",
                    marker=dict(line=dict(color=["#161b27"]*10, width=3))
                )
                fig4.update_layout(**base_layout(showlegend=False, height=280))
                st.plotly_chart(fig4, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c4:
            st.markdown(chart_card_start("Avg Charging Time","By Segment"), unsafe_allow_html=True)
            if "ChargingTimeHours" in fdf.columns:
                chg  = fdf.groupby("Segment")["ChargingTimeHours"].mean().reset_index()
                fig5 = px.bar(chg, x="Segment", y="ChargingTimeHours", color="Segment",
                              labels={"ChargingTimeHours":"Hours"},
                              color_discrete_sequence=PALETTE)
                fig5.update_traces(marker_line_width=0, width=0.5)
                fig5.update_layout(**base_layout(showlegend=False, height=280))
                st.plotly_chart(fig5, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c5:
            st.markdown(chart_card_start("Energy Consumption","By Segment"), unsafe_allow_html=True)
            if "EnergykWh" in fdf.columns:
                erg  = fdf.groupby("Segment")["EnergykWh"].mean().reset_index()
                fig6 = px.bar(erg, x="Segment", y="EnergykWh", color="Segment",
                              labels={"EnergykWh":"kWh"},
                              color_discrete_sequence=[PALETTE[i] for i in [2,0,1,3,4]])
                fig6.update_traces(marker_line_width=0, width=0.5)
                fig6.update_layout(**base_layout(showlegend=False, height=280))
                st.plotly_chart(fig6, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Progress rings (like reference bottom row) ──
        if "UsageType" in fdf.columns:
            st.markdown(chart_card_start("Segment Efficiency Overview", "Live"), unsafe_allow_html=True)
            pct_vals = fdf.groupby("Segment")["ProfitINR"].sum()
            pct_total = pct_vals.sum() or 1
            rings_html = "<div class='progress-row'>"
            ring_colors = ["#00d4b1","#3b82f6","#8b5cf6","#fbbf24","#f87171","#06b6d4"]
            for idx, (seg, val) in enumerate(pct_vals.head(6).items()):
                pct = int(val / pct_total * 100)
                rings_html += progress_ring(pct, ring_colors[idx % len(ring_colors)], seg[:10])
            rings_html += "</div>"
            st.markdown(rings_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── RAW DATA ──
        st.markdown(chart_card_start(
            "Raw Dataset",
            f"{len(fdf):,} rows · {len(fdf.columns)} cols"
        ), unsafe_allow_html=True)
        st.dataframe(fdf.reset_index(drop=True), height=340, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── DOWNLOADS ──
        st.markdown("<br>", unsafe_allow_html=True)
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            st.download_button(
                "⬇  Download Filtered Data (CSV)",
                fdf.to_csv(index=False).encode(),
                "ev_filtered_data.csv", "text/csv",
                use_container_width=True
            )
        with d2:
            summary = pd.DataFrame({
                "Metric": ["Total Vehicles","Total Revenue (₹)","Total Profit (₹)","Avg Battery (kWh)","Avg Range (km)"],
                "Value":  [len(fdf), f"₹{rev:,.0f}", f"₹{prof:,.0f}", f"{bat:.1f}", f"{rng:.1f}"]
            })
            st.download_button(
                "📊  Download Summary Report (CSV)",
                summary.to_csv(index=False).encode(),
                "ev_summary.csv", "text/csv",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.code("""Required columns:
  Manufacturer  ·  Model  ·  Segment
  Battery_kWh (or BatterykWh)  ·  Range_km (or Rangekm)
  Revenue_INR (or RevenueINR)  ·  Operating_Cost_INR (or OperatingCostINR)""")

else:
    # ── EMPTY STATE ──
    st.markdown("""
    <div class='empty-wrap'>
        <div class='empty-icon'>⚡</div>
        <div class='empty-title'>Upload Your EV Dataset</div>
        <p class='empty-body'>
            Drop a CSV or Excel file into the sidebar to unlock live analytics,
            segment breakdowns, manufacturer rankings, and exportable reports.
        </p>
        <div class='fmt-chips'>
            <span class='fmt-chip'>.csv</span>
            <span class='fmt-chip'>.xlsx</span>
        </div>
        <div class='step-grid'>
            <div class='step'>
                <span class='step-num'>Step 1</span>
                <div class='step-text'>Upload your CSV or Excel file from the sidebar panel</div>
            </div>
            <div class='step'>
                <span class='step-num'>Step 2</span>
                <div class='step-text'>Use segment &amp; manufacturer filters to focus your view</div>
            </div>
            <div class='step'>
                <span class='step-num'>Step 3</span>
                <div class='step-text'>Explore charts and download filtered reports instantly</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
