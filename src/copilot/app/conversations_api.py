import json
import logging
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load models
from database.models import ChatHistory, ChatTitle, ChatFeedback

from sqlalchemy.orm import Session
from database.database import get_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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


@app.get(
    "/",
    summary="Get conversations by user_uuid",
    response_description="Return a list of conversations for a given user_uuid",
    status_code=200,
)
async def get_conversations(
    user_uuid: str = None, db: Session = Depends(get_db)
):
    """
    Endpoint to get all conversations for a given user_uuid.
    If user_uuid is not provided, it will raise an HTTP 400 error.
    """
    if not user_uuid:
        raise HTTPException(
            status_code=400, detail="user_uuid query parameter is required."
        )

    conversations = (
        db.query(ChatHistory).filter(ChatHistory.user_uuid == user_uuid).all()
    )
    if not conversations:
        raise HTTPException(
            status_code=404, detail="No conversations found for user_uuid."
        )

    return conversations


@app.get(
    "/titles",
    summary="Get chat titles by user_uuid",
    response_description="Return a list of chat titles for a given user_uuid",
    status_code=200,
)
async def get_chat_titles(
    user_uuid: str = None, db: Session = Depends(get_db)
):
    """
    Endpoint to get all chat titles for a given user_uuid.
    """
    if not user_uuid:
        raise HTTPException(
            status_code=400, detail="user_uuid query parameter is required."
        )

    titles = db.query(ChatTitle).filter(ChatTitle.user_uuid == user_uuid).all()
    if not titles:
        raise HTTPException(
            status_code=404, detail="No chat titles found for user_uuid."
        )

    return titles


