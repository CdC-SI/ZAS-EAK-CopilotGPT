import logging

from fastapi import FastAPI, Depends
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

@app.get("/get_chat_history",
          summary="Get chat history endpoint",
          response_description="Return a list of chat history objects for a given conversation_uuid",
          status_code=200)
async def get_chat_history(conversation_uuid: str, db: Session = Depends(get_db)):
    """
    Endpoint to get chat history for a given conversation_uuid.
    """
    results = db.query(ChatHistory).filter(ChatHistory.conversation_uuid == conversation_uuid).all()
    return results

@app.get("/get_chat_titles",
          summary="Get chat title endpoint",
          response_description="Return a list of chat titles for a given user_uuid",
          status_code=200)
async def get_chat_titles(user_uuid: str, db: Session = Depends(get_db)):
    """
    Endpoint to get chat titles for a given user_uuid.
    """
    results = db.query(ChatTitle.chat_title).filter(ChatTitle.user_uuid == user_uuid).all()
    return [result.chat_title for result in results]
