import sys
import requests

sys.path.append("../app")

from schemas.command import CommandRequest

url = "http://localhost:8000/apy/command/advanced"

input_text = "/summarize last 5"

data = CommandRequest(
    input_text=input_text,
).dict()

response = requests.post(url, json=data)

if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode("utf-8"), end="", flush=True)
else:
    print(f"Error: {response.status_code} - {response.text}")
