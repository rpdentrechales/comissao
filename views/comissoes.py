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
garantido_df = load_from_sheets("base_garantido")

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
    st.session_state["venda_mensal_df"] = venda_mensal_df

if "base_compilada" in st.session_state:

    base_compilada = st.session_state["base_compilada"]
    venda_mensal_df = st.session_state["venda_mensal_df"]
    
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
            base_filtrada = base_filtrada.loc[base_filtrada["periodo"] == periodos_series[0]]
        else:
            base_filtrada = base_filtrada.loc[base_filtrada["periodo"] == periodos_series[1]]
    
    base_comissoes = criar_comissoes(base_filtrada)
    base_avaliacoes = cria_avaliacoes(base_filtrada,tipo_pagamento)
    base_revenda = cria_base_revenda(venda_mensal_df)
    base_lavieen = criar_base_lavieen(base_compilada)
    base_garantido = criar_base_garantido(base_compilada,garantido_df)
    
    base_final = juntar_bases(base_comissoes,base_avaliacoes,base_revenda,base_lavieen,base_garantido)

    column_config={
        "comissao_total": st.column_config.NumberColumn(
            "Comissão sem Garantido",
            format="R$ %.2f",
        ),
        "avaliacoes_total": st.column_config.NumberColumn(
            "Avaliações Total",
            format="R$ %.2f",
        ),
        "comissao_revenda": st.column_config.NumberColumn(
            "Comissão Revenda",
            format="R$ %.2f",
        ),
        "nome_prestadora": st.column_config.TextColumn(
            "Prestadora"
        ),
        "tipo_prestadora": st.column_config.TextColumn(
            "Tipo de Prestadora"
        ),
        "valor_lavieen": st.column_config.NumberColumn(
            "Lavieen",
            format="R$ %.2f",
        ),
        "comissao_garantido_total": st.column_config.NumberColumn(
            "Comissão com Garantido",
            format="R$ %.2f",
        )
    }

    ordem_das_colunas = ['nome_prestadora', 'tipo_prestadora', 'Unidade', 'comissao_total',
                         'comissao_garantido_total','avaliacoes_total', 'comissao_revenda', 'valor_lavieen'
                        ]

    st.dataframe(base_final[ordem_das_colunas],hide_index=True,column_config=column_config,use_container_width=True)
