import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *

st.set_page_config(page_title="Pró-Corpo - Extratos", page_icon="💎",layout="wide")

st.title("Extratos de Comissão")
seletor_pagina = st.pills("Selecionar Visão",["Geral", "Por Prestador"],selection_mode="single",default="Geral")

if seletor_pagina == "Geral":
    comissao_df = get_dataframe_from_mongodb(collection_name="comissoes", database_name="relatorio_comissao")
    prestadores_df = get_dataframe_from_mongodb(collection_name="prestadores_db", database_name="relatorio_comissao",query = { "funcao_prestadora": { "$ne": None } })

    prestadoras = prestadores_df["nome_prestador"].unique()
    extrato_df = get_dataframe_from_mongodb(collection_name="extrato_prestadoras", database_name="relatorio_comissao",query = { "Prestador": { "$in": list(prestadoras) } })

    prestadores_df = prestadores_df[["nome_prestador","funcao_prestadora"]]

    merged_df = pd.merge(extrato_df,prestadores_df,how="left",left_on="Prestador",right_on="nome_prestador")
    merged_df = pd.merge(merged_df,comissao_df,how="left",left_on=["Procedimento","funcao_prestadora"],right_on=["Procedimento","Tipo de prestador"])

    merged_df["valor_total"] = merged_df["Valor"]*merged_df["quantidade"]

    merged_df = merged_df.loc[~merged_df["Valor"].isna()]

    groupby_mes = merged_df.groupby(["nome_prestador","Tipo de prestador","periodo"]).agg({"valor_total":"sum"})

    pivot = pd.pivot_table(
        groupby_mes,
        values="valor_total",
        index=["nome_prestador", "Tipo de prestador"],
        columns=["periodo"],
        aggfunc="sum",
    )

    pivot_reset = pivot.reset_index()

    column_config={
            "nome_prestador": "Prestador",
            "Tipo de prestador": "Tipo de Prestador",
            **{col: st.column_config.NumberColumn(f"Comissão - {col}",width="medium",format="R$%.2f") for col in pivot.columns},
        }


    st.dataframe(
        pivot_reset,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )