import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import math

st.title("🚌 தமிழ்நாடு Live Bus Tracker (v3.0)")
st.write("பயணிகளின் நேரடி மொபைல் GPS மூலம் பஸ் இருப்பிடத்தை அறியவும்!")

# தமிழ்நாடு முக்கிய ஊர்களின் GPS விபரங்கள்
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

# அருகில் உள்ள ஊரைக் கண்டுபிடிக்கும் பைத்தான் லாஜிக்
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
st.info("கீழே உள்ள பட்டனை அழுத்தி உங்கள் மொபைல் Location அனுமதியை (Allow) வழங்கவும்.")

# மொபைலில் இருந்து நிஜமான GPS எடுக்கும் பட்டன்
location = get_geolocation(component_key="get_loc")

if location and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    
    அருகில்_ஊர், கிமீ = அருகில்_ஊர்_கண்டுபிடி(lat, lon)
    
    st.success(f"✅ நேரடி GPS இணைக்கப்பட்டது! உங்கள் பஸ் இப்போது **'{அருகில்_ஊர்}'** அருகே ({கிமீ} கி.மீ தூரத்தில்) உள்ளது!")
    
    # நிஜமான GPS இடத்தை மேப்பில் காட்டுதல்
    live_map = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker(
        location=[lat, lon],
        popup=f"🚌 லைவ் பஸ் இங்கே உள்ளது! ({அருகில்_ஊர்} அருகில்)",
        icon=folium.Icon(color="green", icon="bus", prefix="fa")
    ).add_to(live_map)
    st_folium(live_map, width=700, height=400)
else:
    st.warning("📍 மேலே உள்ள 'Get location' பட்டனை அழுத்தினால் உங்கள் தற்போதைய இடம் மேப்பில் தெரியும்.")
