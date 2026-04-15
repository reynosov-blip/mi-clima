import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# 1. TÍTULO DE LA PÁGINA
st.set_page_config(page_title="La Posta de Víctor")
st.title("🌦️ La Posta de Víctor")

# 2. UBICACIONES (Acá podés cambiar o agregar ciudades)
loc = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí lugar:", list(loc.keys()))

def traer_datos(modelo):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={loc[ciudad]['lat']}&longitude={loc[ciudad]['lon']}&hourly=temperature_2m,precipitation,wind_speed_10m&models={modelo}&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=15)
        return r.json()["hourly"]
    except:
        return None

if st.button('ACTUALIZAR PRONÓSTICO'):
    # 3. MODELOS (Dejamos solo los dos que pediste)
    mods = {
        "ICON (Alemania)": "icon_seamless",
        "WRF (Regional)": "best_match"
    }
    
    for nombre, m_id in mods.items():
        data = traer_datos(m_id)
        if data:
            st.subheader(f"Modelo: {nombre}")
            df = pd.DataFrame({
                "T": data["temperature_2m"],
                "L": data["precipitation"],
                "V": data["wind_speed_10m"]
            }, index=pd.to_datetime(data["time"]))
            
            fig = go.Figure()
            # Temperatura en Rojo
            fig.add_trace(go.Scatter(y=df["T"], name="Temperatura °C", line=dict(color='red')))
            # Viento en Verde
            fig.add_trace(go.Scatter(y=df["V"], name="Viento km/h", line=dict(color='green', dash='dot')))
            # Lluvia en Azul
            fig.add_trace(go.Bar(y=df["L"], name="Lluvia mm", marker_color='blue'))
            
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
            # Usamos la key para que no tire el error de ID duplicado
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{nombre}")
        else:
            st.error(f"No se pudo conectar con el modelo {nombre}")
