# dashboard_pro.py
import sqlite3
from typing import Tuple
import io
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------- CONFIG (edit if your column names differ) ----------
DB_PATH = "argo.db"
TABLE_NAME = "argo_data"

# column names in your table (change if different)
COL_TIME = "time"
COL_LAT = "lat"
COL_LON = "lon"
COL_DEPTH = "depth"
COL_TEMP = "temperature"
COL_SAL = "salinity"

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="🌊 FloatChat - Pro Dashboard", layout="wide", initial_sidebar_state="expanded")

# top header
st.markdown(
    """
    <div style="display:flex;align-items:center;gap:12px">
      <h1 style="margin:0">🌊 FloatChat</h1>
      <div style="color:gray;margin-left:6px">— ARGO data explorer (Interactive · Query · Download)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- HELP / INSTRUCTIONS ----------
with st.expander("How to use this dashboard (quick) ▶", expanded=False):
    st.write(
        """
        1. Use the filters in the left sidebar to limit region, time, depth and variable.  
        2. Map shows float observations (click/hover to inspect).  
        3. Use the table or Download button to export results as CSV.  
        4. If you use the chatbot, it will generate SQL based on available schema.
        """
    )

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")

# Connect to DB to get global bounds (cached)
@st.cache_data(ttl=300)
def get_db_stats(db_path: str, table: str) -> Tuple[float, float, float, float, str, str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # min/max lat lon
    cur.execute(f"SELECT MIN({COL_LAT}), MAX({COL_LAT}), MIN({COL_LON}), MAX({COL_LON}) FROM {table}")
    lat_min_db, lat_max_db, lon_min_db, lon_max_db = cur.fetchone()
    # min/max time
    try:
        cur.execute(f"SELECT MIN({COL_TIME}), MAX({COL_TIME}) FROM {table}")
        tmin, tmax = cur.fetchone()
    except Exception:
        tmin, tmax = None, None
    conn.close()
    return lat_min_db, lat_max_db, lon_min_db, lon_max_db, tmin, tmax

lat_min_db, lat_max_db, lon_min_db, lon_max_db, tmin_db, tmax_db = get_db_stats(DB_PATH, TABLE_NAME)

# sliders & pickers
lat_range = st.sidebar.slider(
    "Latitude range",
    float(lat_min_db or -90.0),
    float(lat_max_db or 90.0),
    (float(lat_min_db or -30.0), float(lat_max_db or 30.0)),
    step=0.1,
)

lon_range = st.sidebar.slider(
    "Longitude range",
    float(lon_min_db or 0.0),
    float(lon_max_db or 360.0),
    (float(lon_min_db or 30.0), float(lon_max_db or 60.0)),
    step=0.1,
)

# time selection (if tmin/tmax available)
if tmin_db and tmax_db:
    try:
        tmin = pd.to_datetime(tmin_db)
        tmax = pd.to_datetime(tmax_db)
        time_range = st.sidebar.date_input("Date range", [tmin.date(), tmax.date()])
    except Exception:
        time_range = None
else:
    time_range = None

depth_min, depth_max = st.sidebar.slider("Depth range (meters)", 0.0, 6000.0, (0.0, 2000.0), step=1.0)
variable = st.sidebar.selectbox("Color by variable", ["temperature", "salinity"], index=0)
max_points = st.sidebar.number_input("Max points to show on map", min_value=100, max_value=20000, value=5000, step=100)

download_button = st.sidebar.checkbox("Show Download Button", value=True)

# ---------- DATA FETCH (cached for speed) ----------
@st.cache_data(ttl=60)
def fetch_data(db_path: str, table: str, lat_rng, lon_rng, t_range, depth_rng, max_rows: int) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    where_clauses = []
    where_clauses.append(f"{COL_LAT} BETWEEN {lat_rng[0]} AND {lat_rng[1]}")
    where_clauses.append(f"{COL_LON} BETWEEN {lon_rng[0]} AND {lon_rng[1]}")
    where_clauses.append(f"{COL_DEPTH} BETWEEN {depth_rng[0]} AND {depth_rng[1]}")
    if t_range:
        t0 = pd.to_datetime(t_range[0]).strftime("%Y-%m-%d")
        t1 = pd.to_datetime(t_range[1]).strftime("%Y-%m-%d")
        where_clauses.append(f"date({COL_TIME}) BETWEEN '{t0}' AND '{t1}'")
    where_sql = " AND ".join(where_clauses)
    query = f"SELECT * FROM {table} WHERE {where_sql} LIMIT {int(max_rows)};"
    df = pd.read_sql(query, conn, parse_dates=[COL_TIME])
    conn.close()
    return df

with st.spinner("Fetching data..."):
    df = fetch_data(DB_PATH, TABLE_NAME, lat_range, lon_range, time_range, (depth_min, depth_max), max_points)

# ---------- TOP METRICS ----------
col1, col2, col3, col4 = st.columns(4)
if not df.empty:
    col1.metric("Records", f"{len(df):,}")
    col2.metric("Avg Temp (°C)", f"{df[COL_TEMP].mean():.2f}")
    col3.metric("Avg Salinity", f"{df[COL_SAL].mean():.2f}")
    col4.metric("Depth range (m)", f"{df[COL_DEPTH].min():.1f} - {df[COL_DEPTH].max():.1f}")
else:
    col1.metric("Records", "0")
    col2.metric("Avg Temp (°C)", "—")
    col3.metric("Avg Salinity", "—")
    col4.metric("Depth range (m)", "—")

st.markdown("---")

# ---------- MAP: interactive scatter_mapbox ----------
st.subheader("Map — Observations")
if df.empty:
    st.info("No records match the filters. Try widening filters or increase 'Max points' in the sidebar.")
else:
    # color variable selection
    color_col = COL_TEMP if variable == "temperature" else COL_SAL
    mapbox_style = "open-street-map"  # works without token

    fig_map = px.scatter_mapbox(
        df,
        lat=COL_LAT,
        lon=COL_LON,
        color=color_col,
        hover_name=COL_TIME,
        hover_data={COL_DEPTH: True, COL_TEMP: True, COL_SAL: True},
        zoom=3,
        height=600,
        size_max=8,
    )
    fig_map.update_layout(mapbox_style=mapbox_style, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

# ---------- PROFILE PLOT: depth vs variable (mean profile) ----------
st.subheader("Depth profile (averaged)")
if df.empty:
    st.info("No profile to show.")
else:
    # compute mean per depth bin
    try:
        # create depth bins
        bins = list(range(int(max(0, depth_min)), int(depth_max)+1, max(1, int((depth_max-depth_min)//20))))
        df['depth_bin'] = pd.cut(df[COL_DEPTH], bins=bins, labels=[f"{int(b)}" for b in bins[:-1]])
        profile = df.groupby('depth_bin')[[COL_TEMP, COL_SAL]].mean().reset_index()
        profile = profile.dropna()
        if not profile.empty:
            # invert y-axis for depth
            fig_prof = px.line(profile, x=COL_TEMP if variable=="temperature" else COL_SAL, y="depth_bin",
                               orientation='h', markers=True,
                               labels={'depth_bin':'Depth (m)', COL_TEMP:'Temp (°C)', COL_SAL:'Salinity'})
            fig_prof.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_prof, use_container_width=True)
        else:
            st.info("Not enough profile data for the selected depth range.")
    except Exception as e:
        st.error(f"Profile error: {e}")

# ---------- TABLE + DOWNLOAD ----------
st.subheader("Data table")
if not df.empty:
    st.dataframe(df, height=300)

    if download_button:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="⬇️ Download CSV", data=csv, file_name="argo_query_result.csv", mime="text/csv")
else:
    st.write("No data to show in table.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<small>Built with ❤️ · Streamlit · Ollama · SQLite · Plotly</small>", unsafe_allow_html=True)
