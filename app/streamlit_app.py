# ---------- PYTHON PATH FIX ----------
import sys
import os

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
    page_title="EV Analytics — India",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- TRY ETL IMPORTS ----------
try:
    from elt.column_mapper import map_columns
    from elt.data_cleaner import clean_data
    HAS_ETL = True
except ImportError:
    HAS_ETL = False

# ---------- PREMIUM CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Root ── */
*, *::before, *::after { box-sizing: border-box; }

:root {
    --bg:        #06080d;
    --surface:   #0d1117;
    --card:      #111722;
    --border:    rgba(255,255,255,0.07);
    --accent:    #00e5ff;
    --accent2:   #7c3aed;
    --green:     #22d3a5;
    --red:       #f43f5e;
    --amber:     #fbbf24;
    --text:      #f0f4ff;
    --muted:     #6b7ca3;
    --font-head: 'Syne', sans-serif;
    --font-body: 'DM Sans', sans-serif;
}

/* ── App Background ── */
.stApp {
    background: var(--bg) !important;
    font-family: var(--font-body) !important;
}

/* Noise grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] > div {
    padding: 2rem 1.5rem !important;
}

/* Sidebar brand */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.75rem;
}

.sidebar-brand .bolt {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 0 18px rgba(0,229,255,0.35);
}

.sidebar-brand .brand-text {
    font-family: var(--font-head);
    font-size: 1rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.sidebar-brand .brand-sub {
    font-size: 0.7rem;
    color: var(--muted);
    font-weight: 400;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Section labels */
.section-label {
    font-family: var(--font-head);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.5rem 0 0.6rem;
}

/* ── Main Header ── */
.dash-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 2rem 0 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

.dash-title {
    font-family: var(--font-head);
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0;
}

.dash-title span {
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.dash-sub {
    color: var(--muted);
    font-size: 0.9rem;
    margin: 0.4rem 0 0;
    font-weight: 400;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(34,211,165,0.1);
    border: 1px solid rgba(34,211,165,0.25);
    border-radius: 100px;
    padding: 0.3rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--green);
    letter-spacing: 0.03em;
}

.status-pill::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Metric Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 16px 16px 0 0;
}

.kpi-card.cyan::before  { background: linear-gradient(90deg, var(--accent), transparent); }
.kpi-card.violet::before { background: linear-gradient(90deg, var(--accent2), transparent); }
.kpi-card.green::before  { background: linear-gradient(90deg, var(--green), transparent); }
.kpi-card.amber::before  { background: linear-gradient(90deg, var(--amber), transparent); }

.kpi-card:hover {
    border-color: rgba(255,255,255,0.14);
    transform: translateY(-3px);
}

.kpi-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.75rem;
}

.kpi-value {
    font-family: var(--font-head);
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.04em;
    line-height: 1;
}

.kpi-icon {
    position: absolute;
    top: 1.25rem; right: 1.25rem;
    font-size: 1.4rem;
    opacity: 0.2;
}

.kpi-delta {
    font-size: 0.72rem;
    color: var(--green);
    margin-top: 0.4rem;
    font-weight: 500;
}

/* ── Chart Wrapper ── */
.chart-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}

.chart-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
}

.chart-head-title {
    font-family: var(--font-head);
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.02em;
}

.chart-head-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 6px;
    padding: 0.2rem 0.55rem;
}

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    background: rgba(0,229,255,0.03) !important;
    border: 1.5px dashed rgba(0,229,255,0.25) !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
}

[data-testid="stFileUploader"] label {
    color: var(--muted) !important;
}

