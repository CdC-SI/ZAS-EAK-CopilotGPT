import sys
import requests

sys.path.append("../app")

from schemas.chat import ChatRequest

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
command = "/summarize"
command_args = ["last"]
autocomplete = True
rag = True

query = "explique moi le concept du splitting"

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

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode("utf-8"), end='', flush=True)
else:
    print(f"Error: {response.status_code} - {response.text}")
