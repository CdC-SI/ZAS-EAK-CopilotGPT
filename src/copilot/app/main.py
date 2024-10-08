from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS
from contextlib import asynccontextmanager

from indexing_api import init_indexing, app as indexing_app
from autocomplete_api import app as autocomplete_app
from rag_api import app as rag_app
from session_api import app as session_app

import logging
logger = logging.getLogger(__name__)


PREFIX = "/apy"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_indexing()
    yield

app = FastAPI(lifespan=lifespan)
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
api.mount("/session", session_app)

@api.post("/",
          summary="Hello",
          status_code=200)
async def welcome():
    """
    Dummy endpoint for testing the API.

    Returns
    -------
    str
        A welcome message.
    """
    return "Hello!"
