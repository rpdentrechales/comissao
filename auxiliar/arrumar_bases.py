import pandas as pd
import numpy as np

def cria_base_agendamento(agendamentos_df,procedimentos_padronizados,prestadora_df,comissao_df,tipo_prestadora_df):

  colunas = ['ID agendamento', 'ID cliente', 'Unidade do agendamento', 'procedimento_padronizado', "nome_prestadora",
             "tipo_prestadora", 'Data','periodo',"mes","valor_comissao","tipo_pagamento"]

  for df in [agendamentos_df,procedimentos_padronizados,prestadora_df,comissao_df,tipo_prestadora_df]:
    for col in df.select_dtypes(include=["object"]).columns:
      df[col] = df[col].str.normalize("NFKC").str.strip().str.lower()

  comissao_df["valor_comissao"] = comissao_df["valor_comissao"].astype(str).str.replace("r$", "", regex=False).str.replace(",", ".").astype(float)

  base_limpa = agendamentos_df.loc[agendamentos_df["Unidade do agendamento"] != 'plástica']
  base_limpa = base_limpa.loc[base_limpa["Unidade do agendamento"] != 'homa']

  base_limpa = base_limpa.loc[base_limpa['Status'] == "atendido"]

  base_limpa = pd.merge(base_limpa, procedimentos_padronizados, left_on="Procedimento", right_on="procedimento_crm", how="left")
  base_limpa = pd.merge(base_limpa, prestadora_df, left_on="Prestador", right_on="nome_prestadora", how="left")
  base_limpa = pd.merge(base_limpa, comissao_df, left_on=["procedimento_padronizado","tipo_prestadora"], right_on=["procedimento_padronizado","tipo_prestadora"], how="left")
  base_limpa = pd.merge(base_limpa, tipo_prestadora_df, left_on=["tipo_prestadora"], right_on=["tipo_prestadora"], how="left")

  base_limpa["Data"] = pd.to_datetime(base_limpa["Data"],format="%d/%m/%Y")
  start_of_month = base_limpa['Data'].dt.to_period('M').dt.start_time
  base_limpa['periodo'] = start_of_month + pd.to_timedelta(15 * (base_limpa['Data'].dt.day > 15), unit='D')
  base_limpa["mes"] = base_limpa['Data'].dt.to_period('M')

  base_limpa = base_limpa.reset_index()

  base_limpa = base_limpa[colunas]

  return base_limpa

def cria_base_revenda(venda_mensal_df):

  colunas = ['Unidade','nome_prestadora', "comissao_revenda"]

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

  revenda_df = revenda_df.rename(columns={"Avaliador":"nome_prestadora","Valor líquido":"valor_revenda",'Data venda':"Data"})

  revenda_por_prestador = revenda_df.groupby(["nome_prestadora","Unidade"]).agg(valor_revenda=("valor_revenda","sum"))
  revenda_por_prestador = revenda_por_prestador.reset_index()
  revenda_por_prestador["revenda_total"] = revenda_por_prestador.groupby(["nome_prestadora"])['valor_revenda'].transform("sum")
  revenda_por_prestador["revenda_proporcional"] = revenda_por_prestador["valor_revenda"]/revenda_por_prestador["revenda_total"]

  valor_comissao_revenda = 50
  bin_width = 2500
  max_val = revenda_por_prestador["revenda_total"].max()
  bins = np.arange(0, max_val + bin_width, bin_width)
  labels = np.arange(0, len(bins) - 1)
  revenda_total = revenda_por_prestador["revenda_total"]

  labels = labels * valor_comissao_revenda
  revenda_por_prestador["comissao_revenda"] = pd.cut(revenda_total, bins=bins, labels=labels, include_lowest=True)
  revenda_por_prestador.loc[revenda_por_prestador["comissao_revenda"] < 200,"comissao_revenda"] = 0
  revenda_por_prestador["comissao_revenda"] = revenda_por_prestador["comissao_revenda"].astype(float)
  revenda_por_prestador["comissao_revenda"] = (
      revenda_por_prestador["comissao_revenda"] * revenda_por_prestador["revenda_proporcional"]
  )

  revenda_df = revenda_por_prestador[colunas]
  revenda_df["Unidade"] = revenda_df["Unidade"].str.normalize("NFKC").str.strip().str.lower()
  revenda_df["nome_prestadora"] = revenda_df["nome_prestadora"].str.normalize("NFKC").str.strip().str.lower()

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

