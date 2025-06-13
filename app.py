import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Cargar base de datos de cámaras
df_camaras = pd.read_csv("camaras_db.csv")

# Asegurar que lat y long estén en formato float
df_camaras["lat"] = df_camaras["lat"].astype(float)
df_camaras["long"] = df_camaras["long"].astype(float)

# Encabezado
st.title("Simulador de Cámaras de Seguridad (MDP)")
direccion = st.text_input("Ingrese una dirección en Mar del Plata", "jujuy 1500")

# Geolocalizar dirección
if direccion:
    geolocator = Nominatim(user_agent="simulador-mdp")
    try:
        location = geolocator.geocode(f"{direccion}, Mar del Plata, Argentina")
        if location:
            lat_usuario, lon_usuario = location.latitude, location.longitude
            st.success(f"Coordenadas encontradas: lat={lat_usuario}, lon={lon_usuario}")

            # Calcular distancias
            df_camaras["distancia"] = df_camaras.apply(
                lambda row: geodesic(
                    (lat_usuario, lon_usuario), (row["lat"], row["long"])
                ).meters,
                axis=1,
            )
            camaras_en_rango = df_camaras[df_camaras["distancia"] <= 700]

            st.info(f"Se encontraron {len(camaras_en_rango)} cámaras en un radio de 700 metros.")

            # Crear mapa
            m = folium.Map(location=[lat_usuario, lon_usuario], zoom_start=16)
            folium.Marker(
                location=[lat_usuario, lon_usuario],
                popup="Dirección ingresada",
                icon=folium.Icon(color="red"),
            ).add_to(m)

            cluster = MarkerCluster().add_to(m)

            # Agregar cámaras con número
            for _, row in camaras_en_rango.iterrows():
                lat_cam = row["lat"]
                lon_cam = row["long"]
                numero = row.get("nro_camara", "N/A")  # Cambiar si la columna tiene otro nombre

                folium.Marker(
                    location=[lat_cam, lon_cam],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size: 12px; color: blue; font-weight: bold;">
                            {numero}
                        </div>
                    """),
                    tooltip=f"Cámara #{numero}"
                ).add_to(cluster)

            # Mostrar mapa
            st_data = st_folium(m, width=700, height=500)

        else:
            st.error("No se pudo geolocalizar la dirección.")
    except Exception as e:
        st.error(f"Error al geolocalizar: {e}")

