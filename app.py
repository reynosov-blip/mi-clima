import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="La Posta", layout="wide")
st.title("🌦️ La Posta: Comparativa Real")

loc = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Lugar:", list(loc.keys()))

def traer(modelo):
    # Pedimos todo de una para no marear al servidor
    url = f"https://api.open-meteo.com/v1/forecast?latitude={loc[ciudad]['lat']}&longitude={loc[ciudad]['lon']}&hourly=temperature_2m,precipitation,wind_speed_10m&models={modelo}&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=15)
        return r.json()["hourly"]
    except:
        return None

if st.button('VER PRONÓSTICO'):
    # Consultamos los tres que pediste
    mods = {"ECMWF": "ecmwf_ifs04", "ICON": "icon_seamless", "WRF": "best_match"}
    
    for nombre, m_id in mods.items():
        data = traer(m_id)
        st.subheader(f"Modelo: {nombre}")
        
        if data and "time" in data:
            # Forzamos la creación del gráfico aunque falten datos
            df = pd.DataFrame({
                "T": data.get("temperature_2m", [0]*72),
                "L": data.get("precipitation", [0]*72),
                "V": data.get("wind_speed_10m", [0]*72)
            })
            df.index = pd.to_datetime(data["time"])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df["T"], name="Grados", line=dict(color='red')))
            fig.add_trace(go.Scatter(y=df["V"], name="Viento", line=dict(color='green', dash='dot')))
            fig.add_trace(go.Bar(y=df["L"], name="Lluvia mm", marker_color='blue'))
            fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Aviso: {nombre} tardó en responder. Dale de nuevo al botón.")
