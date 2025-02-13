# %% Imports
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

# %% 
vmb_path = "assets/venda-mensal-bruta_colab-bi_2025-02-11.xlsx"
agendamento_path = "assets/agendamentos_colab-bi_2025-02-12 (1).xlsx"

venda_mensal_df = pd.read_excel(vmb_path)
agendamentos_df = pd.read_excel(agendamento_path)
procedimentos_df = get_sheetdata("procedimentos_padronizados")
prestadora_df = get_sheetdata("base_prestadoras")
comissao_df = get_sheetdata("comissoes")
tipo_prestadora_df = get_sheetdata("tipo_prestadora")


# %%
relatorio_comissoes_df = criar_base_final(agendamentos_df,venda_mensal_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df)

display(relatorio_comissoes_df.sample(50))


# %%
base_agendamento = cria_base_agendamento(agendamentos_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df)
display(base_agendamento.loc[base_agendamento["nome_prestadora"].isna(),"Prestador"].unique())

# %%