/* ── Multiselect ── */
[data-baseweb="select"] {
    background-color: #161d2e !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}

[data-baseweb="tag"] {
    background-color: rgba(0,229,255,0.15) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(0,229,255,0.3) !important;
    border-radius: 6px !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ── Download buttons ── */
.stDownloadButton button {
    background: transparent !important;
    border: 1px solid rgba(0,229,255,0.3) !important;
    color: var(--accent) !important;
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.25rem !important;
    transition: all 0.2s !important;
    width: 100%;
}

.stDownloadButton button:hover {
    background: rgba(0,229,255,0.08) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 16px rgba(0,229,255,0.15) !important;
}

/* ── Alerts ── */
.stSuccess, .stWarning, .stError, .stInfo {
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
}

/* ── Global text ── */
h1, h2, h3, h4, p, label, .stMarkdown {
    font-family: var(--font-body) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    margin: 1rem 0;
}

.empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1.25rem;
    filter: drop-shadow(0 0 24px rgba(0,229,255,0.3));
}

.empty-title {
    font-family: var(--font-head) !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
    margin-bottom: 0.5rem;
}

.empty-sub {
    color: var(--muted) !important;
    font-size: 0.9rem !important;
    max-width: 380px;
    margin: 0 auto;
    line-height: 1.6;
}

.format-chips {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1.5rem;
}

.format-chip {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ---------- PLOTLY THEME ----------
PLOT_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans, sans-serif', color='#6b7ca3', size=12),
    xaxis=dict(showgrid=False, color='#6b7ca3', linecolor='rgba(255,255,255,0.07)', tickcolor='rgba(0,0,0,0)'),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#6b7ca3', linecolor='rgba(0,0,0,0)', tickcolor='rgba(0,0,0,0)'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#6b7ca3')),
    margin=dict(t=10, l=10, r=10, b=10),
)

PALETTE = ["#00e5ff", "#7c3aed", "#22d3a5", "#f43f5e", "#fbbf24", "#818cf8", "#fb923c"]

# ---------- HELPERS ----------
def process_data(df):
    if HAS_ETL:
        df = map_columns(df)
        df = clean_data(df)
    else:
        mapping = {
            'Vehicle_ID': 'VehicleID', 'Battery_kWh': 'BatterykWh',
            'Range_km': 'Rangekm', 'Ex_Showroom_Price_INR': 'PriceINR',
            'Avg_Charging_Time_Hours': 'ChargingTimeHours',
            'Energy_Consumed_kWh': 'EnergykWh', 'Operating_Cost_INR': 'OperatingCostINR',
            'Revenue_INR': 'RevenueINR', 'Usage_Type': 'UsageType',
            'Customer_Location_Type': 'LocationType'
        }
        df = df.rename(columns=mapping)
        if 'ProfitINR' not in df.columns:
            df['ProfitINR'] = df['RevenueINR'] - df['OperatingCostINR']
        df = df.dropna(subset=['Segment', 'Manufacturer'])
    return df

def fmt_crore(val):
    if val >= 1e7:
        return f"₹{val/1e7:.1f}Cr"
    return f"₹{val/1e5:.0f}L"

def chart_box(title, badge=None):
    badge_html = f"<span class='chart-head-badge'>{badge}</span>" if badge else ""
    return f"""
    <div class='chart-wrap'>
        <div class='chart-head'>
            <span class='chart-head-title'>{title}</span>
            {badge_html}
        </div>
    """

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("""
        <div class='sidebar-brand'>
            <div class='bolt'>⚡</div>
            <div>
                <div class='brand-text'>EV Analytics</div>
                <div class='brand-sub'>India Dashboard</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Data Source</div>", unsafe_allow_html=True)
    file = st.file_uploader("Upload EV Dataset", ["csv", "xlsx"], label_visibility="collapsed")

    st.markdown("<div class='section-label'>Filters</div>", unsafe_allow_html=True)
    segment_filter = st.multiselect("Segment", [], key="seg_empty")
    manufacturer_filter = st.multiselect("Manufacturer", [], key="mfr_empty")

    st.markdown("---")
    st.markdown(f"""
        <div style='font-size:0.72rem; color:#3d4f72; text-align:center; line-height:1.6;'>
            EV Analytics Platform<br>Built with Streamlit &amp; Plotly
        </div>
    """, unsafe_allow_html=True)

# ---------- MAIN HEADER ----------
st.markdown("""
    <div class='dash-header'>
        <div>
            <h1 class='dash-title'>Electric Vehicle <span>Intelligence</span></h1>
            <p class='dash-sub'>Comprehensive analytics for India's EV ecosystem</p>
        </div>
        <div class='status-pill'>Live Dashboard</div>
    </div>
""", unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
if file:
    try:
        df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
        df = process_data(df)

        # ── Dynamic sidebar filters ──
        with st.sidebar:
            st.markdown("<div class='section-label'>Filters</div>", unsafe_allow_html=True)
            segment_filter = st.multiselect(
                "Segment",
                sorted(df["Segment"].unique()),
                default=list(df["Segment"].unique()),
                key="seg_live"
            )
            manufacturer_filter = st.multiselect(
                "Manufacturer",
                sorted(df["Manufacturer"].unique()),
                default=list(df["Manufacturer"].unique()),
                key="mfr_live"
            )
            st.markdown("---")
            st.markdown(f"""
                <div style='font-size:0.72rem; color:#3d4f72; text-align:center; line-height:1.6;'>
                    EV Analytics Platform<br>Built with Streamlit &amp; Plotly
                </div>
            """, unsafe_allow_html=True)

        fdf = df[df["Segment"].isin(segment_filter) & df["Manufacturer"].isin(manufacturer_filter)]

        # ── KPI Cards ──
        total_rev = fdf['RevenueINR'].sum()
        total_profit = fdf['ProfitINR'].sum()
        avg_battery = fdf['BatterykWh'].mean()
        avg_range = fdf['Rangekm'].mean()

        st.markdown(f"""
        <div class='kpi-grid'>
            <div class='kpi-card cyan'>
                <div class='kpi-icon'>🚗</div>
                <div class='kpi-label'>Total Vehicles</div>
                <div class='kpi-value'>{len(fdf):,}</div>
                <div class='kpi-delta'>↑ across {fdf["Segment"].nunique()} segments</div>
            </div>
            <div class='kpi-card violet'>
                <div class='kpi-icon'>💹</div>
                <div class='kpi-label'>Total Revenue</div>
                <div class='kpi-value'>{fmt_crore(total_rev)}</div>
                <div class='kpi-delta'>₹{total_rev:,.0f}</div>
            </div>
            <div class='kpi-card green'>
                <div class='kpi-icon'>💰</div>
                <div class='kpi-label'>Net Profit</div>
                <div class='kpi-value'>{fmt_crore(total_profit)}</div>
                <div class='kpi-delta'>{(total_profit/total_rev*100):.1f}% margin</div>
            </div>
            <div class='kpi-card amber'>
                <div class='kpi-icon'>🔋</div>
                <div class='kpi-label'>Avg Battery</div>
                <div class='kpi-value'>{avg_battery:.0f}<span style='font-size:1rem;font-weight:400;color:#6b7ca3'> kWh</span></div>
                <div class='kpi-delta'>~{avg_range:.0f} km avg range</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chart 1: Revenue by Segment (full width) ──
        st.markdown(chart_box("Revenue Distribution by Segment", "Bar Chart") + "</div>", unsafe_allow_html=True)
        seg_rev = fdf.groupby("Segment")["RevenueINR"].sum().reset_index().sort_values('RevenueINR', ascending=False)
        fig1 = px.bar(
            seg_rev, x="Segment", y="RevenueINR",
            color="Segment", text="RevenueINR",
            color_discrete_sequence=PALETTE
        )
        fig1.update_traces(
            texttemplate="₹%{text:,.0f}", textposition="outside",
            textfont=dict(size=11, color='#6b7ca3'),
            marker_line_width=0,
            width=0.55
        )
        fig1.update_layout(**PLOT_LAYOUT, showlegend=False, height=360)
        st.plotly_chart(fig1, use_container_width=True)

        # ── Charts Row 2 ──
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(chart_box("Battery Capacity vs Range", "Scatter") + "</div>", unsafe_allow_html=True)
            fig2 = px.scatter(
                fdf, x="BatterykWh", y="Rangekm",
                size="RevenueINR", color="Segment",
                hover_data=["Manufacturer", "Model"] if "Model" in fdf.columns else ["Manufacturer"],
                labels={"BatterykWh": "Battery (kWh)", "Rangekm": "Range (km)"},
                color_discrete_sequence=PALETTE
            )
            fig2.update_traces(marker=dict(line=dict(width=0), opacity=0.85))
            fig2.update_layout(**PLOT_LAYOUT, height=360)
            st.plotly_chart(fig2, use_container_width=True)

        with c2:
            st.markdown(chart_box("Top 10 Manufacturers by Profit", "Bar") + "</div>", unsafe_allow_html=True)
            top_mfr = fdf.groupby("Manufacturer")["ProfitINR"].sum().sort_values(ascending=False).head(10).reset_index()
            fig3 = px.bar(
                top_mfr, x="Manufacturer", y="ProfitINR",
                text="ProfitINR", color="ProfitINR",
                color_continuous_scale=["#0d1117", "#00e5ff"]
            )
            fig3.update_traces(
                texttemplate="₹%{text:,.0f}", textposition="outside",
                textfont=dict(size=10, color='#6b7ca3'),
                marker_line_width=0, width=0.55
            )
            fig3.update_layout(**PLOT_LAYOUT, showlegend=False, height=360,
                               xaxis=dict(tickangle=-40, showgrid=False, color='#6b7ca3', linecolor='rgba(255,255,255,0.07)'),
                               coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)

        # ── Charts Row 3 ──
        c3, c4, c5 = st.columns(3)

        with c3:
            st.markdown(chart_box("Usage Type Split", "Donut") + "</div>", unsafe_allow_html=True)
            if 'UsageType' in fdf.columns:
                usage = fdf.groupby('UsageType').size().reset_index(name='Count')
                fig4 = px.pie(usage, values='Count', names='UsageType',
                              color_discrete_sequence=PALETTE, hole=0.58)
                fig4.update_traces(textinfo='percent+label', textfont_size=11,
                                   marker=dict(line=dict(color='#06080d', width=2)))
                fig4.update_layout(**PLOT_LAYOUT, showlegend=False, height=300,
                                   margin=dict(t=10, l=10, r=10, b=10))
                st.plotly_chart(fig4, use_container_width=True)

        with c4:
            st.markdown(chart_box("Avg Charging Time", "By Segment") + "</div>", unsafe_allow_html=True)
            if 'ChargingTimeHours' in fdf.columns:
                chg = fdf.groupby('Segment')['ChargingTimeHours'].mean().reset_index()
                fig5 = px.bar(chg, x='Segment', y='ChargingTimeHours',
                              color='Segment', labels={'ChargingTimeHours': 'Hours'},
                              color_discrete_sequence=PALETTE)
                fig5.update_traces(marker_line_width=0, width=0.55)
                fig5.update_layout(**PLOT_LAYOUT, showlegend=False, height=300)
                st.plotly_chart(fig5, use_container_width=True)

        with c5:
            st.markdown(chart_box("Energy Consumption", "By Segment") + "</div>", unsafe_allow_html=True)
            if 'EnergykWh' in fdf.columns:
                energy = fdf.groupby('Segment')['EnergykWh'].mean().reset_index()
                fig6 = px.bar(energy, x='Segment', y='EnergykWh',
                              color='Segment', labels={'EnergykWh': 'kWh'},
                              color_discrete_sequence=PALETTE[::-1])
                fig6.update_traces(marker_line_width=0, width=0.55)
                fig6.update_layout(**PLOT_LAYOUT, showlegend=False, height=300)
                st.plotly_chart(fig6, use_container_width=True)

        # ── Raw Data ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(chart_box("Raw Dataset", f"{len(fdf):,} rows") + "</div>", unsafe_allow_html=True)
        st.dataframe(fdf.reset_index(drop=True), height=360, use_container_width=True)

        # ── Downloads ──
        st.markdown("<br>", unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            csv = fdf.to_csv(index=False).encode('utf-8')
            st.download_button("⬇ Download Filtered Data (CSV)", csv, "ev_filtered_data.csv", "text/csv", use_container_width=True)
        with d2:
            summary = pd.DataFrame({
                'Metric': ['Total Vehicles','Total Revenue (₹)','Total Profit (₹)','Avg Battery (kWh)','Avg Range (km)'],
                'Value': [
                    len(fdf),
                    f"₹{fdf['RevenueINR'].sum():,.0f}",
                    f"₹{fdf['ProfitINR'].sum():,.0f}",
                    f"{fdf['BatterykWh'].mean():.1f}",
                    f"{fdf['Rangekm'].mean():.1f}"
                ]
            })
            st.download_button("📊 Download Summary Report (CSV)", summary.to_csv(index=False).encode('utf-8'),
                               "ev_summary.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.code("""Required columns:
- Vehicle_ID / VehicleID        - Manufacturer
- Model                         - Segment
- Battery_kWh / BatterykWh     - Range_km / Rangekm
- Revenue_INR / RevenueINR      - Operating_Cost_INR / OperatingCostINR""")

else:
    st.markdown("""
    <div class='empty-state'>
        <div class='empty-icon'>⚡</div>
        <h2 class='empty-title'>Upload Your EV Dataset</h2>
        <p class='empty-sub'>
            Drop in a CSV or Excel file to unlock real-time analytics, 
            visual breakdowns, and downloadable reports.
        </p>
        <div class='format-chips'>
            <span class='format-chip'>.csv</span>
            <span class='format-chip'>.xlsx</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
