import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="La Posta de Víctor")
st.title("🌦️ La Posta de Víctor")

loc = {
    "Santa Fe": {"lat": -31.63, "lon": -60.70},
    "Colón": {"lat": -32.22, "lon": -58.14}
}

ciudad = st.selectbox("Elegí lugar:", list(loc.keys()))

def traer_datos(modelo):
    # Agregamos 'precipitation_probability' a la consulta
    url = f"https://api.open-meteo.com/v1/forecast?latitude={loc[ciudad]['lat']}&longitude={loc[ciudad]['lon']}&hourly=temperature_2m,precipitation,precipitation_probability,wind_speed_10m&models={modelo}&forecast_days=3&timezone=America%2FArgentina%2FBuenos_Aires"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()["hourly"]
    except:
        return None

if st.button('ACTUALIZAR PRONÓSTICO'):
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
                "Prob": data["precipitation_probability"], # NUEVA COLUMNA
                "V": data["wind_speed_10m"]
            }, index=pd.to_datetime(data["time"]))
            
            # Usamos subplots para poner la probabilidad en un eje separado (derecho)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Temperatura (Rojo)
            fig.add_trace(go.Scatter(y=df["T"], name="Temp °C", line=dict(color='red')), secondary_y=False)
            
            # Viento (Verde)
            fig.add_trace(go.Scatter(y=df["V"], name="Viento km/h", line=dict(color='green', dash='dot')), secondary_y=False)
            
            # Lluvia mm (Barras Azules)
            fig.add_trace(go.Bar(y=df["L"], name="Lluvia mm", marker_color='blue', opacity=0.4), secondary_y=False)
            
            # PROBABILIDAD (Línea Cian en el eje derecho)
            fig.add_trace(go.Scatter(y=df["Prob"], name="Prob. Lluvia %", line=dict(color='cyan', width=1)), secondary_y=True)
            
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig.update_yaxes(title_text="Temp / Viento / mm", secondary_y=False)
            fig.update_yaxes(title_text="Probabilidad %", range=[0, 100], secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{nombre}")
        else:
            st.error(f"No se pudo conectar con el modelo {nombre}")
