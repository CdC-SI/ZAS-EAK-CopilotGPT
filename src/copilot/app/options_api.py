import os
from dotenv import load_dotenv
import logging

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS
from database.database import get_db
from database.models import Source, Document
from config.llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GEMINI_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
    SUPPORTED_MLX_LLM_MODELS,
    SUPPORTED_LLAMACPP_LLM_MODELS,
)

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/sources",
    summary="Get sources from postgres 'source' table",
    response_description="Return a list of sources",
    status_code=200,
)
async def get_sources(db: Session = Depends(get_db)):
    """
    Endpoint to get all sources from 'source' table in postgres.
    """
    unique_urls = db.query(Source.url).distinct().all()
    return [url[0] for url in unique_urls]


@app.get(
    "/tags",
    summary="Get tags from postgres 'document' table",
    response_description="Return a list of tags",
    status_code=200,
)
async def get_tags(db: Session = Depends(get_db)):
    """
    Endpoint to get all sources from 'source' table in postgres.
    """
    unique_tags = db.query(Document.tag).distinct().all()
    return [tag[0] for tag in unique_tags]


@app.get(
    "/llm_models",
    summary="Get llm models list",
    response_description="Return a list of llm models",
    status_code=200,
)
async def get_llm_models():
    """
    Endpoint to get all supported llm_models from config.
    """
    llm_models = []

    if os.environ.get("OPENAI_API_KEY", None):
        llm_models.extend(SUPPORTED_OPENAI_LLM_MODELS)
    if os.environ.get("AZUREOPENAI_API_KEY", None):
        llm_models.extend(SUPPORTED_AZUREOPENAI_LLM_MODELS)
    if os.environ.get("ANTHROPIC_API_KEY", None):
        llm_models.extend(SUPPORTED_ANTHROPIC_LLM_MODELS)
    if os.environ.get("GEMINI_API_KEY", None):
        llm_models.extend(SUPPORTED_GEMINI_LLM_MODELS)
    if os.environ.get("GROQ_API_KEY", None):
        llm_models.extend(SUPPORTED_GROQ_LLM_MODELS)
    if os.environ.get("LLM_GENERATION_ENDPOINT", None):
        llm_models.extend(SUPPORTED_MLX_LLM_MODELS)
        llm_models.extend(SUPPORTED_LLAMACPP_LLM_MODELS)

    return llm_models


@app.get(
    "/retrieval_methods",
    summary="Get retrieval_methods list",
    response_description="Return a list of retrieval methods",
    status_code=200,
)
async def get_retrieval_methods():
    """
    Endpoint to get all supported retrieval methods from config.
    """
    retrieval_methods = [
        "top_k_retriever",
        "query_rewriting_retriever",
        "contextual_compression_retriever",
        "rag_fusion_retriever",
        "bm25",
        "reranking",
    ]
    return retrieval_methods
