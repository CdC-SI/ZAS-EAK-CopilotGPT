from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

from indexing_api import app as indexing_app
from autocomplete_api import app as autocomplete_app
from rag_api import app as rag_app

PREFIX = ""  # "/api"

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI()
app.mount(PREFIX, api)

api.mount("/indexing", indexing_app)
api.mount("/autocomplete", autocomplete_app)
api.mount("/rag", rag_app)


@api.post("/",
          summary="Hello",
          status_code=200)
async def welcome():
    return "Hello!"
