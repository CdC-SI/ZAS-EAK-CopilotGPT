import os

os.environ["HAYSTACK_TELEMETRY_ENABLED"] = (
    "False"  # disable haystack telemetry
)
os.environ["TELEMETRY_ENABLED"] = "False"  # disable langfuse telemetry

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS
from contextlib import asynccontextmanager

from indexing_api import (
    init_indexing,
    create_source_descriptions,
    app as indexing_app,
)
from autocomplete_api import app as autocomplete_app
from rag_api import app as rag_app
from conversations_api import app as conversations_app
from command_api import app as command_app
from settings_api import app as settings_app
from chat_api import app as chat_app

import logging

logger = logging.getLogger(__name__)


PREFIX = "/apy/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_indexing()
    await create_source_descriptions()
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
api.mount("/conversations", conversations_app)
api.mount("/command", command_app)
api.mount("/settings", settings_app)
api.mount("/chat", chat_app)


@api.post("/", summary="Hello", status_code=200)
async def welcome():
    """
    Dummy endpoint for testing the API.

    Returns
    -------
    str
        A welcome message.
    """
    return "Hello!"
