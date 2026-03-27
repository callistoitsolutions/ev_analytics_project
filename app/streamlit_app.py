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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:          #f4f6fb;
    --white:       #ffffff;
    --sidebar-bg:  #1e2433;
    --border:      #e4e8f0;
    --text:        #1a1f36;
    --text-2:      #4a5173;
    --text-3:      #8b91aa;
    --blue:        #3366ff;
    --blue-light:  #eef1ff;
    --green:       #00b894;
    --green-light: #e6f9f5;
    --amber:       #f59e0b;
    --amber-light: #fef3e2;
    --violet:      #7c3aed;
    --violet-light:#f3f0ff;
    --font:        'Plus Jakarta Sans', sans-serif;
    --font-serif:  'Instrument Serif', serif;
    --radius:      14px;
    --shadow:      0 1px 3px rgba(26,31,54,0.06), 0 4px 12px rgba(26,31,54,0.06);
    --shadow-md:   0 2px 8px rgba(26,31,54,0.09), 0 8px 24px rgba(26,31,54,0.09);
}

/* App background */
.stApp { background: var(--bg) !important; font-family: var(--font) !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--sidebar-bg) !important; }
[data-testid="stSidebar"] > div { padding: 1.75rem 1.5rem !important; }
[data-testid="stSidebar"] * { font-family: var(--font) !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #a8b0cc !important; font-size: 0.8rem !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.25rem 0 !important; }

.sb-brand {
    display: flex; align-items: center; gap: 0.875rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1.75rem;
}
.sb-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #3366ff, #7c3aed);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; flex-shrink: 0;
}
.sb-title { font-size: 0.95rem; font-weight: 700; color: #f0f2f8; line-height: 1.2; }
.sb-sub   { font-size: 0.68rem; color: #6b7699; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }
.sb-section {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #4a5380 !important;
    margin: 1.5rem 0 0.6rem; display: block;
}

/* Main layout */
.main .block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* Page header */
.page-header {
    display: flex; align-items: center; justify-content: space-between;
    background: var(--white); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem 2rem;
    margin-bottom: 1.5rem; box-shadow: var(--shadow);
}
.page-title {
    font-size: 1.6rem !important; font-weight: 800 !important;
    color: var(--text) !important; letter-spacing: -0.03em; line-height: 1.15;
}
.page-title em { font-family: var(--font-serif); font-style: italic; color: var(--blue); }
.page-sub { font-size: 0.85rem !important; color: var(--text-3) !important; margin-top: 0.25rem; }
.live-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: var(--green-light); border: 1px solid rgba(0,184,148,0.2);
    border-radius: 100px; padding: 0.35rem 1rem;
    font-size: 0.72rem; font-weight: 700; color: var(--green);
    letter-spacing: 0.04em; text-transform: uppercase;
}
.live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* KPI grid */
.kpi-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi {
    background: var(--white); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow); position: relative; overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.kpi-bar { position: absolute; top:0; left:0; right:0; height:3px; border-radius:14px 14px 0 0; }
.kpi-icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; margin-bottom:0.875rem; }
.kpi-label { font-size:0.68rem; font-weight:700; letter-spacing:0.09em; text-transform:uppercase; color:var(--text-3); margin-bottom:0.3rem; }
.kpi-value { font-size:1.75rem; font-weight:800; color:var(--text); letter-spacing:-0.04em; line-height:1; }
.kpi-note  { font-size:0.72rem; color:var(--text-3); margin-top:0.35rem; font-weight:500; }

/* Chart card */
.chart-card {
    background: var(--white); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem;
    box-shadow: var(--shadow); margin-bottom: 1.25rem;
}
.chart-card-hd {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1rem; border-bottom: 1px solid var(--border); margin-bottom: 0.25rem;
}
.chart-card-title { font-size:0.95rem; font-weight:700; color:var(--text); letter-spacing:-0.01em; }
.chart-badge {
    font-size:0.64rem; font-weight:700; letter-spacing:0.07em;
    text-transform:uppercase; color:var(--blue);
    background:var(--blue-light); border-radius:6px; padding:0.2rem 0.6rem;
}

