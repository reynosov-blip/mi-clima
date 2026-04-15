import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="La Posta de Víctor", layout="wide")
st.title("🌦️ La Posta: Selección de Modelo")

loc = {"Santa Fe": {"lat": -31.63, "lon": -60.70}, "Colón": {"lat": -32.22, "lon": -58.14}}

col_a, col_b = st.columns(2)
with col_a:
    ciudad = st.selectbox("Lugar:", list(loc.keys()))
with col_b:
    # Elegís el modelo ANTES de pedir los datos para no saturar la conexión
    modelo_txt = st.selectbox("Modelo a consultar:", ["ECMWF (Europa)", "ICON (Alemania)", "WRF (Regional)"])

mods = {"ECMWF (Europa)": "ecmwf_ifs04", "ICON (Alemania)": "icon_seamless", "WRF (Regional)": "best_match"}

if st.button('VER DATOS'):
    lat, lon = loc[ciudad]["lat"], loc[ciudad]["lon"]
    m_id = mods[modelo_txt]
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&models={m_id}&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            h = r.json()["hourly"]
            df = pd.DataFrame({
                "T": h["temperature_2m"],
                "L": h["precipitation"],
                "V": h["wind_speed_10m"]
            }, index=pd.to_datetime(h["time"]))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df["T"], name="Temp °C", line=dict(color='red')))
            fig.add_trace(go.Bar(y=df["L"], name="Lluvia mm", marker_color='blue'))
            fig.add_trace(go.Scatter(y=df["V"], name="Viento km/h", line=dict(color='green', dash='dot')))
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"Datos de {modelo_txt} cargados correctamente.")
        else:
            st.error(f"La API rechazó la conexión (Error {r.status_code}).")
    except Exception as e:
        st.error(f"Error de red: {e}")
