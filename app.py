import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="La Posta de Víctor", layout="wide")
st.title("🌦️ La Posta: ECMWF | ICON | WRF")

ciudades = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón, Entre Ríos": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí tu ubicación:", list(ciudades.keys()))

@st.cache_data(ttl=1800)
def traer_datos(lat, lon, modelo):
    vars = "temperature_2m,precipitation_probability,precipitation,wind_speed_10m"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={vars}&models={modelo}&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            h = r.json()["hourly"]
            return pd.DataFrame({
                "Hora": pd.to_datetime(h["time"]),
                "Temp": h["temperature_2m"],
                "Prob_Lluvia": h["precipitation_probability"],
                "Lluvia_mm": h["precipitation"],
                "Viento": h["wind_speed_10m"]
            })
    except: return None

if st.button('Actualizar Pronóstico'):
    modelos_lista = {
        "ECMWF (Europa)": "ecmwf_ifs04",
        "ICON (Alemania)": "icon_seamless",
        "WRF (Regional)": "best_match" 
    }
    
    for nombre, m_id in modelos_lista.items():
        st.markdown(f"### {nombre}")
        df = traer_datos(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"], m_id)
        
        if df is not None:
            # Gráfico de Temperatura y Viento
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp °C", line=dict(color='red', width=3)))
            fig.add_trace(go.Scatter(x=df['Hora'], y=df['Viento'], name="Viento km/h", line=dict(color='green', dash='dot')), secondary_y=True)
            fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Gráfico de Lluvia (Barras para mm, línea para %)
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia_mm'], name="mm", marker_color='blue'))
            fig2.add_trace(go.Scatter(x=df['Hora'], y=df['Prob_Lluvia'], name="%", line=dict(color='cyan')), secondary_y=True)
            fig2.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("---")
        else:
            st.error(f"No se pudo conectar con {nombre}")
