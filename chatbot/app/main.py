# main.py
from fastapi import FastAPI

# Erstelle eine Instanz von FastAPI
app = FastAPI()

# Definiere einen Endpunkt
@app.get("/")
async def read_root():
    return {"message": "Hello, I am the chatbot!"}


@app.get("/getjoke/{topic}")
async def get_joke(topic: str):
    try:
        answer = f"Here is a joke about {topic}."
        return {"joke": answer}
    except HTTPException as e:
        return {"error": e.detail}