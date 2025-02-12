import pandas as pd
from auxiliar.auxiliar import *

comissao_df = load_from_sheets("comissoes")
prestadora_df = load_from_sheets("base_prestadoras")
procedimentos_df = load_from_sheets("procedimentos_padronizados")

def cria_base_agendamento(agendamentos_df,procedimentos_padronizados,prestadora_df):

  colunas = ['ID agendamento', 'ID cliente', 'Unidade do agendamento', 'procedimento_padronizado', "nome_prestadora","tipo_prestadora", 'Data','periodo',"mes","valor_comissao"]

  base_limpa = agendamentos_df.loc[agendamentos_df["Unidade do agendamento"] != 'PLÁSTICA']
  base_limpa = base_limpa.loc[base_limpa["Unidade do agendamento"] != 'HOMA']

  base_limpa = base_limpa.loc[base_limpa['Status'] == "Atendido"]
  base_limpa["Procedimento"] = base_limpa["Procedimento"].str.normalize("NFKC").str.strip()
  procedimentos_padronizados["procedimento_crm"] = procedimentos_padronizados["procedimento_crm"].str.normalize("NFKC").str.strip()

  base_limpa = pd.merge(base_limpa, procedimentos_padronizados, left_on="Procedimento", right_on="procedimento_crm", how="left")
  base_limpa = pd.merge(base_limpa, prestadora_df, left_on="Prestador", right_on="nome_prestadora", how="left")
  base_limpa = pd.merge(base_limpa, comissao_df, left_on=["procedimento_padronizado","tipo_prestadora"], right_on=["procedimento_padronizado","tipo_prestadora"], how="left")

  base_limpa["Data"] = pd.to_datetime(base_limpa["Data"],format="%d/%m/%Y")
  start_of_month = base_limpa['Data'].dt.to_period('M').dt.start_time
  base_limpa['periodo'] = start_of_month + pd.to_timedelta(15 * (base_limpa['Data'].dt.day > 15), unit='D')
  base_limpa["mes"] = base_limpa['Data'].dt.to_period('M')
  st.write(base_limpa.columns)
  base_limpa = base_limpa[colunas]

  return base_limpa

def cria_base_revenda(venda_mensal_df):
  colunas = ['Data', 'Unidade','Prestador', 'valor_revenda','ID cliente',"mes","periodo","procedimento_padronizado","ID agendamento"]

  revenda_df = venda_mensal_df.loc[venda_mensal_df["Revenda"] == "SIM"]
  revenda_df = revenda_df.loc[revenda_df["Status"] == "Finalizado"]
  revenda_df = revenda_df.loc[revenda_df["Cortesia?"] == "Não"]
  revenda_df = revenda_df.loc[revenda_df["Valor líquido"] > 0]
  revenda_df = revenda_df.drop_duplicates(keep="first")

  revenda_df["Data venda"] = pd.to_datetime(revenda_df["Data venda"])
  revenda_df["Data venda"] = revenda_df['Data venda'].dt.normalize()
  start_of_month = revenda_df['Data venda'].dt.to_period('M').dt.start_time
  revenda_df['periodo'] = start_of_month + pd.to_timedelta(15 * (revenda_df['Data venda'].dt.day > 15), unit='D')
  revenda_df["mes"] = revenda_df['Data venda'].dt.to_period('M')

  revenda_df["procedimento_padronizado"] = "revenda"

  revenda_df = revenda_df.rename(columns={"Avaliador":"Prestador","Valor líquido":"valor_revenda",'Data venda':"Data"})
  revenda_df["ID agendamento"] = "orc-"+revenda_df["ID orçamento"].astype(str)
  revenda_df = revenda_df[colunas]

  return revenda_df

def adicionar_receita_avaliacao(base_procedimentos_final,venda_mensal_df):

  venda_mensal_df["Data venda"] = pd.to_datetime(venda_mensal_df["Data venda"])
  start_of_month = venda_mensal_df['Data venda'].dt.to_period('M').dt.start_time
  venda_mensal_df['periodo'] = start_of_month + pd.to_timedelta(15 * (venda_mensal_df['Data venda'].dt.day > 15), unit='D')
  venda_mensal_df["mes"] = venda_mensal_df['Data venda'].dt.to_period('M')

  receita_mes = venda_mensal_df.groupby(['ID cliente','mes']).agg({"Valor líquido":"sum"}).reset_index()
  receita_periodo = venda_mensal_df.groupby(['ID cliente','periodo']).agg({"Valor líquido":"sum"}).reset_index()

  base_procedimentos_final = pd.merge(base_procedimentos_final, receita_mes, left_on=["ID cliente","mes"], right_on=["ID cliente","mes"], how="left")
  base_procedimentos_final = pd.merge(base_procedimentos_final, receita_periodo, left_on=["ID cliente","periodo"], right_on=["ID cliente","periodo"], how="left")

  base_procedimentos_final = base_procedimentos_final.rename(columns={"Valor líquido_x":"receita_mes","Valor líquido_y":"receita_periodo","Unidade do agendamento":"Unidade"})
  base_procedimentos_final["receita_mes"] = base_procedimentos_final["receita_mes"].astype(float).fillna(0)
  base_procedimentos_final["receita_periodo"] = base_procedimentos_final["receita_periodo"].astype(float).fillna(0)

  return base_procedimentos_final

def adicionar_revenda(base_procedimentos_final,base_revenda):

  base_procedimentos_final = pd.concat([base_procedimentos_final,base_revenda], ignore_index=True)
  base_procedimentos_final["valor_revenda"] = base_procedimentos_final["valor_revenda"].astype(float).fillna(0)
  base_procedimentos_final["receita_mes"] = base_procedimentos_final["receita_mes"].astype(float).fillna(0)
  base_procedimentos_final["receita_periodo"] = base_procedimentos_final["receita_periodo"].astype(float).fillna(0)

  return base_procedimentos_final

def criar_base_final(agendamentos_df,venda_mensal_df):

    base_revenda = cria_base_revenda(venda_mensal_df)
    base_procedimentos_final = cria_base_agendamento(agendamentos_df,procedimentos_df,prestadora_df)
    base_procedimentos_final = adicionar_receita_avaliacao(base_procedimentos_final,venda_mensal_df)
    base_procedimentos_final = adicionar_revenda(base_procedimentos_final,base_revenda)

    # base_procedimentos_final = pd.merge(base_procedimentos_final,comissao_df,how="left",left_on=["procedimento_padronizado",])

    return base_procedimentos_final