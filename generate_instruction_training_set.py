import requests
import json
from astrapy.db import AstraDBCollection, AstraDB
from openai import OpenAI
import ftfy
import instruction_prompts
import re
import os
from dotenv import load_dotenv

load_dotenv()
# AstraDB connection information
token = os.getenv("token")
api_endpoint = os.getenv("endpoint")
collection_name = "c_link_articles"

# API key for OpenAI
OPENAI_API_KEY = os.getenv("openai_key")

# Client for OpenAI API
client = OpenAI(api_key = OPENAI_API_KEY)

# Names of input and output collections
in_collection_name = "c_link_articles"
out_collection_name = "instructions"

# Initialize AstraDB instance and AstraDBCollection instances for input and output collections
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)
in_collection = AstraDBCollection(collection_name=in_collection_name, astra_db=astra_db)

# Create the output collection
astra_db.create_collection(collection_name=out_collection_name)
out_collection = AstraDBCollection(collection_name=out_collection_name, astra_db=astra_db)

# Initial state for pagination
nextPageState = ""

def get_instruction_types(article):
    """
    Retrieves the instruction types for a given article.

    Args:
        article (str): The article for which instruction types need to be fetched.

    Returns:
        response: The response object containing the instruction types.
    """
    prompt = instruction_prompts.outer_prompt + article
    response = client.chat.completions.create(
            model = "gpt-4-0125-preview",
            messages = [ { "role": "user", "content": prompt, } ]
            )
    return response

def extract_numbers(instruction_types_response):
    """
    Extracts the instruction types as numbers from the response.

    Args:
        instruction_types_response (response): The response object from get_instruction_types function.

    Returns:
        list: A list of instruction types as numbers.
    """
    instruction_types_string = instruction_types_response.choices[0].message.content
    instruction_types_split_string = [re.sub('\D', '', section) for section in instruction_types_string.split(".")]
    instruction_types_numbers_1 = [int(number) for number in instruction_types_split_string if number]
    instruction_types_numbers_2 = [ number for number in instruction_types_numbers_1 if number <= 14]
    return instruction_types_numbers_2

def generate_instruction( instruction_number, article):
    """
    Generates an instruction based on the instruction number and article.

    Args:
        instruction_number (int): The number of the instruction type.
        article (str): The article for which the instruction is generated.

    Returns:
        response: The response object containing the generated instruction.
    """
    instruction = instruction_prompts.inner_prompt_list[instruction_number - 1]
    prompt = instruction + instruction_prompts.article_header + article + instruction_prompts.output_format_block
    response = client.chat.completions.create(
            model = "gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            messages = [
                {"role": "system", "content": instruction_prompts.system_prompt},
                { "role": "user", "content": prompt }
            ]
        )
    return response

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
        ids = [article['_id'] for article in data['data']['documents'][0:int(current_batch_size)]]
        articles = [ftfy.fix_text("".join(article['content'])) for article in data['data']['documents'][0:int(current_batch_size)]]
        instruction_types_list = [get_instruction_types(article) for article in articles]
        instruction_types_numbers = [extract_numbers(instruction) for instruction in instruction_types_list]
        print(instruction_types_numbers)
        for j in range(len(instruction_types_numbers)):
            if instruction_types_numbers[j] != []:
                article_instructions = [json.loads(ftfy.fix_text(generate_instruction(instruction_type_number, articles[j]).choices[0].message.content)) for instruction_type_number in instruction_types_numbers[j]]
                [article_instruction.update({"article_id": ids[j]}) for article_instruction in article_instructions]
                response = out_collection.insert_many(documents=article_instructions,partial_failures_allowed=True)
                print(response)
        if current_batch_size < batch_size:
            break
    elif nextPageState == None:
        break
    else:
        data = in_collection.find(options={"pageState":nextPageState}, sort = None)
        nextPageState = data['data']['nextPageState']
        ids = [article['_id'] for article in data['data']['documents'][0:int(current_batch_size)]]
        articles = [ftfy.fix_text("".join(article['content'])) for article in data['data']['documents'][0:int(current_batch_size)]]
        instruction_types_list = [get_instruction_types(article) for article in articles]
        instruction_types_numbers = [extract_numbers(instruction) for instruction in instruction_types_list]
        print(instruction_types_numbers)
        for j in range(len(instruction_types_numbers)):
            if instruction_types_numbers[j] != []:
                article_instructions = [json.loads(ftfy.fix_text(generate_instruction(instruction_type_number, articles[j]).choices[0].message.content)) for instruction_type_number in instruction_types_numbers[j]]
                [article_instruction.update({"article_id": ids[j]}) for article_instruction in article_instructions]
                response = out_collection.insert_many(documents=article_instructions,partial_failures_allowed=True)
                print(response)
        if current_batch_size < batch_size:
            break
