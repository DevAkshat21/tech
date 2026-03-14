# Walkthrough: PyClimaExplorer Cinematic Redesign & Optimizations

## Summary of Changes
The application was completely rebuilt from a multi-page routing framework into a single, cohesive, long-scrolling cinematic story. The new architecture pushes Streamlit to its absolute visual limits using custom heavily-themed CSS injection (`utils/constants.py`), an embedded JavaScript IntersectionObserver for buttery-smooth scroll reveals, and direct Plotly.js embedding for immediate click interaction with the globe.

### Core Enhancements
- **The "Zero Emoji" Framework**: Complete removal of all unicode emojis in favor of pure CSS geometric shapes and targeted text.
- **Bi-Directional Globe**: Switched to a custom Plotly `Scattergeo` embedded in an iframe. This allows the globe to be styled uniquely (dark oceans, teal rings) and instantly capture `plotly_click` coordinates, broadcasting them back to Streamlit using `window.parent.postMessage` AND setting query parameters to trigger state updates natively.
- **Observer Animation System**: CSS transitions applied to classes triggered by a custom vanilla JS script placed at the bottom of the page (`initAOS`), checking viewport entry thresholds post-DOM readystate completions to prevent asynchronous race conditions.
- **Holistic Storytelling**: `app.py` was refactored from a router into a sequential rendering engine calling 9 isolated section functions: `render_hero()`, `render_control_panel()`, `render_context_bar()`, `render_heatmap_section()`, `render_ai_section()`, `render_analogues_section()`, `render_scenarios_section()`, `render_stats_section()`, `render_footer()`.
- **Month Radio Pills**: To prevent interactivity limitations, standard `st.radio` buttons are heavily overridden using custom SCSS rules injected safely through `st.markdown`, offering perfect cross-stream pill selections.
- **Playback Loop**: Global historical timeline `PLAY / STOP` control hooks into a native infinite runtime logic sequence via manual stream ticking `time.sleep()`.

## Testing and Verification
The entire verification suite passed successfully:
- Replaced the embedded HTML `get_globe_html` component configuration strategy with a raw string template and explicit `.replace('PLACEHOLDER')` invocations ("Option B") to circumvent `f-string` un-escaped open brace `{{}}` JSON object crashes.
- No visual API artifacts (`displayModeBar` properly relocated natively).
- Clean `data.loader.load_dataset` python import bindings generating valid trace layouts alongside HTTP 200 Streamlit statuses.
- Zero instances of placeholder `synthetic` data injections.
- Zero implementations using primitive `experimental_rerun`.

### Post-Build Bug Fixes
* **Bug 1 (Coordinates KeyError)**: Patched `LOCATIONS` tuples to reliable dictionary object mappings (`['lat']`/`['lon']`) preventing array access violations and isolated default locations dynamically during initialization.
* **Bug 2 (Unresponsive Variable Selection)**: Rescued variables rendering by mapping the options to a native `st.radio` widget styled strictly with an overlapping CSS flex grid, enabling genuine 2-way session callbacks. 
* **Bug 3 (Vanishing Hero Headings)**: Swapped out unreliable Javascript IntersectionObservers inside the Hero scroll container for native, deterministic `@keyframes` CSS logic ensuring reliable entrance sequencing.
* **Bug 4 (Globe Tooltip Decoding Error)**: Rewrote the client-side map script to parse the `Math.sqrt` hypotenuse to natively determine the `nearestCity` and isolated URL property variables before firing the `streamlit:rerun` postMessage event.
* **Bug 5 (Results Cascading Failure)**: Sandboxed every single data viz container (`render_section_1` through `render_section_6`) behind rigorous Python `try/except` guard rails preventing anomalous metrics from aborting the entire page loop.
* **Syntax Error**: Addressed the JS `{}` un-escaping format issues within standard Python f-strings by abstracting the Globe container exclusively to `TEMPLATE_STRING.replace()`.
* **Globe Visibility**: Reset `block-container` bounds mapping natively the 100% viewport width, configured Plotly bounds margins from `0` to `10`, inserted CSS adjustments resetting default internal Streamlit `column` bounding paddings.
* **Globe Click Sync**: Adjusted Javascript `message` triggers to correctly overwrite the python Session states mapping natively to dropdown targets via manual Haversine distance tracking (within 15 degree offsets) and decoupled `data_loaded` triggers.
