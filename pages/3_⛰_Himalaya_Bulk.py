import streamlit as st

st.set_page_config(page_title="Himalaya Simulator", page_icon="⛰")
st.title("⛰ Himalaya Shipping: Dynamic Breakeven")

# --- 1. CONFIGURATION ---
SHARES_OUTSTANDING = 46650000 
FLEET_COUNT = 12

# --- 2. TIMELINE SELECTOR (NEW) ---
st.sidebar.header("Simulation Period")
# We map the quarters to a "step" number (0, 1, 2, 3...)
quarters = {
    "Q1 2026": 0,
    "Q2 2026": 1,
    "Q3 2026": 2,
    "Q4 2026": 3,
    "Q1 2027": 4,
    "Q2 2027": 5,
    "Q3 2027": 6,
    "Q4 2027": 7
}

target_qtr = st.sidebar.selectbox("Select Target Quarter", list(quarters.keys()))

# --- 3. DYNAMIC BREAKEVEN LOGIC ---
base_cbe = 24900
reduction_per_qtr = 267
steps = quarters[target_qtr]

# The Math: Start at 24900, subtract 267 for every quarter passed
dynamic_breakeven = base_cbe - (steps * reduction_per_qtr)

# --- 4. MARKET INPUTS ---
# Initialize defaults if not set
if 'hshp_bdi' not in st.session_state: st.session_state['hshp_bdi'] = 25000
if 'hshp_prem' not in st.session_state: st.session_state['hshp_prem'] = 138
if 'hshp_spread' not in st.session_state: st.session_state['hshp_spread'] = 120

st.sidebar.header("Market Drivers")
bdi_5tc = st.sidebar.slider("Baltic Capesize Index (5TC)", 10000, 80000, key='hshp_bdi', step=500)
premium_pct = st.sidebar.slider("Newcastlemax Premium (%)", 110, 160, key='hshp_prem', step=1) / 100
fuel_spread = st.sidebar.slider("Fuel Spread (Hi5) $/ton", 0, 500, key='hshp_spread', step=10)

# --- 5. THE ENGINE ---
# Revenue Calculation
freight_rate = bdi_5tc * premium_pct
scrubber_bonus = fuel_spread * 45 
total_tce = freight_rate + scrubber_bonus

# Profit Calculation using DYNAMIC Breakeven
daily_margin = total_tce - dynamic_breakeven
monthly_cash_flow = daily_margin * FLEET_COUNT * 30.4 
monthly_dps = max(0, monthly_cash_flow / SHARES_OUTSTANDING)

# --- 6. REPORT TO DASHBOARD ---
if 'projections' not in st.session_state: st.session_state['projections'] = {}
# Dashboard expects Quarterly equivalent
st.session_state['projections']['Himalaya'] = monthly_dps * 3

# --- 7. DISPLAY ---
# Visualizing the lower breakeven
col1, col2 = st.columns(2)
col1.metric("Achieved Rate", f"${total_tce:,.0f}")
col2.metric("Est. Monthly Dividend", f"${monthly_dps:.3f}", f"Qtr: {target_qtr}")

st.divider()

# Explain the Breakeven Benefit
c1, c2, c3 = st.columns(3)
c1.metric("Current Breakeven", f"${dynamic_breakeven:,.0f}", f"-${(steps * reduction_per_qtr)} from base")
c2.metric("Base (Q1 2026)", f"${base_cbe:,}")
c3.metric("Reduction/Qtr", f"-${reduction_per_qtr}")

st.info(f"**Debt Paydown Benefit:** In **{target_qtr}**, your breakeven is **${dynamic_breakeven:,}**. This saves **${(steps * reduction_per_qtr * FLEET_COUNT * 30):,.0f}** per month compared to Q1 2026, which flows directly to the dividend.")
