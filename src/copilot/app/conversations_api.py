import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load models
from database.models import ChatHistory, ChatTitle

from sqlalchemy.orm import Session
from database.database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

@app.get("/",
         summary="Get conversations by user_uuid",
         response_description="Return a list of conversations for a given user_uuid",
         status_code=200)
async def get_conversations(user_uuid: str = None, db: Session = Depends(get_db)):
    """
    Endpoint to get all conversations for a given user_uuid.
    If user_uuid is not provided, it will raise an HTTP 400 error.
    """
    if not user_uuid:
        raise HTTPException(status_code=400, detail="user_uuid query parameter is required.")

    results = db.query(ChatHistory).filter(ChatHistory.user_uuid == user_uuid).all()
    if not results:
        raise HTTPException(status_code=404, detail="No conversations found for user_uuid.")

    return results

@app.get("/titles",
         summary="Get chat titles by user_uuid",
         response_description="Return a list of chat titles for a given user_uuid",
         status_code=200)
async def get_chat_titles(user_uuid: str = None, db: Session = Depends(get_db)):
    """
    Endpoint to get all chat titles for a given user_uuid.
    """
    if not user_uuid:
        raise HTTPException(status_code=400, detail="user_uuid query parameter is required.")

    results = db.query(ChatTitle).filter(ChatTitle.user_uuid == user_uuid).all()
    if not results:
        raise HTTPException(status_code=404, detail="No chat titles found for user_uuid.")

    return [result.chat_title for result in results]

@app.get("/{conversation_uuid}",
         summary="Get a specific conversation by conversation_uuid",
         response_description="Return a specific conversation by its conversation_uuid",
         status_code=200)
async def get_conversation(conversation_uuid: str = None, db: Session = Depends(get_db)):
    """
    Endpoint to get a specific conversation by conversation_uuid.
    """
    if not conversation_uuid:
        raise HTTPException(status_code=400, detail="conversation_uuid query parameter is required.")

    conversation = db.query(ChatHistory).filter(ChatHistory.conversation_uuid == conversation_uuid).all()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return conversation
