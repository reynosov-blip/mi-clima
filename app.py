import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="La Posta de Víctor")
st.title("🌦️ Pronóstico La Posta de Víctor")

ciudades = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón, Entre Ríos": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí la ciudad:", list(ciudades.keys()))

@st.cache_data(ttl=1800)
def obtener_clima(lat, lon):
    # Pedimos el promedio de los 3 modelos (ECMWF, GFS, ICON)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability&models=ecmwf_ifs04,gfs_seamless,icon_seamless&forecast_days=3"
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        return r.json()
    return None

if st.button('Actualizar Pronóstico'):
    data = obtener_clima(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"])
    
    if data and "hourly" in data:
        df = pd.DataFrame({
            "Hora": pd.to_datetime(data["hourly"]["time"]),
            "Temp": data["hourly"]["temperature_2m"],
            "Lluvia": data["hourly"]["precipitation_probability"]
        }).groupby("Hora").mean().reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp (°C)", line=dict(color='red')))
        fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia'], name="Lluvia %", marker_color='blue', opacity=0.5))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Error de conexión. Intentá de nuevo.")
