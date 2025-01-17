import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
import plotly.express as px

st.set_page_config(page_title="Pró-Corpo - Visualizar Comissões", page_icon="💎",layout="wide")

url_parameters = st.query_params
error_page = False
erro_message = "ID não encontrado"

if "reset_cache" in st.session_state:
  reset_cache = st.session_state["reset_cache"]
else:
  reset_cache = 0
  st.session_state["reset_cache"] = reset_cache

if "id" in url_parameters:

  id_prestadora = st.query_params["id"]
  prestadora_df = get_dataframe_from_mongodb(collection_name="prestadores_db",
                                             database_name="relatorio_comissao",
                                             reset_cache = reset_cache)
  
  prestadora_df = prestadora_df.loc[prestadora_df["id_prestador"] == id_prestadora]
  if prestadora_df.empty:

    error_page = True
    erro_message = "ID da prestadora não encontrado..."

  else:
    nome_prestadora = prestadora_df["nome_prestador"].iloc[0]
    funcao_prestadora = prestadora_df["funcao_prestadora"].iloc[0]

  comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
  comissao_df = comissao_df.loc[comissao_df["funcao_prestadora"] == funcao_prestadora]

  if comissao_df.empty:

    error_page = True
    erro_message = "Erro no cadastro da Prestadora...\nClick em recarregar.."

  else:
    comissao = comissao_df["comissao"].iloc[0]

  if error_page:

    st.title(erro_message)
    recarregar = st.button("Recarregar")
    
    if recarregar:

      reset_cache += 1
      st.session_state["reset_cache"] = reset_cache

  else:

    query = {"Prestador": nome_prestadora}
    atendimentos_df = get_dataframe_from_mongodb(collection_name="agendamentos_db", database_name="relatorio_comissao",query=query)
    atendimentos_df['Data'] = pd.to_datetime(atendimentos_df['Data'],format="%d/%m/%Y")
    atendimentos_df['period'] = atendimentos_df['Data'].dt.to_period('M')
    atendimentos_df["comissao"] = comissao

    st.title(f"Comissões - {nome_prestadora}")

    meses = sorted(atendimentos_df["period"].unique(),reverse=True)

    seletor_mes = st.selectbox("Selecione um mês", meses)
    filtered_atendimentos_df = atendimentos_df.loc[atendimentos_df["period"] == seletor_mes]

    groupby_dia = filtered_atendimentos_df.groupby(['Data']).agg({'ID agendamento': 'nunique', 'comissao': 'sum'}).reset_index()

    metrica_mes_1,metrica_mes_2= st.columns(2)

    with metrica_mes_1:
      atendimentos_totais = filtered_atendimentos_df["ID agendamento"].nunique()
      st.metric(label="Atendimentos Totais", value=atendimentos_totais)

      atendimentos_graph = plot_bar_graph(groupby_dia, "ID agendamento","Agendamentos por dia")
      st.plotly_chart(atendimentos_graph, use_container_width=True)

    with metrica_mes_2:
      comissao_total = filtered_atendimentos_df["comissao"].sum()
      st.metric(label="Comissão total", value=f"R$ {comissao_total:,.2f}")

      comissao_graph = plot_bar_graph(groupby_dia, "comissao","Comissão por dia (R$)")
      st.plotly_chart(comissao_graph, use_container_width=True)

    st.subheader("Detalhe diário:")
    colunas = ["Data","ID agendamento","Procedimento","Unidade do agendamento"]
    resumo_df = filtered_atendimentos_df[colunas]
    resumo_df["Data"] = resumo_df["Data"].dt.strftime('%d/%m/%Y')

    st.dataframe(resumo_df,hide_index=True,use_container_width=True)
