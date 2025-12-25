import streamlit as st

st.set_page_config(page_title="Himalaya Simulator", page_icon="⛰")
st.title("⛰ Himalaya Shipping: Newcastlemax Premium")

st.sidebar.header("Market Drivers")
bdi_5tc = st.sidebar.slider("Baltic Capesize Index (5TC)", 10000, 80000, 25000, step=500)
premium_pct = st.sidebar.slider("Newcastlemax Premium (%)", 110, 160, 138, step=1) / 100
fuel_spread = st.sidebar.slider("Fuel Spread (Hi5) $/ton", 0, 500, 120, step=10)

SHARES_OUTSTANDING = 46650000
FLEET_COUNT = 12
BREAKEVEN = 24000 

freight_rate = bdi_5tc * premium_pct
scrubber_bonus = fuel_spread * 45 
total_tce = freight_rate + scrubber_bonus

daily_margin = total_tce - BREAKEVEN
monthly_cash_flow = daily_margin * FLEET_COUNT * 30.4 
monthly_dps = max(0, monthly_cash_flow / SHARES_OUTSTANDING)

if 'projections' not in st.session_state: st.session_state['projections'] = {}
# Dashboard expects Quarterly, so we multiply monthly * 3
st.session_state['projections']['Himalaya'] = monthly_dps * 3

col1, col2 = st.columns(2)
col1.metric("Achieved Rate", f"${total_tce:,.0f}", f"Prem: {(premium_pct-1)*100:.0f}% | Scrub: ${scrubber_bonus:,.0f}")
col2.metric("Proj. Quarterly Dividend", f"${monthly_dps*3:.3f}", "Paid Monthly")
