from fastapi import FastAPI, HTTPException, Depends, status
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
from clients.client_manager import client_manager
from utils.logging import get_logger

logger = get_logger(__name__)

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
        The request object containing: query, language, tags, sources, llm_model, retrieval_method, k_memory, response_style, autocomplete, rag, user_uuid, conversation_uuid, command, command_args parameters.
    db: Session
        The database session.

    Returns
    -------
    StreamingResponse
        The response from the chat service
    """

    logger.info(f"-----FRONTEND REQUEST: {request}")
    try:
        content = bot.process_request(db, request)
        return StreamingResponse(content, media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/direct_chat")
async def direct_chat(request: ChatRequest):
    """
    Direct chat endpoint bypassing RAG for simple queries
    """
    try:
        llm_client = client_manager.get_llm_client(
            model=request.llm_model,
            runtime_overrides={
                "temperature": request.temperature,
                "top_p": request.top_p,
                "max_tokens": request.max_output_tokens,
            },
        )

        messages = [{"role": "user", "content": request.query}]
        response = await llm_client.agenerate(messages)

        return {"response": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Error in direct chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
