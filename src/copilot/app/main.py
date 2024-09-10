from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS
from contextlib import asynccontextmanager

from indexing_api import app as indexing_app
from indexing.from_csv import init_indexing
from autocomplete_api import app as autocomplete_app
from rag_api import app as rag_app

import yaml
from config.config import RUNNING_CONFIG_PATH

import logging
logger = logging.getLogger(__name__)


PREFIX = "/apy"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_indexing()
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


@api.get("/config",
         summary="Get configuration of the app",
         status_code=200)
async def get_config():
    """
    Get the configuration of the app.

    Returns
    -------
    dict
    """
    with open(RUNNING_CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    return config
