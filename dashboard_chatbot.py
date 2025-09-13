import sqlite3
import pandas as pd
import streamlit as st
import pydeck as pdk
import altair as alt
import ollama

# -------------- Page Config --------------
st.set_page_config(
    page_title="🌊 FloatChat Pro Dashboard",
    page_icon="🌊",
    layout="wide",
)

# -------------- Header --------------
st.markdown(
    """
    <h1 style='text-align:center; font-size:42px; margin-bottom:0;'>🌊 FloatChat – Argo Data Pro Dashboard</h1>
    <p style='text-align:center; color:gray; font-size:18px;'>Interactive ocean data explorer + AI powered SQL chatbot</p>
    """,
    unsafe_allow_html=True,
)
st.write("")

# -------------- Sidebar Filters --------------
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Argo_floats_logo.svg/320px-Argo_floats_logo.svg.png",
    use_column_width=True
)
st.sidebar.header("🔎 Filters")

# existing sliders
lat_min, lat_max = st.sidebar.slider("Latitude Range", -90.0, 90.0, (-30.0, 30.0))
lon_min, lon_max = st.sidebar.slider("Longitude Range", 0.0, 360.0, (30.0, 60.0))
depth_min, depth_max = st.sidebar.slider(
    "Depth Range (m)", 0.0, 6000.0, (0.0, 2000.0), step=50.0
)

# new filters
date_range = st.sidebar.date_input("Date Range (time column)", [])
regions = st.sidebar.multiselect(
    "Region/Ocean",
    ["Global", "Indian Ocean", "Atlantic Ocean", "Pacific Ocean", "Southern Ocean", "Arctic Ocean"],
    default=["Global"]
)
float_id = st.sidebar.text_input("Float ID (leave blank for all)")
limit = st.sidebar.number_input("Max records to display", 100, 20000, 5000, step=500)

# -------------- Build SQL Query --------------
where_clauses = [
    f"lat BETWEEN {lat_min} AND {lat_max}",
    f"lon BETWEEN {lon_min} AND {lon_max}",
    f"depth BETWEEN {depth_min} AND {depth_max}",
]

# if user selected date range
if date_range:
    if len(date_range) == 2:
        start, end = date_range
        where_clauses.append(f"time BETWEEN '{start}' AND '{end}'")

# if float_id provided
if float_id.strip():
    where_clauses.append(f"float_id = '{float_id.strip()}'")

# if region selected but not 'Global'
if "Global" not in regions:
    # assume your DB has a 'region' or 'ocean' column
    # adjust column name accordingly
    region_list = ",".join([f"'{r}'" for r in regions])
    where_clauses.append(f"ocean IN ({region_list})")

where_sql = " AND ".join(where_clauses)
query = f"SELECT * FROM argo_data WHERE {where_sql} LIMIT {limit};"

# -------------- Fetch Data --------------
conn = sqlite3.connect("argo.db")     
# df = pd.read_sql(query, conn)  ise abhi comment out kr rau kuki isi k karan africa ka data ata hai kuki ye direct db se ara hai 
df = pd.read_pickle("argo_df_india.pkl")  # abhi ye use krunga kuki india k liye alg pkl bnaya hai taki india ka data show ho
conn.close()

# -------------- Summary Cards --------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("📍 Records", len(df))
if not df.empty:
    col2.metric("🌡 Avg Temp", f"{df['temperature'].mean():.2f} °C")
    col3.metric("🧂 Avg Salinity", f"{df['salinity'].mean():.2f}")
    col4.metric("🔎 Depth Range", f"{int(df['depth'].min())}–{int(df['depth'].max())} m")
else:
    col2.metric("🌡 Avg Temp", "-")
    col3.metric("🧂 Avg Salinity", "-")
    col4.metric("🔎 Depth Range", "-")

st.write("---")

# -------------- 3-D Globe (PyDeck) --------------
st.subheader("🌍 Interactive 3-D Globe")

if not df.empty:
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_fill_color='[255, (1 - (temperature/30)) * 255, (temperature/30) * 255]',
        get_radius=40000,
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1, min_zoom=0, max_zoom=15, pitch=30, bearing=0)

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=None,
        tooltip={"text": "Float: {float_id}\nLat: {lat}\nLon: {lon}\nTemp: {temperature} °C\nDepth: {depth} m\nSalinity: {salinity}"}
    )

    st.pydeck_chart(r, use_container_width=True)
else:
    st.warning("⚠️ No records found for selected filters.")

# -------------- Clean Charts --------------
if not df.empty:
    st.subheader("📊 Temperature & Salinity Trends")
    # time series chart
    df['time'] = pd.to_datetime(df['time'])
    temp_chart = alt.Chart(df).mark_line().encode(
        x='time:T', y='temperature:Q', color='float_id:N'
    ).properties(title="Temperature over Time")
    sal_chart = alt.Chart(df).mark_line().encode(
        x='time:T', y='salinity:Q', color='float_id:N'
    ).properties(title="Salinity over Time")

    st.altair_chart(temp_chart, use_container_width=True)
    st.altair_chart(sal_chart, use_container_width=True)

# -------------- Data Table --------------
with st.expander("📄 Show Raw Data Table"):
    st.dataframe(df, use_container_width=True, height=300)

st.write("---")

# -------------- Chatbot Panel --------------
st.subheader("🤖 Ask Questions (SQL via Ollama)")

with st.form(key="chatbot_form"):
    user_question = st.text_input("Type your question:")
    run_query = st.form_submit_button("Generate & Run")

if run_query and user_question:
    schema = """
The SQLite database has one table: argo_data
Columns: time (datetime), depth (float), lat (float), lon (float),
temperature (float), salinity (float), float_id (text), ocean (text)
Return ONLY a SQL query valid for SQLite.
"""
    prompt = f"""{schema}

Translate this natural language query to a valid SQL query:

{user_question}
"""

    response = ollama.generate(model="gemma3:latest", prompt=prompt)
    sql_query = response["response"].strip()

    if sql_query.startswith("```"):
        sql_query = sql_query.strip("`")
        if "sql" in sql_query:
            sql_query = sql_query.replace("sql", "", 1)
    sql_query = sql_query.strip()

    st.code(sql_query, language="sql")

    try:
        conn = sqlite3.connect("argo.db")
        result_df = pd.read_sql(sql_query, conn)
        conn.close()

        st.success(f"Returned {len(result_df)} rows")
        st.dataframe(result_df, use_container_width=True, height=300)
    except Exception as e:
        st.error(f"Error executing SQL: {e}")
