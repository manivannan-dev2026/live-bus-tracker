import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import datetime

st.set_page_config(page_title="நம்ம தமிழ்நாடு Smart Bus", page_icon="🚌")

st.title("🚌 நம்ம தமிழ்நாடு Smart Bus")
st.write("நேரடிப் பயணத்தின் போது பஸ் இருப்பிடத்தை அறியும் செயலி!")

# 1. புதிய லைவ் மெமரி (v3)
@st.cache_resource
def get_live_db_v3():
    return {}

live_db = get_live_db_v3()

# 2. பேருந்து தரவுகள்
@st.cache_resource
def get_routes_v3():
    data = [
        {"Bus_No": "25G", "From": "பூந்தமல்லி", "To": "மயிலாப்பூர்", "Stops": "பூந்தமல்லி - போரூர் - வடபழனி - தி.நகர் - மயிலாப்பூர்"},
        {"Bus_No": "26", "From": "பூந்தமல்லி", "To": "மயிலாப்பூர்", "Stops": "பூந்தமல்லி - கரையான்சாவடி - போரூர் - சாலிகிராமம் - மயிலாப்பூர்"},
        {"Bus_No": "54", "From": "பூந்தமல்லி", "To": "பிராட்வே", "Stops": "பூந்தமல்லி - போரூர் - கிண்டி - சைதாப்பேட்டை - எழும்பூர் - பிராட்வே"},
        {"Bus_No": "572", "From": "திருவள்ளூர்", "To": "அம்பத்தூர்", "Stops": "திருவள்ளூர் - மணவாள நகர் - வேப்பம்பட்டு - திருநின்றவூர் - ஆவடி - அம்பத்தூர்"},
        {"Bus_No": "597", "From": "திருவள்ளூர்", "To": "தி.நகர்", "Stops": "திருவள்ளூர் - மப்பேடு - பூந்தமல்லி - போரூர் - கிண்டி - தி.நகர்"},
        {"Bus_No": "576", "From": "காஞ்சிபுரம்", "To": "தி.நகர்", "Stops": "காஞ்சிபுரம் - சுங்குவார்சத்திரம் - ஸ்ரீபெரும்புதூர் - பூந்தமல்லி - போரூர் - தி.நகர்"},
        {"Bus_No": "79", "From": "காஞ்சிபுரம்", "To": "தாம்பரம்", "Stops": "காஞ்சிபுரம் - வாலாஜாபாத் - ஒரகடம் - முடிச்சூர் - தாம்பரம்"},
        {"Bus_No": "21G", "From": "தாம்பரம்", "To": "பிராட்வே", "Stops": "தாம்பரம் - குரோம்பேட்டை - பல்லாவரம் - கிண்டி - சைதாப்பேட்டை - பிராட்வே"},
        {"Bus_No": "500", "From": "செங்கல்பட்டு", "To": "தி.நகர்", "Stops": "செங்கல்பட்டு - சிங்கப்பெருமாள் கோவில் - மறைமலைநகர் - கூடுவாஞ்சேரி - தாம்பரம் - தி.நகர்"},
        {"Bus_No": "515", "From": "தாம்பரம்", "To": "மாமல்லபுரம்", "Stops": "தாம்பரம் - பெருங்களத்தூர் - வண்டலூர் - கேளம்பாக்கம் - திருப்போரூர் - மாமல்லபுரம்"}
    ]
    return pd.DataFrame(data)

routes_df = get_routes_v3()

tab1, tab2, tab3 = st.tabs(["📡 லைவ் GPS பகிர (இப்போது பஸ்ஸில்)", "📍 லைவ் மேப் பார்க்க", "🔍 பஸ் தேட"])

# --- டேப் 1: பஸ்ஸில் பயணிப்பவர் உடனே GPS பகிர ---
with tab1:
    st.subheader("📡 நீங்கள் இப்போது பயணிக்கும் பஸ்:")
    bus_no = st.text_input("பஸ் நம்பரை டைப் செய்யவும் (எ.கா: 25G அல்லது 21G):", "25G")
    crowd = st.radio("கூட்டம் எப்படி உள்ளது?", ["🟢 சீட் காலி", "🟡 நின்று வரலாம்", "🔴 அதிக கூட்டம்"], horizontal=True)
    
    st.info("👇 கீழே உள்ள சிறிய பட்டனை (📍) அழுத்தினால் உங்கள் பஸ்ஸின் லைவ் இடம் உடனே பதிவாகும்!")
    loc = streamlit_geolocation()
    
    if loc and loc.get("latitude") is not None:
        lat, lon = loc["latitude"], loc["longitude"]
        now = datetime.datetime.now().strftime("%I:%M:%S %p")
        live_db[bus_no] = {"lat": lat, "lon": lon, "crowd": crowd, "time": now}
        
        st.success(f"✅ **{bus_no}** பேருந்தின் லைவ் இடம் பதிவாகிவிட்டது! (நேரம்: {now})")
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker([lat, lon], popup=f"🚌 {bus_no}", icon=folium.Icon(color="green", icon="bus", prefix="fa")).add_to(m)
        st_folium(m, width=700, height=300, key="live_bus_now")

# --- டேப் 2: லைவ் மேப் ---
with tab2:
    st.subheader("📍 லைவில் ஓடும் பேருந்துகள்")
    if live_db:
        sel = st.selectbox("பேருந்தைத் தேர்ந்தெடுக்கவும்:", list(live_db.keys()))
        d = live_db[sel]
        st.success(f"🚌 **{sel}** | 👥 {d['crowd']} | 🕒 {d['time']}")
        m2 = folium.Map(location=[d["lat"], d["lon"]], zoom_start=16)
        folium.Marker([d["lat"], d["lon"]], popup=f"🚌 {sel}", icon=folium.Icon(color="red", icon="bus", prefix="fa")).add_to(m2)
        st_folium(m2, width=700, height=300, key="view_bus_now")
    else:
        st.warning("⚠️ முதல் டேப்பிற்குச் சென்று 📍 பட்டனை அழுத்தினால் இங்கே பஸ் லைவாகத் தெரியும்!")

# --- டேப் 3: ஊர் தேடுதல் ---
with tab3:
    st.subheader("🔍 ஊர் பெயர் தேட")
    q = st.text_input("ஊர் பெயர் (எ.கா: போரூர், தாம்பரம், திருவள்ளூர்):").strip()
    if q:
        res = routes_df[routes_df["Stops"].str.contains(q, case=False, na=False)]
        st.dataframe(res, use_container_width=True)
    else:
        st.dataframe(routes_df, use_container_width=True)
