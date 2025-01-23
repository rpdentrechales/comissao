import streamlit as st

# --- PAGE SETUP ---
visualizar_page = st.Page(
    "views/visualizar.py",
    title="Visualizar Comissões",
    icon=":material/payments:"
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Visualizar": [visualizar_page],
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
