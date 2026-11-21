import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Namma Tamil Nadu Smart Bus", page_icon="🚌")

# 1. நிரந்தர ஃபைல் சேமிப்பு (Permanent CSV Storage)
ROUTES_FILE = "permanent_routes.csv"
LIVE_FILE = "permanent_live_bus.csv"

def load_routes():
    if os.path.exists(ROUTES_FILE):
        return pd.read_csv(ROUTES_FILE)
    default_routes = [
        {"Bus_No": "25G", "From": "பூந்தமல்லி / Poonamallee", "To": "மயிலாப்பூர் / Mylapore", "Stops": "பூந்தமல்லி - போரூர் - வடபழனி - தி.நகர் - மயிலாப்பூர்"},
        {"Bus_No": "26", "From": "பூந்தமல்லி / Poonamallee", "To": "மயிலாப்பூர் / Mylapore", "Stops": "பூந்தமல்லி - கரையான்சாவடி - போரூர் - சாலிகிராமம் - மயிலாப்பூர்"},
        {"Bus_No": "54", "From": "பூந்தமல்லி / Poonamallee", "To": "பிராட்வே / Broadway", "Stops": "பூந்தமல்லி - போரூர் - கிண்டி - சைதாப்பேட்டை - எழும்பூர் - பிராட்வே"},
        {"Bus_No": "572", "From": "திருவள்ளூர் / Thiruvallur", "To": "அம்பத்தூர் / Ambattur", "Stops": "திருவள்ளூர் - திருநின்றவூர் - ஆவடி - அம்பத்தூர்"},
        {"Bus_No": "597", "From": "திருவள்ளூர் / Thiruvallur", "To": "தி.நகர் / T.Nagar", "Stops": "திருவள்ளூர் - பூந்தமல்லி - போரூர் - கிண்டி - தி.நகர்"},
        {"Bus_No": "576", "From": "காஞ்சிபுரம் / Kanchipuram", "To": "தி.நகர் / T.Nagar", "Stops": "காஞ்சிபுரம் - ஸ்ரீபெரும்புதூர் - பூந்தமல்லி - போரூர் - தி.நகர்"},
        {"Bus_No": "79", "From": "காஞ்சிபுரம் / Kanchipuram", "To": "தாம்பரம் / Tambaram", "Stops": "காஞ்சிபுரம் - வாலாஜாபாத் - ஒரகடம் - முடிச்சூர் - தாம்பரம்"},
        {"Bus_No": "21G", "From": "தாம்பரம் / Tambaram", "To": "பிராட்வே / Broadway", "Stops": "தாம்பரம் - குரோம்பேட்டை - பல்லாவரம் - கிண்டி - பிராட்வே"},
        {"Bus_No": "500", "From": "செங்கல்பட்டு / Chengalpattu", "To": "தி.நகர் / T.Nagar", "Stops": "செங்கல்பட்டு - மறைமலைநகர் - கூடுவாஞ்சேரி - தாம்பரம் - தி.நகர்"}
    ]
    df = pd.DataFrame(default_routes)
    df.to_csv(ROUTES_FILE, index=False)
    return df

def load_live_db():
    if os.path.exists(LIVE_FILE):
        return pd.read_csv(LIVE_FILE)
    return pd.DataFrame(columns=["Bus_No", "Lat", "Lon", "Crowd", "Time"])

routes_df = load_routes()
live_df = load_live_db()

# 2. மொழி மாற்றும் பட்டன்
lang = st.radio("🌐 மொழி / Language:", ["தமிழ்", "English"], horizontal=True)

txt = {
    "தமிழ்": {
        "title": "🚌 நம்ம தமிழ்நாடு Smart Bus",
        "sub": "நேரடி GPS இருப்பிடம், கூட்ட நெரிசல் & வழித்தட வழிகாட்டி!",
        "t1": "🔍 பஸ் தேட", "t2": "📍 லைவ் மேப்", "t3": "📡 லைவ் GPS பகிர", "t4": "➕ புதிய பஸ் சேர்க்க",
        "search_lbl": "ஊர் அல்லது நிறுத்தம் பெயரை உள்ளிடவும்:",
        "live_sel": "லைவில் ஓடும் பேருந்தைத் தேர்ந்தெடுக்கவும்:",
        "no_live": "ℹ️ இப்போது எந்தப் பேருந்தும் லைவில் இல்லை.",
        "share_h": "📡 நீங்கள் பயணிக்கும் பஸ்ஸின் இடத்தைப் பகிருங்கள்",
        "crowd_lbl": "பஸ்ஸில் கூட்டம் எப்படி உள்ளது?",
        "gps_info": "👇 கீழே உள்ள 📍 பட்டனை அழுத்தி உங்கள் மொபைல் லொகேஷனை ஆன் செய்யவும்:",
        "add_h": "➕ புதிய பேருந்து வழித்தடத்தை நிரந்தரமாகச் சேர்க்கவும்",
        "save_btn": "✅ நிரந்தரமாகச் சேர்க்கவும்"
    },
    "English": {
        "title": "🚌 Namma Tamil Nadu Smart Bus",
        "sub": "Live Crowdsourced GPS Tracking, Crowd Meter & Route Finder!",
        "t1": "🔍 Search Bus", "t2": "📍 Live Map", "t3": "📡 Share Live GPS", "t4": "➕ Add Route",
        "search_lbl": "Enter City or Bus Stop Name:",
        "live_sel": "Select Active Live Bus:",
        "no_live": "ℹ️ No active live buses at the moment.",
        "share_h": "📡 Share Live Location of Your Bus",
        "crowd_lbl": "Current Crowd Status in Bus:",
        "gps_info": "👇 Click the 📍 button below to share your live mobile GPS:",
        "add_h": "➕ Add a New Bus Route Permanently",
        "save_btn": "✅ Save Route Permanently"
    }
}[lang]

