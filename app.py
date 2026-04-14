import streamlit as st
import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Mi Clima", layout="wide")

st.title("🌦️ Consenso Meteorológico Personal")

if st.button('Actualizar Pronóstico'):
    openmeteo = openmeteo_requests.Client()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -31.6333,
        "longitude": -60.7,
        "hourly": ["temperature_2m", "precipitation_probability", "wind_speed_10m"],
        "models": ["ecmwf_ifs04", "gfs_seamless", "icon_seamless"],
        "forecast_days": 3
    }
    responses = openmeteo.weather_api(url, params=params)
    
    # Procesar promedios
    t_avg = pd.DataFrame([res.Hourly().Variables(0).ValuesAsNumpy() for res in responses]).mean(axis=0)
    p_avg = pd.DataFrame([res.Hourly().Variables(1).ValuesAsNumpy() for res in responses]).mean(axis=0)
    w_avg = pd.DataFrame([res.Hourly().Variables(2).ValuesAsNumpy() for res in responses]).mean(axis=0)
    
    df = pd.DataFrame({
        "Hora": pd.date_range(start=pd.to_datetime(responses[0].Hourly().Time(), unit="s"), periods=len(t_avg), freq="1h"),
        "Temp": t_avg, "Prob_Lluvia": p_avg, "Viento": w_avg
    })

    # Gráficos
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=('Temperatura (°C)', 'Probabilidad de Lluvia (%)'))
    fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temperatura", line=dict(color='red')), row=1, col=1)
    fig.add_trace(go.Bar(x=df['Hora'], y=df['Prob_Lluvia'], name="Lluvia %", marker_color='blue'), row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
