import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Shipping Alpha", page_icon="⚓", layout="wide")

# --- 1. SIDEBAR LOGIN (Skjult for offentligheten) ---
with st.sidebar:
    st.header("🔐 Portefølje Login")
    # Vi sjekker passordet her, men bruker ikke st.stop()
    password_input = st.text_input("Adgangskode", type="password")
    
    is_authenticated = False
    secret_pass = st.secrets.get("general", {}).get("site_password")
    
    if secret_pass and password_input == secret_pass:
        is_authenticated = True
        st.success("Logget inn: Eier")
    elif password_input:
        st.error("Feil kode")
    
    st.divider()
    
    # Valutainnstillinger er nyttig for både deg og investorer
    st.header("💱 Valuta")
    usd_nok = st.number_input("USD/NOK Kurs", value=11.0, step=0.1, format="%.2f")

# =========================================================
# 📢 DEL 1: OFFENTLIG FORSIDE (Synlig for alle på Nordnet)
# =========================================================

st.title("⚓ Shipping Alpha: Analyseverktøy")
st.markdown("""
Velkommen! Denne siden samler interaktive simulatorer for utvalgte shipping-aksjer på Oslo Børs.
Modellene lar deg teste egne forutsetninger (rater, drivstoff-spread, kontraktsdekning) for å estimere fremtidige utbytter.

**Velg et selskap under for å kjøre din egen analyse:**
""")

# --- Navigasjons-kort (Grid Layout) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⛰ Himalaya Shipping")
    st.caption("Newcastlemax tørrlast med scrubbere.")
    if st.button("Gå til HSHP Kalkulator ➝"):
        st.switch_page("pages/3_⛰_Himalaya_Bulk.py") # Sjekk at filnavnet stemmer
    if st.button("Les Investorguiden 📘"):
        st.switch_page("pages/8_📘_HSHP_Investorguide.py")

with col2:
    st.subheader("🛢 Bruton (VLCC)")
    st.caption("Pure-play tank med nybygg-leveringer.")
    if st.button("Gå til Bruton Simulator ➝"):
        st.switch_page("pages/1_🛢_Bruton_VLCC.py")

with col3:
    st.subheader("📦 MPCC")
    st.caption("Container feeder med kontrakts-waterfall.")
    if st.button("Gå til MPCC Simulator ➝"):
        st.switch_page("pages/2_📦_MPCC_Feeder.py")

st.markdown("---")
st.caption("Tips: Du finner også flere simulatorer (BW LPG, Odfjell, HAUTO) i menyen til venstre.")


# =========================================================
# 🔐 DEL 2: PRIVAT PORTEFØLJE (Kun synlig hvis logget inn)
# =========================================================

if is_authenticated:
    st.divider()
    st.subheader(f"💼 Min Portefølje (Privat Visning)")
    st.info("Denne seksjonen er kun synlig fordi du har skrevet inn riktig passord.")

    # --- SETUP PORTEFØLJE DEFAULTS ---
    companies = ["Himalaya", "MPCC", "HAUTO", "Bruton", "BW LPG", "Odfjell"]

    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = {ticker: {"shares": 0, "gav": 0.0} for ticker in companies}
        
        # OWNER AUTO-LOAD
        if "my_portfolio" in st.secrets:
            for ticker in companies:
                if ticker in st.secrets["my_portfolio"]:
                    data = st.secrets["my_portfolio"][ticker]
                    st.session_state['portfolio'][ticker] = {"shares": data['shares'], "gav": data['gav']}
                    # Pre-fill widgets
                    st.session_state[f"{ticker}_s"] = data['shares']
                    st.session_state[f"{ticker}_g"] = data['gav']

    if 'projections' not in st.session_state:
        st.session_state['projections'] = {ticker: 0.0 for ticker in companies}

    # --- MANUELLE JUSTERINGER (I en expander for å spare plass) ---
    with st.expander("Rediger Beholdning (Admin)", expanded=False):
        c1, c2 = st.columns(2)
        selected_ticker = c1.selectbox("Velg Selskap", companies)
        
        # Hent nåværende verdier
        curr_s = st.session_state.get(f"{selected_ticker}_s", 0)
        curr_g = st.session_state.get(f"{selected_ticker}_g", 0.0)
        
        new_s = c2.number_input("Antall Aksjer", value=curr_s, key=f"{selected_ticker}_s")
        new_g = c2.number_input("GAV (NOK)", value=curr_g, key=f"{selected_ticker}_g")
        
        # Lagre endringer
        st.session_state['portfolio'][selected_ticker] = {"shares": new_s, "gav": new_g}

    # --- DASHBOARD DISPLAY ---
    total_income_nok = 0
    total_invested_nok = 0
    data = []

    for ticker in companies:
        p = st.session_state['portfolio'][ticker]
        shares = p['shares']
        gav_nok = p['gav']
        div_usd = st.session_state['projections'].get(ticker, 0.0)
        
        # Konvertering
        div_nok = div_usd * usd_nok
        income_nok = shares * div_nok
        invested_nok = shares * gav_nok
        
        total_income_nok += income_nok
        total_invested_nok += invested_nok
        
        if shares > 0:
            yoc = (div_nok * 4 / gav_nok) * 100 if gav_nok > 0 else 0
            data.append({
                "Ticker": ticker, 
                "Aksjer": f"{shares:,}", 
                "Utbytte (NOK)": f"{div_nok:.2f} kr", 
                "Min Inntekt": f"{income_nok:,.0f} kr",
                "Yield on Cost": f"{yoc:.1f}%"
            })

    df = pd.DataFrame(data)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Investert", f"{total_invested_nok:,.0f} kr")
        c2.metric("Kvartalsvis Sjekk", f"{total_income_nok:,.0f} kr", f"USD: {usd_nok}")
        if total_invested_nok > 0:
            c3.metric("Portefølje Yield", f"{(total_income_nok * 4 / total_invested_nok) * 100:.1f}%")
