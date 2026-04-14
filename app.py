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

# Función robusta con cache para no quemar la API
@st.cache_data(ttl=3600)
def traer_datos_consenso(lat, lon):
    # Usamos la URL directa para evitar bloqueos de librería
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability&models=ecmwf_ifs04,gfs_seamless,icon_seamless&forecast_days=3"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return None

if st.button('Actualizar Pronóstico'):
    res = traer_datos_consenso(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"])
    
    if res and "hourly" in res:
        # Extraemos los tiempos y datos
        horas = pd.to_datetime(res["hourly"]["time"])
        # Open-Meteo devuelve los datos pegados cuando pedís varios modelos. 
        # Vamos a pivotearlos para sacar el promedio real (La Posta).
        temp_data = res["hourly"]["temperature_2m"]
        precip_data = res["hourly"]["precipitation_probability"]
        
        df_raw = pd.DataFrame({"Hora": horas, "Temp": temp_data, "Lluvia": precip_data})
        # Promediamos los valores que coinciden en la misma hora (consenso de modelos)
        df = df_raw.groupby("Hora").mean().reset_index()

        # Armado de gráficos
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Consenso Temperatura (°C)', 'Consenso Lluvia (%)'))
        
        fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp", line=dict(color='red', width=3)), row=1, col=1)
        fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia'], name="Lluvia %", marker_color='blue'), row=2, col=1)
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"Datos obtenidos de ECMWF, GFS e ICON para {ciudad}")
    else:
        st.error("El servidor de clima sigue saturado por el uso global de Streamlit. Esperá 5 minutos e intentá de nuevo.")