@app.get(
    "/{conversation_uuid}",
    summary="Get a specific conversation by conversation_uuid",
    response_description="Return a specific conversation by its conversation_uuid",
    status_code=200,
)
async def get_conversation(
    conversation_uuid: str = None, db: Session = Depends(get_db)
):
    """
    Endpoint to get a specific conversation by conversation_uuid.
    """
    if not conversation_uuid:
        raise HTTPException(
            status_code=400,
            detail="conversation_uuid query parameter is required.",
        )

    conversation = (
        db.query(ChatHistory)
        .filter(ChatHistory.conversation_uuid == conversation_uuid)
        .all()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return conversation


@app.delete(
    "/{conversation_uuid}",
    summary="Delete a specific conversation by conversation_uuid",
    response_description="Delete a specific conversation and return success status",
    status_code=200,
)
async def delete_conversation(
    conversation_uuid: str = None, db: Session = Depends(get_db)
):
    """
    Endpoint to delete a specific conversation by conversation_uuid.
    """
    if not conversation_uuid:
        raise HTTPException(
            status_code=400,
            detail="conversation_uuid parameter is required.",
        )

    try:
        # Delete from ChatFeedback
        db.query(ChatFeedback).filter(
            ChatFeedback.conversation_uuid == conversation_uuid
        ).delete()

        # Delete from ChatHistory
        result = (
            db.query(ChatHistory)
            .filter(ChatHistory.conversation_uuid == conversation_uuid)
            .delete()
        )

        # Delete from ChatTitle
        result = (
            db.query(ChatTitle)
            .filter(ChatTitle.conversation_uuid == conversation_uuid)
            .delete()
        )

        db.commit()

        if result > 0:
            logger.info(
                "Conversation %s deleted successfully", conversation_uuid
            )
            return {
                "status": "success",
                "message": "Conversation deleted successfully",
            }
        else:
            raise HTTPException(
                status_code=404, detail="Conversation not found"
            )

    except Exception as e:
        db.rollback()
        logger.error("Error deleting conversation: %s", e)
        raise HTTPException(
            status_code=500, detail="Error deleting conversation"
        ) from e


@app.put("/feedback/thumbs_up")
def thumbs_up(
    user_uuid: str = None,
    conversation_uuid: str = None,
    message_uuid: str = None,
    db: Session = Depends(get_db),
):
    # Check if feedback already exists
    feedback_entry = (
        db.query(ChatFeedback)
        .filter(
            ChatFeedback.user_uuid == user_uuid,
            ChatFeedback.conversation_uuid == conversation_uuid,
            ChatFeedback.message_uuid == message_uuid,
        )
        .first()
    )

    if feedback_entry:
        try:
            # Update existing entry
            feedback_entry.score += 1
            feedback_entry.timestamp = datetime.utcnow()

            db.commit()
            db.refresh(feedback_entry)
            return {"status": "updated", "feedback": feedback_entry}
        except Exception as e:
            db.rollback()
            logger.error("Error updating feedback: %s", e)
            raise HTTPException(
                status_code=500, detail="Error updating feedback."
            ) from e
    else:
        try:
            # Create new feedback entry
            new_feedback = ChatFeedback(
                user_uuid=user_uuid,
                conversation_uuid=conversation_uuid,
                message_uuid=message_uuid,
                score=1,
                timestamp=datetime.utcnow(),
            )
            db.add(new_feedback)
            db.commit()
            db.refresh(new_feedback)
            return {"status": "created", "feedback": new_feedback}
        except Exception as e:
            db.rollback()
            logger.error("Error updating feedback: %s", e)
            raise HTTPException(
                status_code=500, detail="Error updating feedback."
            ) from e


@app.put("/feedback/thumbs_down")
def thumbs_down(
    user_uuid: str = None,
    conversation_uuid: str = None,
    message_uuid: str = None,
    comment: str = None,
    db: Session = Depends(get_db),
):
    # Check if feedback already exists
    feedback_entry = (
        db.query(ChatFeedback)
        .filter(
            ChatFeedback.user_uuid == user_uuid,
            ChatFeedback.conversation_uuid == conversation_uuid,
            ChatFeedback.message_uuid == message_uuid,
        )
        .first()
    )

    if feedback_entry:
        try:
            # Update existing entry
            feedback_entry.score -= 1
            feedback_entry.timestamp = datetime.utcnow()

            # Append new comment to existing comments
            existing_comments = (
                json.loads(feedback_entry.comment)
                if feedback_entry.comment
                else []
            )
            if isinstance(existing_comments, list):
                existing_comments.append(comment)
            else:
                existing_comments = [existing_comments, comment]
            feedback_entry.comment = json.dumps(existing_comments)

            db.commit()
            db.refresh(feedback_entry)
            return {"status": "updated", "feedback": feedback_entry}
        except Exception as e:
            db.rollback()
            logger.error("Error updating feedback: %s", e)
            raise HTTPException(
                status_code=500, detail="Error updating feedback."
            ) from e
    else:
        try:
            # Create new feedback entry
            new_feedback = ChatFeedback(
                user_uuid=user_uuid,
                conversation_uuid=conversation_uuid,
                message_uuid=message_uuid,
                score=-1,
                comment=json.dumps([comment]),
                timestamp=datetime.utcnow(),
            )
            db.add(new_feedback)
            db.commit()
            db.refresh(new_feedback)
            return {"status": "created", "feedback": new_feedback}
        except Exception as e:
            db.rollback()
            logger.error("Error updating feedback: %s", e)
            raise HTTPException(
                status_code=500, detail="Error updating feedback."
            ) from e


@app.put(
    "/{conversation_uuid}/title",
    summary="Update conversation title",
    response_description="Update the title of a specific conversation",
    status_code=200,
)
async def update_conversation_title(
    conversation_uuid: str,
    title_update: dict,
    db: Session = Depends(get_db),
):
    """
    Endpoint to update the title of a specific conversation by conversation_uuid.
    """
    logger.info(
        f"Received title update request for {conversation_uuid}: {title_update}"
    )

    try:
        chat_title = (
            db.query(ChatTitle)
            .filter(ChatTitle.conversation_uuid == conversation_uuid)
            .first()
        )

        if not chat_title:
            raise HTTPException(
                status_code=404, detail="Conversation not found"
            )

        chat_title.chat_title = title_update["new_title"]
        db.commit()
        db.refresh(chat_title)

        logger.info(f"Successfully updated title for {conversation_uuid}")
        return {
            "status": "success",
            "message": "Conversation title updated successfully",
            "title": {
                "conversationId": chat_title.conversation_uuid,
                "title": chat_title.chat_title,
            },
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating conversation title: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating conversation title: {str(e)}",
        )
