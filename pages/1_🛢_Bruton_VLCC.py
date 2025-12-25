import streamlit as st

st.set_page_config(page_title="Bruton Simulator", page_icon="🛢")
st.title("🛢 Bruton Ltd: VLCC Simulator")

st.sidebar.header("Market Scenarios")
spot_rate = st.sidebar.slider("VLCC Spot Rate (TD3C)", 20000, 120000, 60000, step=5000)
fuel_spread = st.sidebar.slider("Hi5 Fuel Spread", 50, 400, 150, step=10)

FLEET_COUNT = 6
COMPANY_SHARES = 52400000
BREAKEVEN = 34000 

scrubber_bonus = (fuel_spread / 100) * 4000 
achieved_tce = spot_rate + scrubber_bonus + 3000
daily_profit = max(0, achieved_tce - BREAKEVEN)

annual_fcf = daily_profit * FLEET_COUNT * 365
annual_dps = annual_fcf / COMPANY_SHARES
quarterly_dps = annual_dps / 4

if 'projections' not in st.session_state: st.session_state['projections'] = {}
st.session_state['projections']['Bruton'] = quarterly_dps

col1, col2 = st.columns(2)
col1.metric("Achieved TCE", f"${achieved_tce:,.0f}", f"Spread Bonus: +${scrubber_bonus:.0f}")
col2.metric("Proj. Quarterly Dividend", f"${quarterly_dps:.3f}")
