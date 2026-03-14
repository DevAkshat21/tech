import numpy as np
import xarray as xr
import pandas as pd

lats  = np.arange(-90, 91, 2.5)
lons  = np.arange(-180, 181, 2.5)
times = pd.date_range('1950-01', '2024-12', freq='MS')

np.random.seed(42)
data = (
    20 - np.abs(lats[:, None, None]) * 0.3
    + np.random.randn(len(lats), len(lons), len(times)) * 2
    + np.arange(len(times))[None, None, :] * 0.002
)

ds = xr.Dataset(
    {'t2m': (['lat', 'lon', 'time'], data)},
    coords={'lat': lats, 'lon': lons, 'time': times}
)
ds['t2m'].attrs['units'] = 'degC'
ds.to_netcdf('era5_temperature.nc')
print('Done — data/era5_temperature.nc created successfully')