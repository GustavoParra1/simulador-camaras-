import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Cargar base de datos
df = pd.read_csv("camaras_db.csv")
df["lat"] = df["lat"].astype(float)
df["long"] = df["long"].astype(float)

# Título
st.title("Simulador de Cámaras de Seguridad (MDP)")

# Session state para manejar inputs
if "direccion" not in st.session_state:
    st.session_state["direccion"] = ""

# Formulario con botones
with st.form("formulario_direccion", clear_on_submit=False):
    direccion_input = st.text_input("Ingrese una dirección en Mar del Plata", value=st.session_state["direccion"])
    col1, col2 = st.columns([1, 1])
    with col1:
        buscar = st.form_submit_button("🔍 Buscar")
    with col2:
        limpiar = st.form_submit_button("🧹 Limpiar")

# Acción botón limpiar
if limpiar:
    st.session_state["direccion"] = ""
    st.experimental_rerun()

# Acción botón buscar
if buscar and direccion_input.strip() != "":
    st.session_state["direccion"] = direccion_input.strip()
    geolocator = Nominatim(user_agent="simulador-mdp")
    try:
        loc = geolocator.geocode(f"{direccion_input}, Mar del Plata, Argentina")
        if loc:
            lat_u, lon_u = loc.latitude, loc.longitude
            st.success(f"Coordenadas encontradas: lat={lat_u}, lon={lon_u}")

            # Filtrar cámaras a 700 m
            df["distancia"] = df.apply(lambda r: geodesic((lat_u, lon_u), (r["lat"], r["long"])).meters, axis=1)
            df_ok = df[df["distancia"] <= 700]
            st.info(f"Se encontraron {len(df_ok)} cámaras en un radio de 700 metros.")

            # Mapa
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
        st.error(f"Error: {e}")
