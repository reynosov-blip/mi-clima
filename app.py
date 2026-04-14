import streamlit as st
import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="La Posta de Víctor", layout="wide")

st.title("🌦️ Pronóstico La Posta de Víctor")

# Diccionario con las coordenadas
ciudades = {
    "Santa Fe": {"lat": -31.6333, "lon": -60.7},
    "Colón, Entre Ríos": {"lat": -32.2231, "lon": -58.1432}
}

# Selector de ciudad en la barra lateral
ciudad_select = st.selectbox("Elegí la ciudad:", list(ciudades.keys()))

if st.button('Actualizar Pronóstico'):
    lat = ciudades[ciudad_select]["lat"]
    lon = ciudades[ciudad_select]["lon"]
    
    openmeteo = openmeteo_requests.Client()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "precipitation_probability", "wind_speed_10m"],
        "models": ["ecmwf_ifs04", "gfs_seamless", "icon_seamless"],
        "forecast_days": 3
    }
    responses = openmeteo.weather_api(url, params=params)
    
    t_avg = pd.DataFrame([res.Hourly().Variables(0).ValuesAsNumpy() for res in responses]).mean(axis=0)
    p_avg = pd.DataFrame([res.Hourly().Variables(1).ValuesAsNumpy() for res in responses]).mean(axis=0)
    w_avg = pd.DataFrame([res.Hourly().Variables(2).ValuesAsNumpy() for res in responses]).mean(axis=0)
    
    df = pd.DataFrame({
        "Hora": pd.date_range(start=pd.to_datetime(responses[0].Hourly().Time(), unit="s"), periods=len(t_avg), freq="1h"),
        "Temp": t_avg, "Prob_Lluvia": p_avg, "Viento": w_avg
    })

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=(f'Temperatura en {ciudad_select} (°C)', 'Probabilidad de Lluvia (%)'))
    
    fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temp", line=dict(color='red')), row=1, col=1)
    fig.add_trace(go.Bar(x=df['Hora'], y=df['Prob_Lluvia'], name="Lluvia %", marker_color='blue'), row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
