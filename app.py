import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="La Posta de Víctor", layout="wide")
st.title("🌦️ Pronóstico La Posta de Víctor")

ciudades = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón, Entre Ríos": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí la ciudad:", list(ciudades.keys()))

@st.cache_data(ttl=3600)
def traer_clima(lat, lon):
    # Pedimos solo los modelos de alta precisión
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability&models=ecmwf_ifs04,gfs_seamless,icon_seamless&forecast_days=3"
    r = requests.get(url)
    return r.json()

if st.button('Actualizar Pronóstico'):
    data = traer_clima(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"])
    
    if "hourly" in data:
        df = pd.DataFrame({
            "Hora": pd.to_datetime(data["hourly"]["time"]),
            "Temp": data["hourly"]["temperature_2m"],
            "Lluvia": data["hourly"]["precipitation_probability"]
        })
        
        # Agrupamos por hora para sacar el promedio de los modelos
        df = df.groupby("Hora").mean().reset_index()

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
        fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp", line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia'], name="Lluvia %"), row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("La API sigue bloqueada por exceso de uso global. Probá en un rato.")
