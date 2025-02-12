# %%
import pandas as pd
from datetime import datetime, timedelta
from IPython.display import display

vmb_path = "assets/agendamentos_colab-bi_2025-02-12 (1).xlsx"
agendamento_path = "assets/agendamentos_colab-bi_2025-02-12 (1).xlsx"

venda_mensal_df = pd.read_excel(vmb_path)
agendamentos_df = pd.read_excel(agendamento_path)

#relatorio_comissoes_df = criar_base_final(agendamentos_df,venda_mensal_df)

display(agendamentos_df)