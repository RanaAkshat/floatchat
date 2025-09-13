#ye query test ke liye ek chotta sa code hai 
import sqlite3
import pandas as pd

conn = sqlite3.connect("argo.db")
query = "SELECT * FROM argo_data LIMIT 5;"
df = pd.read_sql(query, conn)
print(df)
conn.close()
