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
def obtener_clima_consenso(lat, lon):
    # Pedimos los 3 mejores modelos del mundo por separado
    modelos = ["ecmwf_ifs04", "gfs_seamless", "icon_seamless"]
    dfs = []
    
    for m in modelos:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability&models={m}&forecast_days=3"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                d = r.json()["hourly"]
                temp_df = pd.DataFrame({
                    "Hora": pd.to_datetime(d["time"]),
                    "Temp": d["temperature_2m"],
                    "Lluvia": d["precipitation_probability"]
                })
                dfs.append(temp_df)
        except:
            continue
            
    if dfs:
        # Concatenamos y promediamos: esto es el Consenso Real
        full_df = pd.concat(dfs)
        return full_df.groupby("Hora").mean().reset_index()
    return None

if st.button('Actualizar Pronóstico'):
    df = obtener_clima_consenso(ciudades[ciudad]["lat"], ciudades[ciudad]["lon"])
    
    if df is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Hora'], y=df['Temp'], name="Temperatura (°C)", line=dict(color='red', width=3)))
        fig.add_trace(go.Bar(x=df['Hora'], y=df['Lluvia'], name="Lluvia %", marker_color='blue', opacity=0.4))
        
        fig.update_layout(hovermode="x unified", height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.success("Promedio calculado de ECMWF, GFS e ICON")
    else:
        st.error("Error al conectar con los modelos. Render está reintentando.")
