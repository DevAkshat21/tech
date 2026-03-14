import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from components.landing import render_landing
from components.explore import render_explore
from components.results import render_results

st.set_page_config(
    page_title="PyClimaExplorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Kill all default Streamlit chrome ──────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, header, footer, .stDeployButton,
  [data-testid="stToolbar"], .stDecoration,
  div[data-testid="stStatusWidget"],
  .viewerBadge_container__1QSob { display: none !important; }
  section[data-testid="stSidebar"] { display: none !important; }
  .stApp { background: #00000f !important; padding: 0 !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  .appview-container .main .block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────
defaults = {
    "page": "landing",
    "selected_location": "Paris, France",
    "selected_lat": 48.86,
    "selected_lon": 2.35,
    "selected_year": 2024,
    "selected_month": "April",
    "selected_variable": "Temperature",
    "results_data": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Router ─────────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    render_landing()
elif st.session_state.page == "explore":
    render_explore()
elif st.session_state.page == "results":
    render_results()
