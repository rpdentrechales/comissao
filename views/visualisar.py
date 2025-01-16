import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
import plotly.express as px

st.set_page_config(page_title="Pró-Corpo - Visualizar Comissões", page_icon="💎",layout="wide")

url_parameters = st.query_params
error_page = True

if "id" in url_parameters:

  id_prestadora = st.query_params["id"]
  prestadora_df = get_dataframe_from_mongodb(collection_name="prestadores_db", database_name="relatorio_comissao")
  prestadora_df = prestadora_df.loc[prestadora_df["id_prestador"] == id_prestadora]
  nome_prestadora = prestadora_df["nome_prestador"].iloc[0]
  funcao_prestadora = prestadora_df["funcao_prestadora"].iloc[0]

  comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
  comissao_df = comissao_df.loc[comissao_df["funcao_prestadora"] == funcao_prestadora]
  comissao = comissao_df["comissao"].iloc[0]

  if nome_prestadora:
    query = {"Prestador": nome_prestadora}
    atendimentos_df = get_dataframe_from_mongodb(collection_name="agendamentos_db", database_name="relatorio_comissao",query=query)
    atendimentos_df['Data'] = pd.to_datetime(atendimentos_df['Data'])
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
      st.metric(label="Atendimentos Totais", value=f"atendimentos_totais")

      atendimentos_graph = plot_bar_graph(groupby_dia, "ID agendamento")

    with metrica_mes_2:
      comissao_total = filtered_atendimentos_df["comissao"].sum()
      st.metric(label="Comissão total", value=f"R$ {comissao_total:,.2f}")

      comissao_graph = plot_bar_graph(groupby_dia, "comissao")


    st.dataframe(filtered_atendimentos_df)
    error_page = False

if error_page:
  st.title("Página não encontrada")
