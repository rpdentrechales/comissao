import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
import numpy as np

st.set_page_config(page_title="Pró-Corpo - Configurações", page_icon="💎",layout="wide")

st.title("Configurações")
seletor_pagina = st.pills("Configurar",["Prestadoras", "Comissões","Tipo de prestadoras"],selection_mode="single",default="Prestadoras")

if "dados_comissao" in st.session_state:
  comissao_df = st.session_state["dados_comissao"]
else:
  comissao_df = load_from_sheets("comissoes")
  st.session_state["dados_comissao"] = comissao_df

if "dados_prestadoras" in st.session_state:
  prestadora_df = st.session_state["dados_prestadoras"]
else:
  prestadora_df = load_from_sheets("base_prestadoras")
  st.session_state["dados_prestadoras"] = prestadora_df

if "dados_procedimentos" in st.session_state:
  procedimentos_df = st.session_state["dados_procedimentos"]
else:
  procedimentos_df = load_from_sheets("procedimentos_padronizados")
  st.session_state["dados_procedimentos"] = procedimentos_df

if "tipo_prestadora" in st.session_state:
  tipo_prestadora_df = st.session_state["tipo_prestadora"]
else:
  tipo_prestadora_df = load_from_sheets("tipo_prestadora")
  st.session_state["tipo_prestadora"] = tipo_prestadora_df
            
if seletor_pagina == "Prestadoras":
  st.subheader("Configurar prestadoras")

  column_order_prestadoras = ["nome_prestadora","tipo_prestadora","status","id_prestadora"]
  opcoes_tipo_prestador = tipo_prestadora_df["tipo_prestadora"].unique()
  
  column_config_prestadoras = {
      "nome_prestadora": st.column_config.TextColumn("Nome da Prestadora",width="medium",disabled=True),
      "tipo_prestadora": st.column_config.SelectboxColumn("Tipo Prestador",width="medium",options=opcoes_tipo_prestador),
      "id_prestadora": st.column_config.TextColumn("ID da Prestadora",width="small",disabled=True),
      "status": st.column_config.SelectboxColumn("Status do Prestador",width="medium",options=["ativo","inativo"]),
  }

  mostrar_todos = st.toggle("Mostrar todos",value=False)

  if mostrar_todos:
    visualizar_prestadoras_df = prestadora_df.loc[prestadora_df["status"].isin(["ativo","inativo"])]
  else:
    visualizar_prestadoras_df = prestadora_df.loc[prestadora_df["status"].isin(["ativo"])]

  edited_prestadora_df = st.data_editor(visualizar_prestadoras_df,
                                        use_container_width=True,
                                        hide_index=True,
                                        column_order=column_order_prestadoras,
                                        column_config=column_config_prestadoras,
                                        num_rows="fixed")

  if st.button("Salvar alterações"):
    st.session_state["dados_prestadoras"] = edited_prestadora_df
    update_to_sheets("base_prestadoras", edited_prestadora_df)

    st.success("Alterações salvas com sucesso!")

if seletor_pagina == "Comissões":
  st.subheader("Configurar comissões")

  column_order_comissao = ["Procedimento","Tipo de prestador","Valor"]
  opcoes_tipo_prestador = tipo_prestador_df["tipo_prestador"].dropna().unique()
  opcoes_procedimentos = procedimentos_df["procedimento"].dropna().unique()

  column_config_comissao = {
      "Tipo de prestador": st.column_config.SelectboxColumn("Tipo de prestador",width="medium",options=opcoes_tipo_prestador),
      "Procedimento": st.column_config.SelectboxColumn("Procedimento",width="medium",options=opcoes_procedimentos),
      "Valor": st.column_config.NumberColumn("Valor Comissão",width="medium",format="R$%.2f")
  }

  comissao_df = comissao_df[column_order_comissao]
  comissao_df = comissao_df.sort_values(by=["Valor","Procedimento"], ascending=[True,True],na_position="first")

  edited_comissao_df = st.data_editor(comissao_df,
                                      use_container_width=False,
                                      hide_index=True,
                                      column_order=column_order_comissao,
                                      column_config=column_config_comissao,
                                      num_rows="fixed"
                                      )

  if st.button("Salvar alterações"):

    edited_comissao_df = edited_comissao_df.loc[~edited_comissao_df[["Procedimento","Tipo de prestador"]].isna().any(axis=1)]
    st.session_state["dados_comissao"] = edited_comissao_df[column_order_comissao]
    
    result = upload_dataframe_to_mongodb(collection_name="comissoes",
                            database_name="relatorio_comissao",
                            dataframe=edited_comissao_df,
                            unique_keys=["Procedimento","Tipo de prestador"])
    
    st.success("Alterações salvas com sucesso!")

if seletor_pagina == "Tipo de prestadoras":

  st.subheader("Configurar Tipo de prestadoras")

  column_order_tipo_prestador = ["tipo_prestador"]

  column_config_tipo_prestador = {
      "tipo_prestador": st.column_config.TextColumn("Tipo de prestador",width="medium")
  }

  tipo_prestador_df = tipo_prestador_df[column_order_tipo_prestador]

  edited_tipo_prestador_df = st.data_editor(tipo_prestador_df,
                                      use_container_width=False,
                                      hide_index=True,
                                      column_order=column_order_tipo_prestador,
                                      column_config=column_config_tipo_prestador,
                                      num_rows="dynamic"
                                      )

  if st.button("Salvar alterações"):

    edited_tipo_prestador_df = edited_tipo_prestador_df.loc[~edited_tipo_prestador_df["tipo_prestador"].isna()]
    edited_tipo_prestador_df = edited_tipo_prestador_df[column_order_tipo_prestador]
    st.session_state["dados_tipo_prestador"] = edited_tipo_prestador_df[column_order_tipo_prestador]

    result = upload_dataframe_to_mongodb(collection_name="tipo_prestador",
                            database_name="relatorio_comissao",
                            dataframe=edited_tipo_prestador_df,
                            unique_keys=["funcao_prestadora"])
    
    st.success("Alterações salvas com sucesso!")