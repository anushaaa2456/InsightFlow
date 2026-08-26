"""Reusable, human-designed Streamlit UI components for InsightFlow:
Refined, organic SaaS layout with Dark Obsidian background & Purple typography accents.
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import textwrap

def inject_custom_css():
    """Inject human-crafted SaaS CSS with asymmetric hierarchy and refined typography."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,300;0,400;0,700;0,900;1,300;1,400;1,700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Outlined|Material+Icons+Round|Material+Symbols+Rounded|Material+Symbols+Outlined');

    /* Global Typography & Canvas - Scoped to avoid touching icons */
    html, body, .stApp {
        color: #F8FAFC;
        font-size: 14.5px;
        -webkit-font-smoothing: antialiased;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li,
    h1, h2, h3, h4, h5, h6, p, label, input, textarea, select {
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #0B0F17 !important;
    }

    /* Natural Container Spacing */
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.75rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Dark Header & Native Controls */
    header[data-testid="stHeader"],
    .stAppHeader,
    div[data-testid="stHeader"] {
        background: #0B0F17 !important;
        background-color: #0B0F17 !important;
        color: #F8FAFC !important;
    }

    /* Premium Glassmorphic Sidebar Toggle & Collapse Controls */
    div[data-testid="stSidebarCollapsedControl"],
    div[data-testid="collapsedControl"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 999999 !important;
        padding-left: 10px !important;
        padding-top: 10px !important;
    }

    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarCollapsedControl"] button,
    div[data-testid="collapsedControl"] button,
    button[aria-label*="sidebar" i],
    button[aria-label*="Sidebar" i] {
        background: linear-gradient(135deg, rgba(76, 29, 149, 0.45) 0%, rgba(15, 23, 42, 0.65) 100%) !important;
        backdrop-filter: blur(18px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
        border: 1.5px solid rgba(192, 132, 252, 0.4) !important;
        border-top: 1.5px solid rgba(255, 255, 255, 0.55) !important;
        border-radius: 10px !important;
        color: #C084FC !important;
        width: 38px !important;
        height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.4), 0 0 16px rgba(168, 85, 247, 0.35), inset 0 1px 2px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        z-index: 999999 !important;
    }

    button[data-testid="stSidebarCollapseButton"]:hover,
    div[data-testid="stSidebarCollapsedControl"] button:hover,
    div[data-testid="collapsedControl"] button:hover,
    button[aria-label*="sidebar" i]:hover,
    button[aria-label*="Sidebar" i]:hover {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.8) 0%, rgba(124, 58, 237, 0.9) 100%) !important;
        border-color: rgba(255, 255, 255, 0.7) !important;
        color: #FFFFFF !important;
        box-shadow: 0 12px 32px 0 rgba(0, 0, 0, 0.5), 0 0 28px rgba(168, 85, 247, 0.75), inset 0 1px 3px rgba(255, 255, 255, 0.6) !important;
        transform: translateY(-2px) scale(1.06) !important;
    }

    button[data-testid="stSidebarCollapseButton"]:active,
    div[data-testid="stSidebarCollapsedControl"] button:active,
    div[data-testid="collapsedControl"] button:active {
        transform: scale(0.96) !important;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.6), 0 0 12px rgba(168, 85, 247, 0.4) !important;
    }

    button[data-testid="stSidebarCollapseButton"] svg,
    div[data-testid="stSidebarCollapsedControl"] button svg,
    div[data-testid="collapsedControl"] button svg,
    button[data-testid="stSidebarCollapseButton"] span,
    div[data-testid="stSidebarCollapsedControl"] button span,
    div[data-testid="collapsedControl"] button span {
        color: #E9D5FF !important;
        fill: currentColor !important;
        font-size: 20px !important;
        pointer-events: none !important;
        filter: drop-shadow(0 0 6px rgba(192, 132, 252, 0.6)) !important;
        transition: all 0.2s ease !important;
    }

    button[data-testid="stSidebarCollapseButton"]:hover svg,
    div[data-testid="stSidebarCollapsedControl"] button:hover svg,
    div[data-testid="collapsedControl"] button:hover svg,
    button[data-testid="stSidebarCollapseButton"]:hover span,
    div[data-testid="stSidebarCollapsedControl"] button:hover span,
    div[data-testid="collapsedControl"] button:hover span {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        filter: drop-shadow(0 0 10px #FFFFFF) !important;
    }

    /* Subtle Entry Animation */
    @keyframes fadeInUpSubtle {
        0% {
            opacity: 0;
            transform: translateY(3px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animated-entrance {
        animation: fadeInUpSubtle 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Header Bar */
    .app-header {
        background: linear-gradient(180deg, rgba(22, 28, 48, 0.85) 0%, rgba(15, 23, 42, 0.75) 100%);
        border: 1px solid rgba(168, 85, 247, 0.22);
        border-radius: 10px;
        padding: 16px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .header-title-group h1 {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .header-title-group p {
        color: #C084FC;
        font-size: 13px;
        margin: 3px 0 0 0;
        font-weight: 400;
    }

    .persona-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 13px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(168, 85, 247, 0.18);
        border: 1px solid rgba(168, 85, 247, 0.5);
        color: #F8FAFC;
    }

    .persona-badge .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
        background-color: #C084FC;
    }

    /* Asymmetric KPI Metric Section */
    .kpi-layout-grid {
        display: grid;
        grid-template-columns: 1.2fr 1fr 1fr 1fr;
        gap: 14px;
        margin-bottom: 22px;
    }

    @media (max-width: 1050px) {
        .kpi-layout-grid {
            grid-template-columns: 1fr 1fr;
        }
    }

    @media (max-width: 600px) {
        .kpi-layout-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Hero Metric Card */
    .kpi-card-hero {
        background: linear-gradient(145deg, rgba(28, 32, 60, 0.9) 0%, rgba(17, 24, 39, 0.85) 100%);
        border: 1.5px solid rgba(168, 85, 247, 0.5);
        border-radius: 10px;
        padding: 18px 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 132px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        transition: all 0.18s ease-out;
    }

    .kpi-card-hero:hover {
        border-color: #C084FC;
        transform: translateY(-1px);
        box-shadow: 0 6px 24px -2px rgba(0, 0, 0, 0.45);
    }

    /* Secondary Metric Cards */
    .kpi-card-secondary {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 132px;
        transition: all 0.18s ease-out;
    }

    .kpi-card-secondary:hover {
        background: rgba(24, 32, 54, 0.88);
        border-color: rgba(168, 85, 247, 0.35);
        transform: translateY(-1px);
    }

    .kpi-meta-tag {
        font-size: 11px;
        font-weight: 700;
        color: #C084FC;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .kpi-hero-num {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 6px;
    }

    .kpi-sec-num {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        line-height: 1.15;
        margin-bottom: 4px;
    }

    .kpi-delta-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11.5px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        width: fit-content;
    }

    .delta-negative {
        background: rgba(244, 63, 94, 0.18);
        color: #FDA4AF;
        border: 1px solid rgba(244, 63, 94, 0.35);
    }

    .delta-positive {
        background: rgba(168, 85, 247, 0.18);
        color: #E9D5FF;
        border: 1px solid rgba(168, 85, 247, 0.4);
    }

    .delta-neutral {
        background: rgba(148, 163, 184, 0.15);
        color: #CBD5E1;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    /* Polished Tab Bar with Violet Accent */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 2px;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 9px 18px;
        border-radius: 6px 6px 0 0;
        color: #94A3B8;
        font-size: 13.5px;
        font-weight: 500;
        border: none;
        background: transparent;
        transition: all 0.15s ease-out;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC;
        background: rgba(255, 255, 255, 0.04);
    }

    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        background: rgba(168, 85, 247, 0.16) !important;
        border-bottom: 2.5px solid #A855F7 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #080C14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"] .block-container,
    div[data-testid="stSidebarContent"],
    div[data-testid="stSidebarUserContent"] {
        padding-top: 1.25rem !important;
        margin-top: 0rem !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSidebarHeader"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        height: auto !important;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #C084FC !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    div[role="radiogroup"] > label {
        background: rgba(20, 27, 44, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-left: 3px solid #A855F7 !important;
        border-radius: 7px !important;
        padding: 10px 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.15s ease-out !important;
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(28, 38, 62, 0.95) !important;
        border-color: rgba(168, 85, 247, 0.5) !important;
        transform: translateX(1px) !important;
    }

    div[role="radiogroup"] > label p,
    div[role="radiogroup"] > label div,
    div[role="radiogroup"] > label span {
        color: #FFFFFF !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
    }

    /* Evidence List Item */
    .evidence-item {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        transition: all 0.15s ease-out;
    }

    .evidence-item:hover {
        border-color: rgba(168, 85, 247, 0.4);
        background: rgba(24, 34, 56, 0.85);
    }

    .evidence-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .evidence-source-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(168, 85, 247, 0.16);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.4);
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    .evidence-meta {
        font-size: 12px;
        color: #94A3B8;
    }

    .evidence-finding {
        color: #F1F5F9;
        font-size: 13.5px;
        line-height: 1.5;
        margin: 0;
    }

    /* Editorial Executive Narrative Brief */
    .narrative-box {
        background: linear-gradient(135deg, rgba(24, 28, 52, 0.85) 0%, rgba(15, 22, 38, 0.8) 100%);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-left: 3.5px solid #A855F7;
        border-radius: 9px;
        padding: 18px 22px;
        margin-bottom: 22px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
    }

    .narrative-box h3 {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 700;
        margin: 0 0 10px 0;
        display: flex;
        align-items: center;
        gap: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
    }

    .narrative-box ul {
        margin: 0;
        padding-left: 18px;
    }

    .narrative-box li {
        margin-bottom: 6px;
        line-height: 1.55;
        color: #E2E8F0;
        font-size: 13.5px;
    }

    /* Action Cards */
    .action-primary-card {
        background: linear-gradient(180deg, rgba(26, 32, 58, 0.85) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(168, 85, 247, 0.45);
        border-radius: 9px;
        padding: 16px 18px;
        height: 100%;
    }

    .action-recovery-card {
        background: linear-gradient(180deg, rgba(32, 22, 42, 0.8) 0%, rgba(17, 24, 39, 0.75) 100%);
        border: 1px solid rgba(244, 63, 94, 0.35);
        border-radius: 9px;
        padding: 16px 18px;
        height: 100%;
    }

    /* Terminal Log */
    .terminal-log {
        background: #05080E;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 7px;
        padding: 14px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #CBD5E1;
        line-height: 1.65;
        overflow-x: auto;
    }

    .terminal-log .log-info { color: #C084FC; font-weight: 600; }
    .terminal-log .log-warn { color: #FDE047; font-weight: 600; }
    .terminal-log .log-success { color: #86EFAC; font-weight: 600; }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #9333EA, #7C3AED) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 6px !important;
        padding: 7px 16px !important;
        transition: all 0.15s ease-out !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #A855F7, #9333EA) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """
    st.markdown(textwrap.dedent(css), unsafe_allow_html=True)

def render_header(persona_name: str, persona_info: dict):
    """Render clean, human-designed header with role context."""
    html = f"""<div class="app-header animated-entrance">
<div class="header-title-group">
<h1><span style="color:#C084FC;">◈</span> InsightFlow AI <span style="font-weight:400; color:#94A3B8; font-size:16px;">/ Decision Engine</span></h1>
<p>Deterministic KPI Decomposition ➔ Grounded Causal Reasoning ➔ Role Actionability</p>
</div>
<div>
<div class="persona-badge">
<span class="status-dot"></span>
{persona_info['badge']}
</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_kpi_cards(scenario_data: dict):
    """Render asymmetric, visually prioritized KPI summary with clear visual hierarchy."""
    actual = scenario_data['actual_change'] * 100
    expected = scenario_data['expected_change'] * 100
    delta = actual - expected
    
    delta_class = "delta-negative" if delta < 0 else ("delta-positive" if delta > 0 else "delta-neutral")
    delta_icon = "↓" if delta < 0 else ("↑" if delta > 0 else "→")
    
    mat_color = "#FDA4AF" if "HIGH" in scenario_data['materiality'] else ("#FEF08A" if "MEDIUM" in scenario_data['materiality'] else "#E2E8F0")
    conf = scenario_data['confidence']
    conf_color = "#C084FC" if conf['label'] == "HIGH" else ("#FEF08A" if conf['label'] == "MEDIUM" else "#FDA4AF")
    val_color = '#FDA4AF' if actual < 0 else '#C084FC'

    html = f"""<div class="kpi-layout-grid animated-entrance">
<div class="kpi-card-hero">
<div class="kpi-meta-tag"><span>Primary Metric · {scenario_data['kpi']}</span><span>{scenario_data['entity']}</span></div>
<div class="kpi-hero-num" style="color: {val_color};">{actual:+.2f}%</div>
<div class="kpi-delta-pill {delta_class}">{delta_icon} {abs(delta):.2f}% vs expected</div>
</div>
<div class="kpi-card-secondary">
<div class="kpi-meta-tag"><span>Expected Baseline</span><span>{scenario_data['period']}</span></div>
<div class="kpi-sec-num">{expected:+.2f}%</div>
<div class="kpi-delta-pill delta-neutral">Forecast Corridor</div>
</div>
<div class="kpi-card-secondary">
<div class="kpi-meta-tag"><span>Materiality Gate</span><span>Stat. Sig</span></div>
<div class="kpi-sec-num" style="color: {mat_color};">{scenario_data['materiality']}</div>
<div style="font-size: 11.5px; color: #94A3B8; margin-top: 2px;">&gt; 3σ Volatility Gate Passed</div>
</div>
<div class="kpi-card-secondary">
<div class="kpi-meta-tag"><span>Confidence Score</span><span>Bayesian</span></div>
<div class="kpi-sec-num" style="color: {conf_color};">{conf['score']*100:.0f}% <span style="font-size: 13px; font-weight: 500; opacity: 0.85;">({conf['label']})</span></div>
<div style="font-size: 11.5px; color: #94A3B8; margin-top: 2px;">Corroborated Lineage</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_trend_chart(trend_data: list, kpi_name: str):
    """Render clean, production-grade time-series trajectory chart."""
    if not trend_data:
        st.info("No historical time-series available for this scenario.")
        return
    df = pd.DataFrame(trend_data)
    df['date'] = pd.to_datetime(df['date'])

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['expected'], 
        mode='lines', 
        name='Forecast Baseline', 
        line=dict(color='rgba(148, 163, 184, 0.65)', dash='dash', width=2),
        hoverinfo='x+y'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['actual'], 
        mode='lines+markers', 
        name='Observed Actual', 
        line=dict(color='#A855F7', width=2.5),
        marker=dict(size=6, color='#C084FC', line=dict(color='#0B0F17', width=1.5)),
        fill='tonexty',
        fillcolor='rgba(168, 85, 247, 0.08)',
        hoverinfo='x+y'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{kpi_name}</b> Trajectory vs Baseline Corridor",
            font=dict(size=14, color="#F8FAFC", family="Lato, sans-serif")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17, 24, 39, 0.35)',
        margin=dict(l=14, r=14, t=36, b=14),
        height=340,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11.5, color="#CBD5E1")
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            tickfont=dict(color='#94A3B8', size=11),
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            tickfont=dict(color='#94A3B8', size=11),
            zeroline=False
        ),
        hoverlabel=dict(
            bgcolor="#1E1B4B",
            bordercolor="#A855F7",
            font=dict(family="Inter", size=12, color="#FFFFFF")
        )
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

def render_driver_waterfall(drivers: list):
    """Render MECE waterfall decomposition chart."""
    if not drivers:
        st.markdown("""<div style="background: rgba(168, 85, 247, 0.1); border: 1px dashed rgba(168, 85, 247, 0.4); padding: 16px; border-radius: 8px; color: #E9D5FF; font-size: 13px;"><strong>[ATTRIBUTION SUSPENDED]</strong> Engine abstained from computing driver contributions due to insufficient observation history (&lt; 30 samples).</div>""", unsafe_allow_html=True)
        return

    labels = [d['driver'] for d in drivers]
    values = [d['contribution'] * 100 for d in drivers]

    fig = go.Figure(go.Waterfall(
        name="Drivers",
        orientation="v",
        measure=["relative"] * len(values),
        x=labels,
        text=[f"{v:+.2f}%" for v in values],
        textposition="outside",
        textfont=dict(size=12, color="#F8FAFC", family="Inter"),
        y=values,
        connector={"line": {"color": "rgba(255, 255, 255, 0.15)", "width": 1.5}},
        decreasing={"marker": {"color": "#F43F5E", "line": {"width": 0}}},
        increasing={"marker": {"color": "#A855F7", "line": {"width": 0}}}
    ))

    fig.update_layout(
        title=dict(
            text="<b>MECE Driver Contribution</b> (% Share of Overall Shift)",
            font=dict(size=14, color="#F8FAFC", family="Lato, sans-serif")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17, 24, 39, 0.35)',
        height=340,
        margin=dict(l=14, r=14, t=36, b=14),
        xaxis=dict(
            tickfont=dict(color='#E2E8F0', size=11),
            gridcolor='rgba(255, 255, 255, 0.04)'
        ),
        yaxis=dict(
            tickfont=dict(color='#94A3B8', size=11),
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=True,
            zerolinecolor='rgba(255, 255, 255, 0.15)'
        )
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

def render_evidence_cards(evidence_list: list):
    """Render structured evidence cards."""
    if not evidence_list:
        st.write("No evidence items available.")
        return
        
    for item in evidence_list:
        html = f"""<div class="evidence-item">
<div class="evidence-header">
<span class="evidence-source-pill">SOURCE · {item.get('source')}</span>
<span class="evidence-meta">Freshness: <strong style="color:#FFFFFF;">{item.get('freshness')}</strong> • Provenance: <em style="color:#C084FC;">{item.get('reliability')}</em></span>
</div>
<p class="evidence-finding">{item.get('finding')}</p>
</div>"""
        st.markdown(html, unsafe_allow_html=True)
