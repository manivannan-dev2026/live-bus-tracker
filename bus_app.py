import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import pandas as pd
import datetime

st.set_page_config(page_title="நம்ம தமிழ்நாடு Smart Bus", page_icon="🚌")

st.title("🚌 நம்ம தமிழ்நாடு Smart Bus")
st.write("சென்னை, திருவள்ளூர், செங்கல்பட்டு & காஞ்சிபுரம் பேருந்து வழித்தடங்கள் மற்றும் லைவ் இருப்பிடம்!")

# 1. பொதுவான லைவ் டேட்டாபேஸ்
@st.cache_resource
def get_live_bus_db():
    return {}

live_bus_db = get_live_bus_db()

# 2. 4 மாவட்டங்களின் பேருந்து தரவுகள் (எந்த CSV எரரும் வராமல் நேரடியாக கோடிற்குள்!)
@st.cache_resource
def get_bus_routes():
    data = [
        {"Bus_No": "25G", "From": "பூந்தமல்லி", "To": "மயிலாப்பூர்", "Stops": "பூந்தமல்லி - போரூர் - வடபழனி - தி.நகர் - மயிலாப்பூர்"},
        {"Bus_No": "26", "From": "பூந்தமல்லி", "To": "மயிலாப்பூர்", "Stops": "பூந்தமல்லி - கரையான்சாவடி - போரூர் - சாலிகிராமம் - மயிலாப்பூர்"},
        {"Bus_No": "54", "From": "பூந்தமல்லி", "To": "பிராட்வே", "Stops": "பூந்தமல்லி - போரூர் - கிண்டி - சைதாப்பேட்டை - எழும்பூர் - பிராட்வே"},
        {"Bus_No": "101", "From": "பூந்தமல்லி", "To": "திருவொற்றியூர்", "Stops": "பூந்தமல்லி - மதுரவாயல் - கோயம்பேடு - அண்ணா நகர் - பாரிமுனை - திருவொற்றியூர்"},
        {"Bus_No": "572", "From": "திருவள்ளூர்", "To": "அம்பத்தூர்", "Stops": "திருவள்ளூர் - மணவாள நகர் - வேப்பம்பட்டு - திருநின்றவூர் - ஆவடி - அம்பத்தூர்"},
        {"Bus_No": "597", "From": "திருவள்ளூர்", "To": "தி.நகர்", "Stops": "திருவள்ளூர் - மப்பேடு - பூந்தமல்லி - போரூர் - கிண்டி - தி.நகர்"},
        {"Bus_No": "580", "From": "திருவள்ளூர்", "To": "ஆவடி", "Stops": "திருவள்ளூர் - செவ்வாப்பேட்டை - வேப்பம்பட்டு - பட்டாபிராம் - ஆவடி"},
        {"Bus_No": "40A", "From": "ஆவடி", "To": "அண்ணா சதுக்கம்", "Stops": "ஆவடி - திருமுல்லைவாயல் - அம்பத்தூர் - அண்ணா நகர் - எழும்பூர் - அண்ணா சதுக்கம்"},
        {"Bus_No": "77", "From": "ஆவடி", "To": "கோயம்பேடு", "Stops": "ஆவடி - அம்பத்தூர் - பாடி - திருமங்கலம் - கோயம்பேடு"},
        {"Bus_No": "557", "From": "கும்மிடிப்பூண்டி", "To": "பிராட்வே", "Stops": "கும்மிடிப்பூண்டி - கவரப்பேட்டை - பொன்னேரி - காரனோடை - ரெட்ஹில்ஸ் - பிராட்வே"},
        {"Bus_No": "576", "From": "காஞ்சிபுரம்", "To": "தி.நகர்", "Stops": "காஞ்சிபுரம் - சுங்குவார்சத்திரம் - ஸ்ரீபெரும்புதூர் - பூந்தமல்லி - போரூர் - தி.நகர்"},
        {"Bus_No": "578", "From": "காஞ்சிபுரம்", "To": "வடபழனி", "Stops": "காஞ்சிபுரம் - வாலாஜாபாத் - ஒரகடம் - படப்பை - தாம்பரம் - கிண்டி - வடபழனி"},
        {"Bus_No": "79", "From": "காஞ்சிபுரம்", "To": "தாம்பரம்", "Stops": "காஞ்சிபுரம் - வாலாஜாபாத் - ஒரகடம் - முடிச்சூர் - தாம்பரம்"},
        {"Bus_No": "583", "From": "ஸ்ரீபெரும்புதூர்", "To": "தாம்பரம்", "Stops": "ஸ்ரீபெரும்புதூர் - மண்ணிவாக்கம் - படப்பை - முடிச்சூர் - தாம்பரம்"},
        {"Bus_No": "21G", "From": "தாம்பரம்", "To": "பிராட்வே", "Stops": "தாம்பரம் - குரோம்பேட்டை - பல்லாவரம் - கிண்டி - சைதாப்பேட்டை - பிராட்வே"},
        {"Bus_No": "70C", "From": "கோயம்பேடு", "To": "தாம்பரம்", "Stops": "கோயம்பேடு - வடபழனி - அசோக் பில்லர் - கிண்டி - பல்லாவரம் - தாம்பரம்"},
        {"Bus_No": "91", "From": "வேளச்சேரி", "To": "தாம்பரம்", "Stops": "வேளச்சேரி - பள்ளிக்கரணை - மேடவாக்கம் - சேலையூர் - தாம்பரம்"},
        {"Bus_No": "515", "From": "தாம்பரம்", "To": "மாமல்லபுரம்", "Stops": "தாம்பரம் - பெருங்களத்தூர் - வண்டலூர் - கேளம்பாக்கம் - திருப்போரூர் - மாமல்லபுரம்"},
        {"Bus_No": "500", "From": "செங்கல்பட்டு", "To": "தி.நகர்", "Stops": "செங்கல்பட்டு - சிங்கப்பெருமாள் கோவில் - மறைமலைநகர் - கூடுவாஞ்சேரி - தாம்பரம் - தி.நகர்"},
        {"Bus_No": "568C", "From": "கல்பாக்கம்", "To": "தி.நகர்", "Stops": "கல்பாக்கம் - மாமல்லபுரம் - கோவளம் - சோழிங்கநல்லூர் - அடையாறு - தி.நகர்"},
        {"Bus_No": "TNSTC-801", "From": "செங்கல்பட்டு", "To": "காஞ்சிபுரம்", "Stops": "செங்கல்பட்டு - பாலூர் - வாலாஜாபாத் - அய்யம்பேட்டை - காஞ்சிபுரம்"},
        {"Bus_No": "TNSTC-804", "From": "மதுராந்தகம்", "To": "தாம்பரம்", "Stops": "மதுராந்தகம் - படாளம் - செங்கல்பட்டு - கூடுவாஞ்சேரி - தாம்பரம்"}
    ]
    return pd.DataFrame(data)

