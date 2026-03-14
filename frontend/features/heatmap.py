import xarray as xr
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def render_heatmap(
    _ds: xr.Dataset,
    year: int,
    month: int,
    variable: str
) -> go.Figure:
    COLORSCALES = {
        'Temperature':   'RdBu_r',
        'Precipitation': 'Blues',
        'Wind Speed':    'Viridis',
        'Humidity':      'YlGnBu',
    }
    UNITS = {
        'Temperature':   'C',
        'Precipitation': 'mm',
        'Wind Speed':    'm/s',
        'Humidity':      '%',
    }
    try:
        time_mask = ((_ds.time.dt.year == year) & (_ds.time.dt.month == month))
        data_slice = _ds.t2m.sel(time=time_mask).squeeze()
        if data_slice.dims == (): raise ValueError("Empty slice")
    except Exception:
        data_slice = _ds.t2m.isel(time=0)

    lats = data_slice.lat.values[::3]
    lons = data_slice.lon.values[::3]
    vals = data_slice.values[::3, ::3]

    lat_g, lon_g = np.meshgrid(lats, lons, indexing='ij')
    lat_flat = lat_g.flatten()
    lon_flat = lon_g.flatten()
    val_flat = vals.flatten()
    mask = ~np.isnan(val_flat)

    colorscale = COLORSCALES.get(variable, 'RdBu_r')
    unit = UNITS.get(variable, '')

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=lat_flat[mask], lon=lon_flat[mask], mode='markers',
        marker=dict(
            size=4, color=val_flat[mask], colorscale=colorscale, opacity=0.8,
            colorbar=dict(title=dict(text=unit, font=dict(color='#7eb8cc', family='Inter')), thickness=14, len=0.65, bgcolor='rgba(0,0,0,0)',
                          bordercolor='rgba(0,180,255,0.2)', tickfont=dict(color='#7eb8cc', size=10, family='Inter')),
        ),
        hovertemplate='%{lat:.1f}N, %{lon:.1f}E<br>%{marker.color:.1f} ' + unit + '<extra></extra>',
    ))

    sel_lat = st.session_state.get('selected_lat', 48.86)
    sel_lon = st.session_state.get('selected_lon', 2.35)
    sel_name = st.session_state.get('selected_location_name', '')

    fig.add_trace(go.Scattergeo(
        lat=[sel_lat], lon=[sel_lon], mode='markers+text',
        marker=dict(size=12, color='#00d4ff', symbol='circle'),
        text=[sel_name.split(',')[0]], textposition='top center',
        textfont=dict(color='#00d4ff', size=12, family='Inter'),
        hovertemplate=f'{sel_name}<extra></extra>'
    ))

    fig.update_layout(
        geo=dict(showland=True, landcolor='#001428', showocean=True, oceancolor='#000d1a',
                 showcoastlines=True, coastlinecolor='rgba(0,212,255,0.2)', coastlinewidth=0.6,
                 showcountries=True, countrycolor='rgba(0,180,255,0.08)', bgcolor='rgba(0,0,0,0)',
                 showframe=False, projection_type='natural earth'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False, height=480, font=dict(color='#7eb8cc', family='Inter')
    )
    return fig

def render_heatmap_controls(_ds: xr.Dataset, variable: str) -> int:
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
    return year
