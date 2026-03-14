"""
Climate data router.

Endpoints:
  GET  /api/climate/full      → full results payload (heatmap + timeseries + forecast + analogues + AI)
  GET  /api/climate/heatmap   → heatmap data only
  GET  /api/climate/timeseries→ time series only
  GET  /api/climate/datasets  → list available datasets
  POST /api/climate/upload    → upload a .nc file
"""
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Query, UploadFile, File, HTTPException

from config import settings
from models.schemas import FullClimateResponse
from services.netcdf_service import (
    load_dataset, get_heatmap_data, get_timeseries,
    compute_anomaly, get_climate_signature, get_dataset_time_range,
)
from services.forecast_service import forecast_timeseries, generate_rcp_scenarios
from services.analogue_service import (
    find_analogues, compute_future_signature, _approximate_signature,
)
from services.llm_service import explain_anomaly
from db.supabase_client import (
    upload_nc_file, save_dataset_metadata, get_datasets,
)

router = APIRouter()


def _find_nc_file(variable: str) -> str:
    """
    Find the best NetCDF file for a given variable.
    Looks in settings.data_dir for files matching variable name patterns.
    """
    data_path = settings.data_path
    # Priority: exact match → partial match → any .nc file
    for pattern in [f"*{variable}*", "*.nc"]:
        files = list(data_path.rglob(pattern))
        if files:
            return str(files[0])
    raise HTTPException(
        status_code=404,
        detail=f"No NetCDF file found for variable '{variable}'. "
               f"Add a .nc file to the '{settings.data_dir}' directory."
    )


@router.get("/full")
async def get_full_climate_data(
    lat:      float = Query(..., ge=-90,  le=90),
    lon:      float = Query(..., ge=-180, le=180),
    year:     int   = Query(..., ge=1950, le=2024),
    month:    int   = Query(..., ge=1,    le=12),
    variable: str   = Query(...),
):
    """
    Main endpoint — returns the complete payload for the results page.
    Orchestrates: heatmap + timeseries + forecast + RCP + analogues + AI.
    """
    try:
        nc_path = _find_nc_file(variable)
        ds = load_dataset(nc_path)
    except HTTPException:
        # Return placeholder response when no data files exist
        return _placeholder_response(lat, lon, year, month, variable)

    # ── Heatmap ────────────────────────────────────────────────────────────
    hm_lats, hm_lons, hm_vals = get_heatmap_data(ds, variable, year, month)

    # ── Timeseries + forecast ──────────────────────────────────────────────
    ts_years, ts_values = get_timeseries(ds, variable, lat, lon)
    anomalies   = compute_anomaly(ts_values, [1980, 2010], ts_years)
    fc          = forecast_timeseries(ts_years, ts_values)
    rcp_scen    = generate_rcp_scenarios(ts_years, ts_values)

    # ── Stats ──────────────────────────────────────────────────────────────
    cur_idx     = next((i for i, y in enumerate(ts_years) if y == year), -1)
    cur_val     = ts_values[cur_idx] if cur_idx >= 0 else ts_values[-1]
    base_vals   = [v for v, y in zip(ts_values, ts_years) if 1980 <= y <= 2010]
    base_mean   = round(sum(base_vals) / len(base_vals), 1) if base_vals else round(cur_val - 1.5, 1)
    anom_val    = round(cur_val - base_mean, 1)
    fc_2045_idx = -1
    proj_2045   = round(fc["values"][fc_2045_idx], 1) if fc.get("values") else round(base_mean + 2.1, 1)

    unit_map = {"temperature":"°C","wind_speed":"m/s","precipitation":"mm",
                "sea_level_pressure":"hPa","humidity":"%"}
    unit = unit_map.get(variable, "")

    rcp_end = lambda key: round(rcp_scen.get(key, {}).get("values", [proj_2045])[-1], 1)
    anom_sign = "+" if anom_val >= 0 else ""

    # ── Analogues ──────────────────────────────────────────────────────────
    sig_now    = _approximate_signature(float(base_mean), lat)
    sig_future = compute_future_signature(sig_now, warming_delta=2.0)
    analogues  = find_analogues(lat, lon, sig_future, n_results=4)

    # ── AI explanation ─────────────────────────────────────────────────────
    ai_text = explain_anomaly(
        variable=variable, lat=lat, lon=lon, year=year,
        value=cur_val, anomaly=anom_val, baseline=base_mean,
    )
    # Split AI text into two paragraphs
    paragraphs = [p.strip() for p in ai_text.split("\n\n") if p.strip()]
    para1 = paragraphs[0] if len(paragraphs) > 0 else ai_text[:300]
    para2 = paragraphs[1] if len(paragraphs) > 1 else ai_text[300:600]

    return {
        "stats": {
            "current_value":  f"{cur_val:.1f} {unit}",
            "baseline_mean":  f"{base_mean} {unit}",
            "anomaly":        f"{anom_sign}{anom_val} {unit}",
            "projected_2045": f"{proj_2045} {unit}",
            "record_year":    str(ts_years[ts_values.index(max(ts_values))]),
            "rcp26_proj":     f"{anom_sign}{round(rcp_end('rcp_26') - base_mean, 1)} {unit}",
            "rcp45_proj":     f"{anom_sign}{round(rcp_end('rcp_45') - base_mean, 1)} {unit}",
            "rcp85_proj":     f"{anom_sign}{round(rcp_end('rcp_85') - base_mean, 1)} {unit}",
        },
        "heatmap":   {"lats": hm_lats, "lons": hm_lons, "values": hm_vals},
        "timeseries": {
            "years":           ts_years,
            "values":          ts_values,
            "forecast_years":  fc.get("years", []),
            "forecast_values": fc.get("values", []),
            "forecast_upper":  fc.get("upper", []),
            "forecast_lower":  fc.get("lower", []),
        },
        "rcp_scenarios":  rcp_scen,
        "analogues":      analogues,
        "ai_explanation": {"paragraph1": para1, "paragraph2": para2, "metrics": []},
    }


