import logging

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load env variables
from config.base_config import rag_app_config

# Load models
from chat.chatbot import bot
from schemas.chat import ChatRequest

from sqlalchemy.orm import Session
from database.database import get_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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


@app.post(
    "/query",
    summary="Process chat query endpoint",
    response_description="Return result from processing chat query",
    status_code=200,
)
async def process_chat_query(
    request: ChatRequest, db: Session = Depends(get_db)
):
    """
    Main endpoint for the RAG service, processes a RAG query.

    Parameters
    ----------
    request: ChatRequest
        The request object containing: query, language, tags, sources, llm_model, retrieval_method, k_memory, response_style, autocomplete, rag, user_uuid, conversation_uuid parameters.

    Returns
    -------
    StreamingResponse
        The response from the chat service
    """
    logger.info(f"-----FRONTEND REQUEST: {request}")
    content = bot.process_request(db, request)

    return StreamingResponse(content, media_type="text/event-stream")
