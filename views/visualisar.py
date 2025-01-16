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

  if nome_prestadora:
    query = {"Prestador": nome_prestadora}
    atendimentos_df = get_dataframe_from_mongodb(collection_name="agendamentos_db", database_name="relatorio_comissao",query=query)
    atendimentos_df['date'] = pd.to_datetime(atendimentos_df['date'])
    atendimentos_df['period'] = atendimentos_df['Data'].dt.to_period('M')

    st.title(f"Comissões - {nome_prestadora}")

    st.dataframe(atendimentos_df)
    error_page = False

if error_page:
  st.title("Página não encontrada")
