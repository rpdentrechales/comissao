import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *

st.set_page_config(page_title="Pró-Corpo - Configurações", page_icon="💎",layout="wide")

st.title("Configurações")
seletor_pagina = st.pills("Configurar",["Prestadoras", "Comissões"],selection_mode="single",default="Prestadoras")

if "dados_comissao" in st.session_state:
  comissao_df = st.session_state["dados_comissao"]
else:
  comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
  st.session_state["dados_comissao"] = comissao_df

if "dados_prestadoras" in st.session_state:
  prestadora_df = st.session_state["dados_prestadoras"]
else:
  prestadora_df = get_dataframe_from_mongodb(collection_name="prestadores_db", database_name="relatorio_comissao")
  st.session_state["dados_prestadoras"] = prestadora_df

if seletor_pagina == "Prestadoras":
  st.subheader("Configurar prestadoras")

  column_order_prestadoras = ["nome_prestador","funcao_prestadora"]
  opcoes_funcoes = comissao_df["funcao_prestadora"].unique()
  column_config_prestadoras = {
      "nome_prestador": st.column_config.TextColumn("Nome da Prestadora",width="medium",disabled=True),
      "funcao_prestadora": st.column_config.SelectboxColumn("Função da Prestadora",width="medium",options=opcoes_funcoes)
  }

  edited_prestadora_df = st.data_editor(prestadora_df,
                                        use_container_width=True,
                                        hide_index=True,
                                        column_order=column_order_prestadoras,
                                        column_config=column_config_prestadoras,
                                        num_rows="dynamic")

  if st.button("Salvar alterações"):

    st.session_state["dados_prestadoras"] = edited_prestadora_df
    result = sync_dataframe(collection_name="prestadores_db",database_name="relatorio_comissao", dataframe=edited_prestadora_df, unique_key="nome_prestador")
    st.success("Alterações salvas com sucesso!")

if seletor_pagina == "Comissões":
  st.subheader("Configurar comissões")
  
  if "dados_comissao" in st.session_state:
    comissao_df = st.session_state["dados_comissao"]
  else:
    comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
    st.session_state["dados_comissao"] = comissao_df

  column_order_comissao = ["funcao_prestadora","comissao"]
  column_config_comissao = {
      "funcao_prestadora": st.column_config.TextColumn("Função da Prestadora",width="medium"),
      "comissao": st.column_config.NumberColumn("Comissão",width="medium",format="R$%.2f")
  }

  edited_comissao_df = st.data_editor(comissao_df,
                                      use_container_width=False,
                                      hide_index=True,
                                      column_order=column_order_comissao,
                                      column_config=column_config_comissao,
                                      num_rows="dynamic"
                                      )
  
  if st.button("Salvar alterações"):

    edited_comissao_df = edited_comissao_df.loc[~edited_comissao_df["funcao_prestadora"].isna()]
    st.session_state["dados_comissao"] = edited_comissao_df
    result = sync_dataframe(collection_name="comissoes",database_name="relatorio_comissao", dataframe=edited_comissao_df, unique_key="funcao_prestadora")
    st.success("Alterações salvas com sucesso!")
