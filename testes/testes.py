# %% Imports and variables

import pandas as pd
from datetime import datetime, timedelta
from IPython.display import display
import toml
import gspread
from google.oauth2.service_account import Credentials
from auxiliar.arrumar_bases import *

def get_sheetdata(sheet_name):
    # Load credentials from the .streamlit/secrets.toml file
    secrets = toml.load(".streamlit/secrets.toml")
    creds_info = secrets["connections"]["gsheets"]

    # Define scopes for accessing Google Sheets and Drive
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # Create credentials and authorize the gspread client
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet using the URL from the toml file
    spreadsheet = client.open_by_url(creds_info["spreadsheet"])

    # Select the first worksheet and fetch all records
    worksheet = spreadsheet.worksheet(sheet_name)
    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df
    
vmb_path = "assets/venda-mensal-bruta_colab-bi_2025-02-11.xlsx"
agendamento_path = "assets/agendamentos_colab-bi_2025-02-12 (1).xlsx"

venda_mensal_df = pd.read_excel(vmb_path)
agendamentos_df = pd.read_excel(agendamento_path)
procedimentos_df = get_sheetdata("procedimentos_padronizados")
prestadora_df = get_sheetdata("base_prestadoras")
comissao_df = get_sheetdata("comissoes")
tipo_prestadora_df = get_sheetdata("tipo_prestadora")

# %%
base_compilada = criar_base_compilada(agendamentos_df,venda_mensal_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df)
periodos = base_compilada["periodo"].unique()
periodos = pd.Series(periodos)
s_date_str = "periodo: " + periodos.dt.strftime('%Y-%m-%d')


base_compilada.columns
#%%

base_comissoes = criar_comissoes(base_compilada)
display(base_comissoes)


#%%
base_avaliacoes = cria_avaliacoes(base_compilada,"mensal")
display(base_avaliacoes)

# %%
base_final = juntar_bases(base_comissoes,base_avaliacoes)
display(base_final)
