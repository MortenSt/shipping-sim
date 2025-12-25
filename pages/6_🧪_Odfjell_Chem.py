import streamlit as st

st.set_page_config(page_title="Odfjell Simulator", page_icon="🧪")
st.title("🧪 Odfjell SE: Chemical Tanker Cycle")

SHARES_OUTSTANDING = 79700000 
FLEET_COUNT = 70
BREAKEVEN = 24000

st.sidebar.header("Chemical Tanker Market")
avg_tce = st.sidebar.slider("Avg Fleet TCE ($/day)", 20000, 45000, 31000, step=500)
payout_ratio = st.sidebar.slider("Payout Ratio (%)", 40, 70, 50, step=5) / 100

daily_profit_per_ship = avg_tce - BREAKEVEN
quarterly_net_income = daily_profit_per_ship * FLEET_COUNT * 90 * 0.95 # 5% tax/leakage
q_dps = max(0, (quarterly_net_income * payout_ratio) / SHARES_OUTSTANDING)

if 'projections' not in st.session_state: st.session_state['projections'] = {}
st.session_state['projections']['Odfjell'] = q_dps

col1, col2 = st.columns(2)
col1.metric("Net Income (Qtr)", f"${quarterly_net_income/1e6:.1f}M")
col2.metric("Proj. Dividend", f"${q_dps:.3f}")
