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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:     #0d1117;
    --surf:   #161b27;
    --surf2:  #1e2535;
    --surf3:  #252d40;
    --sb-bg:  #0b0f1a;
    --bdr:    rgba(255,255,255,0.07);
    --bdr2:   rgba(255,255,255,0.12);
    --t1:     #e8edf5;
    --t2:     #8b95b0;
    --t3:     #4a5270;
    --teal:   #00d4b1;
    --teal-d: rgba(0,212,177,0.12);
    --blue:   #3b82f6;
    --blue-d: rgba(59,130,246,0.12);
    --vio:    #8b5cf6;
    --vio-d:  rgba(139,92,246,0.12);
    --amb:    #fbbf24;
    --amb-d:  rgba(251,191,36,0.12);
    --cor:    #f87171;
    --cor-d:  rgba(248,113,113,0.12);
    --font:   'DM Sans', sans-serif;
    --r:      12px;
    --rl:     18px;
    --sh:     0 1px 3px rgba(0,0,0,.3), 0 4px 16px rgba(0,0,0,.2);
    --sh2:    0 8px 32px rgba(0,0,0,.4);
}

.stApp { background: var(--bg) !important; font-family: var(--font) !important; }
.main .block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--sb-bg) !important; border-right: 1px solid var(--bdr) !important; }
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] * { font-family: var(--font) !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { color: var(--t2) !important; font-size: .78rem !important; }
[data-testid="stSidebar"] .stMultiSelect > label {
    color: var(--t3) !important; font-size: .62rem !important;
    font-weight: 700 !important; letter-spacing: .1em !important; text-transform: uppercase !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] {
    background: var(--surf2) !important; border: 1px solid var(--bdr2) !important; border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: var(--teal-d) !important; color: var(--teal) !important;
    border: 1px solid rgba(0,212,177,.2) !important; border-radius: 4px !important;
}
[data-testid="stFileUploader"] {
    background: var(--surf2) !important; border: 1.5px dashed var(--bdr2) !important;
    border-radius: var(--r) !important;
}
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small { color: var(--t2) !important; }

/* Top nav */
.ev-nav {
    display: flex; align-items: center; justify-content: space-between;
    background: var(--surf); border-bottom: 1px solid var(--bdr);
    padding: .875rem 2rem; margin: 0 -2rem 1.75rem -2rem;
    position: sticky; top: 0; z-index: 100;
}
.ev-tabs { display: flex; gap: .25rem; }
.ev-tab { font-size: .78rem; font-weight: 500; color: var(--t3); padding: .4rem .875rem; border-radius: 6px; }
.ev-tab-on { color: var(--t1) !important; background: var(--surf3); }
.ev-right { display: flex; align-items: center; gap: .875rem; }
.ev-search { display: flex; align-items: center; gap: .5rem; background: var(--surf2); border: 1px solid var(--bdr); border-radius: 8px; padding: .35rem .875rem; font-size: .75rem; color: var(--t3); }
.ev-avatar { width: 32px; height: 32px; background: linear-gradient(135deg,#6366f1,#8b5cf6); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: .72rem; font-weight: 700; color: #fff; }
.ev-ibtn { width: 32px; height: 32px; background: var(--surf2); border: 1px solid var(--bdr); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: .85rem; position: relative; }
.ev-dot { position: absolute; top: 4px; right: 4px; width: 6px; height: 6px; background: var(--cor); border-radius: 50%; border: 1px solid var(--sb-bg); }

/* KPI */
.ev-krow { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.ev-kpi {
    background: var(--surf); border: 1px solid var(--bdr); border-radius: var(--rl);
    padding: 1.375rem 1.5rem; box-shadow: var(--sh); position: relative; overflow: hidden;
    transition: transform .2s, box-shadow .2s;
}
.ev-kpi:hover { transform: translateY(-3px); box-shadow: var(--sh2); }
.ev-kpi::before { content:''; position:absolute; top:0; left:20%; right:20%; height:1px; border-radius:0 0 4px 4px; opacity:.8; }
.ev-kpi::after  { content:''; position:absolute; top:-30px; right:-30px; width:100px; height:100px; border-radius:50%; opacity:.07; }
.k-teal::before  { background:var(--teal); } .k-teal::after  { background:var(--teal); }
.k-vio::before   { background:var(--vio);  } .k-vio::after   { background:var(--vio);  }
.k-amb::before   { background:var(--amb);  } .k-amb::after   { background:var(--amb);  }
.k-blue::before  { background:var(--blue); } .k-blue::after  { background:var(--blue); }
.ev-ki { width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;margin-bottom:1rem; }
.ev-kl { font-size:.62rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t3);margin-bottom:.375rem; }
.ev-kv { font-size:1.65rem;font-weight:700;color:var(--t1);letter-spacing:-.04em;line-height:1; }
.ev-kt { display:inline-flex;align-items:center;gap:.2rem;font-size:.68rem;font-weight:600;padding:.15rem .45rem;border-radius:4px;margin-top:.4rem;color:var(--teal);background:var(--teal-d); }

/* Card — used as a pure wrapper; header inside, plotly chart AFTER */
.ev-card { background: var(--surf); border: 1px solid var(--bdr); border-radius: var(--rl); padding: 1.375rem 1.5rem; box-shadow: var(--sh); margin-bottom: 1.25rem; }
.ev-chd { display:flex;align-items:center;justify-content:space-between;padding-bottom:.875rem;border-bottom:1px solid var(--bdr);margin-bottom:.75rem; }
.ev-ct  { font-size:.88rem;font-weight:600;color:var(--t1); }
.ev-cs  { font-size:.7rem;color:var(--t3);margin-top:.15rem; }
.ev-bg  { font-size:.62rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;border-radius:6px;padding:.2rem .6rem; }
.bg-teal  { color:var(--teal);background:var(--teal-d);border:1px solid rgba(0,212,177,.15); }
.bg-vio   { color:var(--vio); background:var(--vio-d); border:1px solid rgba(139,92,246,.15); }
.bg-amb   { color:var(--amb); background:var(--amb-d); border:1px solid rgba(251,191,36,.15); }
.bg-blue  { color:var(--blue);background:var(--blue-d);border:1px solid rgba(59,130,246,.15); }

/* Activity */
.ev-ahd { display:flex;align-items:center;justify-content:space-between;padding-bottom:.875rem;border-bottom:1px solid var(--bdr);margin-bottom:.75rem; }
.ev-at  { font-size:.88rem;font-weight:600;color:var(--t1); }
.ev-ac  { background:var(--cor);color:#fff;font-size:.62rem;font-weight:700;padding:.1rem .5rem;border-radius:10px; }
.ev-ai  { display:flex;align-items:flex-start;gap:.75rem;padding:.75rem 0;border-bottom:1px solid var(--bdr); }
.ev-ai:last-child { border-bottom:none; }
.ev-ad  { width:32px;height:32px;border-radius:8px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:.85rem; }
.ev-ab  { flex:1;min-width:0; }
.ev-abt { font-size:.75rem;color:var(--t2);line-height:1.4; }
.ev-abt strong { color:var(--t1);font-weight:600; }
.ev-atm { font-size:.65rem;color:var(--t3);margin-top:.2rem; }

/* Rings */
.ev-rings { display:flex;gap:1.5rem;flex-wrap:wrap;padding:.25rem 0; }
.ev-ri    { display:flex;flex-direction:column;align-items:center;gap:.5rem; }
.ev-rw    { position:relative;width:72px;height:72px; }
.ev-rw svg{ transform:rotate(-90deg); }
.ev-rc    { position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:700;color:var(--t1); }
.ev-rl    { font-size:.65rem;color:var(--t3);font-weight:500;text-align:center;max-width:72px; }

/* Downloads */
.stDownloadButton button { background: var(--surf2) !important; color: var(--t1) !important; border: 1px solid var(--bdr2) !important; border-radius: var(--r) !important; font-family: var(--font) !important; font-weight: 600 !important; font-size: .82rem !important; padding: .625rem 1.25rem !important; width: 100%; transition: all .2s !important; }
.stDownloadButton button:hover { background: var(--teal-d) !important; border-color: rgba(0,212,177,.3) !important; color: var(--teal) !important; transform: translateY(-1px) !important; }

.stDataFrame { border-radius: var(--r) !important; border: 1px solid var(--bdr) !important; overflow: hidden !important; }
.stSuccess,.stWarning,.stError,.stInfo { border-radius: var(--r) !important; font-family: var(--font) !important; font-size: .82rem !important; }
::-webkit-scrollbar { width:4px;height:4px; } ::-webkit-scrollbar-track { background:var(--bg); } ::-webkit-scrollbar-thumb { background:var(--surf3);border-radius:2px; }
#MainMenu, footer, header { visibility:hidden; } .stDeployButton { display:none; }

/* Empty */
.ev-empty { display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;background:var(--surf);border:1px solid var(--bdr);border-radius:24px;padding:5rem 2rem;box-shadow:var(--sh);position:relative;overflow:hidden; }
.ev-empty::before { content:'';position:absolute;top:-80px;left:50%;transform:translateX(-50%);width:300px;height:300px;background:radial-gradient(circle,rgba(0,212,177,.08) 0%,transparent 70%);pointer-events:none; }
.ev-ei { font-size:3rem;margin-bottom:1rem; }
.ev-etitle { font-size:1.35rem;font-weight:700;color:var(--t1);letter-spacing:-.03em;margin-bottom:.5rem; }
.ev-ebody  { font-size:.82rem;color:var(--t2);max-width:360px;line-height:1.75; }
.ev-chips { display:flex;gap:.5rem;justify-content:center;margin-top:1.25rem; }
.ev-chip  { font-size:.65rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--teal);background:var(--teal-d);border:1px solid rgba(0,212,177,.2);border-radius:6px;padding:.25rem .65rem; }
.ev-steps { display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:2rem;max-width:560px; }
.ev-step  { background:var(--surf2);border:1px solid var(--bdr);border-radius:var(--r);padding:1rem;text-align:left; }
.ev-sn    { font-size:.6rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);background:var(--teal-d);border-radius:4px;padding:.15rem .5rem;display:inline-block;margin-bottom:.5rem; }
.ev-st    { font-size:.75rem;color:var(--t2);line-height:1.55; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ──
PAL = ["#00d4b1","#3b82f6","#8b5cf6","#fbbf24","#f87171","#06b6d4","#f97316"]

def base_layout(**kw):
    d = dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#4a5270", size=11),
        margin=dict(t=16, l=8, r=8, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8b95b0", size=11)),
        xaxis=dict(showgrid=False, color="#4a5270", linecolor="rgba(255,255,255,0.05)", tickcolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#4a5270", linecolor="rgba(0,0,0,0)"),
    )
    for k, v in kw.items():
        if k in ("xaxis","yaxis") and isinstance(v, dict):
            d[k] = {**d[k], **v}
        else:
            d[k] = v
    return d

def card_hdr(title, badge, bg_cls="bg-teal", sub=""):
    """Returns a complete self-contained header block string — no orphan divs."""
    sub_html = f"<div class='ev-cs'>{sub}</div>" if sub else ""
    return (
        f"<div class='ev-chd'>"
        f"<div><div class='ev-ct'>{title}</div>{sub_html}</div>"
        f"<span class='ev-bg {bg_cls}'>{badge}</span>"
        f"</div>"
    )

def kpi(icon, label, value, trend, k_cls, i_bg):
    return (
        f"<div class='ev-kpi {k_cls}'>"
        f"<div class='ev-ki' style='background:{i_bg}'>{icon}</div>"
        f"<div class='ev-kl'>{label}</div>"
        f"<div class='ev-kv'>{value}</div>"
        f"<div class='ev-kt'>{trend}</div>"
        f"</div>"
    )

def smart_money(v):
    if v >= 1e7: return f"&#8377;{v/1e7:.1f}Cr"
    if v >= 1e5: return f"&#8377;{v/1e5:.0f}L"
    return f"&#8377;{v:,.0f}"

def ring(pct, color):
    r=28; c=2*3.14159*r; dash=pct/100*c
    return (
        f"<div class='ev-ri'><div class='ev-rw'>"
        f"<svg width='72' height='72' viewBox='0 0 72 72'>"
        f"<circle cx='36' cy='36' r='{r}' fill='none' stroke='rgba(255,255,255,0.06)' stroke-width='5'/>"
        f"<circle cx='36' cy='36' r='{r}' fill='none' stroke='{color}' stroke-width='5' "
        f"stroke-dasharray='{dash:.1f} {c:.1f}' stroke-linecap='round'/>"
        f"</svg><div class='ev-rc'>{pct}%</div></div>"
    )

def process_data(df):
    if HAS_ETL:
        df = map_columns(df); df = clean_data(df)
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

# ══════════════════════════════════════════
# SIDEBAR  — single block, filters appear once
# ══════════════════════════════════════════
with st.sidebar:

    # Brand header
    st.markdown("""
<div style='padding:1.5rem 1rem 0'>
  <div style='display:flex;align-items:center;gap:.75rem;padding-bottom:1.25rem;
              border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:1.25rem'>
    <div style='width:38px;height:38px;background:linear-gradient(135deg,#00d4b1,#00b8d4);
                border-radius:10px;display:flex;align-items:center;justify-content:center;
                font-size:1.1rem;flex-shrink:0'>&#9889;</div>
    <div>
      <div style='font-size:.9rem;font-weight:700;color:#e8edf5;line-height:1.2'>EV Analytics</div>
      <div style='font-size:.62rem;color:#4a5270;letter-spacing:.09em;text-transform:uppercase;margin-top:2px'>India Platform</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Nav — pure inline styles, no separate CSS class block needed
    NAV = [("📊","Overview",True),("💬","Reports",False),("📈","Analytics",False),
           ("⚙️","Performance",False),("🏭","Manufacturers",False),("💰","Accounting",False),("⚙️","Settings",False)]
    parts = ["<div style='padding:0 1rem'>"]
    for icon, label, active in NAV:
        if active:
            s = "display:flex;align-items:center;gap:.75rem;padding:.6rem .875rem;border-radius:8px;font-size:.82rem;font-weight:600;cursor:default;color:#00d4b1;background:rgba(0,212,177,.12);border:1px solid rgba(0,212,177,.15);margin-bottom:.1rem"
        else:
            s = "display:flex;align-items:center;gap:.75rem;padding:.6rem .875rem;border-radius:8px;font-size:.82rem;font-weight:500;cursor:default;color:#4a5270;margin-bottom:.1rem"
        parts.append(f"<div style='{s}'>{icon}&nbsp;{label}</div>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

    st.markdown(
        "<div style='height:.75rem'></div>"
        "<hr style='border:none;border-top:1px solid rgba(255,255,255,.06);margin:0 1rem'>"
        "<div style='height:.75rem'></div>",
        unsafe_allow_html=True
    )

    # Data source label + uploader
    st.markdown(
        "<div style='padding:0 1rem'>"
        "<p style='font-size:.6rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;"
        "color:#4a5270;margin-bottom:.5rem'>Data Source</p></div>",
        unsafe_allow_html=True
    )
    file = st.file_uploader("Upload Dataset", ["csv","xlsx"], label_visibility="collapsed")

    # Process on upload → store in session_state
    if file is not None:
        try:
            raw = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
            st.session_state["_ev_df"] = process_data(raw)
        except Exception as exc:
            st.error(f"Error: {exc}")
            st.session_state.pop("_ev_df", None)

    df_loaded = st.session_state.get("_ev_df", None)

    # Filters — ONE block, always here, never duplicated
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='padding:0 1rem'>"
        "<p style='font-size:.6rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;"
        "color:#4a5270;margin-bottom:.4rem'>Filters</p></div>",
        unsafe_allow_html=True
    )
    if df_loaded is not None:
        seg_opts = sorted(df_loaded["Segment"].unique())
        mfr_opts = sorted(df_loaded["Manufacturer"].unique())
        seg_sel  = st.multiselect("Segment",      seg_opts, default=seg_opts, key="seg_f")
        mfr_sel  = st.multiselect("Manufacturer", mfr_opts, default=mfr_opts, key="mfr_f")
    else:
        st.multiselect("Segment",      [], key="seg_f", disabled=True, placeholder="Upload a file first")
        st.multiselect("Manufacturer", [], key="mfr_f", disabled=True, placeholder="Upload a file first")
        seg_sel, mfr_sel = [], []

    st.markdown(
        "<div style='padding:1.5rem 1rem 1rem;margin-top:.5rem'>"
        "<div style='font-size:.62rem;color:#2a3050;text-align:center;line-height:2'>"
        "EV Analytics v2.0 &middot; Streamlit + Plotly</div></div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════
# TOP NAV
# ══════════════════════════════════════════
st.markdown("""
<div class='ev-nav'>
  <div class='ev-tabs'>
    <div class='ev-tab ev-tab-on'>Overview</div>
    <div class='ev-tab'>Analytics</div>
    <div class='ev-tab'>Performance</div>
    <div class='ev-tab'>Reports</div>
  </div>
  <div class='ev-right'>
    <div class='ev-search'>&#128269;&nbsp;Search...</div>
    <div class='ev-ibtn'>&#128276;<div class='ev-dot'></div></div>
    <div class='ev-ibtn'>&#9889;</div>
    <div style='display:flex;align-items:center;gap:.5rem'>
      <div class='ev-avatar'>EV</div>
      <span style='font-size:.78rem;color:#8b95b0;font-weight:500'>Admin &#9660;</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if df_loaded is not None and seg_sel and mfr_sel:

    fdf  = df_loaded[df_loaded["Segment"].isin(seg_sel) & df_loaded["Manufacturer"].isin(mfr_sel)]
    rev  = fdf["RevenueINR"].sum()
    prof = fdf["ProfitINR"].sum()
    bat  = fdf["BatterykWh"].mean()
    rng  = fdf["Rangekm"].mean()
    marg = (prof / rev * 100) if rev > 0 else 0

    # ── KPIs ──
    st.markdown(
        "<div class='ev-krow'>" +
        kpi("🚗","Total Vehicles", f"{len(fdf):,}",
            f"&#8593; {fdf['Segment'].nunique()} segs &middot; {fdf['Manufacturer'].nunique()} brands",
            "k-teal","rgba(0,212,177,.12)") +
        kpi("📈","Total Revenue",  smart_money(rev),
            f"&#8593; {marg:.1f}% profit margin",
            "k-vio","rgba(139,92,246,.12)") +
        kpi("💰","Net Profit",     smart_money(prof),
            f"&#8593; {marg:.0f}% of revenue",
            "k-amb","rgba(251,191,36,.12)") +
        kpi("🔋","Avg Battery",    f"{bat:.0f} kWh",
            f"&#8593; {rng:.0f} km avg range",
            "k-blue","rgba(59,130,246,.12)") +
        "</div>",
        unsafe_allow_html=True
    )

    # ── Row 1: Revenue + Top Segments ──
    col1, col2 = st.columns([3,1], gap="medium")

    with col1:
        # Card header rendered as its own complete div; chart rendered below it via st
        st.markdown(
            f"<div class='ev-card'>{card_hdr('Revenue by Segment','Bar Chart',sub='Segment-level revenue breakdown')}</div>",
            unsafe_allow_html=True
        )
        seg_rev = fdf.groupby("Segment")["RevenueINR"].sum().reset_index().sort_values("RevenueINR",ascending=False)
        fig1 = go.Figure()
        for i, row in seg_rev.iterrows():
            fig1.add_trace(go.Bar(
                x=[row["Segment"]], y=[row["RevenueINR"]], name=row["Segment"],
                marker_color=PAL[i % len(PAL)],
                text=[f"\u20B9{row['RevenueINR']:,.0f}"], textposition="outside",
                textfont=dict(size=10,color="#8b95b0"), marker_line_width=0, width=0.5,
            ))
        fig1.update_layout(**base_layout(showlegend=False, height=300, bargap=0.4))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        top_segs = fdf.groupby("Segment")["RevenueINR"].sum().sort_values(ascending=False).head(5)
        total_r  = top_segs.sum() or 1
        icons2   = ["🚗","⚡","🔋","🏭","📊"]
        bg2      = ["rgba(0,212,177,.15)","rgba(59,130,246,.15)","rgba(139,92,246,.15)","rgba(251,191,36,.15)","rgba(248,113,113,.15)"]
        tx2      = ["#00d4b1","#3b82f6","#8b5cf6","#fbbf24","#f87171"]
        rows = ""
        for idx,(seg,val) in enumerate(top_segs.items()):
            rows += (
                f"<div class='ev-ai'>"
                f"<div class='ev-ad' style='background:{bg2[idx]};color:{tx2[idx]}'>{icons2[idx]}</div>"
                f"<div class='ev-ab'>"
                f"<div class='ev-abt'><strong>{seg}</strong> &middot; {val/total_r*100:.1f}%</div>"
                f"<div class='ev-atm'>{smart_money(val)}</div>"
                f"</div></div>"
            )
        st.markdown(
            f"<div class='ev-card'>"
            f"<div class='ev-ahd'><div class='ev-at'>Top Segments</div>"
            f"<div class='ev-ac'>{len(top_segs)}</div></div>"
            f"{rows}</div>",
            unsafe_allow_html=True
        )

    # ── Row 2 ──
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(f"<div class='ev-card'>{card_hdr('Battery vs Range','Scatter','bg-vio')}</div>", unsafe_allow_html=True)
        hov  = ["Manufacturer","Model"] if "Model" in fdf.columns else ["Manufacturer"]
        fig2 = px.scatter(fdf, x="BatterykWh", y="Rangekm", size="RevenueINR",
                          color="Segment", hover_data=hov,
                          labels={"BatterykWh":"Battery (kWh)","Rangekm":"Range (km)"},
                          color_discrete_sequence=PAL)
        fig2.update_traces(marker=dict(line=dict(width=0), opacity=0.75))
        fig2.update_layout(**base_layout(height=300))
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown(f"<div class='ev-card'>{card_hdr('Top 10 Manufacturers','Ranked','bg-amb')}</div>", unsafe_allow_html=True)
        top10 = fdf.groupby("Manufacturer")["ProfitINR"].sum().sort_values(ascending=False).head(10).reset_index()
        fig3  = px.bar(top10, x="Manufacturer", y="ProfitINR", text="ProfitINR",
                       color="ProfitINR", color_continuous_scale=["#1e2535","#00d4b1"])
        fig3.update_traces(texttemplate="\u20B9%{text:,.0f}", textposition="outside",
                           textfont=dict(size=9,color="#8b95b0"), marker_line_width=0, width=0.5)
        fig3.update_layout(**base_layout(showlegend=False, height=300,
                                          coloraxis_showscale=False, xaxis={"tickangle":-40}))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Row 3 ──
    c3, c4, c5 = st.columns(3, gap="medium")
    with c3:
        st.markdown(f"<div class='ev-card'>{card_hdr('Usage Type Split','Donut')}</div>", unsafe_allow_html=True)
        if "UsageType" in fdf.columns:
            usage = fdf.groupby("UsageType").size().reset_index(name="Count")
            fig4  = px.pie(usage, values="Count", names="UsageType",
                           color_discrete_sequence=PAL, hole=0.62)
            fig4.update_traces(textinfo="percent+label", textfont_size=10, textfont_color="#8b95b0",
                               marker=dict(line=dict(color=["#161b27"]*10, width=3)))
            fig4.update_layout(**base_layout(showlegend=False, height=270))
            st.plotly_chart(fig4, use_container_width=True)

    with c4:
        st.markdown(f"<div class='ev-card'>{card_hdr('Avg Charging Time','By Segment')}</div>", unsafe_allow_html=True)
        if "ChargingTimeHours" in fdf.columns:
            chg  = fdf.groupby("Segment")["ChargingTimeHours"].mean().reset_index()
            fig5 = px.bar(chg, x="Segment", y="ChargingTimeHours", color="Segment",
                          labels={"ChargingTimeHours":"Hours"}, color_discrete_sequence=PAL)
            fig5.update_traces(marker_line_width=0, width=0.5)
            fig5.update_layout(**base_layout(showlegend=False, height=270))
            st.plotly_chart(fig5, use_container_width=True)

    with c5:
        st.markdown(f"<div class='ev-card'>{card_hdr('Energy Consumption','By Segment')}</div>", unsafe_allow_html=True)
        if "EnergykWh" in fdf.columns:
            erg  = fdf.groupby("Segment")["EnergykWh"].mean().reset_index()
            fig6 = px.bar(erg, x="Segment", y="EnergykWh", color="Segment",
                          labels={"EnergykWh":"kWh"},
                          color_discrete_sequence=[PAL[i] for i in [2,0,1,3,4]])
            fig6.update_traces(marker_line_width=0, width=0.5)
            fig6.update_layout(**base_layout(showlegend=False, height=270))
            st.plotly_chart(fig6, use_container_width=True)

    # ── Progress rings (fully self-contained single markdown call) ──
    pct_vals  = fdf.groupby("Segment")["ProfitINR"].sum()
    pct_total = pct_vals.sum() or 1
    rcols     = ["#00d4b1","#3b82f6","#8b5cf6","#fbbf24","#f87171","#06b6d4"]
    rings_html = ""
    for idx,(seg,val) in enumerate(pct_vals.head(6).items()):
        pct = int(val/pct_total*100)
        rings_html += ring(pct, rcols[idx % len(rcols)]) + f"<div class='ev-rl'>{seg[:10]}</div></div>"

    st.markdown(
        f"<div class='ev-card'>"
        f"{card_hdr('Segment Efficiency Overview','Live','bg-blue')}"
        f"<div class='ev-rings'>{rings_html}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Raw data ──
    st.markdown(
        f"<div class='ev-card'>"
        f"{card_hdr('Raw Dataset', f'{len(fdf):,} rows &middot; {len(fdf.columns)} cols')}"
        f"</div>",
        unsafe_allow_html=True
    )
    st.dataframe(fdf.reset_index(drop=True), height=340, use_container_width=True)

    # ── Downloads ──
    st.markdown("<br>", unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="medium")
    with d1:
        st.download_button("&#x2B07; Download Filtered Data (CSV)",
                           fdf.to_csv(index=False).encode(),
                           "ev_filtered_data.csv","text/csv", use_container_width=True)
    with d2:
        summary = pd.DataFrame({
            "Metric":["Total Vehicles","Total Revenue","Total Profit","Avg Battery (kWh)","Avg Range (km)"],
            "Value": [len(fdf),f"\u20B9{rev:,.0f}",f"\u20B9{prof:,.0f}",f"{bat:.1f}",f"{rng:.1f}"]
        })
        st.download_button("&#x1F4CA; Download Summary Report (CSV)",
                           summary.to_csv(index=False).encode(),
                           "ev_summary.csv","text/csv", use_container_width=True)

else:
    st.markdown("""
<div class='ev-empty'>
  <div class='ev-ei'>&#9889;</div>
  <div class='ev-etitle'>Upload Your EV Dataset</div>
  <p class='ev-ebody'>Drop a CSV or Excel file into the sidebar to unlock live analytics, segment breakdowns, manufacturer rankings, and exportable reports.</p>
  <div class='ev-chips'><span class='ev-chip'>.csv</span><span class='ev-chip'>.xlsx</span></div>
  <div class='ev-steps'>
    <div class='ev-step'><span class='ev-sn'>Step 1</span><div class='ev-st'>Upload your CSV or Excel file from the sidebar</div></div>
    <div class='ev-step'><span class='ev-sn'>Step 2</span><div class='ev-st'>Use filters to focus on segments and manufacturers</div></div>
    <div class='ev-step'><span class='ev-sn'>Step 3</span><div class='ev-st'>Explore charts and download filtered reports instantly</div></div>
  </div>
</div>""", unsafe_allow_html=True)
