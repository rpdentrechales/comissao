import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
import plotly.express as px

st.set_page_config(page_title="Pró-Corpo - Visualizar Comissões", page_icon="💎",layout="wide")

url_parameters = st.query_params
error_page = False
erro_message = "ID não encontrado"

if "reset_cache" in st.session_state:
  reset_cache = st.session_state["reset_cache"]
else:
  reset_cache = 0
  st.session_state["reset_cache"] = reset_cache

if "id" in url_parameters:

  id_prestadora = st.query_params["id"]

  query_id_prestadora = {"id_prestador": id_prestadora}
  prestadora_df = get_dataframe_from_mongodb(collection_name="prestadores_db",
                                             database_name="relatorio_comissao",
                                             reset_cache = reset_cache,
                                             query=query_id_prestadora)
  
  prestadora_df = prestadora_df.loc[prestadora_df["id_prestador"] == id_prestadora]

  if prestadora_df.empty:

    error_page = True
    erro_message = "ID da prestadora não encontrado..."

  else:
    nome_prestadora = prestadora_df["nome_prestador"].iloc[0]
    funcao_prestadora = prestadora_df["funcao_prestadora"].iloc[0]

    query_tipo_prestadora = {"Tipo de prestador": funcao_prestadora}

    comissao_df = get_dataframe_from_mongodb(
                                            collection_name="comissoes",
                                            database_name="relatorio_comissao",
                                            query=query_tipo_prestadora
                                            )

  if comissao_df.empty:

    error_page = True
    erro_message = "Erro no cadastro da Prestadora...\nClick em recarregar.."

  query_prestador = {"Prestador": nome_prestadora}
  atendimentos_df = get_dataframe_from_mongodb(
                                              collection_name="agendamentos_db",
                                              database_name="relatorio_comissao",
                                              query=query_prestador
                                              )
  
  if atendimentos_df.empty:

    error_page = True
    erro_message = "Não há dados dessa prestadora na base de agendamentos...\nClick em recarregar.."

  if error_page:

    st.title(erro_message)
    recarregar = st.button("Recarregar")
    
    if recarregar:

      reset_cache += 1
      st.session_state["reset_cache"] = reset_cache

  else:

    atendimentos_df['Data'] = pd.to_datetime(atendimentos_df['Data'],format="%d/%m/%Y")
    atendimentos_df['period'] = atendimentos_df['Data'].dt.to_period('M')
    merged_data_df = pd.merge(atendimentos_df,comissao_df,how="left",left_on="Procedimento",right_on="Procedimento")

    st.title("Comissões:")
    st.subheader(nome_prestadora)

    meses = sorted(merged_data_df["period"].unique(),reverse=True)

    seletor_mes = st.selectbox("Selecione um mês", meses)
    filtered_atendimentos_df = merged_data_df.loc[merged_data_df["period"] == seletor_mes]

    groupby_dia = filtered_atendimentos_df.groupby(['Data']).agg({'ID agendamento': 'nunique', 'Valor': 'sum'}).reset_index()

    metrica_mes_1,metrica_mes_2= st.columns(2)

    with metrica_mes_1:
      atendimentos_totais = filtered_atendimentos_df["ID agendamento"].nunique()
      st.metric(label="Atendimentos Totais", value=atendimentos_totais)

      atendimentos_graph = plot_bar_graph(groupby_dia, "ID agendamento","Agendamentos por dia")
      st.plotly_chart(atendimentos_graph, use_container_width=True)

    with metrica_mes_2:
      comissao_total = filtered_atendimentos_df["Valor"].sum()
      st.metric(label="Comissão total", value=f"R$ {comissao_total:,.2f}")

      comissao_graph = plot_bar_graph(groupby_dia, "Valor","Comissão por dia (R$)")
      st.plotly_chart(comissao_graph, use_container_width=True)

    st.subheader("Detalhe diário:")
    colunas = ["Data","ID agendamento","Procedimento","Unidade do agendamento","Valor"]
    resumo_df = filtered_atendimentos_df[colunas]
    resumo_df["Data"] = resumo_df["Data"].dt.strftime('%d/%m/%Y')

    column_config_comissao = {
      "Valor": st.column_config.NumberColumn("Valor Comissão",width="medium",format="R$%.2f"),
      "ID agendamento": st.column_config.TextColumn("ID agendamento",width="medium")
    }

    st.dataframe(
                resumo_df,
                hide_index=True,
                use_container_width=True,
                column_order=colunas,
                column_config=column_config_comissao
                )

    procedimentos_sem_valor = merged_data_df.loc[merged_data_df["Valor"].isnull(),["Procedimento","Tipo de prestador","Valor"]].drop_duplicates()
    procedimentos_sem_valor["Tipo de prestador"] = funcao_prestadora

    quantidade_de_procedimentos_sem_valor = procedimentos_sem_valor.shape[0]

    if quantidade_de_procedimentos_sem_valor > 0:
      st.write(f"Foram encontrados {quantidade_de_procedimentos_sem_valor} procedimentos sem valor cadastrado")

      subir_procedimentos = st.button("Informar procedimentos sem valor cadastrado")

      if subir_procedimentos:
        result_comissao = upload_dataframe_to_mongodb(collection_name="comissoes",
                                database_name="relatorio_comissao",
                                dataframe=procedimentos_sem_valor,
                                unique_keys=["Procedimento","Tipo de prestador"])

        result_procedimento = upload_dataframe_to_mongodb(collection_name="procedimentos",
                                database_name="relatorio_comissao",
                                dataframe=procedimentos_sem_valor["Procedimento"].unique(),
                                unique_keys=["Procedimento"])
    
        st.success("Procedimentos informados com sucesso!")
        st.write("Dentro de alguns dias o valor será atualizado no sistema")


st.title("testes")

comissao_df = get_dataframe_from_mongodb(collection_name="comissoes",database_name="relatorio_comissao")

prestadores_df = get_dataframe_from_mongodb(collection_name="prestadores_db",
                                            database_name="relatorio_comissao",
                                            query = { "funcao_prestadora": { "$ne": None } })

prestadoras = prestadores_df["nome_prestador"].unique()
extrato_df = get_dataframe_from_mongodb(collection_name="extrato_prestadoras",
                                        database_name="relatorio_comissao",
                                        query = { "Prestador": { "$in": list(prestadoras) }})

prestadores_df = prestadores_df[["nome_prestador","funcao_prestadora"]]

merged_df = pd.merge(extrato_df,prestadores_df,how="left",left_on="Prestador",right_on="nome_prestador")
merged_df = pd.merge(merged_df,comissao_df,
                     how="left",
                     left_on=["Procedimento","funcao_prestadora"],
                     right_on=["Procedimento","Tipo de prestador"])

merged_df["valor_total"] = merged_df["Valor"]*merged_df["quantidade"]
merged_df = merged_df.loc[~merged_df["Valor"].isna()]

teste_df = merged_df.loc[merged_df["Prestador"] == "Bárbara Raquel de Góes Silva"]
st.dataframe(teste_df)

st.write(f"quantidade: {teste_df["quantidade"].sum()}")
st.write(f"valor: {teste_df["valor_total"].sum()}")
