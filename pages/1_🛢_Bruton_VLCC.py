import streamlit as st

st.set_page_config(page_title="Bruton Simulator", page_icon="🛢")
st.title("🛢 Bruton Ltd: VLCC Simulator")

# --- MEMORY INITIALIZATION ---
# 1. Check if we have a saved value. If not, set the default (60,000).
if 'bruton_spot' not in st.session_state:
    st.session_state['bruton_spot'] = 60000
if 'bruton_spread' not in st.session_state:
    st.session_state['bruton_spread'] = 150

# --- SIDEBAR INPUTS ---
st.sidebar.header("Market Scenarios")

# 2. Add the 'key' argument. This links the slider to the memory above.
spot_rate = st.sidebar.slider("VLCC Spot Rate (TD3C)", 20000, 120000, key='bruton_spot', step=5000)
fuel_spread = st.sidebar.slider("Hi5 Fuel Spread", 50, 400, key='bruton_spread', step=10)

# --- THE ENGINE ---
FLEET_COUNT = 6
COMPANY_SHARES = 52400000
BREAKEVEN = 34000 

scrubber_bonus = (fuel_spread / 100) * 4000 
achieved_tce = spot_rate + scrubber_bonus + 3000
daily_profit = max(0, achieved_tce - BREAKEVEN)

annual_fcf = daily_profit * FLEET_COUNT * 365
annual_dps = annual_fcf / COMPANY_SHARES
quarterly_dps = annual_dps / 4

# Report to Dashboard
if 'projections' not in st.session_state: st.session_state['projections'] = {}
st.session_state['projections']['Bruton'] = quarterly_dps

col1, col2 = st.columns(2)
col1.metric("Achieved TCE", f"${achieved_tce:,.0f}", f"Spread Bonus: +${scrubber_bonus:.0f}")
col2.metric("Proj. Quarterly Dividend", f"${quarterly_dps:.3f}")
