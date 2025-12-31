import streamlit as st
import pandas as pd

# 1. KONFIGURASJON
st.set_page_config(page_title="Himalaya Shipping: Investorguide og utbyttekalkulator", page_icon="⛰", layout="wide")

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
    with st.expander("1. Flåte & Strategi", expanded=True): # Default expanded for å vise 6/6 split
        total_fleet = st.number_input("Antall Skip", value=12, step=1)
        
        # PROGNOSE-TALL: 6 Skip på fastpris
        fixed_ships = st.slider("Skip på Fastpris", 0, total_fleet, 6) 
        spot_ships = total_fleet - fixed_ships
        
        fixed_rate = 0
        if fixed_ships > 0:
            # PROGNOSE-TALL: $38,300
            fixed_rate = st.number_input("Fastpris Rate ($/dag)", value=38300, step=100)
    
    st.markdown("---")

  # --- SEKSJON B: SCRUBBER & DRIVSTOFF (RENERE MODELL) ---
    st.subheader("2. Scrubber & LNG")
    
    scrubber_mode = st.radio(
        "Beregningsmetode:",
        ["Enkel (Netto Beløp)", "Avansert (Markedspriser)"],
        horizontal=True
    )

    scrubber_bonus_net = 0.0
    scrubber_share_pct = 1.0 
    scrubber_bonus_gross = 0.0 

    if scrubber_mode == "Enkel (Netto Beløp)":
        # Dette er tallet fra kvartalsrapporten/PDF-en
        scrubber_bonus_net = st.number_input(
            "Netto Premium til HSHP ($/dag)", 
            value=2300, 
            step=100,
            help="Beløpet HSHP sitter igjen med etter deling med charterer."
        )
        scrubber_share_pct = 1.0 
    
    else: # Avansert modus
        # 1. Eierandel
        scrubber_share_pct = st.number_input(
            "HSHP Eierandel av Benefit (%)", 
            min_value=0.0, max_value=100.0, value=75.0, step=5.0,
            help="Standard er ofte 75% til reder, 25% til charterer."
        ) / 100

        # 2. Velg Marked
        st.write("🌍 **Velg Bunkrings-marked:**")
        hub_choice = st.radio("Hub", ["Rotterdam", "Singapore"], label_visibility="collapsed", horizontal=True)

        if hub_choice == "Rotterdam":
            url_oil = "https://shipandbunker.com/prices/emea/nwe/nl-rtm-rotterdam"
            url_lng = "https://shipandbunker.com/prices/emea/nwe/nl-rtm-rotterdam#LNG"
            def_vlsfo, def_ifo, def_lng = 530, 430, 550
        else: 
            url_oil = "https://shipandbunker.com/prices/apac/sea/sg-sin-singapore"
            url_lng = "https://shipandbunker.com/prices/apac/sea/sg-sin-singapore#LNG"
            def_vlsfo, def_ifo, def_lng = 580, 460, 560

        c1, c2 = st.columns(2)
        c1.link_button("Oljepriser", url_oil)
        c2.link_button("LNG Priser", url_lng)

        st.caption("Markedspriser ($/mt):")
        col_f1, col_f2 = st.columns(2)
        p_vlsfo = col_f1.number_input("VLSFO", value=def_vlsfo, step=10, help="Dyr standardolje")
        p_ifo = col_f2.number_input("IFO380", value=def_ifo, step=10, help="Billig olje (Scrubber)")
        p_lng = st.number_input("LNG", value=def_lng, step=10, help="Naturgass")
        
        consumption = st.slider("Forbruk (tonn/dag)", 35, 55, 45)
        
        # LOGIKK:
        # Finn billigste drivstoff (HFO vs LNG)
        cheapest_price = min(p_ifo, p_lng)
        fuel_source = "LNG" if p_lng < p_ifo else "HFO (IFO380)"
        
        # Beregn spread mot VLSFO
        fuel_spread = p_vlsfo - cheapest_price
        
        # Brutto besparelse
        scrubber_bonus_gross = max(0, fuel_spread * consumption)
        
        # Netto til HSHP
        scrubber_bonus_net = scrubber_bonus_gross * scrubber_share_pct
        
        if scrubber_bonus_gross > 0:
            st.success(f"""
            ✅ **Billigste drivstoff:** {fuel_source}
            \n💰 **Netto til HSHP:** ${scrubber_bonus_net:,.0f}/dag
            """)
        else:
            st.warning("Ingen besparelse med dagens priser.")
    # --- SEKSJON C: MARKED (SPOT) ---
    st.subheader("3. Spot Marked")
    # PROGNOSE-TUNING: BDI 35,000 gir spot rate (uten scrubber) på $48,300
    bdi_5tc = st.slider("Baltic Capesize Index (5TC)", 10000, 100000, 35000, step=1000)
    premium_pct = st.number_input("HSHP Premium %", value=138, step=1) / 100
    
    st.markdown("---")
    
    # --- SEKSJON D: KOSTNADER ---
    st.subheader("4. Selskap")
    # PROGNOSE-TALL: $24,900
    breakeven = st.number_input("Cash Breakeven ($/dag)", value=24900, step=100)
    shares = 46650000 

# 4. HOVEDINNHOLD
st.title("⛰ Himalaya Shipping: Investorguide")

pdf_url = "https://mortenst.github.io/HSHP/Himalaya_Shipping___investor_guide__29-12-25_.pdf"
c_link1, c_link2 = st.columns([1, 3])
c_link1.link_button("📄 Last ned PDF-Guide", pdf_url)
c_link2.markdown("*Standardverdiene er satt i henhold til Desember-estimatet i rapporten.*")

st.divider()

