"""
HTTP client for calling the FastAPI backend.
All frontend → backend communication goes through here.
Falls back to mock data if backend is unavailable (useful during UI development).
"""
import os
import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30.0


def _get(path: str, params: dict = None) -> dict:
    url = f"{BACKEND_URL}{path}"
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.warning(f"⚠️ Backend unavailable ({e}). Using placeholder data.")
        return {}


def _post(path: str, body: dict) -> dict:
    url = f"{BACKEND_URL}{path}"
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.post(url, json=body)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.warning(f"⚠️ Backend unavailable ({e}). Using placeholder data.")
        return {}


# ── Public API ──────────────────────────────────────────────────────────────

def fetch_climate_data(lat: float, lon: float, year: int,
                        month: int, variable: str) -> dict:
    """
    Fetches the full results payload for one location/time/variable.
    Returns a dict consumed by results.py:
      { stats, heatmap, timeseries, rcp_scenarios, analogues, ai_explanation }
    """
    data = _get("/api/climate/full", params=dict(
        lat=lat, lon=lon, year=year, month=month, variable=variable
    ))
    if not data:
        data = _mock_data(lat, lon, year, month, variable)
    return data


def fetch_ai_explanation(variable: str, lat: float, lon: float,
                          year: int, question: str = None) -> str:
    """Ask the AI analyst a question about a specific data point."""
    body = dict(variable=variable, lat=lat, lon=lon, year=year, question=question)
    resp = _post("/api/ai/explain", body)
    return resp.get("explanation", "AI analyst is unavailable. Please check your API key.")


def fetch_forecast(lat: float, lon: float, variable: str) -> dict:
    return _get("/api/forecast", params=dict(lat=lat, lon=lon, variable=variable))


def fetch_analogues(lat: float, lon: float, variable: str, target_year: int = 2050) -> list:
    data = _get("/api/forecast/analogues", params=dict(
        lat=lat, lon=lon, variable=variable, target_year=target_year
    ))
    return data.get("analogues", [])


def upload_nc_file(file_bytes: bytes, filename: str) -> dict:
    url = f"{BACKEND_URL}/api/climate/upload"
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(url, files={"file": (filename, file_bytes, "application/octet-stream")})
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return {}


# ── Mock data (UI development / backend offline) ────────────────────────────

def _mock_data(lat, lon, year, month, variable) -> dict:
    import random, math
    rng = random.Random(int(abs(lat * 100) + abs(lon * 100) + year + month))

    def wave(n, base, amp, noise=0.5):
        return [base + amp * math.sin(i / n * 2 * math.pi) + rng.uniform(-noise, noise)
                for i in range(n)]

    years_hist = list(range(1950, year + 1))
    hist_vals  = [12 + i * 0.04 + rng.uniform(-1, 1) for i in range(len(years_hist))]

    fc_years  = list(range(year + 1, 2046))
    fc_base   = hist_vals[-1] if hist_vals else 14
    fc_vals   = [fc_base + i * 0.06 + rng.uniform(-0.3, 0.3) for i in range(len(fc_years))]

    # Heatmap (sparse sample)
    hm_lats, hm_lons, hm_vals = [], [], []
    for flat in range(-80, 81, 5):
        for flon in range(-180, 181, 5):
            hm_lats.append(flat)
            hm_lons.append(flon)
            hm_vals.append(20 - abs(flat) * 0.3 + rng.uniform(-4, 4))

    cur = round(hist_vals[-1] if hist_vals else 14.2, 1)
    base_mean = round(sum(hist_vals[:30]) / 30, 1)
    anom = round(cur - base_mean, 1)

    return {
        "stats": {
            "current_value": f"{cur}",
            "baseline_mean": f"{base_mean} °C",
            "anomaly":       f"{abs(anom)} °C",
            "projected_2045": f"{round(fc_base + 1.5, 1)} °C",
            "record_year":   "2023",
            "rcp26_proj":    f"+{round(0.8 + rng.uniform(0,0.4), 1)} °C",
            "rcp45_proj":    f"+{round(1.8 + rng.uniform(0,0.4), 1)} °C",
            "rcp85_proj":    f"+{round(3.5 + rng.uniform(0,0.5), 1)} °C",
        },
        "heatmap": {"lats": hm_lats, "lons": hm_lons, "values": hm_vals},
        "timeseries": {
            "years":           years_hist,
            "values":          [round(v, 2) for v in hist_vals],
            "forecast_years":  fc_years,
            "forecast_values": [round(v, 2) for v in fc_vals],
            "forecast_upper":  [round(v + 0.8, 2) for v in fc_vals],
            "forecast_lower":  [round(v - 0.5, 2) for v in fc_vals],
        },
        "rcp_scenarios": {
            "rcp_26": {
                "years":  list(range(1950, 2046)),
                "values": [12 + i * 0.025 + rng.uniform(-0.5, 0.5) for i in range(96)],
                "upper":  [12 + i * 0.03  + 0.6 for i in range(96)],
                "lower":  [12 + i * 0.02  - 0.4 for i in range(96)],
            },
            "rcp_45": {
                "years":  list(range(1950, 2046)),
                "values": [12 + i * 0.04  + rng.uniform(-0.5, 0.5) for i in range(96)],
                "upper":  [12 + i * 0.045 + 0.7 for i in range(96)],
                "lower":  [12 + i * 0.035 - 0.5 for i in range(96)],
            },
            "rcp_85": {
                "years":  list(range(1950, 2046)),
                "values": [12 + i * 0.07  + rng.uniform(-0.5, 0.5) for i in range(96)],
                "upper":  [12 + i * 0.075 + 0.9 for i in range(96)],
                "lower":  [12 + i * 0.065 - 0.6 for i in range(96)],
            },
        },
        "analogues": [
            {"city": "Barcelona, Spain",  "lat": 41.38, "lon": 2.17,  "meta": "21.4°C avg · 52mm rain", "match_score": 97},
            {"city": "Porto, Portugal",   "lat": 41.15, "lon": -8.61, "meta": "19.8°C avg · 61mm rain", "match_score": 94},
            {"city": "Milan, Italy",      "lat": 45.46, "lon": 9.19,  "meta": "20.1°C avg · 48mm rain", "match_score": 91},
            {"city": "Istanbul, Turkey",  "lat": 41.01, "lon": 28.95, "meta": "18.9°C avg · 44mm rain", "match_score": 88},
        ],
        "ai_explanation": {
            "paragraph1": f"{variable} at {lat:.1f}°N, {lon:.1f}°E in {year} showed a significant deviation from the historical baseline. This anomaly is consistent with long-term warming patterns observed across the region.",
            "paragraph2": f"The event is linked to shifts in atmospheric circulation patterns and ocean surface temperatures. Under current emission trajectories, such deviations are projected to become more frequent and intense through 2050.",
            "metrics": [],
        },
    }
