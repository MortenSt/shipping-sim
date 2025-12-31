import streamlit as st
import pandas as pd

# 1. KONFIGURASJON
st.set_page_config(page_title="Himalaya Investorguide", page_icon="⛰", layout="wide")

# 2. CSS HACK: SKJUL NAVIGASJON
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR: KONTROLLSENTER
with st.sidebar:
    st.header("⚙️ Konfigurasjon")
    
    # --- SEKSJON A: FLÅTE ---
    with st.expander("1. Flåte & Strategi", expanded=False):
        total_fleet = st.number_input("Antall Skip", value=12, step=1)
        fixed_ships = st.slider("Skip på Fastpris", 0, total_fleet, 0)
        spot_ships = total_fleet - fixed_ships
        
        fixed_rate = 0
        if fixed_ships > 0:
            fixed_rate = st.number_input("Fastpris Rate ($/dag)", value=30000, step=500)
    
    st.markdown("---")

    # --- SEKSJON B: SCRUBBER & DRIVSTOFF (OPPDATERT) ---
    st.subheader("2. Scrubber & LNG")
    
    scrubber_mode = st.radio(
        "Beregningsmetode:",
        ["Enkel (Fast sum)", "Avansert (Markedspriser)"],
        horizontal=True
    )

    scrubber_bonus = 0.0
    fuel_spread = 0.0 

    if scrubber_mode == "Enkel (Fast sum)":
        scrubber_bonus = st.number_input(
            "Scrubber/LNG Premium ($/dag)", 
            value=2500, 
            step=100,
            help="Hvor mye sparer skipet per dag? (Historisk snitt: $2k-$4k)"
        )
    
    else: # Avansert modus
        st.info("💡 **Tips:** Hent dagens priser fra **Rotterdam** (stor hub).")
        
        # Linker til kildene
        c_url1, c_url2 = st.columns(2)
        c_url1.link_button("Oljepriser (Ship&Bunker)", "https://shipandbunker.com/prices/emea/nwe/nl-rtm-rotterdam")
        c_url2.link_button("LNG Priser (Rotterdam)", "https://shipandbunker.com/prices/emea/nwe/nl-rtm-rotterdam#LNG")

        st.caption("Fyll inn prisene under ($/mt):")
        
        col_fuel1, col_fuel2 = st.columns(2)
        
        # Vi bruker navnene som står på nettsiden
        with col_fuel1:
            price_vlsfo = st.number_input("Pris VLSFO", value=530, step=10, help="Dyr standardolje (0.5% S)")
            
        with col_fuel2:
            # Her presiserer vi at HFO er det samme som IFO380
            price_ifo380 = st.number_input("Pris IFO380 (HFO)", value=430, step=10, help="Billig olje for scrubbere (3.5% S)")
            
        price_lng = st.number_input("Pris LNG", value=550, step=10, help="Flytende naturgass (LNG Bunker)")
        
        consumption = st.slider("Forbruk (tonn/dag)", 35, 55, 45, help="Newcastlemax bruker ca 45 tonn.")
        
        # LOGIKK:
        # 1. Finn billigste alternativ (HFO/IFO380 vs LNG)
        cheapest_fuel_price = min(price_ifo380, price_lng)
        chosen_fuel_name = "LNG" if price_lng < price_ifo380 else "HFO (IFO380)"
        
        # 2. Beregn besparelse mot VLSFO
        fuel_spread = price_vlsfo - cheapest_fuel_price
        
        # 3. Beregn dags-bonus
        scrubber_bonus = fuel_spread * consumption
        
        if scrubber_bonus < 0: 
            scrubber_bonus = 0 
            st.warning("⚠️ VLSFO er billigere enn alternativene. Ingen scrubber-bonus.")
        else:
            st.success(f"""
            ✅ **Billigste drivstoff:** {chosen_fuel_name} (${cheapest_fuel_price})
            \n💰 **Spread:** ${fuel_spread}/tonn
            \n🚀 **Daglig Bonus:** ${scrubber_bonus:,.0f}
            """)
    # --- SEKSJON C: MARKED (SPOT) ---
    st.subheader("3. Spot Marked")
    bdi_5tc = st.slider("Baltic Capesize Index (5TC)", 10000, 100000, 25000, step=1000)
    premium_pct = st.number_input("HSHP Premium %", value=138, step=1, help="Newcastlemax fordel") / 100
    
    st.markdown("---")
    
    # --- SEKSJON D: KOSTNADER ---
    st.subheader("4. Selskap")
    breakeven = st.number_input("Cash Breakeven ($/dag)", value=24700, step=100)
    shares = 46650000 

