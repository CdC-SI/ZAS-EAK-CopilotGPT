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
from chat.chatbot import bot
from schemas.chat import ChatRequest
from rag.factory import RetrieverFactory

from sqlalchemy.orm import Session
from database.database import get_db

from memory import MemoryService
from memory.config import MemoryConfig
from config.base_config import chat_config
from chat.messages import MessageBuilder
from llm.factory import LLMFactory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

message_builder = MessageBuilder()
memory_config = MemoryConfig.from_dict(chat_config["memory"])
memory_service = MemoryService(
    memory_type=memory_config.memory_type,
    k_memory=memory_config.k_memory,
    config=memory_config.storage,
)

app = FastAPI(**rag_app_config)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/query",
    summary="Process RAG query endpoint",
    response_description="Return result from processing RAG query",
    status_code=200,
)
async def process_query(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main endpoint for the RAG service, processes a RAG query.

    Parameters
    ----------
    request: ChatRequest
        The request object containing: query, language, tags, sources, llm_model, retrieval_method, k_memory, response_style, autocomplete, rag, user_uuid, conversation_uuid parameters.

    Returns
    -------
    StreamingResponse
        The response from the RAG service
    """
    content = bot.process_request(db, request)

    return StreamingResponse(content, media_type="text/event-stream")


@app.post(
    "/context_docs",
    summary="Retrieve context docs endpoint",
    response_description="Return context docs from semantic search",
    response_model=List[Document],
    status_code=200,
)
async def docs(
    query: str,
    language: Optional[str] = "de",
    tags: Optional[List[str]] = None,
    source: Optional[List[str]] = None,
    organizations: Optional[List[str]] = ["ZAS", "EAK"],
    user_uuid: Optional[str] = "test_uuid",
    conversation_uuid: Optional[str] = "test_conversation_uuid",
    llm_model: Optional[str] = "gpt-4o",
    retrieval_method: Optional[List[str]] = ["top_k_retriever"],
    k: int = 10,
    db: Session = Depends(get_db),
):
    """
    Retrieve context documents for a given query.

    Parameters
    ----------
    request: ChatRequest
        The request object containing the query and context.
    language: str
        The language of the query.
    tags: List[str]
        The tags to filter the documents.
    k: int
        The number of documents to retrieve.
    db: Session
        The database session.

    Returns
    -------
    dict
        The retrieved documents.
    """

    tags = None if not tags or tags == [""] else tags

    conversational_memory = (
        await (
            memory_service.chat_memory.get_formatted_conversation(
                db,
                user_uuid,
                conversation_uuid,
                k,
            )
        )
    )

    llm_client = LLMFactory.get_llm_client(
        model=llm_model,
        stream=False,
        temperature=0.0,
        top_p=0.95,
        max_tokens=4096,
    )

    retriever_client = RetrieverFactory.get_retriever_client(
        retrieval_method=retrieval_method,
        llm_client=llm_client,
        message_builder=message_builder,
    )

    rows = await retriever_client.get_documents(
        db,
        query,
        language=language,
        tags=tags,
        source=source,
        organizations=organizations,
        user_uuid=user_uuid,
        k_retrieve=k,
        llm_model=llm_model,
        conversational_memory=conversational_memory,
    )

    # Return empty document with proper types instead of empty strings
    return rows if len(rows) > 0 else [Document(id=None, text="", url="")]


@app.get(
    "/rerank",
    summary="Reranking endpoint",
    response_description="Welcome Message",
)
async def rerank():
    """
    Dummy endpoint for retrieved docs reranking.
    """
    return Response(
        content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED
    )
