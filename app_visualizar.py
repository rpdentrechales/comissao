import streamlit as st

# --- PAGE SETUP ---
visualizar_page = st.Page(
    "views/visualizar.py",
    title="Visualizar",
    icon=":material/payments:"
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
        "Visualizar": [visualizar_page],
        # "Testes": [configurar_page]
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
