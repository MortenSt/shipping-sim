import streamlit as st

st.set_page_config(page_title="BW LPG Simulator", page_icon="🔥")
st.title("🔥 BW LPG: The Gas Arbitrage")

SHARES_OUTSTANDING = 151500000 
OWNED_DAYS = 4050
BREAKEVEN = 22000

st.sidebar.header("Shipping Market")
spot_rate = st.sidebar.slider("VLGC Spot Rate", 10000, 100000, 45000, step=1000)

st.sidebar.header("Trading Division")
trading_result = st.sidebar.number_input("Trading Profit/Loss (USD)", min_value=-50000000, max_value=100000000, value=15000000, step=5000000)

daily_margin = spot_rate - BREAKEVEN
shipping_profit = daily_margin * OWNED_DAYS
total_net_profit = shipping_profit + trading_result
q_dps = max(0, total_net_profit) / SHARES_OUTSTANDING

if 'projections' not in st.session_state: st.session_state['projections'] = {}
st.session_state['projections']['BW LPG'] = q_dps

col1, col2 = st.columns(2)
col1.metric("Shipping Profit", f"${shipping_profit/1e6:.1f}M")
col2.metric("Trading Result", f"${trading_result/1e6:.1f}M")
st.divider()
st.metric("Total Projected Dividend", f"${q_dps:.3f}")
