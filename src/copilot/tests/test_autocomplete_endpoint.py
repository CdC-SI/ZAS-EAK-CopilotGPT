import requests
from pydantic import BaseModel
from typing import List, Optional


class AutocompleteRequest(BaseModel):
    question: str
    language: Optional[str] = None
    tag: Optional[List[str]] = None
    k: Optional[int] = 5


url = "http://localhost:8000/apy/autocomplete"

language = "de"
tags = ["Familienzulagen"]
k = 5

question = "wann"

data = AutocompleteRequest(
    question=question, language=language, tags=tags, k=k
).dict()

response = requests.get(url, params=data)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode("utf-8"), end="", flush=True)
else:
    print(f"Error: {response.status_code} - {response.text}")