routes_df = get_bus_routes()

def ஏரியா_பெயர்_கண்டுபிடி(lat, lon):
    try:
        geolocator = Nominatim(user_agent="tn_smart_bus_safe")
        location = geolocator.reverse((lat, lon), exactly_one=True, language="ta")
        if location and location.address:
            parts = location.address.split(",")[:3]
            return ", ".join(parts)
    except:
        pass
    return f"GPS: {round(lat, 4)}, {round(lon, 4)}"

# நான்கு டேப்கள் (புதிய பஸ் சேர்க்கும் டேப்புடன்!)
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 பஸ் தேட", 
    "📍 லைவ் மேப்", 
    "📡 லைவ் GPS பகிர",
    "➕ புதிய பஸ் சேர்க்க"
])

# --- டேப் 1: பஸ் தேடுதல் ---
with tab1:
    st.subheader("🔍 ஊர் அல்லது நிறுத்தம் பெயரை உள்ளிடவும்")
    தேடும்_ஊர் = st.text_input("ஊர் பெயர் (எ.கா: போரூர், தாம்பரம், திருவள்ளூர், காஞ்சிபுரம், கிண்டி):").strip()
    
    if தேடும்_ஊர்:
        matched = routes_df[
            routes_df["From"].str.contains(தேடும்_ஊர், case=False, na=False) |
            routes_df["To"].str.contains(தேடும்_ஊர், case=False, na=False) |
            routes_df["Stops"].str.contains(தேடும்_ஊர், case=False, na=False)
        ]
        
        if not matched.empty:
            st.success(f"✅ **'{தேடும்_ஊர்}'** வழியாகச் செல்லும் {len(matched)} பேருந்துகள்:")
            for _, row in matched.iterrows():
                bus_no = str(row["Bus_No"])
                st.info(f"🚌 **பேருந்து: {bus_no}** ({row['From']} ➡️ {row['To']})\n\n🛣️ **வழி:** {row['Stops']}")
                if bus_no in live_bus_db:
                    live_info = live_bus_db[bus_no]
                    st.warning(f"🟢 **LIVE:** இப்போது **{live_info['area']}** அருகே வருகிறது! | 👥 {live_info['crowd']}")
        else:
            st.warning(f"❌ '{தேடும்_ஊர்}' என்ற பெயரில் பேருந்து இல்லை. 4-வது டேப்பில் நீங்களே சேர்க்கலாம்!")
    else:
        st.dataframe(routes_df, use_container_width=True)

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
        st_folium(view_map, width=700, height=350, key="safe_map")
    else:
        st.info("ℹ️ இப்போது எந்தப் பேருந்தும் லைவில் இல்லை. 3-வது டேப்பிற்குச் சென்று பஸ் எண்ணைப் போட்டு லொகேஷனை ஆன் செய்யவும்.")

# --- டேப் 3: லைவ் GPS பகிர ---
with tab3:
    st.subheader("📡 நீங்கள் பயணிக்கும் பஸ்ஸின் இடத்தைப் பகிருங்கள்")
    bus_list = sorted(routes_df["Bus_No"].astype(str).unique())
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
            "lat": lat, "lon": lon, "area": area_name, "crowd": crowd_status, "time": current_time
        }
        st.success(f"✅ **{bus_input}** பேருந்தின் லைவ் இடம் (**{area_name}**) அனைவருக்கும் பகிரப்பட்டுவிட்டது!")

# --- டேப் 4: புதிய பஸ் சேர்க்க ---
with tab4:
    st.subheader("➕ புதிய பேருந்து எண் மற்றும் ஊர்களைச் சேர்க்கவும்")
    with st.form("add_bus_form"):
        new_bus = st.text_input("பேருந்து எண் (எ.கா: 154 அல்லது 570):")
        new_from = st.text_input("புறப்படும் ஊர்:")
        new_to = st.text_input("சேரும் ஊர்:")
        new_stops = st.text_input("செல்லும் நிறுத்தங்கள்:")
        if st.form_submit_button("சேர்க்கவும் (Add Bus)"):
            if new_bus and new_from and new_to:
                routes_df.loc[len(routes_df)] = [new_bus, new_from, new_to, new_stops]
                st.success(f"🎉 **{new_bus} ({new_from} ➡️ {new_to})** சேர்க்கப்பட்டுவிட்டது! முதல் டேப்பில் தேடிப் பாருங்கள்.")
