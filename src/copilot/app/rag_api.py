import logging

from typing import List
from schemas.document import Document

from fastapi import FastAPI, status, Depends
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load env variables
from config.config import RAGConfigApp

# Load models
from rag.rag_processor import processor
from rag.models import RAGRequest

from sqlalchemy.orm import Session
from database.database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(**RAGConfigApp)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/query",
          summary="Process RAG query endpoint",
          response_description="Return result from processing RAG query",
          status_code=200)
async def process_query(request: RAGRequest, language: str = None, db: Session = Depends(get_db)):
    """
    Main endpoint for the RAG service, processes a RAG query.

    Parameters
    ----------
    request: RAGRequest
        The request object containing the query and context.
    language: str
        The language of the query.
    db: Session
        The database session.

    Returns
    -------
    StreamingResponse
        The response from the RAG processor
    """
    content = processor.process(db, request, language=language)
    return StreamingResponse(content, media_type="text/event-stream")


@app.post("/context_docs",
          summary="Retrieve context docs endpoint",
          response_description="Return context docs from semantic search",
          response_model=List[Document],
          status_code=200)
async def docs(request: RAGRequest, language: str = None, tag: str = None, k: int = 0, db: Session = Depends(get_db)):
    """
    Retrieve context documents for a given query.

    Parameters
    ----------
    request: RAGRequest
        The request object containing the query and context.
    language: str
        The language of the query.
    tag: str
        The tag of the documents to retrieve.
    k: int
        The number of documents to retrieve.
    db: Session
        The database session.

    Returns
    -------
    dict
        The retrieved documents.
    """

    return processor.retrieve(db, request, language, tag=tag, k=k)


@app.get("/rerank",
         summary="Reranking endpoint",
         response_description="Welcome Message")
async def rerank():
    """
    Dummy endpoint for retrieved docs reranking.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)
