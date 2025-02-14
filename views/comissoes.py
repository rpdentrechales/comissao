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
    st.session_state["base_compilada"] = base_compilada

if "base_compilada" in st.session_state:

    base_compilada = st.session_state["base_compilada"]
    
    periodos = base_compilada["periodo"].unique()
    periodos_series = pd.Series(periodos)
    periodos_list = ("periodo: " + periodos_series.dt.strftime('%Y-%m-%d')).tolist()
    periodos_list.insert(0,"mensal")

    seletor_periodo = st.pills("Selecione Visão",periodos_list,selection_mode="single",default="mensal")

    if seletor_periodo == "mensal":
        base_filtrada = base_compilada.loc[base_compilada["tipo_pagamento"] == "mensal"]
        tipo_pagamento = "mensal"

    else:
        base_filtrada = base_compilada.loc[base_compilada["tipo_pagamento"] == "quinzenal"]
        tipo_pagamento = "quinzenal"

        if seletor_periodo == periodos_list[1]:
            base_filtrada = base_compilada.loc[base_compilada["periodo"] == periodos_series[0]]
        else:
            base_filtrada = base_compilada.loc[base_compilada["periodo"] == periodos_series[1]]
    
    st.write(seletor_periodo)
    st.dataframe(base_filtrada)
    base_comissoes = criar_comissoes(base_filtrada)
    st.dataframe(base_comissoes)
    base_avaliacoes = cria_avaliacoes(base_filtrada,tipo_pagamento)
    st.dataframe(base_avaliacoes)
    
    base_final = juntar_bases(base_comissoes,base_avaliacoes)

    st.dataframe(base_final,hide_index=True)
