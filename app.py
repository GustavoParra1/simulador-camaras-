import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Configuración de la página
st.set_page_config(page_title="Simulador Cámaras de Seg.", layout="centered")
st.title("Simulador Cámaras de Seg.(MDP)")
st.caption("Ingrese una dirección en Mar del Plata")

# Inicializar session_state
if "direccion" not in st.session_state:
    st.session_state.direccion = ""
if "mostrar_mapa" not in st.session_state:
    st.session_state.mostrar_mapa = False
if "coordenadas" not in st.session_state:
    st.session_state.coordenadas = None
if "resultado" not in st.session_state:
    st.session_state.resultado = None

# Entrada de dirección
st.session_state.direccion = st.text_input("Dirección:", value=st.session_state.direccion)

# Botón buscar
buscar = st.button("🔍 Buscar")

# Acción al presionar "Buscar"
if buscar and st.session_state.direccion:
    df_camaras = pd.read_csv("camaras_db.csv", dtype=str)
    df_camaras["lat"] = df_camaras["lat"].str.replace(",", ".").astype(float)
    df_camaras["long"] = df_camaras["long"].str.replace(",", ".").astype(float)

    geolocator = Nominatim(user_agent="simulador-mdp")
    try:
        ubicacion = geolocator.geocode(f"{st.session_state.direccion}, Mar del Plata, Argentina")
        if ubicacion:
            lat = ubicacion.latitude
            lon = ubicacion.longitude
            st.session_state.coordenadas = (lat, lon)
            st.success(f"Coordenadas encontradas: lat={lat}, lon={lon}")

            def en_rango(fila):
                return geodesic((lat, lon), (fila["lat"], fila["long"])).meters <= 300

            camaras_en_rango = df_camaras[df_camaras.apply(en_rango, axis=1)]
            st.session_state.resultado = camaras_en_rango
            st.session_state.mostrar_mapa = True
        else:
            st.error("No se pudo geolocalizar la dirección.")
            st.session_state.mostrar_mapa = False
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.session_state.mostrar_mapa = False

# Mostrar el mapa si corresponde
if st.session_state.mostrar_mapa and st.session_state.coordenadas:
    lat, lon = st.session_state.coordenadas
    camaras_en_rango = st.session_state.resultado

    st.info(f"Se encontraron {len(camaras_en_rango)} cámaras en un radio de 300 metros.")

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

File "/mount/src/simulador-camaras-/app.py", line 80
  File "/mount/src/simulador-camaras-/app.py", line 80
       ^
SyntaxError: invalid syntax
