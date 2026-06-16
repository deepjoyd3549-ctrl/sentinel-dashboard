import streamlit as st
import requests
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# ⚠️ VERY IMPORTANT: Replace this with your actual Web API Key from Firebase!
# KEEP THE QUOTATION MARKS! Example: "AIzaSy..."
FIREBASE_WEB_API_KEY = "AIzaSyD1EmHInF3eYXKad9lJL_Tj2oxEdePwKSU"

# ____ Page Configuration ____
st.set_page_config(page_title="🛡️ SENTINEL COMMAND CENTER", layout="wide", initial_sidebar_state="expanded")

# --- FIREBASE AUTHENTICATION LOGIC ---
def verify_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    try:
        response = requests.post(url, json=payload)
        if response.ok:
            return True
        else:
            st.error(f"SYSTEM LOG: {response.json()}") 
            return False
    except Exception as e:
        st.error(f"NETWORK LOG: {e}")
        return False

# Initialize session state so the user stays logged in
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- THE LOGIN SCREEN (BLAST DOORS) ---
if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FF9900;'>🛡️ SENTINEL</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #00FF9D; letter-spacing: 2px;'>RESTRICTED ACCESS</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Admin ID")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("AUTHENTICATE", use_container_width=True)
            
            if submit:
                if verify_login(email, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Invalid Credentials")

# --- THE ACTUAL DASHBOARD (Only runs if authenticated) ---
else:
    # ____ Custom CSS ____
    st.markdown("""
        <style>
        h1 { color: #00FFCC; font-family: 'Courier New', Courier, monospace; text-align: center; text-shadow: 0px 0px 10px #00FFCC;}
        h2, h3 { color: #00C853; font-family: 'Courier New', Courier, monospace; }
        .stMetric { background-color: #1A1A2E; padding: 15px; border-radius: 10px; border-left: 5px solid #00C853; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.5);}
        .critical-alert { background-color: rgba(255, 0, 0, 0.1); padding: 20px; border-radius: 10px; border-left: 5px solid #FF0000; color: #FF4B4B; font-family: monospace; border: 1px solid #FF0000; box-shadow: 0px 0px 15px rgba(255, 0, 0, 0.3);}
        .warning-alert { background-color: rgba(255, 165, 0, 0.1); padding: 20px; border-radius: 10px; border-left: 5px solid orange; color: orange; font-family: monospace; border: 1px solid orange;}
        </style>
        """, unsafe_allow_html=True)

    # ENTERPRISE VENDOR MAPPING DICTIONARY
    VENDOR_MAP = {
        "00:1C:B3": "Apple",
        "00:00:F0": "Samsung",
        "00:1A:A1": "Cisco",
        "B8:27:EB": "🚨 Rogue IoT (Raspberry Pi)",
        "00:50:F2": "Microsoft",
        "3C:5A:B4": "Google",
        "F0:D2:F1": "Amazon",
        "14:F6:5A": "Xiaomi",
        "00:01:4A": "Sony",
        "00:1B:21": "Intel",
        "C0:EE:FB": "OnePlus"
    }

    # FIREBASE ARCHIVE ENDPOINTS
    LATEST_SCAN_URL = "https://sentinel-iot-81214-default-rtdb.firebaseio.com/SentinelReports/latest_scan.json"
    HISTORY_URL = "https://sentinel-iot-81214-default-rtdb.firebaseio.com/SentinelReports/Scan_History.json"

    # ____ SIDEBAR CONTROL PANEL ____
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/cyber-security.png", width=80)
        st.markdown("## 🛡️ SENTINEL OS")
        st.markdown("---")
        st.markdown("**Status:** 🟢 Online")
        st.markdown("**Uplink:** Firebase RTDB")
        
        # NEW CONTROL: Select data mode
        scan_mode = st.radio("SELECT TELEMETRY MODE:", ["🟢 Live Feed (Latest Scan)", "📜 Historical Archives"])
        
        selected_history_log = None
        
        if scan_mode == "📜 Historical Archives":
            try:
                hist_response = requests.get(HISTORY_URL)
                hist_data = hist_response.json()
                
                if hist_data:
                    # Construct a list of records sorted from newest to oldest
                    history_options = []
                    log_mapping = {}
                    
                    for push_id, record in hist_data.items():
                        raw_ts = record.get("timestamp", "0")
                        try:
                            # Convert millisecond string to readable datetime
                            formatted_time = datetime.fromtimestamp(int(raw_ts) / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_time = f"Log ID: {push_id}"
                            
                        history_options.append(formatted_time)
                        log_mapping[formatted_time] = record.get("raw_log", "")
                    
                    # Reverse options so newest is at the top
                    history_options.reverse()
                    
                    selected_time = st.selectbox("CHOOSE HISTORICAL TIMESTAMP:", history_options)
                    if selected_time:
                        selected_history_log = log_mapping[selected_time]
                else:
                    st.info("No logs saved in History database yet.")
            except Exception as e:
                st.error(f"Error fetching history: {e}")

        st.markdown("---")
        if st.button("🔄 Force Refresh Telemetry", use_container_width=True):
            st.rerun()
        
        if st.button("🔒 LOGOUT", type="primary", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # ____ DASHBOARD HEADER ____
    st.markdown("""
        <div style="text-align: center; padding-bottom: 20px;">
            <h1 style="margin-bottom: 0px;">🛡️ SENTINEL COMMAND CENTER</h1>
            <p style="color: #888; font-size: 18px; margin-top: 5px; letter-spacing: 2px;">TACTICAL ASSET & VULNERABILITY INTELLIGENCE</p>
        </div>
        <hr style="border-color: #333; margin-top: 0px;">
    """, unsafe_allow_html=True)

    # --- PARSING ENGINE ---
    @st.cache_data(ttl=2)
    def parse_raw_log_text(raw_log):
        if not raw_log: return [], 0, 0
            
        devices, total_open_ports, critical_threats = [], 0, 0
        current_device = None

        for line in raw_log.split('\n'):
            line = line.strip()
            if line.startswith('[+] ACTIVE:'):
                match = re.search(r'ACTIVE: ([\d\.]+) \[([a-fA-F0-9:]+)\]', line)
                if match:
                    ip, mac = match.group(1), match.group(2)
                    
                    # Match MAC address prefix to Vendor
                    vendor = "Unknown"
                    for mac_prefix, vend_name in VENDOR_MAP.items():
                        if mac_prefix in mac:
                            vendor = vend_name
                            if "Rogue IoT" in vend_name:
                                critical_threats += 1
                            break

                    current_device = {"IP Address": ip, "MAC Address": mac, "Vendor": vendor, "Vulnerabilities": []}
                    devices.append(current_device)
            
            elif line.startswith('[!]Port') and current_device is not None:
                match = re.search(r'Port (\d+) OPEN \(([^)]+)\)', line)
                if match:
                    port, service = match.group(1), match.group(2)
                    current_device["Vulnerabilities"].append(f"{port}/{service}")
                    total_open_ports += 1

        for d in devices:
            d["Vulnerabilities"] = " | ".join(d["Vulnerabilities"]) if d["Vulnerabilities"] else "Secure"

        return devices, total_open_ports, critical_threats

    # Fetch data based on the chosen mode
    raw_log = ""
    if scan_mode == "🟢 Live Feed (Latest Scan)":
        try:
            response = requests.get(LATEST_SCAN_URL)
            data = response.json()
            if data:
                raw_log = data.get("raw_log", "")
        except Exception as e:
            st.error(f"Error fetching live data: {e}")
    else:
        raw_log = selected_history_log if selected_history_log else ""

    # Process Data through parsing engine
    devices, total_ports, critical_threats = parse_raw_log_text(raw_log)

    def highlight_threats(row):
        if "🚨 Rogue IoT" in row['Vendor']:
            return ['background-color: rgba(255, 0, 0, 0.2); color: #ff4b4b; font-weight: bold'] * len(row)
        elif row['Vulnerabilities'] != "Secure":
            return ['background-color: rgba(255, 165, 0, 0.1); color: orange'] * len(row)
        return [''] * len(row)

    if raw_log:
        # Show what time block we are currently viewing
        if scan_mode == "📜 Historical Archives":
            st.info(f"💾 VIEWING ARCHIVED RECORD: {selected_time}")

        # ____ TOP ROW: KPI METRICS ____
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(label="Total Active Assets", value=len(devices))
        with col2: st.metric(label="Exposed Services", value=total_ports, delta=f"{total_ports} Risks" if total_ports > 0 else "Secure", delta_color="inverse")
        with col3: st.metric(label="Critical Anomalies", value=critical_threats, delta="BREACH DETECTED" if critical_threats > 0 else "Clear", delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)

        # ____ MIDDLE ROW: DETAILED TABLES & ALERTS ____
        col_left, col_right = st.columns([2, 1.2])
        
        with col_left:
            st.markdown("### 🖥️ Live Asset Inventory")
            if devices:
                df = pd.DataFrame(devices)
                styled_df = df.style.apply(highlight_threats, axis=1)
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                st.markdown("### 📊 Hardware Fingerprint Distribution")
                vendor_counts = df['Vendor'].value_counts().reset_index()
                vendor_counts.columns = ['Vendor', 'Count']
                
                color_map = {
                    "Apple": "#A2AAAD", "Samsung": "#1428A0", "Cisco": "#00BCEB", 
                    "🚨 Rogue IoT (Raspberry Pi)": "#E30B5C", "Microsoft": "#F35325",
                    "Google": "#FBBC05", "Amazon": "#FF9900", "Xiaomi": "#FF6900",
                    "Sony": "#9E9E9E", "Intel": "#0071C5", "OnePlus": "#F5010C",
                    "Unknown": "#FFFFFF"
                }
                
                fig = px.pie(vendor_counts, names='Vendor', values='Count', hole=0.65, color='Vendor', color_discrete_map=color_map)
                fig.update_traces(
                    textposition='inside', textinfo='percent', 
                    marker=dict(line=dict(color='#0E1117', width=5)), 
                    textfont=dict(size=18, family="Courier New, monospace", color="black"), 
                    hoverinfo="label+percent+name"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                    font=dict(color='#E2E8F0', family="Courier New, monospace", size=14), 
                    margin=dict(t=20, b=20, l=0, r=0),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=16))
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown("### 🚨 Threat Intelligence")
            if critical_threats > 0:
                st.markdown("""
                    <div class="critical-alert">
                        <strong>⚠️ CRITICAL ALERT:</strong><br><br>
                        Unauthorized Rogue IoT Device (Raspberry Pi) detected on network. Immediate physical verification required.
                    </div><br>
                """, unsafe_allow_html=True)
            else:
                st.success("✅ No rogue hardware signatures detected.")
                
            if total_ports > 0:
                st.markdown(f"""
                    <div class="warning-alert">
                        <strong>⚡ WARNING:</strong><br><br>
                        {total_ports} open ports detected. Verify if DNS/SMB services are intentionally exposed.
                    </div>
                """, unsafe_allow_html=True)

        # ____ BOTTOM ROW: RAW LOGS ____
        st.markdown("---")
        with st.expander("Show Raw Encrypted Transmission (JSON/Text)") :
            st.code(raw_log, language="bash")

    else:
        st.warning("Awaiting transmission or no records available for this selected mode.")
