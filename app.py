import streamlit as st
import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración
st.set_page_config(page_title="La Posta de Víctor", layout="wide")
st.title("🌦️ Pronóstico La Posta de Víctor")
st.info("Consenso de modelos: ECMWF (Europa), GFS (EE.UU.) e ICON (Alemania)")

# Ciudades
ciudades = {
    "Santa Fe": {"lat": -31.6333, "lon": -60.7},
    "Colón, Entre Ríos": {"lat": -32.2231, "lon": -58.1432}
}

ciudad_select = st.selectbox("Elegí la ciudad:", list(ciudades.keys()))

if st.button('Actualizar Pronóstico'):
    try:
        openmeteo = openmeteo_requests.Client()
        url = "https://api.open-meteo.com/v1/forecast"
        
        params = {
            "latitude": ciudades[ciudad_select]["lat"],
            "longitude": ciudades[ciudad_select]["lon"],
            "hourly": ["temperature_2m", "precipitation_probability"],
            "models": ["ecmwf_ifs04", "gfs_seamless", "icon_seamless"],
            "forecast_days": 3
        }
        
        responses = openmeteo.weather_api(url, params=params)
        
        # Promediar modelos (Consenso)
        t_avg = pd.DataFrame([res.Hourly().Variables(0).ValuesAsNumpy() for res in responses]).mean(axis=0)
        p_avg = pd.DataFrame([res.Hourly().Variables(1).ValuesAsNumpy() for res in responses]).mean(axis=0)
        
        df = pd.DataFrame({
            "Hora": pd.date_range(start=pd.to_datetime(responses[0].Hourly().Time(), unit="s"), periods=len(t_avg), freq="1h"),
            "Temperatura": t_avg, 
            "Lluvia_Prob": p_avg
        })

        # Gráficos
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Temperatura (°C)', 'Probabilidad de Lluvia (%)'))
        
        fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temperatura'], name="Temp", line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia_Prob'], name="Lluvia %", marker_color='blue'), row=2, col=1)
        
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.head(24)) # Muestra las primeras 24 horas en tabla

    except Exception as e:
        st.error(f"Hubo un problema al conectar con los modelos. Probá de nuevo en un ratito. Error: {e}")
