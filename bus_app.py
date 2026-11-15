import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import pandas as pd
import datetime

st.set_page_config(page_title="நம்ம தமிழ்நாடு Smart Bus", page_icon="🚌")

st.title("🚌 நம்ம தமிழ்நாடு Smart Bus (v7.0)")
st.write("எந்த ஊர் பெயரைத் தேடினாலும் அந்த வழியாகச் செல்லும் பஸ்கள் மற்றும் லைவ் இருப்பிடத்தை அறியவும்!")

# 1. பொதுவான லைவ் டேட்டாபேஸ்
@st.cache_resource
def get_live_bus_db():
    return {}

live_bus_db = get_live_bus_db()

# 2. CSV ஃபைலைப் பாதுகாப்பாகப் படிக்கிறோம்
def load_routes():
    try:
        return pd.read_csv("bus_routes.csv")
    except Exception as e:
        st.error(f"CSV கோப்பில் சிறிய பிழை உள்ளது: {e}")
        return pd.DataFrame(columns=["Bus_No", "From", "To", "Stops"])

routes_df = load_routes()

def ஏரியா_பெயர்_கண்டுபிடி(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tn_smart_bus_v7")
        location = geolocator.reverse((lat, lon), exactly_one=True, language="ta")
        if location and location.address:
            parts = location.address.split(",")[:3]
            return ", ".join(parts)
    except:
        pass
    return f"GPS: {round(lat, 4)}, {round(lon, 4)}"

# மூன்று எளிய டேப்கள்
tab1, tab2, tab3 = st.tabs([
    "🔍 பஸ் தேட (Smart Search)", 
    "📍 லைவ் மேப் & கூட்டம்", 
    "📡 லைவ் GPS பகிர"
])

# --- டேப் 1: எந்த ஊர் பெயரைத் தேடினாலும் பஸ் வரும்! ---
with tab1:
    st.subheader("🔍 ஊர் அல்லது நிறுத்தம் பெயரை உள்ளிடவும்")
    தேடும்_ஊர் = st.text_input("ஊர் பெயரை டைப் செய்யவும் (எ.கா: போரூர், தாம்பரம், திருவள்ளூர், காஞ்சிபுரம், கிண்டி):").strip()
    
    if தேடும்_ஊர்:
        # From, To, அல்லது Stops எதில் அந்த ஊர் பெயர் இருந்தாலும் தேடி எடுக்கும்!
        matched = routes_df[
            routes_df["From"].str.contains(தேடும்_ஊர், case=False, na=False) |
            routes_df["To"].str.contains(தேடும்_ஊர், case=False, na=False) |
            routes_df["Stops"].str.contains(தேடும்_ஊர், case=False, na=False)
        ]
        
        if not matched.empty:
            st.success(f"✅ **'{தேடும்_ஊர்}'** வழியாகச் செல்லும் {len(matched)} பேருந்துகள் கண்டறியப்பட்டுள்ளன:")
            for _, row in matched.iterrows():
                bus_no = str(row["Bus_No"])
                st.info(f"🚌 **பேருந்து எண்: {bus_no}** ({row['From']} ➡️ {row['To']})\n\n🛣️ **வழித்தடம்:** {row['Stops']}")
                
                if bus_no in live_bus_db:
                    live_info = live_bus_db[bus_no]
                    st.warning(f"🟢 **LIVE:** இப்போது **{live_info['area']}** அருகே வருகிறது! | 👥 {live_info['crowd']}")
        else:
            st.warning(f"❌ '{தேடும்_ஊர்}' என்ற பெயரில் பேருந்து இல்லை. 'பூந்தமல்லி', 'தாம்பரம்', 'ஆவடி', 'போரூர்' என டைப் செய்து பாருங்கள்!")
    else:
        st.caption("👇 கீழே உள்ள பட்டியலில் சில முக்கியப் பேருந்துகள் காட்டப்பட்டுள்ளன:")
        st.dataframe(routes_df.head(10), use_container_width=True)

# --- டேப் 2: லைவ் மேப் ---
with tab2:
    st.subheader("📍 லைவ் மேப்பில் பேருந்து இருப்பிடம்")
    if live_bus_db:
        selected_bus = st.selectbox("லைவில் ஓடும் பேருந்து:", list(live_bus_db.keys()))
        info = live_bus_db[selected_bus]
        
        st.success(f"🚌 பேருந்து **{selected_bus}** இப்போது **{info['area']}** அருகே உள்ளது!")
        st.info(f"👥 **கூட்டம்:** {info['crowd']} | 🕒 நேரம்: {info['time']}")
        
        view_map = folium.Map(location=[info['lat'], info['lon']], zoom_start=15)
        folium.Marker(
            location=[info['lat'], info['lon']],
            popup=f"🚌 {selected_bus}",
            icon=folium.Icon(color="red", icon="bus", prefix="fa")
        ).add_to(view_map)
        st_folium(view_map, width=700, height=350, key="v7_map")
    else:
        st.info("ℹ️ இப்போது எந்தப் பேருந்தும் லைவில் இல்லை. மூன்றாவது டேப்பிற்குச் சென்று பஸ் எண்ணைப் போட்டு லொகேஷனை ஆன் செய்யவும்.")

# --- டேப் 3: லைவ் GPS பகிர ---
with tab3:
    st.subheader("📡 நீங்கள் பயணிக்கும் பஸ்ஸின் இடத்தைப் பகிருங்கள்")
    bus_list = sorted(routes_df["Bus_No"].astype(str).unique()) if not routes_df.empty else ["25G", "21G"]
    bus_input = st.selectbox("பேருந்து எண்:", bus_list)
    crowd_status = st.radio(
        "பஸ்ஸில் கூட்டம் எப்படி உள்ளது?",
        ["🟢 சீட் காலியாக உள்ளது", "🟡 நின்று கொண்டு வரலாம்", "🔴 அதிக கூட்டம்"]
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
        st.success(f"✅ **{bus_input}** பேருந்தின் லைவ் இடம் (**{area_name}**) அனைவருக்கும் பகிரப்பட்டுவிட்டது!")
