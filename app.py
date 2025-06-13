import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Cargar base de datos
df = pd.read_csv("camaras_db.csv")

# Asegurar lat/long como float
df["lat"] = df["lat"].astype(float)
df["long"] = df["long"].astype(float)

# Interfaz
st.title("Simulador de Cámaras de Seguridad (MDP)")
direccion = st.text_input("Ingrese una dirección en Mar del Plata")

if direccion:
    geolocator = Nominatim(user_agent="simulador-mdp")
    try:
        loc = geolocator.geocode(f"{direccion}, Mar del Plata, Argentina")
        if loc:
            lat_u, lon_u = loc.latitude, loc.longitude
            st.success(f"Coordenadas encontradas: lat={lat_u}, lon={lon_u}")

            # Filtrar cámaras a 300 m
            df["distancia"] = df.apply(lambda r: geodesic((lat_u, lon_u), (r["lat"], r["long"])).meters, axis=1)
            df_ok = df[df["distancia"] <= 300]
            st.info(f"Se encontraron {len(df_ok)} cámaras en un radio de 300 metros.")

            # Crear mapa
            m = folium.Map(location=[lat_u, lon_u], zoom_start=16)
            folium.Marker([lat_u, lon_u], popup="Dirección ingresada", icon=folium.Icon(color="red")).add_to(m)
            cluster = MarkerCluster().add_to(m)

            for _, row in df_ok.iterrows():
                folium.Marker(
                  [row["lat"], row["long"]],
                  icon=folium.DivIcon(html=f"<div style='font-size:12px;color:blue;font-weight:bold'>{row.get('nro_camara', 'N/A')}</div>"),
                  tooltip=f"Cámara #{row.get('nro_camara', 'N/A')}"
                ).add_to(cluster)

            st_folium(m, width=700, height=500)
        else:
            st.error("No se pudo geolocalizar la dirección.")
    except Exception as e:
        st.error(f"Error al geolocalizar: {e}")
