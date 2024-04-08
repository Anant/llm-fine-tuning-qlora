# Import required python packages
from astrapy.db import AstraDBCollection, AstraDB
from datasets import Dataset
from pprint import pprint
import pandas as pd
import requests
import json
from openai import OpenAI
import ftfy
import evaluation_prompts
import re
import os
from dotenv import load_dotenv

load_dotenv()
# AstraDB connection information
token = os.getenv("token")
endpoint = os.getenv("endpoint")

collection_name = "test_instructions"
astra_db = AstraDB(token=token, api_endpoint=endpoint)
collection = AstraDBCollection(collection_name=collection_name, astra_db=astra_db)

# API key for OpenAI
OPENAI_API_KEY = os.getenv("openai_key")

# Client for OpenAI API
client = OpenAI(api_key = OPENAI_API_KEY)

nextPageState = ""
raw_dataset = []
expected_columns = ['_id','instruction', 'input', 'output', 'original_response', 'fine_tuned_response']

def check_expected_columns(raw_instruction):
    if all(column in raw_instruction for column in expected_columns):
        return True
    else:
        return False

while nextPageState != None:
    if nextPageState == "":
        data = collection.find()
        nextPageState = data['data']['nextPageState']
        raw_instructions = [instruction for instruction in data['data']['documents'] if check_expected_columns(instruction)]
        raw_dataset.extend(raw_instructions)
    else:
        data = collection.find(options={"pageState":nextPageState}, sort = None)
        nextPageState = data['data']['nextPageState']
        raw_instructions = [instruction for instruction in data['data']['documents'] if check_expected_columns(instruction)]
        raw_dataset.extend(raw_instructions)

# Turns separated instruction dicts from Astra into a dataset of combined instructions
def create_prompts(record):
    start = "Read the Instruction below and provide an answer."
    question = f"### INSTRUCTION:\n{record['instruction']}\n\n"
    response = f"### Context:\n{record['input']}\n"
    original_answer = f"### Response:\n {record['original_response']}\n\n"
    fine_tuned_answer = f"### Response:\n {record['fine_tuned_response']}\n\n"
    end = "### End"

    original_parts = [part for part in [start, question, response, original_answer, end] if part]
    fine_tuned_parts = [part for part in [start, question, response, fine_tuned_answer, end] if part]

    original_formatted_prompt = "\n\n".join(original_parts).replace('\\n', '\n')
    fine_tuned_formatted_prompt = "\n\n".join(fine_tuned_parts).replace('\\n', '\n')

    record["original_text"] = original_formatted_prompt
    record["fine_tuned_text"] = fine_tuned_formatted_prompt

    return record

combined_dataset = list(map(create_prompts, raw_dataset))

dataframe = pd.DataFrame(data=combined_dataset, dtype='string')
dataframe.info()
dataset = Dataset.from_pandas(dataframe)

idx_min = 0
idx_max = 500
partial_dataset = dataset.filter(lambda example, idx: idx >= idx_min and idx < idx_max, with_indices=True)

def generate_rating( instruction_and_response):
    prompt = evaluation_prompts.evaluation_prompt + "\n" + instruction_and_response
    response = client.chat.completions.create(
            model = "gpt-3.5-turbo-0125",
            messages = [
                {"role": "system", "content": evaluation_prompts.system_prompt},
                { "role": "user", "content": prompt }
            ]
        )
    return response

for row in partial_dataset:
    original_rating = int(re.sub('\\D', '', generate_rating(row['original_text']).choices[0].message.content)[0])
    fine_tuned_rating = int(re.sub('\\D', '', generate_rating(row['fine_tuned_text']).choices[0].message.content)[0])
    #print(original_rating)
    #print(fine_tuned_rating)
    print("Original: "+str(original_rating)+"\t Fine Tuned: "+str(fine_tuned_rating))
    collection.update_one(
      filter={"_id": row['_id']},
      update={"$set": {"original_response": original_rating,
                     "fine_tuned_response": fine_tuned_rating}},
    )