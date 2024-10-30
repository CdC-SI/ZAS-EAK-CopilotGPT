import sys
import requests
from pydantic import BaseModel
from typing import List, Optional

sys.path.append("../app")
from config.base_config import rag_config
from config.base_config import chat_config

class ChatRequest(BaseModel):
    query: str
    language: Optional[str] = None
    tag: Optional[List[str]] = None
    source: Optional[List[str]] = None
    llm_model: Optional[str] = rag_config["llm"]["model"]
    retrieval_method: Optional[List[str]] = rag_config["retrieval"]["retrieval_method"]
    k_retrieve: Optional[int] = rag_config["retrieval"]["top_k"]
    k_memory: Optional[int] = chat_config["memory"]["k_memory"]
    response_style: Optional[str] = None
    command: Optional[str] = None
    command_args: Optional[List[str]] = None
    autocomplete: Optional[bool] = None
    rag: Optional[bool] = None
    user_uuid: Optional[str] = None
    conversation_uuid: Optional[str] = None

url = "http://localhost:8000/apy/rag/query"

user_uuid = "04001f7b-224b-47ae-8fdf-9e9135255cdG"
conversation_uuid = "a90a6103-2092-4e08-8cb9-bea9396ec420"
# Note: set language param when data is indexed with language
language = "fr"
tag = ["Familienzulagen", "Allgemeines"]
source = ["AHV_Lernbaustein_2024.csv"]
llm_model = "gpt-4o-2024-05-13"
retrieval_method = ["top_k_retriever", "reranking"]
k_memory = 5
response_style = None
#command = "/summarize"
#command_args = ["last"]
autocomplete = True
rag = True

#query = "explique moi le concept du splitting"
query = "donne moi des détails sur gilles jobin reset"
#query = "hallo"
#query = "Wie erfolgt die Koordination zwischen der Mutterschaftsentschädigung nach Bundesrecht und der kantonalen Mutterschaftszulage?"
#query = "Je suis invalide à 45%, combien de rente ai-je droit ? réponse en une phrase !!!"

data = ChatRequest(
    query=query,
    #language=language,
    tag=tag,
    #source=source,
    llm_model=llm_model,
    retrieval_method=retrieval_method,
    #k_memory=k_memory,
    #command=command,
    #command_args=command_args,
    user_uuid=user_uuid,
    conversation_uuid=conversation_uuid,
    #autocomplete=autocomplete,
    #rag=rag,
    ).dict()

# data = ChatRequest(
#     query=query,
#     language=language,
#     tag=tag,
#     source=source,
#     llm_model=llm_model,
#     retrieval_method=retrieval_method,
#     k_memory=k_memory,
#     response_style=response_style,
#     autocomplete=autocomplete,
#     rag=rag,
#     user_uuid=user_uuid,
#     conversation_uuid=conversation_uuid
#     ).dict()

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode("utf-8"), end='', flush=True)
else:
    print(f"Error: {response.status_code} - {response.text}")
