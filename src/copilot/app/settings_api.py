import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi.middleware.cors import CORSMiddleware

from config.project_config import ProjectConfig
from config.network_config import CORS_ALLOWED_ORIGINS
from database.database import get_db
from database.models import Source, Document, Tag
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
    "/organization",
    summary="Get organizations list",
    response_description="Return a list of organizations",
    status_code=200,
)
async def get_organizations(db: Session = Depends(get_db)) -> List[str]:
    """
    Endpoint to get all organizations.
    """
    return ["ZAS", "EAK"]


@app.get("/sources")
async def get_sources(
    db: Session = Depends(get_db),
    user_uuid: str = None,
    organizations: str = None,
) -> List:
    """
    Endpoint to get all sources from 'source' table in postgres filtered by user's documents and organizations.
    Access rules:
    - Include documents owned by the user (user_uuid match)
    - Include organization documents (user_uuid is NULL and organization matches)
    - Include public documents (user_uuid is NULL and organizations is NULL)
    """

    org_list = (
        [org.strip() for org in organizations.split(",")]
        if organizations
        else None
    )

    # Base query for document source_id
    query = db.query(Document.source_id).distinct()

    filters = []

    # User's personal documents
    if user_uuid:
        filters.append(Document.user_uuid == user_uuid)

    # Organizational/public documents (must have NULL user_uuid)
    org_filters = [Document.user_uuid.is_(None)]
    if org_list:
        org_filters.append(
            Document.organizations.op("&&")(org_list)
            | Document.organizations.is_(None)
        )
    else:
        org_filters.append(Document.organizations.is_(None))

    filters.append(and_(*org_filters))

    # Combine all filters with OR
    query = query.filter(or_(*filters))

    source_ids = query.all()

    # Get matching sources
    sources = (
        db.query(Source)
        .filter(Source.id.in_([sid[0] for sid in source_ids]))
        .distinct()
        .all()
    )

    return [source.url for source in sources]


@app.get(
    "/sources/descriptions",
    summary="Get source descriptions from postgres 'source' table",
    response_description="Return a list of source descriptions",
    status_code=200,
)
async def get_source_descriptions(db: Session = Depends(get_db)) -> List[Dict]:
    """
    Endpoint to get all sources descriptions from 'source' table in postgres.
    """
    source_descriptions = (
        db.query(Source.url, Source.description).distinct().all()
    )
    return [
        {"url": source.url, "description": source.description}
        for source in source_descriptions
    ]


@app.get("/tags")
async def get_tags(
    db: Session = Depends(get_db),
    user_uuid: str = None,
    organizations: str = None,
) -> List:
    """
    Get all unique tags from document table with access control.
    Access rules:
    - Include tags from documents owned by the user (user_uuid match)
    - Include tags from organization documents (user_uuid is NULL and organization matches)
    - Include tags from public documents (user_uuid is NULL and organizations is NULL)
    """

    # Parse organizations
    org_list = (
        [org.strip() for org in organizations.split(",")]
        if organizations
        else None
    )

    # Base query for documents with tags
    query = db.query(Document.tags, Document.organizations).filter(
        Document.tags.isnot(None)
    )

    filters = []

    # User's personal documents
    if user_uuid:
        filters.append(Document.user_uuid == user_uuid)

    # Organizational/public documents (must have NULL user_uuid)
    if org_list:
        # Only get documents where:
        # - user_uuid is NULL AND
        # - (organizations array contains ANY of our org_list OR organizations is NULL)
        org_filter = and_(
            Document.user_uuid.is_(None),
            or_(
                *[Document.organizations.any(org) for org in org_list],
                Document.organizations.is_(None),
            ),
        )
        filters.append(org_filter)
    else:
        # If no organizations specified, only get public documents
        filters.append(
            and_(
                Document.user_uuid.is_(None), Document.organizations.is_(None)
            )
        )

    # Apply filters with OR logic
    query = query.filter(or_(*filters))
    results = query.distinct().all()

    # Remove duplicates
    all_tags = set()
    for tags, _ in results:
        if tags:
            all_tags.update(tags)

    return all_tags


@app.get("/tags/description")
async def get_tags_descriptions(
    db: Session = Depends(get_db), language: str = None
) -> List:
    """
    Endpoint to get all tags descriptions from 'tags' table in postgres based on language.
    """
    # TO DO: semantic search on tag description embeddings by language (embed all language descriptions of description col)

    tags_descriptions = db.query(Tag).filter(Tag.language == language).all()

    # tags_descriptions = {
    #     "AKIS": "Les documents AKIS contient toute l'information sur l'outil d'aide en ligne AKIS.",
    #     "Familienzulagen": "Les documents Familienzulagen contiennent toute l'information sur les allocations familiales.",
    #     "Firmen": "Les documents Firmen contiennent toute l'information sur l'AVS/AI des entreprises.",
    #     "Private": "Les documents Private contiennent toute l'information sur l'AVS/AI des personnes privées.",
    #     "Documentation": "Les documents Documentation contiennent toute l'information sur l'AVS/AI des personnes privées.",
    # }
    return [(tag.tag_en, tag.description) for tag in tags_descriptions]


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
