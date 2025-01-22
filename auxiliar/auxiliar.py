from pymongo import MongoClient, UpdateOne
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import hashlib

@st.cache_data
def get_dataframe_from_mongodb(collection_name, database_name, query={},reset_cache=None):

    client = MongoClient(f"mongodb+srv://rpdprocorpo:iyiawsSCfCsuAzOb@cluster0.lu6ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client[database_name]
    collection = db[collection_name]

    data = list(collection.find(query))

    if data:
        dataframe = pd.DataFrame(data)
        if '_id' in dataframe.columns:
            dataframe = dataframe.drop(columns=['_id'])
    else:
        dataframe = pd.DataFrame()

    return dataframe

def upload_dataframe_to_mongodb(collection_name, database_name, dataframe, unique_keys):

    print(f"Uploading data to {database_name} : {collection_name}")
    client = MongoClient(f"mongodb+srv://rpdprocorpo:iyiawsSCfCsuAzOb@cluster0.lu6ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client[database_name]
    collection = db[collection_name]

    bulk_operations = []

    for _, row in dataframe.iterrows():
        item = row.to_dict()
        # Create a composite query using the unique keys
        query = {key: item[key] for key in unique_keys}
        update = {"$set": item}
        bulk_operations.append(UpdateOne(query, update, upsert=True))

    if bulk_operations:
        result = collection.bulk_write(bulk_operations)
        results = {
            "inserted": result.upserted_count,
            "updated": result.modified_count,
            "matched": result.matched_count,
        }
    else:
        results = {"inserted": 0, "updated": 0, "matched": 0}

    print(f"Upload results: {database_name} : {collection_name} - {results}")

    return results


def convert_name_to_id(name):
  id = hashlib.md5(name.encode()).hexdigest()[:12]
  return id

def plot_bar_graph(df, y_axis_column,title):

  df['Data'] = pd.to_datetime(df['Data'])
  df['formatted_date'] = df['Data'].dt.strftime('%d/%m/%Y')

  fig = px.bar(
      df,
      x='formatted_date',
      y=y_axis_column,
      title=title,
      labels={'formatted_date': 'Dia', y_axis_column: y_axis_column}  # Axis labels
  )

  fig.update_xaxes(tickangle=-45)  # Rotate x-axis labels

  return fig
