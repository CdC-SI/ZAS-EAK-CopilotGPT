import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

# Load env variables
from config.base_config import rag_config
from config.network_config import CORS_ALLOWED_ORIGINS

# Load utility functions
from utils.embedding import get_embedding
from utils.db import get_db_connection

# Load models
from rag.app.models import RAGRequest, EmbeddingRequest

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/rag/docs", summary="Retrieve context docs endpoint", response_description="Return context docs from semantic search", status_code=200)
async def docs(request: RAGRequest):

    conn = await get_db_connection()

    try:

        # Make POST request to the RAG service to get the question embedding
        async with httpx.AsyncClient() as client:
            response = await client.post("http://rag:8010/rag/embed", json={"text": request.query})

        # Ensure the request was successful
        response.raise_for_status()

        # Get the resulting embedding vector from the response
        query_embedding = response.json()["data"][0]["embedding"]

        # Only supports retrieval of 1 document at the moment (set in /config/config.yaml). Will implement multi-doc retrieval later
        top_k = rag_config["retrieval"]["top_k"]
        similarity_metric = rag_config["retrieval"]["metric"]
        docs = await conn.fetch(f"""
            SELECT text, url,  1 - (embedding <=> '{query_embedding}') AS {similarity_metric}
            FROM embeddings
            ORDER BY {similarity_metric} desc
            LIMIT $1
        """, top_k)
        docs = [dict(row) for row in docs][0]

    except Exception as e:
        await conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn:
            await conn.close()

    return {"contextDocs": docs["text"], "sourceUrl": docs["url"], "cosineSimilarity": docs["cosine_similarity"]}

@app.post("/rag/embed", summary="Embedding endpoint", response_description="A dictionary with embeddings for the input text")
async def embed(text_input: EmbeddingRequest):
    try:
        embedding = get_embedding(text_input.text)
        return {"data": embedding}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/rerank", summary="Reranking endpoint", response_description="Welcome Message")
async def rerank():
    """
    Dummy endpoint for retrieved docs reranking.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)