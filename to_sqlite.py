# ye code data ko sqlite database format mai dalta hai 
import sqlite3
import pandas as pd

# DataFrame load karo (jo tu read_argo.py se bana raha hai)
df = pd.read_pickle("argo_df.pkl")  # hum next step me save karenge

# SQLite DB banalo
conn = sqlite3.connect("argo.db")

# Data ko 'argo_data' table me daalo
df.to_sql("argo_data", conn, if_exists="replace", index=False)

conn.close()

print("Data successfully inserted into argo.db")
