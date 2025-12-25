import streamlit as st
import pandas as pd

st.set_page_config(page_title="MPCC Simulator", page_icon="📦")
st.title("📦 MPCC: Backlog Waterfall")

col1, col2 = st.columns(2)
with col1:
    market_rate_2026 = st.number_input("2026 Avg Market Rate", value=22000)
with col2:
    market_rate_2027 = st.number_input("2027 Avg Market Rate", value=16000)

data = [
    {"Qtr": "Q1 2026", "Fixed_Days": 4900, "Open_Days": 100, "Fixed_Rate": 27000, "Mkt_Rate": market_rate_2026},
    {"Qtr": "Q2 2026", "Fixed_Days": 4800, "Open_Days": 200, "Fixed_Rate": 27000, "Mkt_Rate": market_rate_2026},
    {"Qtr": "Q3 2026", "Fixed_Days": 4500, "Open_Days": 500, "Fixed_Rate": 26500, "Mkt_Rate": market_rate_2026},
    {"Qtr": "Q4 2026", "Fixed_Days": 4200, "Open_Days": 800, "Fixed_Rate": 26000, "Mkt_Rate": market_rate_2026},
    {"Qtr": "Q1 2027", "Fixed_Days": 3500, "Open_Days": 1500, "Fixed_Rate": 25000, "Mkt_Rate": market_rate_2027},
    {"Qtr": "Q2 2027", "Fixed_Days": 3000, "Open_Days": 2000, "Fixed_Rate": 24000, "Mkt_Rate": market_rate_2027},
]

df = pd.DataFrame(data)
df['Revenue'] = (df['Fixed_Days'] * df['Fixed_Rate']) + (df['Open_Days'] * df['Mkt_Rate'])
df['EBITDA'] = df['Revenue'] - (5000 * 7000) # Approx OpEx
df['Dividend'] = (df['EBITDA'] * 0.50) / 444000000 

if 'projections' not in st.session_state: st.session_state['projections'] = {}
# Use Q1 2026 as the 'current' projection for the dashboard
st.session_state['projections']['MPCC'] = df.iloc[0]['Dividend']

st.dataframe(df[['Qtr', 'Revenue', 'Dividend']].style.format({"Revenue": "${:,.0f}", "Dividend": "${:.3f}"}))
st.bar_chart(df, x="Qtr", y="Dividend")