def criar_base_compilada(agendamentos_df,venda_mensal_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df):

    base_procedimentos_final = cria_base_agendamento(agendamentos_df,procedimentos_df,prestadora_df,comissao_df,tipo_prestadora_df)
    base_procedimentos_final = adicionar_receita_avaliacao(base_procedimentos_final,venda_mensal_df)

    return base_procedimentos_final

def cria_avaliacoes(base_procedimentos_final,tipo_pagamento):

  if tipo_pagamento == "quinzenal":
    coluna_receita = "receita_periodo"
  else:
    coluna_receita = "receita_mes"

  base_avaliacoes = base_procedimentos_final.loc[base_procedimentos_final["procedimento_padronizado"].str.contains("avaliação",na=False)].copy()
  base_avaliacoes["valor_avaliacao"] = 10
  base_avaliacoes.loc[base_avaliacoes[coluna_receita] >= 200,"valor_avaliacao"] = 20

  base_avaliacoes = base_avaliacoes.groupby(["nome_prestadora","tipo_prestadora","Unidade"]).agg(avaliacoes_total=('valor_avaliacao', 'sum'))

  return base_avaliacoes
    

def criar_comissoes(base_procedimentos_final):

    base_comissoes = base_procedimentos_final.groupby(["nome_prestadora","tipo_prestadora","Unidade"]).agg(comissao_total=('valor_comissao', 'sum'))
    base_comissoes = base_comissoes.reset_index()
    
    return base_comissoes

def criar_base_lavieen(base_procedimentos_final):
  base_lavieen_filtrada = base_procedimentos_final.loc[base_procedimentos_final["procedimento_padronizado"].str.contains("lavieen",case=False,na=False)]
  base_lavieen_groupby = base_lavieen_filtrada.groupby(["nome_prestadora","Unidade"]).agg(quantidade_lavieen=('Data', 'nunique')).reset_index()

  comissao_lavieen = 500
  base_lavieen_groupby["valor_lavieen"] = comissao_lavieen * base_lavieen_groupby["quantidade_lavieen"]

  return base_lavieen_groupby

def juntar_bases(base_comissoes,base_avaliacoes,revenda_df,base_lavieen,base_garantido):

  colunas = ['nome_prestadora', 'tipo_prestadora', 'Unidade', 'comissao_total','avaliacoes_total','comissao_revenda','valor_lavieen',"comissao_garantido_total"]

  base_final = pd.merge(base_comissoes,base_avaliacoes,how="left",on=["nome_prestadora","tipo_prestadora","Unidade"])
  base_final = pd.merge(base_final,revenda_df,how="left",on=["nome_prestadora","Unidade"])
  base_final = pd.merge(base_final,base_lavieen,how="left",on=["nome_prestadora","Unidade"])
  base_final = pd.merge(base_final,base_garantido,how="left",on=["nome_prestadora","Unidade"])
  
  colunas_de_numeros = ["avaliacoes_total", "comissao_revenda", "comissao_total","valor_lavieen","comissao_garantido_total"]
  base_final[colunas_de_numeros] = base_final[colunas_de_numeros].fillna(0)
  
  return base_final[colunas]


def criar_base_garantido(base_procedimentos_final,garantido_df):
  base_garantido = base_procedimentos_final.groupby(["nome_prestadora","Unidade","Data"]).agg(comissao_total_dia=('valor_comissao', 'sum')).reset_index()
  base_garantido = pd.merge(base_garantido,garantido_df,how="left",on=["nome_prestadora","Unidade"])

  mask_garantido_dia = base_garantido["tipo_garantido"] == "dia"
  mask_comissao_dia = base_garantido["comissao_total_dia"] < base_garantido["valor_garantido"]
  base_garantido["comissao_garantido_dia"] = base_garantido["comissao_total_dia"]
  base_garantido.loc[mask_comissao_dia&mask_garantido_dia,"comissao_garantido_dia"] = base_garantido["valor_garantido"]

  groupby_total = base_garantido.groupby(["nome_prestadora","Unidade"]).agg(comissao_garantido_total = ("comissao_garantido_dia","sum")).reset_index()
  base_garantido = pd.merge(groupby_total,garantido_df,how="left",on=["nome_prestadora","Unidade"])

  mask_garantido_mes = base_garantido["tipo_garantido"] == "mes"
  mask_comissao_mes = base_garantido["comissao_garantido_total"] < base_garantido["valor_garantido"]

  base_garantido.loc[mask_garantido_mes&mask_comissao_mes,"comissao_garantido_total"] = base_garantido["valor_garantido"]
  colunas = ["nome_prestadora","Unidade","comissao_garantido_total"]

  return base_garantido[colunas]