import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Cargar datos
@st.cache_data
def cargar_camaras():
    return pd.read_csv("camaras.csv")

camaras_df = cargar_camaras()

# Interfaz
st.title("Simulador de Cámaras de Seguridad")
direccion = st.text_input("Ingrese una dirección (Ej: Av. Luro 3000, Mar del Plata)")

if direccion:
    geolocator = Nominatim(user_agent="simulador_camaras")
    ubicacion = geolocator.geocode(direccion)

    if ubicacion:
        lat_usuario = ubicacion.latitude
        lon_usuario = ubicacion.longitude

        # Calcular distancia a cada cámara
        def calcular_distancia(row):
            return geodesic((lat_usuario, lon_usuario), (row["latitud"], row["longitud"])).meters

        camaras_df["distancia"] = camaras_df.apply(calcular_distancia, axis=1)
        camaras_cercanas = camaras_df[camaras_df["distancia"] <= 700]

        st.write(f"Se encontraron {len(camaras_cercanas)} cámaras a menos de 700 metros.")

        # Mapa
        mapa = folium.Map(location=[lat_usuario, lon_usuario], zoom_start=15)
        folium.Marker([lat_usuario, lon_usuario], tooltip="Ubicación ingresada", icon=folium.Icon(color="red")).add_to(mapa)

        marker_cluster = MarkerCluster().add_to(mapa)
        for _, row in camaras_cercanas.iterrows():
            folium.Marker(
                [row["latitud"], row["longitud"]],
                tooltip=f"Cámara #{row['numero_camara']}"
            ).add_to(marker_cluster)

        st_folium(mapa, width=700, height=500)
    else:
        st.warning("No se pudo geocodificar la dirección.")
