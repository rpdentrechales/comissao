import streamlit as st

# --- PAGE SETUP ---
configurar_page = st.Page(
    "views/configurar.py",
    title="Configurações",
    icon=":material/settings:"
)
# configurar_page = st.Page(
#     "views/configurar_vendedoras.py",
#     title="Configurar Vendedoras",
#     icon=":material/manufacturing:",
#     default=True
# )

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Configurar": [configurar_page],
        # "Testes": [configurar_page]
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
