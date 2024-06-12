import logging

from fastapi import FastAPI, status
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Load env variables
from config.base_config import rag_app_config
from config.network_config import CORS_ALLOWED_ORIGINS

# Load models
from rag.rag_processor import *
from rag.models import RAGRequest, EmbeddingRequest

from autocomplete import autocomplete
from indexing import indexing

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create required instances
app = FastAPI(**rag_app_config)
app.mount("indexing", autocomplete.app)
app.mount("autocomplete", indexing.app)

processor = RAGProcessor()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process",
          summary="Process RAG query endpoint",
          response_description="Return result from processing RAG query",
          status_code=200)
async def process_query(request: RAGRequest):
    content = await processor.process(request)
    return StreamingResponse(content, media_type="text/event-stream")


@app.post("/docs",
          summary="Retrieve context docs endpoint",
          response_description="Return context docs from semantic search",
          status_code=200)
async def docs(request: RAGRequest, language: str = '*'):
    return await processor.retrieve(request, language)


@app.post("/embed",
          summary="Embedding endpoint",
          response_description="A dictionary with embeddings for the input text")
async def embed(text_input: EmbeddingRequest):
    return await processor.embed(text_input)


@app.get("/rerank",
         summary="Reranking endpoint",
         response_description="Welcome Message")
async def rerank():
    """
    Dummy endpoint for retrieved docs reranking.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)
