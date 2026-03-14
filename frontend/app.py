import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
import time

from utils.constants import GLOBAL_CSS, OBSERVER_JS
from utils.geo import LOCATIONS, nearest_city
from utils.api_client import fetch_climate_data, fetch_ai_explanation

st.set_page_config(page_title="PyClimaExplorer", layout="wide", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def get_plotly_config():
    return {'displayModeBar': False, 'responsive': True}

def _pt_layout(title="", height=280):
    return dict(
        title=title, height=height, margin=dict(l=40, r=16, t=16 if not title else 36, b=36),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#7eb8cc', family='Inter'),
        xaxis=dict(gridcolor='rgba(0,180,255,0.06)', zeroline=False), yaxis=dict(gridcolor='rgba(0,180,255,0.06)', zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#7eb8cc'))
    )

def render_hero():
    HERO_CSS = """
    <style>
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(24px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .hero-label { animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.05s both; }
    .hero-line-1 { animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.15s both; }
    .hero-line-2 { animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.3s both; }
    .hero-sub { animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.45s both; }
    .hero-scroll { animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.65s both; }
    @keyframes breathe {
      0%,100% { transform: scale(1); opacity:0.5; }
      50% { transform: scale(1.08); opacity:0.8; }
    }
    @keyframes bounce {
      0%,100% { transform: translateY(0); }
      50% { transform: translateY(4px); }
    }
    </style>
    """
    st.markdown(HERO_CSS, unsafe_allow_html=True)
    st.components.v1.html("""
    <div style="position:absolute;top:0;left:0;width:100%;height:100vh;overflow:hidden;pointer-events:none;z-index:0;">
        <canvas id="stars"></canvas>
        <div style="position:absolute;top:8%;left:6%;width:400px;height:280px;background:rgba(124,58,237,0.07);border-radius:50%;filter:blur(80px);animation:breathe 18s ease-in-out infinite;"></div>
        <div style="position:absolute;bottom:8%;right:5%;width:300px;height:200px;background:rgba(0,180,255,0.05);border-radius:50%;filter:blur(60px);animation:breathe 22s ease-in-out infinite reverse;"></div>
    </div>
    <script>
    const canvas = document.getElementById('stars'); const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    for(let i=0; i<80; i++) {
        let op = Math.random();
        ctx.fillStyle = op > 0.6 ? 'rgba(255,255,255,0.9)' : (op > 0.3 ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.2)');
        ctx.beginPath(); ctx.arc(Math.random()*canvas.width, Math.random()*canvas.height, Math.random()*1.5, 0, Math.PI*2); ctx.fill();
    }
    </script>
    """, height=1, scrolling=False)

    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:95vh;position:relative;z-index:10;">
        <div class="hero-label" style="font-family:'Inter';font-size:11px;font-weight:500;letter-spacing:0.3em;color:var(--ice);text-transform:uppercase;margin-bottom:24px;">PYCLIMAEXPLORER</div>
        <div class="hero-line-1" style="font-family:'Syne';font-size:clamp(48px, 8vw, 96px);font-weight:800;color:var(--text-primary);line-height:1.0;text-align:center;">Earth's Climate</div>
        <div class="hero-line-2" style="font-family:'Syne';font-size:clamp(48px, 8vw, 96px);font-weight:800;color:var(--text-primary);line-height:1.0;text-align:center;margin-bottom:32px;">Through Time</div>
        <div class="hero-sub" style="font-family:'Inter';font-size:18px;font-weight:300;color:var(--text-secondary);max-width:480px;text-align:center;margin-bottom:56px;line-height:1.6;">
            75 years of real ERA5 data. AI-powered anomaly detection.<br>Your planet's past, present, and 2045 projection.
        </div>
        <div class="hero-scroll" style="display:flex;flex-direction:column;align-items:center;">
            <div style="width:2px;height:56px;background:var(--ice);opacity:0.6;"></div>
            <div style="width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid var(--ice);opacity:0.8;animation:bounce 1.2s infinite;margin-bottom:8px;"></div>
            <div style="font-family:'Inter';font-size:10px;font-weight:300;letter-spacing:0.3em;color:var(--text-dim);text-transform:uppercase;">scroll to explore</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_control_panel():
    st.markdown('<div style="border-top:1px solid var(--rim);width:100%;margin:20px 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div:first-child {
      padding-right: 0 !important;
      overflow: visible !important;
    }
    div[data-testid="column"] {
      overflow: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)
    cl, cr = st.columns([6, 4], gap="large")
    loc = st.session_state.get("selected_location_name", "Paris, France")
    
    # Safe location name setter
    def safe_set_location(name: str) -> None:
        if name in LOCATIONS:
            st.session_state["selected_location_name"] = name
            st.session_state["selected_lat"] = LOCATIONS[name]["lat"]
            st.session_state["selected_lon"] = LOCATIONS[name]["lon"]
            
    # Default initialize coordinates if not present
    if "selected_lat" not in st.session_state:
        safe_set_location(loc)
        
    lat = st.session_state.get("clicked_lat", st.session_state.get("selected_lat", LOCATIONS["Paris, France"]["lat"]))
    lon = st.session_state.get("clicked_lon", st.session_state.get("selected_lon", LOCATIONS["Paris, France"]["lon"]))
    
    import json as _json
    from urllib.parse import unquote
    params = st.query_params
    if 'globe_click' in params:
        try:
            raw = params['globe_click']
            click_data = _json.loads(unquote(raw))
            
            clicked_lat   = float(click_data['lat'])
            clicked_lon   = float(click_data['lon'])
            clicked_city  = str(click_data.get('city_name', ''))
            clicked_ctry  = str(click_data.get('country', ''))
            era5_val      = click_data.get('era5_value')
            
            # Always update the click display values
            st.session_state['clicked_lat']       = clicked_lat
            st.session_state['clicked_lon']       = clicked_lon
            st.session_state['clicked_city_name'] = clicked_city
            st.session_state['clicked_country']   = clicked_ctry
            st.session_state['clicked_value']     = float(era5_val) if era5_val else None
            
            # KEY FIX: also update the selected location for the panel
            # Always update lat/lon with the exact click coordinates
            st.session_state['selected_lat'] = clicked_lat
            st.session_state['selected_lon'] = clicked_lon
            
            # If clicked city matches a LOCATIONS key exactly, update dropdown
            if clicked_city in LOCATIONS:
                st.session_state['selected_location_name'] = clicked_city
            else:
                import math
                best_name = None
                best_dist = float('inf')
                for name, info in LOCATIONS.items():
                    dist = math.sqrt(
                        (info['lat'] - clicked_lat) ** 2 +
                        (info['lon'] - clicked_lon) ** 2
                    )
                    if dist < best_dist:
                        best_dist = dist
                        best_name = name
                # Only snap to nearest LOCATIONS city if within ~15 degrees
                if best_dist < 15 and best_name:
                    st.session_state['selected_location_name'] = best_name
            
            st.session_state['data_loaded'] = False
            st.query_params.clear()
            st.rerun()
        except Exception:
            st.query_params.clear()

    with cl:
        st.components.v1.html(get_globe_html(lat, lon), height=600, scrolling=False)
        
    with cr:
        st.markdown("""
        <div style="background:rgba(0,16,36,0.78);border:1px solid var(--rim);border-radius:24px;padding:32px;backdrop-filter:blur(32px);-webkit-backdrop-filter:blur(32px);">
            <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:20px;padding:6px 14px;display:inline-flex;align-items:center;gap:8px;">
                <div style="width:7px;height:7px;border-radius:50%;background:var(--life);animation:pulse 2s ease-in-out infinite;"></div>
                <div style="font-family:'Inter';font-size:11px;font-weight:500;color:var(--life);letter-spacing:0.15em;text-transform:uppercase;">ERA5 Reanalysis  &middot;  1950-2024  &middot;  900 records</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="font-family:var(--font-body);font-size:10px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin:24px 0 8px;">LOCATION</div>', unsafe_allow_html=True)
        selected_loc = st.selectbox("Location", list(LOCATIONS.keys()), index=list(LOCATIONS.keys()).index(st.session_state.get("selected_location_name", "Paris, France")), key="ctrl_loc")
        if selected_loc in LOCATIONS:
            safe_set_location(selected_loc)
            
        display_lat = st.session_state.get('selected_lat', LOCATIONS[selected_loc]["lat"])
        display_lon = st.session_state.get('selected_lon', LOCATIONS[selected_loc]["lon"])
        
        lat_str = f"{abs(display_lat):.2f} {'N' if display_lat >= 0 else 'S'}"
        lon_str = f"{abs(display_lon):.2f} {'E' if display_lon >= 0 else 'W'}"
        
        clicked_city = st.session_state.get('clicked_city_name', '')
        show_city = (
            clicked_city and
            clicked_city != st.session_state.get('selected_location_name', '')
        )
        
        coord_html = f"""
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #2d6a7a; margin-top: -10px; letter-spacing: 0.05em;">
            {lat_str}   {lon_str}
            {'<span style="color:#7eb8cc;margin-left:12px;font-family:Inter,sans-serif;">' + clicked_city + ', ' + st.session_state.get('clicked_country','') + '</span>' if show_city else ''}
        </div>
        """
        st.markdown(coord_html, unsafe_allow_html=True)
        
        st.markdown('<div style="font-family:var(--font-body);font-size:10px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin:24px 0 8px;">YEAR</div>', unsafe_allow_html=True)
        st.session_state.selected_year = st.slider("Year", 1950, 2024, st.session_state.selected_year, key="ctrl_year")
        st.markdown(f'<div style="font-family:var(--font-display);font-size:56px;font-weight:800;color:var(--ice);text-align:center;line-height:1;">{st.session_state.selected_year}</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="font-family:var(--font-body);font-size:10px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin:24px 0 8px;">MONTH</div>', unsafe_allow_html=True)
        st.markdown("""<style>
        div[data-testid="stRadio"] > div { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 6px !important; }
        div[data-testid="stRadio"] > div > label { background: rgba(0,20,40,0.8) !important; border: 1px solid rgba(0,180,255,0.2) !important; border-radius: 8px !important; padding: 6px 14px !important; cursor: pointer !important; color: #7eb8cc !important; font-size: 13px !important; font-family: Inter, sans-serif !important; }
        div[data-testid="stRadio"] > div > label:has(input:checked) { background: #00d4ff !important; border-color: #00d4ff !important; color: #00030a !important; font-weight: 600 !important; }
        div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }
        </style>""", unsafe_allow_html=True)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        idx = months.index(st.session_state.selected_month) if st.session_state.selected_month in months else 3
        st.session_state.selected_month = st.radio("MONTH", options=months, index=idx, horizontal=True, key="month_radio", label_visibility="collapsed")
        
        st.markdown('<div style="font-family:var(--font-body);font-size:10px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin:24px 0 8px;">VARIABLE</div>', unsafe_allow_html=True)
        VARIABLES = ["Temperature", "Precipitation", "Wind Speed", "Humidity"]
        
        st.markdown("""<style>
        div[data-testid="stRadio"][aria-label*="variable"] > div {
          display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 10px !important;
        }
        div[data-testid="stRadio"][aria-label*="variable"] label {
          background: rgba(0,20,40,0.8) !important; border: 1px solid rgba(0,180,255,0.15) !important;
          border-radius: 12px !important; padding: 18px 12px !important; cursor: pointer !important;
          color: #7eb8cc !important; font-size: 14px !important; font-weight: 500 !important;
          font-family: Inter, sans-serif !important; text-align: center !important; justify-content: center !important;
          min-height: 60px !important; display: flex !important; align-items: center !important;
        }
        div[data-testid="stRadio"][aria-label*="variable"] label:has(input:checked) {
          background: rgba(124,58,237,0.18) !important; border-color: #7c3aed !important;
          color: #f0f9ff !important; font-weight: 600 !important;
        }
        div[data-testid="stRadio"][aria-label*="variable"] label > div:first-child { display: none !important; }
        </style>""", unsafe_allow_html=True)
        
        variable_choice = st.radio(
            "variable_select", options=VARIABLES,
            index=VARIABLES.index(st.session_state.get("selected_variable", "Temperature")),
            key="variable_radio", label_visibility="collapsed", horizontal=False
        )
        st.session_state["selected_variable"] = variable_choice
        
        st.markdown('<div style="margin:16px 0;font-size:13px;color:var(--text-dim);font-family:var(--font-body);">&nbsp;&nbsp;&nbsp;&nbsp;Upload custom .nc dataset</div>', unsafe_allow_html=True)
        if st.button("EXPLORE CLIMATE DATA"):
            with st.spinner("Loading"):
                st.session_state.results_data = fetch_climate_data(clat, clon, st.session_state.selected_year, months.index(st.session_state.selected_month)+1, st.session_state.selected_variable.lower().replace(" ", "_"))
                st.session_state.data_loaded = True
            st.rerun()
            
        st.markdown("""<style>
        div[data-testid="stButton"] button {
            width: 100%; height: 52px; background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(124,58,237,0.08)) !important;
            border: 1px solid var(--ice) !important; border-radius: 14px !important; font-family: var(--font-display) !important; font-size: 13px !important; font-weight: 700 !important;
            letter-spacing: 0.25em !important; text-transform: uppercase !important; color: var(--ice) !important; animation: border-glow 3s ease-in-out infinite;
        }
        div[data-testid="stButton"] button:hover { border-color: var(--rim-hot) !important; background: rgba(0,212,255,0.12) !important; }
        </style></div>""", unsafe_allow_html=True)

def get_globe_html(lat, lon):
    cities_json = json.dumps([{"city": k, "lat": v["lat"], "lon": v["lon"]} for k, v in LOCATIONS.items()])
    GLOBE_HTML_TEMPLATE = """
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            body { margin: 0; overflow: hidden; font-family: 'Inter', sans-serif; }
            .globe-container { filter: drop-shadow(0 0 48px rgba(0,180,255,0.18)); position: relative; }
            .tooltip {
                position: absolute; top: 20px; right: 20px; background: rgba(0,20,40,0.95); border: 1px solid rgba(0,210,255,0.35);
                border-radius: 10px; padding: 12px 16px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                color: #fff; display: none; z-index: 1000; animation: fadeIn 0.2s ease;
            }
            .tooltip-close { position: absolute; top: 8px; right: 10px; color: #2d6a7a; font-size: 12px; cursor: pointer; }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        </style>
    </head>
    <body style="background:transparent; overflow: visible;">
        <div id="globe-container" style="width: 100%; height: HEIGHT_VALUEpx; overflow: visible; position: relative;">
            <div id="globe" style="width: 100%; height: 100%;"></div>
        </div>
        <div id="tooltip" class="tooltip">
            <div class="tooltip-close" onclick="document.getElementById('tooltip').style.display='none'">x</div>
            <div id="tt-city" style="font-family:'Syne', sans-serif; font-weight:700; font-size:15px; color:#f0f9ff;">City</div>
            <div id="tt-country" style="font-weight:300; font-size:12px; color:#7eb8cc; margin-bottom:6px;">Country</div>
            <div id="tt-coords" style="font-family:'JetBrains Mono', monospace; font-size:12px; color:#00d4ff;">0.0 N  0.0 E</div>
        </div>
        <script>
            const CITIES = CITIES_PLACEHOLDER;
            
            function nearestCity(lat, lon) {
                if (!CITIES || CITIES.length === 0) return null;
                let best = CITIES[0];
                let bestDist = Infinity;
                for (let i = 0; i < CITIES.length; i++) {
                    let c = CITIES[i];
                    let d = Math.sqrt(Math.pow(lat - c.lat, 2) + Math.pow(lon - c.lon, 2));
                    if (d < bestDist) { bestDist = d; best = c; }
                }
                return best;
            }

            var layout = {
                geo: { projection: { type: 'orthographic' }, bgcolor: 'rgba(0,0,0,0)', oceancolor: '#000d1a', landcolor: '#001e35',
                    showcoastlines: true, coastlinecolor: 'rgba(0,212,255,0.22)', coastlinewidth: 0.8, showcountries: true, countrycolor: 'rgba(0,180,255,0.08)',
                    showocean: true, showland: true, showrivers: false, showlakes: false, lataxis: { showgrid: true, gridcolor: 'rgba(0,180,255,0.04)' },
                    lonaxis: { showgrid: true, gridcolor: 'rgba(0,180,255,0.04)' }, center: { lon: LON_PLACEHOLDER, lat: LAT_PLACEHOLDER }
                },
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', margin: { l: 10, r: 10, t: 10, b: 10 }, width: null, height: 520, dragmode: 'pan'
            };
            Plotly.newPlot('globe', [{ type: 'scattergeo', mode: 'markers', lat: [LAT_PLACEHOLDER], lon: [LON_PLACEHOLDER], marker: { size: 8, color: '#00d4ff' } }], layout, {
                displayModeBar: false,
                scrollZoom: false,
                responsive: true
            });
            window.addEventListener('resize', function() {
                Plotly.Plots.resize(document.getElementById('globe'));
            });
            
            document.getElementById('globe').on('plotly_click', function(eventData) {
                 if (!eventData.points || eventData.points.length === 0) return;
                 var pt = eventData.points[0];
                 var lat = pt.lat !== undefined ? pt.lat : null;
                 var lon = pt.lon !== undefined ? pt.lon : null;
                 if (lat === null || lon === null) return;
                 
                 var city = nearestCity(lat, lon);
                 var cityName = city ? city.city : 'Unknown Location';
                 var country  = city && city.country ? city.country : '';
                 
                 var latStr = lat >= 0 ? lat.toFixed(2) + ' N' : Math.abs(lat).toFixed(2) + ' S';
                 var lonStr = lon >= 0 ? lon.toFixed(2) + ' E' : Math.abs(lon).toFixed(2) + ' W';
                 
                 document.getElementById('tt-city').textContent  = cityName;
                 document.getElementById('tt-country').textContent  = country;
                 document.getElementById('tt-coords').textContent = latStr + '   ' + lonStr;
                 
                 // If you ever pass values down via marker colors:
                 var val = (pt.marker && pt.marker.color !== undefined && typeof pt.marker.color === 'number') ? parseFloat(pt.marker.color).toFixed(1) + ' C' : 'No data';
                 
                 var tooltipEl = document.getElementById('tooltip');
                 tooltipEl.style.display = 'block';
                 
                 var bbox = document.getElementById('globe').getBoundingClientRect();
                 var ex = eventData.event ? eventData.event.clientX - bbox.left : 200;
                 var ey = eventData.event ? eventData.event.clientY - bbox.top  : 200;
                 tooltipEl.style.left = Math.min(ex + 14, bbox.width - 210) + 'px';
                 tooltipEl.style.top  = Math.max(ey - 90, 8) + 'px';
                 
                 var payload = JSON.stringify({
                   lat: lat, lon: lon, city_name: cityName, country: country, era5_value: pt.marker ? pt.marker.color : null
                 });
                 
                 try {
                   var url = new URL(window.parent.location.href);
                   url.searchParams.set('globe_click', encodeURIComponent(payload));
                   window.parent.history.replaceState({}, '', url.toString());
                   window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:rerun'}, '*');
                 } catch(e) { console.log('postMessage failed:', e); }
            });
        </script>
    </body>
    </html>
    """
    return GLOBE_HTML_TEMPLATE.replace('LAT_PLACEHOLDER', str(lat)).replace('LON_PLACEHOLDER', str(lon)).replace('CITIES_PLACEHOLDER', cities_json).replace('HEIGHT_VALUE', '520')

def placeholder_view():
    st.markdown('<div style="border:1px dashed rgba(0,180,255,0.15);border-radius:16px;height:200px;display:flex;align-items:center;justify-content:center;margin-top:40px;"><div style="font-family:\'Inter\';font-weight:300;font-size:14px;color:var(--text-dim);">Select a location and click Explore to begin</div></div>', unsafe_allow_html=True)

def render_context_bar():
    loc = st.session_state.get("selected_location_name", "Paris, France")
    display_loc = loc
    st.markdown(f"""
    <div class="ctx-bar">
      <div style="display:flex;align-items:center;gap:8px">
        <div style="width:7px;height:7px;border-radius:50%;background:var(--ice);animation:pulse 2s ease-in-out infinite;"></div>
        <span style="font-family:'Inter';font-weight:500;font-size:12px;letter-spacing:0.08em;color:var(--ice);">{display_loc} &middot; {st.session_state.selected_month} {st.session_state.selected_year} &middot; {st.session_state.selected_variable} &middot; ERA5</span>
      </div>
      <div><span class="ctx-pill">Share View</span></div>
    </div>
    """, unsafe_allow_html=True)

def render_heatmap_section():
    st.markdown('<div class="section-header aos"><div class="eyebrow">SPATIAL ANALYSIS</div><div class="section-title aos aos-d1">Global Distribution</div><div class="section-sub aos aos-d2">ERA5 Reanalysis &middot; Click any region for AI analysis</div></div>', unsafe_allow_html=True)
    d = st.session_state.results_data.get("heatmap", {})
    fig = go.Figure(go.Scattergeo(lat=d.get("lats",[]), lon=d.get("lons",[]), mode="markers", marker=dict(color=d.get("values",[]), colorscale="RdBu_r", size=6, opacity=0.7, colorbar=dict(bgcolor='rgba(0,0,0,0)', outlinecolor='rgba(0,180,255,0.12)', tickfont=dict(color='#7eb8cc', family='Inter')))))
    fig.update_geos(projection_type="natural earth", showland=True, landcolor="#001e35", showocean=True, oceancolor="#000d1a", showcoastlines=True, coastlinecolor="rgba(0,212,255,0.3)", bgcolor="rgba(0,0,0,0)", showframe=False)
    fig.update_layout(height=520, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())
    
    col1, col2, col3, col4, col5 = st.columns([1, 6, 1, 1, 1])
    with col1: st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#2d6a7a;padding-top:12px">1950</div>', unsafe_allow_html=True)
    with col2:
        year = st.slider("Year", min_value=1950, max_value=2024, value=st.session_state.get('selected_year', 2024), key='heatmap_year_slider', label_visibility='collapsed')
        st.session_state['selected_year'] = year
    with col3: st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#2d6a7a;padding-top:12px">2024</div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div style="font-family:Syne,sans-serif;font-weight:800;font-size:36px;color:#00d4ff;text-align:center;line-height:1;">{year}</div>', unsafe_allow_html=True)
    with col5:
        is_playing = st.session_state.get('heatmap_playing', False)
        btn_label = "STOP" if is_playing else "PLAY"
        if st.button(btn_label, key='animate_btn', use_container_width=True):
            st.session_state['heatmap_playing'] = not is_playing
            st.rerun()

    if st.session_state.get('heatmap_playing', False):
        current = st.session_state.get('selected_year', 1950)
        if current >= 2024:
            st.session_state['heatmap_playing'] = False
            st.session_state['selected_year'] = 1950
            st.rerun()
        import time
        next_year = current + 1
        st.session_state['selected_year'] = next_year
        time.sleep(0.15)
        st.rerun()

def render_ai_section():
    ts = st.session_state.results_data.get("timeseries", {})
    c1, c2 = st.columns([0.55, 0.45], gap="large")
    with c1:
        st.markdown(f'<div style="font-family:\'Inter\';font-size:11px;font-weight:500;letter-spacing:0.15em;color:var(--text-dim);">TIME SERIES  —  {st.session_state.selected_location}</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ts.get("years",[]), y=ts.get("values",[]), mode="lines", line=dict(color="#00d4ff", width=2), name="ERA5 Historical"))
        fy = ts.get("forecast_years",[])
        fv = ts.get("forecast_values",[])
        fu = ts.get("forecast_upper",[])
        fl = ts.get("forecast_lower",[])
        if fv and fu and fl:
            fig.add_trace(go.Scatter(x=fy+[fy[-1]], y=fv+[fv[-1]], mode="lines", line=dict(color="rgba(0,212,255,0.35)", width=1, dash="dot"), name="10yr Mean"))
            fig.add_trace(go.Scatter(x=fy, y=fv, mode="lines", line=dict(color="#7c3aed", width=2, dash="dash"), name="Forecast 2045"))
            fig.add_trace(go.Scatter(x=fy+fy[::-1], y=fu+fl[::-1], fill="toself", fillcolor="rgba(124,58,237,0.08)", line=dict(color="rgba(0,0,0,0)"), name="Confidence"))
        fig.update_layout(**_pt_layout(height=400), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())
        
        st.markdown('<div style="display:flex;gap:16px;"><div style="display:flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:11px;color:var(--text-secondary);"><div style="width:20px;height:2px;background:var(--ice);"></div>Historical</div><div style="display:flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:11px;color:var(--text-secondary);"><div style="width:20px;height:2px;border-top:2px dashed var(--aurora);"></div>Forecast 2045</div><div style="display:flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:11px;color:var(--text-secondary);"><div style="width:20px;height:8px;background:rgba(124,58,237,0.15);"></div>Confidence band</div></div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass glass-hot" style="position:relative;margin-top:20px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:16px;">
                <div style="font-family:\'Inter\';font-size:10px;font-weight:500;letter-spacing:0.2em;color:var(--text-dim);text-transform:uppercase;">AI CLIMATE ANALYST</div>
                <div style="font-family:\'Inter\';font-size:10px;font-weight:300;color:var(--aurora);background:var(--aurora-dim);border:1px solid rgba(124,58,237,0.25);border-radius:20px;padding:3px 10px;">claude-sonnet-4-6</div>
            </div>
            <div style="background:var(--flare-dim);border:1px solid var(--flare);color:var(--flare);display:inline-block;border-radius:20px;padding:4px 12px;font-family:var(--font-body);font-size:10px;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;">ABOVE AVERAGE</div>
            <div style="font-family:var(--font-display);font-size:52px;font-weight:800;color:var(--flare);line-height:1;">+2.1 C</div>
            <div style="font-family:var(--font-body);font-size:13px;font-weight:300;color:var(--text-dim);margin-bottom:24px;">above 1980-2010 baseline</div>
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <div style="flex:1;background:var(--surface2);border-radius:10px;padding:12px;"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.15em;color:var(--text-dim);text-transform:uppercase;">ANOMALY</div><div class="font-mono" style="font-size:18px;font-weight:600;color:var(--flare);">+2.1</div></div>
                <div style="flex:1;background:var(--surface2);border-radius:10px;padding:12px;"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.15em;color:var(--text-dim);text-transform:uppercase;">PERCENTILE</div><div class="font-mono" style="font-size:18px;font-weight:600;color:var(--aurora);">98th</div></div>
                <div style="flex:1;background:var(--surface2);border-radius:10px;padding:12px;"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.15em;color:var(--text-dim);text-transform:uppercase;">TREND</div><div class="font-mono" style="font-size:18px;font-weight:600;color:var(--ice);">+0.28</div></div>
            </div>
            <div style="font-family:var(--font-body);font-size:14px;font-weight:300;color:var(--text-secondary);line-height:1.85;">
                <p>The record values observed are consistent with the long-term regional warming trend and shifting baseline norms for this location.</p>
                <p>These persistent positive anomalies across multiple decades reflect macro-changes in the foundational climate state, necessitating forward-looking adaptation.</p>
            </div>
            <button style="background:transparent;border:1px solid var(--aurora);color:var(--aurora);border-radius:8px;font-family:var(--font-body);font-size:12px;padding:8px 16px;cursor:pointer;margin-top:16px;">Ask a follow-up question</button>
        </div>
        """, unsafe_allow_html=True)


def render_analogues_section():
    st.markdown(f'<div class="section-header aos"><div class="eyebrow">CLIMATE ANALOGUES</div><div class="section-title aos aos-d1">Where does {st.session_state.selected_location}\'s 2050 climate exist today?</div><div class="section-sub aos aos-d2">5-vector climate signature matching &middot; Scientifically grounded methodology</div></div>', unsafe_allow_html=True)
    
    an = st.session_state.results_data.get("analogues", [])
    slat, slon = LOCATIONS[st.session_state.selected_location]
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(lat=[slat], lon=[slon], mode="markers", marker=dict(color="#00d4ff", size=14, symbol="circle"), name="Source"))
    
    for a in an:
        fig.add_trace(go.Scattergeo(lat=[a['lat']], lon=[a['lon']], mode="markers", marker=dict(color="#7c3aed", size=10, symbol="circle"), name="Analogue"))
        fig.add_trace(go.Scattergeo(lat=[slat, a['lat']], lon=[slon, a['lon']], mode="lines", line=dict(color="rgba(124,58,237,0.25)", width=1, dash="dot"), showlegend=False))
        
    fig.update_geos(projection_type="natural earth", geo_bgcolor='#000d1a', showland=True, landcolor="#001e35", showocean=True, oceancolor="#000d1a", showcoastlines=True, coastlinecolor="rgba(0,212,255,0.3)", bgcolor="rgba(0,0,0,0)", showframe=False)
    fig.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

    html = '<div class="analogue-cards-container">'
    for a in an[:4]:
        html += f'<div class="glass aos"><div class="font-display" style="font-size:20px;color:var(--text-primary);font-weight:700;">{a["city"]}</div><div style="font-family:var(--font-body);font-size:14px;font-weight:300;color:var(--text-dim);margin-bottom:16px;">Country Name</div><div style="display:flex;gap:12px;margin-bottom:16px;"><div style="flex:1"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;color:var(--text-dim);text-transform:uppercase;">MEAN TEMP</div><div class="font-mono text-secondary" style="font-size:12px;">21.4 C</div></div><div style="flex:1"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;color:var(--text-dim);text-transform:uppercase;">SEASONALITY</div><div class="font-mono text-secondary" style="font-size:12px;">Moderate</div></div><div style="flex:1"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;color:var(--text-dim);text-transform:uppercase;">WARMING</div><div class="font-mono text-secondary" style="font-size:12px;">High</div></div></div><div class="font-display text-purple" style="font-size:32px;font-weight:800;">{a.get("match_score","94")}%</div><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.2em;color:var(--text-dim);text-transform:uppercase;">CLIMATE MATCH</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_scenarios_section():
    st.markdown('<div class="section-header aos"><div class="eyebrow">EMISSIONS SCENARIOS</div><div class="section-title aos aos-d1">Two Lines.<br>Same Planet.<br>Different Choices.</div></div>', unsafe_allow_html=True)
    
    rcp_data = st.session_state.results_data.get("rcp_scenarios", {})
    
    def mk_card(id, title, sub, color_cls, color_hex, val="20.1"):
        rcp = rcp_data.get(id, {})
        fig = go.Figure()
        if rcp.get("values"):
            fig.add_trace(go.Scatter(x=rcp["years"], y=rcp["values"], mode="lines", line=dict(color=color_hex, width=2)))
            fig.add_trace(go.Scatter(x=rcp["years"]+rcp["years"][::-1], y=rcp["upper"]+rcp["lower"][::-1], fill="toself", fillcolor=f"rgba({124 if '45' in id else 0},58,237,0.1)", line=dict(color="rgba(0,0,0,0)")))
        fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        st.markdown(f'<div class="rcp-card aos" style="border-left-color:{color_hex};"><div style="display:flex;flex-direction:column;justify-content:center;"><div style="font-family:var(--font-body);font-size:10px;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:{color_hex};border:1px solid {color_hex};border-radius:12px;padding:4px 10px;display:inline-block;width:fit-content;margin-bottom:12px;">{title.split("-")[1].strip().upper()}</div><div class="font-display" style="font-size:18px;font-weight:700;color:var(--text-primary);">{title}</div><div style="font-family:var(--font-body);font-size:13px;font-weight:300;color:var(--text-dim);margin-bottom:16px;">{sub}</div><div class="font-mono" style="font-size:24px;font-weight:600;color:{color_hex};">{val}</div><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.1em;color:var(--text-dim);text-transform:uppercase;">PROJECTED 2045</div></div><div id="rcp-plot-{id}"></div></div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config=get_plotly_config())

    mk_card("rcp_26", "RCP 2.6 - Aggressive Mitigation", "Net zero by 2050 pathway", "text-cyan", "#00d4ff")
    mk_card("rcp_45", "RCP 4.5 - Moderate Action", "Current policy trajectory", "text-amber", "#f59e0b")
    mk_card("rcp_85", "RCP 8.5 - Business As Usual", "No additional climate policy", "text-red", "#ef4444")
    
    st.markdown('<div style="font-family:var(--font-body);font-size:16px;font-weight:300;font-style:italic;color:var(--text-secondary);text-align:center;margin-top:20px;">The shaded region is the range of futures still in our hands.</div>', unsafe_allow_html=True)


def render_stats_section():
    st.markdown(f'<div class="stat-grid">', unsafe_allow_html=True)
    st.markdown('<div class="glass aos"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin-bottom:8px;">CURRENT VALUE</div><div class="font-display" style="font-size:44px;font-weight:800;color:var(--text-primary);">18.7<span style="font-size:24px;font-family:var(--font-display);font-weight:400;color:var(--text-dim);"> C</span></div><div class="font-mono text-red" style="font-size:13px;">+1.2 vs baseline</div><div style="font-family:var(--font-body);font-size:11px;font-weight:300;color:var(--text-dim);margin-top:8px;">Apr 2024 &middot; Paris, France</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass aos aos-d1"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin-bottom:8px;">1980-2010 MEAN</div><div class="font-display" style="font-size:44px;font-weight:800;color:var(--text-primary);">17.5<span style="font-size:24px;font-family:var(--font-display);font-weight:400;color:var(--text-dim);"> C</span></div><div style="font-family:var(--font-body);font-size:11px;font-weight:300;color:var(--text-dim);margin-top:8px;margin-bottom:8px;">30-year reference period</div><div style="height:3px;background:var(--surface2);border-radius:2px;overflow:hidden;"><div style="width:60%;height:100%;background:var(--ice);"></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass aos aos-d2"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin-bottom:8px;">CLASSIFICATION</div><div class="font-display text-amber" style="font-size:26px;font-weight:700;">HEAT ALERT</div><div style="font-family:var(--font-body);font-size:11px;font-weight:300;color:var(--text-dim);margin-top:8px;">Above moderate threshold</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass aos aos-d3"><div style="font-family:var(--font-body);font-size:9px;font-weight:500;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-dim);margin-bottom:8px;">TREND / DECADE</div><div class="font-display text-amber" style="font-size:44px;font-weight:800;">+0.28<span style="font-size:24px;font-family:var(--font-display);font-weight:400;color:var(--text-dim);"> C</span></div><div style="font-family:var(--font-body);font-size:11px;font-weight:300;color:var(--text-dim);margin-top:8px;">Since 1950</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div style="background:var(--void);border-top:1px solid var(--rim);padding:48px 32px;display:flex;justify-content:space-between;align-items:center;margin-top:80px;">
        <div>
            <div style="font-family:var(--font-display);font-weight:700;font-size:18px;color:var(--ice);">PyClimaExplorer</div>
            <div style="font-family:var(--font-body);font-weight:300;font-size:12px;color:var(--text-dim);margin-top:4px;">Built for Hack It Out  &middot;  Technex '26  &middot;  IIT (BHU) Varanasi</div>
        </div>
        <div style="text-align:right;">
            <div style="font-family:var(--font-body);font-weight:300;font-size:12px;color:var(--text-dim);margin-bottom:4px;">Data: ERA5 Reanalysis  &middot;  ECMWF</div>
            <div style="font-family:var(--font-body);font-weight:300;font-size:12px;color:var(--text-dim);margin-bottom:4px;">AI: Claude claude-sonnet-4-6  &middot;  Anthropic</div>
            <div style="font-family:var(--font-body);font-weight:300;font-size:12px;color:var(--text-dim);">Forecast: Prophet  &middot;  RCP 2.6 / 4.5 / 8.5</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.markdown("""
    <style>
    .aos { opacity: 0; transform: translateY(28px); transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1); }
    .aos.visible { opacity: 1 !important; transform: translateY(0) !important; }
    .aos-d1 { transition-delay: 0.1s !important; }
    .aos-d2 { transition-delay: 0.2s !important; }
    .aos-d3 { transition-delay: 0.3s !important; }
    @keyframes fadeUp { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }
    .hero-line-1 { animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.1s both; }
    .hero-line-2 { animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.25s both; }
    </style>
    """, unsafe_allow_html=True)
    defaults = {
        "page": "landing", "selected_location_name": "Paris, France", "selected_lat": 48.86, "selected_lon": 2.35, "selected_year": 2024, "selected_month": "Apr", "selected_variable": "Temperature", "results_data": None, "data_loaded": False, "clicked_lat": 48.86, "clicked_lon": 2.35, "clicked_city_name": "Paris",
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    render_hero()
    render_control_panel()
    
    if st.session_state.data_loaded:
        render_context_bar()
        render_heatmap_section()
        render_ai_section()
        render_analogues_section()
        render_scenarios_section()
        render_stats_section()
    else:
        placeholder_view()
        
    render_footer()
    st.markdown("""
    <script>
    (function() {
      function initAOS() {
        // Look in the parent document (Streamlit host) for .aos elements
        const doc = window.parent.document;
        const els = doc.querySelectorAll('.aos');
        if(els.length === 0) {
          // Elements not rendered yet, retry in 300ms
          setTimeout(initAOS, 300);
          return;
        }
        const obs = new window.parent.IntersectionObserver(
          entries => entries.forEach(e => {
            if(e.isIntersecting) e.target.classList.add('visible');
          }),
          { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
        );
        els.forEach(el => obs.observe(el));
      }
      // Wait for parent DOM to be ready
      if(window.parent.document.readyState === 'complete') {
        setTimeout(initAOS, 400);
      } else {
        window.parent.addEventListener('load', () => setTimeout(initAOS, 400));
      }
    })();
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
