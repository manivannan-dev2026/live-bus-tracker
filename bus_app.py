import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import math

st.title("🚌 தமிழ்நாடு Live Bus Tracker (v3.5)")
st.write("ஊர் பெயரைத் தேடியும் பார்க்கலாம், நேரடி மொபைல் GPS மூலமும் பார்க்கலாம்!")

# தமிழ்நாடு முக்கிய ஊர்கள், பஸ் எண்கள் மற்றும் GPS விபரங்கள்
பஸ்_தரவுகள் = {
    "சென்னை (கோயம்பேடு)": {"gps": [13.0694, 80.1948], "bus": "27B / 15F (MTC)", "route": "கோயம்பேடு ➡️ அண்ணா நகர் ➡️ பிராட்வே"},
    "தாம்பரம்": {"gps": [12.9249, 80.1000], "bus": "21G / 515 (MTC)", "route": "பிராட்வே ➡️ கிண்டி ➡️ தாம்பரம்"},
    "செங்கல்பட்டு": {"gps": [12.6819, 79.9888], "bus": "500A / TNSTC", "route": "தாம்பரம் ➡️ கூடுவாஞ்சேரி ➡️ செங்கல்பட்டு"},
    "விழுப்புரம்": {"gps": [11.9401, 79.4861], "bus": "TNSTC Ultra Deluxe", "route": "சென்னை ➡️ திண்டிவனம் ➡️ விழுப்புரம்"},
    "திருச்சி": {"gps": [10.7905, 78.7047], "bus": "SETC Express", "route": "விழுப்புரம் ➡️ பெரம்பலூர் ➡️ திருச்சி"},
    "மதுரை": {"gps": [9.9252, 78.1198], "bus": "TNSTC Superfast", "route": "திருச்சி ➡️ மேலூர் ➡️ மதுரை"},
    "கோயம்புத்தூர்": {"gps": [11.0168, 76.9558], "bus": "SETC AC Sleeper", "route": "சேலம் ➡️ ஈரோடு ➡️ கோயம்புத்தூர்"},
    "சேலம்": {"gps": [11.6643, 78.1460], "bus": "TNSTC Express", "route": "வேலூர் ➡️ தர்மபுரி ➡️ சேலம்"},
    "திருநெல்வேலி": {"gps": [8.7139, 77.7567], "bus": "SETC Express", "route": "மதுரை ➡️ விருதுநகர் ➡️ திருநெல்வேலி"}
}

def அருகில்_ஊர்_கண்டுபிடி(lat, lon):
    அருகில்_ஊர் = ""
    குறைந்த_தூரம் = 999999
    for ஊர், தகவல் in பஸ்_தரவுகள்.items():
        தூரம் = math.dist([lat, lon], தகவல்["gps"]) * 111
        if தூரம் < குறைந்த_தூரம்:
            குறைந்த_தூரம் = தூரம்
            அருகில்_ஊர் = ஊர்
    return அருகில்_ஊர், round(குறைந்த_தூரம், 1)

# பகுதி 1: Search Box (ஊர் பெயரைத் தேடும் வசதி)
st.subheader("🔍 1. ஊர் பெயர் மூலம் பஸ் தேட:")
தேர்ந்தெடுத்த_ஊர் = st.selectbox("நீங்கள் செல்ல வேண்டிய ஊரைத் தேர்ந்தெடுக்கவும்:", list(பஸ்_தரவுகள்.keys()))

if தேர்ந்தெடுத்த_ஊர்:
    தகவல் = பஸ்_தரவுகள்[தேர்ந்தெடுத்த_ஊர்]
    பஸ்_இடம் = தகவல்["gps"]
    
    st.success(f"🚌 பேருந்து எண்: **{தகவல்['bus']}** | 🛣️ வழித்தடம்: {தகவல்['route']}")
    
    search_map = folium.Map(location=பஸ்_இடம், zoom_start=14)
    folium.Marker(
        location=பஸ்_இடம்,
        popup=f"🚌 {தகவல்['bus']} - {தேர்ந்தெடுத்த_ஊர்}",
        icon=folium.Icon(color="red", icon="bus", prefix="fa")
    ).add_to(search_map)
    st_folium(search_map, width=700, height=350, key="search_map")

st.divider()

# பகுதி 2: Live GPS (நேரடி மொபைல் லொகேஷன் வசதி)
st.subheader("📡 2. பயணிகள் நேரடி மொபைல் GPS பகிர:")
st.info("கீழே உள்ள சிறிய லொகேஷன் பட்டனை (📍) அழுத்தி உங்கள் மொபைல் Location அனுமதியை (Allow) வழங்கவும்.")

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
    st_folium(live_map, width=700, height=350, key="live_map")
