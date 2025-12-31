import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Himalaya Investorguide", page_icon="📘", layout="wide")

# --- INTRODUKSJON (Guiden) ---
st.title("📘 Himalaya Shipping: Investorguide & Kalkulator")

st.markdown("""
### Hvorfor Himalaya Shipping?
Himalaya Shipping (HSHP) er et "pure-play" tørrlastrederi med 12 store Newcastlemax-skip.
Selskapet skiller seg ut på tre områder som driver utbyttekapasiteten:

1.  **Størrelse-Premium:** Skipene tar 210,000 tonn last vs. standard 180,000. Dette gir historisk **35-40% premium** på ratene.
2.  **Scrubbere:** Alle skip har scrubbere, som gjør at de kan brenne billigere drivstoff (HSFO) men få betalt som om de brenner dyrt (VLSFO).
3.  **Lav Breakeven:** Takket være effektiv finansiering har selskapet en svært lav kontant-breakeven på ca **$24,000 - $25,000** per dag.

Alt over breakeven utbetales månedlig til aksjonærene. Bruk kalkulatoren under for å se potensialet.
""")

st.divider()

# --- KALKULATOREN ---
st.header("🧮 Utbyttekalkulator")
st.caption("Juster forutsetningene i menyen til venstre (eller under på mobil).")

# --- INPUTS (Sidebar) ---
with st.sidebar:
    st.header("Markedsforutsetninger")
    
    # Capesize Index
    bdi_5tc = st.slider("Baltic Capesize Index (5TC)", 10000, 100000, 25000, step=1000)
    
    # Premium
    st.subheader("HSHP Fordeler")
    premium_pct = st.slider("Newcastlemax Premium (%)", 110, 160, 138, step=1) / 100
    fuel_spread = st.slider("Fuel Spread (Scrubber) $/ton", 0, 500, 100, step=10)
    
    # Breakeven
    st.subheader("Selskapsdata")
    breakeven = st.number_input("Cash Breakeven ($/dag)", value=24700, step=100)
    shares = 46650000 # Antall aksjer

# --- BEREGNINGER ---
# 1. Inntekter
freight_rate = bdi_5tc * premium_pct
scrubber_bonus = fuel_spread * 45 
total_tce = freight_rate + scrubber_bonus

# 2. Profitt
daily_margin = total_tce - breakeven
monthly_cash_flow = daily_margin * 12 * 30.42 # 12 skip, 30.42 dager/mnd
monthly_dps = max(0, monthly_cash_flow / shares)
annual_yield_usd = monthly_dps * 12

# --- VISUALISERING AV TALLENE ---
c1, c2, c3 = st.columns(3)
c1.metric("Oppnådd Rate (TCE)", f"${total_tce:,.0f}", f"Index: ${bdi_5tc:,}")
c2.metric("Margin per skip", f"${daily_margin:,.0f}", f"Breakeven: ${breakeven:,}")
c3.metric("Månedlig Utbytte", f"${monthly_dps:.3f}", f"Årlig takt: ${annual_yield_usd:.2f}")

# --- DEN VISUELLE FORMELEN ---
st.markdown("#### Slik regnes det ut:")
formula = rf'''
\text{{Utbytte}} = \frac{{({total_tce:,.0f} - {breakeven:,.0f}) \times 12 \text{{ skip}} \times 30.4 \text{{ dager}}}}{{46.65 \text{{ mill aksjer}}}} = \mathbf{{\$ {monthly_dps:.3f}}}
'''
st.latex(formula)

st.divider()

# --- SENSITIVITETSANALYSE (Matrise) ---
st.subheader("📊 Sensitivitetsanalyse: Hva hvis ratene endres?")
st.write("Tabellen viser **årlig direkteavkastning (Dividend Yield)** gitt en aksjekurs.")

share_price_nok = st.number_input("Din antatte aksjekurs (NOK)", value=85.0)
usd_nok = st.number_input("USD/NOK Kurs", value=11.0)

# Lage en matrise
rates = [20000, 30000, 40000, 50000, 60000] # BDI Indeks nivåer
premiums = [1.30, 1.38, 1.45] # Ulike premium scenarioer

data = []
for p in premiums:
    row = {}
    row['Premium'] = f"{int((p-1)*100)}%"
    for r in rates:
        # Regn ut utbytte for denne kombinasjonen
        tce = (r * p) + scrubber_bonus
        margin = tce - breakeven
        ann_div_usd = (margin * 12 * 365) / shares
        ann_div_nok = ann_div_usd * usd_nok
        
        # Regn ut yield %
        yield_pct = (ann_div_nok / share_price_nok) * 100 if share_price_nok > 0 else 0
        
        # Formater som tekst med %
        row[f"Index ${r/1000:.0f}k"] = f"{yield_pct:.1f}%"
    data.append(row)

df = pd.DataFrame(data).set_index('Premium')
st.dataframe(df, use_container_width=True)

st.caption(f"Tabellen inkluderer scrubber-bonus på ${scrubber_bonus}/dag og breakeven på ${breakeven}/dag.")
