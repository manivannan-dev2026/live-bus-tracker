import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import pandas as pd
import datetime

st.title("🚌 தமிழ்நாடு Live Bus Tracker (v5.0)")
st.write("புறப்படும் ஊர் முதல் சேரும் ஊர் வரை பஸ் எண்கள் மற்றும் லைவ் இருப்பிடத்தை அறியவும்!")

# 1. பொதுவான லைவ் டேட்டாபேஸ் (Shared Live Memory)
@st.cache_resource
def get_live_bus_db():
    return {}

live_bus_db = get_live_bus_db()

# 2. CSV ஃபைலில் இருந்து பேருந்து வழித்தடங்களைப் படிக்கிறோம் (Pandas)
@st.cache_data
def load_routes():
    return pd.read_csv("bus_routes.csv")

routes_df = load_routes()

# 3. GPS எண்களை வைத்து சரியான ஏரியா/ஊர் பெயரைத் தானாகக் கண்டுபிடிக்கும் கருவி (Geopy)
def ஏரியா_பெயர்_கண்டுபிடி(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tn_live_bus_tracker")
        location = geolocator.reverse((lat, lon), exactly_one=True, language="ta")
        if location and location.address:
            # முகவரியின் முதல் 3 முக்கிய பகுதிகளை மட்டும் எடுக்கிறோம்
            parts = location.address.split(",")[:3]
            return ", ".join(parts)
    except:
        pass
    return f"GPS: {round(lat, 4)}, {round(lon, 4)}"

# மூன்று தனித்தனி டேப்கள் (Tabs)
tab1, tab2, tab3 = st.tabs(["🔍 வழித்தடம் தேட (From ➡️ To)", "📍 லைவ் பஸ் எங்கே வருது?", "📡 லைவ் லொகேஷன் பகிர"])

# --- டேப் 1: From ➡️ To பஸ் தேடுதல் ---
with tab1:
    st.subheader("🔍 புறப்படும் இடம் முதல் சேரும் இடம் வரை பஸ் தேட")
    col1, col2 = st.columns(2)
    with col1:
        from_place = st.selectbox("புறப்படும் இடம் (From):", routes_df["From"].unique())
    with col2:
        to_place = st.selectbox("சேரும் இடம் (To):", routes_df["To"].unique())

    # பயனர் தேடிய ஊர்களுக்குப் பொருத்தமான பஸ்களை ஃபில்டர் செய்கிறோம்
    matched_buses = routes_df[(routes_df["From"] == from_place) & (routes_df["To"] == to_place)]

    if not matched_buses.empty:
        st.success(f"✅ **{from_place}** முதல் **{to_place}** வரை செல்லும் பேருந்துகள்:")
        for index, row in matched_buses.iterrows():
            bus_no = row["Bus_No"]
            st.info(f"🚌 **பேருந்து எண்: {bus_no}**\n\n🛣️ **செல்லும் வழி:** {row['Stops']}")
            
            # இந்த பஸ் இப்போது லைவில் உள்ளதா என்று சரிபார்க்கிறோம்!
            if bus_no in live_bus_db:
                live_info = live_bus_db[bus_no]
                st.warning(f"🟢 **LIVE:** இந்த {bus_no} பேருந்து இப்போது **{live_info['area']}** அருகே வந்து கொண்டிருக்கிறது! (நேரம்: {live_info['time']})")
    else:
        st.error("❌ இந்த வழித்தடத்திற்கு இப்போது பேருந்து விபரங்கள் இல்லை. 'பூந்தமல்லி' ➡️ 'மயிலாப்பூர்' தேர்ந்தெடுத்துப் பாருங்கள்!")

# --- டேப் 2: லைவ் மேப்பில் பஸ் பார்த்தல் ---
with tab2:
    st.subheader("📍 லைவ் மேப்பில் பேருந்து இருப்பிடம்")
    if live_bus_db:
        selected_bus = st.selectbox("லைவில் ஓடும் பேருந்தைத் தேர்ந்தெடுக்கவும்:", list(live_bus_db.keys()))
        info = live_bus_db[selected_bus]
        
        st.success(f"🚌 பேருந்து **{selected_bus}** இப்போது **{info['area']}** அருகே உள்ளது!")
        st.caption(f"🕒 கடைசியாக அப்டேட் செய்த நேரம்: {info['time']}")
        
        view_map = folium.Map(location=[info['lat'], info['lon']], zoom_start=15)
        folium.Marker(
            location=[info['lat'], info['lon']],
            popup=f"🚌 {selected_bus} - {info['area']}",
            icon=folium.Icon(color="red", icon="bus", prefix="fa")
        ).add_to(view_map)
        st_folium(view_map, width=700, height=350, key="v5_map")
    else:
        st.warning("⚠️ இப்போது எந்தப் பேருந்தும் லைவில் இல்லை. '📡 லைவ் லொகேஷன் பகிர' டேப்பிற்குச் சென்று பஸ் எண்ணைப் போட்டு லொகேஷனை ஆன் செய்யவும்!")

# --- டேப் 3: பஸ்ஸில் இருப்பவர் லைவ் லொகேஷன் பகிர ---
with tab3:
    st.subheader("📡 நீங்கள் பயணிக்கும் பஸ்ஸின் இடத்தைப் பகிருங்கள்")
    bus_input = st.selectbox("நீங்கள் பயணிக்கும் பேருந்து எண்ணைத் தேர்ந்தெடுக்கவும்:", routes_df["Bus_No"].unique())
    st.write("கீழே உள்ள 📍 பட்டனை அழுத்தி உங்கள் மொபைல் லொகேஷனை ஆன் செய்யவும்:")
    
    location = streamlit_geolocation()
    
    if location and location.get("latitude") is not None:
        lat = location["latitude"]
        lon = location["longitude"]
        area_name = ஏரியா_பெயர்_கண்டுபிடி(lat, lon)
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        
        live_bus_db[bus_input] = {
            "lat": lat,
            "lon": lon,
            "area": area_name,
            "time": current_time
        }
        st.success(f"✅ நன்றி! **{bus_input}** பேருந்தின் லைவ் இடம் (**{area_name}**) அனைவருக்கும் பகிரப்பட்டுவிட்டது!")
