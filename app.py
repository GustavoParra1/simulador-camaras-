import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Configuración de página ancha
st.set_page_config(page_title="Simulador Cámaras de Seg.", layout="wide")

# Título con logo a la derecha
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("<h1 style='margin-bottom: 0;'>Simulador Cámaras de Seg. (MDP)</h1>", unsafe_allow_html=True)
    st.caption("Ingrese una dirección en Mar del Plata")
with col2:
    st.image("logo calado.png", width=100)

# Entrada
st.markdown("**Dirección:**")
direccion = st.text_input("", placeholder="Ej. Salta 3200")

# Botón buscar
buscar = st.button("🔍 Buscar")

# Cargar base de datos
df_camaras = pd.read_csv("camaras_db.csv", dtype=str)
df_camaras["lat"] = df_camaras["lat"].str.replace(",", ".").astype(float)
df_camaras["long"] = df_camaras["long"].str.replace(",", ".").astype(float)

# Geolocalizador
geolocator = Nominatim(user_agent="simulador-mdp")

# Lógica de búsqueda
if buscar and direccion:
    try:
        ubicacion = geolocator.geocode(f"{direccion}, Mar del Plata, Argentina")
        if ubicacion:
            lat = ubicacion.latitude
            lon = ubicacion.longitude
            st.success(f"Coordenadas encontradas: lat={lat:.6f}, lon={lon:.6f}")

            # Calcular cámaras en radio de 300 metros
            def en_rango(fila):
                return geodesic((lat, lon), (fila["lat"], fila["long"])).meters <= 300

            camaras_en_rango = df_camaras[df_camaras.apply(en_rango, axis=1)]

            st.info(f"Se encontraron {len(camaras_en_rango)} cámaras en un radio de 300 metros.")

            # Crear mapa
            mapa = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], tooltip="Dirección ingresada", icon=folium.Icon(color="red")).add_to(mapa)

            cluster = MarkerCluster().add_to(mapa)
            for _, row in camaras_en_rango.iterrows():
                folium.Marker(
                    location=[row["lat"], row["long"]],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size: 24px; color: blue; font-weight: bold;">
                            {row.get("nro_camara", "N/A")}
                        </div>
                    """),
                    tooltip=f"Cámara #{row.get('nro_camara', 'N/A')}"
                ).add_to(cluster)

            # Mostrar mapa en 16:9 y full width
            st_folium(mapa, width=1200, height=675)
        else:
            st.error("No se pudo geolocalizar la dirección.")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
