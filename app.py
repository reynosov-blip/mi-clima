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
def traer_clima(lat, lon):
    # Pedimos un solo modelo estándar para asegurar que la tabla de datos no se rompa
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

if st.button('Actualizar Pronóstico'):
    data = traer_clima(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"])
    
    if data and "hourly" in data:
        # Procesamiento directo sin vueltas
        df = pd.DataFrame({
            "Hora": pd.to_datetime(data["hourly"]["time"]),
            "Temp": data["hourly"]["temperature_2m"],
            "Lluvia": data["hourly"]["precipitation_probability"]
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp (°C)", line=dict(color='red')))
        fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia'], name="Lluvia %", marker_color='blue'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("La API no respondió. Intentá de nuevo en unos segundos.")