st.title(txt["title"])
st.caption(txt["sub"])

tab1, tab2, tab3, tab4 = st.tabs([txt["t1"], txt["t2"], txt["t3"], txt["t4"]])

# --- டேப் 1: பஸ் தேடுதல் ---
with tab1:
    q = st.text_input(txt["search_lbl"]).strip()
    if q:
        matched = routes_df[
            routes_df["From"].str.contains(q, case=False, na=False) |
            routes_df["To"].str.contains(q, case=False, na=False) |
            routes_df["Stops"].str.contains(q, case=False, na=False)
        ]
        if not matched.empty:
            for _, row in matched.iterrows():
                b_no = str(row["Bus_No"])
                st.info(f"🚌 **{b_no}** ({row['From']} ➡️ {row['To']})\n\n🛣️ {row['Stops']}")
                if not live_df.empty and b_no in live_df["Bus_No"].astype(str).values:
                    l_row = live_df[live_df["Bus_No"].astype(str) == b_no].iloc[-1]
                    st.warning(f"🟢 **LIVE:** {l_row['Crowd']} | 🕒 {l_row['Time']}")
        else:
            st.warning("❌ No matching bus found. You can add it in the 4th tab!")
    else:
        st.dataframe(routes_df, use_container_width=True)

# --- டேப் 2: லைவ் மேப் ---
with tab2:
    latest_live = load_live_db()
    if not latest_live.empty:
        active_buses = latest_live["Bus_No"].astype(str).unique()
        sel_bus = st.selectbox(txt["live_sel"], active_buses)
        bus_info = latest_live[latest_live["Bus_No"].astype(str) == sel_bus].iloc[-1]
        
        st.success(f"🚌 **{sel_bus}** | 👥 {bus_info['Crowd']} | 🕒 {bus_info['Time']}")
        m = folium.Map(location=[float(bus_info["Lat"]), float(bus_info["Lon"])], zoom_start=15)
        folium.Marker([float(bus_info["Lat"]), float(bus_info["Lon"])], popup=f"🚌 {sel_bus}", icon=folium.Icon(color="red", icon="bus", prefix="fa")).add_to(m)
        st_folium(m, width=700, height=350, key="final_bus_map")
    else:
        st.info(txt["no_live"])

# --- டேப் 3: லைவ் GPS பகிர ---
with tab3:
    st.subheader(txt["share_h"])
    bus_in = st.selectbox("Bus No:", sorted(routes_df["Bus_No"].astype(str).unique()))
    crowd_in = st.radio(txt["crowd_lbl"], ["🟢 Seats Available / சீட் காலி", "🟡 Moderate / நின்று வரலாம்", "🔴 Overcrowded / அதிக கூட்டம்"])
    st.info(txt["gps_info"])
    
    loc = streamlit_geolocation()
    if loc and loc.get("latitude") is not None:
        lat, lon = loc["latitude"], loc["longitude"]
        now = datetime.datetime.now().strftime("%d-%m %I:%M %p")
        new_live = pd.DataFrame([{"Bus_No": bus_in, "Lat": lat, "Lon": lon, "Crowd": crowd_in, "Time": now}])
        updated_live = pd.concat([latest_live, new_live], ignore_index=True)
        updated_live.to_csv(LIVE_FILE, index=False)
        st.success(f"✅ **{bus_in}** Live GPS Saved Permanently! ({now})")

# --- டேப் 4: நிரந்தரமாக புதிய பஸ் சேர்க்க ---
with tab4:
    st.subheader(txt["add_h"])
    with st.form("perm_add_bus"):
        nb = st.text_input("Bus No (எ.கா: 154):")
        nf = st.text_input("From (புறப்படும் ஊர்):")
        nt = st.text_input("To (சேரும் ஊர்):")
        ns = st.text_input("Stops (வழித்தடங்கள்):")
        if st.form_submit_button(txt["save_btn"]):
            if nb and nf and nt:
                new_r = pd.DataFrame([{"Bus_No": nb, "From": nf, "To": nt, "Stops": ns}])
                updated_r = pd.concat([routes_df, new_r], ignore_index=True)
                updated_r.to_csv(ROUTES_FILE, index=False)
                st.success(f"🎉 **{nb}** Saved Permanently!")
