import logging

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Load env variables
from config.base_config import rag_config, rag_app_config
from config.network_config import CORS_ALLOWED_ORIGINS
from config.pgvector_config import SIMILARITY_METRICS

# Load utility functions
from utils.embedding import get_embedding
from utils.db import get_db_connection

# Load models
from rag_processor import *
from rag.app.models import RAGRequest, EmbeddingRequest

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI(**rag_app_config)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


processor = RAGProcessor(rag_config)


@app.post("/rag/process", summary="Process RAG query endpoint", response_description="Return result from processing RAG query", status_code=200)
async def process_query(request: RAGRequest):

    json_response = await processor.fetch_context_docs(request.query)
    context_docs = json_response['contextDocs']
    source_url = json_response['sourceUrl']
    messages = processor.create_openai_message(context_docs, request.query)
    openai_stream = processor.create_openai_stream(messages)

    return StreamingResponse(processor.generate(openai_stream, source_url), media_type="text/event-stream")


@app.post("/rag/docs", summary="Retrieve context docs endpoint", response_description="Return context docs from semantic search", status_code=200)
async def docs(request: RAGRequest):

    conn = await get_db_connection()

    try:
        # Get the query embedding vector
        query_embedding = get_embedding(request.query)[0].embedding

        # Only supports retrieval of 1 document at the moment (set in /config/config.yaml). Will implement multi-doc retrieval later
        top_k = rag_config["retrieval"]["top_k"]
        similarity_metric_symbol = SIMILARITY_METRICS[similarity_metric]
        documents = await conn.fetch(f"""
            SELECT text, url,  1 - (embedding {similarity_metric_symbol} '{query_embedding}') AS similarity_metric
            FROM embeddings
            ORDER BY similarity_metric desc
            LIMIT {top_k}
        """)
        documents = [dict(row) for row in documents][0]

    finally:
        await conn.close()

    return {"contextDocs": documents["text"], "sourceUrl": documents["url"], "cosineSimilarity": documents["cosine_similarity"]}

@app.post("/rag/embed", summary="Embedding endpoint", response_description="A dictionary with embeddings for the input text")
async def embed(text_input: EmbeddingRequest):
    embedding = get_embedding(text_input.text)[0].embedding
    return {"data": embedding}

@app.get("/rag/rerank", summary="Reranking endpoint", response_description="Welcome Message")
async def rerank():
    """
    Dummy endpoint for retrieved docs reranking.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)