from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.network_config import CORS_ALLOWED_ORIGINS

from indexing_api import app as indexing_app, index_faq_data, index_rag_vectordb, index_faq_vectordb
from autocomplete_api import app as autocomplete_app
from rag_api import app as rag_app

from config.base_config import indexing_config
from utils.db import check_db_connection

import logging
logger = logging.getLogger(__name__)


PREFIX = "/apy"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection(retries=10, delay=10)

    if indexing_config["faq"]["auto_index"]:
        # With dev-mode, only index sample FAQ data
        if indexing_config["dev_mode"]:
            try:
                logger.info("Auto-indexing sample FAQ data")
                await index_faq_vectordb()
            except Exception as e:
                logger.error("Dev-mode: Failed to index sample FAQ data: %s", e)
        # If dev-mode is deactivated, scrap and index all bsv.admin.ch FAQ data
        else:
            try:
                logger.info("Auto-indexing bsv.admin.ch FAQ data")
                await index_faq_data()
            except Exception as e:
                logger.error("Failed to index bsv.admin.ch FAQ data: %s", e)

    if indexing_config["rag"]["auto_index"]:
        # With dev-mode, only index sample data
        if indexing_config["dev_mode"]:
            try:
                logger.info("Auto-indexing sample RAG data")
                await index_rag_vectordb()
            except Exception as e:
                logger.error("Failed to index sample RAG data: %s", e)
        # If dev-mode is deactivated, scrap and index all RAG data (NOTE: Will be implemented soon.)
        else:
            raise NotImplementedError("Feature is not implemented yet.")

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
    return "Hello!"