/* Multiselect */
[data-baseweb="select"] { background:rgba(255,255,255,0.05) !important; border-color:rgba(255,255,255,0.1) !important; border-radius:8px !important; }
[data-baseweb="tag"]    { background:rgba(51,102,255,0.25) !important; color:#8ab0ff !important; border-radius:5px !important; border:none !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.04) !important;
    border:1.5px dashed rgba(255,255,255,0.12) !important;
    border-radius:10px !important;
}

/* Download buttons */
.stDownloadButton button {
    background:var(--blue) !important; color:white !important; border:none !important;
    border-radius:10px !important; font-family:var(--font) !important;
    font-weight:600 !important; font-size:0.85rem !important;
    padding:0.6rem 1.25rem !important; width:100%; transition:all 0.2s !important;
}
.stDownloadButton button:hover {
    background:#254de0 !important; box-shadow:0 4px 12px rgba(51,102,255,0.3) !important;
    transform:translateY(-1px) !important;
}

/* Dataframe */
.stDataFrame { border-radius:10px !important; border:1px solid var(--border) !important; overflow:hidden !important; }

/* Alerts */
.stSuccess,.stWarning,.stError,.stInfo { border-radius:10px !important; font-family:var(--font) !important; font-size:0.85rem !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }

/* Scrollbar */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:#d1d5e0; border-radius:3px; }

