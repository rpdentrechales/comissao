import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from auxiliar.auxiliar import *
from auxiliar.visualizar_prestadora import *
import plotly.express as px

st.set_page_config(page_title="Pró-Corpo - Visualizar Comissões", page_icon="💎",layout="wide")

url_parameters = st.query_params

if "reset_cache" in st.session_state:
  reset_cache = st.session_state["reset_cache"]
else:
  reset_cache = 0
  st.session_state["reset_cache"] = reset_cache

if "id" in url_parameters:

  id_prestadora = st.query_params["id"]
  
  visualizar_prestadora(id_prestadora=id_prestadora)

else:
  
  st.write("Página não encontrada!")