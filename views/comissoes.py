import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
from auxiliar.visualizar_prestadora import *
from auxiliar.arrumar_bases import *

st.set_page_config(page_title="Pró-Corpo - Comissões Consolidadas", page_icon="💎",layout="wide")

comissao_df = load_from_sheets("comissoes")
prestadora_df = load_from_sheets("base_prestadoras")
procedimentos_df = load_from_sheets("procedimentos_padronizados")
tipo_prestadora_df = load_from_sheets("tipo_prestadora")

uploaded_file = st.file_uploader("Subir Relatório de Agendamento")
if uploaded_file is not None:
    
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_excel(uploaded_file)
    st.write(dataframe)