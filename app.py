import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

@st.cache_data
def cargar_camaras():
    return pd.read_csv("camaras_db.csv")

def geolocalizar_direccion(direccion):
    geolocator = Nominatim(user_agent="simulador_mdq")
    location = geolocator.geocode(direccion)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def filtrar_camaras(df, lat, lon, radio_metros=700):
    from geopy.distance import geodesic
    def en_rango(fila):
       return geodesic((lat, lon), (fila["lat"], fila["long"])).meters <= 700

    return df[df.apply(en_rango, axis=1)]

# Interfaz Streamlit
st.title("Simulador de Cámaras de Seguridad (MDP)")
direccion = st.text_input("Ingrese una dirección en Mar del Plata")

if direccion:
    lat, lon = geolocalizar_direccion(direccion)
    if lat is None:
        st.error("No se pudo geolocalizar la dirección.")
    else:
        df_camaras = cargar_camaras()
        camaras_en_rango = filtrar_camaras(df_camaras, lat, lon)

        st.markdown(f"### Cámaras encontradas: {len(camaras_en_rango)}")

        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup="Dirección ingresada", icon=folium.Icon(color='red')).add_to(m)
        cluster = MarkerCluster().add_to(m)

        for _, row in camaras_en_rango.iterrows():
            folium.Marker([row["latitud"], row["longitud"]], popup=f"Cámara {row['numero']}").add_to(cluster)

        st_data = st_folium(m, width=700, height=500)