# 4. HOVEDINNHOLD
st.title("⛰ Himalaya Shipping: Investorguide")

pdf_url = "https://mortenst.github.io/HSHP/Himalaya_Shipping___investor_guide__29-12-25_.pdf"
c_link1, c_link2 = st.columns([1, 3])
c_link1.link_button("📄 Last ned PDF-Guide", pdf_url)
c_link2.markdown("*Bruk menyen til venstre for å velge mellom enkel eller avansert drivstoff-modellering.*")

st.divider()

# 5. BEREGNINGSMOTOR

# A. Spot Inntekter (Rate + Scrubber Bonus fra logikken over)
spot_freight = bdi_5tc * premium_pct
spot_tce = spot_freight + scrubber_bonus

# B. Vektet Snitt
daily_revenue_total = (spot_tce * spot_ships) + (fixed_rate * fixed_ships)
weighted_avg_tce = daily_revenue_total / total_fleet

# C. Kontantstrøm
daily_margin = weighted_avg_tce - breakeven
monthly_cash_flow = daily_margin * total_fleet * 30.42 
monthly_dps = max(0, monthly_cash_flow / shares)
annual_yield_usd = monthly_dps * 12

# 6. DASHBOARD
st.subheader("📊 Resultater")
c1, c2, c3 = st.columns(3)

rate_label = "Oppnådd Rate (TCE)" if fixed_ships == 0 else "Snittrate (TCE)"

c1.metric(
    rate_label, 
    f"${weighted_avg_tce:,.0f}", 
    f"Inkl. Scrubber: ${scrubber_bonus:,.0f}/dag"
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

# 7. MATEMATIKKEN
st.markdown("#### 🧮 Slik regnes det ut:")
st.caption("Tallene oppdateres automatisk.")

calculation_latex = rf'''
\text{{{monthly_dps:.3f}}} = \frac{{(\text{{Rate }} {weighted_avg_tce:,.0f} - \text{{Kost }} {breakeven:,.0f}) \times {total_fleet} \text{{ skip}} \times 30.4}}{{46.65 \text{{ mill aksjer}}}}
'''
st.latex(calculation_latex)

st.divider()

# 8. SENSITIVITET (YIELD)
st.subheader("📈 Sensitivitetsanalyse")
st.markdown("Tabellen viser **årlig direkteavkastning (Yield)** gitt dine valg for Scrubber og Fastpris.")

col_input1, col_input2 = st.columns(2)
share_price_nok = col_input1.number_input("Aksjekurs (NOK)", value=82.0)
usd_nok = col_input2.number_input("USD/NOK", value=11.1)

rates = [20000, 30000, 40000, 50000, 60000, 80000] 
data = []
row = {}

for r in rates:
    # 1. Spot Rate + Din valgte scrubber bonus (fast eller beregnet)
    this_spot_tce = (r * premium_pct) + scrubber_bonus
    
    # 2. Vektet Rate (hvis du har valgt skip på fastpris)
    this_total_rev = (this_spot_tce * spot_ships) + (fixed_rate * fixed_ships)
    this_avg_tce = this_total_rev / total_fleet
    
    # 3. Utbytte
    margin = this_avg_tce - breakeven
    ann_div_usd = (margin * total_fleet * 365) / shares
    ann_div_nok = ann_div_usd * usd_nok
    
    # 4. Yield
    yield_pct = (ann_div_nok / share_price_nok) * 100 if share_price_nok > 0 else 0
    
    label = f"Spot-Rate ${r/1000:.0f}k"
    if yield_pct < 0:
        row[label] = "0%"
    else:
        row[label] = f"{yield_pct:.1f}%"

st.dataframe(pd.DataFrame([row], index=["Yield"]), use_container_width=True)

if scrubber_mode == "Avansert (Drivstoffpriser)":
    st.info(f"💡 **Info:** Tabellen baserer seg på en beregnet scrubber-fordel på **${scrubber_bonus:,.0f}/dag** (Spread: ${fuel_spread}).")
else:
    st.info(f"💡 **Info:** Tabellen baserer seg på din faste scrubber-premium på **${scrubber_bonus:,.0f}/dag**.")
