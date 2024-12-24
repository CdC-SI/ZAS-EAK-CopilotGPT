import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from config.project_config import ProjectConfig
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
    SUPPORTED_OLLAMA_LLM_MODELS,
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
async def get_sources(db: Session = Depends(get_db)) -> List:
    """
    Endpoint to get all sources from 'source' table in postgres.
    """
    unique_urls = db.query(Source.url).distinct().all()
    return [url[0] for url in unique_urls]


async def get_sources_descriptions(db: Session = Depends(get_db)) -> Dict:
    """
    Endpoint to get all sources descriptions from 'source' table in postgres.
    """
    # TO DO: LLM call to parse user uploaded docs and add to table
    # TO DO: multilingual descriptions
    # TO DO: update source names
    sources_descriptions = {
        "rag_test_data_tags_lang_org.csv": "Les documents rag_test_data_tags_lang_org.csv contiennent toute l'information sur l'AVS/AI en général.",
        "akis.csv": "Les documents rag_test_data_tags_lang_org.csv contiennent toute l'information sur l'outil AKIS.",
    }
    return sources_descriptions


@app.get("/tags")
async def get_tags(db: Session = Depends(get_db)) -> List:
    """Get all unique tags from document table."""
    unique_tags = (
        db.query(Document.tags)
        .filter(Document.tags.isnot(None))
        .distinct()
        .all()
    )
    all_tags = set()
    for tags in unique_tags:
        if tags[0]:
            all_tags.update(tags[0])
    return sorted(all_tags)


async def get_tags_descriptions(db: Session = Depends(get_db)) -> Dict:
    """
    Endpoint to get all tags descriptions from 'tags' table in postgres.
    """
    # TO DO: multilingual descriptions
    tags_descriptions = {
        "AKIS": "Les documents AKIS contient toute l'information sur l'outil d'aide en ligne AKIS.",
        "Familienzulagen": "Les documents Familienzulagen contiennent toute l'information sur les allocations familiales.",
        "Firmen": "Les documents Firmen contiennent toute l'information sur l'AVS/AI des entreprises.",
        "Private": "Les documents Private contiennent toute l'information sur l'AVS/AI des personnes privées.",
        "Documentation": "Les documents Documentation contiennent toute l'information sur l'AVS/AI des personnes privées.",
    }
    return tags_descriptions


@app.get(
    "/llm_models",
    summary="Get llm models list",
    response_description="Return a list of llm models",
    status_code=200,
)
async def get_llm_models() -> List:
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
        llm_models.extend(SUPPORTED_OLLAMA_LLM_MODELS)

    return llm_models


@app.get(
    "/retrieval_methods",
    summary="Get retrieval_methods list",
    response_description="Return a list of retrieval methods",
    status_code=200,
)
async def get_retrieval_methods() -> List:
    """
    Endpoint to get all supported retrieval methods.
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


@app.get(
    "/response_style",
    summary="Get response style list",
    response_description="Return a list of response styles",
    status_code=200,
)
async def get_response_style() -> List:
    """
    Endpoint to get all supported response_styles.
    """
    response_styles = ["concise", "detailed", "plain", "easy", "legal"]
    return response_styles


@app.get(
    "/response_format",
    summary="Get response format list",
    response_description="Return a list of response formats",
    status_code=200,
)
async def get_response_format() -> List:
    """
    Endpoint to get all supported response_formats.
    """
    response_formats = ["condensed", "complete"]
    return response_formats


@app.get(
    "/authorized_commands",
    summary="Get list of authorized commands",
    response_description="Return a list of authorized commands",
    status_code=200,
)
async def get_authorized_commands() -> List:
    """
    Endpoint to get all supported authorized commands.
    """
    authorized_commands = ["/summarize", "/translate"]
    return authorized_commands


@app.get(
    "/project_version",
    summary="Get project version",
    response_description="Return project version",
    status_code=200,
)
async def get_project_version() -> List[str]:
    """
    Endpoint to get project version.
    """
    # project_version = {
    #     "version": ProjectConfig.PYTHON_PROJECT_VERSION.value,
    #     "repository_url": ProjectConfig.REPOSITORY_URL.value,
    #     "release_date": ProjectConfig.RELEASE_DATE.value,
    # }
    # return [project_version]
    return [ProjectConfig.PYTHON_PROJECT_VERSION.value]