/* Empty state */
.empty-wrap {
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    text-align:center; background:var(--white); border:1px solid var(--border);
    border-radius:20px; padding:5rem 2rem; box-shadow:var(--shadow);
}
.empty-icon { font-size:3rem; margin-bottom:1rem; }
.empty-title { font-size:1.4rem !important; font-weight:800 !important; color:var(--text) !important; letter-spacing:-0.03em; margin-bottom:0.5rem; }
.empty-body  { font-size:0.875rem !important; color:var(--text-3) !important; max-width:360px; line-height:1.7; }
.fmt-chips   { display:flex; gap:0.5rem; justify-content:center; margin-top:1.25rem; }
.fmt-chip    { font-size:0.68rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; color:var(--text-3); background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:0.25rem 0.65rem; }
.step-grid   { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-top:2rem; max-width:580px; }
.step        { background:var(--bg); border:1px solid var(--border); border-radius:12px; padding:1rem; text-align:left; }
.step-num    { font-size:0.63rem; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:var(--blue); background:var(--blue-light); border-radius:5px; padding:0.15rem 0.5rem; display:inline-block; margin-bottom:0.5rem; }
.step-text   { font-size:0.78rem; color:var(--text-2); font-weight:500; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# ── Chart helpers ──
PALETTE = ["#3366ff","#00b894","#f59e0b","#ef4444","#7c3aed","#06b6d4","#f97316"]

def base_layout(**kw):
    """Build a fresh plotly layout dict each call — no shared dict to conflict."""
    d = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#8b91aa", size=11),
        margin=dict(t=16, l=8, r=8, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#4a5173", size=11)),
        xaxis=dict(showgrid=False, color="#8b91aa", linecolor="#e4e8f0", tickcolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=True, gridcolor="#f0f2f8", color="#8b91aa", linecolor="rgba(0,0,0,0)"),
    )
    # Allow callers to override individual axis keys safely
    for k, v in kw.items():
        if k in ("xaxis","yaxis") and isinstance(v, dict):
            d[k] = {**d[k], **v}   # merge instead of replace
        else:
            d[k] = v
    return d

def chart_card_start(title, badge):
    return f"""<div class='chart-card'>
    <div class='chart-card-hd'>
        <span class='chart-card-title'>{title}</span>
        <span class='chart-badge'>{badge}</span>
    </div>"""

def kpi_html(icon, label, value, note, bar_color, icon_bg):
    return f"""<div class='kpi'>
        <div class='kpi-bar' style='background:{bar_color}'></div>
        <div class='kpi-icon' style='background:{icon_bg}'>{icon}</div>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-note'>{note}</div>
    </div>"""

def smart_money(v):
    if v >= 1e7:  return f"₹{v/1e7:.1f}Cr"
    if v >= 1e5:  return f"₹{v/1e5:.0f}L"
    return f"₹{v:,.0f}"

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
    <div class='sb-brand'>
        <div class='sb-logo'>⚡</div>
        <div>
            <div class='sb-title'>EV Analytics</div>
            <div class='sb-sub'>India Platform</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<span class='sb-section'>Data Source</span>", unsafe_allow_html=True)
    file = st.file_uploader("Upload Dataset", ["csv","xlsx"], label_visibility="collapsed")

    st.markdown("<span class='sb-section'>Filters</span>", unsafe_allow_html=True)
    _seg = st.multiselect("Segment", [], key="seg0")
    _mfr = st.multiselect("Manufacturer", [], key="mfr0")

    st.markdown("---")
    st.markdown("""<div style='font-size:0.7rem;color:#3a4260;text-align:center;line-height:1.8'>
        EV Analytics Platform v2.0<br>Powered by Streamlit & Plotly</div>""", unsafe_allow_html=True)

# ── PAGE HEADER ──
st.markdown("""
<div class='page-header'>
    <div>
        <div class='page-title'>Electric Vehicle <em>Analytics</em></div>
        <div class='page-sub'>Comprehensive intelligence for India's EV market ecosystem</div>
    </div>
    <div class='live-badge'><div class='live-dot'></div> Live Dashboard</div>
</div>""", unsafe_allow_html=True)

# ── MAIN ──
if file:
    try:
        df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
        df = process_data(df)

        # Live sidebar filters
        with st.sidebar:
            st.markdown("<span class='sb-section'>Filters</span>", unsafe_allow_html=True)
            seg_sel = st.multiselect("Segment", sorted(df["Segment"].unique()),
                                     default=list(df["Segment"].unique()), key="seg1")
            mfr_sel = st.multiselect("Manufacturer", sorted(df["Manufacturer"].unique()),
                                     default=list(df["Manufacturer"].unique()), key="mfr1")
            st.markdown("---")
            st.markdown("""<div style='font-size:0.7rem;color:#3a4260;text-align:center;line-height:1.8'>
                EV Analytics Platform v2.0<br>Powered by Streamlit & Plotly</div>""", unsafe_allow_html=True)

        fdf = df[df["Segment"].isin(seg_sel) & df["Manufacturer"].isin(mfr_sel)]

        # ── KPI CARDS ──
        rev   = fdf["RevenueINR"].sum()
        prof  = fdf["ProfitINR"].sum()
        bat   = fdf["BatterykWh"].mean()
        rng   = fdf["Rangekm"].mean()
        marg  = (prof / rev * 100) if rev > 0 else 0

        st.markdown(
            "<div class='kpi-row'>" +
            kpi_html("🚗","Total Vehicles", f"{len(fdf):,}",
                     f"{fdf['Segment'].nunique()} segments · {fdf['Manufacturer'].nunique()} brands",
                     "#3366ff","#eef1ff") +
            kpi_html("💹","Total Revenue", smart_money(rev),
                     f"₹{rev:,.0f}","#7c3aed","#f3f0ff") +
            kpi_html("💰","Net Profit", smart_money(prof),
                     f"{marg:.1f}% profit margin","#00b894","#e6f9f5") +
            kpi_html("🔋","Avg Battery", f"{bat:.0f} kWh",
                     f"≈ {rng:.0f} km avg range","#f59e0b","#fef3e2") +
            "</div>",
            unsafe_allow_html=True
        )

        # ── CHART 1: Revenue by Segment (full width) ──
        st.markdown(chart_card_start("Revenue Distribution by Segment","Bar Chart"), unsafe_allow_html=True)
        seg_rev = fdf.groupby("Segment")["RevenueINR"].sum().reset_index().sort_values("RevenueINR", ascending=False)
        fig1 = px.bar(seg_rev, x="Segment", y="RevenueINR", color="Segment",
                      text="RevenueINR", color_discrete_sequence=PALETTE)
        fig1.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside",
                           textfont=dict(size=11, color="#4a5173"), marker_line_width=0, width=0.5)
        fig1.update_layout(**base_layout(showlegend=False, height=360))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── CHARTS ROW 2 ──
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(chart_card_start("Battery Capacity vs Range","Scatter Plot"), unsafe_allow_html=True)
            hov = ["Manufacturer","Model"] if "Model" in fdf.columns else ["Manufacturer"]
            fig2 = px.scatter(fdf, x="BatterykWh", y="Rangekm", size="RevenueINR",
                              color="Segment", hover_data=hov,
                              labels={"BatterykWh":"Battery (kWh)","Rangekm":"Range (km)"},
                              color_discrete_sequence=PALETTE)
            fig2.update_traces(marker=dict(line=dict(width=0), opacity=0.8))
            fig2.update_layout(**base_layout(height=360))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown(chart_card_start("Top 10 Manufacturers by Profit","Ranked Bar"), unsafe_allow_html=True)
            top10 = (fdf.groupby("Manufacturer")["ProfitINR"].sum()
                       .sort_values(ascending=False).head(10).reset_index())
            fig3 = px.bar(top10, x="Manufacturer", y="ProfitINR", text="ProfitINR",
                          color="ProfitINR",
                          color_continuous_scale=["#c7d0ff","#3366ff"])
            fig3.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside",
                               textfont=dict(size=10, color="#4a5173"), marker_line_width=0, width=0.5)
            # merge xaxis override safely via base_layout
            fig3.update_layout(**base_layout(
                showlegend=False, height=360, coloraxis_showscale=False,
                xaxis={"tickangle":-40}
            ))
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── CHARTS ROW 3 ──
        c3, c4, c5 = st.columns(3, gap="medium")
        with c3:
            st.markdown(chart_card_start("Usage Type Split","Donut Chart"), unsafe_allow_html=True)
            if "UsageType" in fdf.columns:
                usage = fdf.groupby("UsageType").size().reset_index(name="Count")
                fig4  = px.pie(usage, values="Count", names="UsageType",
                               color_discrete_sequence=PALETTE, hole=0.6)
                fig4.update_traces(textinfo="percent+label", textfont_size=11,
                                   marker=dict(line=dict(color="#ffffff", width=2)))
                fig4.update_layout(**base_layout(showlegend=False, height=300))
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
                fig5.update_layout(**base_layout(showlegend=False, height=300))
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
                fig6.update_layout(**base_layout(showlegend=False, height=300))
                st.plotly_chart(fig6, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── RAW DATA ──
        st.markdown(chart_card_start(f"Raw Dataset",f"{len(fdf):,} rows · {len(fdf.columns)} columns"), unsafe_allow_html=True)
        st.dataframe(fdf.reset_index(drop=True), height=360, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── DOWNLOADS ──
        st.markdown("<br>", unsafe_allow_html=True)
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            st.download_button("⬇  Download Filtered Data (CSV)",
                               fdf.to_csv(index=False).encode(), "ev_filtered_data.csv",
                               "text/csv", use_container_width=True)
        with d2:
            summary = pd.DataFrame({
                "Metric":["Total Vehicles","Total Revenue (₹)","Total Profit (₹)","Avg Battery (kWh)","Avg Range (km)"],
                "Value": [len(fdf), f"₹{rev:,.0f}", f"₹{prof:,.0f}", f"{bat:.1f}", f"{rng:.1f}"]
            })
            st.download_button("📊  Download Summary Report (CSV)",
                               summary.to_csv(index=False).encode(), "ev_summary.csv",
                               "text/csv", use_container_width=True)

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
        <div class='empty-icon'>📊</div>
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
                <div class='step-text'>Use segment & manufacturer filters to focus your view</div>
            </div>
            <div class='step'>
                <span class='step-num'>Step 3</span>
                <div class='step-text'>Explore charts and download filtered reports instantly</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
