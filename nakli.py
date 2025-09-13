from netCDF4 import Dataset 
import pandas as pd
import numpy as np
import xarray as xr

# ---- Dataset load karo ----
file_path = "data/argo_sample.nc"
# netCDF4 se info check karne ke liye
ds_info = Dataset(file_path, "r")
print(ds_info)                # dataset info
print(ds_info.variables.keys())  # variables list
ds_info.close()

# xarray se data use karne ke liye
ds = xr.open_dataset(file_path)

# ye vala code 1.9 crore data points k liye hai bht bada ram pe load jada padega or chalne mai time lega

# import pandas as pd
# import numpy as np
# import xarray as xr

# file_path = "data/argo_sample.nc"
# ds = xr.open_dataset(file_path)

# # Longitude, Latitude, Depth, Time arrays
# lon = ds['XAXIS'].values
# lat = ds['YAXIS'].values
# depth = ds['ZAX'].values
# time = ds['TAXIS'].values

# # Temperature and Salinity arrays
# temp = ds['TEMP'].values  # shape: (time, depth, lat, lon)
# sal = ds['SAL'].values

# rows = []
# for t_idx, t_val in enumerate(time):
#     for d_idx, d_val in enumerate(depth):
#         for y_idx, y_val in enumerate(lat):
#             for x_idx, x_val in enumerate(lon):
#                 rows.append({
#                     'time': np.datetime64(t_val, 's') if np.issubdtype(type(t_val), np.number) else t_val,
#                     'depth': float(d_val),
#                     'lat': float(y_val),
#                     'lon': float(x_val),
#                     'temperature': float(temp[t_idx, d_idx, y_idx, x_idx]),
#                     'salinity': float(sal[t_idx, d_idx, y_idx, x_idx])
#                 })

# df = pd.DataFrame(rows)
# print(df.head())
# print(df.shape)

# ye vala data chota hai 500 data points ka fast chalega 

# ====== SUBSET CHOOSE KARO ======
# sirf pehla 1 time step, pehle 5 depth
time = ds['TAXIS'][:1].values        # 1 time
depth = ds['ZAX'][:5].values         # 5 depth

# saare lat/lon arrays lo
all_lat = ds['YAXIS'].values
all_lon = ds['XAXIS'].values

# India ke liye mask banao
lat_mask = (all_lat >= 6) & (all_lat <= 37)
lon_mask = (all_lon >= 68) & (all_lon <= 97)

# mask apply karo aur sirf first 10 hi lo (zyada chahiye to :10 hata do ya bada do)
lat = all_lat[lat_mask][:10]
lon = all_lon[lon_mask][:10]

# TEMP/SAL pe bhi wahi mask lagana hai
temp = ds['TEMP'][:1, :5, lat_mask, :][:, :, :, lon_mask][:, :, :len(lat), :len(lon)].values
sal = ds['SAL'][:1, :5, lat_mask, :][:, :, :, lon_mask][:, :, :len(lat), :len(lon)].values

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
df.to_pickle("argo_df_india.pkl")
print("India region DataFrame saved to argo_df_india.pkl")







# ye hi code argo data ko read karta hai fir readble format mai convert karta hai
from netCDF4 import Dataset 


file_path = "data/argo_sample.nc"
ds = Dataset(file_path, "r")

print(ds)                # dataset info
print(ds.variables.keys())  # variables list

# ye vala code 1.9 crore data points k liye hai bht bada ram pe load jada padega or chalne mai time lega

# import pandas as pd
# import numpy as np
# import xarray as xr

# file_path = "data/argo_sample.nc"
# ds = xr.open_dataset(file_path)

# # Longitude, Latitude, Depth, Time arrays
# lon = ds['XAXIS'].values
# lat = ds['YAXIS'].values
# depth = ds['ZAX'].values
# time = ds['TAXIS'].values

# # Temperature and Salinity arrays
# temp = ds['TEMP'].values  # shape: (time, depth, lat, lon)
# sal = ds['SAL'].values

# rows = []
# for t_idx, t_val in enumerate(time):
#     for d_idx, d_val in enumerate(depth):
#         for y_idx, y_val in enumerate(lat):
#             for x_idx, x_val in enumerate(lon):
#                 rows.append({
#                     'time': np.datetime64(t_val, 's') if np.issubdtype(type(t_val), np.number) else t_val,
#                     'depth': float(d_val),
#                     'lat': float(y_val),
#                     'lon': float(x_val),
#                     'temperature': float(temp[t_idx, d_idx, y_idx, x_idx]),
#                     'salinity': float(sal[t_idx, d_idx, y_idx, x_idx])
#                 })

# df = pd.DataFrame(rows)
# print(df.head())
# print(df.shape)

# ye vala data chota hai 500 data points ka fast chalega 

import pandas as pd
import numpy as np
import xarray as xr

file_path = "data/argo_sample.nc"
ds = xr.open_dataset(file_path)

# ====== SUBSET CHOOSE KARO ======
# sirf pehla 1 time step, pehle 5 depth, 10 latitudes, 10 longitudes
time = ds['TAXIS'][:1].values        # 1 time
depth = ds['ZAX'][:5].values         # 5 depth
lat = ds['YAXIS'][:10].values        # 10 latitudes
lon = ds['XAXIS'][:10].values        # 10 longitudes

temp = ds['TEMP'][:1, :5, :10, :10].values
sal = ds['SAL'][:1, :5, :10, :10].values

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
df.to_pickle("argo_df.pkl")
print("DataFrame saved to argo_df.pkl")