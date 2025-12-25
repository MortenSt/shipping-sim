import streamlit as st

st.set_page_config(page_title="HAUTO Simulator", page_icon="🚗")
st.title("🚗 Hoegh Autoliners: The Contract Machine")

SHARES_OUTSTANDING = 190769749
FLEET_CAPACITY_CBM = 40000000
OPEX_AND_DEBT = 600000000

st.sidebar.header("Contract Renewals")
avg_net_rate = st.sidebar.slider("Avg Net Rate ($/cbm)", 60.0, 130.0, 93.0, step=0.5)
quarterly_capex = st.sidebar.number_input("Quarterly Capex (USD)", value=50000000, step=5000000)

annual_revenue = FLEET_CAPACITY_CBM * 0.95 * avg_net_rate
quarterly_operating_cash = (annual_revenue - OPEX_AND_DEBT) / 4
fcf_equity = max(0, quarterly_operating_cash - quarterly_capex)
q_dps = fcf_equity / SHARES_OUTSTANDING

if 'projections' not in st.session_state: st.session_state['projections'] = {}
st.session_state['projections']['HAUTO'] = q_dps

col1, col2 = st.columns(2)
col1.metric("Blended Rate", f"${avg_net_rate:.1f}/cbm")
col2.metric("Proj. Dividend", f"${q_dps:.3f}")
