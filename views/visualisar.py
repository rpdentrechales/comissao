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
  prestadora_df = get_dataframe_from_mongodb(collection_name="dados_vendedoras", database_name="rpd_db")
  prestadora_df = prestadora_df.loc[prestadora_df["id_prestadora"] == id_vendedora]
  nome_vendedora = prestadora_df["nome_vendedora"].iloc[0]

  if nome_vendedora:
    query = {"created_by": nome_vendedora,"status":"completed"}
    get_dataframe_from_mongodb("relatorio_comissao", "agendamentos_db")
    billcharges_prestadora_df = get_dataframe_from_mongodb(collection_name="billcharges_db", database_name="dash_midia",query=query)

    error_page = False

if error_page:
  st.title("Página não encontrada")
