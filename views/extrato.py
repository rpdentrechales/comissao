import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *

st.set_page_config(page_title="Pró-Corpo - Extratos", page_icon="💎",layout="wide")

st.title("Extratos de Comissão")
seletor_pagina = st.pills("Selecionar Visão",["Geral", "Por Prestador"],selection_mode="single",default="Geral")


comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
prestadores_df = get_dataframe_from_mongodb(collection_name="prestadores_db", database_name="relatorio_comissao",query = { "funcao_prestadora": { "$ne": None } })

prestadoras = prestadores_df["nome_prestador"].unique()
extrato_df = get_dataframe_from_mongodb(collection_name="extrato_prestadoras", database_name="relatorio_comissao",query = { "Prestador": { "$in": list(prestadoras) } })

prestadores_df = prestadores_df[["nome_prestador","funcao_prestadora"]]

merged_df = pd.merge(extrato_df,prestadoras,how="left",left_on="Prestador",right_on="nome_prestador")

st.dataframe(merged_df)