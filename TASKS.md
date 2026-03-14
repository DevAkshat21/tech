# PyClimaExplorer UI Redesign Tasks

- [x] Create strict CSS ruleset in `frontend/utils/constants.py` (Zero Unicode Emoji Rule).
- [x] Create geospatial utilities `LOCATIONS` and `nearest_city` in `frontend/utils/geo.py`.
- [x] Implement Section 1: Cinematic scroll hero section with animated CSS nebulas and JS starfield.
- [x] Implement Section 2: Interactive 3D Plotly globe embedded in `st.components.v1.html` passing click events.
- [x] Implement Section 2 (Right): Glass panel form controls.
- [x] Implement Section 3: Context bar sticky header.
- [x] Implement Section 4: Heatmap visualization using `make_heatmap()` data payload.
- [x] Implement Section 5: Dual column AI analyst and prophet timeseries overlay.
- [x] Implement Section 6: Analogue climate profile matching network map.
- [x] Implement Section 7: Future scenario divergence models (RCP 2.6, 4.5, 8.5).
- [x] Implement Section 8: KPI and statistical summary row.
- [x] Refactor all components directly into a single massive scrollable `app.py`.
- [x] Verify complete compliance with styling constraints and data structures.

## Bug Fixes
- [x] **Bug 1:** Fixed KeyError accessing dictionary coords in `geo.py` tuples.
- [x] **Bug 2:** Transformed static Variable Select cards into native interactive `st.radio` elements configured via CSS overrides.
- [x] **Bug 3:** Rescued the missing Hero Headlines natively within `HERO_CSS` keyframes instead of unreliable pure Javascript IntersectionObservers.
- [x] **Bug 4:** Rebuilt the interactive Globe map click handlers safely isolating tooltips logic from streamlit query-param encoding conflicts.
- [x] **Bug 5:** Embedded robust Python `try-except` boundary blocks wrapping individual feature visualizers to completely arrest chain-reaction failures.
- [x] **SyntaxError Fix:** Corrected Python rendering crash in `app.py` line 175 inside the Globe's script block by removing the raw f-string markup and replacing it with a hardcoded HTML constants template evaluated via string `.replace()`.
- [x] **Globe Visibility & Margins Fix:** Removed block-container padding and internal Streamlit column padding, adjusted the Plotly `margin` and `height`, and set the config to `responsive: true`.
- [x] **Globe Click Sync Fix:** Rewrote `st.query_params` ingestion logic to actively override the RHS coordinate elements and auto-snap `selected_location_name` to the nearest matched `LOCATIONS` configuration, resetting `data_loaded = False`.
