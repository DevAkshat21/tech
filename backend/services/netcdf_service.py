"""
NetCDF Service — loads and processes climate datasets using Xarray.

NetCDF files have dimensions like (time, lat, lon) or (time, level, lat, lon).
Xarray lets us slice by label (e.g., sel(time="2010")) instead of raw indices.

Variable name aliases: ERA5 uses 't2m' for temperature, 'u10'/'v10' for wind,
'tp' for precipitation. CESM uses different names. We normalise them here.
"""
import os
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from functools import lru_cache
from typing import Tuple, Dict, List

# ── Variable name mappings (raw NC name → our canonical name) ──────────────
VARIABLE_ALIASES: Dict[str, List[str]] = {
    "temperature":       ["t2m", "tas", "temp", "temperature", "T2", "air"],
    "wind_speed":        ["si10", "wspd", "wind_speed", "sfcWind"],
    "wind_u":            ["u10", "u", "ua"],
    "wind_v":            ["v10", "v", "va"],
    "precipitation":     ["tp", "pr", "precip", "precipitation", "RAIN"],
    "sea_level_pressure":["msl", "psl", "slp", "sea_level_pressure"],
    "humidity":          ["r2", "hurs", "rh", "relative_humidity"],
}


def resolve_variable_name(ds: xr.Dataset, canonical: str) -> str:
    """
    Find the actual variable name in a Dataset for a canonical name like 'temperature'.
    Raises KeyError if not found.
    """
    aliases = VARIABLE_ALIASES.get(canonical, [canonical])
    for alias in aliases:
        if alias in ds.data_vars:
            return alias
    # Fallback: try first data variable
    available = list(ds.data_vars)
    if available:
        return available[0]
    raise KeyError(f"Variable '{canonical}' not found. Available: {list(ds.data_vars)}")


