import requests
import json
from astrapy.db import AstraDBCollection, AstraDB
import os
from dotenv import load_dotenv

load_dotenv()
# AstraDB connection information
token = os.getenv("token")
api_endpoint = os.getenv("endpoint")
collection_name = "c_link_articles"

# Names of input and output collections
in_collection_name = "c_link_articles"

# Initialize AstraDB instance and AstraDBCollection instances for input and output collections
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)
in_collection = AstraDBCollection(collection_name=in_collection_name, astra_db=astra_db)

# Initial state for pagination
nextPageState = ""

articles_to_process = 200
batch_size = 20
total_articles = 1470

for i in range(0, total_articles, batch_size):
    current_batch_size = batch_size
    batch_max = i+batch_size
    if batch_max > articles_to_process:
        current_batch_size = articles_to_process - i

    if nextPageState == "":
        data = in_collection.find()
        nextPageState = data['data']['nextPageState']
        print(nextPageState)
        if current_batch_size < batch_size:
            break
    elif nextPageState == None:
        break
    else:
        data = in_collection.find(options={"pageState":nextPageState}, sort = None)
        nextPageState = data['data']['nextPageState']
        print(nextPageState)
        if current_batch_size < batch_size:
            break
