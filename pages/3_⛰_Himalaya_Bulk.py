import streamlit as st

st.set_page_config(page_title="Himalaya Simulator", page_icon="⛰")
st.title("⛰ Himalaya Shipping: Hedge & Spot")

# --- 1. KONFIGURASJON ---
SHARES_OUTSTANDING = 46650000 
FLEET_COUNT = 12

# --- 2. TIDSALINJE (Dynamisk Breakeven) ---
st.sidebar.header("Tidsperiode")
quarters = {
    "Q1 2026": 0, "Q2 2026": 1, "Q3 2026": 2, "Q4 2026": 3,
    "Q1 2027": 4, "Q2 2027": 5, "Q3 2027": 6, "Q4 2027": 7
}
target_qtr = st.sidebar.selectbox("Velg Kvartal", list(quarters.keys()))

# Beregn CBE (Cash Breakeven)
base_cbe = 24900
reduction_per_qtr = 267
steps = quarters[target_qtr]
dynamic_cbe = base_cbe - (steps * reduction_per_qtr)

# --- 3. FLÅTE-MIKS (NYHET: Fastpris vs Spot) ---
st.sidebar.header("Flåte Kontrakter")

# Slider for antall skip på fast kontrakt
fixed_ships = st.sidebar.slider("Antall skip på Fastpris", 0, 12, 0)
spot_ships = FLEET_COUNT - fixed_ships

# Hvis vi har skip på fastpris, vis felt for å skrive inn prisen
fixed_rate = 0
if fixed_ships > 0:
    fixed_rate = st.sidebar.number_input(
        f"Gjennomsnittlig Fastpris for {fixed_ships} skip ($/dag)", 
        value=30000, 
        step=500,
        help="Total rate (TCE) for skipene som ikke går i spot-markedet."
    )

st.sidebar.markdown("---")

# --- 4. SPOT MARKEDET ---
# Initialiser session state for å huske tallene
if 'hshp_bdi' not in st.session_state: st.session_state['hshp_bdi'] = 25000
if 'hshp_prem' not in st.session_state: st.session_state['hshp_prem'] = 138
if 'hshp_spread' not in st.session_state: st.session_state['hshp_spread'] = 120

st.sidebar.header("Spot Marked Drivere")
bdi_5tc = st.sidebar.slider("Baltic Capesize Index (5TC)", 10000, 80000, key='hshp_bdi', step=500)
premium_pct = st.sidebar.slider("Newcastlemax Premium (%)", 110, 160, key='hshp_prem', step=1) / 100
fuel_spread = st.sidebar.slider("Fuel Spread (Hi5) $/ton", 0, 500, key='hshp_spread', step=10)

# --- 5. BEREGNINGSMOTOR ---

# A. Beregn Spot Rate
scrubber_bonus = fuel_spread * 45 
spot_tce = (bdi_5tc * premium_pct) + scrubber_bonus

# B. Beregn Vektet Snitt Rate for hele flåten
# (Spot Rate * Spot Skip) + (Fastpris * Fastpris Skip) / Totalt antall
total_revenue_daily = (spot_tce * spot_ships) + (fixed_rate * fixed_ships)
weighted_avg_tce = total_revenue_daily / FLEET_COUNT

# C. Beregn Utbytte
daily_margin = weighted_avg_tce - dynamic_cbe
monthly_cash_flow = daily_margin * FLEET_COUNT * 30.42 # 365/12
monthly_dps = max(0, monthly_cash_flow / SHARES_OUTSTANDING)

# --- 6. VISUALISERING AV FORMELEN (NYHET) ---
st.markdown("### 🧮 Matematikken bak tallet")

# Vi lager en visuell ligning med LaTeX
formula_latex = r'''
\text{Utbytte} = \frac{(\text{Snitt Rate} - \text{CBE}) \times \text{Skip} \times \text{Dager}}{\text{Aksjer}}
'''
st.latex(formula_latex)

st.caption("Med dine tall blir dette:")

# Dynamisk visning av tallene
calculation_latex = rf'''
\text{{{monthly_dps:.3f}}} = \frac{{({weighted_avg_tce:,.0f} - {dynamic_cbe:,.0f}) \times {FLEET_COUNT} \times 30.4}}{{46.65 \text{{ mill}}}}
'''
st.latex(calculation_latex)

st.divider()

# --- 7. RAPPORT TIL DASHBOARD ---
if 'projections' not in st.session_state: st.session_state['projections'] = {}
st.session_state['projections']['Himalaya'] = monthly_dps * 3

# --- 8. RESULTAT DISPLAY ---
col1, col2 = st.columns(2)

# Viser Vektet Rate (Blend av spot og fast)
col1.metric(
    "Snitt Rate (Spot + Fast)", 
    f"${weighted_avg_tce:,.0f}", 
    f"Spot: ${spot_tce:,.0f} | Fast: ${fixed_rate:,.0f}" if fixed_ships > 0 else None
)

col2.metric(
    "Est. Månedlig Utbytte", 
    f"${monthly_dps:.3f}", 
    f"Breakeven: ${dynamic_cbe:,.0f}"
)

# Info boks om miksen
if fixed_ships > 0:
    st.info(f"📊 **Hedge Profil:** Du har sikret **{fixed_ships} skip** på ${fixed_rate:,}/dag. De resterende **{spot_ships} skipene** tjener ${spot_tce:,.0f}/dag i spot-markedet.")
else:
    st.info("📊 **100% Spot Eksponering:** Hele flåten flyter på markedsraten.")
