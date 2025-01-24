import streamlit as st

# --- PAGE SETUP ---
configurar_page = st.Page(
    "views/configurar.py",
    title="Configurações",
    icon=":material/settings:"
)

extrato_page = st.Page(
    "views/extrato.py",
    title="Extrato",
    icon=":material/payments:",
    default=True
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Extratos": [extrato_page],
        "Configurar": [configurar_page],
        
    }
)


# --- SHARED ON ALL PAGES ---
st.logo("assets/logoprocorpo.jpg")


# --- RUN NAVIGATION ---
pg.run()
