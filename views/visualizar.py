import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
from auxiliar.visualizar_prestadora import *
import plotly.express as px

st.set_page_config(page_title="Pró-Corpo - Visualizar Comissões", page_icon="💎",layout="wide")

url_parameters = st.query_params

header_1,header_2 = st.columns([3,1])

with header_1:
  st.title("Comissões:")

with header_2:
  st.image("assets/logo-topo-min.png",use_container_width=True)


if "id" in url_parameters:

  id_prestadora = st.query_params["id"]
  visualizar_prestadora(id_prestadora=id_prestadora)

else:

  st.title("Página não encontrada!")