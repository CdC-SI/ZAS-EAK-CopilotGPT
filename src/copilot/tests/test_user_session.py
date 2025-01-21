import sys
import requests

sys.path.append("../app")

from schemas.chat import ChatRequest

url = "http://localhost:8000/apy/v1/chat/query"

user_uuid = "dc5d516a-b93a-4085-b37c-094ef8da2fb4"
conversation_uuid = "a90a6103-2092-4e08-8cb9-bea9396ec333"
# Note: set language param when data is indexed with language
language = "fr"
tags = ["Familienzulagen", "Allgemeines"]
source = ["AHV_Lernbaustein_2024.csv"]
organization = "EAK"
llm_model = "gpt-4o-2024-05-13"
retrieval_method = ["top_k_retriever", "reranking"]
k_retrieve = 5
k_memory = 5
response_style = None
command = "/summarize"
command_args = ["last"]
autocomplete = True
rag = True

query = "Que signifie l'âge de la retraite flexible ? "

data = ChatRequest(
    query=query,
    language=language,
    # tags=tags,
    # source=source,
    organization=organization,
    llm_model=llm_model,
    retrieval_method=retrieval_method,
    k_retrieve=k_retrieve,
    # k_memory=k_memory,
    # command=command,
    # command_args=command_args,
    user_uuid=user_uuid,
    conversation_uuid=conversation_uuid,
    # autocomplete=autocomplete,
    # rag=rag,
).dict()

response = requests.post(url, json=data, stream=True)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode("utf-8"), end="", flush=True)
else:
    print(f"Error: {response.status_code} - {response.text}")
