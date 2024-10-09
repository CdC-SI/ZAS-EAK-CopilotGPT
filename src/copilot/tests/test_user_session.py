import requests
from pydantic import BaseModel

class RAGRequest(BaseModel):
    query: str

url = "http://localhost:8000/apy/rag/query"

user_uuid = "04001f7b-224b-47ae-8fdf-9e9135255cdA"
conversation_uuid = "a90a6103-2092-4e08-8cb9-bea9396ec496"
# Note: set language param when data is indexed with language
language = None
llm_model = "gpt-4o-2024-05-13"
retrieval_method = ["top_k_retriever", "reranking"]
k_memory = 5

query = "Come si puo verificare se lo splitting è stato effettuato?"

data = {
        "request": RAGRequest(query=query).dict(),
        "retrieval_method": retrieval_method
        }

params = {
    "language": language,
    "tag": "Allgemeines",
    "user_uuid": user_uuid,
    "conversation_uuid": conversation_uuid,
    "llm_model": llm_model,
    "k_memory": k_memory,
}

response = requests.post(url, json=data, params=params, stream=True)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode("utf-8"), end='', flush=True)
else:
    print(f"Error: {response.status_code} - {response.text}")
