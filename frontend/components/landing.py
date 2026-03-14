import streamlit as st
import streamlit.components.v1 as components
from .globe import get_globe_html


STAR_FIELD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700&display=swap');

.landing-wrapper {
    position: relative;
    width: 100%;
    min-height: 100vh;
    background: radial-gradient(ellipse at 70% 10%, #1a0a3a 0%, #000510 40%, #000000 100%);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* Animated star particles */
.stars-layer {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(circle, rgba(255,255,255,0.9) 1px, transparent 1px),
        radial-gradient(circle, rgba(255,255,255,0.6) 1px, transparent 1px),
        radial-gradient(circle, rgba(255,255,255,0.4) 1px, transparent 1px);
    background-size: 300px 300px, 500px 500px, 700px 700px;
    background-position: 0 0, 150px 100px, 50px 200px;
    animation: twinkle 8s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

/* Nebula effect top right */
.nebula {
    position: fixed;
    top: -100px; right: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(ellipse, rgba(80,0,180,0.25) 0%, rgba(30,0,80,0.1) 50%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

@keyframes twinkle {
    0%   { opacity: 0.7; }
    100% { opacity: 1.0; }
}

/* Logo */
.logo-row {
    display: flex; align-items: center; gap: 12px;
    margin-top: 36px; position: relative; z-index: 10;
}
.logo-icon {
    width: 42px; height: 42px;
    filter: drop-shadow(0 0 8px rgba(74,212,232,0.8));
}
.logo-text {
    font-family: 'Exo 2', 'Trebuchet MS', sans-serif;
    font-size: 26px; font-weight: 600;
    color: #ffffff;
    letter-spacing: 0.02em;
}

/* Hero text */
.hero-title {
    font-family: 'Exo 2', 'Trebuchet MS', sans-serif;
    font-size: 46px; font-weight: 700;
    color: #5ac8e8;
    text-align: center;
    line-height: 1.2;
    margin-top: 28px;
    letter-spacing: -0.01em;
    position: relative; z-index: 10;
    animation: fadeSlideUp 0.8s ease-out both;
}
.hero-subtitle {
    font-family: 'Exo 2', 'Trebuchet MS', sans-serif;
    font-size: 16px; font-weight: 300;
    color: rgba(255,255,255,0.6);
    text-align: center;
    max-width: 480px;
    line-height: 1.7;
    margin-top: 14px;
    position: relative; z-index: 10;
    animation: fadeSlideUp 0.8s 0.15s ease-out both;
}

/* Globe container - rises from bottom */
.globe-container {
    margin-top: 10px;
    position: relative; z-index: 5;
    animation: globeRise 1.2s 0.2s cubic-bezier(0.22,1,0.36,1) both;
}

@keyframes globeRise {
    from { transform: translateY(120px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}

@keyframes fadeSlideUp {
    from { transform: translateY(20px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}

/* Explore button */
.explore-btn-wrap {
    position: relative; z-index: 10;
    margin-top: -60px;
    animation: fadeSlideUp 0.8s 0.5s ease-out both;
}

/* Override Streamlit button on landing */
div[data-testid="stButton"].explore-cta > button {
    background: rgba(0,40,100,0.85) !important;
    border: 1.5px solid rgba(74,212,232,0.6) !important;
    color: #ffffff !important;
    font-family: 'Exo 2', 'Trebuchet MS', sans-serif !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 14px 70px !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(74,212,232,0.15) !important;
}
div[data-testid="stButton"].explore-cta > button:hover {
    background: rgba(0,80,160,0.9) !important;
    box-shadow: 0 0 32px rgba(74,212,232,0.35) !important;
    transform: translateY(-2px) !important;
}
</style>
"""


def render_landing():
    st.markdown(STAR_FIELD_CSS, unsafe_allow_html=True)

    # ── Full-page wrapper open ─────────────────────────────────────────────
    st.markdown("""
    <div class="landing-wrapper">
      <div class="stars-layer"></div>
      <div class="nebula"></div>

      <!-- Logo -->
      <div class="logo-row">
        <svg class="logo-icon" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="21" cy="21" r="4" fill="#4ad4e8"/>
          <ellipse cx="21" cy="21" rx="18" ry="7" stroke="#4ad4e8" stroke-width="1.5" fill="none"/>
          <ellipse cx="21" cy="21" rx="18" ry="7" stroke="#4ad4e8" stroke-width="1.5" fill="none"
            transform="rotate(60 21 21)"/>
          <ellipse cx="21" cy="21" rx="18" ry="7" stroke="#4ad4e8" stroke-width="1.5" fill="none"
            transform="rotate(120 21 21)"/>
        </svg>
        <span class="logo-text">PyClimaExplorer</span>
      </div>

      <!-- Hero -->
      <div class="hero-title">Explore Climate Data<br>Across Time and Space</div>
      <div class="hero-subtitle">
        Utilize advanced climate data analysis tools to visualize global climate
        patterns, study historical trends, and forecast future changes with ease.
      </div>

      <!-- Globe rises from bottom -->
      <div class="globe-container">
    """, unsafe_allow_html=True)

    # Three.js Globe (transparent bg so space shows through)
    globe_html = get_globe_html(width=580, height=520, auto_rotate=True,
                                 show_rings=True, bg_transparent=True)
    components.html(globe_html, height=520, scrolling=False)

    st.markdown("</div>", unsafe_allow_html=True)  # close globe-container

    # ── Explore button ─────────────────────────────────────────────────────
    st.markdown('<div class="explore-btn-wrap">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1.2, 2])
    with col2:
        st.markdown('<div class="explore-cta">', unsafe_allow_html=True)
        if st.button("Explore", key="landing_explore_btn"):
            st.session_state.page = "explore"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close explore-btn-wrap

    st.markdown('</div>', unsafe_allow_html=True)  # close landing-wrapper
