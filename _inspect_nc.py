import xarray as xr
import numpy as np
import json

ds = xr.open_dataset('data/sample/era5_monthly.nc')

info = {
    "dimensions": dict(ds.sizes),
    "variables": {},
    "coordinates": {}
}

for v in ds.data_vars:
    var = ds[v]
    info["variables"][v] = {
        "shape": list(var.shape),
        "dims": list(var.dims),
        "units": var.attrs.get("units", "N/A"),
        "long_name": var.attrs.get("long_name", "N/A"),
        "standard_name": var.attrs.get("standard_name", "N/A"),
    }

for c in ds.coords:
    coord = ds[c]
    entry = {"shape": list(coord.shape), "dtype": str(coord.dtype)}
    if c in ("valid_time", "time"):
        vals = coord.values
        entry["first"] = str(vals[0])[:10]
        entry["last"] = str(vals[-1])[:10]
        entry["count"] = int(len(vals))
    elif c in ("lat", "latitude"):
        entry["min"] = float(coord.min())
        entry["max"] = float(coord.max())
    elif c in ("lon", "longitude"):
        entry["min"] = float(coord.min())
        entry["max"] = float(coord.max())
    info["coordinates"][c] = entry

print(json.dumps(info, indent=2))
