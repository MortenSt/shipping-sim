import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Shipping Alpha", page_icon="⚓", layout="wide")

# --- 1. THE BOUNCER (Global Password) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_password():
    # Looks for 'site_password' in your secrets file
    # If no secrets file exists, we allow access (for testing purposes)
    secret_pass = st.secrets.get("general", {}).get("site_password")
    if secret_pass is None or secret_pass == st.session_state['password_input']:
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

st.title("⚓ Shipping Portfolio (NOK)")

# --- 2. GLOBAL SETTINGS (USD/NOK) ---
with st.sidebar:
    st.header("💱 Currency Settings")
    usd_nok = st.number_input("USD/NOK Exchange Rate", value=11.0, step=0.1, format="%.2f")
    st.divider()

# --- 3. SETUP PORTFOLIO DEFAULTS ---
companies = ["Himalaya", "MPCC", "HAUTO", "Bruton", "BW LPG", "Odfjell"]

if 'portfolio' not in st.session_state:
    # Default structure
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

# --- 4. FRIEND ZONE: FILE UPLOADER ---
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

# --- 5. MANUAL ADJUSTMENTS (Sidebar) ---
st.sidebar.header("💼 Adjust Positions (NOK)")
for ticker in companies:
    with st.sidebar.expander(ticker):
        curr_s = st.session_state['portfolio'][ticker]['shares']
        curr_g = st.session_state['portfolio'][ticker]['gav']
        
        # NOTE: GAV is now clearly labeled as NOK
        s = st.number_input(f"Shares", value=curr_s, key=f"{ticker}_s")
        g = st.number_input(f"Avg Cost (NOK)", value=curr_g, key=f"{ticker}_g")
        st.session_state['portfolio'][ticker] = {"shares": s, "gav": g}

# --- 6. DASHBOARD DISPLAY ---
st.subheader(f"📊 Projected Income @ {usd_nok} USD/NOK")
st.info("Dividends are calculated in USD by the simulators, then converted to NOK here.")

total_income_nok = 0
total_invested_nok = 0
data = []

for ticker in companies:
    p = st.session_state['portfolio'][ticker]
    shares = p['shares']
    gav_nok = p['gav']
    
    # Get the USD dividend from the simulator pages
    div_usd = st.session_state['projections'].get(ticker, 0.0)
    
    # CONVERSION LOGIC
    div_nok = div_usd * usd_nok
    income_nok = shares * div_nok
    invested_nok = shares * gav_nok
    
    total_income_nok += income_nok
    total_invested_nok += invested_nok
    
    if shares > 0:
        # Yield is (Annualized NOK Dividend / NOK Cost Basis)
        yoc = (div_nok * 4 / gav_nok) * 100 if gav_nok > 0 else 0
        
        data.append({
            "Ticker": ticker, 
            "Shares": f"{shares:,}", 
            "Div (USD)": f"${div_usd:.3f}", 
            "Div (NOK)": f"{div_nok:.2f} kr", 
            "My Income (NOK)": f"{income_nok:,.0f} kr",
            "Yield (NOK)": f"{yoc:.1f}%"
        })

df = pd.DataFrame(data)

if not df.empty:
    # Display the table
    st.dataframe(df, use_container_width=True)
    
    # Display the Big Metrics
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Total Invested (NOK)", f"{total_invested_nok:,.0f} kr")
    
    # Conditional formatting for income
    c2.metric("Quarterly Check (NOK)", f"{total_income_nok:,.0f} kr", f"USD Rate: {usd_nok}")
    
    if total_invested_nok > 0:
        portfolio_yield = (total_income_nok * 4 / total_invested_nok) * 100
        c3.metric("Portfolio Yield", f"{portfolio_yield:.1f}%")
else:
    st.warning("No positions found. Enter shares in the sidebar to see calculations.")

# Download Button
if st.sidebar.button("💾 Download Portfolio Config"):
    json_str = json.dumps(st.session_state['portfolio'])
    st.sidebar.download_button(
        label="Click to Save JSON",
        data=json_str,
        file_name="my_shipping_portfolio.json",
        mime="application/json"
    )
