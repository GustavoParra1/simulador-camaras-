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

# Cargar base de datos
df_camaras = pd.read_csv("camaras_db.csv", dtype=str)
df_camaras["lat"] = df_camaras["lat"].str.replace(",", ".").astype(float)
df_camaras["long"] = df_camaras["long"].str.replace(",", ".").astype(float)

# Geolocalizador
geolocator = Nominatim(user_agent="simulador-mdp")

# Entrada del usuario
direccion = st.text_input("")

# Procesar si hay dirección
if direccion:
    try:
        ubicacion = geolocator.geocode(f"{direccion}, Mar del Plata, Argentina")
        if ubicacion:
            lat = ubicacion.latitude
            lon = ubicacion.longitude
            st.success(f"Coordenadas encontradas: lat={lat}, lon={lon}")

            # Calcular cámaras en radio de 300 metros
            def en_rango(fila):
                return geodesic((lat, lon), (fila["lat"], fila["long"])).meters <= 300

            camaras_en_rango = df_camaras[df_camaras.apply(en_rango, axis=1)]

            st.info(f"Se encontraron {len(camaras_en_rango)} cámaras en un radio de 300 metros.")

            # Crear mapa
            mapa = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], tooltip="Dirección ingresada", icon=folium.Icon(color="red")).add_to(mapa)

            # Agrupar cámaras
            cluster = MarkerCluster().add_to(mapa)

            # Añadir cámaras al mapa con números
            for _, row in camaras_en_rango.iterrows():
                lat_cam = row["lat"]
                lon_cam = row["long"]
                numero = row.get("nro_camara", "N/A")  # Reemplazar con el nombre real

                folium.Marker(
                    location=[lat_cam, lon_cam],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size: 24px; color: blue; font-weight: bold;">
                            {numero}
                        </div>
                    """),
                    tooltip=f"Cámara #{numero}"
                ).add_to(cluster)

            # Mostrar el mapa
            st_folium(mapa, width=700, height=900)

        else:
            st.error("No se pudo geolocalizar la dirección.")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
