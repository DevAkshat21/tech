import streamlit as st
import streamlit.components.v1 as components
from .globe import get_globe_html

EXPLORE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700&display=swap');

/* Full-page space background */
.explore-page {
    position: relative;
    width: 100%;
    min-height: 100vh;
    background: radial-gradient(ellipse at 70% 10%, #1a0a3a 0%, #000510 40%, #000000 100%);
}
.stars-layer {
    position: fixed; top:0; left:0; right:0; bottom:0;
    background-image:
        radial-gradient(circle, rgba(255,255,255,0.9) 1px, transparent 1px),
        radial-gradient(circle, rgba(255,255,255,0.5) 1px, transparent 1px);
    background-size: 300px 300px, 600px 600px;
    animation: twinkle 8s ease-in-out infinite alternate;
    pointer-events: none; z-index: 0;
}
.nebula {
    position: fixed; top:-80px; right:-80px;
    width: 450px; height: 450px;
    background: radial-gradient(ellipse, rgba(80,0,180,0.22) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}
@keyframes twinkle { 0% { opacity:.7; } 100% { opacity:1; } }

/* Logo bar */
.logo-bar {
    position: relative; z-index: 20;
    display: flex; align-items: center;
    justify-content: center; gap: 12px;
    padding: 24px 0 8px;
    animation: fadeIn 0.5s ease-out both;
}
.logo-text { font-family:'Exo 2',sans-serif; font-size:22px; font-weight:600; color:#fff; }

/* Slide-in animations for globe and panel */
@keyframes slideFromRight { from { transform:translateX(80px); opacity:0; } to { transform:translateX(0); opacity:1; } }
@keyframes fadeIn        { from { opacity:0; }                             to { opacity:1; }                          }

.globe-col { animation: fadeIn 0.7s 0.1s ease-out both; }
.panel-col { animation: slideFromRight 0.7s 0.2s cubic-bezier(0.22,1,0.36,1) both; }

/* Glassmorphism control panel */
.glass-panel {
    background: rgba(0, 18, 45, 0.88);
    border: 1px solid rgba(74,212,232,0.25);
    border-radius: 12px;
    padding: 28px 28px 24px;
    margin: 0 16px;
}
.panel-section-label {
    font-family: 'Exo 2', sans-serif;
    font-size: 15px; font-weight: 600;
    color: #b0d8f0;
    margin-bottom: 8px;
    letter-spacing: 0.03em;
}

/* Streamlit widget overrides inside the panel */
div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stSelectSlider"] label {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #8ac0d8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: rgba(0,30,70,0.8) !important;
    border: 1px solid rgba(74,212,232,0.3) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-family: 'Exo 2', sans-serif !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #4ad4e8 !important;
    border-color: #4ad4e8 !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stSliderTrackFill"] {
    background: #4ad4e8 !important;
}
div[data-testid="stSelectSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #4ad4e8 !important;
}

/* Month pills style override */
div[data-testid="stSelectSlider"] {
    margin-top: 4px;
}

/* Load Data button */
div[data-testid="stButton"].load-btn > button {
    background: rgba(0,50,120,0.9) !important;
    border: 1.5px solid rgba(74,212,232,0.55) !important;
    color: #ffffff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    padding: 14px 0 !important;
    border-radius: 8px !important;
    width: 100% !important;
    margin-top: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 16px rgba(74,212,232,0.1) !important;
}
div[data-testid="stButton"].load-btn > button:hover {
    background: rgba(0,80,180,0.95) !important;
    box-shadow: 0 0 28px rgba(74,212,232,0.3) !important;
    transform: translateY(-1px) !important;
}

/* Back button */
div[data-testid="stButton"].back-btn > button {
    background: transparent !important;
    border: 1px solid rgba(74,212,232,0.25) !important;
    color: #4ad4e8 !important;
    font-size: 13px !important;
    padding: 6px 16px !important;
    border-radius: 20px !important;
}

/* Location display under globe */
.location-chip {
    text-align: center;
    font-family: 'Exo 2', sans-serif;
    font-size: 12px;
    color: #4ad4e8;
    margin-top: -16px;
    padding: 6px 0;
    letter-spacing: 0.05em;
}
</style>
"""

LOCATIONS = {
    "Paris, France":         (48.86,  2.35),
    "New York, USA":         (40.71, -74.01),
    "Tokyo, Japan":          (35.68, 139.69),
    "Sydney, Australia":    (-33.87, 151.21),
    "Mumbai, India":         (19.07,  72.88),
    "London, UK":            (51.51,  -0.13),
    "Beijing, China":        (39.91, 116.39),
    "Cairo, Egypt":          (30.04,  31.24),
    "São Paulo, Brazil":    (-23.55, -46.63),
    "Moscow, Russia":        (55.75,  37.62),
    "Reykjavik, Iceland":    (64.13, -21.93),
    "Cape Town, South Africa": (-33.93, 18.42),
}

VARIABLES = [
    "Temperature",
    "Wind Speed",
    "Precipitation",
    "Sea Level Pressure",
    "Humidity",
]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def render_explore():
    st.markdown(EXPLORE_CSS, unsafe_allow_html=True)
    st.markdown('<div class="explore-page"><div class="stars-layer"></div><div class="nebula"></div>', 
                unsafe_allow_html=True)

    # ── Logo bar ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="logo-bar">
      <svg width="32" height="32" viewBox="0 0 42 42" fill="none">
        <circle cx="21" cy="21" r="4" fill="#4ad4e8"/>
        <ellipse cx="21" cy="21" rx="18" ry="7" stroke="#4ad4e8" stroke-width="1.5" fill="none"/>
        <ellipse cx="21" cy="21" rx="18" ry="7" stroke="#4ad4e8" stroke-width="1.5" fill="none"
          transform="rotate(60 21 21)"/>
        <ellipse cx="21" cy="21" rx="18" ry="7" stroke="#4ad4e8" stroke-width="1.5" fill="none"
          transform="rotate(120 21 21)"/>
      </svg>
      <span class="logo-text">PyClimaExplorer</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout ──────────────────────────────────────────────────
    col_globe, col_form = st.columns([1.15, 0.85])

    # Current location
    location_name = st.session_state.get("selected_location", "Paris, France")
    lat, lon = LOCATIONS.get(location_name, (48.86, 2.35))
    variable  = st.session_state.get("selected_variable", "Temperature")
    year      = st.session_state.get("selected_year", 2024)

    var_unit_map = {
        "Temperature": "°C", "Wind Speed": "m/s",
        "Precipitation": "mm", "Sea Level Pressure": "hPa", "Humidity": "%",
    }
    unit = var_unit_map.get(variable, "")

    with col_globe:
        st.markdown('<div class="globe-col">', unsafe_allow_html=True)

        pin_val = f"Avg. {variable}: — {unit}"
        if st.session_state.get("results_data"):
            d = st.session_state.results_data
            pin_val = f"Avg. {variable}: {d.get('current_value','—')} {unit}"

        globe_html = get_globe_html(
            width=520, height=520,
            pin_lat=lat, pin_lon=lon,
            pin_label=location_name,
            pin_value=pin_val,
            auto_rotate=True, show_rings=True, bg_transparent=True,
        )
        components.html(globe_html, height=520, scrolling=False)

        st.markdown(f'<div class="location-chip">{lat:.2f}°N · {lon:.2f}°E</div>', 
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_form:
        st.markdown('<div class="panel-col"><div class="glass-panel">', unsafe_allow_html=True)

        # ── Location ───────────────────────────────────────────────────────
        st.markdown('<div class="panel-section-label">Select Location</div>', unsafe_allow_html=True)
        selected_location = st.selectbox(
            "Location", list(LOCATIONS.keys()),
            index=list(LOCATIONS.keys()).index(location_name),
            label_visibility="collapsed", key="location_select"
        )
        lat, lon = LOCATIONS[selected_location]
        coords_html = f'<div style="font-size:11px;color:#5cb8d4;margin-top:-8px;margin-bottom:14px;font-family:Exo 2,sans-serif;">{lat:.2f}°N, {lon:.2f}°E</div>'
        st.markdown(coords_html, unsafe_allow_html=True)

        # ── Year ───────────────────────────────────────────────────────────
        st.markdown('<div class="panel-section-label">Select Year</div>', unsafe_allow_html=True)
        selected_year = st.slider(
            "Year", min_value=1950, max_value=2024,
            value=st.session_state.selected_year,
            label_visibility="collapsed", key="year_slider"
        )

        # ── Month ──────────────────────────────────────────────────────────
        st.markdown('<div class="panel-section-label" style="margin-top:10px;">Select Month</div>', 
                    unsafe_allow_html=True)
        selected_month = st.select_slider(
            "Month", options=MONTHS,
            value=st.session_state.selected_month
                  if st.session_state.selected_month in MONTHS else "Apr",
            label_visibility="collapsed", key="month_slider"
        )

        # ── Variable ───────────────────────────────────────────────────────
        st.markdown('<div class="panel-section-label" style="margin-top:10px;">Select Variable</div>', 
                    unsafe_allow_html=True)
        selected_variable = st.selectbox(
            "Variable", VARIABLES,
            index=VARIABLES.index(variable) if variable in VARIABLES else 0,
            label_visibility="collapsed", key="variable_select"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Load Data ──────────────────────────────────────────────────────
        st.markdown('<div class="load-btn">', unsafe_allow_html=True)
        if st.button("Load Data", key="load_data_btn"):
            # Save selections to session state
            st.session_state.selected_location = selected_location
            st.session_state.selected_lat      = lat
            st.session_state.selected_lon      = lon
            st.session_state.selected_year     = selected_year
            st.session_state.selected_month    = selected_month
            st.session_state.selected_variable = selected_variable

            with st.spinner("Fetching climate data..."):
                from utils.api_client import fetch_climate_data
                data = fetch_climate_data(
                    lat=lat, lon=lon, year=selected_year,
                    month=MONTHS.index(selected_month) + 1,
                    variable=selected_variable.lower().replace(" ", "_"),
                )
                st.session_state.results_data = data

            st.session_state.page = "results"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)  # glass-panel, panel-col

    # ── Back to landing ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _, back_col, _ = st.columns([4, 1, 4])
    with back_col:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← Back", key="back_btn"):
            st.session_state.page = "landing"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # explore-page
