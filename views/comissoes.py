import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
from auxiliar.arrumar_bases import *

st.set_page_config(page_title="Pró-Corpo - Comissões Consolidadas", page_icon="💎",layout="wide")

comissao_df = load_from_sheets("comissoes")
prestadora_df = load_from_sheets("base_prestadoras")
procedimentos_df = load_from_sheets("procedimentos_padronizados")
tipo_prestadora_df = load_from_sheets("tipo_prestadora")

st.title("Calcular Comissões")

uploader_col_1, uploader_col_2 = st.columns(2)

with uploader_col_1:
    st.subheader("Subir Agendamentos")
    agendamento_file = st.file_uploader("Agendamento",type=["xlsx"],label_visibility = "collapsed")

with uploader_col_2:
    st.subheader("Subir Venda Mensal Bruta")
    vmb_file = st.file_uploader("Venda Mensal",type=["xlsx"],label_visibility = "collapsed")

if (agendamento_file is not None) and (vmb_file is not None):
    button_disabled = False

else:
    button_disabled = True

processar_button = st.button("Processar Arquivos",disabled=button_disabled)

if processar_button:
    
    venda_mensal_df = pd.read_excel(vmb_file)
    agendamentos_df = pd.read_excel(agendamento_file)

    base_compilada = criar_base_compilada(agendamentos_df,venda_mensal_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df)

    periodos = base_compilada["periodo"].unique()
    periodos_series = pd.Series(periodos)
    periodos_list = "periodo: " + periodos.dt.strftime('%Y-%m-%d')
    periodos_list = periodos.to_list()
    periodos = periodos.insert(0,"mensal")

    seletor_periodo = st.pills("Selecione Visão",periodos,selection_mode="single",default="mensal")

    if seletor_periodo == "mensal":
        base_filtrada = base_compilada_df.loc[base_compilada_df["tipo_pagamento"] == "mensal"]
        tipo_pagamento = "mensal"

    else:
        base_filtrada = base_compilada_df.loc[base_compilada_df["tipo_pagamento"] == "quinzenal"]
        tipo_pagamento = "quinzenal"

        if seletor_periodo == periodos_list[1]:
            base_filtrada = base_compilada_df.loc[base_compilada_df["periodo"] == periodos_series[0]]
        else:
            base_filtrada = base_compilada_df.loc[base_compilada_df["periodo"] == periodos_series[0]]
    

    base_comissoes = criar_comissoes(base_filtrada)
    base_avaliacoes = cria_avaliacoes(base_filtrada,tipo_pagamento)
    
    base_final = juntar_bases(base_comissoes,base_avaliacoes)

    st.dataframe(base_final,hide_index=True)
