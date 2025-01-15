import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *

st.set_page_config(page_title="Pró-Corpo - Configurações", page_icon="💎",layout="wide")

st.title("Configurações")
seletor_pagina = st.pills("Configurar",["Prestadoras", "Comissões"],selection_mode="single",default="Prestadoras")


if seletor_pagina == "Prestadoras":
  st.subheader("Configurar prestadoras")

  if "dados_prestadoras" in st.session_state:
    prestadora_df = st.session_state["dados_prestadoras"]
  else:
    prestadora_df = get_dataframe_from_mongodb(collection_name="prestadores_db", database_name="relatorio_comissao")
    st.session_state["dados_prestadoras"] = prestadora_df

  column_order = ["nome_prestador","funcao_prestadora"]
  column_config = {
      "nome_prestador": st.column_config.TextColumn("Nome da Prestadora",width="medium",disabled=True),
      "funcao_prestadora": st.column_config.TextColumn("Função da Prestadora",width="medium")
  }

  edited_df = st.data_editor(prestadora_df,use_container_width=True,hide_index=True, column_order=column_order,column_config=column_config)

if seletor_pagina == "Comissões":
  st.subheader("Configurar comissões")
  
  if "dados_comissao" in st.session_state:
    comissao_df = st.session_state["dados_comissao"]
  else:
    comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
    st.session_state["dados_comissao"] = comissao_df

  st.data_editor(comissao_df)  
