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

uploader_col_1, uploader_col_2 = st.columns(2)

with uploader_col_1:
    st.subheader("Subir Relatório de Agendamento")
    agendamento_file = st.file_uploader("Agendamento",type=["xlsx"],label_visibility = "collapsed")

with uploader_col_2:
    st.subheader("Subir Relatório de Venda Mensal Bruta")
    vmb_file = st.file_uploader("Venda Mensal",type=["xlsx"],label_visibility = "collapsed")

if (agendamento_file is not None) and (vmb_file is not None):
    button_disabled = False

else:
    button_disabled = True

processar_button = st.button("Processar Arquivos",disabled=button_disabled)

if processar_button:
    
    venda_mensal_df = pd.read_excel(vmb_file)
    agendamentos_df = pd.read_excel(agendamento_file)

    relatorio_comissoes_df = criar_base_final(agendamentos_df,venda_mensal_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df)

    st.dataframe(relatorio_comissoes_df)
