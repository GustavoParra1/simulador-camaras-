import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Cargar la base de datos
df_camaras = pd.read_csv("camaras_db.csv")

# Configurar geolocalizador
geolocator = Nominatim(user_agent="simulador-camaras-mdp")

# Función para obtener coordenadas de una dirección
def geolocalizar(direccion):
    location = geolocator.geocode(direccion + ", Mar del Plata, Argentina")
    if location:
        return location.latitude, location.longitude
    return None, None

# Función para filtrar cámaras en un radio de 700 metros
def filtrar_camaras(df, lat, lon):
    return df[df.apply(lambda fila: geodesic((lat, lon), (
        float(str(fila["lat"]).replace(",", ".")),
        float(str(fila["long"]).replace(",", "."))
    )).meters <= 700, axis=1)]

st.title("Simulador de Cámaras de Seguridad (MDP)")
direccion = st.text_input("Ingrese una dirección en Mar del Plata", "")

if direccion:
    lat, lon = geolocalizar(direccion)
    st.write(f"Coordenadas encontradas: lat={lat}, lon={lon}")

    if lat and lon:
        camaras_en_rango = filtrar_camaras(df_camaras, lat, lon)

        st.write(f"Se encontraron **{len(camaras_en_rango)}** cámaras en un radio de 700 metros.")
        
        mapa = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker
    for _, row in camaras_en_rango.iterrows():
    try:
        lat = float(str(row["lat"]).replace(",", "."))
        lon = float(str(row["long"]).replace(",", "."))
        folium.Marker(
            [lat, lon],
            tooltip=f"Cámara #{row.get('camara', 'N/A')}"
        ).add_to(m)
    except Exception as e:
        st.warning(f"No se pudo agregar una cámara al mapa: {e}")


        cluster = MarkerCluster().add_to(mapa)
        for _, row in camaras_en_rango.iterrows():
            folium.Marker([row["lat"], row["long"]], tooltip=f"Cámara #{row.get('camara', row.name)}").add_to(cluster)

        st_folium(mapa, width=700, height=500)
    else:
        st.error("No se pudo geolocalizar la dirección.")
