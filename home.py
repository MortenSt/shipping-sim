import streamlit as st
import pandas as pd

# 1. KONFIGURASJON
st.set_page_config(page_title="Himalaya Investorguide", page_icon="⛰", layout="wide")

# 2. CSS HACK: SKJUL NAVIGASJON (Gjør siden til en "App")
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR: KONTROLLSENTER
with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    st.info("Juster forutsetningene for å matche scenariene i rapporten.")
    
    # --- SEKSJON A: FLÅTE & STRATEGI (Viktig for fremtidige konfigurasjoner) ---
    st.subheader("1. Flåte & Strategi")
    
    # Her kan du endre flåtestørrelse i fremtiden hvis de kjøper flere skip
    total_fleet = st.number_input("Antall Skip i Flåten", value=12, step=1)
    
    # Hedging-slider: Hvor mange skip går på fast kontrakt?
    fixed_ships = st.slider("Antall skip på Fastpris", 0, total_fleet, 0, 
                            help="Bruk denne for å simulere hedging-scenarier fra PDF-en.")
    
    spot_ships = total_fleet - fixed_ships
    
    # Vises kun hvis man har valgt skip på fastpris
    fixed_rate = 0
    if fixed_ships > 0:
        fixed_rate = st.number_input("Rate på Fastpris-skip ($/dag)", value=30000, step=500)
        st.caption(f"De resterende {spot_ships} skipene går i spot-markedet.")
    
    st.markdown("---")

    # --- SEKSJON B: MARKED (SPOT) ---
    st.subheader("2. Spot Markedet")
    bdi_5tc = st.slider("Baltic Capesize Index (5TC)", 10000, 100000, 25000, step=1000)
    
    # Premium & Scrubber
    col_p1, col_p2 = st.columns(2)
    premium_pct = col_p1.number_input("Premium %", value=138, step=1, help="Newcastlemax fordel") / 100
    fuel_spread = col_p2.number_input("Hi5 Spread", value=100, step=10, help="Scrubber fordel ($/tonn)")
    
    st.markdown("---")
    
    # --- SEKSJON C: SELSKAPSDATA (Kostnader) ---
    st.subheader("3. Kostnader & Aksjer")
    # Denne er viktig å kunne justere etter hvert som gjelden nedbetales
    breakeven = st.number_input("Cash Breakeven ($/dag)", value=24700, step=100, 
                                help="Inkluderer Opex, G&A og Renter/Avdrag.")
    shares = 46650000 

# 4. HOVEDINNHOLD
st.title("⛰ Himalaya Shipping: Investorguide & Kalkulator")

# Link til PDF
pdf_url = "https://mortenst.github.io/HSHP/Himalaya_Shipping___investor_guide__29-12-25_.pdf"
c_link1, c_link2 = st.columns([1, 3])
c_link1.link_button("📄 Last ned PDF-Guide", pdf_url)
c_link2.markdown("*Bruk denne kalkulatoren til å regne på utbytte-scenariene beskrevet i rapporten.*")

st.divider()

# 5. BEREGNINGSMOTOR (Hjertet av appen)

# A. Spot Inntekter
spot_freight = bdi_5tc * premium_pct
scrubber_bonus = fuel_spread * 45 
spot_tce = spot_freight + scrubber_bonus

# B. Vektet Snitt (Blended Rate)
# Formel: ((Spot Rate * Spot Skip) + (Fastpris * Fastpris Skip)) / Totalt antall
daily_revenue_total = (spot_tce * spot_ships) + (fixed_rate * fixed_ships)
weighted_avg_tce = daily_revenue_total / total_fleet

# C. Kontantstrøm & Utbytte
daily_margin = weighted_avg_tce - breakeven
monthly_cash_flow = daily_margin * total_fleet * 30.42 
monthly_dps = max(0, monthly_cash_flow / shares)
annual_yield_usd = monthly_dps * 12

# 6. DASHBOARD (Visualisering)
st.subheader("📊 Resultater")
c1, c2, c3 = st.columns(3)

