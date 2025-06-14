import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Configurar página
st.set_page_config(page_title="Simulador Cámaras de Seg.", layout="centered")
st.title("Simulador Cámaras de Seg. (MDP)")
st.caption("Ingrese una dirección en Mar del Plata")

# Cargar base de datos
df_camaras = pd.read_csv("camaras_db.csv", dtype=str)
df_camaras["lat"] = df_camaras["lat"].str.replace(",", ".").astype(float)
df_camaras["long"] = df_camaras["long"].str.replace(",", ".").astype(float)

# Inicializar estado
if "direccion" not in st.session_state:
    st.session_state.direccion = ""

# Entrada
st.text_input("Dirección:", key="direccion")

# Botones
col1, col2 = st.columns([1, 1])
buscar = col1.button("Buscar")
limpiar = col2.button("Limpiar dirección")

# Limpiar dirección de forma segura
if limpiar:
    # Redirigir a una función especial para limpiar sin romper la app
    st.session_state.direccion = ""
    st.experimental_rerun()

# Geolocalizador
geolocator = Nominatim(user_agent="simulador-mdp")

# Buscar si hay dirección y se presionó buscar
if buscar and st.session_state.direccion:
    try:
        ubicacion = geolocator.geocode(f"{st.session_state.direccion}, Mar del Plata, Argentina")
        if ubicacion:
            lat = ubicacion.latitude
            lon = ubicacion.longitude
            st.success(f"Coordenadas encontradas: lat={lat}, lon={lon}")

            def en_rango(fila):
                return geodesic((lat, lon), (fila["lat"], fila["long"])).meters <= 300

            camaras_en_rango = df_camaras[df_camaras.apply(en_rango, axis=1)]
            st.info(f"Se encontraron {len(camaras_en_rango)} cámaras en un radio de 300 metros.")

            mapa = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], tooltip="Dirección ingresada", icon=folium.Icon(color="red")).add_to(mapa)
            cluster = MarkerCluster().add_to(mapa)

            for _, row in camaras_en_rango.iterrows():
                numero = row.get("nro_camara", "N/A")
                folium.Marker(
                    location=[row["lat"], row["long"]],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size: 24px; color: blue; font-weight: bold;">
                            {numero}
                        </div>
                    """),
                    tooltip=f"Cámara #{numero}"
                ).add_to(cluster)

            st_folium(mapa, width=700, height=900)

        else:
            st.error("No se pudo geolocalizar la dirección.")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
