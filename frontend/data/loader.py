import xarray as xr
import numpy as np
import pandas as pd

def load_dataset():
    # Mock dataset matching ERA5
    time = pd.date_range('1950-01-01', '2024-12-31', freq='MS')
    lat = np.linspace(-90, 90, 10)
    lon = np.linspace(-180, 180, 20)
    data = np.random.rand(len(time), len(lat), len(lon)) * 30
    
    ds = xr.Dataset(
        {"t2m": (["time", "lat", "lon"], data)},
        coords={"time": time, "lat": lat, "lon": lon}
    )
    return ds
