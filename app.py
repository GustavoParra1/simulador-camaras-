import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Título
st.title("Simulador de Cámaras de Seguridad (MDP)")
st.write("Ingrese una dirección en Mar del Plata")

# Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("camaras_db.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df_camaras = cargar_datos()

# Entrada de dirección
direccion = st.text_input("Ingrese una dirección en Mar del Plata")

# Función para geolocalizar
def geolocalizar_direccion(direccion):
    geolocator = Nominatim(user_agent="simulador-mdp")
    location = geolocator.geocode(direccion + ", Mar del Plata, Argentina")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Filtrar cámaras por distancia
def filtrar_camaras(df, lat, lon, radio=700):
    def en_rango(row):
        try:
            lat2 = float(str(row["lat"]).replace(",", "."))
            lon2 = float(str(row["long"]).replace(",", "."))
            return geodesic((lat, lon), (lat2, lon2)).meters <= radio
        except:
            return False

    return df[df.apply(en_rango, axis=1)]

# Si hay dirección ingresada
if direccion:
    lat, lon = geolocalizar_direccion(direccion)

    if lat is None or lon is None:
        st.error("No se pudo geolocalizar la dirección.")
    else:
        st.success(f"Coordenadas encontradas: lat={lat}, lon={lon}")

        camaras_en_rango = filtrar_camaras(df_camaras, lat, lon)

        st.info(f"Se encontraron {len(camaras_en_rango)} cámaras en un radio de 700 metros.")

        # Crear mapa
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], tooltip="Ubicación ingresada", icon=folium.Icon(color='red')).add_to(m)

        cluster = MarkerCluster().add_to(m)

        for _, row in camaras_en_rango.iterrows():
            try:
                lat_cam = float(str(row["lat"]).replace(",", "."))
                lon_cam = float(str(row["long"]).replace(",", "."))
                # Agregar marcador con número visible en el mapa
folium.Marker(
    location=[lat_cam, lon_cam],
    icon=folium.DivIcon(
        html=f"""
            <div style="font-size: 12px; color: blue; font-weight: bold;">
                {int(row.get('camara', 0))}
            </div>
        """
    ),
    tooltip=f"Cámara #{row.get('camara', 'N/A')}"
).add_to(cluster)

            except Exception as e:
                st.warning(f"No se pudo agregar una cámara: {e}")

        st_folium(m, width=700, height=500)
