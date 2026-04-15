import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="La Posta de Víctor")
st.title("🌦️ La Posta: ECMWF | ICON | WRF")

ciudades = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón, Entre Ríos": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí tu ubicación:", list(ciudades.keys()))

def traer_datos_seguro(lat, lon, modelo):
    # Pedimos solo lo básico para que la conexión no se caiga
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation&models={modelo}&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()["hourly"]
    except:
        return None
    return None

if st.button('Actualizar Pronóstico'):
    modelos = {"ECMWF": "ecmwf_ifs04", "ICON": "icon_seamless", "WRF": "best_match"}
    
    for nombre, m_id in modelos.items():
        st.subheader(f"Modelo: {nombre}")
        datos = traer_datos_seguro(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"], m_id)
        
        if datos:
            df = pd.DataFrame({"Hora": pd.to_datetime(datos["time"]), "Temp": datos["temperature_2m"], "Lluvia": datos["precipitation"]})
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp °C", line=dict(color='red')))
            fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia'], name="Lluvia mm", marker_color='blue'))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"El modelo {nombre} no respondió. Reintentá.")
