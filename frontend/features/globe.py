import xarray as xr
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import json

def render_globe(_ds: xr.Dataset, year: int, height: int = 520, show_click_handler: bool = True) -> dict | None:
    try:
        year_data = _ds.t2m.sel(time=_ds.time.dt.year == year).mean(dim='time')
    except Exception:
        year_data = _ds.t2m.isel(time=0)

    lats = year_data.lat.values[::4]
    lons = year_data.lon.values[::4]
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing='ij')
    vals = year_data.values[::4, ::4]
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    val_flat = vals.flatten()
    mask = ~np.isnan(val_flat)

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=lat_flat[mask], lon=lon_flat[mask], mode='markers',
        marker=dict(size=3, color=val_flat[mask], colorscale='RdBu_r', cmin=-30, cmax=40, opacity=0.75,
                    colorbar=dict(title='C', thickness=12, len=0.6, bgcolor='rgba(0,0,0,0)',
                                  tickfont=dict(color='#7eb8cc', size=10), titlefont=dict(color='#7eb8cc'))),
        hovertemplate='%{lat:.1f}N %{lon:.1f}E<br>%{marker.color:.1f}C<extra></extra>', name='Temperature'
    ))

    sel_lat = st.session_state.get('selected_lat', 48.86)
    sel_lon = st.session_state.get('selected_lon', 2.35)
    sel_name = st.session_state.get('selected_location_name', 'Paris, France')

    fig.add_trace(go.Scattergeo(
        lat=[sel_lat], lon=[sel_lon], mode='markers+text',
        marker=dict(size=10, color='#00d4ff', symbol='circle'), text=[sel_name.split(',')[0]],
        textposition='top center', textfont=dict(color='#00d4ff', size=11), hovertemplate=f'{sel_name}<extra></extra>', name='Selected'
    ))

    if st.session_state.get('clicked_lat') is not None:
        fig.add_trace(go.Scattergeo(
            lat=[st.session_state['clicked_lat']], lon=[st.session_state['clicked_lon']], mode='markers',
            marker=dict(size=12, color='#f59e0b', symbol='circle'),
            hovertemplate=f"{st.session_state.get('clicked_city_name','')}<extra></extra>", name='Clicked'
        ))

    fig.update_layout(
        geo=dict(projection_type='orthographic', showland=True, landcolor='#001e35', showocean=True, oceancolor='#000d1a',
                 showcoastlines=True, coastlinecolor='rgba(0,212,255,0.25)', coastlinewidth=0.8, showcountries=True,
                 countrycolor='rgba(0,180,255,0.1)', showrivers=False, showlakes=False, showframe=False, bgcolor='rgba(0,0,0,0)',
                 lataxis=dict(showgrid=True, gridcolor='rgba(0,180,255,0.05)'), lonaxis=dict(showgrid=True, gridcolor='rgba(0,180,255,0.05)')),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=height
    )

    from data.cities import CITIES
    cities_js = json.dumps([{'name': name, 'country': info.get('country', ''), 'lat': info['lat'], 'lon': info['lon']} for name, info in CITIES.items()])
    fig_json = fig.to_json()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{ background:transparent; overflow:hidden; }}
      #globe {{ width:100%; height:{height}px; }}
      #tooltip {{ display:none; position:absolute; background:rgba(0,16,36,0.97); border:1px solid rgba(0,210,255,0.4); border-radius:10px; padding:12px 16px; pointer-events:none; z-index:999; font-family:'Inter',sans-serif; min-width:180px; backdrop-filter:blur(20px); }}
      #tooltip .city  {{ font-size:15px; font-weight:700; color:#f0f9ff; margin-bottom:2px; }}
      #tooltip .ctry  {{ font-size:12px; color:#7eb8cc; margin-bottom:4px; }}
      #tooltip .coord {{ font-size:12px; font-family:'JetBrains Mono',monospace; color:#00d4ff; margin-bottom:4px; }}
      #tooltip .val   {{ font-size:13px; font-family:'JetBrains Mono',monospace; color:#f59e0b; }}
    </style>
    </head>
    <body>
    <div id="globe"></div>
    <div id="tooltip"><div class="city" id="tt-city"></div><div class="ctry" id="tt-ctry"></div><div class="coord" id="tt-coord"></div><div class="val" id="tt-val"></div></div>
    <script>
    const CITIES = {cities_js}; const figData = {fig_json};
    Plotly.newPlot('globe', figData.data, figData.layout, {{ displayModeBar: false, scrollZoom: false, responsive: true }});
    function nearestCity(lat, lon) {{
      let best = null, bestDist = Infinity;
      CITIES.forEach(c => {{ const d = Math.sqrt(Math.pow(c.lat-lat,2) + Math.pow(c.lon-lon,2)); if(d < bestDist) {{ bestDist=d; best=c; }} }});
      return best;
    }}
    const tt = document.getElementById('tooltip'); const globe = document.getElementById('globe');
    globe.on('plotly_click', function(data) {{
      if(!data.points || !data.points.length) return;
      const pt = data.points[0]; const lat = pt.lat; const lon = pt.lon; const val = pt.marker ? pt.marker.color : null;
      const city = nearestCity(lat, lon); const cityName = city ? city.name : 'Unknown'; const country  = city ? city.country : '';
      const latStr = lat >= 0 ? lat.toFixed(2) + ' N' : Math.abs(lat).toFixed(2) + ' S';
      const lonStr = lon >= 0 ? lon.toFixed(2) + ' E' : Math.abs(lon).toFixed(2) + ' W';
      document.getElementById('tt-city').textContent  = cityName; document.getElementById('tt-ctry').textContent  = country;
      document.getElementById('tt-coord').textContent = latStr + '   ' + lonStr;
      document.getElementById('tt-val').textContent   = val !== null ? 't2m: ' + val.toFixed(1) + ' C' : '';
      const bbox = globe.getBoundingClientRect(); const ex = data.event ? data.event.clientX - bbox.left : 200; const ey = data.event ? data.event.clientY - bbox.top  : 200;
      const left = Math.min(ex + 12, bbox.width - 200); const top  = Math.max(ey - 80, 8);
      tt.style.left = left + 'px'; tt.style.top = top + 'px'; tt.style.display = 'block';
      const payload = {{ lat: lat, lon: lon, city_name: cityName, country: country, era5_value: val }};
      window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: JSON.stringify(payload) }}, '*');
    }});
    globe.on('plotly_relayout', function() {{ tt.style.display = 'none'; }});
    </script>
    </body>
    </html>
    """
    st.components.v1.html(html, height=height, scrolling=False)
    return None
