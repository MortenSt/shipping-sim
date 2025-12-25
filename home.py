import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Shipping Alpha", page_icon="⚓", layout="wide")

# --- 1. THE BOUNCER (Global Password) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_password():
    # Looks for 'site_password' in your secrets file
    if st.secrets.get("general", {}).get("site_password") == st.session_state['password_input']:
        st.session_state['authenticated'] = True
    elif st.secrets.get("general", {}).get("site_password") is None:
        st.warning("No password set in Secrets. allowing access for testing.")
        st.session_state['authenticated'] = True
    else:
        st.error("Incorrect password")

if not st.session_state['authenticated']:
    st.title("🔒 Private Access Only")
    st.text_input("Enter Access Code:", type="password", key="password_input", on_change=check_password)
    st.stop()

# =========================================================
# 🚢 THE APP STARTS HERE
# =========================================================

st.title("⚓ Shipping Portfolio Simulator")

# --- 2. SETUP PORTFOLIO DEFAULTS ---
companies = ["Himalaya", "MPCC", "HAUTO", "Bruton", "BW LPG", "Odfjell"]

if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = {ticker: {"shares": 0, "gav": 0.0} for ticker in companies}
    
    # OWNER AUTO-LOAD: Check if "my_portfolio" exists in secrets
    if "my_portfolio" in st.secrets:
        st.toast("Owner Identity Recognized. Portfolio Loaded.", icon="👑")
        for ticker in companies:
            if ticker in st.secrets["my_portfolio"]:
                data = st.secrets["my_portfolio"][ticker]
                st.session_state['portfolio'][ticker] = {"shares": data['shares'], "gav": data['gav']}

if 'projections' not in st.session_state:
    st.session_state['projections'] = {ticker: 0.0 for ticker in companies}

# --- 3. FRIEND ZONE: FILE UPLOADER ---
with st.sidebar.expander("📂 Load Portfolio File"):
    uploaded_file = st.file_uploader("Drag your JSON file here", type=['json'])
    if uploaded_file is not None:
        try:
            friend_data = json.load(uploaded_file)
            for ticker in companies:
                if ticker in friend_data:
                    st.session_state['portfolio'][ticker] = friend_data[ticker]
            st.success("Portfolio Loaded Successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# --- 4. MANUAL ADJUSTMENTS (Sidebar) ---
st.sidebar.header("💼 Adjust Positions")
for ticker in companies:
    with st.sidebar.expander(ticker):
        curr_s = st.session_state['portfolio'][ticker]['shares']
        curr_g = st.session_state['portfolio'][ticker]['gav']
        
        s = st.number_input(f"Shares", value=curr_s, key=f"{ticker}_s")
        g = st.number_input(f"GAV", value=curr_g, key=f"{ticker}_g")
        st.session_state['portfolio'][ticker] = {"shares": s, "gav": g}

# --- 5. DASHBOARD DISPLAY ---
st.subheader("📊 Live Projections")
st.info("Edit market assumptions in the sidebar pages to update these dividends.")

total_income = 0
total_invested = 0
data = []

for ticker in companies:
    p = st.session_state['portfolio'][ticker]
    shares = p['shares']
    gav = p['gav']
    div = st.session_state['projections'].get(ticker, 0.0)
    
    income = shares * div
    invested = shares * gav
    
    total_income += income
    total_invested += invested
    
    if shares > 0:
        yoc = (div * 4 / gav) * 100 if gav > 0 else 0
        data.append({
            "Ticker": ticker, 
            "Shares": f"{shares:,}", 
            "Proj. Div (Qtr)": f"${div:.3f}", 
            "My Income": f"${income:,.2f}",
            "Yield on Cost": f"{yoc:.1f}%"
        })

df = pd.DataFrame(data)
if not df.empty:
    st.dataframe(df, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invested", f"${total_invested:,.0f}")
    c2.metric("Quarterly Check", f"${total_income:,.2f}")
    if total_invested > 0:
        c3.metric("Portfolio Yield", f"{(total_income*4/total_invested)*100:.1f}%")
else:
    st.warning("No positions found. Enter shares in the sidebar or upload a file.")

# Download Button
if st.sidebar.button("💾 Download Portfolio Config"):
    json_str = json.dumps(st.session_state['portfolio'])
    st.sidebar.download_button(
        label="Click to Save JSON",
        data=json_str,
        file_name="my_shipping_portfolio.json",
        mime="application/json"
    )