@lru_cache(maxsize=8)
def load_dataset(filepath: str) -> xr.Dataset:
    """
    Open and cache a NetCDF file. Uses LRU cache so we don't reload on every request.
    The filepath string is used as cache key.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"NetCDF file not found: {filepath}")
    ds = xr.open_dataset(filepath, engine="netcdf4", chunks="auto")
    # Normalise coordinate names to lat/lon/time if different
    rename_map = {}
    for dim in ds.dims:
        if dim.lower() in ("latitude", "lat"):
            rename_map[dim] = "lat"
        elif dim.lower() in ("longitude", "lon"):
            rename_map[dim] = "lon"
        elif dim.lower() in ("time", "t"):
            rename_map[dim] = "time"
    if rename_map:
        ds = ds.rename(rename_map)
    return ds


def get_heatmap_data(
    ds: xr.Dataset,
    variable: str,
    year: int,
    month: int,
    subsample: int = 4,
) -> Tuple[List[float], List[float], List[float]]:
    """
    Extract a 2D lat/lon slice for a given year+month.
    Returns (lats, lons, values) lists — subsampled for performance.

    subsample=4 means every 4th grid point (ERA5 is 0.25° resolution,
    so subsample=4 gives ~1° resolution — still very detailed).
    """
    var_name = resolve_variable_name(ds, variable)
    da = ds[var_name]

    # Select time slice
    if "time" in da.dims:
        target = f"{year}-{month:02d}"
        try:
            da = da.sel(time=target, method="nearest")
        except Exception:
            # Some files have integer year dimension
            da = da.isel(time=0)

    # If there's a vertical level dimension, take the surface (index 0)
    for level_dim in ("level", "lev", "plev", "pressure"):
        if level_dim in da.dims:
            da = da.isel({level_dim: 0})

    # Squeeze any remaining size-1 dims
    da = da.squeeze()

    # Convert Kelvin → Celsius for temperature
    if variable == "temperature" and da.values.mean() > 200:
        da = da - 273.15

    # Subsample
    lats_arr = da.lat.values[::subsample]
    lons_arr = da.lon.values[::subsample]
    vals_2d  = da.values[::subsample, ::subsample] if da.values.ndim == 2 else da.values

    # Flatten meshgrid → 1D lists
    lons_grid, lats_grid = np.meshgrid(lons_arr, lats_arr)
    lats_flat = lats_grid.flatten().tolist()
    lons_flat = lons_grid.flatten().tolist()
    vals_flat = np.where(np.isfinite(vals_2d.flatten()), vals_2d.flatten(), np.nan).tolist()

    # Remove NaN rows
    valid = [(la, lo, v) for la, lo, v in zip(lats_flat, lons_flat, vals_flat)
             if v == v]  # NaN != NaN
    if not valid:
        return [], [], []
    lats_out, lons_out, vals_out = zip(*valid)
    return list(lats_out), list(lons_out), [round(v, 2) for v in vals_out]


def get_timeseries(
    ds: xr.Dataset,
    variable: str,
    lat: float,
    lon: float,
) -> Tuple[List[int], List[float]]:
    """
    Extract a time series at the nearest grid point to (lat, lon).
    Returns (years, annual_means).
    """
    var_name = resolve_variable_name(ds, variable)
    da = ds[var_name]

    # Nearest point
    da = da.sel(lat=lat, lon=lon, method="nearest")

    # Drop level dims
    for level_dim in ("level", "lev", "plev"):
        if level_dim in da.dims:
            da = da.isel({level_dim: 0})

    # Convert K → C
    if variable == "temperature" and float(da.mean()) > 200:
        da = da - 273.15

    # Annual mean
    if "time" in da.dims:
        da_annual = da.resample(time="1YE").mean()
        years  = [int(t.dt.year) for t in da_annual.time]
        values = [round(float(v), 2) for v in da_annual.values]
    else:
        years  = [2000]
        values = [round(float(da.mean()), 2)]

    return years, values


def compute_anomaly(values: List[float], baseline_years: List[int],
                    years: List[int]) -> List[float]:
    """
    Compute anomaly: value - mean(baseline period).
    baseline_years: e.g. [1980, 2010]
    """
    mask = [baseline_years[0] <= y <= baseline_years[1] for y in years]
    baseline_vals = [v for v, m in zip(values, mask) if m]
    if not baseline_vals:
        return values
    baseline_mean = sum(baseline_vals) / len(baseline_vals)
    return [round(v - baseline_mean, 2) for v in values]


def get_climate_signature(
    ds: xr.Dataset,
    variable: str,
    lat: float,
    lon: float,
    year_range: Tuple[int, int] = (2040, 2050),
) -> np.ndarray:
    """
    Build a 12-element climate signature vector (monthly means) for a location.
    Used by the analogue finder to compare locations.
    """
    var_name = resolve_variable_name(ds, variable)
    da = ds[var_name].sel(lat=lat, lon=lon, method="nearest")
    for ld in ("level", "lev", "plev"):
        if ld in da.dims:
            da = da.isel({ld: 0})
    if variable == "temperature" and float(da.mean()) > 200:
        da = da - 273.15

    if "time" in da.dims:
        da_period = da.sel(
            time=slice(f"{year_range[0]}-01", f"{year_range[1]}-12"))
        if len(da_period.time) > 0:
            monthly = da_period.groupby("time.month").mean()
            sig = monthly.values
            if len(sig) == 12:
                return sig
    return np.full(12, float(da.mean()))


def list_dataset_variables(filepath: str) -> List[str]:
    """Return all variable names in a NetCDF file."""
    ds = load_dataset(filepath)
    return list(ds.data_vars)


def get_dataset_time_range(filepath: str) -> Dict:
    """Return metadata about a dataset."""
    ds = load_dataset(filepath)
    result = {"variables": list(ds.data_vars)}
    if "time" in ds.dims:
        times = pd.to_datetime(ds.time.values)
        result["start"] = str(times.min().date())
        result["end"]   = str(times.max().date())
    return result
