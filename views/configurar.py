import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *

st.set_page_config(page_title="Pró-Corpo - Configurações", page_icon="💎",layout="wide")

st.title("Configurações")
seletor_pagina = st.pills(["Configurar prestadoras", "Configurar comissões"],selection_mode="single",default="Configurar porestadoras")


if seletor_pagina == "Configurar prestadoras":
  st.subheader("Configurar prestadoras")

  if "dados_prestadoras" in st.session_state:
    prestadora_df = st.session_state["dados_prestadoras"]
  else:
    prestadora_df = get_dataframe_from_mongodb(collection_name="dados_vendedoras", database_name="rpd_db")
    st.session_state["dados_prestadoras"] = prestadora_df

  st.data_editor(prestadora_df)

if seletor_pagina == "Configurar comissões":
  st.subheader("Configurar comissões")
