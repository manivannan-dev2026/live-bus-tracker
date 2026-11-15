import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import pandas as pd
import datetime

st.title("🚌 நம்ம தமிழ்நாடு Smart Bus (v6.0)")
st.write("அனைத்து ஊர் பேருந்துகள், லைவ் இருப்பிடம் மற்றும் கூட்ட நெரிசல் (Crowd Status) அறியும் செயலி!")

# 1. பொதுவான லைவ் டேட்டாபேஸ் (Shared Live Memory)
@st.cache_resource
def get_live_bus_db():
    return {}

live_bus_db = get_live_bus_db()

# 2. பேருந்து வழித்தடங்களைப் படிக்கிறோம் (CSV + புதியதாகச் சேர்க்கப்பட்டவை)
@st.cache_resource
def get_routes_data():
    return pd.read_csv("bus_routes.csv")

routes_df = get_routes_data()

def ஏரியா_பெயர்_கண்டுபிடி(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tn_smart_bus_v6")
        location = geolocator.reverse((lat, lon), exactly_one=True, language="ta")
        if location and location.address:
            parts = location.address.split(",")[:3]
            return ", ".join(parts)
    except:
        pass
    return f"GPS: {round(lat, 4)}, {round(lon, 4)}"

# நான்கு தனித்தனி டேப்கள் (Tabs)
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 பஸ் தேட (From ➡️ To)", 
    "📍 லைவ் மேப் & கூட்டம்", 
    "📡 லைவ் GPS & கூட்டம் பகிர",
    "➕ புதிய ஊர்/பஸ் சேர்க்க"
])

# --- டேப் 1: From ➡️ To பஸ் தேடுதல் ---
with tab1:
    st.subheader("🔍 புறப்படும் ஊர் முதல் சேரும் ஊர் வரை தேட")
    col1, col2 = st.columns(2)
    with col1:
        from_place = st.selectbox("புறப்படும் இடம் (From):", sorted(routes_df["From"].unique()))
    with col2:
        to_place = st.selectbox("சேரும் இடம் (To):", sorted(routes_df["To"].unique()))

    matched_buses = routes_df[(routes_df["From"] == from_place) & (routes_df["To"] == to_place)]

    if not matched_buses.empty:
        st.success(f"✅ **{from_place}** முதல் **{to_place}** வரை செல்லும் பேருந்துகள்:")
        for index, row in matched_buses.iterrows():
            bus_no = row["Bus_No"]
            st.info(f"🚌 **பேருந்து எண்: {bus_no}**\n\n🛣️ **வழித்தடம்:** {row['Stops']}")
            
            if bus_no in live_bus_db:
                live_info = live_bus_db[bus_no]
                st.warning(
                    f"🟢 **LIVE:** இப்போது **{live_info['area']}** அருகே வருகிறது!\n\n"
                    f"👥 **பஸ்ஸில் கூட்டம்:** {live_info['crowd']} | 🕒 நேரம்: {live_info['time']}"
                )
    else:
        st.warning("⚠️ இந்த இரண்டு ஊர்களுக்கும் நேரடி பஸ் பட்டியலில் இல்லை. '➕ புதிய ஊர்/பஸ் சேர்க்க' பகுதிக்குச் சென்று நீங்களே சேர்க்கலாம்!")

# --- டேப் 2: லைவ் மேப்பில் பஸ் பார்த்தல் ---
with tab2:
    st.subheader("📍 லைவ் மேப்பில் பேருந்து இருப்பிடம் & கூட்டம்")
    if live_bus_db:
        selected_bus = st.selectbox("லைவில் ஓடும் பேருந்தைத் தேர்ந்தெடுக்கவும்:", list(live_bus_db.keys()))
        info = live_bus_db[selected_bus]
        
        st.success(f"🚌 பேருந்து **{selected_bus}** இப்போது **{info['area']}** அருகே உள்ளது!")
        st.info(f"👥 **பஸ்ஸில் கூட்டம்:** {info['crowd']} | 🕒 அப்டேட் நேரம்: {info['time']}")
        
        view_map = folium.Map(location=[info['lat'], info['lon']], zoom_start=15)
        folium.Marker(
            location=[info['lat'], info['lon']],
            popup=f"🚌 {selected_bus} ({info['crowd']})",
            icon=folium.Icon(color="red", icon="bus", prefix="fa")
        ).add_to(view_map)
        st_folium(view_map, width=700, height=350, key="v6_map")
    else:
        st.warning("⚠️ இப்போது எந்தப் பேருந்தும் லைவில் இல்லை. '📡 லைவ் GPS & கூட்டம் பகிர' டேப்பிற்குச் சென்று பஸ் எண்ணைப் போட்டு ஆன் செய்யவும்!")

# --- டேப் 3: பஸ்ஸில் இருப்பவர் லைவ் லொகேஷன் & கூட்டம் பகிர ---
with tab3:
    st.subheader("📡 நீங்கள் பயணிக்கும் பஸ்ஸின் இடத்தையும் கூட்டத்தையும் பகிருங்கள்")
    bus_input = st.selectbox("பேருந்து எண்ணைத் தேர்ந்தெடுக்கவும்:", sorted(routes_df["Bus_No"].unique()))
    crowd_status = st.radio(
        "இப்போது பஸ்ஸில் கூட்டம் எப்படி உள்ளது?",
        ["🟢 சீட் காலியாக உள்ளது (Seats Available)", "🟡 நின்று கொண்டு வரலாம் (Moderate)", "🔴 அதிக கூட்டம் (Overcrowded)"]
    )
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
            "crowd": crowd_status,
            "time": current_time
        }
        st.success(f"✅ நன்றி! **{bus_input}** பேருந்தின் லைவ் இடம் (**{area_name}**) மற்றும் கூட்ட நிலை (**{crowd_status}**) பகிரப்பட்டுவிட்டது!")

# --- டேப் 4: பயனர்களே புதிய ஊர்/பஸ் சேர்க்க ---
with tab4:
    st.subheader("➕ புதிய ஊர் மற்றும் பேருந்து எண்ணைச் சேர்க்கவும்")
    with st.form("add_route_form"):
        new_bus = st.text_input("பேருந்து எண் (எ.கா: 102 அல்லது TNSTC-707):")
        new_from = st.text_input("புறப்படும் ஊர் (From):")
        new_to = st.text_input("சேரும் ஊர் (To):")
        new_stops = st.text_input("செல்லும் முக்கிய நிறுத்தங்கள் (Stops):")
        submitted = st.form_submit_button("புதிய பேருந்தைச் சேர்க்கவும்")
        
        if submitted and new_bus and new_from and new_to:
            new_row = pd.DataFrame([{"Bus_No": new_bus, "From": new_from, "To": new_to, "Stops": new_stops}])
            routes_df.loc[len(routes_df)] = [new_bus, new_from, new_to, new_stops]
            st.success(f"🎉 **{new_bus} ({new_from} ➡️ {new_to})** வெற்றிகரமாகப் பட்டியலில் சேர்க்கப்பட்டுவிட்டது! இப்போது முதல் டேப்பில் தேடிப் பார்க்கலாம்.")
