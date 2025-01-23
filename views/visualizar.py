import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
from auxiliar.visualizar_prestadora import *
import plotly.express as px

st.set_page_config(page_title="Pró-Corpo - Visualizar Comissões", page_icon="💎",layout="wide")

url_parameters = st.query_params

if "id" in url_parameters:

  id_prestadora = st.query_params["id"]
  
  visualizar_prestadora(id_prestadora=id_prestadora)

else:

  st.title("Página não encontrada!")