# Viser om vi kjører rent spot eller mix
rate_label = "Oppnådd Spot Rate" if fixed_ships == 0 else "Vektet Snittrate (TCE)"

c1.metric(
    rate_label, 
    f"${weighted_avg_tce:,.0f}", 
    f"Spot-skip tjener: ${spot_tce:,.0f}" if fixed_ships > 0 else f"Index: ${bdi_5tc:,}"
)

c2.metric(
    "Margin per skip", 
    f"${daily_margin:,.0f}", 
    f"Breakeven: ${breakeven:,}"
)

c3.metric(
    "Est. Månedlig Utbytte", 
    f"${monthly_dps:.3f}", 
    f"Årlig takt: ${annual_yield_usd:.2f}"
)

# 7. MATEMATIKKEN (Dynamisk Formel)
st.markdown("#### 🧮 Slik regnes det ut:")
st.caption("Tallene oppdateres automatisk når du endrer verdiene i menyen.")

# Viser utregningen visuelt med LaTeX
calculation_latex = rf'''
\text{{{monthly_dps:.3f}}} = \frac{{(\text{{Rate }} {weighted_avg_tce:,.0f} - \text{{Kost }} {breakeven:,.0f}) \times {total_fleet} \text{{ skip}} \times 30.4}}{{46.65 \text{{ mill aksjer}}}}
'''
st.latex(calculation_latex)

st.divider()

# 8. SENSITIVITETSANALYSE (Tilpasset Mix)
st.subheader("📈 Sensitivitet: Utbytte ved ulike Spot-rater")
st.markdown("Tabellen viser **årlig direkteavkastning (Yield)** basert på dagens aksjekurs og din valgte fordeling av fastpris/spot.")

# Input for aksjekurs
col_input1, col_input2 = st.columns(2)
share_price_nok = col_input1.number_input("Din antatte aksjekurs (NOK)", value=82.0)
usd_nok = col_input2.number_input("USD/NOK Kurs", value=11.1)

# Vi genererer en tabell som tar hensyn til at noen skip kanskje er låst på fastpris
rates = [20000, 30000, 40000, 50000, 60000, 80000] 
scenarios = ["Bear (Lav)", "Base (Dine tall)", "Bull (Høy)"]

# For enkelhets skyld i tabellen varierer vi kun Spot-raten, men beholder fastpris-andelen konstant
data = []
row = {}

# Vi lager en rad
for r in rates:
    # 1. Regn ut Spot TCE for dette nivået
    this_spot_tce = (r * premium_pct) + scrubber_bonus
    
    # 2. Regn ut Vektet TCE (Beholder fastpris-skipene dine låst)
    this_total_rev = (this_spot_tce * spot_ships) + (fixed_rate * fixed_ships)
    this_avg_tce = this_total_rev / total_fleet
    
    # 3. Regn ut utbytte
    margin = this_avg_tce - breakeven
    ann_div_usd = (margin * total_fleet * 365) / shares
    ann_div_nok = ann_div_usd * usd_nok
    
    # 4. Yield
    yield_pct = (ann_div_nok / share_price_nok) * 100 if share_price_nok > 0 else 0
    
    if yield_pct < 0:
        row[f"Index ${r/1000:.0f}k"] = "0%"
    else:
        row[f"Index ${r/1000:.0f}k"] = f"{yield_pct:.1f}%"

# Vis tabellen som en enkel rad (renere for investorer)
st.dataframe(pd.DataFrame([row], index=["Din Portefølje-Yield"]), use_container_width=True)

if fixed_ships > 0:
    st.info(f"💡 **Merk:** Tabellen over tar hensyn til at **{fixed_ships} skip** er sikret på ${fixed_rate:,}/dag, og derfor ikke påvirkes av svingningene i spot-markedet. Dette stabiliserer utbyttet.")
else:
    st.caption("Tabellen viser yield med 100% spot-eksponering.")
