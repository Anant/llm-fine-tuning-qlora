import requests
import json
from bs4 import BeautifulSoup
from astrapy.db import AstraDBCollection, AstraDB
from langchain_openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
# AstraDB connection information
token = os.getenv("token")
api_endpoint = os.getenv("endpoint")
collection_name = "c_link_articles"

# API endpoint URL
url = "http://167.172.142.105:5000/api/elasticsearch/leaves_articles/_search"
headers = {'Content-Type': 'application/json'}


# Initialize AstraDB instance
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)

# Check if collection exists and create if not
if collection_name in astra_db.get_collections()['status']['collections']:
    print(f"Collection '{collection_name}' already exists. New collection not created")
else:
    astra_db.create_collection(collection_name=collection_name)

# Initialize AstraDBCollection instance
collection = AstraDBCollection(collection_name=collection_name, astra_db=astra_db)

def gen_request_body(batch_size=20, start_index=0):
    """
    Generates the request body for the API request.

    Args:
        batch_size (int, optional): The batch size of articles. Defaults to 20.
        start_index (int, optional): The starting index of articles. Defaults to 0.

    Returns:
        str: JSON string representing the request body.
    """
    return json.dumps({"size": int(batch_size), "from": int(start_index)})

def get_total_articles():
    """
    Retrieves the total number of articles from the API.

    Returns:
        int: Total number of articles.
    """
    response = requests.request("POST", url, headers=headers, data=gen_request_body())
    return int(response.json()['hits']['total'])

def shred_article(article, char_limit=6500):
    """
    Splits the given article into smaller chunks.

    Args:
        article (str): The article text.
        char_limit (int, optional): The character limit for each chunk. Defaults to 6500.

    Returns:
        list: A list of strings representing the split article chunks.
    """
    len_article = len(article)
    result = []
    for i in range(0, len_article, char_limit):
        result.append(article[i:(i+char_limit)])
    return result

total_articles = get_total_articles()
batch_size = 20
empty_articles = 0

# Iterate over articles in batches
for i in range(0, total_articles, batch_size):
    # Make API request to fetch articles
    response = requests.request("POST", url, headers=headers, data=gen_request_body(batch_size, i))
    articles = []

    # Process each article in the response
    for article in response.json()['hits']['hits']:
        if 'content' in article['_source']:
            # Shred the article into smaller chunks
            articles.append({"content": shred_article(BeautifulSoup(article['_source']['content'], 'html.parser').get_text(separator=" \n "))})

    # Insert shredded articles into AstraDB collection
    results = collection.insert_many(documents=articles)
    inserted_articles = len(results['status']['insertedIds'])
    empty_articles = empty_articles + (batch_size - inserted_articles)
    print(results)
    print(f"Articles {str(i)} to {str(i+len(articles))} uploaded.")

print(f"{str(empty_articles)} empty articles found of {str(total_articles)}")