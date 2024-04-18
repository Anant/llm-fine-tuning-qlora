import requests
import json
from astrapy.db import AstraDBCollection, AstraDB
from openai import OpenAI
import os
from dotenv import load_dotenv
import ftfy
import pprint

load_dotenv()
# AstraDB connection information
token = os.getenv("token")
api_endpoint = os.getenv("endpoint")
in_collection_name = "c_link_articles"
out_collection_name = "article_embeddings"

# API key for OpenAI
OPENAI_API_KEY = os.getenv("openai_key")

# Client for OpenAI API
client = OpenAI(api_key = OPENAI_API_KEY)

# Initialize AstraDB instance and AstraDBCollection instances for input and output collections
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)
in_collection = AstraDBCollection(collection_name=in_collection_name, astra_db=astra_db)

# Create the output collection
astra_db.create_collection(collection_name=out_collection_name, dimension=1536)
out_collection = AstraDBCollection(collection_name=out_collection_name, astra_db=astra_db)

# Initial state for pagination
nextPageState = ""

articles_to_process = 1470
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
        ids = [article['_id'] for article in data['data']['documents'][0:int(current_batch_size)]]
        articles = [article['content'] for article in data['data']['documents'][0:int(current_batch_size)]]
        #pprint.pprint([len(article) for article in articles])
        for i in range(len(articles)):
            article = articles[i]
            id = ids[i]
            for j in range(len(article)):
                snippet_text = article[j]
                embedding = client.embeddings.create( input=snippet_text, model="text-embedding-ada-002").data[0].embedding
                out_collection.insert_one(document={"$vector": embedding, "content": snippet_text, "artice_id": id, "chunk_index": j})
        print(nextPageState)
        if current_batch_size < batch_size:
            break
    elif nextPageState == None:
        break
    else:
        data = in_collection.find(options={"pageState":nextPageState}, sort = None)
        nextPageState = data['data']['nextPageState']
        ids = [article['_id'] for article in data['data']['documents'][0:int(current_batch_size)]]
        articles = [article['content'] for article in data['data']['documents'][0:int(current_batch_size)]]
        #pprint.pprint([len(article) for article in articles])
        for i in range(len(articles)):
            article = articles[i]
            id = ids[i]
            for j in range(len(article)):
                snippet_text = article[j]
                embedding = client.embeddings.create( input=snippet_text, model="text-embedding-ada-002").data[0].embedding
                out_collection.insert_one(document={"$vector": embedding, "content": snippet_text, "artice_id": id, "chunk_index": j})
        print(nextPageState)
        if current_batch_size < batch_size:
            break