@router.get("/datasets")
async def list_datasets():
    return get_datasets()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".nc"):
        raise HTTPException(status_code=400, detail="Only .nc files are supported.")

    content = await file.read()

    # Save locally first
    local_path = settings.data_path / file.filename
    settings.data_path.mkdir(parents=True, exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(content)

    # Upload to Supabase Storage
    try:
        file_url = upload_nc_file(file.filename, content)
    except Exception:
        file_url = str(local_path)

    # Get metadata
    meta = get_dataset_time_range(str(local_path))

    # Save to DB
    dataset_id = str(uuid.uuid4())
    try:
        save_dataset_metadata({
            "id":         dataset_id,
            "name":       file.filename,
            "source":     "user_upload",
            "variables":  meta.get("variables", []),
            "file_url":   file_url,
        })
    except Exception:
        pass  # DB save failure shouldn't break the upload response

    return {
        "dataset_id": dataset_id,
        "filename":   file.filename,
        "variables":  meta.get("variables", []),
        "time_range": {k: v for k, v in meta.items() if k != "variables"},
        "file_url":   file_url,
    }


def _placeholder_response(lat, lon, year, month, variable):
    """Returns example data when no .nc files are present (demo mode)."""
    import random, math
    rng = random.Random(int(abs(lat * 100) + abs(lon * 100) + year))
    base = 14 if variable == "temperature" else 10
    return {
        "stats": {
            "current_value": f"{round(base + rng.uniform(1,3), 1)}",
            "baseline_mean": f"{base}",
            "anomaly": f"+{round(rng.uniform(0.5, 2), 1)}",
            "projected_2045": f"{round(base + 2.5, 1)}",
            "record_year": "2023",
            "rcp26_proj": "+0.9", "rcp45_proj": "+1.8", "rcp85_proj": "+3.4",
        },
        "heatmap": {"lats": [], "lons": [], "values": []},
        "timeseries": {
            "years": list(range(1950, year+1)),
            "values": [round(base + i*0.04 + rng.uniform(-1,1), 2) for i in range(year-1949)],
            "forecast_years": list(range(year+1, 2046)),
            "forecast_values": [round(base+2.5+i*0.06, 2) for i in range(2045-year)],
            "forecast_upper":  [round(base+3.3+i*0.06, 2) for i in range(2045-year)],
            "forecast_lower":  [round(base+1.8+i*0.06, 2) for i in range(2045-year)],
        },
        "rcp_scenarios": {},
        "analogues": [],
        "ai_explanation": {
            "paragraph1": "No NetCDF data file found. Add a .nc file to the data/ directory to see real climate analysis.",
            "paragraph2": "See SETUP.md for instructions on downloading ERA5 or CESM datasets.",
            "metrics": [],
        },
    }
