import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import math
import datetime

st.title("🚌 தமிழ்நாடு Live Bus Tracker (v4.0)")
st.write("பயணிகள் பகிரும் நேரடி GPS மூலம் பஸ் எங்கே வருகிறது என்று அனைவரும் பார்க்கலாம்!")

# 1. அனைவரும் பார்க்கக்கூடிய பொதுவான லைவ் டேட்டாபேஸ் (Shared Live Memory)
@st.cache_resource
def get_live_bus_db():
    return {}

live_bus_db = get_live_bus_db()

# 2. தமிழ்நாடு முக்கிய ஊர்களின் GPS விபரங்கள்
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

# இரண்டு தனித்தனி டேப்கள் (Tabs) உருவாக்குகிறோம்
tab1, tab2 = st.tabs(["🔍 பஸ் எங்கே வருது? (பயணிகள் பார்க்க)", "📡 லைவ் லொகேஷன் பகிர (பஸ்ஸில் இருப்பவர்)"])

# --- டேப் 1: பஸ் ஸ்டாண்டில் காத்திருப்பவர் பார்ப்பது ---
with tab1:
    st.subheader("🔍 லைவ் பஸ் இருப்பிடத்தைத் தேடுங்கள்")
    if live_bus_db:
        தேர்ந்தெடுத்த_பஸ் = st.selectbox("இப்போது லைவில் ஓடும் பேருந்துகள்:", list(live_bus_db.keys()))
        தகவல் = live_bus_db[தேர்ந்தெடுத்த_பஸ்]
        
        st.success(f"🚌 பேருந்து: **{தேர்ந்தெடுத்த_பஸ்}**")
        st.info(f"📍 தற்போதைய நிலை: **'{தகவல்['near_town']}'** அருகே ({தகவல்['distance']} கி.மீ தூரத்தில்) வந்து கொண்டிருக்கிறது!")
        st.caption(f"🕒 கடைசியாக அப்டேட் செய்த நேரம்: {தகவல்['time']}")
        
        view_map = folium.Map(location=[தகவல்['lat'], தகவல்['lon']], zoom_start=15)
        folium.Marker(
            location=[தகவல்['lat'], தகவல்['lon']],
            popup=f"🚌 {தேர்ந்தெடுத்த_பஸ்} ({தகவல்['near_town']} அருகில்)",
            icon=folium.Icon(color="red", icon="bus", prefix="fa")
        ).add_to(view_map)
        st_folium(view_map, width=700, height=350, key="view_map")
    else:
        st.warning("⚠️ இப்போது எந்தப் பேருந்தும் லைவ் லொகேஷனைப் பகிரவில்லை. பக்கத்தில் உள்ள '📡 லைவ் லொகேஷன் பகிர' பகுதிக்குச் சென்று ஒரு பஸ்ஸை ஆன் செய்து பாருங்கள்!")

# --- டேப் 2: பஸ்ஸுக்குள் பயணிப்பவர் லொகேஷன் பகிர்வது ---
with tab2:
    st.subheader("📡 நீங்கள் பயணிக்கும் பஸ்ஸின் இடத்தைப் பகிருங்கள்")
    பஸ்_எண் = st.text_input("பஸ் எண் அல்லது பெயரை உள்ளிடவும் (எ.கா: 21G - தாம்பரம்):", "21G - தாம்பரம்")
    st.write("கீழே உள்ள 📍 பட்டனை அழுத்தி உங்கள் மொபைல் லொகேஷனை ஆன் செய்யவும்:")
    
    location = streamlit_geolocation()
    
    if location and location.get("latitude") is not None:
        lat = location["latitude"]
        lon = location["longitude"]
        அருகில்_ஊர், கிமீ = அருகில்_ஊர்_கண்டுபிடி(lat, lon)
        நேரம் = datetime.datetime.now().strftime("%I:%M:%S %p")
        
        # பொதுவான டேட்டாபேஸில் பஸ் இடத்தைச் சேமிக்கிறோம்!
        live_bus_db[பஸ்_எண்] = {
            "lat": lat,
            "lon": lon,
            "near_town": அருகில்_ஊர்,
            "distance": கிமீ,
            "time": நேரம்
        }
        st.success(f"✅ நன்றி! **{பஸ்_எண்}** பேருந்தின் லைவ் இருப்பிடம் ('{அருகில்_ஊர்}' அருகில்) அனைவருக்கும் பகிரப்பட்டுவிட்டது!")
