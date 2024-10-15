import logging

from typing import List, Optional
from schemas.document import Document

from fastapi import FastAPI, status, Depends
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load env variables
from config.base_config import rag_app_config

# Load models
from rag.rag_service import rag_service
from chat.chatbot import bot
from rag.models import RAGRequest

from sqlalchemy.orm import Session
from database.database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(**rag_app_config)

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
async def process_query(request: RAGRequest,
                        language: Optional[str] = None,
                        db: Session = Depends(get_db),
                        tag: Optional[str] = None,
                        source: Optional[str] = None,
                        llm_model: Optional[str] = None,
                        retrieval_method: Optional[List[str]] = None,
                        k_memory: Optional[int] = 1,
                        user_uuid: Optional[str] = None,
                        conversation_uuid: Optional[str] = None,):
    """
    Main endpoint for the RAG service, processes a RAG query.

    Parameters
    ----------
    request: RAGRequest
        The request object containing the query and context.
    language: Optional[str]
        The language of the query.
    db: Session
        The database session.
    tag: Optional[str]
        The tag for document retrieval.
    source: Optional[str]
        The source for document retrieval.
    llm_model: Optional[str]
        The LLM model to use from user selection.
    retrieval_method: Optional[List[str]]
        The retrieval method to use for document retrieval.
    k_memory: Optional[int]
        The number of messages to store in conversational memory.
    user_uuid: Optional[str]
        The user UUID for conversational memory/chat history.
    conversation_uuid: Optional[str]
        The conversation UUID to for conversational memory/chat history.


    Returns
    -------
    StreamingResponse
        The response from the RAG service
    """
    content = await bot.rag_service.process_request(db, request, language=language, tag=tag, source=source, user_uuid=user_uuid, conversation_uuid=conversation_uuid, llm_model=llm_model, retrieval_method=retrieval_method, k_memory=k_memory)

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
    k: int
        The number of documents to retrieve.
    db: Session
        The database session.

    Returns
    -------
    dict
        The retrieved documents.
    """

    return rag_service.retrieve(db, request, language, tag=tag, k=k)

@app.get("/rerank",
         summary="Reranking endpoint",
         response_description="Welcome Message")
async def rerank():
    """
    Dummy endpoint for retrieved docs reranking.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)