# 5. BEREGNINGSMOTOR

term_fixed = fixed_ships * fixed_rate
spot_freight_rate = bdi_5tc * premium_pct
term_spot = spot_ships * spot_freight_rate
term_scrubber = total_fleet * scrubber_bonus_net 

daily_revenue_total = term_fixed + term_spot + term_scrubber
daily_cost_total = total_fleet * breakeven
daily_profit = daily_revenue_total - daily_cost_total

# Merk: Vi bruker standard 30.42 dager for å være konsistente over tid, 
# selv om desember spesifikt har 31 dager.
monthly_cash_flow = daily_profit * 30.42 
monthly_dps = max(0, monthly_cash_flow / shares)
annual_yield_usd = monthly_dps * 12

# 6. DASHBOARD
st.subheader("📊 Resultater")
c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Daglig Inntekt", 
    f"${daily_revenue_total:,.0f}", 
    f"Snitt: ${(daily_revenue_total/total_fleet):,.0f}/skip"
)

c2.metric(
    "Daglig Overskudd", 
    f"${daily_profit:,.0f}", 
    f"Kostnader: -${daily_cost_total:,.0f}"
)

c3.metric(
    "Est. Månedlig Utbytte", 
    f"${monthly_dps:.3f}", 
    f"Årlig takt: ${annual_yield_usd:.2f}"
)

# 7. MATEMATIKKEN (DYNAMISK FORMEL)
st.markdown("#### 🧮 Slik er regnestykket bygget opp:")

if scrubber_mode == "Enkel (Netto Beløp)":
    latex_formula = r'''
    \text{Inntekt} = 
    \underbrace{(N_{fast} \times \$_{fast})}_{\text{Fastpris}} + 
    \underbrace{(N_{spot} \times \text{BDI} \times \%_{prem})}_{\text{Spot Frakt}} + 
    \underbrace{(N_{total} \times \$_{netto})}_{\text{Scrubber}}
    '''
    latex_numbers = rf'''
    \text{{{daily_revenue_total:,.0f}}} = 
    ({fixed_ships} \times {fixed_rate:,.0f}) + 
    ({spot_ships} \times {bdi_5tc:,} \times {premium_pct:.2f}) + 
    ({total_fleet} \times {scrubber_bonus_net:,.0f})
    '''
else:
    latex_formula = r'''
    \text{Inntekt} = 
    \underbrace{(N_{fast} \times \$_{fast})}_{\text{Fastpris}} + 
    \underbrace{(N_{spot} \times \text{BDI} \times \%_{prem})}_{\text{Spot Frakt}} + 
    \underbrace{(N_{total} \times \$_{brutto} \times \%_{eier})}_{\text{Scrubber (Netto)}}
    '''
    latex_numbers = rf'''
    \text{{{daily_revenue_total:,.0f}}} = 
    ({fixed_ships} \times {fixed_rate:,.0f}) + 
    ({spot_ships} \times {bdi_5tc:,} \times {premium_pct:.2f}) + 
    ({total_fleet} \times {scrubber_bonus_gross:,.0f} \times {scrubber_share_pct:.2f})
    '''

st.latex(latex_formula)
st.markdown(f"**Med dine tall:**")
st.latex(latex_numbers)

st.divider()
st.markdown("**Fra Inntekt til Utbytte:**")
div_formula = rf'''
\text{{Utbytte}} = \frac{{({daily_revenue_total:,.0f} - {daily_cost_total:,.0f}) \times 30.42}}{{46.65 \text{{ mill}}}} = \mathbf{{\$ {monthly_dps:.3f}}}
'''
st.latex(div_formula)

st.divider()

# 8. SENSITIVITET (YIELD)
st.subheader("📈 Sensitivitetsanalyse")
st.markdown("Tabellen viser **årlig direkteavkastning (Yield)** gitt dine valg.")

col_input1, col_input2 = st.columns(2)
share_price_nok = col_input1.number_input("Aksjekurs / Din GAV (NOK)", value=82.0)
usd_nok = col_input2.number_input("USD/NOK", value=11.1)

# --- NYTT: BEREGN YIELD ON COST FOR ESTIMATET ---
est_yoc = ((annual_yield_usd * usd_nok) / share_price_nok) * 100 if share_price_nok > 0 else 0
st.info(f"💰 **Din Yield on Cost** med dagens estimat er: **{est_yoc:.1f}%**")
# ------------------------------------------------

rates = [20000, 30000, 40000, 50000, 60000, 80000]
row = {}

for r in rates:
    t_fixed = fixed_ships * fixed_rate
    t_spot = spot_ships * (r * premium_pct)
    t_scrub = total_fleet * scrubber_bonus_net 
    
    d_rev = t_fixed + t_spot + t_scrub
    d_profit = d_rev - (total_fleet * breakeven)
    
    ann_div_usd = (d_profit * 365) / shares
    ann_div_nok = ann_div_usd * usd_nok
    
    yield_pct = (ann_div_nok / share_price_nok) * 100 if share_price_nok > 0 else 0
    
    label = f"Spot-Rate ${r/1000:.0f}k"
    row[label] = "0%" if yield_pct < 0 else f"{yield_pct:.1f}%"
    
st.dataframe(pd.DataFrame([row], index=["Yield"]), width="stretch") # Oppdatert parameter
if scrubber_mode == "Enkel (Netto Beløp)":
    st.caption(f"Tabellen bruker en netto scrubber-gevinst på ${scrubber_bonus_net:,.0f}/dag.")
else:
    st.caption(f"Tabellen bruker en beregnet scrubber-gevinst basert på {scrubber_share_pct*100:.0f}% eierandel.")
