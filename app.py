import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# Configuración básica
st.set_page_config(page_title="La Posta de Víctor", layout="wide")
st.title("🌦️ Pronóstico La Posta de Víctor")

ciudades = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón, Entre Ríos": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí la ciudad:", list(ciudades.keys()))

@st.cache_data(ttl=1800)
def traer_clima_seguro(lat, lon):
    # Usamos el modelo principal de alta resolución para que no haya errores de formato
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

if st.button('Actualizar Pronóstico'):
    with st.spinner('Cargando datos...'):
        data = traer_clima_seguro(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"])
        
        if data and "hourly" in data:
            # Procesamiento ultra-seguro de datos
            h = data["hourly"]
            df = pd.DataFrame({
                "Hora": pd.to_datetime(h["time"]),
                "Temperatura (°C)": h["temperature_2m"],
                "Lluvia (%)": h["precipitation_probability"]
            })

            # Gráfico de Temperatura
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df['Hora'], y=df['Temperatura (°C)'], 
                                         line=dict(color='red', width=3), name="Temp"))
            fig_temp.update_layout(title="Temperatura para los próximos 3 días", height=300)
            st.plotly_chart(fig_temp, use_container_width=True)

            # Gráfico de Lluvia
            fig_rain = go.Figure()
            fig_rain.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia (%)'], 
                                     marker_color='blue', name="Lluvia"))
            fig_rain.update_layout(title="Probabilidad de Lluvia (%)", height=300)
            st.plotly_chart(fig_rain, use_container_width=True)
            
            st.success(f"Datos actualizados para {ciudad}")
        else:
            st.error("La API de clima no respondió. Probá darle al botón de nuevo en 10 segundos.")
