import streamlit as st

# --- PAGE SETUP ---
configurar_page = st.Page(
    "views/configurar.py",
    title="Configurações",
    icon=":material/settings:"
)

comissoes_page = st.Page(
    "views/comissoes.py",
    title="Comissões Consolidadas",
    icon=":material/payments:",
    default=True
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Comissões": [comissoes_page],
        "Configurar": [configurar_page],
        
    }
)


# --- SHARED ON ALL PAGES ---
st.logo("assets/logo-topo-min.png",size="large")


# --- RUN NAVIGATION ---
pg.run()
