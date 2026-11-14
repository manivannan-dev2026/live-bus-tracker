import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import math

st.title("🚌 தமிழ்நாடு Live Bus Tracker (v3.1)")
st.write("பயணிகளின் நேரடி மொபைல் GPS மூலம் பஸ் இருப்பிடத்தை அறியவும்!")

ஊர்கள்_GPS = {
    "சென்னை (கோயம்பேடு)": [13.0694, 80.1948],
    "தாம்பரம்": [12.9249, 80.1000],
    "செங்கல்பட்டு": [12.6819, 79.9888],
    "விழுப்புரம்": [11.9401, 79.4861],
    "திருச்சி": [10.7905, 78.7047],
    "மதுரை": [9.9252, 78.1198],
    "கோயம்புத்தூர்": [11.0168, 76.9558],
    "சேலம்": [11.6643, 78.1460],
    "திருநெல்வேலி": [8.7139, 77.7567]
}

def அருகில்_ஊர்_கண்டுபிடி(lat, lon):
    அருகில்_ஊர் = ""
    குறைந்த_தூரம் = 999999
    for ஊர், coords in ஊர்கள்_GPS.items():
        தூரம் = math.dist([lat, lon], coords) * 111
        if தூரம் < குறைந்த_தூரம்:
            குறைந்த_தூரம் = தூரம்
            அருகில்_ஊர் = ஊர்
    return அருகில்_ஊர், round(குறைந்த_தூரம், 1)

st.subheader("📡 1. பஸ்ஸில் பயணிப்பவர் Live GPS பகிர:")
st.info("கீழே தோன்றும் சிறிய லொகேஷன் பட்டனை (📍) அழுத்தி உங்கள் மொபைல் Location அனுமதியை (Allow) வழங்கவும்.")

# தெளிவான லொகேஷன் பட்டனைக் காட்டும் புதிய கருவி
location = streamlit_geolocation()

if location and location.get("latitude") is not None:
    lat = location["latitude"]
    lon = location["longitude"]
    
    அருகில்_ஊர், கிமீ = அருகில்_ஊர்_கண்டுபிடி(lat, lon)
    
    st.success(f"✅ நேரடி GPS இணைக்கப்பட்டது! உங்கள் பஸ் இப்போது **'{அருகில்_ஊர்}'** அருகே ({கிமீ} கி.மீ தூரத்தில்) உள்ளது!")
    
    live_map = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker(
        location=[lat, lon],
        popup=f"🚌 லைவ் பஸ் இங்கே உள்ளது! ({அருகில்_ஊர்} அருகில்)",
        icon=folium.Icon(color="green", icon="bus", prefix="fa")
    ).add_to(live_map)
    st_folium(live_map, width=700, height=400)
else:
    st.warning("📍 மேலே உள்ள சிறிய பட்டனை அழுத்தினால் உங்கள் தற்போதைய இடம் மேப்பில் தெரியும்.")
  
