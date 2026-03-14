import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json

RESULTS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700&display=swap');

.stApp { background: #00000f !important; }
.block-container { padding: 0 24px 40px !important; max-width: 100% !important; }

/* Space background */
body, .stApp {
    background: radial-gradient(ellipse at 70% 5%, #120620 0%, #000510 35%, #00000f 100%) !important;
}

/* Context bar */
.ctx-bar {
    background: rgba(0,15,35,0.97);
    border-bottom: 1px solid rgba(74,212,232,0.2);
    padding: 10px 24px;
    display: flex; align-items: center; justify-content: space-between;
    margin: 0 -24px 20px;
    font-family: 'Exo 2', sans-serif;
}
.ctx-crumb { font-size: 12px; color: #4ad4e8; letter-spacing: 0.08em; text-transform: uppercase; }
.ctx-crumb span { color: #fff; margin: 0 6px; }
.ctx-pill {
    font-size: 11px;
    background: rgba(74,212,232,0.1);
    border: 1px solid rgba(74,212,232,0.3);
    color: #4ad4e8;
    padding: 4px 14px; border-radius: 20px; cursor: pointer;
    font-family: 'Exo 2', sans-serif;
}
.ctx-pills { display: flex; gap: 8px; }

/* Section labels */
.section-label {
    font-family: 'Exo 2', sans-serif;
    font-size: 11px; letter-spacing: 0.12em;
    text-transform: uppercase; color: #3ab8cc;
    margin: 0 0 10px;
}

/* Glassmorphism card */
.glass-card {
    background: rgba(0,15,35,0.88);
    border: 1px solid rgba(74,212,232,0.18);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
}
.glass-card-accent { border-color: rgba(74,212,232,0.45); }

/* Stat cards */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 20px;
}
.stat-card {
    background: rgba(0,15,38,0.88);
    border: 1px solid rgba(74,212,232,0.18);
    border-radius: 10px;
    padding: 16px; text-align: center;
    font-family: 'Exo 2', sans-serif;
}
.stat-val  { font-size: 26px; font-weight: 700; color: #4ad4e8; line-height: 1; }
.stat-val.warm { color: #ff6b4a; }
.stat-val.warn { color: #f0b429; }
.stat-label { font-size: 11px; color: #3ab8cc; margin-top: 4px; letter-spacing: 0.06em; }
.stat-sub   { font-size: 10px; color: #2a5a6a; margin-top: 2px; }

/* AI panel */
.ai-tag {
    display: inline-block; font-size: 10px;
    background: rgba(74,212,232,0.13);
    border: 1px solid rgba(74,212,232,0.35);
    color: #4ad4e8; padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.06em; font-family: 'Exo 2', sans-serif;
}
.ai-anomaly { font-size: 28px; font-weight: 700; color: #ff6b4a; margin: 8px 0 2px; font-family: 'Exo 2', sans-serif; }
.ai-anomaly.cool { color: #a78bfa; }
.ai-baseline { font-size: 11px; color: #3ab8cc; font-family: 'Exo 2', sans-serif; }
.ai-text    { font-size: 12px; line-height: 1.75; color: #7aaabb; font-family: 'Exo 2', sans-serif; margin-top: 10px; }
.ai-text p  { margin: 0 0 8px; }
.ai-metrics { display: flex; gap: 18px; margin: 10px 0; }
.ai-metric  { text-align: center; }
.ai-metric .val { font-size: 17px; font-weight: 700; color: #4ad4e8; font-family: 'Exo 2', sans-serif; }
.ai-metric .lbl { font-size: 10px; color: #2a5a6a; font-family: 'Exo 2', sans-serif; }

/* Chart legend dots */
.legend-row { display: flex; gap: 16px; margin-top: 8px; }
.legend-item { display: flex; align-items: center; gap: 6px;
    font-size: 10px; color: #3ab8cc; font-family: 'Exo 2', sans-serif; }
.legend-line { width: 20px; height: 2px; border-radius: 1px; }
.legend-band { width: 20px; height: 8px; border-radius: 2px; }

/* Analogue cards */
.analogue-card {
    background: rgba(0,30,60,0.5);
    border: 1px solid rgba(74,212,232,0.13);
    border-radius: 8px; padding: 10px 14px;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 8px; font-family: 'Exo 2', sans-serif;
}
.analogue-name { font-size: 13px; font-weight: 600; color: #fff; }
.analogue-meta { font-size: 11px; color: #3ab8cc; margin-top: 2px; }
.match-badge {
    font-size: 11px;
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.3);
    color: #a78bfa; padding: 3px 8px; border-radius: 20px;
}

/* RCP cards */
.rcp-header { font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    margin-bottom: 8px; font-family: 'Exo 2', sans-serif; }
.rcp-26 { color: #4ad4e8; }
.rcp-45 { color: #f0b429; }
.rcp-85 { color: #a78bfa; }

/* Scroll-in animation */
@keyframes scrollReveal {
    from { transform: translateY(30px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}
.results-content { animation: scrollReveal 0.6s ease-out both; }

/* Back button */
div[data-testid="stButton"].back-btn > button {
    background: transparent !important;
    border: 1px solid rgba(74,212,232,0.25) !important;
    color: #4ad4e8 !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 13px !important; padding: 6px 16px !important;
    border-radius: 20px !important;
}

/* Plotly chart background override */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
"""

# ── Plotly chart builders ──────────────────────────────────────────────────

def _plotly_cfg():
    return dict(displayModeBar=False, responsive=True)

def _dark_layout(title="", height=280):
    return dict(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Exo 2, Trebuchet MS", color="#8ab8cc", size=11),
        margin=dict(l=40, r=16, t=16 if not title else 36, b=36),
        xaxis=dict(gridcolor="rgba(74,212,232,0.07)", zerolinecolor="rgba(74,212,232,0.15)"),
        yaxis=dict(gridcolor="rgba(74,212,232,0.07)", zerolinecolor="rgba(74,212,232,0.15)"),
    )


def make_heatmap(data: dict, variable: str, year: int) -> go.Figure:
    """Generate global choropleth heatmap from backend data."""
    heatmap_data = data.get("heatmap", {})
    lats   = heatmap_data.get("lats", [])
    lons   = heatmap_data.get("lons", [])
    values = heatmap_data.get("values", [])

    colorscales = {
        "temperature":       "RdBu_r",
        "wind_speed":        "Blues",
        "precipitation":     "BuPu",
        "sea_level_pressure":"Viridis",
        "humidity":          "YlGnBu",
    }
    cscale = colorscales.get(variable.lower().replace(" ", "_"), "RdBu_r")

    fig = go.Figure()
    if lats:
        fig.add_trace(go.Scattergeo(
            lat=lats, lon=lons,
            mode="markers",
            marker=dict(
                color=values,
                colorscale=cscale,
                size=6,
                opacity=0.85,
                colorbar=dict(
                    title=dict(text=variable, font=dict(color="#8ab8cc", size=10)),
                    tickfont=dict(color="#8ab8cc", size=9),
                    thickness=12,
                ),
            ),
            hovertemplate="%{lat:.1f}°N %{lon:.1f}°E<br>Value: %{marker.color:.1f}<extra></extra>",
        ))
    else:
        # Placeholder when no data
        fig.add_annotation(text="No data loaded — click Load Data on Explore page",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(color="#3a6a80", size=14), showarrow=False)

    fig.update_geos(
        projection_type="natural earth",
        showland=True,  landcolor="rgba(20,40,60,0.8)",
        showocean=True, oceancolor="rgba(5,15,35,0.9)",
        showcoastlines=True, coastlinecolor="rgba(74,212,232,0.3)",
        showframe=False, bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(**_dark_layout(height=320))
    return fig


def make_timeseries(data: dict, variable: str, location: str) -> go.Figure:
    """Time-series with historical line + forecast + confidence band."""
    ts = data.get("timeseries", {})
    years  = ts.get("years", list(range(1950, 2025)))
    values = ts.get("values", [])
    fc_years  = ts.get("forecast_years", list(range(2025, 2046)))
    fc_values = ts.get("forecast_values", [])
    fc_upper  = ts.get("forecast_upper", [v + 0.8 for v in fc_values])
    fc_lower  = ts.get("forecast_lower", [v - 0.5 for v in fc_values])

    fig = go.Figure()

    # Confidence band (fill)
    if fc_upper and fc_lower:
        fig.add_trace(go.Scatter(
            x=fc_years + fc_years[::-1],
            y=fc_upper + fc_lower[::-1],
            fill="toself",
            fillcolor="rgba(167,139,250,0.12)",
            line=dict(color="rgba(255,255,255,0)"),
            showlegend=False, hoverinfo="skip",
        ))

    # Historical
    if values:
        fig.add_trace(go.Scatter(
            x=years, y=values,
            mode="lines",
            line=dict(color="#4ad4e8", width=2),
            name="Historical",
        ))

    # Forecast
    if fc_values:
        fig.add_trace(go.Scatter(
            x=fc_years, y=fc_values,
            mode="lines",
            line=dict(color="#a78bfa", width=2, dash="dot"),
            name="Forecast 2045",
        ))

    fig.update_layout(
        **_dark_layout(height=230),
        showlegend=False,
        yaxis_title=variable,
        hovermode="x unified",
    )
    return fig


def make_rcp_chart(data: dict, scenario: str, color: str) -> go.Figure:
    """Single RCP scenario line chart."""
    key = f"rcp_{scenario}"
    rcp = data.get("rcp_scenarios", {}).get(key, {})
    years  = rcp.get("years",  list(range(1950, 2046)))
    values = rcp.get("values", [])
    upper  = rcp.get("upper",  [v + 0.6 for v in values])
    lower  = rcp.get("lower",  [v - 0.4 for v in values])

    fig = go.Figure()
    if upper and lower:
        fig.add_trace(go.Scatter(
            x=years + years[::-1], y=upper + lower[::-1],
            fill="toself", fillcolor=f"{color}18",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ))
    if values:
        fig.add_trace(go.Scatter(
            x=years, y=values, mode="lines",
            line=dict(color=color, width=2),
            showlegend=False,
        ))
    fig.update_layout(**_dark_layout(height=120))
    return fig


def make_analogue_map(data: dict, home_lat: float, home_lon: float) -> go.Figure:
    """World map with home city and analogue cities pinned."""
    analogues = data.get("analogues", [])

    fig = go.Figure()

    # Analogue cities
    if analogues:
        alat = [a["lat"] for a in analogues]
        alon = [a["lon"] for a in analogues]
        aname = [a["city"] for a in analogues]
        fig.add_trace(go.Scattergeo(
            lat=alat, lon=alon, text=aname,
            mode="markers+text",
            marker=dict(color="#a78bfa", size=10, opacity=0.9,
                        line=dict(color="#a78bfa", width=1)),
            textfont=dict(color="#a78bfa", size=9),
            textposition="top center",
            name="Analogues",
        ))

    # Home city
    fig.add_trace(go.Scattergeo(
        lat=[home_lat], lon=[home_lon],
        mode="markers",
        marker=dict(color="#4ad4e8", size=14, opacity=1.0,
                    symbol="circle",
                    line=dict(color="#4ad4e8", width=2)),
        name="Selected City",
    ))

    fig.update_geos(
        projection_type="natural earth",
        showland=True, landcolor="rgba(20,40,60,0.8)",
        showocean=True, oceancolor="rgba(5,15,35,0.9)",
        showcoastlines=True, coastlinecolor="rgba(74,212,232,0.25)",
        showframe=False, bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(**_dark_layout(height=200), showlegend=False)
    return fig


# ── Main render ─────────────────────────────────────────────────────────────

def render_results():
    st.markdown(RESULTS_CSS, unsafe_allow_html=True)

    data     = st.session_state.get("results_data") or {}
    location = st.session_state.get("selected_location", "Paris, France")
    year     = st.session_state.get("selected_year", 2024)
    month    = st.session_state.get("selected_month", "Apr")
    variable = st.session_state.get("selected_variable", "Temperature")
    lat      = st.session_state.get("selected_lat", 48.86)
    lon      = st.session_state.get("selected_lon", 2.35)

    var_slug = variable.lower().replace(" ", "_")

    stats       = data.get("stats", {})
    current_val = stats.get("current_value", "—")
    baseline    = stats.get("baseline_mean", "—")
    anomaly     = stats.get("anomaly", "—")
    projected   = stats.get("projected_2045", "—")
    record_year = stats.get("record_year", "2023")
    beaufort    = stats.get("beaufort", None)

    ai_text  = data.get("ai_explanation", {})
    analogues = data.get("analogues", [])

    # ── Context bar ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ctx-bar">
      <div style="display:flex;align-items:center;gap:8px">
        <div style="width:7px;height:7px;border-radius:50%;background:#4ad4e8;
             box-shadow:0 0 6px #4ad4e8"></div>
        <span class="ctx-crumb">{location}<span>·</span>{month} {year}
          <span>·</span>{variable}<span>·</span>ERA5
        </span>
      </div>
      <div class="ctx-pills">
        <span class="ctx-pill">Share View</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="results-content">', unsafe_allow_html=True)

    # ── 1. Heatmap (full width) ────────────────────────────────────────────
    st.markdown(f'<div class="section-label">Global {variable} Map — {month} {year}</div>',
                unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_heatmap = make_heatmap(data, var_slug, year)
        st.plotly_chart(fig_heatmap, use_container_width=True, config=_plotly_cfg())
        st.markdown('</div>', unsafe_allow_html=True)

    # Year slider
    new_year = st.slider("", 1950, 2024, year, key="results_year_slider",
                          label_visibility="collapsed")
    if new_year != year:
        st.session_state.selected_year = new_year
        st.rerun()

    # ── 2. Timeseries + AI Analyst ─────────────────────────────────────────
    col_ts, col_ai = st.columns([1, 1], gap="medium")

    with col_ts:
        st.markdown(f'<div class="section-label">Time Series — {location}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_ts = make_timeseries(data, variable, location)
        st.plotly_chart(fig_ts, use_container_width=True, config=_plotly_cfg())
        st.markdown("""
        <div class="legend-row">
          <div class="legend-item"><div class="legend-line" style="background:#4ad4e8"></div>Historical</div>
          <div class="legend-item"><div class="legend-line" style="background:#a78bfa;border-top:1px dashed #a78bfa"></div>Forecast 2045</div>
          <div class="legend-item"><div class="legend-band" style="background:rgba(167,139,250,0.15)"></div>Confidence</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_ai:
        st.markdown('<div class="section-label">AI Climate Analyst</div>', unsafe_allow_html=True)
        anomaly_str = f"+{anomaly}" if isinstance(anomaly, (int, float)) and anomaly > 0 else str(anomaly)
        anomaly_class = "cool" if var_slug == "wind_speed" else ""
        ai_label = "GUST EVENT DETECTED" if var_slug == "wind_speed" else "ANOMALY DETECTED"
        ai_para1 = ai_text.get("paragraph1", f"{location} recorded an exceptional {variable} value in {month} {year}. This deviation from the historical baseline is consistent with observed long-term climate trends driven by global warming and regional feedback mechanisms.")
        ai_para2 = ai_text.get("paragraph2", f"The pattern is part of a broader shift in atmospheric circulation. Scientists link such events to changes in the jet stream and ocean surface temperatures that are increasingly common under current emission trajectories.")

        # Pre-compute metrics HTML outside f-string (Python <3.12 backslash restriction)
        metrics_list = ai_text.get("metrics", [])
        if metrics_list:
            metric_items = "".join(
                f'<div class="ai-metric">'
                f'<div class="val">{m["value"]}</div>'
                f'<div class="lbl">{m["label"]}</div>'
                f'</div>'
                for m in metrics_list
            )
            metrics_html = f'<div class="ai-metrics">{metric_items}</div>'
        else:
            metrics_html = ""

        st.markdown(f"""
        <div class="glass-card glass-card-accent">
          <div><span class="ai-tag">{ai_label}</span></div>
          <div class="ai-anomaly {anomaly_class}">{anomaly_str} above baseline</div>
          <div class="ai-baseline">vs. 1980–2010 mean of {baseline}</div>
          {metrics_html}
          <div class="ai-text">
            <p>{ai_para1}</p>
            <p>{ai_para2}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Ask AI a follow-up question ↗", key="ai_followup"):
            st.session_state["show_ai_chat"] = True

        if st.session_state.get("show_ai_chat"):
            q = st.text_input("Your question:", key="ai_q",
                              placeholder=f"Why did {variable} spike in {year}?")
            if q:
                from utils.api_client import fetch_ai_explanation
                with st.spinner("Asking AI analyst..."):
                    resp = fetch_ai_explanation(variable=var_slug, lat=lat, lon=lon,
                                                year=year, question=q)
                st.markdown(f'<div class="ai-text"><p>{resp}</p></div>',
                            unsafe_allow_html=True)

    # ── 3. Climate Analogue Finder ──────────────────────────────────────────
    st.markdown(f'<div class="section-label" style="margin-top:8px;">Climate Analogue Finder — Where does {location} feel like in 2050?</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col_amap, col_alist = st.columns([1.4, 0.9], gap="medium")
    with col_amap:
        fig_analogue = make_analogue_map(data, lat, lon)
        st.plotly_chart(fig_analogue, use_container_width=True, config=_plotly_cfg())
    with col_alist:
        st.markdown(f'<div style="font-size:11px;color:#2a5a6a;font-family:Exo 2,sans-serif;margin-bottom:8px;">Cities matching {location}\'s projected 2050 {variable} profile</div>',
                    unsafe_allow_html=True)
        default_analogues = [
            {"city": "Barcelona, Spain", "meta": "21.4°C avg · 52mm rain", "match": "97%"},
            {"city": "Porto, Portugal",  "meta": "19.8°C avg · 61mm rain", "match": "94%"},
            {"city": "Milan, Italy",     "meta": "20.1°C avg · 48mm rain", "match": "91%"},
            {"city": "Istanbul, Turkey", "meta": "18.9°C avg · 44mm rain", "match": "88%"},
        ]
        display_analogues = [
            {"city": a.get("city","—"),
             "meta": a.get("meta", f'{a.get("distance_km","—")} km'),
             "match": f'{a.get("match_score","—")}%'}
            for a in analogues
        ] if analogues else default_analogues

        for a in display_analogues:
            st.markdown(f"""
            <div class="analogue-card">
              <div>
                <div class="analogue-name">{a['city']}</div>
                <div class="analogue-meta">{a['meta']}</div>
              </div>
              <div class="match-badge">{a['match']}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 4. RCP Emission Scenarios ──────────────────────────────────────────
    st.markdown(f'<div class="section-label" style="margin-top:8px;">Emissions Scenario Comparison — {location} {variable} Forecast to 2045</div>',
                unsafe_allow_html=True)
    col26, col45, col85 = st.columns(3, gap="medium")
    rcp_configs = [
        (col26, "26", "#4ad4e8", "RCP 2.6 — Optimistic",  "Projected 2045:", stats.get("rcp26_proj","—")),
        (col45, "45", "#f0b429", "RCP 4.5 — Moderate",    "Projected 2045:", stats.get("rcp45_proj","—")),
        (col85, "85", "#a78bfa", "RCP 8.5 — Worst Case",  "Projected 2045:", stats.get("rcp85_proj","—")),
    ]
    for col, scenario, color, label, proj_label, proj_val in rcp_configs:
        with col:
            st.markdown(f'<div class="glass-card" style="border-color:{color}33">'
                        f'<div class="rcp-header" style="color:{color}">{label}</div>',
                        unsafe_allow_html=True)
            fig_rcp = make_rcp_chart(data, scenario, color)
            st.plotly_chart(fig_rcp, use_container_width=True, config=_plotly_cfg())
            st.markdown(f'<div style="font-size:11px;color:#2a5a6a;font-family:Exo 2,sans-serif;margin-top:4px;">'
                        f'{proj_label} <b style="color:{color}">{proj_val}</b></div>'
                        f'</div>', unsafe_allow_html=True)

    # ── 5. Stats bar ───────────────────────────────────────────────────────
    unit_map = {"temperature":"°C","wind_speed":"m/s","precipitation":"mm",
                "sea_level_pressure":"hPa","humidity":"%"}
    unit = unit_map.get(var_slug, "")

    st.markdown(f"""
    <div class="stat-grid" style="margin-top:16px;">
      <div class="stat-card">
        <div class="stat-val">{record_year}</div>
        <div class="stat-label">Hottest Year on Record</div>
        <div class="stat-sub">Global surface {variable.lower()}</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{baseline} {unit}</div>
        <div class="stat-label">Baseline Average</div>
        <div class="stat-sub">1980–2010 mean, {location}</div>
      </div>
      <div class="stat-card">
        <div class="stat-val warm">{projected} {unit}</div>
        <div class="stat-label">Projected 2045</div>
        <div class="stat-sub">Under RCP 4.5 scenario</div>
      </div>
      <div class="stat-card">
        <div class="stat-val warn">{anomaly_str} {unit}</div>
        <div class="stat-label">Current Anomaly</div>
        <div class="stat-sub">Above 74-year baseline</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(74,212,232,0.12);padding:12px 0;
         display:flex;justify-content:space-between;font-size:11px;
         color:#1a4a5a;font-family:'Exo 2',sans-serif;margin-top:8px;">
      <span>Data: ERA5 Reanalysis · ECMWF · Updated daily</span>
      <span>PyClimaExplorer · TECHNEX 2026</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Nav buttons ────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 5])
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Explore", key="results_back"):
            st.session_state.page = "explore"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⌂ Home", key="results_home"):
            st.session_state.page = "landing"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # results-content
