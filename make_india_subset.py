import pandas as pd
import numpy as np
import xarray as xr

# ====== Open dataset (.nc file) ======
file_path = "data/argo_sample.nc"  # apna file path
ds = xr.open_dataset(file_path)

# ====== Subset for India region ======
# latitude approx 5–30°N, longitude 60–100°E
time = ds['TAXIS'][:1].values        # 1 time step
depth = ds['ZAX'][:5].values         # 5 depths

# select only lat/lon in India region
lat_all = ds['YAXIS'].values
lon_all = ds['XAXIS'].values
lat_mask = (lat_all >= 5) & (lat_all <= 30)
lon_mask = (lon_all >= 60) & (lon_all <= 100)
lat = lat_all[lat_mask]
lon = lon_all[lon_mask]

# slice temperature & salinity arrays with these masks
temp = ds['TEMP'][:1, :5, lat_mask, :][:, :, :, lon_mask].values
sal = ds['SAL'][:1, :5, lat_mask, :][:, :, :, lon_mask].values

rows = []
for t_idx, t_val in enumerate(time):
    for d_idx, d_val in enumerate(depth):
        for y_idx, y_val in enumerate(lat):
            for x_idx, x_val in enumerate(lon):
                rows.append({
                    'time': np.datetime64(t_val, 's') if np.issubdtype(type(t_val), np.number) else t_val,
                    'depth': float(d_val),
                    'lat': float(y_val),
                    'lon': float(x_val),
                    'temperature': float(temp[t_idx, d_idx, y_idx, x_idx]),
                    'salinity': float(sal[t_idx, d_idx, y_idx, x_idx])
                })

df = pd.DataFrame(rows)
print(df.head())
print(df.shape)

# ====== Save as a new pickle file ======
df.to_pickle("argo_df_india.pkl")
print("✅ India region DataFrame saved to argo_df_india.pkl")
